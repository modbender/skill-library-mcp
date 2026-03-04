#!/usr/bin/env python3
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Parse arguments
import argparse
parser = argparse.ArgumentParser(description="Launch Selenium Chrome.")
parser.add_argument("url", help="URL to open")
parser.add_argument("--headless", action="store_true", help="Run Chrome headless")
parser.add_argument("--proxy", help="Proxy URL (e.g., http://proxy:3128)")
args = parser.parse_args()

# Chrome options
chrome_options = Options()
if args.headless:
    chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Proxy support
if args.proxy:
    chrome_options.add_argument(f'--proxy-server={args.proxy}')

# Locate binaries
chrome_bin = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
chromedriver_path = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")

service = ChromeService(executable_path=chromedriver_path)

# Start browser
driver = webdriver.Chrome(
    service=service,
    options=chrome_options,
    executable_path=chrome_bin
)

# Open URL
driver.get(args.url)

# Keep the browser alive until the agent sends a terminate command
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    driver.quit()

