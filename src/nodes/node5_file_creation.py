import os
from typing import Dict, Any, Optional
import src.utils as utils

class Node5_File_Creation:
    """
    Node 5: Responsible for creating empty Markdown files in Google Drive.
    """
    def __init__(self) -> None:
        """Initializes the Google Drive service."""
        self.service = utils.get_drive_service()

    def check_file_exists(self, folder_id: str, message_id: str) -> bool:
        """
        Checks if a file for the given Discord message ID already exists in the folder.
        Uses appProperties to store and retrieve the message ID.
        """
        if not self.service:
            return False
            
        try:
            # Query for files in the folder with the specific message_id in appProperties
            query = f"'{folder_id}' in parents and appProperties has {{ key='discord_message_id' and value='{message_id}' }} and trashed = false"
            results = self.service.files().list(
                q=query,
                fields="files(id, name)",
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            if files:
                print(f"Node 5: File already exists for message {message_id} (ID: {files[0]['id']})")
                return True
            return False
        except Exception as e:
            print(f"Error checking for existing file: {e}")
            return False
        
    def create_file(self, folder_id: str, file_name: str, message_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Creates a new file in the specified folder.

        Args:
            folder_id (str): The ID of the parent folder.
            file_name (str): The name of the file to create.
            message_id (str, optional): The Discord message ID to store in appProperties.

        Returns:
            Optional[Dict[str, Any]]: Metadata of the created file, or None on error.
        """
        print(f"Node 5: Creating file {file_name} in folder {folder_id}...")
        if not self.service:
            return None
            
        file_metadata = {
            'name': file_name,
            'parents': [folder_id],
            'mimeType': 'text/markdown'
        }
        
        if message_id:
            file_metadata['appProperties'] = {
                'discord_message_id': str(message_id)
            }
        
        try:
            # Create an empty file first
            file = self.service.files().create(body=file_metadata, fields='id, webViewLink').execute()
            print(f"Created file ID: {file.get('id')}")
            return file
        except Exception as e:
            print(f"Error creating file: {e}")
            return None
