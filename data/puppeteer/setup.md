# Setup — Puppeteer

Read this when `~/puppeteer/` doesn't exist. Don't ask — just start naturally.

## Your Attitude

You're enabling powerful browser automation. The user can scrape websites, test web apps, generate PDFs, and automate repetitive browser tasks. Be practical and code-focused.

## Priority Order

### 1. First: Integration

Figure out how they want to use browser automation:
- Web scraping specific sites?
- E2E testing for their app?
- Generating screenshots/PDFs?
- Automating repetitive browser tasks?

Once clear, confirm and note their primary use case.

### 2. Then: Environment

Check their setup:
- Node.js installed? (`node --version`)
- Puppeteer installed? (`npm list puppeteer`)

If not installed:
```bash
npm install puppeteer
# or for lighter install (uses system Chrome):
npm install puppeteer-core
```

### 3. Finally: First Script

Offer to create a starter script for their use case:
- Scraping → extraction template
- Testing → assertion template  
- Screenshots → capture template

Save to `~/puppeteer/scripts/`.

## What You're Saving (internally)

As you learn their workflow:
- Primary use case (scraping, testing, screenshots)
- Target sites or apps
- Preferred patterns (headless, viewport size)
- Common selectors they use

Store in `~/puppeteer/memory.md` without mentioning file paths to them.
