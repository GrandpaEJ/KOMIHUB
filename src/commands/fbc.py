from core import Message, command, logger, get_lang, FSInputFile
import os
import tempfile
import subprocess
import config

lang = get_lang()

def help():
    return {
        "name": "fbc",
        "version": "0.0.1",
        "description": "Generate Facebook cover photo with profile image and contact info",
        "author": "Komihub",
        "usage": "/fbc John Doe john@email.com +1234567890 - Reply to an image to create Facebook cover"
    }

@command('fbc')
async def fbc_command(message: Message):
    logger.info(lang.log_command_executed.format(command='fbc', user_id=message.from_user.id))

    # Check if message is a reply to a photo
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.answer(
            "📸 Facebook Cover Generator\n\n"
            "Reply to a profile image with:\n"
            "<code>/fbc John Doe john@email.com +1234567890</code>",
            parse_mode="HTML"
        )
        return

    # Parse command arguments
    args = message.text.split(maxsplit=3)
    if len(args) < 4:
        await message.answer(
            "❌ Invalid format!\n\n"
            "Usage: <code>/fbc John Doe john@email.com +1234567890</code>",
            parse_mode="HTML"
        )
        return

    name = args[1].strip()
    email = args[2].strip()
    phone = args[3].strip()

    # Validate inputs
    if not name or not email or not phone:
        await message.answer("❌ All fields (name, email, phone) are required!")
        return

    if len(name) > 50:
        await message.answer("❌ Name is too long (max 50 characters)")
        return

    if len(email) > 50:
        await message.answer("❌ Email is too long (max 50 characters)")
        return

    if len(phone) > 20:
        await message.answer("❌ Phone number is too long (max 20 characters)")
        return

    await message.answer("🎨 Generating Facebook cover photo...")

    try:
        # Download the replied image
        photo = message.reply_to_message.photo[-1]  # Get the largest size
        file_info = await message.bot.get_file(photo.file_id)
        downloaded_file = await message.bot.download_file(file_info.file_path)

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_input:
            temp_input.write(downloaded_file.getvalue())
            input_path = temp_input.name

        # Create output path
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_output:
            output_path = temp_output.name

        # Facebook cover dimensions: 820x312 pixels
        cover_width = 820
        cover_height = 312

        # Build command for img-processor
        cmd = [
            './core/bin/img-processor',
            '-width', str(cover_width),
            '-height', str(cover_height),
            '-output', output_path,
            # Add circular profile image on the right
            '-circle-image', input_path,
            '-circle-x', '650',  # Right side
            '-circle-y', '156',  # Center vertically
            '-circle-r', '120',  # Large circle
            # Add name text on the left, large and centered
            '-text', name,
            '-text-x', '200',  # Left side
            '-text-y', '120',  # Upper middle
            '-text-color', '#FFFFFF',  # White text
            '-font-size', '48',  # Large font
            # Add email below name
            '-text', f'📧 {email}',
            '-text-x', '200',
            '-text-y', '180',
            '-text-color', '#CCCCCC',  # Light gray
            '-font-size', '24',
            # Add phone number below email
            '-text', f'📱 {phone}',
            '-text-x', '200',
            '-text-y', '220',
            '-text-color', '#CCCCCC',  # Light gray
            '-font-size', '24',
        ]

        # Run the image processor
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')

        if result.returncode != 0:
            logger.error(f"Image processing failed: {result.stderr}")
            await message.answer("❌ Failed to generate cover photo. Please try again.")
            return

        # Send the generated cover photo
        photo_file = FSInputFile(output_path)
        await message.answer_photo(
            photo=photo_file,
            caption=f"🖼️ Facebook Cover Generated!\n\n"
                    f"👤 {name}\n"
                    f"📧 {email}\n"
                    f"📱 {phone}\n\n"
                    f"Dimensions: {cover_width}x{cover_height} (Facebook cover size)"
        )

        logger.info(f"Facebook cover generated for user {message.from_user.id}")

    except Exception as e:
        logger.error(f"Facebook cover generation error: {e}")
        await message.answer("❌ An error occurred while generating the cover photo.")

    finally:
        # Clean up temporary files
        try:
            if 'input_path' in locals():
                os.unlink(input_path)
            if 'output_path' in locals():
                os.unlink(output_path)
        except:
            pass