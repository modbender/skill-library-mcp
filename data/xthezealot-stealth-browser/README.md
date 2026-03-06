# Stealth Browser Skill

A headless browser with advanced anti-detection capabilities for bypassing bot protection.

## Usage

```
/stealth-browser open <url>           - Open a URL and return content
/stealth-browser screenshot <url>     - Take a screenshot
/stealth-browser pdf <url>            - Save as PDF
/stealth-browser parallel <urls...>   - Fetch multiple URLs in parallel
```

## Examples

```
/stealth-browser open https://www.bazaraki.com/adv/6203561_2-bedroom-detached-house-for-sale/
/stealth-browser parallel https://site1.com https://site2.com
```

## Technical Details

Uses Playwright Extra with Stealth Plugin to bypass:
- Cloudflare bot detection
- reCAPTCHA challenges  
- Fingerprint-based blocking

## Requirements

- playwright-extra
- puppeteer-extra-plugin-stealth
- playwright-core
- chromium (system-installed)
