# KOMIHUB BOT
**বাংলায় দেখুন:** [examples.bn.md](examples.bn.md)

A comprehensive Telegram bot framework built with aiogram, featuring modular command handling, event management, web API integration, and multilingual support.

## Features

- **Modular Architecture**: Easily extensible with commands and events in separate modules
- **Multilingual Support**: Built-in English and Banglish language packs
- **Web API**: RESTful API for bot management and interactions
- **Database Integration**: JSON-based data storage for users, admins, bans, and statistics
- **Hot Reload**: Automatic reloading of commands and events during development
- **PID Management**: Automatic cleanup of old bot instances
- **Rich Command Set**: Includes commands for broadcasting, QR code generation, social media downloads, and more
- **Middleware Support**: User tracking and authentication middleware
- **Logging**: Comprehensive logging system with configurable levels

## Prerequisites

- Python 3.12 or higher
- A Telegram Bot Token (obtain from [@BotFather](https://t.me/botfather))

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd tg-aiogram-1
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Configure the bot:
   - Copy `config.py` and update the following variables:
     - `BOT_TOKEN`: Your Telegram bot token
     - `BOT_NAME`: Name of your bot
     - `ADMIN_NAME`: Your admin username
     - Other configuration options as needed

## Usage

### Running the Bot

Start the bot with:
```bash
python main.py
```

The bot will automatically:
- Load and register all commands from `src/commands/`
- Load and register events from `src/events/`
- Start polling for updates
- Clean up old instances if any

### Web API

The bot includes a FastAPI-based web interface. Run the web server with:
```bash
python web_api/main.py
```

Access the API documentation at `http://localhost:8000/docs`

### Available Commands

- `/start` - Initialize the bot
- `/help` - Display available commands
- `/ping` - Check bot responsiveness
- `/info` - Get bot information
- `/broadcast` - Send messages to all users (admin only)
- `/add_admin` - Add new administrators (admin only)
- `/ban` - Ban users (admin only)
- `/kick` - Remove users from chats (admin only)
- `/qrcode` - Generate QR codes
- `/social_dl` - Download from social media platforms
- `/yt_music` - Download YouTube music
- `/restart` - Restart the bot (admin only)
- `/reload` - Reload commands and events (admin only)
- `/add_command` - Add custom commands (admin only)
- `/upload_limit` - Set upload limits
- `/unsend` - Delete messages

### Events

The bot handles various events including:
- User joins/leaves chats
- Song replies
- Chat member updates

## Configuration

Edit `config.py` to customize:
- Bot token and credentials
- Admin settings
- Language preferences
- API settings
- Upload limits
- Database paths

## Project Structure

```
tg-aiogram-1/
├── core/                    # Core bot functionality
│   ├── bot.py              # Main bot class
│   ├── database.py         # Data management
│   ├── handler/            # Command and event handlers
│   ├── langs/              # Language files
│   ├── logging.py          # Logging configuration
│   ├── middleware.py       # Bot middleware
│   └── pid_manager.py      # Process management
├── src/                    # Source code
│   ├── commands/           # Bot commands
│   └── events/             # Event handlers
├── web_api/                # Web API server
├── data/                   # Data storage (JSON files)
├── docs/                   # Documentation
├── main.py                 # Entry point
├── config.py               # Configuration file
└── pyproject.toml          # Project dependencies
```

## Development

### Adding New Commands

1. Create a new file in `src/commands/`
2. Implement an async function that takes a `Message` object
3. The file will be automatically loaded on startup

Example:
```python
from aiogram.types import Message

async def handle_my_command(message: Message):
    await message.answer("Hello from my command!")
```

### Adding New Events

1. Create a new file in `src/events/`
2. Implement event handler functions
3. Events are automatically registered based on file naming

### Hot Reload

The bot supports hot reloading of commands and events during development. Use `/reload` command to refresh without restarting.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the logs in the console
- Review the data files for bot statistics
- Ensure all dependencies are properly installed
- Verify your bot token is correct and has necessary permissions

## Examples

See [examples.md](examples.md) for detailed usage examples and command demonstrations.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes.