from core import Message, command, logger, get_lang
import re
import yt_dlp
import os
import tempfile

lang = get_lang()


def help():
    return {
        "name": "social_dl",
        "version": "0.0.1",
        "description": "Download content from social media platforms",
        "author": "Komihub",
        "usage": "/social_dl <URL> - Download from Facebook/Instagram/Twitter/X",
    }


def identify_platform(url: str) -> str:
    """Identify social media platform from URL"""
    url = url.lower()

    if "facebook.com" in url or "fb.watch" in url:
        return "facebook"
    elif "instagram.com" in url:
        return "instagram"
    elif "twitter.com" in url or "x.com" in url or "t.co" in url:
        return "twitter"
    elif "tiktok.com" in url:
        return "tiktok"
    else:
        return None


def extract_video_id(url: str, platform: str) -> str:
    """Extract video/post ID from URL"""
    try:
        if platform == "facebook":
            # Facebook URLs are complex, return the URL as identifier
            return url
        elif platform == "instagram":
            # Extract Instagram post ID
            match = re.search(r"/p/([a-zA-Z0-9_-]+)", url)
            return match.group(1) if match else None
        elif platform == "twitter":
            # Extract tweet ID
            match = re.search(r"/status/(\d+)", url)
            return match.group(1) if match else None
        elif platform == "tiktok":
            # Extract TikTok video ID
            match = re.search(r"/video/(\d+)", url)
            return match.group(1) if match else None
    except:
        pass
    return None


@command("social_dl")
async def social_dl_command(message: Message):
    logger.info(
        lang.log_command_executed.format(
            command="social_dl", user_id=message.from_user.id
        )
    )

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "📱 <b>Social Media Downloader</b>\n\n"
            "Supported platforms:\n"
            "• Facebook (Videos, Reels)\n"
            "• Instagram (Posts, Reels, Stories)\n"
            "• Twitter/X (Videos, GIFs)\n"
            "• TikTok (Videos)\n\n"
            "Usage: /social_dl <URL>\n\n"
            "Example:\n"
            "/social_dl https://www.instagram.com/p/ABC123/\n"
            "/social_dl https://twitter.com/user/status/1234567890",
            parse_mode="HTML",
        )
        return

    url = args[1].strip()

    # Validate URL
    if not url.startswith(("http://", "https://")):
        await message.answer(
            "❌ Please provide a valid URL starting with http:// or https://"
        )
        return

    # Identify platform
    platform = identify_platform(url)
    if not platform:
        await message.answer(
            "❌ Unsupported platform. Currently supported:\n"
            "• Facebook\n"
            "• Instagram\n"
            "• Twitter/X\n"
            "• TikTok"
        )
        return

    # Extract content ID
    content_id = extract_video_id(url, platform)

    # Start download process
    platform_names = {
        "facebook": "Facebook",
        "instagram": "Instagram",
        "twitter": "Twitter/X",
        "tiktok": "TikTok",
    }

    await message.answer(
        f"📥 <b>Download Request</b>\n\n"
        f"🌐 Platform: {platform_names[platform]}\n"
        f"🔗 URL: {url}\n"
        f"🆔 Content ID: <code>{content_id or 'N/A'}</code>\n\n"
        f"<i>Downloading content...</i>",
        parse_mode="HTML",
    )

    try:
        # yt-dlp options for social media download
        ydl_opts = {
            "format": "best[height<=720]",  # Limit quality to avoid large files
            "outtmpl": os.path.join(tempfile.gettempdir(), "%(title)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }

        # Add platform-specific options
        if platform == "instagram":
            ydl_opts.update(
                {"extractor_args": {"instagram": {"api_hostname": "i.instagram.com"}}}
            )

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first
            info = ydl.extract_info(url, download=False)

            # Check file size (Telegram limit: 2GB for regular users)
            if info.get("filesize", 0) > 2 * 1024 * 1024 * 1024:  # 2GB
                await message.answer(
                    "❌ File is too large (>2GB). Telegram limit exceeded."
                )
                return

            # Download the content
            ydl.download([url])

            # Find the downloaded file
            expected_filename = ydl.prepare_filename(info)
            if not os.path.exists(expected_filename):
                # Try to find the actual file
                temp_dir = tempfile.gettempdir()
                title = info.get("title", "").replace("/", "_").replace("\\", "_")
                for file in os.listdir(temp_dir):
                    if title in file and (
                        file.endswith(
                            (".mp4", ".webm", ".m4v", ".jpg", ".jpeg", ".png")
                        )
                    ):
                        expected_filename = os.path.join(temp_dir, file)
                        break

            if os.path.exists(expected_filename):
                file_size = os.path.getsize(expected_filename)
                file_size_mb = file_size / (1024 * 1024)

                # Send the file based on type
                if expected_filename.endswith((".jpg", ".jpeg", ".png")):
                    with open(expected_filename, "rb") as media_file:
                        await message.answer_photo(
                            photo=media_file,
                            caption=f"📱 Downloaded from {platform_names[platform]}\n📄 {info.get('title', 'Unknown')}\n📊 Size: {file_size_mb:.1f} MB",
                        )
                elif expected_filename.endswith((".mp4", ".webm", ".m4v")):
                    with open(expected_filename, "rb") as media_file:
                        await message.answer_video(
                            video=media_file,
                            caption=f"📱 Downloaded from {platform_names[platform]}\n🎬 {info.get('title', 'Unknown')}\n📊 Size: {file_size_mb:.1f} MB",
                            duration=info.get("duration", 0),
                        )
                else:
                    # Send as document for other formats
                    with open(expected_filename, "rb") as media_file:
                        await message.answer_document(
                            document=media_file,
                            caption=f"📱 Downloaded from {platform_names[platform]}\n📄 {info.get('title', 'Unknown')}\n📊 Size: {file_size_mb:.1f} MB",
                        )

                # Clean up
                os.remove(expected_filename)
                logger.info(
                    f"Downloaded and sent {platform} content: {info.get('title', 'Unknown')}"
                )
            else:
                await message.answer("❌ Failed to find downloaded file.")

    except Exception as e:
        logger.error(f"Social media download error: {e}")
        await message.answer(
            f"❌ Failed to download content: {str(e)}\n\n<i>Note: Some platforms may require login or have restrictions</i>",
            parse_mode="HTML",
        )
