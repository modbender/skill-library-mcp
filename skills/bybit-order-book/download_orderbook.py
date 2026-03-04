#!/usr/bin/env python3
"""
ByBit Derivatives Historical Order Book Downloader (Selenium)

Downloads L2 order book snapshots (ob500) from:
  https://www.bybit.com/derivatives/en/history-data

Handles the 7-day download limit by chunking date ranges automatically.
Uses undetected-chromedriver to bypass Cloudflare protection.

Usage:
    python download_orderbook.py --symbol BTCUSDT --start 2024-01-01 --end 2024-01-31 --output ./data
"""

import argparse
import glob
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import (
        TimeoutException,
        ElementClickInterceptedException,
        StaleElementReferenceException,
        NoSuchElementException,
    )
except ImportError:
    print("ERROR: Missing dependencies. Install with:")
    print("  pip install undetected-chromedriver selenium --break-system-packages")
    sys.exit(1)

BYBIT_HISTORY_URL = "https://www.bybit.com/derivatives/en/history-data"
MAX_CHUNK_DAYS = 7
PAGE_LOAD_TIMEOUT = 30
ELEMENT_TIMEOUT = 15
DOWNLOAD_WAIT_TIMEOUT = 120  # seconds to wait for download to complete


def parse_args():
    parser = argparse.ArgumentParser(description="Download ByBit order book snapshots")
    parser.add_argument("--symbol", type=str, default="BTCUSDT", help="Trading pair (default: BTCUSDT)")
    parser.add_argument("--start", type=str, required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, required=True, help="End date YYYY-MM-DD")
    parser.add_argument("--output", type=str, default="./data/raw", help="Output directory for ZIPs")
    parser.add_argument("--headless", action="store_true", default=True, help="Run headless (default: True)")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Show browser window")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between actions (seconds)")
    return parser.parse_args()


def chunk_date_range(start_date: datetime, end_date: datetime, chunk_days: int = MAX_CHUNK_DAYS):
    """Split a date range into chunks of at most chunk_days."""
    chunks = []
    current = start_date
    while current <= end_date:
        chunk_end = min(current + timedelta(days=chunk_days - 1), end_date)
        chunks.append((current, chunk_end))
        current = chunk_end + timedelta(days=1)
    return chunks


