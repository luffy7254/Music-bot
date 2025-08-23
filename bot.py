import asyncio
from time import time
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, TIME

app = Client("autodelete-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
to_delete = []

@app.on_message(filters.group)
async def auto_delete(client, message):
    try:
        # Only process messages the bot is allowed to delete
        if message.from_user and not message.from_user.is_self:
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
    await message.reply(
        "👋 I'm an AutoDelete bot!\n"
        "Add me to your group as admin (with 'delete messages' permission) and I'll auto-delete all new messages after a short time."
    )

if __name__ == "__main__":
    async def main():
        await app.start()
        asyncio.create_task(delete_worker())
        print("AutoDelete bot running.")
        await app.idle()
    asyncio.run(main())
