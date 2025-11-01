import logging
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.DEBUG:
            color = Fore.CYAN
        elif record.levelno == logging.INFO:
            color = Fore.GREEN
        elif record.levelno == logging.WARNING:
            color = Fore.YELLOW
        elif record.levelno == logging.ERROR:
            color = Fore.RED
        elif record.levelno == logging.CRITICAL:
            color = Fore.MAGENTA
        else:
            color = Fore.WHITE

        record.levelname = f"{color}{record.levelname}{Style.RESET_ALL}"
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)


# Configure logger
logger = logging.getLogger("komihub_bot")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setFormatter(
    ColoredFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger.addHandler(console_handler)


def log_command(command, user):
    logger.info(f"Command '{command}' executed by user {user}")


def log_event(event, details):
    logger.info(f"Event '{event}': {details}")


def log_error(error):
    logger.error(f"Error: {error}")


def log_warning(warning):
    logger.warning(f"Warning: {warning}")


def log_debug(debug):
    logger.debug(f"Debug: {debug}")
