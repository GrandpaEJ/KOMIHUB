# Database Guide for Komihub Bot

This guide explains how to use the JSON-based database system in the Komihub bot framework.

## Table of Contents
- [Database Overview](#database-overview)
- [Database Files](#database-files)
- [Basic Operations](#basic-operations)
- [User Management](#user-management)
- [Admin Management](#admin-management)
- [Ban Management](#ban-management)
- [Command Management](#command-management)
- [Statistics](#statistics)
- [Advanced Usage](#advanced-usage)

## Database Overview

The Komihub bot uses a JSON-based database system stored in the `data/` directory. This provides:

- **Simple file-based storage** - No external database required
- **JSON format** - Human-readable and editable
- **Automatic initialization** - Creates files and default data on first run
- **Backup on corruption** - Automatically backs up corrupted files
- **Thread-safe operations** - Safe for concurrent access

## Database Files

The system manages several JSON files:

- `bot_stats.json` - Bot statistics and metadata
- `users.json` - User information and roles
- `admins.json` - Administrator configurations
- `bans.json` - Banned user information
- `disabled_commands.json` - List of disabled commands
- `command_stats.json` - Command usage statistics
- `bots/bot_{admin_id}.json` - Bot-specific configuration

## Basic Operations

### Importing the Database

```python
from core.database import db
```

### Loading Data

```python
# Load data from a database file
users = db.load_data('users')
admins = db.load_data('admins')
```

### Saving Data

```python
# Save data to a database file
data = {'key': 'value', 'number': 42}
success = db.save_data('custom_data', data)
```

### Updating Data

```python
# Update bot statistics
db.update_bot_stats(total_commands=100, online_since=time.time())
```

## User Management

### Adding Users

```python
user_data = {
    'username': 'john_doe',
    'first_name': 'John',
    'last_name': 'Doe'
}
db.add_user(user_id=123456789, user_data=user_data)
```

### Getting User Data

```python
user = db.get_user(user_id=123456789)
if user:
    print(f"User role: {user.get('role', 'user')}")
    print(f"Joined at: {user.get('joined_at')}")
```

### Updating User Data

```python
# Update last seen time and other data
db.update_user(user_id=123456789, last_seen=time.time(), custom_field='value')
```

### Setting User Roles

```python
# Set user role
db.set_user_role(user_id=123456789, role='admin')

# Available roles: 'user', 'admin', 'elder', 'owner', etc.
```

### Getting Users by Role

```python
# Get all admins
admins = db.get_role_users('admin')

# Get all users with a specific role
elders = db.get_role_users('elder')
```

## Admin Management

### Adding Admins

```python
# Add admin with specific type
db.add_admin(user_id=123456789, admin_type='admins')  # General admin
db.add_admin(user_id=123456789, admin_type='elders')  # Senior admin
db.add_admin(user_id=123456789, admin_type='gc_admins')  # Group chat admin
```

### Removing Admins

```python
# Remove from specific admin type
db.remove_admin(user_id=123456789, admin_type='admins')
```

### Checking Admin Status

```python
# Check if user is admin (any type)
is_admin = db.is_admin(user_id=123456789)

# Check specific admin type
is_owner = db.is_admin(user_id=123456789, admin_type='owner')
is_group_admin = db.is_admin(user_id=123456789, admin_type='gc_admins')
```

### Getting Admin Lists

```python
admins_data = db.load_data('admins')
owners = admins_data.get('owner', [])
general_admins = admins_data.get('admins', [])
elders = admins_data.get('elders', [])
```

## Ban Management

### Banning Users

```python
db.ban_user(
    user_id=123456789,
    reason="Spamming",
    banned_by=987654321  # Admin ID who banned
)
```

### Unbanning Users

```python
success = db.unban_user(user_id=123456789)
```

### Checking Ban Status

```python
is_banned = db.is_banned(user_id=123456789)
```

### Getting Ban Information

```python
ban_info = db.get_ban_info(user_id=123456789)
if ban_info:
    print(f"Banned at: {ban_info['banned_at']}")
    print(f"Reason: {ban_info['reason']}")
    print(f"Banned by: {ban_info['banned_by']}")
```

## Command Management

### Disabling Commands

```python
success = db.disable_command('dangerous_command')
```

### Enabling Commands

```python
success = db.enable_command('dangerous_command')
```

### Checking Command Status

```python
is_disabled = db.is_command_disabled('command_name')
```

### Getting Disabled Commands

```python
disabled_commands = db.get_disabled_commands()
print(f"Disabled commands: {disabled_commands}")
```

### Updating Command Status in Bot Data

```python
db.update_bot_command_status('command_name', disabled=True)
```

## Statistics

### Command Usage Tracking

```python
# Increment command usage
db.increment_command_usage('help', user_id=123456789)

# Get command statistics
stats = db.get_command_stats()
help_stats = db.get_command_stats('help')

if help_stats:
    print(f"Help command used {help_stats['total_uses']} times")
    print(f"Unique users: {help_stats['unique_users']}")
```

### Bot Statistics

```python
# Update various bot stats
db.update_bot_stats(
    total_commands=150,
    total_users=50,
    version='1.2.0'
)

# Get bot statistics
bot_stats = db.get_bot_stats()
print(f"Bot started at: {bot_stats.get('started_at')}")
print(f"Total commands: {bot_stats.get('total_commands')}")
```

## Advanced Usage

### Custom Database Operations

```python
# Create a custom database file
custom_data = {
    'settings': {
        'theme': 'dark',
        'language': 'en'
    },
    'features': ['feature1', 'feature2']
}
db.save_data('custom_settings', custom_data)

# Load and modify
settings = db.load_data('custom_settings')
settings['settings']['theme'] = 'light'
db.save_data('custom_settings', settings)
```

### Bot-Specific Data

```python
# Get bot-specific information
bot_info = db.get_bot_info()
if bot_info:
    print(f"Bot name: {bot_info.get('bot_name')}")
    print(f"Owner ID: {bot_info.get('owner_id')}")

    # Access commands configuration
    commands = bot_info.get('commands', {})
    for cmd_name, cmd_info in commands.items():
        print(f"{cmd_name}: {cmd_info.get('description')}")
```

### Bulk Operations

```python
# Bulk user operations
users_data = db.load_data('users')
for user_id, user_data in users_data.items():
    # Update all users with a new field
    db.update_user(int(user_id), new_field='value')
```

### Data Validation

```python
# Validate data before saving
def save_user_preferences(user_id, preferences):
    if not isinstance(preferences, dict):
        raise ValueError("Preferences must be a dictionary")

    # Validate preference keys
    allowed_keys = ['theme', 'notifications', 'language']
    for key in preferences.keys():
        if key not in allowed_keys:
            raise ValueError(f"Invalid preference key: {key}")

    # Save validated data
    db.update_user(user_id, preferences=preferences)
```

### Backup and Recovery

```python
# Manual backup
import shutil
import os

def backup_database():
    backup_dir = 'data/backup'
    os.makedirs(backup_dir, exist_ok=True)

    for filename in os.listdir('data'):
        if filename.endswith('.json'):
            src = os.path.join('data', filename)
            dst = os.path.join(backup_dir, filename)
            shutil.copy2(src, dst)

# The database automatically creates backups when files are corrupted
```

### Performance Considerations

```python
# Cache frequently accessed data
class DataCache:
    def __init__(self):
        self._cache = {}
        self._cache_time = {}

    def get_cached_data(self, db_name, max_age=300):  # 5 minutes
        current_time = time.time()

        if db_name in self._cache_time:
            if current_time - self._cache_time[db_name] < max_age:
                return self._cache[db_name]

        # Cache miss - load from database
        data = db.load_data(db_name)
        self._cache[db_name] = data
        self._cache_time[db_name] = current_time
        return data

# Usage
cache = DataCache()
users = cache.get_cached_data('users')
```

## Error Handling

```python
try:
    user = db.get_user(user_id)
    if not user:
        # Handle user not found
        pass
except Exception as e:
    logger.error(f"Database error: {e}")
    # Handle database errors gracefully
```

## Database Schema

### Users Schema
```json
{
  "123456789": {
    "user_id": 123456789,
    "role": "user",
    "joined_at": 1640995200.0,
    "last_seen": 1640995300.0,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "custom_field": "value"
  }
}
```

### Admins Schema
```json
{
  "owner": [123456789],
  "admins": [987654321, 111111111],
  "elders": [222222222],
  "gc_admins": [],
  "ch_admins": []
}
```

### Command Stats Schema
```json
{
  "help": {
    "total_uses": 150,
    "unique_users": 45,
    "last_used": 1640995300.0,
    "users": {
      "123456789": 5,
      "987654321": 3
    }
  }
}
```

## Best Practices

1. **Always check return values** from database operations
2. **Use appropriate data types** (strings, numbers, booleans)
3. **Handle missing data gracefully** with `.get()` methods
4. **Validate data** before saving to prevent corruption
5. **Use transactions** for related operations (though not supported in JSON)
6. **Backup important data** regularly
7. **Log database operations** for debugging
8. **Avoid storing sensitive data** in plain JSON files
9. **Use caching** for frequently accessed data
10. **Test database operations** thoroughly

## Troubleshooting

### Common Issues

1. **Permission errors**: Ensure the bot has write access to the `data/` directory
2. **Corrupted files**: The system automatically creates backups of corrupted files
3. **Large files**: JSON files can become large; consider pagination for large datasets
4. **Concurrent access**: The database is thread-safe but avoid simultaneous writes
5. **Memory usage**: Large datasets are loaded entirely into memory

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check database file contents
import json
with open('data/users.json', 'r') as f:
    data = json.load(f)
    print(json.dumps(data, indent=2))
```

## Need Help?

- Check the `core/database.py` file for all available methods
- Review existing commands for database usage examples
- Use the `/help` command to see available database-related commands
- Check logs for database operation errors