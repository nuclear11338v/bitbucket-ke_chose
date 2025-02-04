import os
import asyncio
import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import Message
from youtube_dl import YoutubeDL

# Replace these with your own values
API_ID = "8120903065:AAHteYq0QAIMqPypZq_Gt9B3qHw6J4rEF60"
API_HASH = "27152769"
BOT_TOKEN = "b98dff566803b43b3c3120eec537fc1d"

# Initialize the Pyrogram client
app = Client("vc_music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# YouTube-DL options
YDL_OPTIONS = {
    "format": "bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }
    ],
    "outtmpl": "downloads/%(title)s.%(ext)s",
}

# Global variables to manage voice chat
vc_chat_id = None
vc = None

# Command: /start
@app.on_message(filters.command("start"))
async def start(_, message: Message):
    await message.reply("🎵 Welcome to the VC Music Bot! Use /play <song_name> to play music in a voice chat.")

# Command: /play <song_name>
@app.on_message(filters.command("play"))
async def play_music(_, message: Message):
    global vc_chat_id, vc

    # Check if the user provided a song name
    if len(message.command) < 2:
        await message.reply("❌ Please provide a song name. Usage: /play <song_name>")
        return

    # Check if the bot is in a voice chat
    if vc_chat_id is None:
        await message.reply("❌ Please join a voice chat first and invite me!")
        return

    # Extract the song name
    song_name = " ".join(message.command[1:])
    await message.reply(f"🔍 Finding and playing: {song_name}...")

    # Download the song using YouTube-DL
    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
            if not info:
                await message.reply("❌ No results found for the given song name.")
                return

            # Get the first result
            song_url = info["entries"][0]["url"]
            song_title = info["entries"][0]["title"]

        # Stream the song in the voice chat
        await message.reply(f"🎶 Now playing: {song_title}")
        await vc.join()
        await vc.start_audio(song_url)

    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

# Command: /join
@app.on_message(filters.command("join"))
async def join_vc(_, message: Message):
    global vc_chat_id, vc

    # Check if the user is in a voice chat
    if message.chat.type != "supergroup":
        await message.reply("❌ Please use this command in a group with a voice chat.")
        return

    # Join the voice chat
    try:
        vc_chat_id = message.chat.id
        vc = await app.join_chat(vc_chat_id)
        await message.reply("✅ Joined the voice chat! Use /play <song_name> to play music.")
    except Exception as e:
        await message.reply(f"❌ Error joining the voice chat: {str(e)}")

# Command: /leave
@app.on_message(filters.command("leave"))
async def leave_vc(_, message: Message):
    global vc_chat_id, vc

    # Leave the voice chat
    if vc_chat_id is not None:
        await vc.leave()
        vc_chat_id = None
        vc = None
        await message.reply("✅ Left the voice chat.")
    else:
        await message.reply("❌ I'm not in any voice chat.")

# Command: /stop
@app.on_message(filters.command("stop"))
async def stop_music(_, message: Message):
    global vc

    # Stop the music
    if vc is not None:
        await vc.stop_audio()
        await message.reply("⏹️ Stopped the music.")
    else:
        await message.reply("❌ No music is currently playing.")

# Run the bot
print("🎵 VC Music Bot is running...")
app.run()