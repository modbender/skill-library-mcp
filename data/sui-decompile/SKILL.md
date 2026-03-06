---
name: sui-decompile
description: Fetch on-chain Sui Move contract source code and let your agent explain how smart contracts work. Scrape from Suivision/Suiscan explorers, analyze DeFi protocols, and understand any contract on Sui.
homepage: https://suivision.xyz
metadata:
  openclaw:
    emoji: "🔓"
---

# Sui Decompile Skill

Fetch decompiled source code for on-chain Sui Move packages via block explorers.

**GitHub:** <https://github.com/EasonC13-agent/sui-skills/tree/main/sui-decompile>

## Suivision (Preferred)

May have official verified source code when available.

```
URL: https://suivision.xyz/package/{package_id}?tab=Code
```

**Browser workflow:**
1. `browser action=open profile=openclaw targetUrl="https://suivision.xyz/package/{package_id}?tab=Code"`
2. Click module tabs on the left if multiple modules exist
3. Extract code:
```javascript
() => {
  const rows = document.querySelectorAll('table tr');
  const lines = [];
  rows.forEach(r => {
    const cells = r.querySelectorAll('td');
    if (cells.length >= 2) lines.push(cells[1].textContent);
  });
  return lines.join('\n');
}
```

## Suiscan (Alternative)

```
URL: https://suiscan.xyz/mainnet/object/{package_id}/contracts
```

**Browser workflow:**
1. `browser action=open profile=openclaw targetUrl="https://suiscan.xyz/mainnet/object/{package_id}/contracts"`
2. Click "Source" tab (default may show Bytecode)
3. Click module tabs if multiple modules
4. Extract code:
```javascript
() => {
  const rows = document.querySelectorAll('table tr');
  const lines = [];
  rows.forEach(r => {
    const cells = r.querySelectorAll('td');
    if (cells.length >= 2) lines.push(cells[1].textContent);
  });
  return lines.join('\n') || 'not found';
}
```

## Multiple Modules

Packages like DeepBook (`0xdee9`) have multiple modules:
1. List module tabs from sidebar
2. Click each tab, extract code
3. Save to separate `.move` files

## Examples

| Package | Suivision | Suiscan |
|---------|-----------|---------|
| Sui Framework | `suivision.xyz/package/0x2?tab=Code` | `suiscan.xyz/mainnet/object/0x2/contracts` |
| DeepBook | `suivision.xyz/package/0xdee9?tab=Code` | `suiscan.xyz/mainnet/object/0xdee9/contracts` |

## Use with Other Skills

This skill works great with the Sui development skill suite:

- **sui-move**: Write and deploy Move smart contracts. Use `sui-decompile` to study existing contracts, then use `sui-move` to write your own.
- **sui-coverage**: Analyze test coverage. Decompile a contract, write tests for it, then check coverage.

**Typical workflow:**
1. `sui-decompile` - Study how a DeFi protocol works
2. `sui-move` - Write your own contract based on learned patterns
3. `sui-coverage` - Ensure your code is well-tested

## Server/Headless Setup

For running on servers without display (CI/CD, VPS, etc.), use Puppeteer with a virtual display to avoid headless detection:

```bash
# Install xvfb (virtual framebuffer)
sudo apt-get install xvfb

# Run with virtual display (avoids headless detection)
xvfb-run --auto-servernum node scraper.js
```

**Puppeteer example:**
```javascript
const puppeteer = require('puppeteer');

async function fetchContractSource(packageId) {
  const browser = await puppeteer.launch({
    headless: false,  // Use 'new' headless or false with xvfb
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.goto(`https://suivision.xyz/package/${packageId}?tab=Code`);
  await page.waitForSelector('table tr');
  
  const code = await page.evaluate(() => {
    const rows = document.querySelectorAll('table tr');
    const lines = [];
    rows.forEach(r => {
      const cells = r.querySelectorAll('td');
      if (cells.length >= 2) lines.push(cells[1].textContent);
    });
    return lines.join('\n');
  });
  
  await browser.close();
  return code;
}
```

**Why xvfb?** Some sites detect headless browsers. Running with `xvfb-run` creates a virtual display, making the browser behave like a real desktop browser.

## Notes

- Suivision may show official verified source (MovebitAudit)
- Suiscan shows Revela decompiled code
- Decompiled code may not compile directly
- **Close browser tabs after use!**

## Related Skills

This skill is part of the Sui development skill suite:

| Skill | Description |
|-------|-------------|
| **sui-decompile** | Fetch and read on-chain contract source code |
| [sui-move](https://clawhub.ai/EasonC13/sui-move) | Write and deploy Move smart contracts |
| [sui-coverage](https://clawhub.ai/EasonC13/sui-coverage) | Analyze test coverage with security analysis |
| [sui-agent-wallet](https://clawhub.ai/EasonC13/sui-agent-wallet) | Build and test DApps frontend |

**Workflow:**
```
sui-decompile → sui-move → sui-coverage → sui-agent-wallet
    Study        Write      Test & Audit   Build DApps
```

All skills: <https://github.com/EasonC13-agent/sui-skills>
