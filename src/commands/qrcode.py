from core import Message, command, logger, get_lang
import pyqrcode
import io
import config

lang = get_lang()

def help():
    return {
        "name": "qrcode",
        "version": "0.0.1",
        "description": "Generate QR codes from text",
        "author": "Komihub",
        "usage": "/qrcode <text> - Generate QR code from text"
    }

@command('qrcode')
async def qrcode_command(message: Message):
    logger.info(lang.log_command_executed.format(command='qrcode', user_id=message.from_user.id))

    # Get text from command arguments
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Please provide text to generate QR code.\n\nUsage: /qrcode <text>")
        return

    text = args[1].strip()

    if not text:
        await message.answer("Please provide valid text to generate QR code.")
        return

    if len(text) > 1000:
        await message.answer("Text is too long. Maximum 1000 characters allowed.")
        return

    try:
        # Generate QR code
        qr = pyqrcode.create(text)

        # Create PNG buffer
        buffer = io.BytesIO()
        qr.png(buffer, scale=6)
        buffer.seek(0)

        # Send the QR code image
        await message.answer_photo(
            photo=buffer,
            caption=f"🔳 QR Code for: <code>{text[:50]}{'...' if len(text) > 50 else ''}</code>",
            parse_mode="HTML"
        )

        logger.info(f"QR code generated for user {message.from_user.id}")

    except Exception as e:
        logger.error(f"Error generating QR code: {e}")
        await message.answer("❌ Failed to generate QR code. Please try again.")