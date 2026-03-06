---
name: selenium-automation
description: "Teaches the agent how to perform advanced web automation using Python, Selenium WebDriver, and ChromeDriver."
metadata:
  openclaw:
    emoji: "🌐"
    requires:
      - exec
      - write
    dependencies:
      system:
        - python3
        - chromedriver
        - google-chrome
      python:
        - selenium
    install: |
      pip install selenium
---

# Selenium Automation Skill

You are an expert at web automation using Python and Selenium WebDriver. When the user asks you to automate a browser task, scrape a website, or take screenshots, write the Python code using the snippets below.

## 0. Security and Execution Rules
* **Never run the script automatically.**
* After you write the Python script (for example `automation.py`), you must stop and ask the user for explicit permission to run it.
* Only use the `exec` tool after the user says "yes" or "approved".

## 1. Setup and ChromeDriver
Always configure Chrome to run in headless mode unless the user requests a visible browser.

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize the WebDriver
service = Service()
driver = webdriver.Chrome(service=service, options=chrome_options)
```

## 2. Navigation Commands
Use these commands to open web pages and navigate.

```python
driver.get("[https://example.com](https://example.com)")
driver.refresh()
driver.back()
driver.forward()

current_url = driver.current_url
page_title = driver.title
```

## 3. Taking Screenshots
You can take a screenshot of the entire visible window or a specific HTML element.

```python
driver.save_screenshot("full_page.png")

from selenium.webdriver.common.by import By
element = driver.find_element(By.ID, "main-content")
element.screenshot("element.png")
```

## 4. JavaScript Injections
Use `execute_script` to run custom JavaScript directly inside the browser.

```python
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
page_height = driver.execute_script("return document.body.scrollHeight;")

element = driver.find_element(By.ID, "hidden-button")
driver.execute_script("arguments[0].click();", element)

driver.execute_script("document.getElementById('cookie-banner').remove();")
```

## 5. Finding and Interacting with Elements
Use these standard commands to find elements, click buttons, and type text.

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".submit-btn")))
button.click()

search_box = driver.find_element(By.NAME, "q")
search_box.send_keys("OpenClaw documentation")
search_box.send_keys(Keys.RETURN)

header = driver.find_element(By.TAG_NAME, "h1")
print("Text:", header.text)
print("Class attribute:", header.get_attribute("class"))
```

## 6. Closing the Browser
Always close the browser at the end of the script to free up system memory.

```python
driver.quit()
```
