# meta developer: @coddan

import asyncio
import re
import logging
import aiohttp
from datetime import datetime
from zoneinfo import ZoneInfo

from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors import FloodWaitError
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)

DEFAULT_TZ = "Europe/Moscow"

CLOCK_RE = re.compile(r"\s*\|.*$")

EMO_CLOCK = "<emoji document_id=5877530150345641603>⏳</emoji>"
EMO_OK    = "<emoji document_id=5256182535917940722>✅</emoji>"
EMO_SCHED = "<emoji document_id=5253527438675158560>⏰</emoji>"

FONT_LIST = [
    ("Default",     "0123456789"),
    ("Bold Math",   "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"),
    ("Bold Sans",   "<b>0123456789</b>"),
    ("Bold Italic", "<i><b>0123456789</b></i>"),
    ("Mono",        "<code>0123456789</code>"),
    ("Fullwidth",   "０１２３４５６７８９"),
    ("Superscript", "⁰¹²³⁴⁵⁶⁷⁸⁹"),
    ("Subscript",   "₀₁₂₃₄₅₆₇₈₉"),
    ("Circle",      "⓪①②③④⑤⑥⑦⑧⑨"),
    ("Black Circle","⓿❶❷❸❹❺❻❼❽❾"),
]

DEFAULT_FONT = "𝟘𝟙𝟚𝟛𝟜𝟝𝟞𝟟𝟠𝟡"


def _fancy(t: str, font: str) -> str:
    return "".join(font[int(c)] if c.isdigit() else c for c in t)


