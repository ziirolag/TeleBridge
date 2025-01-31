import asyncio
import requests
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel

# Replace with your actual Telegram App API credentials
api_id = 'your_api_id_here'
api_hash = 'your_api_hash_here'

# Supports multiple Telegram Channels, separated by comma
channel_ids = [-100000000000, -1000000000000]  # 5080ti and 5070ti channels

# Create a discord webhook for your server and insert URL
discord_webhook_url = 'your_discord_webhook_here'

# Initialize Telegram Client
client = TelegramClient('session_name', api_id, api_hash)

async def relay_last_three_messages(chat):
    """Fetch and relay the last 3 messages from a specific channel."""
    messages = []
    async for message in client.iter_messages(chat, limit=3):  # Fetch last 3 messages
        if message.text:
            messages.append(message)

    # Send the messages to Discord
    for message in reversed(messages):  # Preserve chronological order
        payload = {
            "content": f"**Message from Channel {chat.id}:**\n{message.text}"
        }
        response = requests.post(discord_webhook_url, json=payload)
        if response.status_code == 204:
            print(f"Message sent to Discord from Channel {chat.id}: {message.text}")
        else:
            print(f"Failed to send message: {response.text}")

async def main():
    # Connect to Telegram
    await client.start()

    # Fetch and relay the last 3 messages for each channel
    for target_chat_id in channel_ids:
        chat = await client.get_entity(PeerChannel(target_chat_id))
        await relay_last_three_messages(chat)

    # Relay live messages from both channels
    @client.on(events.NewMessage(chats=channel_ids))
    async def handler(event):
        if event.message.text:
            payload = {
                "content": f"**Message from Channel {event.chat_id}:**\n{event.message.text}"
            }
            response = requests.post(discord_webhook_url, json=payload)
            if response.status_code == 204:
                print(f"Live message sent to Discord from Channel {event.chat_id}: {event.message.text}")
            else:
                print(f"Failed to send message: {response.text}")

    # Keep the client running
    await client.run_until_disconnected()

# Run the script
asyncio.run(main())
