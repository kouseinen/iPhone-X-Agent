"""
Main entry point for the X Bookmark Summarizer Agent.
This script orchestrates the flow of data between Discord (Input), Gemini, Google Drive, and Discord (Notification).
"""

import os
import asyncio
from dotenv import load_dotenv
from src.nodes import (
    Node1_Discord_Input, Node2_Preprocessing, Node3_Gemini, 
    Node4_Folder_Management, Node5_File_Creation, 
    Node6_Content_Writing, Node7_Metadata_Extraction, 
    Node8_Discord_Notification
)
import src.utils as utils

def main(event=None, context=None) -> None:
    """
    Main execution function.
    
    Args:
        event: Lambda event data
        context: Lambda context data
    
    1. Loads environment variables.
    2. Initializes all workflow nodes.
    3. Fetches messages from Discord containing X links.
    4. Processes each message through the pipeline:
       - Preprocessing
       - Summarization (Gemini with Grounding)
       - Folder Management (Drive)
       - File Creation (Drive)
       - Content Writing (Drive)
       - Metadata Extraction
    5. Sends a summary notification back to Discord.
    """
    # 1. Setup
    load_dotenv()
    print("Starting X Bookmark Summarizer Agent (Discord Input Mode)...")
    
    # Initialize Nodes
    node1 = Node1_Discord_Input()
    node2 = Node2_Preprocessing()
    node3 = Node3_Gemini()
    node4 = Node4_Folder_Management()
    node5 = Node5_File_Creation()
    node6 = Node6_Content_Writing()
    node7 = Node7_Metadata_Extraction()
    node8 = Node8_Discord_Notification(os.getenv("DISCORD_WEBHOOK_URL"))

    # 2. Execution Flow
    try:
        # Node 1: Fetch Discord Messages (Sync wrapper for async call)
        # Fetching last 15 minutes of messages to ensure we catch recent posts even with minor time drifts
        # The deduplication logic in Node 5 will prevent double processing.
        raw_posts = asyncio.run(node1.fetch_recent_messages(limit=50, minutes=15))
        
        title_list = []
        
        for post in raw_posts:
            print(f"Processing message ID: {post['id']}")
            
            # Node 4: Folder Management (Check early to avoid redundant processing)
            post_date = post['created_at'] 
            folder_id = node4.get_or_create_folder(post_date)
            
            if not folder_id:
                print("Skipping: Could not retrieve folder ID.")
                continue

            # Check if file already exists for this message ID (Idempotency)
            if node5.check_file_exists(folder_id, str(post['id'])):
                print(f"Skipping: File for message {post['id']} already exists.")
                continue
            
            # Node 2: Preprocess
            structured_data = node2.process(post)
            
            # Node 3: Gemini Summary
            content = node3.generate_summary(structured_data)
            
            if not content:
                print("Skipping: Gemini generated empty content.")
                continue

            # Generate File Name from Content (First Line)
            file_name = utils.format_file_name(content)
            
            if file_name.startswith("Untitled") and "Error" in content:
                 # If utils returned Untitled but content has error, use error name
                 file_name = "Error Generating Summary.md"
            
                # Node 5: File Creation
            file_meta = node5.create_file(folder_id, file_name, message_id=str(post['id']))
                
            if file_meta:
                # Node 6: Content Writing
                updated_file = node6.write_content(file_meta, content)
                
                if updated_file:
                    # Node 7: Metadata Extraction
                    meta = node7.extract(updated_file, content)
                    title_list.append(meta)
            
            # Optional: Sleep to avoid rate limits
            # time.sleep(2)
            
        # Node 8: Discord Notification
        # Notify immediately for items processed in this run
        if title_list:
            node8.send_notification(title_list)
        else:
            print("No new items processed in this run.")
            
    except Exception as e:
        print(f"An error occurred during execution: {e}")

    print("Execution finished.")

if __name__ == "__main__":
    main()
