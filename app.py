import os
import logging
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

logging.basicConfig(level=logging.INFO)
print("🔥 SIMPLE MUSIC BOT Starting...")

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION")

app = Client("music_bot", API_ID, API_HASH, session_string=SESSION)

@app.on_message(filters.command("start", prefixes="."))
async def start(client, message):
    await message.reply("**🎵 Simple Music Bot Ready!**\n`.song kesariya`")

@app.on_message(filters.command("song", prefixes="."))
async def download_song(client, message):
    if len(message.command) < 2:
        return await message.reply("**Usage**: `.song kesariya`")
    
    query = " ".join(message.command[1:])
    await message.reply(f"**🔍 Downloading** `{query}`...")
    
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'music/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudioPP',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            song = info['entries'][0]
            
        await message.reply_audio(
            f"music/{song['title']}.mp3",
            caption=f"**🎵 {song['title'][:50]}**\n👤 {song['uploader']}"
        )
        print(f"✅ Song sent: {song['title']}")
        
    except Exception as e:
        await message.reply(f"**❌ Error**: `{str(e)[:100]}`")

async def main():
    print("🚀 Starting bot...")
    await app.start()
    print("✅ Bot Started! Use `.song kesariya`")
    print("🎵 LIVE!")
    
    # Keep alive
    import asyncio
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
