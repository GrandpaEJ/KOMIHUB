# Creating New Commands for Komihub Bot

This guide explains how to create new commands for the Komihub Telegram bot framework.

## Table of Contents
- [Basic Command Structure](#basic-command-structure)
- [Command Registration](#command-registration)
- [Help Function](#help-function)
- [Command Examples](#command-examples)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)

## Basic Command Structure

All commands are stored in the `src/commands/` directory. Each command should be in its own Python file.

### Minimal Command File

```python
from core import Message, command, logger, get_lang

lang = get_lang()

def help():
    return {
        "name": "my_command",
        "version": "1.0.0",
        "description": "Description of what this command does",
        "author": "Your Name",
        "usage": "/my_command [parameters]"
    }

@command('my_command')
async def my_command(message: Message):
    logger.info(lang.log_command_executed.format(command='my_command', user_id=message.from_user.id))

    # Your command logic here
    await message.answer("Hello! This is my new command.")
```

## Command Registration

### Using the @command Decorator

The `@command` decorator automatically registers your function as a bot command:

```python
@command('command_name')
async def command_function(message: Message):
    # Command implementation
    pass
```

### Multiple Commands in One File

You can define multiple commands in a single file:

```python
@command('cmd1')
async def command_one(message: Message):
    await message.answer("Command 1 executed")

@command('cmd2')
async def command_two(message: Message):
    await message.answer("Command 2 executed")
```

## Help Function

Every command file must have a `help()` function that returns a dictionary with command information:

```python
def help():
    return {
        "name": "command_name",        # Command name (required)
        "version": "1.0.0",           # Version (required)
        "description": "What it does", # Description (required)
        "author": "Your Name",        # Author name (required)
        "usage": "/command [params]"  # Usage syntax (required)
    }
```

## Command Examples

### Simple Text Response

```python
from core import Message, command, logger, get_lang

lang = get_lang()

def help():
    return {
        "name": "hello",
        "version": "1.0.0",
        "description": "Say hello to the bot",
        "author": "Komihub",
        "usage": "/hello"
    }

@command('hello')
async def hello(message: Message):
    logger.info(lang.log_command_executed.format(command='hello', user_id=message.from_user.id))

    user_name = message.from_user.first_name or "User"
    await message.answer(f"Hello {user_name}! 👋")
```

### Command with Parameters

```python
from core import Message, command, logger, get_lang

lang = get_lang()

def help():
    return {
        "name": "echo",
        "version": "1.0.0",
        "description": "Echo back the message",
        "author": "Komihub",
        "usage": "/echo <message>"
    }

@command('echo')
async def echo(message: Message):
    logger.info(lang.log_command_executed.format(command='echo', user_id=message.from_user.id))

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Usage: /echo <message>")
        return

    text_to_echo = args[1]
    await message.answer(f"📢 {text_to_echo}")
```

### Admin-Only Command

```python
from core import Message, command, logger, get_lang
from core.database import db

lang = get_lang()

def help():
    return {
        "name": "admin_only",
        "version": "1.0.0",
        "description": "Admin-only command example",
        "author": "Komihub",
        "usage": "/admin_only"
    }

@command('admin_only')
async def admin_only(message: Message):
    # Check if user is admin
    if not db.is_admin(message.from_user.id):
        await message.answer("❌ This command is only available to administrators.")
        return

    logger.info(lang.log_command_executed.format(command='admin_only', user_id=message.from_user.id))

    await message.answer("✅ Admin command executed successfully!")
```

### Reply-Based Command

```python
from core import Message, command, logger, get_lang

lang = get_lang()

def help():
    return {
        "name": "reply_test",
        "version": "1.0.0",
        "description": "Test command that works with replies",
        "author": "Komihub",
        "usage": "/reply_test [text] - Reply to a message to quote it"
    }

@command('reply_test')
async def reply_test(message: Message):
    logger.info(lang.log_command_executed.format(command='reply_test', user_id=message.from_user.id))

    if message.reply_to_message:
        # User replied to a message
        original_text = message.reply_to_message.text or "[Non-text message]"
        args = message.text.split(maxsplit=1)
        quote_text = args[1] if len(args) > 1 else "Quote"

        await message.answer(f"💬 {quote_text}:\n\n{original_text}")
    else:
        # No reply, just echo the text
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("Usage: /reply_test <text>\nOr reply to a message with /reply_test")
            return

        await message.answer(f"📢 {args[1]}")
```

### File Upload/Download Command

```python
from core import Message, command, logger, get_lang, FSInputFile
import tempfile
import os

lang = get_lang()

def help():
    return {
        "name": "process_file",
        "version": "1.0.0",
        "description": "Process uploaded files",
        "author": "Komihub",
        "usage": "/process_file - Reply to a document or photo"
    }

@command('process_file')
async def process_file(message: Message):
    logger.info(lang.log_command_executed.format(command='process_file', user_id=message.from_user.id))

    if not message.reply_to_message or not (message.reply_to_message.document or message.reply_to_message.photo):
        await message.answer("Please reply to a document or photo with this command.")
        return

    await message.answer("🔄 Processing file...")

    try:
        # Download the file
        if message.reply_to_message.document:
            file_info = await message.bot.get_file(message.reply_to_message.document.file_id)
        else:
            # Photo - get the largest size
            photo = message.reply_to_message.photo[-1]
            file_info = await message.bot.get_file(photo.file_id)

        downloaded_file = await message.bot.download_file(file_info.file_path)

        # Process the file (example: just get file size)
        file_size = len(downloaded_file.getvalue())
        file_name = message.reply_to_message.document.file_name if message.reply_to_message.document else "photo.jpg"

        await message.answer(
            f"✅ File processed!\n\n"
            f"📁 Name: {file_name}\n"
            f"📊 Size: {file_size:,} bytes\n"
            f"📂 Type: {'Document' if message.reply_to_message.document else 'Photo'}"
        )

    except Exception as e:
        logger.error(f"File processing error: {e}")
        await message.answer("❌ Failed to process the file.")
```

## Advanced Features

### Using Database

```python
from core import Message, command, logger, get_lang
from core.database import db

@command('user_stats')
async def user_stats(message: Message):
    user_id = message.from_user.id

    # Get user data
    user_data = db.get_user(user_id)
    if not user_data:
        await message.answer("No data found for this user.")
        return

    # Get command usage stats
    command_stats = db.get_command_stats()

    response = f"📊 <b>User Statistics</b>\n\n"
    response += f"👤 User ID: <code>{user_id}</code>\n"
    response += f"📅 Joined: {user_data.get('joined_at', 'Unknown')}\n"
    response += f"🎯 Role: {user_data.get('role', 'user')}\n"

    await message.answer(response, parse_mode="HTML")
```

### Using Configuration

```python
from core import Message, command, logger, get_lang
import config

@command('bot_info')
async def bot_info(message: Message):
    response = f"🤖 <b>Bot Information</b>\n\n"
    response += f"📛 Name: {config.BOT_NAME}\n"
    response += f"👤 Owner: {config.ADMIN_NAME}\n"
    response += f"🆔 Owner ID: <code>{config.ADMIN_ID}</code>\n"
    response += f"🌐 Language: {config.DEFAULT_LANG}\n"

    await message.answer(response, parse_mode="HTML")
```

### Error Handling

```python
@command('risky_command')
async def risky_command(message: Message):
    try:
        # Some risky operation
        result = some_risky_function()

        await message.answer(f"✅ Success: {result}")

    except ValueError as e:
        await message.answer(f"❌ Invalid input: {e}")

    except Exception as e:
        logger.error(f"Unexpected error in risky_command: {e}")
        await message.answer("❌ An unexpected error occurred. Please try again later.")
```

### Async Operations

```python
import asyncio

@command('async_example')
async def async_example(message: Message):
    # Show progress
    progress_msg = await message.answer("🔄 Starting async operation...")

    # Simulate async work
    await asyncio.sleep(2)
    await progress_msg.edit_text("🔄 Processing... 50%")

    await asyncio.sleep(2)
    await progress_msg.edit_text("✅ Operation completed!")

    # Clean up
    await asyncio.sleep(1)
    await progress_msg.delete()
```

## Best Practices

### 1. Always Include Help Function
Every command file must have a `help()` function with complete information.

### 2. Use Proper Logging
Always log command execution and important events:

```python
logger.info(lang.log_command_executed.format(command='command_name', user_id=message.from_user.id))
```

### 3. Handle Errors Gracefully
Use try-catch blocks and provide meaningful error messages to users.

### 4. Validate Input
Check command arguments and provide usage instructions when invalid.

### 5. Use HTML Formatting
Format messages with HTML tags for better readability:

```python
await message.answer(
    "<b>Success!</b> Operation completed.\n"
    "<code>Result: 12345</code>",
    parse_mode="HTML"
)
```

### 6. Respect Rate Limits
Add delays between operations to avoid hitting Telegram's rate limits.

### 7. Clean Up Resources
Always clean up temporary files and resources in finally blocks.

### 8. Check Permissions
Use database checks for admin-only commands:

```python
if not db.is_admin(message.from_user.id):
    await message.answer("❌ Admin access required.")
    return
```

### 9. File Naming
Use descriptive filenames: `my_command.py`, `user_management.py`, etc.

### 10. Documentation
Add comments explaining complex logic and keep code readable.

## Testing Your Command

1. Save your command file in `src/commands/`
2. Restart the bot or use `/reload` command
3. Test with `/help` to see if your command appears
4. Test the command functionality
5. Check logs for any errors

## Command File Template

Use this template for new commands:

```python
from core import Message, command, logger, get_lang
# Import other modules as needed

lang = get_lang()

def help():
    return {
        "name": "command_name",
        "version": "1.0.0",
        "description": "Brief description of what this command does",
        "author": "Your Name",
        "usage": "/command_name [parameters]"
    }

@command('command_name')
async def command_name(message: Message):
    logger.info(lang.log_command_executed.format(command='command_name', user_id=message.from_user.id))

    # Command implementation here
    await message.answer("Command executed successfully!")
```

## Need Help?

- Check existing commands in `src/commands/` for examples
- Review the core modules in `core/` for available utilities
- Use `/help` command in the bot to see all available commands
- Check logs for error messages during development