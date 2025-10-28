import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from .logging import logger
from .lang import get_lang
from .database import db
from .middleware import UserMiddleware
import config

class KomihubBot:
    def __init__(self):
        self.bot = Bot(token=config.BOT_TOKEN)
        self.dp = Dispatcher()
        self.lang = get_lang()

        # Register middleware
        self.dp.message.middleware.register(UserMiddleware())

    async def start_polling(self):
        # Register unknown command handler
        self.dp.message.register(self.handle_unknown_command)

        # Update bot stats
        db.update_bot_stats(
            bot_name=config.BOT_NAME,
            online_since=asyncio.get_event_loop().time()
        )

        logger.info(self.lang.log_bot_started)
        await self.dp.start_polling(self.bot)

    def register_command(self, command_name, handler):
        try:
            self.dp.message.register(handler, Command(command_name))
            logger.debug(f"Successfully registered command: {command_name}")
        except Exception as e:
            logger.error(f"Failed to register command {command_name}: {e}")
            raise

    def register_event(self, event_type, handler):
        if event_type == 'chat_member':
            self.dp.chat_member.register(handler)
        # Add more event types as needed

    async def handle_unknown_command(self, message: Message):
        """Handle unknown commands"""
        try:
            from src.commands.unknown import handle_unknown_command
            await handle_unknown_command(message)
        except Exception as e:
            logger.error(f"Error in unknown command handler: {e}")
            # Fallback response
            await message.answer("❓ Unknown command. Use /help to see available commands.")

bot_instance = KomihubBot()