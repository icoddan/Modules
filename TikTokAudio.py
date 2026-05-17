# meta developer: @coddan
import io
import re
import aiohttp
from .. import loader, utils

@loader.tds
class TikTokAudioMod(loader.Module):
    """Модуль для скачивания звука (аудио) из видео TikTok"""
    
    strings = {
        "name": "TikTokAudio",
        "no_url": "<b>❌ Укажите ссылку на TikTok видео (в аргументах или ответом на сообщение).</b>",
        "downloading": "<b>⏳ Скачиваю аудио...</b>",
        "error": "<b>❌ Ошибка при скачивании:</b> <code>{}</code>",
        "not_found": "<b>❌ Не удалось найти или скачать аудио для этого видео.</b>"
    }

    @loader.command(ru_doc="<ссылка> - Скачать звук из TikTok")
    async def ttaudiocmd(self, message):
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        text_to_search = args
        if not text_to_search and reply and reply.raw_text:
            text_to_search = reply.raw_text

        url_match = re.search(r'(https?://(?:www\.|vm\.|vt\.)?tiktok\.com/[^\s]+)', text_to_search)
        
        if not url_match:
            return await utils.answer(message, self.strings("no_url"))
            
        url = url_match.group(1)
        message = await utils.answer(message, self.strings("downloading"))
        
        try:
            async with aiohttp.ClientSession() as session:
                # Используем публичный API tikwm для получения данных о видео
                api_url = "https://www.tikwm.com/api/"
                async with session.post(api_url, data={"url": url}) as resp:
                    if resp.status != 200:
                        return await utils.answer(message, self.strings("error").format(f"HTTP {resp.status}"))
                    
                    data = await resp.json()
                    
                    if data.get("code") != 0 or "data" not in data or "music" not in data["data"]:
                        return await utils.answer(message, self.strings("not_found"))
                        
                    music_url = data["data"]["music"]
                    music_title = data["data"].get("music_info", {}).get("title", "tiktok_audio")
                    music_author = data["data"].get("music_info", {}).get("author", "Unknown")
                    
                    # Скачиваем сам аудиофайл
                    async with session.get(music_url) as music_resp:
                        if music_resp.status != 200:
                            return await utils.answer(message, self.strings("error").format(f"Audio HTTP {music_resp.status}"))
                            
                        music_bytes = await music_resp.read()
                        
            audio_file = io.BytesIO(music_bytes)
            audio_file.name = f"{music_author} - {music_title}.mp3"
            
            caption = f"<b>🎵 Звук из TikTok</b>\n👤 <b>Автор:</b> <code>{music_author}</code>\n📝 <b>Название:</b> <code>{music_title}</code>"
            
            await utils.answer_file(message, audio_file, caption=caption)
            
        except Exception as e:
            await utils.answer(message, self.strings("error").format(str(e)))