import os
import discord
import asyncio
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone

class Node1_Discord_Input:
    """
    Node 1: Responsible for fetching messages (text posts) from a specific Discord channel.
    Uses discord.py to retrieve message history.
    """
    def __init__(self) -> None:
        """Initializes the Discord client."""
        self.token = os.getenv("DISCORD_TOKEN")
        self.channel_id = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
        
        # Configure intents
        intents = discord.Intents.default()
        intents.message_content = True # Required to read message content
        self.client = discord.Client(intents=intents)

    async def fetch_recent_messages(self, limit: int = 20, hours: int = 0, minutes: int = 15) -> List[Dict[str, Any]]:
        """
        Fetches recent messages from the configured channel.
        
        Args:
            limit (int): Max messages to check.
            hours (int): Lookback period hours.
            minutes (int): Lookback period minutes.
            
        Returns:
            List[Dict[str, Any]]: A list of raw message data.
        """
        if not self.token or not self.channel_id:
            print("Node 1: Discord Token or Channel ID missing.")
            return []

        print(f"Node 1: Connecting to Discord to fetch recent messages (last {minutes} min)...")
        
        messages_data = []
        
        # Define the async function to run the client logic
        async def runner():
            try:
                await self.client.login(self.token)
                
                channel = await self.client.fetch_channel(self.channel_id)
                if not channel:
                    print(f"Node 1: Channel {self.channel_id} not found.")
                    return

                # Calculate cutoff time (UTC)
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours, minutes=minutes)
                
                print(f"Node 1: Fetching messages after {cutoff_time.isoformat()}")

                msg_count = 0
                async for message in channel.history(limit=limit, after=cutoff_time):
                    msg_count += 1
                    # Debug log with safety checks
                    try:
                        author_name = message.author.name if message.author else "Unknown"
                        msg_id = message.id
                        msg_created = message.created_at
                        print(f"DEBUG: Checking message {msg_id} from {author_name} at {msg_created}")
                    except Exception as e:
                        print(f"DEBUG: Error printing message info: {e}")

                    # Explicitly check timestamp again to prevent timezone/API issues
                    if message.created_at < cutoff_time:
                        print(f"DEBUG: Message skipped (Too old): {message.created_at} < {cutoff_time}")
                        continue

                    # Skip bot messages to avoid loops
                    if message.author.bot:
                        print(f"DEBUG: Message skipped (Bot): {message.author.name}")
                        # TEMPORARY FIX: For testing, if the bot is NOT the one running this script (check by name/ID if possible, but for now just log and maybe ALLOW if it's the specific user)
                        # The user "post" seems to be the one posting the INPUT content.
                        # "yt_research" is likely the output bot, so we should SKIP it to avoid loops.
                        
                        target_input_bots = ["post"] # Only allow "post" (the input source)
                        
                        if message.author.name in target_input_bots:
                             print(f"DEBUG: Exception - Processing '{message.author.name}' even if marked as bot/webhook.")
                             # FALL THROUGH - Do not continue
                        else:
                             continue

                    # Extract basic data
                    msg_data = {
                        "id": str(message.id),
                        "text": message.content,
                        "author": message.author.name,
                        "created_at": message.created_at.isoformat(),
                        "attachments": [a.url for a in message.attachments],
                        "embeds": []
                    }
                    
                    # Extract embed info if available (Discord expands links)
                    if message.embeds:
                        for embed in message.embeds:
                            embed_dict = {
                                "title": embed.title,
                                "description": embed.description,
                                "url": embed.url,
                                "image": embed.image.url if embed.image else None
                            }
                            msg_data["embeds"].append(embed_dict)
                    
                    messages_data.append(msg_data)
                    print(f"DEBUG: Message added. Content length: {len(message.content)}")
                
                print(f"DEBUG: Total messages scanned in history: {msg_count}")
                await self.client.close()
                
            except Exception as e:
                print(f"Node 1: Error fetching Discord messages: {e}")
                await self.client.close()

        # Run the async loop
        # Check if we are already in an event loop (unlikely for this script structure but good practice)
        try:
            loop = asyncio.get_running_loop()
            await runner() # If called from async context
        except RuntimeError:
             asyncio.run(runner()) # If called from sync context

        print(f"Node 1: Found {len(messages_data)} messages.")
        return messages_data

