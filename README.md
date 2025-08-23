# AutoDelete Bot

A Telegram bot/userbot to auto-delete messages after a few seconds.

## Modes

- **Bot mode (default, public):**  
  Anyone can add to their group. Deletes messages from users, non-admin bots, and itself.
- **Userbot mode (SESSION):**  
  Deletes all messages (including admin bots) if you use your personal account session string (for private/personal use).

## Setup

**Add to your VPS:**

1. `pip install pyrogram tgcrypto`
2. Set environment variables:
    - `API_ID`, `API_HASH` (from [my.telegram.org](https://my.telegram.org))
    - `BOT_TOKEN` (from [@BotFather](https://t.me/BotFather)) for public bot mode
    - Or `SESSION` (Pyrogram session string) for userbot mode
    - `TIME` (optional, seconds before deletion, default: 10)
3. Run:
    ```
    python main.py
    ```

**Share your bot username so anyone can add it to their group!**

## Note

- **Bot mode:** cannot delete messages from admins/admin bots (Telegram API limitation).
- **Userbot mode:** can delete everything if your user is group admin.
