
## 1️⃣ Telegram HTML Formatting Cheat Sheet

When sending messages with `parse_mode="HTML"` in Telegram (via aiogram or any other bot framework), you can use the following tags:

| Feature                             | HTML Tag / Syntax                                      | Example                                                       | Output                        |
| ----------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------- | ----------------------------- |
| **Bold**                            | `<b>text</b>`                                          | `<b>Hello</b>`                                                | **Hello**                     |
| *Italic*                            | `<i>text</i>`                                          | `<i>Italic</i>`                                               | *Italic*                      |
| Underline                           | `<u>text</u>`                                          | `<u>Underline</u>`                                            | Underline                     |
| Strikethrough                       | `<s>text</s>`                                          | `<s>Strike</s>`                                               | ~~Strike~~                    |
| Monospace / Inline Code             | `<code>text</code>`                                    | `<code>/start</code>`                                         | `/start`                      |
| Code Block (multi-line)             | `<pre>code block</pre>`                                | `<pre>line1\nline2</pre>`                                     | `line1 line2`                 |
| Code Block with syntax highlighting | `<pre><code class="language-python">code</code></pre>` | `<pre><code class="language-python">print("hi")</code></pre>` | Syntax-highlighted code block |
| Hyperlink                           | `<a href="URL">text</a>`                               | `<a href="https://google.com">Google</a>`                     | Google (clickable)            |
| Spoiler                             | `<tg-spoiler>text</tg-spoiler>`                        | `<tg-spoiler>secret</tg-spoiler>`                             | Hidden text, tap to reveal    |

> ✅ **Notes:**
>
> * Line breaks: use `\n` for new lines, `<br>` also works.
> * Nested tags are supported (e.g., `<b><i>text</i></b>`).
> * No need to escape characters (unlike MarkdownV2).

---

## 2️⃣ Remove Link Preview

By default, Telegram generates a preview (title, image) for any link in the message.
You can disable it using `disable_web_page_preview=True` in `message.answer()`:

```python
await message.answer(
    "Check this out: <a href='https://core.telegram.org/bots/api'>Telegram Docs</a>",
    parse_mode="HTML",
    disable_web_page_preview=True  # removes link preview
)
```

---

## 3️⃣ Full Example in aiogram

```python
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import config

async def cmd_help(message: types.Message):
    await message.answer(
        "👋 <b>Welcome!</b><br>"
        "<i>This bot supports HTML formatting.</i><br>"
        "Use <code>/start</code> or <code>/help</code><br>"
        "<u>Underline text</u>, <s>Strikethrough</s><br>"
        "Hidden text: <tg-spoiler>secret info</tg-spoiler><br>"
        '<a href="https://core.telegram.org/bots/api">Telegram Docs</a>',
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