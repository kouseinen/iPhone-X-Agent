from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from typing import Dict, Any, Optional
import src.utils as utils

class Node6_Content_Writing:
    """
    Node 6: Responsible for writing content to the created Google Drive files.
    """
    def __init__(self) -> None:
        """Initializes the Google Drive service."""
        self.service = utils.get_drive_service()
        
    def write_content(self, file_metadata: Dict[str, Any], content: str) -> Optional[Dict[str, Any]]:
        """
        Uploads the markdown content to the specified file.

        Args:
            file_metadata (Dict[str, Any]): Metadata of the target file (must contain 'id').
            content (str): The markdown content to write.

        Returns:
            Optional[Dict[str, Any]]: Updated file metadata, or None on error.
        """
        if not file_metadata or not self.service:
            print("Invalid file metadata or service not ready.")
            return None
            
        file_id = file_metadata.get('id')
        print(f"Node 6: Writing content to file {file_id}...")
        
        try:
            # Convert content string to bytes
            # Try resumable=False to avoid potential quota issues with Service Accounts
            media = MediaIoBaseUpload(BytesIO(content.encode('utf-8')), mimetype='text/markdown', resumable=False)
            
            updated_file = self.service.files().update(
                fileId=file_id,
                media_body=media,
                fields='id, name, webViewLink, createdTime, modifiedTime'
            ).execute()
            
            print("Content written successfully.")
            return updated_file
        except Exception as e:
            print(f"Error writing content: {e}")
            return None
