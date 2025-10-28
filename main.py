import asyncio
from core.bot import bot_instance
from core.handler.commands import load_commands, register_commands
from core.handler.events import load_events, register_events
from core.pid_manager import pid_manager
from core import logger
import config

def print_banner():
    banner = """
╔══════════════════════════════════════╗
║              KOMIHUB BOT              ║
║        Telegram Bot Framework        ║
╚══════════════════════════════════════╝
"""
    print(banner)
    print(f"🤖 Bot Name: {config.BOT_NAME}")
    print(f"👤 Admin: {config.ADMIN_NAME}")
    print("=" * 40)

async def main():
    print_banner()

    # Save current PID and cleanup old instances
    pid_manager.save_pid()
    killed = pid_manager.cleanup_old_instances()
    if killed > 0:
        print(f"🧹 Cleaned up {killed} old bot instances")

    # Load and register commands
    try:
        loaded, failed = load_commands()
        logger.info(f"Commands loaded: {loaded}, failed: {failed}")
        if failed > 0:
            logger.warning(f"{failed} commands failed to load but bot will continue")
    except Exception as e:
        logger.error(f"Critical error loading commands: {e}")

    try:
        register_commands()
        logger.info("Commands registered successfully")
    except Exception as e:
        logger.error(f"Critical error registering commands: {e}")

    # Load and register events
    try:
        loaded, failed = load_events()
        logger.info(f"Events loaded: {loaded}, failed: {failed}")
        if failed > 0:
            logger.warning(f"{failed} events failed to load but bot will continue")
    except Exception as e:
        logger.error(f"Critical error loading events: {e}")

    try:
        register_events()
        logger.info("Events registered successfully")
    except Exception as e:
        logger.error(f"Critical error registering events: {e}")

    # Start the bot
    try:
        await bot_instance.start_polling()
    except Exception as e:
        logger.error(f"Critical error during bot polling: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
