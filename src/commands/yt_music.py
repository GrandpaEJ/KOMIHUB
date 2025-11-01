from core import Message, command, logger, get_lang
import re
import yt_dlp
import os
import tempfile
import config
import requests

lang = get_lang()


async def progress_hook(d, progress_msg, message):
    """Progress hook for yt-dlp downloads"""
    if d["status"] == "downloading":
        try:
            percent = d.get("_percent_str", "0%").strip()
            speed = d.get("_speed_str", "N/A")
            eta = d.get("_eta_str", "N/A")

            progress_text = f"🎵 Downloading audio from YouTube...\n⏳ Progress: {percent}\n🚀 Speed: {speed}\n⏰ ETA: {eta}"

            # Update progress message
            await progress_msg.edit_text(progress_text, parse_mode="HTML")
        except Exception as e:
            logger.error(f"Progress update error: {e}")
    elif d["status"] == "finished":
        try:
            await progress_msg.edit_text(
                "🎵 Download complete! Processing audio...", parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Progress finish error: {e}")


def help():
    return {
        "name": "yt_music",
        "version": "0.0.2",
        "description": "Search and download YouTube music/audio",
        "author": "Komihub",
        "usage": "/yt_music search query - Search for music\n/yt_music YouTube URL - Download audio from URL\n/song SongName - Quick search and select from results",
    }


def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from URL"""
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com\/v\/([a-zA-Z0-9_-]{11})",
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


def search_youtube(query: str, api_key: str, max_results: int = 5):
    """Search YouTube using YouTube Data API v3"""
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": api_key,
        "videoCategoryId": "10",  # Music category
    }

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            # Get video details for duration
            details_url = "https://www.googleapis.com/youtube/v3/videos"
            details_params = {
                "part": "contentDetails,statistics",
                "id": video_id,
                "key": api_key,
            }

            details_response = requests.get(details_url, params=details_params)
            details_response.raise_for_status()
            details_data = details_response.json()

            if details_data.get("items"):
                video_details = details_data["items"][0]
                duration = video_details["contentDetails"]["duration"]
                view_count = video_details["statistics"].get("viewCount", "0")

                # Parse ISO 8601 duration (PT4M13S -> 4:13)
                import re

                duration_match = re.match(
                    r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration
                )
                if duration_match:
                    hours = int(duration_match.group(1) or 0)
                    minutes = int(duration_match.group(2) or 0)
                    seconds = int(duration_match.group(3) or 0)
                    total_seconds = hours * 3600 + minutes * 60 + seconds
                    formatted_duration = format_duration(total_seconds)
                else:
                    formatted_duration = "Unknown"

                results.append(
                    {
                        "title": snippet["title"],
                        "channel": snippet["channelTitle"],
                        "duration": formatted_duration,
                        "views": f"{int(view_count):,}",
                        "url": f"https://youtu.be/{video_id}",
                        "video_id": video_id,
                    }
                )

        return results

    except Exception as e:
        logger.error(f"YouTube API search error: {e}")
        return []


@command("song")
async def song_command(message: Message):
    """Quick song search and selection command"""
    logger.info(
        lang.log_command_executed.format(command="song", user_id=message.from_user.id)
    )

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "❌ Please provide a song name: /song SongName", parse_mode="HTML"
        )
        return

    query = args[1].strip()

    try:
        await message.answer(f"🔍 Searching for: <b>{query}</b>", parse_mode="HTML")

        # Use YouTube API for search
        if not hasattr(config, "YT_API_KEY") or not config.YT_API_KEY:
            await message.answer(
                "❌ YouTube API key not configured. Please set YT_API_KEY in config.py"
            )
            return

        search_results = search_youtube(query, config.YT_API_KEY)

        if not search_results:
            await message.answer("❌ No results found for your search query.")
            return

        response = "🎵 <b>Song Search Results</b>\n\n"
        response += f"Query: <code>{query}</code>\n\n"

        for i, result in enumerate(search_results, 1):
            response += f"{i}. <b>{result['title']}</b>\n"
            response += f"   👤 {result['channel']}\n"
            response += f"   ⏱️ {result['duration']} | 👁️ {result['views']} views\n\n"

        response += "<i>Reply with 1-5 to download the song</i>"

        # Store search results for reply handling
        import time

        search_data = {
            "user_id": message.from_user.id,
            "results": search_results,
            "timestamp": time.time(),
            "command": "song",
        }

        # Store in cache
        if not hasattr(song_command, "cache"):
            song_command.cache = {}
        song_command.cache[message.from_user.id] = search_data

        await message.answer(response, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Song search error: {e}")
        await message.answer("❌ Failed to search for songs. Please try again.")


@command("yt_music")
async def yt_music_command(message: Message):
    logger.info(
        lang.log_command_executed.format(
            command="yt_music", user_id=message.from_user.id
        )
    )

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "🎵 <b>YouTube Music Search & Download</b>\n\n"
            "Usage:\n"
            "/yt_music search query - Search for music\n"
            "/yt_music YouTube URL - Download audio\n"
            "/song SongName - Quick search and select\n\n"
            "Examples:\n"
            "/yt_music billie eilish bad guy\n"
            "/yt_music https://youtu.be/dQw4w9WgXcQ\n"
            "/song despacito",
            parse_mode="HTML",
        )
        return

    query = args[1].strip()

    # Check if it's a YouTube URL
    video_id = extract_youtube_id(query)
    if video_id:
        # Handle direct download
        progress_msg = await message.answer(
            "🎵 Downloading audio from YouTube...\n⏳ Progress: 0%", parse_mode="HTML"
        )

        try:
            # yt-dlp options for audio extraction
            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "outtmpl": os.path.join(tempfile.gettempdir(), "%(title)s.%(ext)s"),
                "quiet": True,
                "no_warnings": True,
                "progress_hooks": [lambda d: progress_hook(d, progress_msg, message)],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(f"https://youtu.be/{video_id}", download=False)

                # Check file size (Telegram limit: 50MB for bots, 2GB for regular users, 4GB for premium)
                filesize = info.get("filesize", 0)
                if filesize > 50 * 1024 * 1024:  # 50MB for bots
                    await message.answer(
                        "❌ Audio file is too large (>50MB). Telegram bot limit exceeded."
                    )
                    return

                # Download the audio
                ydl.download([f"https://youtu.be/{video_id}"])

                # Find the downloaded file
                expected_filename = (
                    ydl.prepare_filename(info)
                    .replace(".webm", ".mp3")
                    .replace(".m4a", ".mp3")
                )
                if not os.path.exists(expected_filename):
                    # Try to find the actual file
                    temp_dir = tempfile.gettempdir()
                    for file in os.listdir(temp_dir):
                        if file.endswith(".mp3") and info["title"] in file:
                            expected_filename = os.path.join(temp_dir, file)
                            break

                if os.path.exists(expected_filename):
                    # Delete progress message
                    try:
                        await progress_msg.delete()
                    except:
                        pass

                    # Send the audio file
                    with open(expected_filename, "rb") as audio_file:
                        await message.answer_audio(
                            audio=audio_file,
                            title=info.get("title", "YouTube Audio"),
                            performer=info.get("uploader", "Unknown"),
                            duration=info.get("duration", 0),
                            caption=f"🎵 Downloaded from YouTube\n📹 {info.get('title', 'Unknown')}\n👤 {info.get('uploader', 'Unknown')}",
                        )

                    # Clean up
                    os.remove(expected_filename)
                    logger.info(
                        f"Downloaded and sent YouTube audio: {info.get('title', 'Unknown')}"
                    )
                else:
                    await message.answer("❌ Failed to find downloaded audio file.")

        except Exception as e:
            logger.error(f"YouTube download error: {e}")
            await message.answer(f"❌ Failed to download audio: {str(e)}")

        return

    # Handle search
    try:
        await message.answer(f"🔍 Searching for: <b>{query}</b>", parse_mode="HTML")

        # Use YouTube API for real search
        if not hasattr(config, "YT_API_KEY") or not config.YT_API_KEY:
            await message.answer(
                "❌ YouTube API key not configured. Please set YT_API_KEY in config.py"
            )
            return

        search_results = search_youtube(query, config.YT_API_KEY)

        if not search_results:
            await message.answer("❌ No results found for your search query.")
            return

        response = "🎵 <b>YouTube Music Search Results</b>\n\n"
        response += f"Query: <code>{query}</code>\n\n"

        for i, result in enumerate(search_results, 1):
            response += f"{i}. <b>{result['title']}</b>\n"
            response += f"   👤 {result['channel']}\n"
            response += f"   ⏱️ {result['duration']} | 👁️ {result['views']} views\n"
            response += f"   🔗 {result['url']}\n\n"

        response += "<i>Reply with 1-5 to download, or use /yt_music URL</i>"

        # Store search results for reply handling
        import time

        search_data = {
            "user_id": message.from_user.id,
            "results": search_results,
            "timestamp": time.time(),
            "command": "yt_music",
        }

        # Store in cache
        if not hasattr(yt_music_command, "cache"):
            yt_music_command.cache = {}
        yt_music_command.cache[message.from_user.id] = search_data

        await message.answer(response, parse_mode="HTML")

    except Exception as e:
        logger.error(f"YouTube search error: {e}")
        await message.answer("❌ Failed to search YouTube. Please try again.")
