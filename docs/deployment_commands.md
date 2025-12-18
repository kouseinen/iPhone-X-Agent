# Deployment Commands Guide

Use this guide to package your application for AWS Lambda deployment.

## 1. Prepare Credentials
Ensure you have your Google Service Account key saved as `credentials.json` in the project root.
(If you have it as `service_account.json`, rename it or copy it).

```bash
cp service_account.json credentials.json
```

## 2. Create Zip File
Run the following command to create `source_code.zip`. This file will contain your source code, dependencies list, system prompt, and credentials.

```bash
zip -r source_code.zip src requirements.txt credentials.json .env
```
*Note: `src/system_prompt.md` is included within the `src` folder.*

## 3. Deployment
Upload the generated `source_code.zip` to your AWS Lambda function via the AWS Console or CLI as described in `aws_console_deployment_guide.md`.

