from core import Message, command, logger, get_lang

lang = get_lang()

def help():
    return {
        "name": "unsend",
        "version": "0.0.1",
        "description": "Delete bot messages by replying to them",
        "author": "Komihub",
        "usage": "/unsend - Reply to any bot message to delete it"
    }

@command('unsend')
async def unsend_command(message: Message):
    logger.info(lang.log_command_executed.format(command='unsend', user_id=message.from_user.id))

    # Check if message is a reply
    if not message.reply_to_message:
        await message.answer(
            "🗑️ <b>Unsend Command</b>\n\n"
            "Reply to any message sent by this bot to delete it.\n\n"
            "<code>/unsend</code> (reply to bot message)",
            parse_mode="HTML"
        )
        return

    # Check if the replied message is from the bot
    if message.reply_to_message.from_user.id != message.bot.id:
        await message.answer("❌ You can only unsend messages sent by this bot.")
        return

    try:
        # Delete the replied message
        await message.reply_to_message.delete()

        # Delete the command message
        await message.delete()

        logger.info(f"Message unsent by user {message.from_user.id}")

    except Exception as e:
        logger.error(f"Unsend error: {e}")
        await message.answer("❌ Failed to delete the message. It may be too old or I may not have permission.")