@loader.tds
class FancyClockBirthdayMod(loader.Module):
    """Periodically updates your Telegram first name to show a countdown to your birthday."""

    strings = {"name": "FancyClockBirthday"}

    def __init__(self):
        self._task = None
        self._running = False
        self._font = DEFAULT_FONT

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self._font = self.db.get("FancyClockBirthday", "font", DEFAULT_FONT)

        if self._enabled():
            self._running = True
            self._task = asyncio.ensure_future(self._loop())

    def _get_tz(self) -> ZoneInfo:
        name = self.db.get("FancyClockBirthday", "tz", DEFAULT_TZ)
        try:
            return ZoneInfo(name)
        except Exception:
            return ZoneInfo(DEFAULT_TZ)

    def _base(self) -> str:
        return self.db.get("FancyClockBirthday", "base", "")

    def _enabled(self) -> bool:
        return self.db.get("FancyClockBirthday", "enabled", False)

    async def _refresh(self):
        if not self._enabled():
            return
        tz = self._get_tz()
        now = datetime.now(tz)
        base = self._base()
        if not base:
            return

        bd_str = self.db.get("FancyClockBirthday", "birthday", "")
        if not bd_str:
            text = "Установи ДР (.fcbd)"
        else:
            try:
                day, month = map(int, bd_str.split("."))
            except Exception:
                day, month = 1, 1

            if now.day == day and now.month == month:
                text = self.db.get("FancyClockBirthday", "bd_text", "С ДР! 🎉")
            else:
                try:
                    target = datetime(now.year, month, day, tzinfo=tz)
                except ValueError:
                    target = datetime(now.year, 3, 1, tzinfo=tz)

                if now >= target:
                    try:
                        target = datetime(now.year + 1, month, day, tzinfo=tz)
                    except ValueError:
                        target = datetime(now.year + 1, 3, 1, tzinfo=tz)

                diff = target - now
                days = diff.days
                hours = diff.seconds // 3600
                minutes = (diff.seconds % 3600) // 60

                fmt = self.db.get("FancyClockBirthday", "format", "до др {d}д {h}ч")
                text = fmt.format(d=days, h=f"{hours:02d}", m=f"{minutes:02d}")

        fancy_text = _fancy(text, self._font)
        await self._set_name(f"{base} | {fancy_text}")

    async def _set_name(self, name: str):
        name = name[:64]
        try:
            await self.client(UpdateProfileRequest(first_name=name))
        except FloodWaitError as e:
            await asyncio.sleep(e.seconds + 3)
            try:
                await self.client(UpdateProfileRequest(first_name=name))
            except Exception:
                pass
        except Exception:
            pass

    async def _loop(self):
        while self._running:
            try:
                await self._refresh()
                tz = self._get_tz()
                now = datetime.now(tz)
                await asyncio.sleep(60 - now.second)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning("FancyClockBirthday: %s", e)
                await asyncio.sleep(10)

    async def _disable_clock(self):
        self._running = False
        self.db.set("FancyClockBirthday", "enabled", False)

        if self._task and not self._task.done():
            self._task.cancel()
            self._task = None

        base = self._base()
        if base:
            await self._set_name(base)

    @loader.command()
    async def fccmd(self, message: Message):
        """включить / выключить отсчет до др в нике"""
        if self._enabled():
            await self._disable_clock()
            await utils.answer(message, f"{EMO_OK} Отсчет выключен")
        else:
            me = await self.client.get_me()
            base = CLOCK_RE.sub("", me.first_name or "").rstrip()
            self.db.set("FancyClockBirthday", "base", base)
            self.db.set("FancyClockBirthday", "enabled", True)
            self._running = True

            if self._task and not self._task.done():
                self._task.cancel()

            self._task = asyncio.ensure_future(self._loop())
            await utils.answer(message, f"{EMO_CLOCK} Отсчет включен")

    @loader.command()
    async def fcbdcmd(self, message: Message):
        """установить дату рождения. Пример: .fcbd 16.09"""
        args = utils.get_args_raw(message).strip()
        if not args:
            bd = self.db.get("FancyClockBirthday", "birthday", "Не установлена")
            await utils.answer(
                message,
                f"{EMO_SCHED} Текущая дата рождения: <code>{bd}</code>\n"
                f"Установи новую: <code>.fcbd ДД.ММ</code>"
            )
            return

        match = re.fullmatch(r"(\d{1,2})[\.\-/](\d{1,2})", args)
        if not match:
            await utils.answer(
                message,
                f"{EMO_SCHED} Неверный формат. Используй ДД.ММ, например: <code>.fcbd 16.09</code>"
            )
            return

        day, month = int(match.group(1)), int(match.group(2))
        try:
            datetime(2024, month, day)
        except ValueError:
            await utils.answer(message, f"{EMO_SCHED} Некорректная дата.")
            return

        bd_str = f"{day:02d}.{month:02d}"
        self.db.set("FancyClockBirthday", "birthday", bd_str)
        await utils.answer(message, f"{EMO_OK} Дата рождения установлена на <b>{bd_str}</b>")
        if self._enabled():
            await self._refresh()

    @loader.command()
    async def fcfmtcmd(self, message: Message):
        """установить формат отсчета. Доступны {d}, {h}, {m}. Пример: .fcfmt до др {d}д {h}ч"""
        args = utils.get_args_raw(message).strip()
        if not args:
            fmt = self.db.get("FancyClockBirthday", "format", "до др {d}д {h}ч")
            await utils.answer(
                message,
                f"{EMO_SCHED} Текущий формат: <code>{fmt}</code>\n"
                f"Доступные переменные: <code>{{d}}</code> (дни), <code>{{h}}</code> (часы), <code>{{m}}</code> (минуты).\n"
                f"Пример: <code>.fcfmt до др {{d}}д {{h}}ч</code>"
            )
            return

        try:
            args.format(d=12, h="04", m="30")
        except Exception:
            await utils.answer(
                message,
                f"{EMO_SCHED} Неверный формат. Убедись, что используешь только разрешенные переменные: {{d}}, {{h}}, {{m}}."
            )
            return

        self.db.set("FancyClockBirthday", "format", args)
        await utils.answer(message, f"{EMO_OK} Формат изменен на: <code>{args}</code>")
        if self._enabled():
            await self._refresh()

    @loader.command()
    async def fcbdtcmd(self, message: Message):
        """установить текст в день рождения. Пример: .fcbdt С ДР! 🎉"""
        args = utils.get_args_raw(message).strip()
        if not args:
            bdt = self.db.get("FancyClockBirthday", "bd_text", "С ДР! 🎉")
            await utils.answer(
                message,
                f"{EMO_SCHED} Текущий текст в день рождения: <code>{bdt}</code>\n"
                f"Изменить: <code>.fcbdt <текст></code>"
            )
            return

        self.db.set("FancyClockBirthday", "bd_text", args)
        await utils.answer(message, f"{EMO_OK} Текст в день рождения изменен на: <code>{args}</code>")
        if self._enabled():
            await self._refresh()

    @loader.command()
    async def fcscmd(self, message: Message):
        """поменять часовой пояс по названию города или страны. Пример: .fcs Красноярск"""
        query = utils.get_args_raw(message).strip()
        if not query:
            await utils.answer(
                message,
                f"{EMO_CLOCK} Укажи город или страну.\n"
                f"Примеры: <code>.fcs Красноярск</code> · <code>.fcs Россия Тула</code>"
            )
            return

        message = await utils.answer(message, f"{EMO_CLOCK} Ищу <b>{query}</b>...")

        try:
            async with aiohttp.ClientSession() as session:
                url = "https://geocoding-api.open-meteo.com/v1/search"
                params = {"name": query, "count": 1, "language": "ru", "format": "json"}

                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    data = await r.json()

                results = data.get("results")
                if not results:
                    await utils.answer(message, f"{EMO_SCHED} Не нашёл <b>{query}</b>. Попробуй по-другому.")
                    return

                result = results[0]
                tz_name = result.get("timezone")
                city_label = result.get("name", query)
                country = result.get("country", "")
                if country:
                    city_label = f"{city_label}, {country}"

                if not tz_name:
                    await utils.answer(message, f"{EMO_SCHED} Не удалось определить часовой пояс для <b>{query}</b>.")
                    return

                self.db.set("FancyClockBirthday", "tz", tz_name)
                await self._refresh()

                await utils.answer(
                    message,
                    f"{EMO_OK} <b>{city_label}</b>\n"
                    f"Таймзона: <code>{tz_name}</code>"
                )

        except Exception:
            await utils.answer(message, f"{EMO_SCHED} Не удалось получить данные. Попробуй позже.")

    @loader.command()
    async def fcfcmd(self, message: Message):
        """шрифты для цифр в нике"""
        dummy = "12д 04ч"

        rows = []
        row = []
        for idx, (label, chars) in enumerate(FONT_LIST):
            preview = _fancy(dummy, chars)
            btn_text = f"{preview} — {label}"
            btn = {"text": btn_text, "callback": self._pick_font, "args": (chars, label)}
            btn["style"] = "danger" if chars == self._font else "success"
            row.append(btn)
            if len(row) == 2 or idx == len(FONT_LIST) - 1:
                rows.append(row)
                row = []

        current_label = next((l for l, c in FONT_LIST if c == self._font), "custom")
        current_preview = _fancy(dummy, self._font)

        rows.append([{"text": "Подписаться", "url": "https://t.me/bmodules", "style": "success"}])

        await self.inline.form(
            text=(
                f"{EMO_CLOCK} <b>Шрифты для цифр (пример на '12д 04ч')</b>\n\n"
                f"Сейчас: {current_preview} — {current_label}"
            ),
            message=message,
            reply_markup=rows,
        )

    async def _pick_font(self, call, chars: str, label: str):
        self._font = chars
        self.db.set("FancyClockBirthday", "font", chars)

        await self._refresh()

        dummy = "12д 04ч"
        preview = _fancy(dummy, chars)

        await call.edit(
            f"Шрифт <b>{label}</b> выбран\n\nПример: {preview}"
        )