# Komihub Bot-এর ডেটাবেস গাইড

এই গাইডটি Komihub বট ফ্রেমওয়ার্কের JSON-ভিত্তিক ডেটাবেস সিস্টেম ব্যবহারের পদ্ধতি ব্যাখ্যা করে।

## সূচিপত্র
- [ডেটাবেস ওভারভিউ](#ডেটাবেস-ওভারভিউ)
- [ডেটাবেস ফাইল](#ডেটাবেস-ফাইল)
- [বেসিক অপারেশন](#বেসিক-অপারেশন)
- [ইউজার ম্যানেজমেন্ট](#ইউজার-ম্যানেজমেন্ট)
- [অ্যাডমিন ম্যানেজমেন্ট](#অ্যাডমিন-ম্যানেজমেন্ট)
- [ব্যান ম্যানেজমেন্ট](#ব্যান-ম্যানেজমেন্ট)
- [কমান্ড ম্যানেজমেন্ট](#কমান্ড-ম্যানেজমেন্ট)
- [স্ট্যাটিস্টিক্স](#স্ট্যাটিস্টিক্স)
- [অ্যাডভান্সড ইউজ](#অ্যাডভান্সড-ইউজ)

## ডেটাবেস ওভারভিউ

Komihub বট `data/` ডিরেক্টরিতে JSON-ভিত্তিক ডেটাবেস সিস্টেম ব্যবহার করে। এটি প্রদান করে:

- **সিম্পল ফাইল-ভিত্তিক স্টোরেজ** - কোনো এক্সটার্নাল ডেটাবেস প্রয়োজন নেই
- **JSON ফরম্যাট** - হিউম্যান-রিডেবল এবং এডিটেবল
- **অটোমেটিক ইনিশিয়ালাইজেশন** - প্রথম রানে ফাইল এবং ডিফল্ট ডেটা তৈরি করে
- **করাপশনে ব্যাকআপ** - করাপ্টেড ফাইল অটোমেটিক্যালি ব্যাকআপ করে
- **থ্রেড-সেফ অপারেশন** - কনকারেন্ট অ্যাক্সেসের জন্য সেফ

## ডেটাবেস ফাইল

সিস্টেম নিচের JSON ফাইল ম্যানেজ করে:

- `bot_stats.json` - বট স্ট্যাটিস্টিক্স এবং মেটাডেটা
- `users.json` - ইউজার তথ্য এবং রোল
- `admins.json` - অ্যাডমিন কনফিগারেশন
- `bans.json` - ব্যান করা ইউজারের তথ্য
- `disabled_commands.json` - ডিসেবল করা কমান্ডের লিস্ট
- `command_stats.json` - কমান্ড ব্যবহার স্ট্যাটিস্টিক্স
- `bots/bot_{admin_id}.json` - বট-স্পেসিফিক কনফিগারেশন

## বেসিক অপারেশন

### ডেটাবেস ইমপোর্ট করা

```python
from core.database import db
```

### ডেটা লোড করা

```python
# ডেটাবেস ফাইল থেকে ডেটা লোড করুন
users = db.load_data('users')
admins = db.load_data('admins')
```

### ডেটা সেভ করা

```python
# ডেটাবেস ফাইলে ডেটা সেভ করুন
data = {'key': 'value', 'number': 42}
success = db.save_data('custom_data', data)
```

### ডেটা আপডেট করা

```python
# বট স্ট্যাটিস্টিক্স আপডেট করুন
db.update_bot_stats(total_commands=100, online_since=time.time())
```

## ইউজার ম্যানেজমেন্ট

### ইউজার যোগ করা

```python
user_data = {
    'username': 'john_doe',
    'first_name': 'John',
    'last_name': 'Doe'
}
db.add_user(user_id=123456789, user_data=user_data)
```

### ইউজার ডেটা পাওয়া

```python
user = db.get_user(user_id=123456789)
if user:
    print(f"ইউজার রোল: {user.get('role', 'user')}")
    print(f"জয়েন তারিখ: {user.get('joined_at')}")
```

### ইউজার ডেটা আপডেট করা

```python
# লাস্ট সিন টাইম এবং অন্যান্য ডেটা আপডেট করুন
db.update_user(user_id=123456789, last_seen=time.time(), custom_field='value')
```

### ইউজার রোল সেট করা

```python
# ইউজার রোল সেট করুন
db.set_user_role(user_id=123456789, role='admin')

# উপলব্ধ রোল: 'user', 'admin', 'elder', 'owner', ইত্যাদি
```

### রোল অনুসারে ইউজার পাওয়া

```python
# সব অ্যাডমিন পান
admins = db.get_role_users('admin')

# স্পেসিফিক রোলের সব ইউজার পান
elders = db.get_role_users('elder')
```

## অ্যাডমিন ম্যানেজমেন্ট

### অ্যাডমিন যোগ করা

```python
# স্পেসিফিক টাইপের অ্যাডমিন যোগ করুন
db.add_admin(user_id=123456789, admin_type='admins')  # জেনারেল অ্যাডমিন
db.add_admin(user_id=123456789, admin_type='elders')  # সিনিয়র অ্যাডমিন
db.add_admin(user_id=123456789, admin_type='gc_admins')  # গ্রুপ চ্যাট অ্যাডমিন
```

### অ্যাডমিন রিমুভ করা

```python
# স্পেসিফিক অ্যাডমিন টাইপ থেকে রিমুভ করুন
db.remove_admin(user_id=123456789, admin_type='admins')
```

### অ্যাডমিন স্ট্যাটাস চেক করা

```python
# ইউজার অ্যাডমিন কিনা চেক করুন (যেকোনো টাইপ)
is_admin = db.is_admin(user_id=123456789)

# স্পেসিফিক অ্যাডমিন টাইপ চেক করুন
is_owner = db.is_admin(user_id=123456789, admin_type='owner')
is_group_admin = db.is_admin(user_id=123456789, admin_type='gc_admins')
```

### অ্যাডমিন লিস্ট পাওয়া

```python
admins_data = db.load_data('admins')
owners = admins_data.get('owner', [])
general_admins = admins_data.get('admins', [])
elders = admins_data.get('elders', [])
```

## ব্যান ম্যানেজমেন্ট

### ইউজার ব্যান করা

```python
db.ban_user(
    user_id=123456789,
    reason="স্প্যামিং",
    banned_by=987654321  # ব্যান করা অ্যাডমিনের ID
)
```

### ইউজার আনব্যান করা

```python
success = db.unban_user(user_id=123456789)
```

### ব্যান স্ট্যাটাস চেক করা

```python
is_banned = db.is_banned(user_id=123456789)
```

### ব্যান তথ্য পাওয়া

```python
ban_info = db.get_ban_info(user_id=123456789)
if ban_info:
    print(f"ব্যানের সময়: {ban_info['banned_at']}")
    print(f"কারণ: {ban_info['reason']}")
    print(f"ব্যান করেছেন: {ban_info['banned_by']}")
```

## কমান্ড ম্যানেজমেন্ট

### কমান্ড ডিসেবল করা

```python
success = db.disable_command('dangerous_command')
```

### কমান্ড ইনেবল করা

```python
success = db.enable_command('dangerous_command')
```

### কমান্ড স্ট্যাটাস চেক করা

```python
is_disabled = db.is_command_disabled('command_name')
```

### ডিসেবল করা কমান্ড পাওয়া

```python
disabled_commands = db.get_disabled_commands()
print(f"ডিসেবল করা কমান্ড: {disabled_commands}")
```

### বট ডেটায় কমান্ড স্ট্যাটাস আপডেট করা

```python
db.update_bot_command_status('command_name', disabled=True)
```

## স্ট্যাটিস্টিক্স

### কমান্ড ব্যবহার ট্র্যাকিং

```python
# কমান্ড ব্যবহার ইনক্রিমেন্ট করুন
db.increment_command_usage('help', user_id=123456789)

# কমান্ড স্ট্যাটিস্টিক্স পান
stats = db.get_command_stats()
help_stats = db.get_command_stats('help')

if help_stats:
    print(f"হেল্প কমান্ড {help_stats['total_uses']} বার ব্যবহার হয়েছে")
    print(f"ইউনিক ইউজার: {help_stats['unique_users']}")
```

### বট স্ট্যাটিস্টিক্স

```python
# বিভিন্ন বট স্ট্যাট আপডেট করুন
db.update_bot_stats(
    total_commands=150,
    total_users=50,
    version='1.2.0'
)

# বট স্ট্যাটিস্টিক্স পান
bot_stats = db.get_bot_stats()
print(f"বট শুরু হয়েছে: {bot_stats.get('started_at')}")
print(f"মোট কমান্ড: {bot_stats.get('total_commands')}")
```

## অ্যাডভান্সড ইউজ

### কাস্টম ডেটাবেস অপারেশন

```python
# কাস্টম ডেটাবেস ফাইল তৈরি করুন
custom_data = {
    'settings': {
        'theme': 'dark',
        'language': 'en'
    },
    'features': ['feature1', 'feature2']
}
db.save_data('custom_settings', custom_data)

# লোড এবং মডিফাই করুন
settings = db.load_data('custom_settings')
settings['settings']['theme'] = 'light'
db.save_data('custom_settings', settings)
```

### বট-স্পেসিফিক ডেটা

```python
# বট-স্পেসিফিক তথ্য পান
bot_info = db.get_bot_info()
if bot_info:
    print(f"বট নাম: {bot_info.get('bot_name')}")
    print(f"ওনার ID: {bot_info.get('owner_id')}")

    # কমান্ড কনফিগারেশন অ্যাক্সেস করুন
    commands = bot_info.get('commands', {})
    for cmd_name, cmd_info in commands.items():
        print(f"{cmd_name}: {cmd_info.get('description')}")
```

### বাল্ক অপারেশন

```python
# বাল্ক ইউজার অপারেশন
users_data = db.load_data('users')
for user_id, user_data in users_data.items():
    # সব ইউজারকে নতুন ফিল্ড যোগ করুন
    db.update_user(int(user_id), new_field='value')
```

### ডেটা ভ্যালিডেশন

```python
# সেভ করার আগে ডেটা ভ্যালিডেট করুন
def save_user_preferences(user_id, preferences):
    if not isinstance(preferences, dict):
        raise ValueError("প্রেফারেন্স অবশ্যই একটি ডিকশনারি হতে হবে")

    # প্রেফারেন্স কী ভ্যালিডেট করুন
    allowed_keys = ['theme', 'notifications', 'language']
    for key in preferences.keys():
        if key not in allowed_keys:
            raise ValueError(f"ইনভ্যালিড প্রেফারেন্স কী: {key}")

    # ভ্যালিডেটেড ডেটা সেভ করুন
    db.update_user(user_id, preferences=preferences)
```

### ব্যাকআপ এবং রিকভারি

```python
# ম্যানুয়াল ব্যাকআপ
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

# করাপ্টেড ফাইল হলে সিস্টেম অটোমেটিক্যালি ব্যাকআপ তৈরি করে
```

### পারফরম্যান্স কনসিডারেশন

```python
# ফ্রিকোয়েন্টলি অ্যাক্সেস করা ডেটা ক্যাশ করুন
class DataCache:
    def __init__(self):
        self._cache = {}
        self._cache_time = {}

    def get_cached_data(self, db_name, max_age=300):  # 5 মিনিট
        current_time = time.time()

        if db_name in self._cache_time:
            if current_time - self._cache_time[db_name] < max_age:
                return self._cache[db_name]

        # ক্যাশ মিস - ডেটাবেস থেকে লোড করুন
        data = db.load_data(db_name)
        self._cache[db_name] = data
        self._cache_time[db_name] = current_time
        return data

# ব্যবহার
cache = DataCache()
users = cache.get_cached_data('users')
```

## এরর হ্যান্ডলিং

```python
try:
    user = db.get_user(user_id)
    if not user:
        # ইউজার না পাওয়া হলে হ্যান্ডেল করুন
        pass
except Exception as e:
    logger.error(f"ডেটাবেস এরর: {e}")
    # ডেটাবেস এরর গ্রেসফুলি হ্যান্ডেল করুন
```

## ডেটাবেস স্কিমা

### ইউজার স্কিমা
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

### অ্যাডমিন স্কিমা
```json
{
  "owner": [123456789],
  "admins": [987654321, 111111111],
  "elders": [222222222],
  "gc_admins": [],
  "ch_admins": []
}
```

### কমান্ড স্ট্যাট স্কিমা
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

## বেস্ট প্র্যাকটিস

1. **রিটার্ন ভ্যালু সর্বদা চেক করুন** ডেটাবেস অপারেশন থেকে
2. **উপযুক্ত ডেটা টাইপ ব্যবহার করুন** (স্ট্রিং, নাম্বার, বুলিয়ান)
3. **মিসিং ডেটা গ্রেসফুলি হ্যান্ডেল করুন** `.get()` মেথড ব্যবহার করে
4. **করাপশন এড়াতে ডেটা ভ্যালিডেট করুন** সেভ করার আগে
5. **রিলেটেড অপারেশনের জন্য ট্রানজ্যাকশন ব্যবহার করুন** (JSON-এ সাপোর্টেড না হলেও)
6. **ইম্পর্ট্যান্ট ডেটা রেগুলারলি ব্যাকআপ করুন**
7. **ডেভেলপমেন্টের জন্য ডেটাবেস অপারেশন লগ করুন**
8. **প্লেইন JSON ফাইলে সেনসিটিভ ডেটা স্টোর করবেন না**
9. **ফ্রিকোয়েন্টলি অ্যাক্সেস করা ডেটার জন্য ক্যাশিং ব্যবহার করুন**
10. **ডেটাবেস অপারেশন ভালোভাবে টেস্ট করুন**

## ট্রাবলশুটিং

### কমন সমস্যা

1. **পারমিশন এরর**: বটের `data/` ডিরেক্টরিতে রাইট অ্যাক্সেস আছে কিনা নিশ্চিত করুন
2. **করাপ্টেড ফাইল**: করাপ্টেড ফাইল হলে সিস্টেম অটোমেটিক্যালি ব্যাকআপ তৈরি করে
3. **বড় ফাইল**: বড় ডেটাসেটের জন্য JSON ফাইল বড় হয়ে যেতে পারে; পেজিনেশন কনসিডার করুন
4. **কনকারেন্ট অ্যাক্সেস**: ডেটাবেস থ্রেড-সেফ কিন্তু সিমালটেনিয়াস রাইট এড়ান
5. **মেমরি ইউজ**: বড় ডেটাসেট সম্পূর্ণ মেমরিতে লোড হয়

### ডিবাগিং

```python
# ডিবাগ লগিং ইনেবল করুন
import logging
logging.basicConfig(level=logging.DEBUG)

# ডেটাবেস ফাইল কনটেন্ট চেক করুন
import json
with open('data/users.json', 'r') as f:
    data = json.load(f)
    print(json.dumps(data, indent=2))
```

## সাহায্য প্রয়োজন?

- `core/database.py` ফাইলে সব উপলব্ধ মেথড দেখুন
- বিদ্যমান কমান্ডে ডেটাবেস ব্যবহারের উদাহরণ দেখুন
- `/help` কমান্ড দিয়ে উপলব্ধ ডেটাবেস-রিলেটেড কমান্ড দেখুন
- ডেটাবেস অপারেশন এররের জন্য লগ চেক করুন

---

**আরও তথ্যের জন্য ইংলিশ ভার্সন দেখুন:** [database-guide.md](database-guide.md)