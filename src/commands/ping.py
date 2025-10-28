from core import Message, command, logger, get_lang
import time

lang = get_lang()

def help():
    return {
        "name": "ping",
        "version": "0.0.1",
        "description": "Check bot response time",
        "author": "Komihub",
        "usage": "/ping"
    }

@command('ping')
async def ping(message: Message):
    start_time = time.time()
    sent_message = await message.answer("Pong!")
    end_time = time.time()
    response_time = round((end_time - start_time) * 1000, 2)
    await sent_message.edit_text(f"Pong! Response time: {response_time}ms")
    logger.info(lang.log_command_executed.format(command='ping', user_id=message.from_user.id))