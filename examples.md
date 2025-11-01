# Komihub Bot - Usage Examples

This document provides practical examples for using the Komihub Telegram bot commands.

## Table of Contents
- [Basic Commands](#basic-commands)
- [Admin Commands](#admin-commands)
- [Media Commands](#media-commands)
- [Utility Commands](#utility-commands)
- [Download Commands](#download-commands)

## Basic Commands

### /start
Start the bot and get a welcome message.
```
/start
```

### /help
Get help for all available commands or specific command help.
```
/help
/help ping
```

### /ping
Check bot response time.
```
/ping
```

### /info
Get information about a user or chat.
```
/info
/info 123456789
```
*(Reply to a message to get info about that user)*

## Admin Commands

### /add_admin
Add a user as an admin (Owner only).
```
/add_admin 123456789 admins
/add_admin @username elders
```
*(Reply to a message to add the sender as admin)*

### /remove_admin
Remove admin privileges from a user (Owner only).
```
/remove_admin 123456789 admins
/remove_admin @username elders
```
*(Reply to a message to remove admin from that user)*

### /list_admins
List all bot administrators.
```
/list_admins
```

### /ban
Ban a user from the chat (Admin only).
```
/ban 123456789 Spam messages
/ban @username Breaking rules
```
*(Reply to a message to ban that user)*

### /kick
Kick a user from the chat (Admin only).
```
/kick 123456789 Temporary removal
/kick @username Rule violation
```
*(Reply to a message to kick that user)*

### /broadcast
Send a message to all bot users (Admin only).
```
/broadcast Hello everyone! This is an important announcement.
```

## Media Commands

### /qrcode
Generate QR codes from text.
```
/qrcode Hello World
/qrcode https://example.com
```

### /fbc
Generate Facebook cover photo with profile image and contact info.
*(Reply to a profile image)*
```
/fbc John Doe john@email.com +1234567890
```

### /unsend
Delete bot messages by replying to them.
*(Reply to any bot message)*
```
/unsend
```

## Utility Commands

### /upload_limit
Check Telegram upload limits and file size restrictions.
```
/upload_limit
```

### /reload
Hot reload all commands and events (Admin only).
```
/reload
```

### /restart
Restart the entire bot application (Admin only).
```
/restart
```

## Download Commands

### /yt_music
Search and download YouTube music/audio.
```
/yt_music billie eilish bad guy
/yt_music https://youtu.be/dQw4w9WgXcQ
```

### /song
Quick search and select songs from YouTube.
```
/song despacito
/song billie eilish
```

### /social_dl
Download content from social media platforms.
```
/social_dl https://www.instagram.com/p/ABC123/
/social_dl https://twitter.com/user/status/1234567890
/social_dl https://www.facebook.com/watch?v=123456789
```

## Command Categories

### Supported Social Media Platforms
- **Facebook**: Videos, Reels
- **Instagram**: Posts, Reels, Stories
- **Twitter/X**: Videos, GIFs
- **TikTok**: Videos

### Admin Types
- `owner`: Bot owner (full access)
- `admins`: General administrators
- `elders`: Senior administrators
- `gc_admins`: Group chat administrators
- `ch_admins`: Channel administrators

### File Size Limits
- Photos: 10 MB
- Videos: 2 GB (Premium: 4 GB)
- Audio: 2 GB
- Documents: 2 GB (Premium: 4 GB)
- Stickers: 512 KB
- GIFs: 2 GB
- Voice messages: 1 MB

## Error Handling

The bot provides helpful error messages and suggestions for:
- Unknown commands
- Permission denied
- Invalid input formats
- File size limits exceeded
- Network errors

## Tips
- Use `/help` to see all available commands
- Reply to messages for user-specific actions
- Check `/upload_limit` for file size restrictions
- Use `/reload` if new commands aren't appearing
- Admin commands require appropriate permissions

## Support

For additional help or reporting issues:
- Use `/help` for command information
- Check bot logs for error details
- Contact bot administrators for support