# X Bookmark Summarizer - Build & Deployment Manual

This document provides a structured set of build steps for deploying this project (X Bookmark Summarizer) to AWS Lambda.

## Prerequisites

- **Docker** is installed and running.  
- You can operate a terminal (Mac/Linux).  
- You are in the project root directory.

---

## 1. How the build works (Overview)

With AWS Lambda (Python runtime), you need to upload a ZIP file that includes both your source code and any external libraries listed in `requirements.txt`.

However, some libraries (such as `google-genai` and `discord.py`) may include OS-dependent binaries. If you simply run `pip install` on macOS and upload the result, it may not work on Lambda (Linux).

To avoid that, this project uses Docker to install dependencies inside an Amazon Linux–compatible environment and then packages everything into a deployable ZIP.

---

## 2. Build steps (Commands)

Copy and paste the following command block into your terminal to automatically generate the latest ZIP file.  
It’s recommended to change the version number (the suffix of the filename) each time you run it.

~~~bash
# === Config: output filename (change as needed) ===
OUTPUT_ZIP="deploy_package.zip"

# 1. Remove existing temp folder
rm -rf /tmp/xbookmark_build

# 2. Create a temp working directory and move into it
mkdir -p /tmp/xbookmark_build
cd /tmp/xbookmark_build

# 3. Copy source code and requirements file
# Note: you may need to adjust the path for your environment
PROJECT_ROOT="/Users/takakuwasouichirou/Library/Mobile Documents/iCloud~md~obsidian/Documents/X Bookmark"
cp -r "$PROJECT_ROOT/src" .
cp "$PROJECT_ROOT/requirements.txt" .

# 4. Install libraries inside a Docker container
# Use the same environment as AWS Lambda (Python 3.12)
docker run --rm --entrypoint /bin/bash \
  -v "$PWD":/var/task \
  public.ecr.aws/lambda/python:3.12 \
  -c "pip install -r requirements.txt -t /var/task --upgrade --no-cache-dir"

# 5. Remove unnecessary files/folders (shrink package size)
rm -rf *.dist-info *.egg-info __pycache__ boto3* botocore* bin
find . -name "__pycache__" -type d -exec rm -rf {} +

# 6. Create an init file so Python recognizes it as a package
touch src/__init__.py

# 7. Create the ZIP file
zip -r "$OUTPUT_ZIP" .

# 8. Move the completed ZIP to the project root
mv "$OUTPUT_ZIP" "$PROJECT_ROOT/"

# 9. Return to the original location and clean up temp files
cd "$PROJECT_ROOT"
rm -rf /tmp/xbookmark_build

# 10. Completion message
echo "Build Complete: $OUTPUT_ZIP"
ls -lh "$OUTPUT_ZIP"
~~~

---

## 3. Deployment steps (AWS Console)

Upload the ZIP file generated in the build step to AWS Lambda.

1. Log in to the **AWS Management Console** and open **Lambda**.  
2. Select the target function (e.g., `XBookmarkSummarizer`).  
3. Open the **Code** tab.  
4. Click **Upload from** on the right and select **.zip file**.  
5. Click **Upload**, then choose the ZIP you created (e.g., `deploy_package.zip`).  
6. Click **Save**.  
   - Uploading may take a few seconds to tens of seconds.  
   - If you get a network error (not something like “Environment variable size is too large”), reload the page and try again.

---

## 4. Troubleshooting

### Q1. I can’t upload and get an error like: “Failed to execute 'readAsArrayBuffer'...”
**Cause:** If you select a file in the browser and then overwrite/update that file locally, the browser’s file reference becomes invalid.

**Fix:** Reload the browser tab, then retry the upload process.

### Q2. After deployment, I get “ModuleNotFoundError”
**Cause:** The required libraries may not be included in the ZIP, or the folder structure may be wrong.

**Fix:**
- Check that the `src` folder and dependency folders (like `google/`) are at the ZIP root (top-level).  
- Confirm `requirements.txt` includes all required libraries.

### Q3. I get a “Permission denied” error
**Cause:** File permission issues.

**Fix:**
- When using Docker, generated files may be owned by root. Run `chmod -R 755 .` to fix permissions, or rebuild the package.