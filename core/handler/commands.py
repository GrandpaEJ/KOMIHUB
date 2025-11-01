import os
import importlib
import sys
from ..logging import logger
from ..bot import bot_instance


def load_commands():
    commands_dir = "src/commands"
    loaded_count = 0
    failed_count = 0

    for filename in os.listdir(commands_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"src.commands.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                logger.info(f"Loaded command module: {module_name}")
                loaded_count += 1
            except ImportError as e:
                logger.error(f"Failed to load command module {module_name}: {e}")
                failed_count += 1
            except Exception as e:
                logger.error(f"Unexpected error loading {module_name}: {e}")
                failed_count += 1

    logger.info(
        f"Command loading complete: {loaded_count} loaded, {failed_count} failed"
    )
    return loaded_count, failed_count


def register_commands():
    from .. import commands

    for cmd_name, handler in commands.items():
        bot_instance.register_command(cmd_name, handler)
        logger.info(f"Registered command: {cmd_name}")


def reload_commands():
    """Reload all command modules and re-register them"""
    commands_dir = "src/commands"

    # Clear existing command registrations
    from .. import commands

    commands.clear()

    # Reload all command modules
    reloaded_count = 0
    for filename in os.listdir(commands_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"src.commands.{filename[:-3]}"
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                else:
                    importlib.import_module(module_name)
                reloaded_count += 1
                logger.debug(f"Reloaded command module: {module_name}")
            except Exception as e:
                logger.error(f"Failed to reload command module {module_name}: {e}")

    # Re-register commands
    register_commands()

    # Also reload the unknown command handler to ensure it's up to date
    try:
        if "src.commands.unknown" in sys.modules:
            importlib.reload(sys.modules["src.commands.unknown"])
            logger.debug("Reloaded unknown command handler")
    except Exception as e:
        logger.error(f"Failed to reload unknown command handler: {e}")

    logger.info(f"Reloaded and re-registered {reloaded_count} command modules")
    return reloaded_count
