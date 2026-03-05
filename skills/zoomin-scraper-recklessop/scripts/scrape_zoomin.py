import os
import hashlib
import time
import sys
from playwright.sync_api import sync_playwright

def scrape_zoomin_docs_playwright(urls_file_path, output_dir="zerto_hyperv_docs_playwright_scrape"):
    """
    Scrapes Zerto documentation URLs using Playwright to handle dynamic content.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    all_urls = []
    try:
        with open(urls_file_path, 'r', encoding='utf-8') as f:
            all_urls = [line.strip() for line in f if line.strip()]
        print(f"DEBUG: Successfully read {len(all_urls)} URLs from {urls_file_path}")
    except FileNotFoundError:
        print(f"ERROR: URLs file not found at {urls_file_path}")
        return

    results = {'success_files': [], 'failed_urls': {}}

    print(f"DEBUG: Attempting to scrape {len(all_urls)} URLs using Playwright into {output_dir}...")

    with sync_playwright() as p:
        # Launch a headless Chromium browser instance
        # Set headless=False if you want to see the browser opening (for debugging)
        browser = p.chromium.launch(headless=True) 
        
        # Create a new browser context with a custom user agent to mimic a regular browser
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for i, url in enumerate(all_urls):
            print(f"[{i+1}/{len(all_urls)}] Scraping: {url}")
            try:
                # Navigate to the URL and wait until the DOM is fully loaded
                page.goto(url, wait_until="domcontentloaded", timeout=30000) # 30 second timeout for navigation
                
                # Wait for the main content element to appear on the page
                # This is crucial for dynamically loaded content
                page.wait_for_selector('article#zDocsContent', timeout=15000) # Wait up to 15 seconds for the content div
                
                # Extract the text content from the identified main article
                # inner_text() gets the rendered text, including text from child elements
                extracted_text = page.locator('article#zDocsContent').inner_text()
                # Remove version dropdown and associated metadata if present
                import re
                # This pattern targets the "Version:" header and all content until the start
                # of the actual feature request submission instructions, using a lookahead.
                version_pattern = r"Version:.*?(?=From the Zerto User Interface)"
                extracted_text = re.sub(version_pattern, "", extracted_text, flags=re.DOTALL)
                # Also remove any leading whitespace/newlines that might remain from the substitution
                extracted_text = extracted_text.strip()


                
                # Basic check to ensure content is not empty or generic portal text
                if extracted_text.strip() and "Powered by Zoomin Software" not in extracted_text[:500]:
                    # Create a unique filename using a hash of the URL
                    filename_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
                    # Sanitize URL for filename, keeping only alphanumeric and replacing others with underscore
                    safe_filename_part = ''.join(c if c.isalnum() else '_' for c in url).replace('https___help_zerto_com_bundle_', '')
                    final_filename = f"{filename_hash}_{safe_filename_part[:50]}.txt" # Use hash + sanitized part, truncate for length
                    file_path = os.path.join(output_dir, final_filename)
                    print(f"DEBUG: Attempting to write to {file_path}")
                    try:
                        os.makedirs(output_dir, exist_ok=True) # Ensure directory exists
                        with open(file_path, 'w', encoding='utf-8') as outfile:
                            outfile.write(extracted_text)
                        print(f"DEBUG: Successfully wrote {len(extracted_text)} bytes to {file_path}")
                        
                        results['success_files'].append({
                            'original_url': url,
                            'file_path': file_path
                        })
                    except Exception as e:
                        results['failed_urls'][url] = f"File write error: {e}"
                        print(f"ERROR: File write error for {url}: {e}")
                else:
                    results['failed_urls'][url] = "Extracted text was empty, contained only whitespace, or looked like generic portal content."
                    print(f"DEBUG: Skipping write for {url}: {results['failed_urls'][url]}")
            except Exception as e:
                results['failed_urls'][url] = f"Scraping/parsing failed: {e}"
                print(f"ERROR: Scraping/parsing failed for {url}: {e}")
            
            time.sleep(1) # Be polite, add a small delay between requests to avoid overwhelming the server

        browser.close() # Close the browser when all URLs are processed

    print("\n--- Scraping Summary ---")
    print(f"Successfully scraped {len(results['success_files'])} URLs.")
    if results['failed_urls']:
        print(f"Failed to scrape {len(results['failed_urls'])} URLs:")
        for url, error in results['failed_urls'].items():
            print(f"- {url}: {error}")
    else:
        print("All URLs scraped successfully!")

    print("Scraping script finished.")

if __name__ == "__main__":
    # Default values for arguments (can be overridden by command line)
    default_urls_file = 'zerto_hyperv_urls.txt'
    default_output_dir = 'zerto_hyperv_docs_playwright_scrape'

    # Parse command line arguments. Expecting: python scrape_zoomin.py <urls_file_path> <output_dir>
    # sys.argv[0] is the script name itself
    urls_file = sys.argv[1] if len(sys.argv) > 1 else default_urls_file
    output_dir = sys.argv[2] if len(sys.argv) > 2 else default_output_dir

    scrape_zoomin_docs_playwright(urls_file, output_dir)
