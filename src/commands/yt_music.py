from core import Message, command, logger, get_lang
import re
import json
import yt_dlp
import os
import tempfile
import config

lang = get_lang()

def help():
    return {
        "name": "yt_music",
        "version": "0.0.1",
        "description": "Search and download YouTube music/audio",
        "author": "Komihub",
        "usage": "/yt_music <search query> - Search for music\n/yt_music <YouTube URL> - Download audio from URL"
    }

def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def format_duration(seconds: int) -> str:
    """Format seconds into MM:SS"""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"

@command('yt_music')
async def yt_music_command(message: Message):
    logger.info(lang.log_command_executed.format(command='yt_music', user_id=message.from_user.id))

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "🎵 <b>YouTube Music Search & Download</b>\n\n"
            "Usage:\n"
            "/yt_music <search query> - Search for music\n"
            "/yt_music <YouTube URL> - Download audio\n\n"
            "Examples:\n"
            "/yt_music billie eilish bad guy\n"
            "/yt_music https://youtu.be/dQw4w9WgXcQ",
            parse_mode="HTML"
        )
        return

    query = args[1].strip()

    # Check if it's a YouTube URL
    video_id = extract_youtube_id(query)
    if video_id:
        # Handle direct download
        await message.answer("🎵 Downloading audio from YouTube...", parse_mode="HTML")

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
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(f"https://youtu.be/{video_id}", download=False)

                # Check file size (Telegram limit: 2GB for regular users, 4GB for premium)
                if info.get('filesize', 0) > 2 * 1024 * 1024 * 1024:  # 2GB
                    await message.answer("❌ Audio file is too large (>2GB). Telegram limit exceeded.")
                    return

                # Download the audio
                ydl.download([f"https://youtu.be/{video_id}"])

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
                    # Send the audio file
                    with open(expected_filename, 'rb') as audio_file:
                        await message.answer_audio(
                            audio=audio_file,
                            title=info.get('title', 'YouTube Audio'),
                            performer=info.get('uploader', 'Unknown'),
                            duration=info.get('duration', 0),
                            caption=f"🎵 Downloaded from YouTube\n📹 {info.get('title', 'Unknown')}\n👤 {info.get('uploader', 'Unknown')}"
                        )

                    # Clean up
                    os.remove(expected_filename)
                    logger.info(f"Downloaded and sent YouTube audio: {info.get('title', 'Unknown')}")
                else:
                    await message.answer("❌ Failed to find downloaded audio file.")

        except Exception as e:
            logger.error(f"YouTube download error: {e}")
            await message.answer(f"❌ Failed to download audio: {str(e)}")

        return

    # Handle search
    try:
        # Simulate YouTube search (in real implementation, would use YouTube API)
        await message.answer(f"🔍 Searching for: <b>{query}</b>\n\n<i>YouTube search requires API key configuration</i>", parse_mode="HTML")

        # Mock search results
        mock_results = [
            {
                "title": f"{query} - Official Music Video",
                "channel": "Artist Channel",
                "duration": "3:45",
                "views": "10M",
                "url": "https://youtu.be/example1"
            },
            {
                "title": f"{query} (Lyrics)",
                "channel": "Lyrics Channel",
                "duration": "3:42",
                "views": "5M",
                "url": "https://youtu.be/example2"
            },
            {
                "title": f"{query} - Live Performance",
                "channel": "Live Music",
                "duration": "4:15",
                "views": "2M",
                "url": "https://youtu.be/example3"
            }
        ]

        response = f"🎵 <b>YouTube Music Search Results</b>\n\n"
        response += f"Query: <code>{query}</code>\n\n"

        for i, result in enumerate(mock_results, 1):
            response += f"{i}. <b>{result['title']}</b>\n"
            response += f"   👤 {result['channel']}\n"
            response += f"   ⏱️ {result['duration']} | 👁️ {result['views']} views\n"
            response += f"   🔗 {result['url']}\n\n"

        response += "<i>Use /yt_music <URL> to download audio</i>"

        await message.answer(response, parse_mode="HTML")

    except Exception as e:
        logger.error(f"YouTube search error: {e}")
        await message.answer("❌ Failed to search YouTube. Please try again.")