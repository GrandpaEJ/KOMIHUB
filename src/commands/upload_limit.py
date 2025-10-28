from core import Message, command, logger, get_lang
import config

lang = get_lang()

def help():
    return {
        "name": "upload_limit",
        "version": "0.0.1",
        "description": "Check Telegram upload limits and file size restrictions",
        "author": "Komihub",
        "usage": "/upload_limit - Show current upload limits"
    }

@command('upload_limit')
async def upload_limit_command(message: Message):
    logger.info(lang.log_command_executed.format(command='upload_limit', user_id=message.from_user.id))

    # Telegram upload limits (as of 2024)
    limits = {
        "Photo": "10 MB",
        "Video": "2 GB (Premium: 4 GB)",
        "Audio": "2 GB",
        "Document": "2 GB (Premium: 4 GB)",
        "Sticker": "512 KB",
        "Animation (GIF)": "2 GB",
        "Voice message": "1 MB",
        "Video note": "2 GB"
    }

    # Premium benefits
    premium_benefits = [
        "Upload files up to 4 GB",
        "Download files up to 4 GB",
        "Faster download speeds",
        "No upload size limits for some file types"
    ]

    response = "📤 <b>Telegram Upload Limits</b>\n\n"

    response += "<b>📁 File Size Limits:</b>\n"
    for file_type, limit in limits.items():
        response += f"• {file_type}: {limit}\n"

    response += "\n<b>⭐ Premium Benefits:</b>\n"
    for benefit in premium_benefits:
        response += f"• {benefit}\n"

    response += "\n<b>ℹ️ Notes:</b>\n"
    response += "• Limits apply per file\n"
    response += "• Some formats may have additional restrictions\n"
    response += "• Bot uploads may have different limits\n"
    response += "• Premium increases most limits to 4 GB"

    await message.answer(response, parse_mode="HTML")