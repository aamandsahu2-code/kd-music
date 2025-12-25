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

PyTgCalls(vc_client)

# ========== COMMANDS ==========
@app.on_message(filters.command("start", prefixes="."))
async def start(client, message):
    await message.reply(
        "**🎵 VC Music Bot Active!**\n\n"
        "**Commands:**\n"
        "`.join` - Join VC\n"
        "**`.play kesariya`** - Song name se play\n"
        "**`.play dQw4w9WgXcQ`** - ID se play\n"
        "`.pause` - Pause\n"
        "`.resume` - Resume\n"
        "`.leave` - Leave VC\n\n"
        "**Examples:**\n"
        "`.play shape of you`\n"
        "`.play rick roll`\n"
        "`.play anime op`"
    )

@app.on_message(filters.command("join", prefixes="."))
async def join_vc(client, message):
    chat_id = message.chat.id
    try:
        await vc_client.join_group_call(chat_id)
        await message.reply("**✅ Joined Voice Chat!**\n**`.play song_name` karo!** 🎵")
    except AlreadyJoinedError:
        await message.reply("**ℹ️ Already in VC!**")
    except Exception as e:
        await message.reply(f"**❌ Join failed**: `{str(e)[:50]}`")

@app.on_message(filters.command("play", prefixes="."))
async def play_song(client, message):
    if len(message.command) < 2:
        return await message.reply("**❌ Usage**: `.play kesariya` **or** `.play VIDEO_ID`")
    
    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    
    await message.reply(f"**🔍 `{query}` dhund raha hoon...**")
    
    try:
        # Check if it's YouTube ID (11 chars)
        if len(query) == 11 and query.startswith(('d', 'k', '7', 'L')):
            url = f"https://youtube.com/watch?v={query}"
            search_query = f"ytsearch1:{query}"
        else:
            # Song name search
            url = f"ytsearch1:{query}"
            search_query = url
        
        # Get song info
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if 'entries' in info and info['entries']:
                song = info['entries'][0]
                title = song.get('title', 'Unknown Song')[:70]
                uploader = song.get('uploader', 'Unknown')[:30]
                duration = song.get('duration', 0)
            else:
                title = info.get('title', 'Unknown Song')[:70]
                uploader = info.get('uploader', 'Unknown')[:30]
                duration = info.get('duration', 0)
        
        # Stream to VC
        stream = AudioPiped(url)
        await PyTgCalls.vc_client.change_stream(chat_id, stream)
        
        dur_str = f"{duration//60}:{duration%60:02d}" if duration else "LIVE"
        
        await message.reply(
            f"**▶️ Ab baj raha hai:**\n"
            f"**🎵 {title}**\n"
            f"👤 **{uploader}**\n"
            f"⏱️ **{dur_str}**\n\n"
            f"`{url}`"
        )
        
    except NoActiveGroupCall:
        await message.reply("**❌ Pehle `.join` karo VC mein!**")
    except Exception as e:
        await message.reply(f"**❌ Play nahi hua**: `{str(e)[:100]}`")

@app.on_message(filters.command("pause", prefixes="."))
async def pause(client, message):
    chat_id = message.chat.id
    try:
        await PyTgCalls.vc_client.pause_stream(chat_id)
        await message.reply("**⏸️ Pause ho gaya**")
    except:
        await message.reply("**❌ Kuch pause nahi hai**")

@app.on_message(filters.command("resume", prefixes="."))
async def resume(client, message):
    chat_id = message.chat.id
    try:
        await PyTgCalls.vc_client.resume_stream(chat_id)
        await message.reply("**▶️ Resume ho gaya**")
    except:
        await message.reply("**❌ Kuch resume nahi hai**")

@app.on_message(filters.command("leave", prefixes="."))
async def leave(client, message):
    chat_id = message.chat.id
    try:
        await PyTgCalls.vc_client.leave_group_call(chat_id)
        await message.reply("**👋 VC se nikal gaya**")
    except:
        await message.reply("**ℹ️ VC mein nahi hai**")

# Start bot
async def main():
    await app.start()
    await vc_client.start()
    logger.info("🚀 VC Music Bot Started Successfully!")
    idle()

if __name__ == "__main__":
    asyncio.run(main())
