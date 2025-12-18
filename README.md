# iPhone X Agent

**iPhone X Agent** is an automated workflow that bridges your iPhone, Discord, and Google Drive using AI.
Simply copy the text of an X (Twitter) post on your iPhone, run the iOS Shortcut, and this agent will automatically generate a detailed explanation using **Gemini 2.5 Flash Lite**, save it to Google Drive, and notify you when it's done.

*(Formerly known as X Bookmark Summarizer)*

## Overview

Instead of manually taking notes on interesting X posts, this system allows you to:
1.  **Capture**: Use an iOS Shortcut to send the post text to a Discord channel.
2.  **Process**: The agent (running on AWS Lambda) picks up the text every 3 minutes.
3.  **Explain**: **Gemini 2.5 Flash Lite** analyzes the content and generates a professional explanation/summary.
4.  **Archive**: The explanation is saved as a Markdown file in Google Drive (organized by year).
5.  **Notify**: You get a notification back in Discord with the link to the file.

## demo
<!-- Failed to upload "x_generate_en.mp4" -->

---

## iPhone Shortcut Setup

To make this work, you need to set up a simple **iOS Shortcut** that sends your clipboard content to Discord.

### Steps to Create the Shortcut
1.  Open the **Shortcuts** app on your iPhone.
2.  Create a new shortcut (e.g., named "X Research").
3.  Add the following actions (refer to the screenshot below):

    *   **Get Clipboard**: To retrieve the text you copied from X.
    *   **Get Contents of URL**:
        *   **URL**: Paste your **Discord Webhook URL** (Input Channel).
        *   **Method**: `POST`
        *   **Headers**: Add `Content-Type`: `application/json`
        *   **Request Body**: `JSON`
        *   **Add new field**: Key=`content`, Value=`Clipboard` (Select the variable from the previous step).
    *   *(Optional)* **Open App**: Select "X" to switch back to the app smoothly.

### How to Use
1.  On the X app, **copy the text** of the post you are interested in.
2.  Tap your **"X Research" shortcut** (from Widget, Home Screen, or Share Sheet).
3.  The text is sent to Discord, triggering the Agent.
4.  Wait for the notification from "X generate" bot!

---

## Architecture

The system operates as a periodic Lambda function with the following pipeline:

1.  **Discord Input**: Receives text from the iOS Shortcut via Webhook.
2.  **Duplicate Check**: Prevents re-generating explanations for the same content.
3.  **Gemini AI**: Generates a summary/explanation based on the text.
4.  **Google Drive**: Saves the Markdown content (organized by year).
5.  **Notification**: Sends a completion link back to Discord.

---

## Prerequisites & Setup

### 1. Services
*   **Discord**: Channel & Webhook URL.
*   **Google Cloud**: Drive API, Gemini API, Service Account.
*   **AWS**: Lambda, EventBridge.

### 2. Environment Variables (AWS Lambda)
| Variable | Description |
| :--- | :--- |
| `DISCORD_TOKEN` | Discord Bot Token. |
| `DISCORD_CHANNEL_ID` | Channel ID to monitor. |
| `DISCORD_WEBHOOK_URL` | Webhook URL for **notifications** (Output). |
| `GEMINI_API_KEY` | Google Gemini API Key. |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Path to `credentials.json`. |

### 3. Build & Deploy
*   **Build**: See [docs/build_manual.md](docs/build_manual.md)
*   **Deploy**: See [aws_deployment_guide.md](aws_deployment_guide.md)

---

## License

[MIT](LICENSE)
