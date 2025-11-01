from aiogram.types import ChatMemberUpdated
from core import logger, get_lang

lang = get_lang()


async def on_user_join(chat_member: ChatMemberUpdated):
    if chat_member.new_chat_member.status in ["member", "administrator", "creator"]:
        user_id = chat_member.new_chat_member.user.id
        chat_id = chat_member.chat.id
        logger.info(lang.log_user_joined.format(user_id=user_id, chat_id=chat_id))


async def on_user_left(chat_member: ChatMemberUpdated):
    if chat_member.new_chat_member.status == "left":
        user_id = chat_member.new_chat_member.user.id
        chat_id = chat_member.chat.id
        logger.info(lang.log_user_left.format(user_id=user_id, chat_id=chat_id))


# Register events
from core.bot import bot_instance

bot_instance.register_event("chat_member", on_user_join)
bot_instance.register_event("chat_member", on_user_left)
