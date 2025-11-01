from core import Message, command, logger, get_lang
import os
import sys
import subprocess
import config

lang = get_lang()


def help():
    return {
        "name": "restart",
        "version": "0.0.1",
        "description": "Restart the entire bot application",
        "author": "Komihub",
        "usage": "/restart",
    }


@command("restart")
async def restart(message: Message):
    # Check if user is admin
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("❌ This command is only available to administrators.")
        return

    logger.info(
        lang.log_command_executed.format(
            command="restart", user_id=message.from_user.id
        )
    )

    try:
        # Notify user that restart is starting
        restart_msg = await message.answer(
            "🔄 <b>Restarting Bot Application...</b>\n\n⏳ Initializing restart process...",
            parse_mode="HTML",
        )

        # Get the current Python executable and script
        python_exe = sys.executable
        script_path = os.path.abspath(sys.argv[0])

        # Start new process in background
        logger.info("Starting new bot process...")
        try:
            new_process = subprocess.Popen([python_exe, script_path], cwd=os.getcwd())
            logger.info(f"New process started with PID: {new_process.pid}")

            # Save the new PID
            from core.pid_manager import pid_manager

            pid_manager.save_pid(new_process.pid)

        except Exception as e:
            await restart_msg.edit_text(
                f"❌ <b>Failed to start new process!</b>\n\nError: {e}",
                parse_mode="HTML",
            )
            return

        # Wait for the new process to initialize
        import time

        time.sleep(5)

        # Check if new process is still running
        if new_process.poll() is None:
            # Process is running, wait a bit more for it to fully start
            time.sleep(2)

            await restart_msg.edit_text(
                "✅ <b>Bot Restarted Successfully!</b>\n\n🔄 New instance is now running.\n⏹️ Shutting down old instance...",
                parse_mode="HTML",
            )

            # Give a moment for the message to be seen
            time.sleep(1)

            # Stop the bot polling before exiting
            from core.bot import bot_instance

            await bot_instance.dp.stop_polling()

            # Exit current process gracefully
            logger.info("Shutting down current bot process for restart")
            os._exit(0)
        else:
            # Process has exited
            exit_code = new_process.returncode
            await restart_msg.edit_text(
                f"❌ <b>Restart Failed!</b>\n\nNew process exited with code: {exit_code}",
                parse_mode="HTML",
            )
            logger.error(f"Restart failed: New process exited with code {exit_code}")

    except Exception as e:
        logger.error(f"Restart error: {e}")
        await message.answer(
            "❌ Failed to restart the application. Check logs for details."
        )
