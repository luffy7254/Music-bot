import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import InputStream, AudioVideoPiped
from pytgcalls.types.stream import StreamType
import yt_dlp
import os

API_ID = 22532815      # Replace with your API ID
API_HASH = "cdc905788c22458df1276e488c6d19b2"    # Replace with your API HASH
SESSION = "AQE1hZwAKug_GOBdXMCf-4THWQxOY57RZehQRPgLzHw4bFG5e2rX_pK5epOe61MZ16rjxjxKH_a3eFEKsl4JK5db76Pcu2-uo2imgn-gbPARCkr7_7XkYmooaEg76QyVrf225-IRaDWk343cVIaCP-aYwIbCrYGgFgkBCa_-IO0ojtuUN5kDnhwA3wg0EygW8sTW6sLK-zSHX5VtrzSz4_uXulNc0OW1zS2eTgHd0K1Ke28prBeekrBcSjBsP3omZdNdvKV4zl6r2i2QEs9zdWfdpCjYBKgnacELqiRMMhkUnZjMdk_kDZtYjllWIKDQkkB0mVa9gi22c545-GlO1UVSMa4IoQAAAAHDHIcwAA"  # Replace with your session string

app = Client(SESSION, api_id=API_ID, api_hash=API_HASH)
vc = PyTgCalls(app)
queues = {}

def get_video_link(url):
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "quiet": True,
        "noplaylist": True,
        "extract_flat": False
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info["url"]

async def is_admin(client, chat_id, user_id):
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in ("administrator", "creator")

async def play_next(chat_id):
    q = queues.get(chat_id)
    if not q or len(q) == 0:
        await vc.leave_group_call(chat_id)
        return
    video = q.pop(0)
    await vc.join_group_call(
        chat_id,
        InputStream(AudioVideoPiped(video)),
        stream_type=StreamType().video_stream
    )
    # Clean up local file if not a URL
    if not video.startswith("http"):
        try:
            os.remove(video)
        except Exception:
            pass

# Command: /play <url>
@app.on_message(filters.command("play") & filters.group)
async def play_handler(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can use this command.")
    if len(message.command) < 2:
        return await message.reply("Send a video URL to play.\nUsage: `/play <url>`")
    url = message.command[1]
    m = await message.reply("🔄 Fetching video...")
    try:
        video_link = get_video_link(url)
    except Exception as e:
        return await m.edit(f"❌ Error: {e}")
    q = queues.setdefault(message.chat.id, [])
    q.append(video_link)
    if not vc.active_calls.get(message.chat.id):
        await m.edit("▶️ Playing video!")
        await play_next(message.chat.id)
    else:
        await m.edit("✅ Added to queue.")

# Detect direct video/document uploads by admin
@app.on_message((filters.video | filters.document) & filters.group)
async def video_file_handler(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return
    m = await message.reply("⬇️ Downloading your video...")
    file_path = await message.download()
    q = queues.setdefault(message.chat.id, [])
    q.append(file_path)
    if not vc.active_calls.get(message.chat.id):
        await m.edit("▶️ Playing your video!")
        await play_next(message.chat.id)
    else:
        await m.edit("✅ Added your video to queue.")

@app.on_message(filters.command("skip") & filters.group)
async def skip_handler(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can use this command.")
    await message.reply("⏭ Skipping current video...")
    await play_next(message.chat.id)

@app.on_message(filters.command("pause") & filters.group)
async def pause_handler(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can use this command.")
    await vc.pause_stream(message.chat.id)
    await message.reply("⏸ Paused.")

@app.on_message(filters.command("resume") & filters.group)
async def resume_handler(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can use this command.")
    await vc.resume_stream(message.chat.id)
    await message.reply("▶️ Resumed.")

@app.on_message(filters.command("end") & filters.group)
async def end_handler(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ Only admins can use this command.")
    queues[message.chat.id] = []
    await vc.leave_group_call(message.chat.id)
    await message.reply("🛑 Ended the stream.")

@vc.on_stream_end()
async def on_stream_end(client, update):
    chat_id = update.chat_id
    await play_next(chat_id)

app.start()
vc.start()
print("Bot running!")
idle()
