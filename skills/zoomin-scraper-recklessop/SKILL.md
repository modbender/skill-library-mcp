---
name: zoomin-scraper
description: Scrape documentation content from Zoomin Software portals using Playwright browser automation to handle dynamic content loading. Use when standard web fetching (requests/BeautifulSoup) returns generic content or fails to capture the main documentation body.
---

# Zoomin Scraper Skill

This skill provides a mechanism to robustly scrape content from documentation portals powered by Zoomin Software. It leverages Playwright to launch a headless Chromium browser, execute JavaScript, wait for dynamic content to load, and then extract the rendered text from the main article body.

## Usage

To use this skill, you need to provide a file containing a list of URLs, one URL per line. The skill will then process each URL, saving the extracted content to a specified output directory.

### Prerequisites (Manual Setup)

This skill relies on Playwright. Before using this skill for the first time on a new system, you *must* manually install Playwright and its browser binaries by running the following commands in your terminal:

```bash
pip install playwright
playwright install chromium
```
These commands should be executed within the virtual environment you intend to use for this skill.

### Running the Scraper

To run the scraper, you will invoke the `run_scraper.sh` script, which is located within this skill's `scripts/` directory. This wrapper script will activate your specified Python virtual environment before executing the main Python Playwright script.

**Parameters for `run_scraper.sh`:**

*   **`urls_file`**: The path to a text file containing the URLs to scrape, one URL per line.
*   **`output_directory`** (optional): The directory where the scraped content will be saved. If not provided, it defaults to `scraped_docs_output`.
*   **`venv_path`**: The absolute path to your Python virtual environment (e.g., `/home/justin/scraper/.env`).

**Example:**

Assuming your list of URLs is in `path/to/urls.txt`, you want to save the output to `my_scraped_docs/`, and your virtual environment is at `path/to/my_venv`:

```bash
zoomin-scraper urls_file="path/to/urls.txt" output_directory="my_scraped_docs" venv_path="path/to/my_venv"
```

The script will launch a headless Chromium browser, navigate to each URL, wait for the main content to load (specifically targeting `<article id="zDocsContent">`), and then save the extracted text. It includes a user agent to mimic a regular browser and a small delay between requests to be polite to the server.