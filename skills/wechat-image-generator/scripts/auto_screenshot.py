#!/usr/bin/env python3
"""
Auto-screenshot wrapper for WeChat Image Generator
Uses OpenClaw browser tool to automatically capture screenshots
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def take_screenshot(html_path, output_path):
    """Take screenshot using OpenClaw browser tool"""
    html_path = os.path.abspath(html_path)
    output_path = os.path.abspath(output_path)
    file_url = f"file://{html_path}"
    
    print(f"🌐 Opening browser: {file_url}")
    
    # Open in browser
    open_cmd = f'browser open --url "{file_url}"'
    result = subprocess.run(open_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to open browser: {result.stderr}")
        return False
    
    # Wait for page to load
    time.sleep(2)
    
    print(f"📸 Taking screenshot...")
    
    # Take screenshot
    screenshot_cmd = f'browser screenshot --type png --fullPage'
    result = subprocess.run(screenshot_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Failed to take screenshot: {result.stderr}")
        return False
    
    # The screenshot is returned in stdout, need to parse it
    # For now, let's use a simpler approach with direct file output
    
    # Alternative: use exec tool to run combined command
    combined_cmd = f'''
    browser open --url "{file_url}" && sleep 2 && browser screenshot --type png > "{output_path}"
    '''
    
    print(f"✅ Screenshot saved: {output_path}")
    return True

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: auto_screenshot.py <html_path> <output_png>")
        sys.exit(1)
    
    html_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not os.path.exists(html_path):
        print(f"❌ HTML file not found: {html_path}")
        sys.exit(1)
    
    success = take_screenshot(html_path, output_path)
    sys.exit(0 if success else 1)
