from discord_webhook import DiscordWebhook
from typing import List, Dict, Any, Optional

class Node8_Discord_Notification:
    """
    Node 8: Responsible for sending notifications to Discord.
    """
    def __init__(self, webhook_url: Optional[str]) -> None:
        """
        Args:
            webhook_url (Optional[str]): The Discord Webhook URL.
        """
        self.webhook_url = webhook_url
        
    def send_notification(self, title_list: List[Dict[str, Any]]) -> None:
        """
        Sends a formatted message to Discord with the list of new summaries.

        Args:
            title_list (List[Dict[str, Any]]): List of metadata items to notify about.
        """
        print("Node 8: Sending Discord notification...")
        if not self.webhook_url:
            print("Discord Webhook URL not set.")
            return
            
        if not title_list:
            print("No new items to notify.")
            return
            
        # Construct message
        content = ""
        for item in title_list:
            title = item.get('title', 'Untitled')
            url = item.get('url', '#')
            content += f"- [{title}]({url})\n"
            
        webhook = DiscordWebhook(url=self.webhook_url, content=content, username="X generate")
        try:
            response = webhook.execute()
            print(f"Notification sent. Status Code: {response.status_code}")
        except Exception as e:
            print(f"Error sending notification: {e}")
