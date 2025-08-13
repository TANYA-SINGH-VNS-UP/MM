import os
import requests
import yt_dlp
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

# ==== CONFIG (ENV variables) ====
API_ID = int(os.getenv("API_ID", 12345))  # Telegram API ID
API_HASH = os.getenv("API_HASH", "your_api_hash")  # Telegram API Hash
BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")  # Telegram Bot Token
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "your_youtube_api_key")  # YouTube Data API Key

# ==== INIT APP ====
app = Client("music_vc_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
vc = PyTgCalls(app)

# ==== YouTube Search ====
def search_youtube(query):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q={query}&key={YOUTUBE_API_KEY}&maxResults=1"
    r = requests.get(url).json()
    if "items" in r and len(r["items"]) > 0:
        video_id = r["items"][0]["id"]["videoId"]
        title = r["items"][0]["snippet"]["title"]
        return f"https://www.youtube.com/watch?v={video_id}", title
    return None, None

# ==== Play Command ====
@app.on_message(filters.command("play") & filters.group)
async def play_music(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /play <song name>")
    
    query = " ".join(message.command[1:])
    yt_url, title = search_youtube(query)
    if not yt_url:
        return await message.reply("❌ No results found!")

    await message.reply(f"🎶 Playing: **{title}**\n🔗 {yt_url}")

    ydl_opts = {"format": "bestaudio"}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(yt_url, download=False)
        audio_url = info['url']

    chat_id = message.chat.id
    await vc.join_group_call(chat_id, AudioPiped(audio_url))

# ==== Leave Command ====
@app.on_message(filters.command("leave") & filters.group)
async def leave_vc(client, message):
    await vc.leave_group_call(message.chat.id)
    await message.reply("✅ Left VC.")

# ==== START BOT ====
vc.start()
print("🎵 Music VC Bot is running...")
app.run()
