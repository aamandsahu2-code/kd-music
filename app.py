import os
import asyncio
import logging
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import AudioPiped
from pytgcalls.exceptions import NoActiveGroupCall, AlreadyJoinedError
from yt_dlp import YoutubeDL
from config import API_ID, API_HASH, SESSION, VC_SESSION

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Clients
app = Client("music_bot", API_ID, API_HASH, session_string=SESSION)
vc_client = Client("vc_session", API_ID, API_HASH, session_string=VC_SESSION)

# PyTgCalls setup
PyTgCalls(vc_client)

# ========== COMMANDS ==========
@app.on_message(filters.command("start", prefixes="."))
async def start(client, message):
    await message.reply(
        "**🎵 VC Music Bot Active!**\n\n"
        "**Commands:**\n"
        "`.join` - Join VC\n"
        "`.play VIDEO_ID` - Play song\n"
        "`.pause` - Pause\n"
        "`.resume` - Resume\n"
        "`.leave` - Leave VC\n\n"
        "**Example:** `.play dQw4w9WgXcQ`"
    )

@app.on_message(filters.command("join", prefixes="."))
async def join_vc(client, message):
    chat_id = message.chat.id
    try:
        await vc_client.join_group_call(chat_id)
        await message.reply("**✅ Joined Voice Chat!**\n**Now use `.play SONG_ID`** 🎵")
    except AlreadyJoinedError:
        await message.reply("**ℹ️ Already in VC!**")
    except Exception as e:
        await message.reply(f"**❌ Join failed**: `{str(e)[:50]}`")

@app.on_message(filters.command("play", prefixes="."))
async def play_song(client, message):
    if len(message.command) < 2:
        return await message.reply("**❌ Usage**: `.play dQw4w9WgXcQ`")
    
    song_id = message.command[1]
    chat_id = message.chat.id
    
    await message.reply("**🔍 Loading song...**")
    
    try:
        # Get song info
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://youtube.com/watch?v={song_id}", download=False)
            title = info.get('title', 'Unknown Song')[:70]
        
        # Stream to VC
        stream_url = f"https://youtube.com/watch?v={song_id}"
        stream = AudioPiped(stream_url)
        
        await PyTgCalls.vc_client.change_stream(chat_id, stream)
        await message.reply(
            f"**▶️ Now Playing**\n"
            f"**{title}**\n\n"
            f"`{stream_url}`"
        )
        
    except NoActiveGroupCall:
        await message.reply("**❌ First join VC with `.join`**")
    except Exception as e:
        await message.reply(f"**❌ Play failed**: `{str(e)[:100]}`")

@app.on_message(filters.command("pause", prefixes="."))
async def pause(client, message):
    chat_id = message.chat.id
    try:
        await PyTgCalls.vc_client.pause_stream(chat_id)
        await message.reply("**⏸️ Paused**")
    except Exception:
        await message.reply("**❌ Nothing to pause**")

@app.on_message(filters.command("resume", prefixes="."))
async def resume(client, message):
    chat_id = message.chat.id
    try:
        await PyTgCalls.vc_client.resume_stream(chat_id)
        await message.reply("**▶️ Resumed**")
    except Exception:
        await message.reply("**❌ Nothing to resume**")

@app.on_message(filters.command("leave", prefixes="."))
async def leave(client, message):
    chat_id = message.chat.id
    try:
        await PyTgCalls.vc_client.leave_group_call(chat_id)
        await message.reply("**👋 Left Voice Chat**")
    except Exception:
        await message.reply("**ℹ️ Not in VC**")

# Start bot
async def main():
    await app.start()
    await vc_client.start()
    logger.info("🚀 VC Music Bot Started Successfully!")
    idle()

if __name__ == "__main__":
    asyncio.run(main())
