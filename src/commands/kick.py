from core import Message, command, logger, get_lang
from aiogram.exceptions import TelegramBadRequest

lang = get_lang()

def help():
    return {
        "name": "kick",
        "version": "0.0.1",
        "description": "Kick a user from the chat",
        "author": "Komihub",
        "usage": "/kick [user_id or reply to message] [reason]"
    }

@command('kick')
async def kick(message: Message):
    logger.info(lang.log_command_executed.format(command='kick', user_id=message.from_user.id))

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
            await message.answer("Usage: /kick [user_id or reply] [reason]")
            return
        try:
            target_user_id = int(args[1])
            target_user = await message.bot.get_chat_member(message.chat.id, target_user_id)
            target_user = target_user.user
            reason = ' '.join(args[2:]) if len(args) > 2 else "No reason provided"
        except (ValueError, Exception):
            await message.answer(lang.unknown_command)
            return

    # Kick the user
    try:
        await message.bot.ban_chat_member(message.chat.id, target_user.id)
        await message.bot.unban_chat_member(message.chat.id, target_user.id)  # Unban immediately to allow rejoin
        await message.answer(lang.kick_success)
        logger.info(lang.log_user_kicked.format(user_id=target_user.id, chat_id=message.chat.id))
    except TelegramBadRequest as e:
        await message.answer(f"Failed to kick user: {e}")
    except Exception as e:
        await message.answer(lang.unknown_error)
        logger.error(f"Kick error: {e}")