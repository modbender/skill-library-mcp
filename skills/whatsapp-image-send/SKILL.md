---
name: whatsapp-image-send
description: Send images/files to WhatsApp. Use when user wants to send an image, photo, screenshot, video, audio or document via WhatsApp. Workflow: (1) Download to /tmp, (2) Copy to ~/.openclaw/workspace/, (3) Send via message tool with filePath, (4) Delete /tmp file. Required because WhatsApp plugin only allows workspace paths for media.
---

# WhatsApp Image Send

## Workflow

1. **Download**: Save file to `/tmp/<filename>`
   ```bash
   curl -o /tmp/<filename> <url>
   ```

2. **Copy to workspace**: WhatsApp requires workspace path
   ```bash
   cp /tmp/<filename> ~/.openclaw/workspace/
   ```

3. **Send to WhatsApp**
   ```bash
   message --channel whatsapp --target <phone> --filePath /home/seekey/.openclaw/workspace/<filename> --message "<caption>"
   ```

4. **Cleanup**: Delete temp file
   ```bash
   rm /tmp/<filename>
   ```

## Notes

- Phone format: +country + number (e.g., +14843124960)
- Supported: jpg, png, gif, video, audio, document
