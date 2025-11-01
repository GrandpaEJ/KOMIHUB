from aiogram import BaseMiddleware
from aiogram.types import Message
from .database import db
from .logging import logger
from .lang import get_lang

lang = get_lang()


class UserMiddleware(BaseMiddleware):
    """Middleware to handle user registration and checks"""

    async def __call__(self, handler, event: Message, data):
        try:
            # Skip if no user (e.g., channel posts)
            if not hasattr(event, "from_user") or not event.from_user:
                return await handler(event, data)

            user_id = event.from_user.id

            # Check if user is banned
            if db.is_banned(user_id):
                ban_info = db.get_ban_info(user_id)
                if ban_info:
                    reason = ban_info.get("reason", "No reason provided")
                    await event.answer(
                        f"❌ You are banned from using this bot.\n\nReason: {reason}"
                    )
                    logger.warning(
                        f"Banned user {user_id} tried to use bot: {event.text}"
                    )
                    return
                else:
                    # Remove invalid ban entry
                    db.unban_user(user_id)

            # Add/update user in database
            db.add_user(
                user_id,
                {
                    "username": event.from_user.username,
                    "first_name": event.from_user.first_name,
                    "last_name": event.from_user.last_name,
                },
            )

            # Update user activity
            db.update_user(user_id, last_seen=None)  # Will set current timestamp

            # Track command usage if it's a command
            if event.text and event.text.startswith("/"):
                command_name = event.text.split()[0].lstrip("/")
                db.increment_command_usage(command_name, user_id)

            # Continue with handler
            return await handler(event, data)

        except Exception as e:
            logger.error(
                f"Middleware error for user {event.from_user.id if event.from_user else 'unknown'}: {e}"
            )
            # Continue with handler even if middleware fails
            return await handler(event, data)
