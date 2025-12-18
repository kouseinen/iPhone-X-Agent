# Design Document: X Bookmark Summarizer Agent

## 1. Overview
This agent automates the process of summarizing X (formerly Twitter) posts that a user shares in a specific Discord channel. It utilizes the Discord API to retrieve post links and content, Google Gemini for summarization, Google Drive for storage, and Discord for notifications.

## 2. Workflow Nodes

### Node 1: Discord (Input Source)
*   **Trigger**: User posts a URL of an X post in a specific Discord channel.
*   **Process**:
    *   Listen for new messages in the configured Discord channel (via Gateway or Bot API).
    *   Extract the X post URL from the message.
    *   Retrieve the message data using Discord API (relying on Discord's link preview/embeds for content if available, or just the URL).
*   **Output**: Raw Message Data (URL, Embed Content, Text).

### Node 2: Data Preprocessing (Python)
*   **Input Trigger**: Receipt of Raw Message Data from Node 1.
*   **Process**:
    *   Extract and clean the `URL` from the Discord message or embed.
    *   Identify and download/reference `images` if present in the embed.
    *   Extract external `URLs`.
    *   Format these inputs for the LLM.
*   **Output**: Structured Data (Cleaned Text, Image Objects/URLs, External Links).

### Node 3: Gemini (LLM API)
*   **Input Trigger**: Structured Data from Node 2 + System Prompt.
*   **Model**: **Gemini-2.5-flash**
*   **System Prompt**: Instructions to summarize the post, analyze the intent, and format the output in Markdown.
*   **Process**:
    *   Send the User Prompt (Text + Image + URL context) to Gemini-2.5-flash.
    *   Gemini generates a summary and insights.
*   **Output**: Generated Content (Markdown text).

### Node 4: Folder Management (Python)
*   **Input Trigger**: Completion of Node 3.
*   **Process**:
    *   Determine the current date/time (or the post's creation time).
    *   Format the folder name as `yyyy` or `mm` (e.g., `2024` or `12`).
    *   Check if this folder exists in the target Google Drive location.
    *   If it does not exist, create it.
*   **Output**: Target Folder ID.

### Node 5: Google Drive File Creation (Python)
*   **Start Trigger**: Completion of Node 4.
*   **Input**: Target Folder ID from Node 4.
*   **Process**:
    *   Authenticate with Google Drive API.
    *   Create a new Markdown file (`.md`) in the **Target Folder**.
    *   Naming convention: `{First Line of Content}.md` (Cleaned to be file-system safe).
*   **Output**: File Metadata (File ID, WebLink).

### Node 6: Content Writing (Python)
*   **Input Trigger**: File Metadata from Node 5 + Generated Content from Node 3.
*   **Process**:
    *   Upload/Write the Generated Content (Markdown) into the newly created file on Google Drive.
*   **Output**: Updated File (Markdown).

### Node 7: Metadata Extraction (Python)
*   **Input Trigger**: Updated File from Node 6.
*   **Process**:
    *   Read the first line of the Markdown content (assumed to be the Title/Header).
    *   Add this title and the file link to a tracking list (TitleList).
*   **Output**: TitleList (List of dictionaries: `{title, url, timestamp}`).

### Node 8: Discord Notification
*   **Start Trigger**: Completion of Node 7 (Runs every 3 minutes as part of the pipeline).
*   **Input**: TitleList (items processed in the current run).
*   **Process**:
    *   Format a message containing the titles and links to the Google Drive folder/files.
    *   Send the message to the `#x` channel via Discord Webhook.
*   **Output**: Discord Message sent.
