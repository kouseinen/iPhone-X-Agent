import re
from typing import Dict, Any
import src.utils as utils

class Node2_Preprocessing:
    """
    Node 2: Responsible for cleaning and structuring the raw tweet data.
    """
    def process(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cleans the raw tweet text and structures the data for the LLM.

        Args:
            raw_data (Dict[str, Any]): The raw tweet data from Node 1 (Discord message).

        Returns:
            Dict[str, Any]: Structured data containing cleaned text and metadata.
        """
        print("Node 2: Preprocessing data...")
        
        cleaned_text = raw_data.get("text", "")
        
        # Remove t.co links (simple regex approach)
        cleaned_text = re.sub(r'https://t\.co/\w+', '', cleaned_text).strip()
        
        # Extract images from attachments and embeds
        media_urls = []
        
        # 1. Direct attachments
        if "attachments" in raw_data:
            media_urls.extend(raw_data["attachments"])
            
        # 2. Embed images
        if "embeds" in raw_data:
            for embed in raw_data["embeds"]:
                if embed.get("image"):
                    media_urls.append(embed["image"])

        # Node 1 doesn't explicitly return external_urls list, 
        # but we can try to extract links from text or use what's in raw_data
        external_urls = []
        # If node1 provided external_urls key, use it, otherwise empty
        if "external_urls" in raw_data:
            external_urls = raw_data["external_urls"]
        
        structured_data = {
            "id": raw_data["id"],
            "text": cleaned_text,
            "media_urls": media_urls,
            "external_urls": external_urls,
            "created_at": raw_data["created_at"]
        }
        
        return structured_data
