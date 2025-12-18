from typing import Dict, Any
import src.utils as utils

class Node7_Metadata_Extraction:
    """
    Node 7: Responsible for extracting metadata (title, URL) from the processed file.
    """
    def extract(self, file_metadata: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        Extracts the title from the first line of the content.

        Args:
            file_metadata (Dict[str, Any]): Metadata of the file in Drive.
            content (str): The content of the file.

        Returns:
            Dict[str, Any]: A dictionary containing 'title', 'url', and 'timestamp'.
        """
        print("Node 7: Extracting metadata...")
        
        title = "Untitled"
        if content:
            lines = content.strip().split('\n')
            if lines:
                # Remove markdown headers (#)
                title = lines[0].replace('#', '').strip()
                
        metadata = {
            "title": title,
            "url": file_metadata.get('webViewLink'),
            "timestamp": utils.get_current_timestamp()
        }
        
        return metadata
