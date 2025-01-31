import asyncio
import requests
from telethon import TelegramClient, events  # Corrected import
from telethon.tl.types import PeerChannel
from datetime import datetime, timedelta
import pytz
import time

api_id = '29086800'  # Replace with your actual API ID
api_hash = '77b53b0ef0789060d722ef1c126dd674'  # Replace with your actual API Hash
channel_ids = [-1002424349104, -1002433129143]  # Channel IDs for the 5080ti and 5070ti channels
discord_webhook_url = 'https://discord.com/api/webhooks/1334606910481109114/xlXcNUPvI_MShqMZmqUpNZQkqzm3p3ymooroy9k3mLzM9zLGmaaStSLg-ukzmsSTNQ87'

# Create the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

async def relay_messages_from_channel(chat, twenty_four_hours_ago):
    """Fetch and relay past messages from a specific channel."""
    print(f"Fetching messages from channel {chat.id}...")  # Debugging line
    messages = []
    async for message in client.iter_messages(chat, limit=100):
        print(f"Found message: {message.id} in Channel {chat.id}")  # Debugging line
        if message.date >= twenty_four_hours_ago:  # Filter by the 24-hour range
            messages.append(message)
        await asyncio.sleep(0.1)  # Small delay to avoid rate limit issues

    if not messages:
        print(f"No messages found in Channel {chat.id} in the past 24 hours.")  # Debugging line
    
    # Send the previous messages to Discord
    for message in messages:
        if message.text:  # Only relay text messages
            print(f"Relaying message from Channel {chat.id} to Discord: {message.text}")  # Debugging line
            payload = {
                "content": f"**Message from Channel {chat.id}:**\n{message.text}"
            }
            response = requests.post(discord_webhook_url, json=payload)
            if response.status_code == 204:
                print(f"Message sent to Discord from Channel {chat.id}: {message.text}")
            else:
                print(f"Failed to send message: {response.text}")
            await asyncio.sleep(1)  # Add a delay between sending messages to Discord to prevent rate limiting

async def main():
    # Connect to Telegram
    await client.start()

    # Define the time range for the past 24 hours, making it timezone-aware
    timezone = pytz.timezone("UTC")  # Replace with the correct timezone if necessary
    twenty_four_hours_ago = datetime.now(timezone) - timedelta(days=1)

    # Fetch and process past 24-hour messages for each channel
    for target_chat_id in channel_ids:
        chat = await client.get_entity(PeerChannel(target_chat_id))
        print(f"Processing Channel ID: {target_chat_id}")  # Debugging line
        await relay_messages_from_channel(chat, twenty_four_hours_ago)
        await asyncio.sleep(1)  # Add a slight delay between channel fetches

    # Relay live messages from both channels
    @client.on(events.NewMessage(chats=channel_ids))  # Listening to both channels
    async def handler(event):
        print(f"New message in Channel {event.chat_id}: {event.message.text}")  # Debugging line
        # Send incoming messages to Discord
        if event.message.text:
            payload = {
                "content": f"**Message from Channel {event.chat_id}:**\n{event.message.text}"
            }
            response = requests.post(discord_webhook_url, json=payload)
            if response.status_code == 204:
                print(f"Live message sent to Discord from Channel {event.chat_id}: {event.message.text}")
            else:
                print(f"Failed to send message: {response.text}")
            await asyncio.sleep(1)  # Add a delay between sending live messages to Discord

    # Keep the client running
    await client.run_until_disconnected()

# Run the script
asyncio.run(main())
