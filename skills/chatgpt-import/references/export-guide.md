# How to Export Your ChatGPT Data

1. Go to [chat.openai.com](https://chat.openai.com) and log in
2. Click your profile icon → **Settings**
3. Go to **Data Controls**
4. Click **Export Data** → **Confirm Export**
5. Wait for an email from OpenAI (usually arrives within minutes, can take up to an hour)
6. Click the download link in the email
7. Download the `.zip` file and unzip it
8. Find `conversations.json` inside — this is what the import scripts need

## Notes

- The export contains **all** your conversations
- The download link expires after a short time — download promptly
- The `conversations.json` file can be large (100MB+) if you have many conversations
- Other files in the export (e.g. `user.json`, `message_feedback.json`) are not needed
