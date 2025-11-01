import importlib
from .logging import logger

# Language support
langs = {"en": "core.langs.english", "bn": "core.langs.banglish"}

current_lang = "en"  # Default language


def set_lang(lang_code):
    global current_lang
    if lang_code in langs:
        current_lang = lang_code
        logger.info(f"Language set to {lang_code}")
    else:
        logger.warning(f"Unsupported language: {lang_code}")


def get_lang():
    try:
        module = importlib.import_module(langs[current_lang])
        return module
    except ImportError as e:
        logger.error(f"Failed to load language module: {e}")
        # Fallback to English
        module = importlib.import_module(langs["en"])
        return module
