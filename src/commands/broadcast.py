from core import Message, command, logger, get_lang
from core.database import db
import asyncio

lang = get_lang()

def help():
    return {
        "name": "broadcast",
        "version": "0.0.1",
        "description": "Broadcast message to all users",
        "author": "Komihub",
        "usage": "/broadcast [message]"
    }

@command('broadcast')
async def broadcast(message: Message):
    # Check if user is admin
    if not db.is_admin(message.from_user.id):
        await message.answer("❌ This command is only available to administrators.")
        return

    logger.info(lang.log_command_executed.format(command='broadcast', user_id=message.from_user.id))

    # Get the message to broadcast
    args = message.text.split(' ', 1)
    if len(args) < 2:
        await message.answer("Usage: /broadcast [message]\n\nSend a message that will be broadcasted to all users who have used the bot.")
        return

    broadcast_message = args[1]

    # Get all users from database
    users_data = db.load_data('users')
    user_ids = list(users_data.keys())

    if not user_ids:
        await message.answer("No users found in database.")
        return

    # Send initial status message
    status_msg = await message.answer(f"📢 <b>Starting broadcast...</b>\n\nTarget users: {len(user_ids)}", parse_mode="HTML")

    sent_count = 0
    failed_count = 0

    # Broadcast to all users
    for user_id_str in user_ids:
        try:
            user_id = int(user_id_str)
            await message.bot.send_message(
                chat_id=user_id,
                text=f"📢 <b>Important Message from Admin:</b>\n\n{broadcast_message}",
                parse_mode="HTML"
            )
            sent_count += 1

            # Update status every 10 messages to avoid flood
            if sent_count % 10 == 0:
                await status_msg.edit_text(
                    f"📢 <b>Broadcasting...</b>\n\n"
                    f"✅ Sent: {sent_count}\n"
                    f"❌ Failed: {failed_count}\n"
                    f"📊 Progress: {sent_count}/{len(user_ids)}",
                    parse_mode="HTML"
                )

            # Small delay to avoid hitting rate limits
            await asyncio.sleep(0.1)

        except Exception as e:
            failed_count += 1
            logger.warning(f"Failed to send broadcast to user {user_id_str}: {e}")

    # Final status update
    await status_msg.edit_text(
        f"✅ <b>Broadcast Complete!</b>\n\n"
        f"📢 Message: {broadcast_message[:50]}{'...' if len(broadcast_message) > 50 else ''}\n"
        f"✅ Successfully sent: {sent_count}\n"
        f"❌ Failed: {failed_count}\n"
        f"📊 Total users: {len(user_ids)}",
        parse_mode="HTML"
    )

    logger.info(f"Broadcast completed: {sent_count} sent, {failed_count} failed")