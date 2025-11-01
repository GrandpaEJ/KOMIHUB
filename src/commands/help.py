from core import Message, command, logger, get_lang
import os
import importlib

lang = get_lang()


def load_all_commands():
    commands_dir = "src/commands"
    command_info = {}
    for filename in os.listdir(commands_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"src.commands.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "help") and callable(getattr(module, "help")):
                    cmd_info = module.help()
                    command_info[cmd_info["name"]] = cmd_info
                    logger.debug(f"Loaded help info for command: {cmd_info['name']}")
                else:
                    logger.debug(f"No help function found for {module_name}, skipping")
            except ImportError as e:
                logger.error(f"Failed to load command module {module_name}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error loading {module_name}: {e}")
    return command_info


def help():
    return {
        "name": "help",
        "version": "0.0.2",
        "description": "Get help for commands",
        "author": "Komihub",
        "usage": "/help [command_name]",
    }


@command("help")
async def help_command(message: Message):
    try:
        logger.info(
            lang.log_command_executed.format(
                command="help", user_id=message.from_user.id
            )
        )
        commands_info = load_all_commands()

        args = message.text.split()
        if len(args) > 1:
            # Specific command help
            cmd_name = args[1].lstrip("/")
            if cmd_name in commands_info:
                info = commands_info[cmd_name]
                help_text = (
                    f"🛠 <b>Command:</b> /{info['name']}\n"
                    f"📝 <i>{info['description']}</i>\n\n"
                    f"<b>Usage:</b> <code>{info['usage']}</code>\n"
                    f"<b>Author:</b> {info['author']}\n"
                    f"<b>Version:</b> {info['version']}"
                )
                await message.answer(help_text, parse_mode="HTML")
            else:
                await message.answer(
                    f"⚠️ Command '<code>{cmd_name}</code>' not found.\nUse /help to see all available commands.",
                    parse_mode="HTML",
                )
        else:
            # General help (box-style)
            box_top = "┌─🤖 Komihub Bot Commands─┐\n"
            box_middle = ""
            for cmd_name, info in sorted(commands_info.items()):
                box_middle += f"│ /{cmd_name:<10} - {info['description']}\n"
            box_bottom = "└─────────────────────────┘"

            help_text = f"{box_top}{box_middle}{box_bottom}"

            await message.answer(
                help_text, parse_mode="HTML", disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"Unexpected error in help command: {e}")
        await message.answer(
            "An unexpected error occurred while processing the help command. Please try again later."
        )
