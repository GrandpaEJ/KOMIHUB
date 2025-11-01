# Komihub Bot-এ নতুন কমান্ড তৈরি করা

এই গাইডটি Komihub টেলিগ্রাম বট ফ্রেমওয়ার্কে নতুন কমান্ড তৈরি করার পদ্ধতি ব্যাখ্যা করে।

## সূচিপত্র
- [বেসিক কমান্ড স্ট্রাকচার](#বেসিক-কমান্ড-স্ট্রাকচার)
- [কমান্ড রেজিস্ট্রেশন](#কমান্ড-রেজিস্ট্রেশন)
- [হেল্প ফাংশন](#হেল্প-ফাংশন)
- [কমান্ড উদাহরণ](#কমান্ড-উদাহরণ)
- [অ্যাডভান্সড ফিচার](#অ্যাডভান্সড-ফিচার)
- [বেস্ট প্র্যাকটিস](#বেস্ট-প্র্যাকটিস)

## বেসিক কমান্ড স্ট্রাকচার

সব কমান্ড `src/commands/` ডিরেক্টরিতে থাকে। প্রত্যেক কমান্ডের জন্য আলাদা Python ফাইল থাকা উচিত।

### মিনিমাল কমান্ড ফাইল

```python
from core import Message, command, logger, get_lang

lang = get_lang()

def help():
    return {
        "name": "my_command",
        "version": "1.0.0",
        "description": "এই কমান্ড কী করে তার বর্ণনা",
        "author": "আপনার নাম",
        "usage": "/my_command [প্যারামিটার]"
    }

@command('my_command')
async def my_command(message: Message):
    logger.info(lang.log_command_executed.format(command='my_command', user_id=message.from_user.id))

    # আপনার কমান্ড লজিক এখানে
    await message.answer("হ্যালো! এটা আমার নতুন কমান্ড।")
```

## কমান্ড রেজিস্ট্রেশন

### @command ডেকোরেটর ব্যবহার করে

`@command` ডেকোরেটর আপনার ফাংশনকে অটোমেটিক্যালি বট কমান্ড হিসেবে রেজিস্টার করে:

```python
@command('command_name')
async def command_function(message: Message):
    # কমান্ড ইমপ্লিমেন্টেশন
    pass
```

### এক ফাইলে একাধিক কমান্ড

আপনি এক ফাইলে একাধিক কমান্ড ডিফাইন করতে পারেন:

```python
@command('cmd1')
async def command_one(message: Message):
    await message.answer("কমান্ড ১ এক্সিকিউট হয়েছে")

@command('cmd2')
async def command_two(message: Message):
    await message.answer("কমান্ড ২ এক্সিকিউট হয়েছে")
```

## হেল্প ফাংশন

প্রত্যেক কমান্ড ফাইলে `help()` ফাংশন থাকতে হবে যা কমান্ড তথ্য সহ একটি ডিকশনারি রিটার্ন করে:

```python
def help():
    return {
        "name": "command_name",        # কমান্ড নাম (প্রয়োজনীয়)
        "version": "1.0.0",           # ভার্সন (প্রয়োজনীয়)
        "description": "কী করে", # বর্ণনা (প্রয়োজনীয়)
        "author": "আপনার নাম",        # লেখকের নাম (প্রয়োজনীয়)
        "usage": "/command [params]"  # ব্যবহার সিনট্যাক্স (প্রয়োজনীয়)
    }
```

## কমান্ড উদাহরণ

### সিম্পল টেক্সট রেসপন্স

```python
from core import Message, command, logger, get_lang

lang = get_lang()

def help():
    return {
        "name": "hello",
        "version": "1.0.0",
        "description": "বটকে হ্যালো বলুন",
        "author": "Komihub",
        "usage": "/hello"
    }

@command('hello')
async def hello(message: Message):
    logger.info(lang.log_command_executed.format(command='hello', user_id=message.from_user.id))

    user_name = message.from_user.first_name or "ইউজার"
    await message.answer(f"হ্যালো {user_name}! 👋")
```

### প্যারামিটার সহ কমান্ড

```python
from core import Message, command, logger, get_lang

lang = get_lang()

def help():
    return {
        "name": "echo",
        "version": "1.0.0",
        "description": "মেসেজটি ব্যাক এখো করে",
        "author": "Komihub",
        "usage": "/echo <message>"
    }

@command('echo')
async def echo(message: Message):
    logger.info(lang.log_command_executed.format(command='echo', user_id=message.from_user.id))

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("ব্যবহার: /echo <message>")
        return

    text_to_echo = args[1]
    await message.answer(f"📢 {text_to_echo}")
```

### অ্যাডমিন-শুধু কমান্ড

```python
from core import Message, command, logger, get_lang
from core.database import db

lang = get_lang()

def help():
    return {
        "name": "admin_only",
        "version": "1.0.0",
        "description": "অ্যাডমিন-শুধু কমান্ড উদাহরণ",
        "author": "Komihub",
        "usage": "/admin_only"
    }

@command('admin_only')
async def admin_only(message: Message):
    # ইউজার অ্যাডমিন কিনা চেক করুন
    if not db.is_admin(message.from_user.id):
        await message.answer("❌ এই কমান্ড শুধু অ্যাডমিনদের জন্য।")
        return

    logger.info(lang.log_command_executed.format(command='admin_only', user_id=message.from_user.id))

    await message.answer("✅ অ্যাডমিন কমান্ড সফলভাবে এক্সিকিউট হয়েছে!")
```

### রিপ্লাই-ভিত্তিক কমান্ড

```python
from core import Message, command, logger, get_lang

lang = get_lang()

def help():
    return {
        "name": "reply_test",
        "version": "1.0.0",
        "description": "রিপ্লাই সহ কাজ করে এমন কমান্ড",
        "author": "Komihub",
        "usage": "/reply_test [text] - একটি মেসেজে রিপ্লাই করে কোট করুন"
    }

@command('reply_test')
async def reply_test(message: Message):
    logger.info(lang.log_command_executed.format(command='reply_test', user_id=message.from_user.id))

    if message.reply_to_message:
        # ইউজার একটি মেসেজে রিপ্লাই করেছে
        original_text = message.reply_to_message.text or "[নন-টেক্সট মেসেজ]"
        args = message.text.split(maxsplit=1)
        quote_text = args[1] if len(args) > 1 else "কোট"

        await message.answer(f"💬 {quote_text}:\n\n{original_text}")
    else:
        # কোনো রিপ্লাই নেই, শুধু টেক্সট এখো করুন
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("ব্যবহার: /reply_test <text>\nবা একটি মেসেজে রিপ্লাই করে /reply_test")
            return

        await message.answer(f"📢 {args[1]}")
```

### ফাইল আপলোড/ডাউনলোড কমান্ড

```python
from core import Message, command, logger, get_lang, FSInputFile
import tempfile
import os

lang = get_lang()

def help():
    return {
        "name": "process_file",
        "version": "1.0.0",
        "description": "আপলোড করা ফাইল প্রসেস করে",
        "author": "Komihub",
        "usage": "/process_file - একটি ডকুমেন্ট বা ফটোতে রিপ্লাই করুন"
    }

@command('process_file')
async def process_file(message: Message):
    logger.info(lang.log_command_executed.format(command='process_file', user_id=message.from_user.id))

    if not message.reply_to_message or not (message.reply_to_message.document or message.reply_to_message.photo):
        await message.answer("একটি ডকুমেন্ট বা ফটোতে রিপ্লাই করে এই কমান্ড ব্যবহার করুন।")
        return

    await message.answer("🔄 ফাইল প্রসেস করা হচ্ছে...")

    try:
        # ফাইল ডাউনলোড করুন
        if message.reply_to_message.document:
            file_info = await message.bot.get_file(message.reply_to_message.document.file_id)
        else:
            # ফটো - সবচেয়ে বড় সাইজ নিন
            photo = message.reply_to_message.photo[-1]
            file_info = await message.bot.get_file(photo.file_id)

        downloaded_file = await message.bot.download_file(file_info.file_path)

        # ফাইল প্রসেস করুন (উদাহরণ: শুধু ফাইল সাইজ পান)
        file_size = len(downloaded_file.getvalue())
        file_name = message.reply_to_message.document.file_name if message.reply_to_message.document else "photo.jpg"

        await message.answer(
            f"✅ ফাইল প্রসেস সম্পন্ন!\n\n"
            f"📁 নাম: {file_name}\n"
            f"📊 সাইজ: {file_size:,} বাইট\n"
            f"📂 টাইপ: {'ডকুমেন্ট' if message.reply_to_message.document else 'ফটো'}"
        )

    except Exception as e:
        logger.error(f"ফাইল প্রসেসিং এরর: {e}")
        await message.answer("❌ ফাইল প্রসেস করতে ব্যর্থ হয়েছে।")
```

## অ্যাডভান্সড ফিচার

### ডেটাবেস ব্যবহার

```python
from core import Message, command, logger, get_lang
from core.database import db

@command('user_stats')
async def user_stats(message: Message):
    user_id = message.from_user.id

    # ইউজার ডেটা পান
    user_data = db.get_user(user_id)
    if not user_data:
        await message.answer("এই ইউজারের জন্য কোনো ডেটা পাওয়া যায়নি।")
        return

    # কমান্ড ব্যবহার স্ট্যাটিস্টিক্স পান
    command_stats = db.get_command_stats()

    response = f"📊 <b>ইউজার স্ট্যাটিস্টিক্স</b>\n\n"
    response += f"👤 ইউজার ID: <code>{user_id}</code>\n"
    response += f"📅 জয়েন: {user_data.get('joined_at', 'অজানা')}\n"
    response += f"🎯 রোল: {user_data.get('role', 'user')}\n"

    await message.answer(response, parse_mode="HTML")
```

### কনফিগারেশন ব্যবহার

```python
from core import Message, command, logger, get_lang
import config

@command('bot_info')
async def bot_info(message: Message):
    response = f"🤖 <b>বট তথ্য</b>\n\n"
    response += f"📛 নাম: {config.BOT_NAME}\n"
    response += f"👤 ওনার: {config.ADMIN_NAME}\n"
    response += f"🆔 ওনার ID: <code>{config.ADMIN_ID}</code>\n"
    response += f"🌐 ল্যাঙ্গুয়েজ: {config.DEFAULT_LANG}\n"

    await message.answer(response, parse_mode="HTML")
```

### এরর হ্যান্ডলিং

```python
@command('risky_command')
async def risky_command(message: Message):
    try:
        # কিছু রিস্কি অপারেশন
        result = some_risky_function()

        await message.answer(f"✅ সফল: {result}")

    except ValueError as e:
        await message.answer(f"❌ ইনভ্যালিড ইনপুট: {e}")

    except Exception as e:
        logger.error(f"অপ্রত্যাশিত এরর in risky_command: {e}")
        await message.answer("❌ একটি অপ্রত্যাশিত এরর ঘটেছে। অনুগ্রহ করে আবার চেষ্টা করুন।")
```

### অ্যাসিঙ্ক অপারেশন

```python
import asyncio

@command('async_example')
async def async_example(message: Message):
    # প্রগ্রেস দেখান
    progress_msg = await message.answer("🔄 অ্যাসিঙ্ক অপারেশন শুরু হচ্ছে...")

    # অ্যাসিঙ্ক কাজ সিমুলেট করুন
    await asyncio.sleep(2)
    await progress_msg.edit_text("🔄 প্রসেস করা হচ্ছে... ৫০%")

    await asyncio.sleep(2)
    await progress_msg.edit_text("✅ অপারেশন সম্পন্ন!")

    # ক্লিনআপ
    await asyncio.sleep(1)
    await progress_msg.delete()
```

## বেস্ট প্র্যাকটিস

### ১. সর্বদা হেল্প ফাংশন ইনক্লুড করুন
প্রত্যেক কমান্ড ফাইলে `help()` ফাংশন থাকতে হবে সম্পূর্ণ তথ্য সহ।

### ২. প্রপার লগিং ব্যবহার করুন
কমান্ড এক্সিকিউশন এবং গুরুত্বপূর্ণ ইভেন্ট লগ করুন:

```python
logger.info(lang.log_command_executed.format(command='command_name', user_id=message.from_user.id))
```

### ৩. এরর গ্রেসফুলি হ্যান্ডেল করুন
ট্রাই-ক্যাচ ব্লক ব্যবহার করে এবং ইউজারদের জন্য অর্থপূর্ণ এরর মেসেজ প্রদান করুন।

### ৪. ইনপুট ভ্যালিডেট করুন
কমান্ড আর্গুমেন্ট চেক করুন এবং ইনভ্যালিড হলে ব্যবহার নির্দেশনা প্রদান করুন।

### ৫. HTML ফরম্যাটিং ব্যবহার করুন
বিটার রিডেবিলিটির জন্য মেসেজে HTML ট্যাগ ব্যবহার করুন:

```python
await message.answer(
    "<b>সফল!</b> অপারেশন সম্পন্ন।\n"
    "<code>রেসাল্ট: 12345</code>",
    parse_mode="HTML"
)
```

### ৬. রেট লিমিট রেসপেক্ট করুন
টেলিগ্রামের রেট লিমিট এড়াতে অপারেশনের মধ্যে ডিলে যোগ করুন।

### ৭. রিসোর্স ক্লিনআপ করুন
ফাইনালি ব্লকে টেম্পোরারি ফাইল এবং রিসোর্স ক্লিনআপ করুন।

### ৮. পারমিশন চেক করুন
অ্যাডমিন-শুধু কমান্ডের জন্য ডেটাবেস চেক ব্যবহার করুন:

```python
if not db.is_admin(message.from_user.id):
    await message.answer("❌ অ্যাডমিন অ্যাক্সেস প্রয়োজন।")
    return
```

### ৯. ফাইল নেমিং
ডেসক্রিপটিভ ফাইল নাম ব্যবহার করুন: `my_command.py`, `user_management.py`, ইত্যাদি।

### ১০. ডকুমেন্টেশন
কোড রিডেবল রাখুন এবং কমপ্লেক্স লজিকের জন্য কমেন্ট যোগ করুন।

## আপনার কমান্ড টেস্ট করা

১. আপনার কমান্ড ফাইল `src/commands/`-এ সেভ করুন
২. বট রিস্টার্ট করুন বা `/reload` কমান্ড ব্যবহার করুন
৩. আপনার কমান্ড দেখা যায় কিনা `/help` দিয়ে চেক করুন
৪. কমান্ড ফাংশনালিটি টেস্ট করুন
৫. ডেভেলপমেন্টের সময় কোনো এররের জন্য লগ চেক করুন

## কমান্ড ফাইল টেমপ্লেট

নতুন কমান্ডের জন্য এই টেমপ্লেট ব্যবহার করুন:

```python
from core import Message, command, logger, get_lang
# প্রয়োজনীয় অন্যান্য মডিউল ইমপোর্ট করুন

lang = get_lang()

def help():
    return {
        "name": "command_name",
        "version": "1.0.0",
        "description": "এই কমান্ড কী করে তার সংক্ষিপ্ত বর্ণনা",
        "author": "আপনার নাম",
        "usage": "/command_name [প্যারামিটার]"
    }

@command('command_name')
async def command_name(message: Message):
    logger.info(lang.log_command_executed.format(command='command_name', user_id=message.from_user.id))

    # কমান্ড ইমপ্লিমেন্টেশন এখানে
    await message.answer("কমান্ড সফলভাবে এক্সিকিউট হয়েছে!")
```

## সাহায্য প্রয়োজন?

- `src/commands/`-এ বিদ্যমান কমান্ড থেকে উদাহরণ দেখুন
- কোর মডিউল `core/` থেকে উপলব্ধ ইউটিলিটি দেখুন
- বটে `/help` কমান্ড দিয়ে উপলব্ধ কমান্ড দেখুন
- ডেভেলপমেন্টের সময় এরর মেসেজের জন্য লগ চেক করুন

---

**আরও তথ্যের জন্য ইংলিশ ভার্সন দেখুন:** [creating-commands.md](creating-commands.md)