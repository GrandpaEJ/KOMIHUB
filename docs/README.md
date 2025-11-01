# Komihub Bot Documentation

Welcome to the Komihub Bot documentation! This directory contains comprehensive guides for developing and extending the bot.

**বাংলায় দেখুন:** [docs/README.bn.md](README.bn.md)

## Table of Contents

### Getting Started
- [Main README](../README.md) - Project overview and setup
- [Examples](../examples.md) - Usage examples and command demonstrations

### Development Guides
- [Creating Commands](creating-commands.md) - How to create new bot commands
- [Creating Events](creating-events.md) - How to handle automatic events
- [Database Guide](database-guide.md) - Using the JSON database system

### Reference
- [HTML Formatting](markdown.md) - Telegram HTML formatting guide

## Quick Start

1. **Setup**: Follow the installation instructions in the main README
2. **Create Commands**: Read [Creating Commands](creating-commands.md) to add new functionality
3. **Handle Events**: Learn about event handling in [Creating Events](creating-events.md)
4. **Use Database**: Understand data persistence with [Database Guide](database-guide.md)

## Project Structure

```
komihub-bot/
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
├── docs/                   # Documentation (this directory)
├── data/                   # Data storage (JSON files)
├── web_api/                # Web API server
├── main.py                 # Entry point
├── config.py               # Configuration file
└── pyproject.toml          # Project dependencies
```

## Key Features

### Modular Architecture
- **Commands**: Individual command files in `src/commands/`
- **Events**: Automatic event handlers in `src/events/`
- **Languages**: Multilingual support with separate language files
- **Database**: JSON-based data storage with automatic backups

### Development Features
- **Hot Reload**: Reload commands and events without restarting
- **Logging**: Comprehensive logging with colored output
- **Middleware**: User tracking and authentication
- **PID Management**: Automatic cleanup of old bot instances

### Built-in Commands
- Admin management (`/add_admin`, `/remove_admin`, `/list_admins`)
- User management (`/ban`, `/kick`, `/info`)
- Media processing (`/qrcode`, `/fbc`, `/social_dl`, `/yt_music`)
- Utility commands (`/help`, `/ping`, `/broadcast`, `/reload`)

## Development Workflow

1. **Create a new command** in `src/commands/your_command.py`
2. **Implement the `help()` function** with command metadata
3. **Use the `@command` decorator** to register the command
4. **Add proper error handling** and logging
5. **Test the command** with `/reload` or bot restart
6. **Update documentation** if needed

## Configuration

Edit `config.py` to customize:
- Bot token and credentials
- Admin settings
- Language preferences
- API settings
- Upload limits
- Database paths

## Support

For issues and questions:
- Check the logs in the console
- Review the data files for bot statistics
- Ensure all dependencies are properly installed
- Verify your bot token is correct and has necessary permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the guides in this documentation
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.