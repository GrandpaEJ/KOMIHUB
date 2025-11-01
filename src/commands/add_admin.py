from core import Message, command, logger, get_lang
from core.database import db

lang = get_lang()


def help():
    return {
        "name": "add_admin",
        "version": "0.0.1",
        "description": "Add a user as admin",
        "author": "Komihub",
        "usage": "/add_admin [user_id or reply] [admin_type]",
    }


@command("add_admin")
async def add_admin(message: Message):
    # Check if user is owner
    if not db.is_admin(message.from_user.id, "owner"):
        await message.answer("❌ This command is only available to the owner.")
        return

    logger.info(
        lang.log_command_executed.format(
            command="add_admin", user_id=message.from_user.id
        )
    )

    args = message.text.split()
    admin_types = ["admins", "elders", "gc_admins", "ch_admins"]

    # Get target user
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        admin_type = args[1] if len(args) > 1 else "admins"
    else:
        if len(args) < 2:
            await message.answer(
                "Usage: /add_admin [user_id or reply] [admin_type]\nAdmin types: admins, elders, gc_admins, ch_admins"
            )
            return
        try:
            target_user_id = int(args[1])
            # Get user info from bot
            target_user = await message.bot.get_chat_member(
                message.chat.id, target_user_id
            )
            target_user = target_user.user
            admin_type = args[2] if len(args) > 2 else "admins"
        except (ValueError, Exception):
            await message.answer("Invalid user ID or user not found.")
            return

    if admin_type not in admin_types:
        await message.answer(f"Invalid admin type. Available: {', '.join(admin_types)}")
        return

    # Add admin
    if db.add_admin(target_user.id, admin_type):
        role_names = {
            "admins": "Admin",
            "elders": "Elder",
            "gc_admins": "Group Chat Admin",
            "ch_admins": "Channel Admin",
        }

        await message.answer(
            f"✅ <b>Admin Added Successfully!</b>\n\n"
            f"👤 User: {target_user.first_name} {target_user.last_name or ''}\n"
            f"🆔 ID: <code>{target_user.id}</code>\n"
            f"👑 Role: {role_names.get(admin_type, admin_type)}\n\n"
            f"User now has admin privileges!",
            parse_mode="HTML",
        )
        logger.info(f"Added {admin_type} admin: {target_user.id}")
    else:
        await message.answer("❌ User is already an admin of this type.")


@command("remove_admin")
async def remove_admin(message: Message):
    # Check if user is owner
    if not db.is_admin(message.from_user.id, "owner"):
        await message.answer("❌ This command is only available to the owner.")
        return

    logger.info(
        lang.log_command_executed.format(
            command="remove_admin", user_id=message.from_user.id
        )
    )

    args = message.text.split()
    admin_types = ["admins", "elders", "gc_admins", "ch_admins"]

    # Get target user
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        admin_type = args[1] if len(args) > 1 else "admins"
    else:
        if len(args) < 2:
            await message.answer(
                "Usage: /remove_admin [user_id or reply] [admin_type]\nAdmin types: admins, elders, gc_admins, ch_admins"
            )
            return
        try:
            target_user_id = int(args[1])
            target_user = await message.bot.get_chat_member(
                message.chat.id, target_user_id
            )
            target_user = target_user.user
            admin_type = args[2] if len(args) > 2 else "admins"
        except (ValueError, Exception):
            await message.answer("Invalid user ID or user not found.")
            return

    if admin_type not in admin_types:
        await message.answer(f"Invalid admin type. Available: {', '.join(admin_types)}")
        return

    # Remove admin
    if db.remove_admin(target_user.id, admin_type):
        await message.answer(
            f"✅ <b>Admin Removed Successfully!</b>\n\n"
            f"👤 User: {target_user.first_name} {target_user.last_name or ''}\n"
            f"🆔 ID: <code>{target_user.id}</code>\n\n"
            f"Admin privileges revoked!",
            parse_mode="HTML",
        )
        logger.info(f"Removed {admin_type} admin: {target_user.id}")
    else:
        await message.answer("❌ User is not an admin of this type.")


@command("list_admins")
async def list_admins(message: Message):
    # Check if user is admin
    if not db.is_admin(message.from_user.id):
        await message.answer("❌ This command is only available to administrators.")
        return

    logger.info(
        lang.log_command_executed.format(
            command="list_admins", user_id=message.from_user.id
        )
    )

    admins = db.load_data("admins")

    admin_text = "<b>👑 Bot Administrators</b>\n\n"

    role_names = {
        "owner": "👑 Owner",
        "admins": "⚡ Admins",
        "elders": "🧙 Elders",
        "gc_admins": "👥 Group Chat Admins",
        "ch_admins": "📢 Channel Admins",
    }

    for role_type, user_ids in admins.items():
        if user_ids:
            admin_text += f"<b>{role_names.get(role_type, role_type)}:</b>\n"
            for user_id in user_ids:
                try:
                    user = await message.bot.get_chat_member(message.chat.id, user_id)
                    user = user.user
                    name = f"{user.first_name} {user.last_name or ''}".strip()
                    admin_text += f"• {name} (<code>{user_id}</code>)\n"
                except:
                    admin_text += f"• Unknown User (<code>{user_id}</code>)\n"
            admin_text += "\n"

    await message.answer(admin_text, parse_mode="HTML")
