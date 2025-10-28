from core import Message, command, logger, get_lang
from aiogram.exceptions import TelegramBadRequest

lang = get_lang()

def help():
    return {
        "name": "ban",
        "version": "0.0.1",
        "description": "Ban a user from the chat",
        "author": "Komihub",
        "usage": "/ban [user_id or reply to message] [reason]"
    }

@command('ban')
async def ban(message: Message):
    logger.info(lang.log_command_executed.format(command='ban', user_id=message.from_user.id))

    # Check if user is admin
    try:
        user_member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if user_member.status not in ['administrator', 'creator']:
            await message.answer(lang.no_rights_to_ban_user)
            return
    except Exception:
        await message.answer(lang.unknown_error)
        return

    # Get target user
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        reason = message.text.split(' ', 1)[1] if len(message.text.split(' ', 1)) > 1 else "No reason provided"
    else:
        args = message.text.split()
        if len(args) < 2:
            await message.answer("Usage: /ban [user_id or reply] [reason]")
            return
        try:
            target_user_id = int(args[1])
            target_user = await message.bot.get_chat_member(message.chat.id, target_user_id)
            target_user = target_user.user
            reason = ' '.join(args[2:]) if len(args) > 2 else "No reason provided"
        except (ValueError, Exception):
            await message.answer(lang.unknown_command)
            return

    # Ban the user
    try:
        await message.bot.ban_chat_member(message.chat.id, target_user.id)
        await message.answer(lang.ban_success)
        logger.info(lang.log_user_banned.format(user_id=target_user.id, chat_id=message.chat.id))
    except TelegramBadRequest as e:
        await message.answer(f"Failed to ban user: {e}")
    except Exception as e:
        await message.answer(lang.unknown_error)
        logger.error(f"Ban error: {e}")