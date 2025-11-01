from core import Message, command, logger, get_lang
import config

lang = get_lang()


# -------------
# help
# -------------
def help():
    return {
        "name": "start",
        "version": "0.0.1",
        "description": "Start bot",
        "author": config.ADMIN_NAME,
        "usage": "/start",
    }


@command("start")
async def start(message: Message):
    logger.info(
        lang.log_command_executed.format(command="start", user_id=message.from_user.id)
    )
    await message.answer("Hello!")


@command
async def echo(message: Message):
    logger.info(
        lang.log_command_executed.format(command="echo", user_id=message.from_user.id)
    )
    await message.answer(message.text)
