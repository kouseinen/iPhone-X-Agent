import os
import datetime
from typing import Any, Optional
import src.utils as utils

class Node4_Folder_Management:
    """
    Node 4: Responsible for managing Google Drive folders (Year/Month/Day).
    """
    def __init__(self) -> None:
        """Initializes the Google Drive service."""
        self.service = utils.get_drive_service()
        self.root_folder_id = os.getenv("DRIVE_ROOT_FOLDER_ID") # Optional
        
    def _get_or_create_single_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Helper to get or create a single folder."""
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
        
        try:
            results = self.service.files().list(q=query, fields="files(id, name)").execute()
            files = results.get('files', [])
            
            if files:
                # print(f"Folder '{folder_name}' exists. ID: {files[0]['id']}")
                return files[0]['id']
            else:
                print(f"Folder '{folder_name}' does not exist. Creating...")
                file_metadata = {
                    'name': folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                if parent_id:
                    file_metadata['parents'] = [parent_id]
                    
                file = self.service.files().create(body=file_metadata, fields='id').execute()
                print(f"Created folder ID: {file.get('id')}")
                return file.get('id')
        except Exception as e:
            print(f"Error managing folder '{folder_name}': {e}")
            return None

    def get_or_create_folder(self, date_str: str) -> Optional[str]:
        """
        Creates a folder hierarchy: Year -> Month -> Day.

        Args:
            date_str (str): ISO format date string.

        Returns:
            Optional[str]: The ID of the deepest folder (Day), or None if error.
        """
        print("Node 4: Checking/Creating folder hierarchy (YYYY/MM/DD) in Drive...")
        if not self.service:
            print("Drive service not initialized.")
            return None
            
        try:
            # Parse ISO date string
            if isinstance(date_str, str):
                dt = datetime.datetime.fromisoformat(date_str)
            else:
                dt = date_str # Fallback if it's already a datetime object
            
            year_str = str(dt.year)
            month_str = f"{dt.month:02d}"
            day_str = f"{dt.day:02d}"
            
            # 1. Year Folder
            parent_id = self.root_folder_id
            year_folder_id = self._get_or_create_single_folder(year_str, parent_id)
            if not year_folder_id: return None
            
            # 2. Month Folder
            month_folder_id = self._get_or_create_single_folder(month_str, year_folder_id)
            if not month_folder_id: return None
            
            # 3. Day Folder
            day_folder_id = self._get_or_create_single_folder(day_str, month_folder_id)
            if not day_folder_id: return None
            
            return day_folder_id

        except Exception as e:
            print(f"Error in folder hierarchy creation: {e}")
            return None
