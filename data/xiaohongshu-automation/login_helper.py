import json
import os
import time
from playwright.sync_api import sync_playwright

def login_helper():
    user_data_dir = os.path.expanduser("~/.openclaw/browser/xiaohongshu_auth_new")
    stealth_path = "/Users/lincolnwang/.openclaw/skills/xiaohongshu-skill/stealth.min.js"
    secret_path = os.path.expanduser("~/.openclaw/secrets/xiaohongshu.json")
    
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=[
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        if os.path.exists(stealth_path):
            browser.add_init_script(path=stealth_path)
            
        page = browser.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        
        print("Navigating to Creator Center (Pro)...")
        page.goto('https://pro.xiaohongshu.com/login')
        time.sleep(5)
        
        # Save HTML to debug selector
        with open("xhs_login_page.html", "w") as f:
            f.write(page.content())
            
        # Try to switch to QR code
        print("Attempting to switch to QR code...")
        try:
            # Try force click on the container of the qr icon
            # Based on HTML structure: <div class="css-jjnw1w"><img ...>
            elem = page.locator('.css-jjnw1w')
            if elem.count() > 0:
                print("Found .css-jjnw1w, clicking...")
                elem.click(force=True, timeout=3000)
            else:
                print(".css-jjnw1w not found")
                
            # Also try the img directly
            img = page.locator('img[src^="data:image/png;base64"]')
            if img.count() > 0:
                print("Found base64 img, clicking...")
                img.first.click(force=True, timeout=3000)
        except Exception as e:
            print(f"Click failed: {e}")

        time.sleep(2)
        page.screenshot(path="xiaohongshu_login_qr.png")
        print("Screenshot saved to xiaohongshu_login_qr.png")
        
        print("Waiting for login...")
        max_retries = 120 # 4 minutes
        for i in range(max_retries):
            url = page.url
            if "login" not in url and ("pro.xiaohongshu.com" in url):
                print("Login successful!")
                cookies = browser.cookies()
                simplified_cookies = {}
                for cookie in cookies:
                    if '.xiaohongshu.com' in cookie['domain']:
                        simplified_cookies[cookie['name']] = cookie['value']
                
                with open(secret_path, 'w') as f:
                    json.dump(simplified_cookies, f, indent=2)
                print(f"Cookies saved to {secret_path}")
                break
            
            if i % 5 == 0 and i > 0:
                 page.screenshot(path=f"xiaohongshu_login_qr_{i}.png")
                 print(f"Updated screenshot: xiaohongshu_login_qr_{i}.png")
            
            time.sleep(2)
        else:
            print("Timeout waiting for login.")
            
        browser.close()

if __name__ == "__main__":
    login_helper()
