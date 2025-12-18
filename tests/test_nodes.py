import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime

# Add src to path to import nodes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from nodes.node1_x_api import Node1_X_API
from nodes.node2_preprocessing import Node2_Preprocessing
from nodes.node3_gemini import Node3_Gemini
from nodes.node4_folder_management import Node4_Folder_Management
from nodes.node5_file_creation import Node5_File_Creation
from nodes.node6_content_writing import Node6_Content_Writing
from nodes.node7_metadata_extraction import Node7_Metadata_Extraction
from nodes.node8_discord_notification import Node8_Discord_Notification

class TestXBookmarkAgent(unittest.TestCase):

    @patch('nodes.node1_x_api.tweepy.Client')
    def test_node1_fetch_bookmarks(self, mock_client):
        # Setup mock
        mock_response = MagicMock()
        mock_tweet = MagicMock()
        mock_tweet.id = "123"
        mock_tweet.text = "Test Tweet"
        mock_tweet.created_at = datetime.now()
        mock_tweet.attachments = {}
        mock_tweet.entities = {}
        
        mock_response.data = [mock_tweet]
        mock_response.includes = {}
        mock_client.return_value.get_bookmarks.return_value = mock_response
        
        # Test
        node = Node1_X_API()
        bookmarks = node.fetch_bookmarks("user_id")
        
        self.assertEqual(len(bookmarks), 1)
        self.assertEqual(bookmarks[0]['id'], "123")
        self.assertEqual(bookmarks[0]['text'], "Test Tweet")

    def test_node2_preprocessing(self):
        node = Node2_Preprocessing()
        raw_data = {
            "id": "123",
            "text": "Hello world https://t.co/xyz",
            "media_urls": [],
            "external_urls": [],
            "created_at": datetime.now()
        }
        
        processed = node.process(raw_data)
        self.assertEqual(processed['text'], "Hello world")

    @patch('nodes.node3_gemini.genai.GenerativeModel')
    @patch('nodes.node3_gemini.genai.configure')
    def test_node3_gemini(self, mock_configure, mock_model):
        mock_model_instance = mock_model.return_value
        mock_response = MagicMock()
        mock_response.text = "# Summary\nThis is a summary."
        mock_model_instance.generate_content.return_value = mock_response
        
        node = Node3_Gemini()
        structured_data = {
            "text": "Some text",
            "external_urls": [],
            "media_urls": []
        }
        
        summary = node.generate_summary(structured_data)
        self.assertIn("# Summary", summary)

    @patch('nodes.node4_folder_management.utils.get_drive_service')
    def test_node4_folder_management(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # Mock list returns empty (folder doesn't exist)
        mock_service.files().list().execute.return_value = {'files': []}
        # Mock create returns new folder
        mock_service.files().create().execute.return_value = {'id': 'new_folder_id'}
        
        node = Node4_Folder_Management()
        folder_id = node.get_or_create_folder(datetime.now())
        
        self.assertEqual(folder_id, 'new_folder_id')

    @patch('nodes.node5_file_creation.utils.get_drive_service')
    def test_node5_file_creation(self, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        mock_service.files().create().execute.return_value = {'id': 'new_file_id', 'webViewLink': 'http://link'}
        
        node = Node5_File_Creation()
        file_meta = node.create_file('folder_id', 'file_name')
        
        self.assertEqual(file_meta['id'], 'new_file_id')

    @patch('nodes.node6_content_writing.utils.get_drive_service')
    @patch('nodes.node6_content_writing.MediaIoBaseUpload')
    def test_node6_content_writing(self, mock_media_upload, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        mock_service.files().update().execute.return_value = {'id': 'file_id', 'name': 'updated_file'}
        
        node = Node6_Content_Writing()
        file_metadata = {'id': 'file_id'}
        updated_file = node.write_content(file_metadata, "Some content")
        
        self.assertEqual(updated_file['name'], 'updated_file')

    def test_node7_metadata_extraction(self):
        node = Node7_Metadata_Extraction()
        content = "# My Title\nSome content."
        file_metadata = {'webViewLink': 'http://drive.google.com/file'}
        
        metadata = node.extract(file_metadata, content)
        self.assertEqual(metadata['title'], "My Title")
        self.assertEqual(metadata['url'], 'http://drive.google.com/file')

    @patch('nodes.node8_discord_notification.DiscordWebhook')
    def test_node8_discord_notification(self, mock_webhook):
        mock_webhook_instance = mock_webhook.return_value
        mock_webhook_instance.execute.return_value.status_code = 200
        
        node = Node8_Discord_Notification("http://webhook.url")
        title_list = [{'title': 'Title 1', 'url': 'http://url1'}]
        
        node.send_notification(title_list)
        mock_webhook_instance.execute.assert_called_once()

if __name__ == '__main__':
    unittest.main()
