from core import Message, command, logger, get_lang

lang = get_lang()


def help():
    return {
        "name": "info",
        "version": "0.0.1",
        "description": "Get information about user or chat",
        "author": "Komihub",
        "usage": "/info [user_id or reply to message]",
    }


@command("info")
async def info(message: Message):
    logger.info(
        lang.log_command_executed.format(command="info", user_id=message.from_user.id)
    )

    # Check if replying to a message
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        # Check if user provided an ID
        args = message.text.split()
        if len(args) > 1:
            try:
                user_id = int(args[1])
                user = await message.bot.get_chat_member(message.chat.id, user_id)
                user = user.user
            except (ValueError, Exception):
                await message.answer(lang.unknown_user)
                return
        else:
            user = message.from_user

    # Get user info
    user_info = f"""
<b>User Information:</b>
ID: <code>{user.id}</code>
Name: {user.first_name} {user.last_name or ''}
Username: @{user.username or 'None'}
Language: {user.language_code or 'Unknown'}
"""

    # Get chat member status if in group
    if message.chat.type in ["group", "supergroup"]:
        try:
            member = await message.bot.get_chat_member(message.chat.id, user.id)
            status_map = {
                "creator": "Owner",
                "administrator": "Admin",
                "member": "Member",
                "restricted": "Restricted",
                "left": "Left",
                "kicked": "Banned",
            }
            status = status_map.get(member.status, member.status)
            user_info += f"Status: {status}\n"
        except Exception:
            pass

    await message.answer(user_info, parse_mode="HTML")
