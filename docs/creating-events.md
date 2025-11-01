# Creating Events for Komihub Bot

This guide explains how to create event handlers for the Komihub Telegram bot framework.

## Table of Contents
- [Event System Overview](#event-system-overview)
- [Basic Event Structure](#basic-event-structure)
- [Event Types](#event-types)
- [Event Examples](#event-examples)
- [Best Practices](#best-practices)

## Event System Overview

Events in the Komihub bot are automatic responses to specific Telegram events like:
- Users joining/leaving chats
- Messages being sent
- Chat member updates
- Callback queries
- Inline queries

Events are stored in the `src/events/` directory and are automatically loaded on startup.

## Basic Event Structure

### Event File Template

```python
# src/events/my_event.py

async def handle_my_event(event):
    """Handle a specific event type"""
    # Event handling logic here
    pass

# Event registration happens automatically based on filename
```

### Event Registration

Events are registered in the main bot file (`core/bot.py`) based on their filename. The system looks for specific patterns:

- `join.py` - Chat join events
- `leave.py` - Chat leave events
- `message.py` - Message events
- `callback.py` - Callback query events

## Event Types

### Chat Member Events

Handle users joining or leaving chats:

```python
# src/events/join.py
from aiogram.types import ChatMemberUpdated
from core.logging import logger
from core.lang import get_lang

lang = get_lang()

async def handle_chat_member_update(update: ChatMemberUpdated):
    """Handle user join/leave events"""
    try:
        if update.new_chat_member.status == 'member' and update.old_chat_member.status != 'member':
            # User joined
            user = update.new_chat_member.user
            logger.info(lang.log_user_joined.format(
                user_id=user.id,
                chat_id=update.chat.id
            ))

            # Send welcome message
            await update.bot.send_message(
                chat_id=update.chat.id,
                text=f"Welcome {user.first_name}! 👋"
            )

        elif update.old_chat_member.status == 'member' and update.new_chat_member.status != 'member':
            # User left
            user = update.old_chat_member.user
            logger.info(lang.log_user_left.format(
                user_id=user.id,
                chat_id=update.chat.id
            ))

    except Exception as e:
        logger.error(f"Error in chat member update: {e}")
```

### Message Events

Handle specific message patterns or content:

```python
# src/events/song_reply.py
from aiogram.types import Message
from core.logging import logger
from core.lang import get_lang

lang = get_lang()

async def handle_message(message: Message):
    """Handle song reply functionality"""
    try:
        # Check if message is a reply to an audio file
        if (message.reply_to_message and
            message.reply_to_message.audio and
            message.text and
            message.text.lower().startswith('song')):

            audio = message.reply_to_message.audio
            song_info = f"🎵 <b>Song Information</b>\n\n"
            song_info += f"📁 Title: {audio.title or 'Unknown'}\n"
            song_info += f"👤 Artist: {audio.performer or 'Unknown'}\n"
            song_info += f"⏱️ Duration: {audio.duration // 60}:{audio.duration % 60:02d}\n"
            song_info += f"📊 Size: {audio.file_size:,} bytes\n"

            await message.answer(song_info, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error in song reply handler: {e}")
```

### Callback Query Events

Handle button presses from inline keyboards:

```python
# src/events/callback_handler.py
from aiogram.types import CallbackQuery
from core.logging import logger

async def handle_callback_query(callback: CallbackQuery):
    """Handle callback queries from inline keyboards"""
    try:
        data = callback.data

        if data.startswith('action_'):
            action = data.split('_', 1)[1]

            if action == 'confirm':
                await callback.answer("✅ Confirmed!")
                await callback.message.edit_text("Action confirmed.")

            elif action == 'cancel':
                await callback.answer("❌ Cancelled!")
                await callback.message.edit_text("Action cancelled.")

        elif data.startswith('page_'):
            page = int(data.split('_', 1)[1])
            # Handle pagination
            await callback.answer(f"Page {page}")

    except Exception as e:
        logger.error(f"Error in callback handler: {e}")
        await callback.answer("An error occurred.")
```

## Event Examples

### Welcome Message Event

```python
# src/events/welcome.py
from aiogram.types import ChatMemberUpdated
from core.logging import logger
from core.lang import get_lang
from core.database import db

lang = get_lang()

async def handle_chat_member_update(update: ChatMemberUpdated):
    """Send welcome message when users join"""
    try:
        if (update.new_chat_member.status == 'member' and
            update.old_chat_member.status != 'member'):

            user = update.new_chat_member.user
            chat = update.chat

            # Add user to database
            db.add_user(user.id, {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'chat_id': chat.id,
                'joined_at': None  # Will be set to current time
            })

            # Create welcome message
            welcome_text = f"""
🎉 <b>Welcome to {chat.title}!</b>

👤 <b>{user.first_name}</b>
"""

            if user.username:
                welcome_text += f"🆔 @{user.username}\n"
            else:
                welcome_text += f"🆔 ID: <code>{user.id}</code>\n"

            welcome_text += f"""
📅 Joined: {time.strftime('%Y-%m-%d %H:%M:%S')}

Please read the chat rules and enjoy your stay! 🚀
"""

            await update.bot.send_message(
                chat_id=chat.id,
                text=welcome_text,
                parse_mode="HTML"
            )

            logger.info(f"Sent welcome message to user {user.id} in chat {chat.id}")

    except Exception as e:
        logger.error(f"Error in welcome event: {e}")
```

### Anti-Spam Event

```python
# src/events/anti_spam.py
from aiogram.types import Message
from core.logging import logger
from core.database import db
import time

# Simple rate limiting
user_last_message = {}

async def handle_message(message: Message):
    """Basic anti-spam protection"""
    try:
        user_id = message.from_user.id
        current_time = time.time()

        # Check rate limit (max 5 messages per 10 seconds)
        if user_id in user_last_message:
            time_diff = current_time - user_last_message[user_id]
            if time_diff < 10:  # Less than 10 seconds
                message_count = getattr(handle_message, f'count_{user_id}', 0)
                if message_count >= 5:
                    # Ban spammer
                    if db.is_admin(message.from_user.id):
                        # Don't ban admins
                        return

                    try:
                        await message.bot.ban_chat_member(
                            message.chat.id,
                            user_id
                        )
                        await message.answer(f"🚫 User {user_id} banned for spamming!")
                        logger.warning(f"Banned user {user_id} for spamming")
                        return
                    except Exception as e:
                        logger.error(f"Failed to ban spammer {user_id}: {e}")

                setattr(handle_message, f'count_{user_id}', message_count + 1)
            else:
                # Reset counter
                setattr(handle_message, f'count_{user_id}', 1)
        else:
            setattr(handle_message, f'count_{user_id}', 1)

        user_last_message[user_id] = current_time

    except Exception as e:
        logger.error(f"Error in anti-spam event: {e}")
```

### Auto-Delete Service Messages

```python
# src/events/cleanup.py
from aiogram.types import Message
from core.logging import logger

async def handle_message(message: Message):
    """Clean up service messages"""
    try:
        # Delete service messages after a delay
        if message.from_user.id == message.bot.id:
            # Bot's own messages - don't delete
            return

        # Check for service messages
        service_keywords = [
            'joined the group',
            'left the group',
            'changed the group photo',
            'pinned a message',
            'unpinned a message'
        ]

        message_text = (message.text or message.caption or '').lower()

        if any(keyword in message_text for keyword in service_keywords):
            # Wait 30 seconds then delete
            import asyncio
            await asyncio.sleep(30)

            try:
                await message.delete()
                logger.info(f"Deleted service message in chat {message.chat.id}")
            except Exception as e:
                logger.warning(f"Failed to delete service message: {e}")

    except Exception as e:
        logger.error(f"Error in cleanup event: {e}")
```

### Keyword Response Event

```python
# src/events/keyword_responses.py
from aiogram.types import Message
from core.logging import logger

# Define keyword responses
KEYWORD_RESPONSES = {
    'hello': 'Hi there! 👋',
    'bye': 'Goodbye! 👋',
    'thanks': 'You\'re welcome! 😊',
    'help': 'Use /help command for assistance! 🤖',
    'ping': 'Pong! 🏓'
}

async def handle_message(message: Message):
    """Respond to specific keywords"""
    try:
        if not message.text:
            return

        text = message.text.lower().strip()

        # Check for exact keyword matches
        for keyword, response in KEYWORD_RESPONSES.items():
            if text == keyword:
                await message.reply(response)
                logger.info(f"Responded to keyword '{keyword}' in chat {message.chat.id}")
                return

        # Check for keyword in message
        for keyword, response in KEYWORD_RESPONSES.items():
            if keyword in text:
                # Only respond if message is short (avoid spam)
                if len(text.split()) <= 3:
                    await message.reply(response)
                    logger.info(f"Responded to keyword '{keyword}' in message")
                    return

    except Exception as e:
        logger.error(f"Error in keyword response event: {e}")
```

## Best Practices

### 1. Error Handling
Always wrap event handlers in try-catch blocks:

```python
async def handle_event(event):
    try:
        # Event logic here
        pass
    except Exception as e:
        logger.error(f"Error in event handler: {e}")
```

### 2. Logging
Log important events and errors:

```python
logger.info(f"Event triggered: {event_type}")
logger.error(f"Event error: {e}")
```

### 3. Performance
- Keep event handlers lightweight
- Avoid blocking operations
- Use async/await properly

### 4. Database Usage
Use the database for persistent data:

```python
from core.database import db

# Store event data
db.add_user(user_id, {'event_data': 'value'})
```

### 5. Rate Limiting
Implement rate limiting for resource-intensive operations:

```python
import time

last_execution = {}

async def rate_limited_handler(event):
    current_time = time.time()
    if current_time - last_execution.get('handler', 0) < 60:  # 1 minute cooldown
        return

    last_execution['handler'] = current_time
    # Handler logic
```

### 6. Configuration
Use config values for customizable behavior:

```python
import config

if config.ENABLE_WELCOME_MESSAGES:
    await send_welcome_message(event)
```

### 7. File Organization
- One event type per file
- Descriptive filenames
- Clear function names

### 8. Testing
Test events in different scenarios:
- Group chats vs private chats
- Different user types (admin, member, etc.)
- Error conditions

### 9. Documentation
Add docstrings to event functions:

```python
async def handle_join_event(update: ChatMemberUpdated):
    """Handle user join events with welcome messages"""
    pass
```

### 10. Cleanup
Clean up resources and temporary data:

```python
finally:
    # Cleanup code here
    pass
```

## Event Registration

Events are automatically registered based on filename patterns. The system looks for:

- Files ending with `.py` in `src/events/`
- Functions that match expected signatures
- Automatic registration in the bot dispatcher

## Need Help?

- Check existing events in `src/events/` for examples
- Review Telegram Bot API documentation for event types
- Use logging to debug event execution
- Test events in a development environment first