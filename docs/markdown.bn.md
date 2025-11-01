# টেলিগ্রাম HTML ফরম্যাটিং চিট শিট

টেলিগ্রামে `parse_mode="HTML"` দিয়ে মেসেজ পাঠানোর সময় (aiogram বা অন্য কোনো বট ফ্রেমওয়ার্ক দিয়ে), আপনি নিচের ট্যাগ ব্যবহার করতে পারেন:

| ফিচার                             | HTML ট্যাগ / সিনট্যাক্স                                      | উদাহরণ                                                       | আউটপুট                        |
| ----------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------- | ----------------------------- |
| **বোল্ড**                            | `<b>টেক্সট</b>`                                          | `<b>হ্যালো</b>`                                                | **হ্যালো**                     |
| *ইটালিক*                            | `<i>টেক্সট</i>`                                          | `<i>ইটালিক</i>`                                               | *ইটালিক*                      |
| আন্ডারলাইন                           | `<u>টেক্সট</u>`                                          | `<u>আন্ডারলাইন</u>`                                            | আন্ডারলাইন                     |
| স্ট্রাইকথ্রু                       | `<s>টেক্সট</s>`                                          | `<s>স্ট্রাইক</s>`                                               | ~~স্ট্রাইক~~                    |
| মনোস্পেস / ইনলাইন কোড             | `<code>টেক্সট</code>`                                    | `<code>/start</code>`                                         | `/start`                      |
| কোড ব্লক (মাল্টি-লাইন)             | `<pre>কোড ব্লক</pre>`                                | `<pre>লাইন1\nলাইন2</pre>`                                     | `লাইন1 লাইন2`                 |
| কোড ব্লক সিনট্যাক্স হাইলাইটিং সহ | `<pre><code class="language-python">কোড</code></pre>` | `<pre><code class="language-python">print("hi")</code></pre>` | সিনট্যাক্স-হাইলাইটেড কোড ব্লক |
| হাইপারলিংক                           | `<a href="URL">টেক্সট</a>`                               | `<a href="https://google.com">গুগল</a>`                     | গুগল (ক্লিকেবল)            |
| স্পয়লার                             | `<tg-spoiler>টেক্সট</tg-spoiler>`                        | `<tg-spoiler>সিক্রেট</tg-spoiler>`                             | হিডেন টেক্সট, ট্যাপ করে দেখুন    |

> ✅ **নোট:**
>
> * নিউ লাইনের জন্য `\n` ব্যবহার করুন, `<br>` ও কাজ করে।
> * নেস্টেড ট্যাগ সাপোর্টেড (যেমন, `<b><i>টেক্সট</i></b>`)।
> * MarkdownV2-এর মতো ক্যারেক্টার এস্কেপ করার দরকার নেই।

---

## লিংক প্রিভিউ রিমুভ করা

ডিফল্টভাবে টেলিগ্রাম যেকোনো লিংকের জন্য প্রিভিউ (টাইটেল, ইমেজ) জেনারেট করে।
এটি রিমুভ করতে `message.answer()`-এ `disable_web_page_preview=True` ব্যবহার করুন:

```python
await message.answer(
    "এটা দেখুন: <a href='https://core.telegram.org/bots/api'>টেলিগ্রাম ডকস</a>",
    parse_mode="HTML",
    disable_web_page_preview=True  # লিংক প্রিভিউ রিমুভ করে
)
```

---

## aiogram-এ ফুল উদাহরণ

```python
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import config

async def cmd_help(message: types.Message):
    await message.answer(
        "👋 <b>স্বাগতম!</b><br>"
        "<i>এই বট HTML ফরম্যাটিং সাপোর্ট করে।</i><br>"
        "ব্যবহার করুন <code>/start</code> বা <code>/help</code><br>"
        "<u>আন্ডারলাইন টেক্সট</u>, <s>স্ট্রাইকথ্রু</s><br>"
        "হিডেন টেক্সট: <tg-spoiler>সিক্রেট ইনফো</tg-spoiler><br>"
        '<a href="https://core.telegram.org/bots/api">টেলিগ্রাম ডকস</a>',
        parse_mode="HTML",
        disable_web_page_preview=True
    )

async def main():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(cmd_help, Command("help"))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

---

**আরও তথ্যের জন্য ইংলিশ ভার্সন দেখুন:** [markdown.md](markdown.md)