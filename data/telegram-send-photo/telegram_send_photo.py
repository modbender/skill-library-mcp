#!/usr/bin/env python3
"""
Telegram Send Photo Skill
Send images via Telegram Bot API
"""

import requests
import os

def send_photo(photo_path, caption="", bot_token=None, chat_id=None):
    """
    Send a photo via Telegram Bot API
    
    Args:
        photo_path: Path to the image file
        caption: Optional caption text
        bot_token: Telegram Bot Token (default from config)
        chat_id: Target Chat ID (default from config)
    
    Returns:
        Response JSON from Telegram API
    """
    # Default configuration
    if bot_token is None:
        bot_token = "8610746914:AAHvbRYhGar_DD81-70IeWSSfkDLyvrWKY0"
    if chat_id is None:
        chat_id = "8422738233"
    
    # Validate file exists
    if not os.path.exists(photo_path):
        raise FileNotFoundError(f"Photo not found: {photo_path}")
    
    # Send photo
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    
    with open(photo_path, "rb") as photo_file:
        files = {"photo": photo_file}
        data = {"chat_id": chat_id, "caption": caption}
        
        resp = requests.post(url, files=files, data=data)
    
    if resp.status_code == 200:
        print("✅ Photo sent successfully!")
        return resp.json()
    else:
        print(f"❌ Failed to send photo: {resp.text}")
        return None


def send_latest_screenshot(caption=""):
    """
    Send the latest screenshot from the photo folder
    
    Args:
        caption: Optional caption text
    """
    photo_dir = r"D:\mimoTool\photo"
    
    # Find the latest screenshot
    files = [f for f in os.listdir(photo_dir) if f.endswith('.png')]
    if not files:
        print("No screenshots found!")
        return None
    
    # Sort by filename (timestamp) and get latest
    latest = sorted(files)[-1]
    photo_path = os.path.join(photo_dir, latest)
    
    print(f"📸 Sending: {latest}")
    return send_photo(photo_path, caption)


if __name__ == "__main__":
    # Test: Send the latest screenshot
    send_latest_screenshot(caption="测试截图喵~🐾")
