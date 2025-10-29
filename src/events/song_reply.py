from core import logger, get_lang, FSInputFile, Message 
import time
import config
import yt_dlp
import os
import tempfile
import asyncio

lang = get_lang()

async def progress_hook(d, progress_msg, message):
    """Progress hook for yt-dlp downloads"""
    if d['status'] == 'downloading':
        try:
            percent = d.get('_percent_str', '0%').strip()
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')

            progress_text = f"🎵 Downloading: <b>{progress_msg.text.split('Downloading:')[1].split('\\n')[0].strip()}</b>\n⏳ Progress: {percent}\n🚀 Speed: {speed}\n⏰ ETA: {eta}"

            # Update progress message
            await progress_msg.edit_text(progress_text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Progress update error: {e}")
    elif d['status'] == 'finished':
        try:
            await progress_msg.edit_text(f"🎵 Download complete! Processing audio...\n{progress_msg.text.split('\\n')[0]}", parse_mode="HTML")
        except Exception as e:
            logger.error(f"Progress finish error: {e}")

async def handle_song_reply(message: Message):
    """Handle replies to song search results"""
    if not message.reply_to_message or not message.text:
        return

    # Check if replying to bot's message
    if not hasattr(message.reply_to_message, 'from_user') or message.reply_to_message.from_user.id != message.bot.id:
        return

    # Check if the reply is a number 1-5
    try:
        selection = int(message.text.strip())
        if selection < 1 or selection > 5:
            return
    except ValueError:
        return

    # Check if user has cached search results
    search_data = None

    # Import here to avoid circular imports
    from src.commands.yt_music import yt_music_command, song_command

    # Check yt_music cache
    if hasattr(yt_music_command, 'cache') and message.from_user.id in yt_music_command.cache:
        search_data = yt_music_command.cache[message.from_user.id]

    # Check song cache
    if not search_data and hasattr(song_command, 'cache') and message.from_user.id in song_command.cache:
        search_data = song_command.cache[message.from_user.id]

    if not search_data:
        return

    # Check if reply is recent (within 10 minutes)
    import datetime
    current_time = datetime.datetime.now().timestamp()
    if current_time - search_data['timestamp'] > 600:
        return

    results = search_data['results']
    if selection > len(results):
        await message.answer("❌ Invalid selection number.")
        return

    selected_video = results[selection - 1]

    progress_msg = await message.answer(f"🎵 Downloading: <b>{selected_video['title']}</b>\n⏳ Progress: 0%", parse_mode="HTML")

    try:
        # yt-dlp options for audio extraction
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(tempfile.gettempdir(), '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [lambda d: progress_hook(d, progress_msg, message)],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first
            info = ydl.extract_info(selected_video['url'], download=False)

            # Check file size (Telegram limit: 50MB for bots, 2GB for regular users, 4GB for premium)
            filesize = info.get('filesize', 0)
            if filesize > 50 * 1024 * 1024:  # 50MB for bots
                await message.answer("❌ Audio file is too large (>50MB). Telegram bot limit exceeded.")
                return

            # Download the audio
            ydl.download([selected_video['url']])

            # Find the downloaded file
            expected_filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            if not os.path.exists(expected_filename):
                # Try to find the actual file
                temp_dir = tempfile.gettempdir()
                for file in os.listdir(temp_dir):
                    if file.endswith('.mp3') and info['title'] in file:
                        expected_filename = os.path.join(temp_dir, file)
                        break

            if os.path.exists(expected_filename):
                # Delete progress message
                try:
                    await progress_msg.delete()
                except:
                    pass

                # Send the audio file
                audio_file = FSInputFile(expected_filename)
                await message.answer_audio(
                    audio=audio_file,
                    title=info.get('title', 'YouTube Audio'),
                    performer=info.get('uploader', 'Unknown'),
                    duration=info.get('duration', 0),
                    caption=f"🎵 Downloaded from YouTube\n📹 {info.get('title', 'Unknown')}\n👤 {info.get('uploader', 'Unknown')}\n🔗 {selected_video['url']}"
                )

                # Clean up
                os.remove(expected_filename)
                logger.info(f"Downloaded and sent YouTube audio: {info.get('title', 'Unknown')}")

                # Clear cache after successful download
                if hasattr(yt_music_command, 'cache'):
                    yt_music_command.cache.pop(message.from_user.id, None)
                if hasattr(song_command, 'cache'):
                    song_command.cache.pop(message.from_user.id, None)

            else:
                await message.answer("❌ Failed to find downloaded audio file.")

    except Exception as e:
        logger.error(f"YouTube download error: {e}")
        await message.answer(f"❌ Failed to download audio: {str(e)}")

# Register the event
from core.bot import bot_instance
bot_instance.register_event('message', handle_song_reply)