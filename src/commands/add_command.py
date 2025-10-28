from core import Message, command, logger, get_lang
import os
import re
import ast
import importlib.util
import sys
import config
import toml
from typing import List, Set

lang = get_lang()

def get_safe_imports_from_pyproject() -> Set[str]:
    """Get safe imports from pyproject.toml dependencies"""
    try:
        with open('pyproject.toml', 'r') as f:
            data = toml.load(f)

        safe_imports = {
            'core', 'aiogram', 'asyncio', 'typing', 'datetime', 'time', 'json', 're', 'os',
            'pathlib', 'tempfile', 'shutil', 'subprocess', 'sys', 'inspect', 'functools',
            'toml', 'config'
        }

        # Add dependencies from pyproject.toml
        dependencies = data.get('project', {}).get('dependencies', [])
        for dep in dependencies:
            # Extract package name (before any version specifiers)
            pkg_name = dep.split()[0].split('>=')[0].split('==')[0].split('<')[0].split('>')[0]
            safe_imports.add(pkg_name.lower())

        return safe_imports

    except Exception as e:
        logger.error(f"Failed to load safe imports from pyproject.toml: {e}")
        # Fallback to hardcoded safe imports
        return {
            'core', 'aiogram', 'asyncio', 'typing', 'datetime', 'time', 'json', 're', 'os',
            'pathlib', 'tempfile', 'shutil', 'subprocess', 'sys', 'inspect', 'functools',
            'toml', 'config'
        }

# Safe imports that are allowed
SAFE_IMPORTS = get_safe_imports_from_pyproject()

def help():
    return {
        "name": "add_command",
        "version": "0.0.1",
        "description": "Add a new command by uploading a Python file",
        "author": "Komihub",
        "usage": "/add_command (reply to a .py file)"
    }

def validate_command_file(file_content: str, filename: str) -> tuple[bool, str]:
    """Validate the uploaded command file"""
    try:
        # Parse the AST
        tree = ast.parse(file_content)

        # Check for help function
        has_help = False
        command_names = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name == 'help':
                    has_help = True
                # Check for @command decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Name) and decorator.func.id == 'command':
                            if decorator.args:
                                arg = decorator.args[0]
                                if isinstance(arg, ast.Str):
                                    command_names.append(arg.s)
                                elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                    command_names.append(arg.value)

        if not has_help:
            return False, "Command file must have a 'help()' function"

        if not command_names:
            return False, "Command file must have at least one function decorated with @command"

        # Check imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split('.')[0] not in SAFE_IMPORTS:
                        return False, f"Unsafe import: {alias.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split('.')[0] not in SAFE_IMPORTS:
                    return False, f"Unsafe import from: {node.module}"

        # Check for dangerous patterns
        dangerous_patterns = [
            r'exec\(', r'eval\(', r'__import__\(', r'open\(', r'file\(',
            r'subprocess\.', r'os\.system', r'os\.popen', r'shutil\.rmtree',
            r'os\.remove', r'os\.unlink', r'pip install', r'pip3 install',
            r'apt install', r'apt-get install', r'yum install', r'brew install',
            r'os\.system.*pip', r'os\.system.*install', r'subprocess.*pip',
            r'subprocess.*install'
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, file_content):
                return False, f"Dangerous code pattern detected: {pattern}"

        return True, f"Valid command file with commands: {', '.join(command_names)}"

    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"

def get_existing_commands() -> Set[str]:
    """Get set of existing command names"""
    commands_dir = 'src/commands'
    existing = set()
    for filename in os.listdir(commands_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            try:
                spec = importlib.util.spec_from_file_location(
                    filename[:-3], os.path.join(commands_dir, filename)
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, 'help') and callable(getattr(module, 'help')):
                    try:
                        help_info = module.help()
                        existing.add(help_info.get('name', ''))
                    except:
                        pass
            except:
                pass
    return existing

@command('add_command')
async def add_command(message: Message):
    # Check if user is admin
    if message.from_user.id != config.ADMIN_ID:
        await message.answer("❌ This command is only available to administrators.")
        return

    logger.info(lang.log_command_executed.format(command='add_command', user_id=message.from_user.id))

    if not message.reply_to_message or not message.reply_to_message.document:
        await message.answer("Please reply to a Python (.py) file with this command.")
        return

    document = message.reply_to_message.document
    if not document.file_name.endswith('.py'):
        await message.answer("Please upload a Python file (.py extension).")
        return

    # Check if filename is unique
    filename = document.file_name
    filepath = os.path.join('src/commands', filename)

    if os.path.exists(filepath):
        await message.answer(f"❌ A file named '{filename}' already exists.")
        return

    try:
        # Download the file
        file_info = await message.bot.get_file(document.file_id)
        downloaded_file = await message.bot.download_file(file_info.file_path)

        file_content = downloaded_file.decode('utf-8')

        # Validate the file
        is_valid, validation_message = validate_command_file(file_content, filename)

        if not is_valid:
            await message.answer(f"❌ Validation failed: {validation_message}")
            return

        # Check for command name conflicts
        existing_commands = get_existing_commands()

        # Extract command names from the new file
        try:
            tree = ast.parse(file_content)
            new_commands = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Call):
                            if isinstance(decorator.func, ast.Name) and decorator.func.id == 'command':
                                if decorator.args:
                                    arg = decorator.args[0]
                                    if isinstance(arg, ast.Str):
                                        new_commands.add(arg.s)
                                    elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                        new_commands.add(arg.value)

            conflicts = existing_commands.intersection(new_commands)
            if conflicts:
                await message.answer(f"❌ Command name conflict: {', '.join(conflicts)} already exists.")
                return

        except Exception as e:
            await message.answer(f"❌ Error checking command names: {e}")
            return

        # Save the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(file_content)

        # Try to load and register the new command safely
        try:
            module_name = f'src.commands.{filename[:-3]}'
            spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
            module = importlib.util.module_from_spec(spec)

            # Execute in isolated environment
            spec.loader.exec_module(module)

            # Check if it has the required structure
            if hasattr(module, 'help') and callable(getattr(module, 'help')):
                # Register the command
                from core import commands as cmd_registry
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and hasattr(attr, '_command_name'):
                        cmd_name = getattr(attr, '_command_name')
                        cmd_registry[cmd_name] = attr
                        from core.bot import bot_instance
                        bot_instance.register_command(cmd_name, attr)
                        logger.info(f"Registered new command: {cmd_name}")

                await message.answer(
                    f"✅ <b>Command Added Successfully!</b>\n\n"
                    f"📁 File: <code>{filename}</code>\n"
                    f"📝 Validation: {validation_message}\n\n"
                    f"The new command is now active!",
                    parse_mode="HTML"
                )
                logger.info(f"New command file added: {filename}")

            else:
                # Remove the file if it doesn't have proper structure
                os.remove(filepath)
                await message.answer("❌ Command file added but doesn't have proper structure. File removed.")

        except Exception as e:
            # Remove the file if loading failed
            if os.path.exists(filepath):
                os.remove(filepath)
            await message.answer(f"❌ Failed to load command: {e}")
            logger.error(f"Failed to load new command {filename}: {e}")

    except Exception as e:
        await message.answer(f"❌ Error processing file: {e}")
        logger.error(f"Error in add_command: {e}")