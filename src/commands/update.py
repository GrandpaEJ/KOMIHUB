"""Update command for version checking and auto-updates"""

from core import Message, command, logger, get_lang
import asyncio

lang = get_lang()


def help():
    return {
        "name": "update",
        "version": "0.0.1",
        "description": "Check for updates and manage auto-updates",
        "author": "Komihub",
        "usage": "/update check - Check for available updates\n/update update - Perform manual update\n/update status - Show current version status",
    }


@command("update")
async def update_command(message: Message):
    logger.info(
        lang.log_command_executed.format(command="update", user_id=message.from_user.id)
    )

    # Check if user is admin
    from core import bot
    bot_instance = bot.get_bot()
    if message.from_user.id != bot_instance.config.ADMIN_ID:
        await message.answer("❌ This command is only available to admins.")
        return

    args = message.text.split()
    
    if len(args) < 2:
        await message.answer(
            "🔄 <b>Update Command</b>\n\n"
            "Available options:\n"
            "/update check - Check for updates\n"
            "/update update - Perform manual update\n"
            "/update status - Show version status\n"
            f"Auto-update: {'✅ Enabled' if bot_instance.config.AUTO_UPDATE else '❌ Disabled'}\n"
            f"GitHub: {bot_instance.config.GITHUB_REPO}",
            parse_mode="HTML",
        )
        return

    subcommand = args[1].lower()

    if subcommand == "check":
        await check_for_updates(message)
    elif subcommand == "update":
        await perform_manual_update(message)
    elif subcommand == "status":
        await show_update_status(message)
    else:
        await message.answer("❌ Unknown subcommand. Use /update for help.")


async def check_for_updates(message: Message):
    """Check for available updates"""
    try:
        await message.answer("🔍 Checking for updates...", parse_mode="HTML")
        
        from core.version_tracker import version_tracker
        
        updates_available, message_text = await version_tracker.check_for_updates()
        
        if updates_available:
            response = f"📦 <b>Updates Available</b>\n\n{message_text}\n\n"
            response += "Use /update update to install updates automatically."
            if not version_tracker.current_versions.get("auto_update"):
                response += "\n\n⚠️ Auto-update is currently disabled."
        else:
            response = f"✅ <b>No Updates</b>\n\n{message_text}"
        
        await message.answer(response, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Update check failed: {e}")
        await message.answer("❌ Failed to check for updates. Please try again.")


async def perform_manual_update(message: Message):
    """Perform manual update"""
    try:
        await message.answer("🔄 Starting update process...", parse_mode="HTML")
        
        from core.version_tracker import version_tracker
        
        # Check if updates are available first
        updates_available, check_message = await version_tracker.check_for_updates()
        if not updates_available:
            await message.answer(f"✅ {check_message}", parse_mode="HTML")
            return
        
        # Perform the update
        success, result_message = await version_tracker.perform_update()
        
        if success:
            response = f"✅ <b>Update Successful</b>\n\n{result_message}\n\n"
            response += "🚀 Restart the bot to apply changes."
            await message.answer(response, parse_mode="HTML")
            
            # Notify admin that restart is recommended
            try:
                await message.answer(
                    "💡 <b>Tip:</b> You can use /restart to restart the bot with new updates.",
                    parse_mode="HTML"
                )
            except:
                pass
        else:
            await message.answer(f"❌ <b>Update Failed</b>\n\n{result_message}", parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Manual update failed: {e}")
        await message.answer("❌ Failed to perform update. Please check logs.")


async def show_update_status(message: Message):
    """Show current version status"""
    try:
        from core.version_tracker import version_tracker
        
        # Load current versions
        versions = version_tracker.current_versions
        
        status_msg = "📊 <b>Version Status</b>\n\n"
        status_msg += f"🤖 Bot Version: <code>{versions.get('v', '0.0.1')}</code>\n"
        status_msg += f"🛠️ Tool Version: <code>{versions.get('tool', '0.0.1')}</code>\n"
        status_msg += f"💫 Kumi Version: <code>{versions.get('komi', '0.0.1')}</code>\n\n"
        
        # Check git status
        try:
            import subprocess
            result = subprocess.run(['git', 'log', '-1', '--pretty=format:%h %s'], 
                                  capture_output=True, text=True, check=True)
            latest_commit = result.stdout.strip()
            status_msg += f"📝 Latest Commit: <code>{latest_commit}</code>\n"
        except:
            status_msg += "📝 Latest Commit: <code>Unable to fetch</code>\n"
        
        # Check if working directory is clean
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                status_msg += "🔧 Status: <b>Working directory has changes</b>\n"
            else:
                status_msg += "🔧 Status: <b>Clean working directory</b>\n"
        except:
            status_msg += "🔧 Status: <b>Unable to check git status</b>\n"
        
        status_msg += f"🔄 Auto-update: {'✅ Enabled' if version_tracker.current_versions.get('auto_update') else '❌ Disabled'}\n"
        status_msg += f"🔗 Repository: <code>{version_tracker.current_versions.get('repo', 'N/A')}</code>\n"
        
        await message.answer(status_msg, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Failed to show update status: {e}")
        await message.answer("❌ Failed to fetch version status. Please try again.")