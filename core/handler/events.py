import os
import importlib
import sys
from ..logging import logger


def load_events():
    events_dir = "src/events"
    loaded_count = 0
    failed_count = 0

    for filename in os.listdir(events_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"src.events.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                logger.info(f"Loaded event module: {module_name}")
                loaded_count += 1
            except ImportError as e:
                logger.error(f"Failed to load event module {module_name}: {e}")
                failed_count += 1
            except Exception as e:
                logger.error(f"Unexpected error loading {module_name}: {e}")
                failed_count += 1

    logger.info(f"Event loading complete: {loaded_count} loaded, {failed_count} failed")
    return loaded_count, failed_count


def register_events():
    # Events are registered in their respective modules
    # This function can be expanded if needed for centralized event registration
    pass


def reload_events():
    """Reload all event modules"""
    events_dir = "src/events"

    # Reload all event modules
    reloaded_count = 0
    for filename in os.listdir(events_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"src.events.{filename[:-3]}"
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                else:
                    importlib.import_module(module_name)
                reloaded_count += 1
                logger.debug(f"Reloaded event module: {module_name}")
            except Exception as e:
                logger.error(f"Failed to reload event module {module_name}: {e}")

    logger.info(f"Reloaded {reloaded_count} event modules")
    return reloaded_count
