"""Automatic update checking event handler"""

import asyncio
from datetime import datetime

from core import logger, get_lang
import config

lang = get_lang()


async def handle_update_check():
    """Handle automatic update checking"""
    if not config.AUTO_UPDATE:
        return
    
    try:
        from core.version_tracker import version_tracker
        
        # Check if it's time to check for updates
        if not version_tracker.should_check_for_updates():
            return
        
        logger.info("Checking for updates...")
        
        # Check for updates
        updates_available, message = await version_tracker.check_for_updates()
        
        if updates_available:
            logger.info(f"Updates available: {message}")
            
            # Log available updates
            logger.info("Auto-updating to latest version...")
            
            # Perform automatic update
            success, result = await version_tracker.perform_update()
            
            if success:
                logger.info(f"Auto-update successful: {result}")
                
                # Notify admin about successful update
                try:
                    from core.bot import bot_instance
                    admin_id = config.ADMIN_ID
                    await bot_instance.bot.send_message(
                        admin_id,
                        f"🔄 <b>Auto-Update Successful</b>\n\n{result}\n\n"
                        "💡 Use /restart to restart the bot with new features.",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin about update: {e}")
            else:
                logger.warning(f"Auto-update failed: {result}")
        
    except Exception as e:
        logger.error(f"Update check failed: {e}")


# Register the event
from core.bot import bot_instance

# Schedule periodic update checks
async def schedule_update_checks():
    """Schedule periodic update checks"""
    while True:
        try:
            await handle_update_check()
            await asyncio.sleep(config.UPDATE_CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Update check scheduling error: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes on error


# Start the update checker
def start_update_checker():
    """Start the background update checker"""
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(schedule_update_checks())
        logger.info("Started automatic update checker")
    except Exception as e:
        logger.error(f"Failed to start update checker: {e}")


# Register event for bot startup
bot_instance.register_event("startup", start_update_checker)