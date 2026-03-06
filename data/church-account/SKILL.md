---
name: church-account
description: Automate tasks on churchofjesuschrist.org and LCR (Leader & Clerk Resources). Use when logging into LDS church accounts, looking up ward/stake rosters, managing callings, viewing temple recommend status, accessing the member directory, or any other LCR/church website automation. Covers OAuth login flow, session management, and key church service URLs.
---

# Church Account (LDS/LCR)

Automate login and tasks on churchofjesuschrist.org.

## Login

### OAuth Flow
The church uses OAuth via `id.churchofjesuschrist.org`. Any protected page redirects to login:
1. Enter username → click Next
2. Enter password → click Verify
3. Redirects back to target page with session cookies

No MFA or CAPTCHA is typically required. Playwright + playwright-stealth handles it cleanly.

### Credentials
Store in a password vault or environment variables:
- Username (church account email or membership ID)
- Password

### Login with Playwright
```python
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def login(target_url="https://lcr.churchofjesuschrist.org", cookies_path="/tmp/church_cookies.json"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ..."
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        await page.goto(target_url)

        # Enter username
        await page.fill('input[name="identifier"]', USERNAME)
        await page.click('button[type="submit"]')

        # Enter password
        await page.wait_for_selector('input[type="password"]')
        await page.fill('input[type="password"]', PASSWORD)
        await page.click('button[type="submit"]')

        # Wait for redirect
        await page.wait_for_url(f"{target_url}/**", timeout=30000)

        # Save session
        await context.storage_state(path=cookies_path.replace('.json', '_state.json'))
        await browser.close()
```

### Reusing a Session
After login, use saved storage state to skip re-authentication:
```python
context = await browser.new_context(
    storage_state="/tmp/church_cookies_state.json",
    viewport={"width": 1920, "height": 1080},
    user_agent="Mozilla/5.0 ..."
)
page = await context.new_page()
await Stealth().apply_stealth_async(page)
```

## Key URLs
| Service | URL |
|---------|-----|
| LCR (Leader & Clerk Resources) | https://lcr.churchofjesuschrist.org |
| Ward Directory | https://directory.churchofjesuschrist.org |
| Calendar | https://www.churchofjesuschrist.org/calendar |
| Donations | https://donations.churchofjesuschrist.org |
| Temple Reservations | https://tos.churchofjesuschrist.org |
| My Home | https://www.churchofjesuschrist.org/my-home |
| Account Settings | https://id.churchofjesuschrist.org/account |

## LCR Sections
After login, LCR provides access to:
- **Membership** — member records, move-in/out, new members
- **Callings** — current callings, sustaining, setting apart
- **Ministering & Welfare** — assignments, needs
- **Finance** — tithing settlement, budget, donations
- **Missionary** — full-time and ward missionaries
- **Temple** — recommend status, temple activity
- **Reports** — attendance, quarterly reports

## Tips
- Login sessions persist via cookies — no need to re-login every request
- Headless Chrome with playwright-stealth avoids detection
- Storage state files contain auth tokens — treat as sensitive
