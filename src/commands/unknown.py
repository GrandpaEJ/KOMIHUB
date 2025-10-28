from core import Message, logger, get_lang
from core.database import db

lang = get_lang()

async def handle_unknown_command(message: Message):
    """Handle unknown commands with better categorization"""
    try:
        # Log unknown command
        logger.warning(f"Unknown command from user {message.from_user.id}: {message.text}")

        # Update user data (add to database if not exists)
        db.add_user(message.from_user.id, {
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name
        })

        # Extract command name
        command_text = message.text.split()[0].lstrip('/').lower()

        # Check if command is disabled
        if db.is_command_disabled(command_text):
            await message.answer("❌ This command is currently disabled by administrators.")
            return

        # Categorize unknown commands
        if command_text in ['start', 'help', 'ping', 'info', 'stats']:
            # Common commands that might be expected
            response = f"❓ <b>Command not found:</b> <code>/{command_text}</code>\n\n"
            response += "💡 <b>Did you mean:</b>\n"
            if command_text == 'start':
                response += "• Use /help to see all available commands\n"
            elif command_text == 'help':
                response += "• The help command should be available\n"
            elif command_text == 'ping':
                response += "• Try /ping to check bot response time\n"
            elif command_text == 'info':
                response += "• Use /info for bot information\n"
            elif command_text == 'stats':
                response += "• Use /stats for bot statistics\n"
            response += "\n🔄 <b>Try:</b> /reload if commands were recently added"

        elif any(keyword in command_text for keyword in ['dl', 'download', 'music', 'video', 'audio']):
            # Download-related commands
            response = f"❓ <b>Download command not found:</b> <code>/{command_text}</code>\n\n"
            response += "📥 <b>Available download commands:</b>\n"
            response += "• /yt_music - YouTube audio download\n"
            response += "• /social_dl - Social media downloads\n"
            response += "• /upload_limit - Check upload limits\n"

        elif any(keyword in command_text for keyword in ['qr', 'code', 'qrcode']):
            # QR code related
            response = f"❓ <b>QR command not found:</b> <code>/{command_text}</code>\n\n"
            response += "🔳 <b>Available:</b> /qrcode <text> - Generate QR codes\n"

        elif any(keyword in command_text for keyword in ['admin', 'manage', 'ban', 'kick']):
            # Admin commands
            response = f"❓ <b>Admin command not found:</b> <code>/{command_text}</code>\n\n"
            response += "👑 <b>Admin commands (owner only):</b>\n"
            response += "• /add_admin, /remove_admin, /list_admins\n"
            response += "• /ban, /kick - User management\n"
            response += "• /broadcast - Send messages to all users\n"

        elif len(command_text) <= 2:
            # Very short commands, might be typos
            response = f"❓ <b>Short command:</b> <code>/{command_text}</code>\n\n"
            response += "💡 This might be a typo. Use /help for available commands.\n"

        else:
            # Generic unknown command
            response = f"❓ <b>Unknown command:</b> <code>/{command_text}</code>\n\n"
            response += f"{lang.unknown_command}\n\n"
            response += "💡 <b>Try:</b> /help - List all commands\n"
            response += "🔄 <b>Or:</b> /reload - Refresh commands\n"

        await message.answer(response, parse_mode="HTML")

        # Track unknown command usage
        db.increment_command_usage('unknown', message.from_user.id)

    except Exception as e:
        logger.error(f"Error handling unknown command: {e}")
        # Fallback with basic error message
        try:
            await message.answer("❌ An error occurred while processing your command. Please try again.")
        except Exception as fallback_error:
            logger.error(f"Fallback error handling also failed: {fallback_error}")