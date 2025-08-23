import asyncio
from time import time
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, SESSION, TIME

# Choose mode: bot for public, session for userbot
if BOT_TOKEN:
    app = Client("autodelete-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    MODE = "bot"
elif SESSION:
    app = Client("autodelete-user", session_string=SESSION, api_id=API_ID, api_hash=API_HASH)
    MODE = "userbot"
else:
    raise Exception("No BOT_TOKEN or SESSION provided in environment!")

to_delete = []

@app.on_message(filters.group)
async def auto_delete(client, message):
    try:
        # In bot mode, skip admin messages (Telegram API restriction)
        if MODE == "bot" and message.from_user and message.from_user.is_bot:
            member = await app.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in ("administrator", "creator"):
                return
        # Schedule deletion
        delete_at = int(time()) + TIME
        to_delete.append({"chat_id": message.chat.id, "message_id": message.id, "delete_at": delete_at})
    except Exception as e:
        print("Error scheduling delete:", e)

async def delete_worker():
    while True:
        now = int(time())
        pending = [msg for msg in to_delete if msg["delete_at"] <= now]
        for msg in pending:
            try:
                await app.delete_messages(msg["chat_id"], msg["message_id"])
            except Exception as e:
                print(f"Failed to delete message {msg['message_id']} in chat {msg['chat_id']}: {e}")
            to_delete.remove(msg)
        await asyncio.sleep(2)

@app.on_message(filters.private & filters.command("start"))
async def start(client, message):
    if MODE == "bot":
        msg = (
            "👋 I'm an AutoDelete bot!\n\n"
            "➤ Add me to your group as admin (with 'delete messages' permission) and I'll auto-delete messages after a few seconds (default: 10).\n"
            "➤ Anyone can use this bot in their group!\n"
            "➤ You can set delete time by setting the TIME variable."
        )
    else:
        msg = (
            "👋 I'm running as a userbot.\n"
            "➤ I can delete all messages (including admin bots) if I'm admin in the group.\n"
            "➤ Userbot mode is for private/personal use only."
        )
    await message.reply(msg)

if __name__ == "__main__":
    async def main():
        await app.start()
        asyncio.create_task(delete_worker())
        print(f"AutoDelete running in {MODE} mode.")
        await app.idle()
    asyncio.run(main())
