import json
import os
import time
import importlib.util
from typing import Dict, List, Any, Optional
from .logging import logger


class JSONDatabase:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._ensure_data_dir()

        # Database files
        self.files = {
            "bot_stats": os.path.join(data_dir, "bot_stats.json"),
            "users": os.path.join(data_dir, "users.json"),
            "admins": os.path.join(data_dir, "admins.json"),
            "bans": os.path.join(data_dir, "bans.json"),
            "disabled_commands": os.path.join(data_dir, "disabled_commands.json"),
            "command_stats": os.path.join(data_dir, "command_stats.json"),
        }

        # Initialize databases
        self._init_databases()

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")

    def _init_databases(self):
        """Initialize all database files with default data"""
        # Bot stats
        if not os.path.exists(self.files["bot_stats"]):
            self.save_data(
                "bot_stats",
                {
                    "bot_name": "Komihub Bot",
                    "started_at": time.time(),
                    "total_commands": 0,
                    "total_users": 0,
                    "online_since": time.time(),
                    "version": "1.0.0",
                },
            )

        # Users
        if not os.path.exists(self.files["users"]):
            self.save_data("users", {})

        # Admins
        if not os.path.exists(self.files["admins"]):
            self.save_data(
                "admins",
                {
                    "owner": [6122160777],  # From config
                    "admins": [],
                    "elders": [],
                    "gc_admins": [],  # Group chat admins
                    "ch_admins": [],  # Channel admins
                },
            )

        # Bans
        if not os.path.exists(self.files["bans"]):
            self.save_data("bans", {})

        # Disabled commands
        if not os.path.exists(self.files["disabled_commands"]):
            self.save_data("disabled_commands", [])

        # Command stats
        if not os.path.exists(self.files["command_stats"]):
            self.save_data("command_stats", {})

        # Initialize bot-specific data
        self._init_bot_data()

    def _init_bot_data(self):
        """Initialize bot-specific data"""
        import config

        bot_username = self._get_bot_username()
        bot_file = os.path.join(self.data_dir, "bots", f"{bot_username}.json")

        if not os.path.exists(bot_file):
            # Get all available commands
            commands_info = self._get_all_commands_info()

            bot_data = {
                "bot_username": bot_username,
                "bot_name": config.BOT_NAME,
                "owner_id": config.ADMIN_ID,
                "created_at": time.time(),
                "commands": commands_info,
                "settings": {
                    "language": "en",
                    "maintenance_mode": False,
                    "auto_backup": True,
                },
                "features": {
                    "hot_reload": True,
                    "user_tracking": True,
                    "broadcast_system": True,
                    "admin_management": True,
                },
            }
            os.makedirs(os.path.dirname(bot_file), exist_ok=True)
            with open(bot_file, "w", encoding="utf-8") as f:
                json.dump(bot_data, f, indent=2, ensure_ascii=False)

    def _get_bot_username(self):
        """Get bot username from token or config"""
        import config

        # Extract username from token (basic implementation)
        # In production, you'd want to get this from Telegram API
        return f"bot_{config.ADMIN_ID}"

    def _get_all_commands_info(self):
        """Get information about all available commands"""
        commands_dir = "src/commands"
        commands_info = {}

        for filename in os.listdir(commands_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    module_name = f"src.commands.{filename[:-3]}"
                    spec = importlib.util.spec_from_file_location(
                        filename[:-3], os.path.join(commands_dir, filename)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    if hasattr(module, "help") and callable(getattr(module, "help")):
                        help_info = module.help()
                        command_name = help_info.get("name", filename[:-3])

                        # Check if command requires admin
                        admin_only = False
                        if hasattr(module, "command"):
                            # Check function content for admin checks
                            import inspect

                            source = inspect.getsource(module)
                            admin_only = (
                                "db.is_admin(message.from_user.id)" in source
                                or "message.from_user.id != config.ADMIN_ID" in source
                            )

                        commands_info[command_name] = {
                            "name": command_name,
                            "description": help_info.get(
                                "description", "No description"
                            ),
                            "admin_only": admin_only,
                            "disabled": False,  # Will be updated from disabled_commands
                            "usage": help_info.get("usage", f"/{command_name}"),
                            "author": help_info.get("author", "Unknown"),
                            "version": help_info.get("version", "1.0.0"),
                        }
                except Exception as e:
                    logger.error(f"Error loading command info for {filename}: {e}")

        # Update disabled status
        disabled_commands = self.load_data("disabled_commands")
        for cmd_name in disabled_commands:
            if cmd_name in commands_info:
                commands_info[cmd_name]["disabled"] = True

        return commands_info

    def get_bot_info(self):
        """Get bot-specific information"""
        bot_username = self._get_bot_username()
        bot_file = os.path.join(self.data_dir, "bots", f"{bot_username}.json")

        try:
            with open(bot_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def update_bot_command_status(self, command_name: str, disabled: bool):
        """Update command status in bot data"""
        bot_info = self.get_bot_info()
        if "commands" in bot_info and command_name in bot_info["commands"]:
            bot_info["commands"][command_name]["disabled"] = disabled

            bot_username = self._get_bot_username()
            bot_file = os.path.join(self.data_dir, "bots", f"{bot_username}.json")
            with open(bot_file, "w", encoding="utf-8") as f:
                json.dump(bot_info, f, indent=2, ensure_ascii=False)

    def load_data(self, db_name: str) -> Dict[str, Any]:
        """Load data from a database file"""
        try:
            with open(self.files[db_name], "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:  # Empty file
                    return {}
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error loading {db_name}: {e}")
            # Try to backup corrupted file and create new one
            if os.path.exists(self.files[db_name]):
                backup_path = f"{self.files[db_name]}.backup"
                os.rename(self.files[db_name], backup_path)
                logger.warning(f"Backed up corrupted {db_name} to {backup_path}")
            return {}

    def save_data(self, db_name: str, data: Dict[str, Any]) -> bool:
        """Save data to a database file"""
        try:
            with open(self.files[db_name], "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving {db_name}: {e}")
            return False

    # Bot stats methods
    def update_bot_stats(self, **kwargs):
        """Update bot statistics"""
        stats = self.load_data("bot_stats")
        stats.update(kwargs)
        stats["last_updated"] = time.time()
        self.save_data("bot_stats", stats)

    def get_bot_stats(self):
        """Get bot statistics"""
        return self.load_data("bot_stats")

    # User management methods
    def add_user(self, user_id: int, user_data: Dict[str, Any]):
        """Add or update user data"""
        users = self.load_data("users")
        users[str(user_id)] = {
            "user_id": user_id,
            "role": "user",  # Default role
            "joined_at": time.time(),
            "last_seen": time.time(),
            **user_data,
        }
        self.save_data("users", users)

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user data"""
        users = self.load_data("users")
        return users.get(str(user_id))

    def update_user(self, user_id: int, **kwargs):
        """Update user data"""
        users = self.load_data("users")
        user_key = str(user_id)
        if user_key in users:
            users[user_key].update(kwargs)
            users[user_key]["last_seen"] = time.time()
            self.save_data("users", users)

    # Role management methods
    def get_user_role(self, user_id: int) -> str:
        """Get user role"""
        user = self.get_user(user_id)
        return user.get("role", "user") if user else "user"

    def set_user_role(self, user_id: int, role: str):
        """Set user role"""
        self.update_user(user_id, role=role)

    def get_role_users(self, role: str) -> List[int]:
        """Get all users with a specific role"""
        users = self.load_data("users")
        return [int(uid) for uid, data in users.items() if data.get("role") == role]

    # Admin management methods
    def add_admin(self, user_id: int, admin_type: str = "admins"):
        """Add user to admin list"""
        admins = self.load_data("admins")
        if admin_type not in admins:
            admins[admin_type] = []
        if user_id not in admins[admin_type]:
            admins[admin_type].append(user_id)
            self.save_data("admins", admins)
            # Update user role
            role_map = {
                "owner": "owner",
                "admins": "admin",
                "elders": "elder",
                "gc_admins": "gc_admin",
                "ch_admins": "ch_admin",
            }
            self.set_user_role(user_id, role_map.get(admin_type, "user"))
            return True
        return False

    def remove_admin(self, user_id: int, admin_type: str = "admins"):
        """Remove user from admin list"""
        admins = self.load_data("admins")
        if admin_type in admins and user_id in admins[admin_type]:
            admins[admin_type].remove(user_id)
            self.save_data("admins", admins)
            # Reset to user role if not in other admin lists
            self._update_user_role_from_admins(user_id)
            return True
        return False

    def _update_user_role_from_admins(self, user_id: int):
        """Update user role based on admin status"""
        admins = self.load_data("admins")
        role_hierarchy = ["owner", "admins", "elders", "gc_admins", "ch_admins"]
        role_map = {
            "owner": "owner",
            "admins": "admin",
            "elders": "elder",
            "gc_admins": "gc_admin",
            "ch_admins": "ch_admin",
        }

        for role_type in role_hierarchy:
            if user_id in admins.get(role_type, []):
                self.set_user_role(user_id, role_map[role_type])
                return

        # Default to user if not in any admin list
        self.set_user_role(user_id, "user")

    def is_admin(self, user_id: int, admin_type: str = None) -> bool:
        """Check if user is admin"""
        admins = self.load_data("admins")

        if admin_type:
            return user_id in admins.get(admin_type, [])

        # Check all admin types
        for admin_list in admins.values():
            if user_id in admin_list:
                return True
        return False

    # Ban management methods
    def ban_user(self, user_id: int, reason: str = "", banned_by: int = None):
        """Ban a user"""
        bans = self.load_data("bans")
        bans[str(user_id)] = {
            "user_id": user_id,
            "banned_at": time.time(),
            "reason": reason,
            "banned_by": banned_by,
        }
        self.save_data("bans", bans)

    def unban_user(self, user_id: int):
        """Unban a user"""
        bans = self.load_data("bans")
        if str(user_id) in bans:
            del bans[str(user_id)]
            self.save_data("bans", bans)
            return True
        return False

    def is_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        bans = self.load_data("bans")
        return str(user_id) in bans

    def get_ban_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get ban information"""
        bans = self.load_data("bans")
        return bans.get(str(user_id))

    # Command management methods
    def disable_command(self, command_name: str):
        """Disable a command"""
        disabled = self.load_data("disabled_commands")
        if command_name not in disabled:
            disabled.append(command_name)
            self.save_data("disabled_commands", disabled)
            self.update_bot_command_status(command_name, True)
            return True
        return False

    def enable_command(self, command_name: str):
        """Enable a command"""
        disabled = self.load_data("disabled_commands")
        if command_name in disabled:
            disabled.remove(command_name)
            self.save_data("disabled_commands", disabled)
            self.update_bot_command_status(command_name, False)
            return True
        return False

    def is_command_disabled(self, command_name: str) -> bool:
        """Check if command is disabled"""
        disabled = self.load_data("disabled_commands")
        return command_name in disabled

    def get_disabled_commands(self) -> List[str]:
        """Get list of disabled commands"""
        return self.load_data("disabled_commands")

    # Command stats methods
    def increment_command_usage(self, command_name: str, user_id: int):
        """Increment command usage statistics"""
        stats = self.load_data("command_stats")
        cmd_key = command_name

        if cmd_key not in stats:
            stats[cmd_key] = {
                "total_uses": 0,
                "unique_users": 0,
                "last_used": 0,
                "users": {},
            }

        stats[cmd_key]["total_uses"] += 1
        stats[cmd_key]["last_used"] = time.time()

        user_key = str(user_id)
        if user_key not in stats[cmd_key]["users"]:
            stats[cmd_key]["users"][user_key] = 0
            stats[cmd_key]["unique_users"] += 1

        stats[cmd_key]["users"][user_key] += 1

        self.save_data("command_stats", stats)

    def get_command_stats(self, command_name: str = None):
        """Get command usage statistics"""
        stats = self.load_data("command_stats")
        if command_name:
            return stats.get(command_name, {})
        return stats


# Global database instance
db = JSONDatabase()