def create_driver(download_dir: str, headless: bool = True):
    """Create an undetected Chrome driver with download directory configured."""
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    prefs = {
        "download.default_directory": str(Path(download_dir).resolve()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    # Enable downloads in headless mode
    if headless:
        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": str(Path(download_dir).resolve())},
        )

    return driver


def wait_and_click(driver, by, value, timeout=ELEMENT_TIMEOUT, description="element"):
    """Wait for element to be clickable, scroll into view, and click."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        element.click()
        return element
    except ElementClickInterceptedException:
        element = driver.find_element(by, value)
        driver.execute_script("arguments[0].click();", element)
        return element
    except TimeoutException:
        print(f"  WARNING: Timeout waiting for {description} ({value})")
        return None


def wait_for_element(driver, by, value, timeout=ELEMENT_TIMEOUT):
    """Wait for element to be present."""
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )


def select_dropdown_option(driver, dropdown_trigger_xpath, option_text, delay=1.0):
    """
    Click a dropdown trigger, then select an option by text.
    ByBit uses custom dropdowns (not native <select>), so we click the trigger
    to open the list, then find and click the matching option.
    """
    # Click dropdown trigger
    trigger = wait_and_click(driver, By.XPATH, dropdown_trigger_xpath, description=f"dropdown for '{option_text}'")
    if not trigger:
        return False
    time.sleep(delay)

    # Try multiple strategies to find the option
    strategies = [
        f"//div[contains(@class,'option') or contains(@class,'item') or contains(@class,'select')]//span[contains(text(),'{option_text}')]",
        f"//li[contains(text(),'{option_text}')]",
        f"//div[contains(text(),'{option_text}')]",
        f"//*[contains(@class,'dropdown')]//*[contains(text(),'{option_text}')]",
        f"//*[text()='{option_text}']",
    ]

    for xpath in strategies:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            for el in elements:
                if el.is_displayed():
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(delay)
                    return True
        except (StaleElementReferenceException, NoSuchElementException):
            continue

    print(f"  WARNING: Could not find option '{option_text}' in dropdown")
    return False


def set_date_range(driver, start_date: datetime, end_date: datetime, delay=1.0):
    """
    Set the date range on the ByBit history page.
    The page uses a date picker component — we look for date input fields
    and interact with them.
    """
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    # Look for date input fields or date picker triggers
    date_input_selectors = [
        "//input[contains(@placeholder,'Start') or contains(@placeholder,'start')]",
        "//input[contains(@placeholder,'Date') or contains(@placeholder,'date')]",
        "//input[contains(@class,'date')]",
        "//div[contains(@class,'date-picker')]//input",
        "//div[contains(@class,'datepicker')]//input",
    ]

    date_inputs = []
    for selector in date_input_selectors:
        found = driver.find_elements(By.XPATH, selector)
        date_inputs.extend([el for el in found if el.is_displayed()])

    if len(date_inputs) >= 2:
        # Clear and set start date
        date_inputs[0].clear()
        date_inputs[0].send_keys(start_str)
        time.sleep(delay)
        # Clear and set end date
        date_inputs[1].clear()
        date_inputs[1].send_keys(end_str)
        time.sleep(delay)
        return True

    # Alternative: click on date range display and use calendar
    date_range_triggers = driver.find_elements(
        By.XPATH,
        "//div[contains(@class,'date') and contains(@class,'range')]"
        " | //div[contains(@class,'calendar')]//button"
        " | //span[contains(@class,'date')]",
    )
    if date_range_triggers:
        print(f"  Found date range trigger, attempting calendar interaction for {start_str} to {end_str}")
        # Click the trigger to open calendar
        driver.execute_script("arguments[0].click();", date_range_triggers[0])
        time.sleep(delay * 2)

    print(f"  Setting date range: {start_str} to {end_str}")
    return True


def select_symbol(driver, symbol: str, delay=1.0):
    """Select the trading pair / symbol on the page."""
    # Try clicking a symbol from the data products list
    symbol_xpaths = [
        f"//*[contains(@class,'product') or contains(@class,'symbol') or contains(@class,'pair')]//*[contains(text(),'{symbol}')]",
        f"//label[contains(text(),'{symbol}')]",
        f"//span[contains(text(),'{symbol}')]",
        f"//div[contains(text(),'{symbol}')]",
        f"//input[@value='{symbol}']/..",
    ]

    for xpath in symbol_xpaths:
        try:
            elements = driver.find_elements(By.XPATH, xpath)
            for el in elements:
                if el.is_displayed():
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(delay)
                    print(f"  Selected symbol: {symbol}")
                    return True
        except (StaleElementReferenceException, NoSuchElementException):
            continue

    # Try search input if available
    search_inputs = driver.find_elements(
        By.XPATH,
        "//input[contains(@placeholder,'Search') or contains(@placeholder,'search') or contains(@placeholder,'Symbol')]",
    )
    for inp in search_inputs:
        if inp.is_displayed():
            inp.clear()
            inp.send_keys(symbol)
            time.sleep(delay * 2)
            # Click first result
            results = driver.find_elements(By.XPATH, f"//*[contains(text(),'{symbol}')]")
            for r in results:
                if r.is_displayed() and r != inp:
                    driver.execute_script("arguments[0].click();", r)
                    time.sleep(delay)
                    print(f"  Selected symbol via search: {symbol}")
                    return True

    print(f"  WARNING: Could not select symbol {symbol}")
    return False


def click_download(driver, delay=1.0):
    """Click the download button on the page."""
    download_xpaths = [
        "//button[contains(text(),'Download') or contains(text(),'download')]",
        "//a[contains(text(),'Download') or contains(text(),'download')]",
        "//button[contains(@class,'download')]",
        "//div[contains(@class,'download')]//button",
        "//*[contains(@class,'download-btn')]",
    ]

    for xpath in download_xpaths:
        result = wait_and_click(driver, By.XPATH, xpath, timeout=5, description="download button")
        if result:
            print("  Clicked download button")
            time.sleep(delay)
            return True

    print("  WARNING: Could not find download button")
    return False


def wait_for_downloads(download_dir: str, timeout: int = DOWNLOAD_WAIT_TIMEOUT):
    """Wait for all .crdownload / .part files to finish."""
    start = time.time()
    while time.time() - start < timeout:
        downloading = glob.glob(os.path.join(download_dir, "*.crdownload")) + \
                      glob.glob(os.path.join(download_dir, "*.part")) + \
                      glob.glob(os.path.join(download_dir, "*.tmp"))
        if not downloading:
            return True
        time.sleep(2)
    return False


def download_chunk(driver, symbol: str, start_date: datetime, end_date: datetime, download_dir: str, delay: float):
    """Download a single 7-day chunk of order book data."""
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    print(f"\n--- Downloading {symbol} from {start_str} to {end_str} ---")

    # Navigate to the page
    driver.get(BYBIT_HISTORY_URL)
    time.sleep(delay * 3)  # Wait for JS to load

    # Step 1: Select "Contract" product line
    print("  Selecting Product Line: Contract")
    select_dropdown_option(
        driver,
        "//div[contains(@class,'product-line') or contains(@class,'productLine')]//div[contains(@class,'select') or contains(@class,'dropdown')]",
        "Contract",
        delay=delay,
    )
    time.sleep(delay)

    # Step 2: Select "Order Book Snapshots" data category
    print("  Selecting Data Category: Order Book Snapshots")
    select_dropdown_option(
        driver,
        "//div[contains(@class,'data-category') or contains(@class,'dataCategory') or contains(@class,'category')]//div[contains(@class,'select') or contains(@class,'dropdown')]",
        "Order Book",
        delay=delay,
    )
    time.sleep(delay)

    # Step 3: Select the symbol
    print(f"  Selecting symbol: {symbol}")
    select_symbol(driver, symbol, delay=delay)
    time.sleep(delay)

    # Step 4: Set date range
    print(f"  Setting date range: {start_str} to {end_str}")
    set_date_range(driver, start_date, end_date, delay=delay)
    time.sleep(delay)

    # Step 5: Click download
    print("  Initiating download...")
    click_download(driver, delay=delay)

    # Step 6: Wait for downloads to complete
    print("  Waiting for download to complete...")
    if wait_for_downloads(download_dir):
        print("  Download complete!")
    else:
        print("  WARNING: Download may not have completed (timeout)")


def main():
    args = parse_args()

    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d")
    symbol = args.symbol.upper()
    download_dir = os.path.abspath(args.output)

    os.makedirs(download_dir, exist_ok=True)

    print(f"ByBit Order Book Downloader")
    print(f"  Symbol:    {symbol}")
    print(f"  Range:     {args.start} to {args.end}")
    print(f"  Output:    {download_dir}")
    print(f"  Headless:  {args.headless}")

    # Chunk the date range into 7-day windows
    chunks = chunk_date_range(start_date, end_date)
    print(f"  Chunks:    {len(chunks)} download(s) required")

    driver = create_driver(download_dir, headless=args.headless)

    try:
        for i, (chunk_start, chunk_end) in enumerate(chunks, 1):
            print(f"\n[Chunk {i}/{len(chunks)}]")
            download_chunk(driver, symbol, chunk_start, chunk_end, download_dir, args.delay)
            time.sleep(args.delay * 2)  # Pause between chunks
    finally:
        driver.quit()

    # Report results
    zips = glob.glob(os.path.join(download_dir, "*.zip"))
    print(f"\n{'='*60}")
    print(f"Download complete! {len(zips)} ZIP file(s) in {download_dir}")
    for z in sorted(zips):
        size_mb = os.path.getsize(z) / (1024 * 1024)
        print(f"  {os.path.basename(z)} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
