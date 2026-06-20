# meta developer: @coddan

from .. import loader, utils
from telethon.tl import types as tl_types
import inspect


@loader.tds
class TriggersMod(loader.Module):
    """Позволяет создавать пользовательские триггеры (ключевое слово -> ответ) и включать их в определённых чатах или топиках, а также управлять чёрным списком пользователей."""

    strings = {
        "name": "Триггеры",
        "no_triggers": "<b>🚫 Триггеры не установлены.</b>",
        "triggers_list": "<b>📝 Список триггеров:</b>\n\n{}",
        "trigger_item": "<b>• <code>{}</code></b> -> <code>{}</code>",
        "no_args_add": "<b>🚫 Укажите триггер и ответ, разделив их |</b>\nПример: <code>.addtrg привет | и тебе привет</code>\nИли, ответьте на сообщение и используйте: <code>.addtrg привет | реплай</code>",
        "no_reply_found": "<b>🚫 Использовано ключевое слово 'реплай', но ответное сообщение не найдено.</b>",
        "no_reply_text": "<b>🚫 В ответном сообщении нет текста.</b>",
        "trigger_added": "<b>✅ Триггер '<code>{}</code>' добавлен.</b>",
        "no_args_del": "<b>🚫 Укажите триггер для удаления.</b>",
        "trigger_not_found": "<b>🚫 Триггер '<code>{}</code>' не найден.</b>",
        "trigger_deleted": "<b>🗑 Триггер '<code>{}</code>' удален.</b>",
        "trg_on_off_args": "<b>🚫 Укажите 'chat' или 'topic'.</b>",
        "not_in_topic": "<b>🚫 Эта команда может быть использована только в топике.</b>",
        "enabled_in": "<b>✅ Триггеры включены в этом {}.</b>",
        "already_enabled_in": "<b>ℹ️ Триггеры уже включены в этом {}.</b>",
        "disabled_in": "<b>🚫 Триггеры выключены в этом {}.</b>",
        "already_disabled_in": "<b>ℹ️ Триггеры уже выключены в этом {}.</b>",
        "location_chat": "чате",
        "location_topic": "топике",
        "_cmd_doc_addtrg": "<триггер> | <ответ/реплай> - Добавить новый триггер. Используйте 'реплай' в качестве ответа, чтобы взять текст (с форматированием и кастомными эмодзи) из ответного сообщения.",
        "_cmd_doc_deltrg": "<триггер> - Удалить триггер.",
        "_cmd_doc_trglist": "Показать список всех триггеров.",
        "_cmd_doc_trgon": "<чат/топик> - Включить триггеры для всего чата или только для этого топика.",
        "_cmd_doc_trgoff": "<чат/топик> - Выключить триггеры для всего чата или только для этого топика.",
        # Blacklist strings
        "no_args_addbl": "<b>🚫 Укажите ID пользователя или ответьте на сообщение.</b>",
        "user_not_found_bl": "<b>🚫 Пользователь не найден.</b>",
        "user_already_bl": "<b>ℹ️ Пользователь <code>{}</code> уже в чёрном списке.</b>",
        "user_added_bl": "<b>✅ Пользователь <code>{}</code> добавлен в чёрный список.</b>",
        "no_args_delbl": "<b>🚫 Укажите ID пользователя для удаления из чёрного списка.</b>",
        "user_not_in_bl": "<b>🚫 Пользователь <code>{}</code> не найден в чёрном списке.</b>",
        "user_removed_bl": "<b>🗑 Пользователь <code>{}</code> удалён из чёрного списка.</b>",
        "no_blacklist_users": "<b>🚫 Чёрный список пуст.</b>",
        "blacklist_list": "<b>📝 Пользователи в чёрном списке:</b>\n\n{}",
        "blacklist_item": "<b>• <code>{}</code></b>",
        "_cmd_doc_addbl": "<ID пользователя/реплай> - Добавить пользователя в чёрный список, чтобы триггеры не срабатывали на его сообщения.",
        "_cmd_doc_delbl": "<ID пользователя/реплай> - Удалить пользователя из чёрного списка.",
        "_cmd_doc_blist": "Показать список пользователей в чёрном списке.",
        "en": {
            "name": "Triggers",
            "no_triggers": "<b>🚫 No triggers set.</b>",
            "triggers_list": "<b>📝 List of triggers:</b>\n\n{}",
            "trigger_item": "<b>• <code>{}</code></b> -> <code>{}</code>",
            "no_args_add": "<b>🚫 Specify trigger and response separated by |</b>\nExample: <code>.addtrg hello | hi there</code>\nOr, reply to a message and use: <code>.addtrg hello | reply</code>",
            "no_reply_found": "<b>🚫 Reply keyword used but no message was replied to.</b>",
            "no_reply_text": "<b>🚫 The replied message has no text.</b>",
            "trigger_added": "<b>✅ Trigger '<code>{}</code>' added.</b>",
            "no_args_del": "<b>🚫 Specify the trigger to delete.</b>",
            "trigger_not_found": "<b>🚫 Trigger '<code>{}</code>' not found.</b>",
            "trigger_deleted": "<b>🗑 Trigger '<code>{}</code>' deleted.</b>",
            "trg_on_off_args": "<b>🚫 Specify 'chat' or 'topic'.</b>",
            "not_in_topic": "<b>🚫 This command can only be used in a topic.</b>",
            "enabled_in": "<b>✅ Triggers enabled in this {}.</b>",
            "already_enabled_in": "<b>ℹ️ Triggers are already enabled in this {}.</b>",
            "disabled_in": "<b>🚫 Triggers disabled in this {}.</b>",
            "already_disabled_in": "<b>ℹ️ Triggers are already disabled in this {}.</b>",
            "location_chat": "chat",
            "location_topic": "topic",
            "_cmd_doc_addtrg": "<trigger> | <response/reply> - Add a new trigger. Use 'reply' as response to take text (with formatting and custom emojis) from replied message.",
            "_cmd_doc_deltrg": "<trigger> - Delete a trigger.",
            "_cmd_doc_trglist": "List all active triggers.",
            "_cmd_doc_trgon": "<chat/topic> - Enable triggers for the whole chat or just this topic.",
            "_cmd_doc_trgoff": "<chat/topic> - Disable triggers for the whole chat or just this topic.",
            # Blacklist strings for English
            "no_args_addbl": "<b>🚫 Specify user ID or reply to a message.</b>",
            "user_not_found_bl": "<b>🚫 User not found.</b>",
            "user_already_bl": "<b>ℹ️ User <code>{}</code> is already in the blacklist.</b>",
            "user_added_bl": "<b>✅ User <code>{}</code> added to blacklist.</b>",
            "no_args_delbl": "<b>🚫 Specify user ID to remove from blacklist.</b>",
            "user_not_in_bl": "<b>🚫 User <code>{}</code> not found in blacklist.</b>",
            "user_removed_bl": "<b>🗑 User <code>{}</code> removed from blacklist.</b>",
            "no_blacklist_users": "<b>🚫 Blacklist is empty.</b>",
            "blacklist_list": "<b>📝 Blacklisted users:</b>\n\n{}",
            "blacklist_item": "<b>• <code>{}</code></b>",
            "_cmd_doc_addbl": "<user_id/reply> - Add user to blacklist, so triggers won't activate on their messages.",
            "_cmd_doc_delbl": "<user_id/reply> - Remove user from blacklist.",
            "_cmd_doc_blist": "List all blacklisted users.",
        },
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "case_sensitive",
                False,
                "Должны ли триггеры быть чувствительны к регистру?",
                validator=loader.validators.Boolean(),
            ),
        )
        self.reply_keywords = {"reply", "реплай"}

    def _serialize_entities(self, entities):
        """Converts a list of MessageEntity objects into a JSON-serializable list of dictionaries using .to_dict()."""
        if not entities:
            return []
        serialized = []
        for entity in entities:
            # Telethon TLObject subclasses (which MessageEntity types are) have a .to_dict() method
            # This method safely converts the object to a dictionary, including its type info in the '_' key.
            serialized.append(entity.to_dict())
        return serialized

    def _deserialize_entities(self, serialized_entities):
        """Converts a JSON-serializable list of dictionaries back into MessageEntity objects."""
        if not serialized_entities:
            return None
        deserialized = []
        for entity_dict in serialized_entities:
            if not isinstance(entity_dict, dict):
                self.logger.warning(f"Invalid entity data found during deserialization (not a dict): {entity_dict}")
                continue

            entity_type_name = entity_dict.pop("_", None)
            if not entity_type_name:
                self.logger.warning(f"Missing entity type name ('_') in entity dict during deserialization: {entity_dict}")
                continue
            
            # Dynamically get the MessageEntity class from telethon.tl.types
            entity_class = getattr(tl_types, entity_type_name, None)
            
            # Validate if it's a valid MessageEntity class
            if not entity_class or not inspect.isclass(entity_class) or not issubclass(entity_class, tl_types.MessageEntity):
                self.logger.warning(f"Unknown or invalid entity type '{entity_type_name}' found during deserialization. Data: {entity_dict}")
                continue
            
            try:
                # Reconstruct the entity object using keyword arguments from the dictionary.
                # The .to_dict() method provides keys compatible with constructor arguments.
                deserialized.append(entity_class(**entity_dict))
            except TypeError as e:
                self.logger.error(f"Failed to reconstruct entity {entity_type_name} with data {entity_dict}: {e}")
                continue
            except Exception as e:
                self.logger.error(f"An unexpected error occurred during entity reconstruction for {entity_type_name} with data {entity_dict}: {e}")
                continue
        return deserialized if deserialized else None

    async def on_ready(self):
        """Initialize database and migrate old data if necessary"""
        if self.get("triggers") is None:
            self.set("triggers", {})

        # Migrate old enabled_chats format
        enabled_chats = self.get("enabled_chats", [])
        # Check if it's a list of integers (old format)
        if isinstance(enabled_chats, list) and enabled_chats and all(isinstance(x, int) for x in enabled_chats):
            # Old format detected, migrate to new format (chat_id, topic_id)
            new_enabled_chats = [(chat_id, None) for chat_id in enabled_chats]
            self.set("enabled_chats", new_enabled_chats)
        elif not isinstance(enabled_chats, list): # Ensure it's a list if it's not already
            self.set("enabled_chats", [])
        
        # Initialize blacklist
        if self.get("blacklist") is None:
            self.set("blacklist", [])

        # Migrate old triggers format (string -> dict with text and entities)
        triggers = self.get("triggers", {})
        migrated_triggers = {}
        for trigger_keyword, response_data in triggers.items():
            if isinstance(response_data, str):
                # Old format: just a string
                migrated_triggers[trigger_keyword] = {
                    "text": response_data,
                    "entities": [], # No entities for old string triggers
                }
            elif isinstance(response_data, dict) and "text" in response_data:
                # Already in new format, ensure entities key exists
                if "entities" not in response_data:
                    response_data["entities"] = []
                
                # Check if entities are still raw MessageEntity objects (shouldn't happen if save failed, but for robustness)
                current_entities = response_data["entities"]
                if current_entities and isinstance(current_entities, list) and all(isinstance(e, tl_types.MessageEntity) for e in current_entities):
                    # If raw entities are found, serialize them
                    response_data["entities"] = self._serialize_entities(current_entities)
                    self.logger.warning(f"Migrated non-serialized MessageEntity objects for trigger '{trigger_keyword}'.")

                migrated_triggers[trigger_keyword] = response_data
            else:
                # Fallback for unexpected formats, treat as plain text
                migrated_triggers[trigger_keyword] = {
                    "text": str(response_data),
                    "entities": [],
                }

        if migrated_triggers != triggers:
            self.set("triggers", migrated_triggers)

    @loader.command(alias="at")
    async def addtrg(self, message):
        """<триггер> | <ответ/реплай> - Добавить новый триггер. Используйте 'реплай' в качестве ответа, чтобы взять текст (с форматированием и кастомными эмодзи) из ответного сообщения."""
        args = utils.get_args_raw(message)
        if not args or "|" not in args:
            await utils.answer(message, self.strings("no_args_add"))
            return

        trigger, response_part = [item.strip() for item in args.split("|", 1)]

        if not trigger or not response_part:
            await utils.answer(message, self.strings("no_args_add"))
            return

        response_text = ""
        response_entities = []

        if response_part.lower() in self.reply_keywords:
            if message.is_reply:
                replied_message = await message.get_reply_message()
                if replied_message and replied_message.text:
                    response_text = replied_message.text
                    # Serialize entities before storing them in the database
                    response_entities = self._serialize_entities(replied_message.entities)
                else:
                    await utils.answer(message, self.strings("no_reply_text"))
                    return
            else:
                await utils.answer(message, self.strings("no_reply_found"))
                return
        else:
            response_text = response_part
            # For direct text input, entities are not parsed from the command arguments.
            # Custom emojis from plain text input cannot be preserved without entities.
            response_entities = []

        triggers = self.get("triggers", {})
        triggers[trigger] = {"text": response_text, "entities": response_entities}
        self.set("triggers", triggers)

        await utils.answer(
            message, self.strings("trigger_added").format(utils.escape_html(trigger))
        )

    @loader.command(alias="dt")
    async def deltrg(self, message):
        """<триггер> - Удалить триггер."""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args_del"))
            return

        triggers = self.get("triggers", {})
        if args not in triggers:
            await utils.answer(
                message,
                self.strings("trigger_not_found").format(utils.escape_html(args)),
            )
            return

        del triggers[args]
        self.set("triggers", triggers)
        await utils.answer(
            message, self.strings("trigger_deleted").format(utils.escape_html(args))
        )

    @loader.command(alias="tl")
    async def trglist(self, message):
        """Показать список всех триггеров."""
        triggers = self.get("triggers", {})
        if not triggers:
            await utils.answer(message, self.strings("no_triggers"))
            return

        output_lines = []
        for t, r_data in triggers.items():
            # Ensure r_data is a dict with 'text' key, fallback to string if old format
            response_text = r_data["text"] if isinstance(r_data, dict) and "text" in r_data else str(r_data)
            # Display text for list, escape HTML to prevent breaking the message itself
            output_lines.append(
                self.strings("trigger_item").format(
                    utils.escape_html(t), utils.escape_html(response_text)
                )
            )
        
        await utils.answer(message, self.strings("triggers_list").format("\n".join(output_lines)))

    async def _toggle_triggers(self, message, enable: bool):
        args = utils.get_args_raw(message).lower()
        chat_id = utils.get_chat_id(message)
        topic_id = getattr(message, "top_id", None) # Use top_id for the current message's topic

        locations_map = {
            "chat": self.strings("location_chat"),
            "topic": self.strings("location_topic"),
        }

        if args == "chat":
            location = (chat_id, None)
            location_name = locations_map["chat"]
        elif args == "topic":
            if not topic_id:
                await utils.answer(message, self.strings("not_in_topic"))
                return
            location = (chat_id, topic_id)
            location_name = locations_map["topic"]
        else:
            await utils.answer(message, self.strings("trg_on_off_args"))
            return

        enabled_locations = self.get("enabled_chats", [])
        is_enabled = location in enabled_locations

        if enable:
            if is_enabled:
                await utils.answer(
                    message, self.strings("already_enabled_in").format(location_name)
                )
                return
            enabled_locations.append(location)
            self.set("enabled_chats", enabled_locations)
            await utils.answer(message, self.strings("enabled_in").format(location_name))
        else:  # disable
            if not is_enabled:
                await utils.answer(
                    message, self.strings("already_disabled_in").format(location_name)
                )
                return
            enabled_locations.remove(location)
            self.set("enabled_chats", enabled_locations)
            await utils.answer(message, self.strings("disabled_in").format(location_name))

    @loader.command(alias="ton")
    async def trgon(self, message):
        """<чат/топик> - Включить триггеры для всего чата или только для этого топика."""
        await self._toggle_triggers(message, enable=True)

    @loader.command(alias="toff")
    async def trgoff(self, message):
        """<чат/топик> - Выключить триггеры для всего чата или только для этого топика."""
        await self._toggle_triggers(message, enable=False)

    @loader.command(alias="abl")
    async def addbl(self, message):
        """<ID пользователя/реплай> - Добавить пользователя в чёрный список, чтобы триггеры не срабатывали на его сообщения."""
        user_id = None
        args = utils.get_args_raw(message)

        if message.is_reply:
            reply_msg = await message.get_reply_message()
            if reply_msg and reply_msg.sender:
                user_id = reply_msg.sender.id
        elif args.isdigit():
            user_id = int(args)
        
        if not user_id:
            await utils.answer(message, self.strings("no_args_addbl"))
            return

        blacklist = self.get("blacklist", [])
        if user_id in blacklist:
            await utils.answer(message, self.strings("user_already_bl").format(user_id))
            return

        blacklist.append(user_id)
        self.set("blacklist", blacklist)
        await utils.answer(message, self.strings("user_added_bl").format(user_id))

    @loader.command(alias="dbl")
    async def delbl(self, message):
        """<ID пользователя/реплай> - Удалить пользователя из чёрного списка."""
        user_id = None
        args = utils.get_args_raw(message)

        if message.is_reply:
            reply_msg = await message.get_reply_message()
            if reply_msg and reply_msg.sender:
                user_id = reply_msg.sender.id
        elif args.isdigit():
            user_id = int(args)
        
        if not user_id:
            await utils.answer(message, self.strings("no_args_delbl"))
            return

        blacklist = self.get("blacklist", [])
        if user_id not in blacklist:
            await utils.answer(message, self.strings("user_not_in_bl").format(user_id))
            return

        blacklist.remove(user_id)
        self.set("blacklist", blacklist)
        await utils.answer(message, self.strings("user_removed_bl").format(user_id))

    @loader.command(alias="bl")
    async def blist(self, message):
        """Показать список пользователей в чёрном списке."""
        blacklist = self.get("blacklist", [])
        if not blacklist:
            await utils.answer(message, self.strings("no_blacklist_users"))
            return

        output = "\n".join(
            [self.strings("blacklist_item").format(user_id) for user_id in blacklist]
        )
        await utils.answer(message, self.strings("blacklist_list").format(output))

    @loader.watcher(only_incoming=True, only_messages=True)
    async def watcher(self, message):
        if message.out or not hasattr(message, "text") or not message.text:
            return

        # Check blacklist first
        if message.sender_id in self.get("blacklist", []):
            return

        chat_id = utils.get_chat_id(message)
        topic_id = getattr(message, "top_id", None) # Use top_id for the current message's topic

        enabled_locations = self.get("enabled_chats", [])

        # Check if triggers are enabled for the specific topic or the whole chat
        is_enabled = False
        if (chat_id, None) in enabled_locations: # Enabled for whole chat
            is_enabled = True
        elif topic_id and (chat_id, topic_id) in enabled_locations: # Enabled for specific topic
            is_enabled = True

        if not is_enabled:
            return

        triggers = self.get("triggers", {})
        if not triggers:
            return

        for trigger_keyword, response_data in triggers.items():
            text_to_check = message.text
            trigger_to_check = trigger_keyword

            if not self.config["case_sensitive"]:
                text_to_check = text_to_check.lower()
                trigger_to_check = trigger_keyword.lower()

            if trigger_to_check in text_to_check:
                response_text = ""
                response_entities = None

                if isinstance(response_data, dict) and "text" in response_data:
                    response_text = response_data["text"]
                    serialized_entities = response_data.get("entities")
                    # Deserialize entities before passing to message.reply
                    response_entities = self._deserialize_entities(serialized_entities)
                else:
                    # Fallback for old string format (should be migrated by on_ready, but good for safety)
                    response_text = str(response_data)
                    response_entities = None

                # Use message.reply to send with entities if available, preserving custom emojis and formatting
                await message.reply(response_text, entities=response_entities)
                # We break here to prevent multiple triggers from firing on a single message
                break