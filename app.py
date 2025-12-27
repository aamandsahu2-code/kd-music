import os
import asyncio
import logging
from pyrogram import Client, filters
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL

# Logging
logging.basicConfig(level=logging.INFO)
print("🔥 VC Music Bot Starting...")

# Env vars direct
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")
VC_SESSION = os.getenv("VC_SESSION")

print(f"✅ Env loaded: API_ID={API_ID}")

app = Client("music_bot", API_ID, API_HASH, session_string=SESSION)
vc_client = Client("vc_session", API_ID, API_HASH, session_string=VC_SESSION)

PyTgCalls(vc_client)

@app.on_message(filters.command("start", prefixes="."))
async def start(client, message):
    await message.reply("**🎵 VC Music Bot Ready!**\n`.join` → `.play kesariya`")

@app.on_message(filters.command("join", prefixes="."))
async def join_vc(client, message):
    try:
        await vc_client.join_group_call(message.chat.id)
        await message.reply("**✅ Joined VC!** `.play song_name`")
        print(f"✅ Joined VC: {message.chat.id}")
    except Exception as e:
        await message.reply(f"**❌ Join error**: {str(e)}")

@app.on_message(filters.command("play", prefixes="."))
async def play_song(client, message):
    if len(message.command) < 2:
        return await message.reply("**Usage**: `.play kesariya`")
    
    query = " ".join(message.command[1:])
    await message.reply(f"**🔍 `{query}` loading...")
    
    try:
        url = f"ytsearch1:{query}"
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info['entries'][0]['title'][:70]
        
        stream = AudioPiped(url)
        await PyTgCalls.vc_client.change_stream(message.chat.id, stream)
        await message.reply(f"**▶️ Playing**: **{title}**")
        print(f"✅ Playing: {title}")
        
    except Exception as e:
        await message.reply(f"**❌ Error**: {str(e)}")

async def main():
    print("🚀 Starting clients...")
    await app.start()
    await vc_client.start()
    print("✅ BOTH Clients Started!")
    print("🎵 Bot FULLY LIVE!")
    idle()

if __name__ == "__main__":
    asyncio.run(main())
