# Version Tracker Documentation

## Overview

KOMIHUB now includes a comprehensive version tracking and auto-update system that monitors GitHub releases and automatically updates the bot when new versions are available.

## Features

### 🔄 Automatic Updates
- Checks for updates at configurable intervals (default: 1 hour)
- Automatically pulls latest changes from GitHub repository
- Notifies admin when updates are completed
- Respects `AUTO_UPDATE` configuration setting

### 🛠️ Manual Commands
- `/update check` - Check for available updates
- `/update update` - Perform manual update
- `/update status` - Show current version and git status

### 📊 Version Monitoring
- Tracks multiple component versions (bot, tool, komi)
- Stores version information locally in `data/version.json`
- Compares local vs remote versions using semantic versioning

## Configuration

Add these settings to your `config.py`:

```python
# Auto-update configuration
AUTO_UPDATE = True
UPDATE_CHECK_INTERVAL = 3600  # Check every hour
VERSION_URL = "https://komihub-v.grandpaacademy.org"
GITHUB_REPO = "GrandpaEJ/KOMIHUB"
```

### Configuration Options

- `AUTO_UPDATE`: Enable/disable automatic updates (boolean)
- `UPDATE_CHECK_INTERVAL`: How often to check for updates (seconds)
- `VERSION_URL`: API endpoint that returns version information
- `GITHUB_REPO`: GitHub repository in format "owner/repo"

## Version API Response Format

The version API should return JSON in this format:

```json
{
  "v": "1.0.0",
  "tool": "0.9.5", 
  "komi": "0.8.2"
}
```

## Files Created

- `core/version_tracker.py` - Main version tracking logic
- `src/commands/update.py` - Manual update commands
- `src/events/update_check.py` - Automatic update checking
- `tools/version_demo.py` - Demo and testing script
- `docs/version-tracker.md` - This documentation

## Usage Examples

### Check for Updates
```
User: /update check
Bot: 📦 Updates Available

tool: 0.0.1 → 0.0.2
komi: 0.0.1 → 0.0.1

Use /update update to install updates automatically.
```

### Perform Manual Update
```
User: /update update
Bot: 🔄 Starting update process...
Bot: ✅ Update Successful

Updated to: 78d3caf Fix YouTube music download functionality:

🚀 Restart the bot to apply changes.
```

### View Status
```
User: /update status
Bot: 📊 Version Status

🤖 Bot Version: 0.0.1
🛠️ Tool Version: 0.0.1
💫 Kumi Version: 0.0.1

📝 Latest Commit: 78d3caf Fix YouTube...
🔧 Status: Clean working directory
🔄 Auto-update: ✅ Enabled
🔗 Repository: GrandpaEJ/KOMIHUB
```

## Error Handling

The system includes comprehensive error handling for:
- Network connectivity issues
- Git repository problems
- Permission errors
- Invalid version responses
- Update conflicts

## Security Considerations

- Only admin users can execute update commands
- Auto-updates require the bot to be in a git repository
- Updates are performed by pulling changes, not replacing entire files
- Version information is cached locally to prevent excessive API calls

## Testing

Run the demo script to test functionality:
```bash
uv run python tools/version_demo.py
```

This will show current versions, check for updates, and display git status.