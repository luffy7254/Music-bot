import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls, idle
from pytgcalls.types.input_stream import InputStream, AudioVideoPiped
from pytgcalls.types.stream import StreamType

API_ID = 22532815  # your api_id from https://my.telegram.org/apps
API_HASH = "cdc905788c22458df1276e488c6d19b2"  # your api_hash from https://my.telegram.org/apps
SESSION = "AQE1hZwAKug_GOBdXMCf-4THWQxOY57RZehQRPgLzHw4bFG5e2rX_pK5epOe61MZ16rjxjxKH_a3eFEKsl4JK5db76Pcu2-uo2imgn-gbPARCkr7_7XkYmooaEg76QyVrf225-IRaDWk343cVIaCP-aYwIbCrYGgFgkBCa_-IO0ojtuUN5kDnhwA3wg0EygW8sTW6sLK-zSHX5VtrzSz4_uXulNc0OW1zS2eTgHd0K1Ke28prBeekrBcSjBsP3omZdNdvKV4zl6r2i2QEs9zdWfdpCjYBKgnacELqiRMMhkUnZjMdk_kDZtYjllWIKDQkkB0mVa9gi22c545-GlO1UVSMa4IoQAAAAHDHIcwAA"  # get from @StringSessionGenBot

app = Client(session_name=SESSION, api_id=API_ID, api_hash=API_HASH)
vc = PyTgCalls(app)

@app.on_message(filters.command("playvideo") & filters.group)
async def play_video(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Send a direct video URL or file path.\nUsage: /playvideo <url_or_path>")
    video_url = message.command[1]
    await message.reply("Joining VC and playing video...")
    await vc.join_group_call(
        message.chat.id,
        InputStream(AudioVideoPiped(video_url)),
        stream_type=StreamType().video_stream
    )
    await message.reply("▶️ Playing video in VC!")

@app.on_message(filters.command("stopvideo") & filters.group)
async def stop_video(client: Client, message: Message):
    await vc.leave_group_call(message.chat.id)
    await message.reply("🛑 Stopped video in VC.")

app.start()
vc.start()
print("Video Play Bot Running!")
idle()
