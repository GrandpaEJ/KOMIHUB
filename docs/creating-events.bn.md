# Komihub Bot-এ ইভেন্ট তৈরি করা

এই গাইডটি Komihub টেলিগ্রাম বট ফ্রেমওয়ার্কে ইভেন্ট হ্যান্ডলার তৈরি করার পদ্ধতি ব্যাখ্যা করে।

## সূচিপত্র
- [ইভেন্ট সিস্টেম ওভারভিউ](#ইভেন্ট-সিস্টেম-ওভারভিউ)
- [বেসিক ইভেন্ট স্ট্রাকচার](#বেসিক-ইভেন্ট-স্ট্রাকচার)
- [ইভেন্ট টাইপ](#ইভেন্ট-টাইপ)
- [ইভেন্ট উদাহরণ](#ইভেন্ট-উদাহরণ)
- [বেস্ট প্র্যাকটিস](#বেস্ট-প্র্যাকটিস)

## ইভেন্ট সিস্টেম ওভারভিউ

Komihub বটের ইভেন্ট হলো স্পেসিফিক টেলিগ্রাম ইভেন্টের অটোমেটিক রেসপন্স যেমন:
- চ্যাটে ইউজার জয়েন/লিভ
- মেসেজ পাঠানো হচ্ছে
- চ্যাট মেম্বার আপডেট
- ক্যালব্যাক কোয়েরি
- ইনলাইন কোয়েরি

ইভেন্ট `src/events/` ডিরেক্টরিতে থাকে এবং স্টার্টআপে অটোমেটিক্যালি লোড হয়।

## বেসিক ইভেন্ট স্ট্রাকচার

### ইভেন্ট ফাইল টেমপ্লেট

```python
# src/events/my_event.py

async def handle_my_event(event):
    """একটি স্পেসিফিক ইভেন্ট টাইপ হ্যান্ডেল করুন"""
    # ইভেন্ট হ্যান্ডলিং লজিক এখানে
    pass

# ফাইল নেমের উপর ভিত্তি করে ইভেন্ট রেজিস্ট্রেশন অটোমেটিক্যালি হয়
```

### ইভেন্ট রেজিস্ট্রেশন

ইভেন্ট ফাইল নেমের প্যাটার্নের উপর ভিত্তি করে রেজিস্টার হয়:

- `join.py` - চ্যাট জয়েন ইভেন্ট
- `leave.py` - চ্যাট লিভ ইভেন্ট
- `message.py` - মেসেজ ইভেন্ট
- `callback.py` - ক্যালব্যাক কোয়েরি ইভেন্ট

## ইভেন্ট টাইপ

### চ্যাট মেম্বার ইভেন্ট

ইউজার জয়েন বা লিভ হ্যান্ডেল করুন:

```python
# src/events/join.py
from aiogram.types import ChatMemberUpdated
from core.logging import logger
from core.lang import get_lang

lang = get_lang()

async def handle_chat_member_update(update: ChatMemberUpdated):
    """ইউজার জয়েন/লিভ ইভেন্ট হ্যান্ডেল করুন"""
    try:
        if update.new_chat_member.status == 'member' and update.old_chat_member.status != 'member':
            # ইউজার জয়েন করেছে
            user = update.new_chat_member.user
            logger.info(lang.log_user_joined.format(
                user_id=user.id,
                chat_id=update.chat.id
            ))

            # ওয়েলকাম মেসেজ পাঠান
            await update.bot.send_message(
                chat_id=update.chat.id,
                text=f"স্বাগতম {user.first_name}! 👋"
            )

        elif update.old_chat_member.status == 'member' and update.new_chat_member.status != 'member':
            # ইউজার লিভ করেছে
            user = update.old_chat_member.user
            logger.info(lang.log_user_left.format(
                user_id=user.id,
                chat_id=update.chat.id
            ))

    except Exception as e:
        logger.error(f"চ্যাট মেম্বার আপডেটে এরর: {e}")
```

### মেসেজ ইভেন্ট

স্পেসিফিক মেসেজ প্যাটার্ন বা কন্টেন্ট হ্যান্ডেল করুন:

```python
# src/events/song_reply.py
from aiogram.types import Message
from core.logging import logger
from core.lang import get_lang

lang = get_lang()

async def handle_message(message: Message):
    """সং রিপ্লাই ফাংশনালিটি হ্যান্ডেল করুন"""
    try:
        # অডিও ফাইলে রিপ্লাই কিনা চেক করুন
        if (message.reply_to_message and
            message.reply_to_message.audio and
            message.text and
            message.text.lower().startswith('song')):

            audio = message.reply_to_message.audio
            song_info = f"🎵 <b>গানের তথ্য</b>\n\n"
            song_info += f"📁 টাইটেল: {audio.title or 'অজানা'}\n"
            song_info += f"👤 আর্টিস্ট: {audio.performer or 'অজানা'}\n"
            song_info += f"⏱️ ডিউরেশন: {audio.duration // 60}:{audio.duration % 60:02d}\n"
            song_info += f"📊 সাইজ: {audio.file_size:,} বাইট\n"

            await message.answer(song_info, parse_mode="HTML")

    except Exception as e:
        logger.error(f"সং রিপ্লাই হ্যান্ডলারে এরর: {e}")
```

### ক্যালব্যাক কোয়েরি ইভেন্ট

ইনলাইন কীবোর্ড থেকে বাটন প্রেস হ্যান্ডেল করুন:

```python
# src/events/callback_handler.py
from aiogram.types import CallbackQuery
from core.logging import logger

async def handle_callback_query(callback: CallbackQuery):
    """ইনলাইন কীবোর্ড থেকে ক্যালব্যাক কোয়েরি হ্যান্ডেল করুন"""
    try:
        data = callback.data

        if data.startswith('action_'):
            action = data.split('_', 1)[1]

            if action == 'confirm':
                await callback.answer("✅ কনফার্ম!")
                await callback.message.edit_text("অ্যাকশন কনফার্ম।")

            elif action == 'cancel':
                await callback.answer("❌ ক্যান্সেল!")
                await callback.message.edit_text("অ্যাকশন ক্যান্সেল।")

        elif data.startswith('page_'):
            page = int(data.split('_', 1)[1])
            # পেজিনেশন হ্যান্ডেল করুন
            await callback.answer(f"পেজ {page}")

    except Exception as e:
        logger.error(f"ক্যালব্যাক হ্যান্ডলারে এরর: {e}")
        await callback.answer("একটি এরর ঘটেছে।")
```

## ইভেন্ট উদাহরণ

### ওয়েলকাম মেসেজ ইভেন্ট

```python
# src/events/welcome.py
from aiogram.types import ChatMemberUpdated
from core.logging import logger
from core.lang import get_lang
from core.database import db

lang = get_lang()

async def handle_chat_member_update(update: ChatMemberUpdated):
    """ইউজার জয়েনে ওয়েলকাম মেসেজ পাঠান"""
    try:
        if (update.new_chat_member.status == 'member' and
            update.old_chat_member.status != 'member'):

            user = update.new_chat_member.user
            chat = update.chat

            # ডেটাবেসে ইউজার যোগ করুন
            db.add_user(user.id, {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'chat_id': chat.id,
                'joined_at': None  # কারেন্ট টাইম সেট হবে
            })

            # ওয়েলকাম মেসেজ তৈরি করুন
            welcome_text = f"""
🎉 <b>{chat.title}-এ স্বাগতম!</b>

👤 <b>{user.first_name}</b>
"""

            if user.username:
                welcome_text += f"🆔 @{user.username}\n"
            else:
                welcome_text += f"🆔 ID: <code>{user.id}</code>\n"

            welcome_text += f"""
📅 জয়েন: {time.strftime('%Y-%m-%d %H:%M:%S')}

চ্যাট রুলস পড়ে আপনার স্টে উপভোগ করুন! 🚀
"""

            await update.bot.send_message(
                chat_id=chat.id,
                text=welcome_text,
                parse_mode="HTML"
            )

            logger.info(f"ইউজার {user.id}-কে চ্যাট {chat.id}-এ ওয়েলকাম মেসেজ পাঠানো হয়েছে")

    except Exception as e:
        logger.error(f"ওয়েলকাম ইভেন্টে এরর: {e}")
```

### অ্যান্টি-স্প্যাম ইভেন্ট

```python
# src/events/anti_spam.py
from aiogram.types import Message
from core.logging import logger
from core.database import db
import time

# সিম্পল রেট লিমিটিং
user_last_message = {}

async def handle_message(message: Message):
    """বেসিক অ্যান্টি-স্প্যাম প্রোটেকশন"""
    try:
        user_id = message.from_user.id
        current_time = time.time()

        # রেট লিমিট চেক করুন (10 সেকেন্ডে ম্যাক্স 5 মেসেজ)
        if user_id in user_last_message:
            time_diff = current_time - user_last_message[user_id]
            if time_diff < 10:  # 10 সেকেন্ডের কম
                message_count = getattr(handle_message, f'count_{user_id}', 0)
                if message_count >= 5:
                    # স্প্যামারকে ব্যান করুন
                    if db.is_admin(message.from_user.id):
                        # অ্যাডমিনকে ব্যান করবেন না
                        return

                    try:
                        await message.bot.ban_chat_member(
                            message.chat.id,
                            user_id
                        )
                        await message.answer(f"🚫 ইউজার {user_id} স্প্যামিংয়ের জন্য ব্যান!")
                        logger.warning(f"স্প্যামিংয়ের জন্য ইউজার {user_id} ব্যান")
                        return
                    except Exception as e:
                        logger.error(f"স্প্যামার {user_id} ব্যান করতে ব্যর্থ: {e}")

                setattr(handle_message, f'count_{user_id}', message_count + 1)
            else:
                # কাউন্টার রিসেট করুন
                setattr(handle_message, f'count_{user_id}', 1)
        else:
            setattr(handle_message, f'count_{user_id}', 1)

        user_last_message[user_id] = current_time

    except Exception as e:
        logger.error(f"অ্যান্টি-স্প্যাম ইভেন্টে এরর: {e}")
```

### অটো-ডিলিট সার্ভিস মেসেজ

```python
# src/events/cleanup.py
from aiogram.types import Message
from core.logging import logger

async def handle_message(message: Message):
    """সার্ভিস মেসেজ ক্লিনআপ করুন"""
    try:
        # বটের নিজস্ব মেসেজ - ডিলিট করবেন না
        if message.from_user.id == message.bot.id:
            return

        # সার্ভিস মেসেজ চেক করুন
        service_keywords = [
            'joined the group',
            'left the group',
            'changed the group photo',
            'pinned a message',
            'unpinned a message'
        ]

        message_text = (message.text or message.caption or '').lower()

        if any(keyword in message_text for keyword in service_keywords):
            # 30 সেকেন্ড পর ডিলিট করুন
            import asyncio
            await asyncio.sleep(30)

            try:
                await message.delete()
                logger.info(f"চ্যাট {message.chat.id}-এ সার্ভিস মেসেজ ডিলিট")
            except Exception as e:
                logger.warning(f"সার্ভিস মেসেজ ডিলিট করতে ব্যর্থ: {e}")

    except Exception as e:
        logger.error(f"ক্লিনআপ ইভেন্টে এরর: {e}")
```

### কীওয়ার্ড রেসপন্স ইভেন্ট

```python
# src/events/keyword_responses.py
from aiogram.types import Message
from core.logging import logger

# কীওয়ার্ড রেসপন্স ডিফাইন করুন
KEYWORD_RESPONSES = {
    'hello': 'হ্যালো! 👋',
    'bye': 'বিদায়! 👋',
    'thanks': 'আপনাকে ধন্যবাদ! 😊',
    'help': 'সাহায্যের জন্য /help কমান্ড ব্যবহার করুন! 🤖',
    'ping': 'পং! 🏓'
}

async def handle_message(message: Message):
    """স্পেসিফিক কীওয়ার্ডে রেসপন্ড করুন"""
    try:
        if not message.text:
            return

        text = message.text.lower().strip()

        # এক্স্যাক্ট কীওয়ার্ড ম্যাচ চেক করুন
        for keyword, response in KEYWORD_RESPONSES.items():
            if text == keyword:
                await message.reply(response)
                logger.info(f"কীওয়ার্ড '{keyword}'-এ রেসপন্ড")
                return

        # মেসেজে কীওয়ার্ড আছে কিনা চেক করুন
        for keyword, response in KEYWORD_RESPONSES.items():
            if keyword in text:
                # খুব লম্বা মেসেজ হলে স্প্যাম এড়াতে শুধু রেসপন্ড করুন
                if len(text.split()) <= 3:
                    await message.reply(response)
                    logger.info(f"মেসেজে কীওয়ার্ড '{keyword}'-এ রেসপন্ড")
                    return

    except Exception as e:
        logger.error(f"কীওয়ার্ড রেসপন্স ইভেন্টে এরর: {e}")
```

## বেস্ট প্র্যাকটিস

### ১. এরর হ্যান্ডলিং
ইভেন্ট হ্যান্ডলারে সর্বদা ট্রাই-ক্যাচ ব্লক ব্যবহার করুন:

```python
async def handle_event(event):
    try:
        # ইভেন্ট লজিক এখানে
        pass
    except Exception as e:
        logger.error(f"ইভেন্ট হ্যান্ডলারে এরর: {e}")
```

### ২. লগিং
গুরুত্বপূর্ণ ইভেন্ট এবং এরর লগ করুন:

```python
logger.info(f"ইভেন্ট ট্রিগার: {event_type}")
logger.error(f"ইভেন্ট এরর: {e}")
```

### ৩. পারফরম্যান্স
ইভেন্ট হ্যান্ডলার লাইটওয়েট রাখুন, ব্লকিং অপারেশন এড়ান, async/await প্রপারলি ব্যবহার করুন।

### ৪. ডেটাবেস ব্যবহার
পার্সিস্টেন্ট ডেটার জন্য ডেটাবেস ব্যবহার করুন:

```python
from core.database import db

# ইভেন্ট ডেটা স্টোর করুন
db.add_user(user_id, {'event_data': 'value'})
```

### ৫. রেট লিমিটিং
রিসোর্স-ইনটেনসিভ অপারেশনের জন্য রেট লিমিটিং ইমপ্লিমেন্ট করুন:

```python
import time

last_execution = {}

async def rate_limited_handler(event):
    current_time = time.time()
    if current_time - last_execution.get('handler', 0) < 60:  # 1 মিনিট কুলডাউন
        return

    last_execution['handler'] = current_time
    # হ্যান্ডলার লজিক
```

### ৬. কনফিগারেশন
কাস্টমাইজেবল বিহেভিয়ারের জন্য কনফিগ ভ্যালু ব্যবহার করুন:

```python
import config

if config.ENABLE_WELCOME_MESSAGES:
    await send_welcome_message(event)
```

### ৭. ফাইল অর্গানাইজেশন
এক ফাইলে এক ইভেন্ট টাইপ, ডেসক্রিপটিভ ফাইল নাম, ক্লিয়ার ফাংশন নাম।

### ৮. টেস্টিং
ইভেন্ট বিভিন্ন সিনারিওতে টেস্ট করুন:
- গ্রুপ চ্যাট vs প্রাইভেট চ্যাট
- বিভিন্ন ইউজার টাইপ (অ্যাডমিন, মেম্বার, ইত্যাদি)
- এরর কন্ডিশন

### ৯. ডকুমেন্টেশন
ইভেন্ট ফাংশনে ডকস্ট্রিং যোগ করুন:

```python
async def handle_join_event(update: ChatMemberUpdated):
    """ওয়েলকাম মেসেজ সহ ইউজার জয়েন ইভেন্ট হ্যান্ডেল করুন"""
    pass
```

### ১০. ক্লিনআপ
রিসোর্স এবং টেম্পোরারি ডেটা ক্লিনআপ করুন:

```python
finally:
    # ক্লিনআপ কোড এখানে
    pass
```

## ইভেন্ট রেজিস্ট্রেশন

ইভেন্ট ফাইল নেম প্যাটার্নের উপর ভিত্তি করে অটোমেটিক্যালি রেজিস্টার হয়। সিস্টেম খোঁজে:

- `src/events/`-এ `.py` দিয়ে শেষ হওয়া ফাইল
- এক্সপেক্টেড সিগনেচার ম্যাচ করে এমন ফাংশন
- বট ডিসপ্যাচারে অটোমেটিক রেজিস্ট্রেশন

## সাহায্য প্রয়োজন?

- `src/events/`-এ বিদ্যমান ইভেন্ট থেকে উদাহরণ দেখুন
- টেলিগ্রাম বট API ডকুমেন্টেশন থেকে ইভেন্ট টাইপ দেখুন
- ইভেন্ট এক্সিকিউশন ডিবাগ করতে লগিং ব্যবহার করুন
- প্রথমে ডেভেলপমেন্ট এনভায়রনমেন্টে ইভেন্ট টেস্ট করুন

---

**আরও তথ্যের জন্য ইংলিশ ভার্সন দেখুন:** [creating-events.md](creating-events.md)