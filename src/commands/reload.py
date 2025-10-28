from core import Message, command, logger, get_lang
from core.handler.commands import reload_commands
from core.handler.events import reload_events
import importlib
import sys
import os
import config

lang = get_lang()

def help():
    return {
        "name": "reload",
        "version": "0.0.1",
        "description": "Hot reload all commands and events",
        "author": "Komihub",
        "usage": "/reload"
    }

@command('reload')
async def reload(message: Message):
    # Check if user is admin
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("❌ This command is only available to administrators.")
        return

    logger.info(lang.log_command_executed.format(command='reload', user_id=message.from_user.id))

    try:
        # Reload commands and events only (not core modules)
        commands_reloaded = reload_commands()
        events_reloaded = reload_events()

        total_reloaded = commands_reloaded + events_reloaded

        # Also reload the help command to update command list
        try:
            import importlib
            if 'src.commands.help' in importlib.sys.modules:
                importlib.reload(importlib.sys.modules['src.commands.help'])
                logger.debug("Reloaded help command for updated command list")
        except Exception as e:
            logger.error(f"Failed to reload help command: {e}")

        await message.answer(
            f"🔄 <b>Command Reload Complete!</b>\n\n"
            f"🤖 Commands: {commands_reloaded}\n"
            f"📡 Events: {events_reloaded}\n"
            f"📊 Total: {total_reloaded}\n\n"
            f"All commands and events have been refreshed!",
            parse_mode="HTML"
        )
        logger.info(f"Command reload completed: {total_reloaded} modules reloaded")

    except Exception as e:
        logger.error(f"Reload error: {e}")
        await message.answer("❌ Failed to reload modules. Check logs for details.")