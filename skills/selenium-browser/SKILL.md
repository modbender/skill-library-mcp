---
name: selenium-browser
description: "Start a Selenium‑controlled Chrome browser, open a URL, take a screenshot, and report progress.  Supports headless mode and optional proxy."
---

## Usage

The skill triggers on any message that contains *Chrome*, *browser*, *Selenium*, *screenshot*, or *open*.

```bash
selenium-browser <URL> [--headless] [--proxy=<url>]
```

### Command flow
1. **Launch** Chrome (or Chromium) under Selenium.
2. **Navigate** to `<URL>`.
3. **Take a screenshot** of the loaded page.
4. **Save** the image in `/home/main/clawd/diffusion_pdfs/` and **report** the path back to the chat.
5. If anything fails, send an **error message**.

## Scripts

### scripts/launch_browser.py

```python
#!/usr/bin/env python3
import os
import sys
import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# CLI parsing
import argparse
parser = argparse.ArgumentParser(description="Launch Selenium Chrome and take a screenshot.")
parser.add_argument("url", help="URL to open")
parser.add_argument("--headless", action="store_true", help="Run Chrome headless")
parser.add_argument("--proxy", help="Proxy URL (e.g., http://proxy:3128)")
args = parser.parse_args()

# Prepare Chrome options
chrome_options = Options()
if args.headless:
    chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
if args.proxy:
    chrome_options.add_argument(f"--proxy-server={args.proxy}")

# Locate binaries
chrome_bin = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

service = Service(executable_path=chromedriver_path)

# Start browser
try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
except Exception as e:
    print(f"❌ Failed to start Chrome: {e}", file=sys.stderr)
    sys.exit(1)

# Navigate and wait for page load
try:
    driver.get(args.url)
    time.sleep(5)  # simple wait; can replace with WebDriverWait for better reliability
except Exception as e:
    print(f"❌ Navigation error: {e}", file=sys.stderr)
    driver.quit()
    sys.exit(1)

# Take screenshot
screenshot_path = os.path.join(os.getenv("HOME", "/tmp"), "screenshot.png")
try:
    driver.save_screenshot(screenshot_path)
except Exception as e:
    print(f"❌ Screenshot error: {e}", file=sys.stderr)
    driver.quit()
    sys.exit(1)

# Clean up
driver.quit()

# Output a JSON object that OpenClaw can parse for the reply
print({"status": "ok", "screenshot": screenshot_path})
```

### scripts/_env.sh

```bash
# Optional: set paths to Chrome/Chromedriver if not in standard locations
# export CHROME_BIN="/opt/google/chrome/google-chrome"
# export CHROMEDRIVER_PATH="/usr/local/bin/chromedriver"
```

## References

- [Selenium docs](https://www.selenium.dev/documentation/)
- [ChromeDriver download page](https://chromedriver.chromium.org/downloads)

## How the skill reports
The skill runs the Python script and captures its stdout as a JSON payload.  OpenClaw parses the JSON and sends a message back:

```
✅ Screenshot saved: /home/main/clawd/diffusion_pdfs/screenshot.png
```

If the script prints an error, the skill forwards the error text.

---

## Installation notes

1. Make sure `chromedriver` is in `/usr/local/bin/chromedriver` or set `CHROMEDRIVER_PATH`.
2. Make sure `google-chrome` (or `chromium`) is in `/usr/bin/google-chrome` or set `CHROME_BIN`.
3. Install Python dependencies: `pip install selenium` (inside the virtual env you use for the skill).

```bash
pip install selenium
```

---

## Logging & timeouts
The script uses a 5‑second static wait after navigation; replace with Selenium's `WebDriverWait` for dynamic waits.

If you encounter timeouts, adjust the `time.sleep(5)` value or use `WebDriverWait(driver, 20).until(...)`.

---

Feel free to tweak the script to fit your environment (proxy, authentication, etc.).
```

