---
name: lsp28-grid
description: Manage LSP28 The Grid on LUKSO Universal Profiles. Create, update, and manage grid layouts with mini-apps, iframes, and external links. Use when working with Universal Profile grids, LSP28 data encoding, VerifiableURI format, or The Grid feature on LUKSO.
---

# LSP28 The Grid Skill

Manage LSP28 The Grid on Universal Profiles. Create grid layouts with mini-apps, iframes, and external links.

## Quick Start

### 1. Configure Environment

Set these environment variables or edit the scripts:

```bash
export UP_PRIVATE_KEY="your_controller_private_key"
export UP_ADDRESS="your_universal_profile_address"
export KEY_MANAGER="your_key_manager_address"
```

### 2. Update Grid Layout

```javascript
const { ethers } = require('ethers');

// Grid data structure
const gridData = {
  isEditable: true,
  items: [
    {
      type: 'miniapp',
      id: 'app1',
      title: 'My App',
      backgroundColor: '#1a1a2e',
      textColor: '#ffffff',
      text: 'Click me'
    },
    {
      type: 'iframe',
      src: 'https://example.com/embed',
      id: 'frame1',
      title: 'External Content'
    },
    {
      type: 'external',
      url: 'https://example.com',
      id: 'link1',
      title: 'Visit Site'
    }
  ]
};

// Encode as VerifiableURI
const jsonString = JSON.stringify(gridData);
const base64Data = Buffer.from(jsonString).toString('base64');
const verifiableUri = `data:application/json;base64,${base64Data}`;
```

### 3. Execute Transaction

```javascript
// LSP28 Grid data key
const LSP28_GRID_KEY = '0x31cf14955c5b0052c1491ec06644438ec7c14454be5eb6cb9ce4e4edef647423';

// Minimal ABIs
const LSP0_ABI = ['function setData(bytes32 dataKey, bytes dataValue) external'];
const LSP6_ABI = ['function execute(bytes calldata payload) external payable returns (bytes memory)'];

// Setup provider and wallet
const provider = new ethers.JsonRpcProvider('https://rpc.mainnet.lukso.network');
const wallet = new ethers.Wallet(process.env.UP_PRIVATE_KEY, provider);

// Encode setData call on UP
const upInterface = new ethers.Interface(LSP0_ABI);
const executeData = upInterface.encodeFunctionData('setData', [
  LSP28_GRID_KEY,
  ethers.toUtf8Bytes(verifiableUri)
]);

// Send via KeyManager
const keyManager = new ethers.Contract(process.env.KEY_MANAGER, LSP6_ABI, wallet);
const tx = await keyManager.execute(executeData);
const receipt = await tx.wait();
console.log('Grid updated in block:', receipt.blockNumber);
```

## Data Structure Reference

### Grid Item Types

**Mini-App (type: 'miniapp')**
```javascript
{
  type: 'miniapp',
  id: 'unique-id',          // Required: unique identifier
  title: 'App Title',       // Required: display title
  text: 'Button text',      // Required: button label
  backgroundColor: '#fe005b',  // Required: hex color
  textColor: '#ffffff',     // Required: hex color for text
  size: 'medium'            // Optional: 'small', 'medium', 'large'
}
```

**IFrame (type: 'iframe')**
```javascript
{
  type: 'iframe',
  id: 'unique-id',          // Required: unique identifier
  title: 'Frame Title',     // Required: display title
  src: 'https://example.com/embed'  // Required: iframe URL
}
```

**External Link (type: 'external')**
```javascript
{
  type: 'external',
  id: 'unique-id',          // Required: unique identifier
  title: 'Link Title',      // Required: display title
  url: 'https://example.com'  // Required: external URL
}
```

### Full Grid Structure

```javascript
{
  isEditable: true,  // Boolean: allows editing
  items: [
    // Array of grid items (see types above)
  ]
}
```

## Important Constants

| Constant | Value | Description |
|----------|-------|-------------|
| LSP28_GRID_KEY | `0x31cf14955c5b0052c1491ec06644438ec7c14454be5eb6cb9ce4e4edef647423` | Data key for grid storage |
| Chain ID | 42 | LUKSO Mainnet |
| RPC URL | `https://rpc.mainnet.lukso.network` | Public RPC endpoint |

## Color Contrast Requirements

Ensure text is readable on background colors:

| Background | Text Color | Result |
|------------|-----------|--------|
| #1a1a2e (dark) | #ffffff (white) | Good contrast |
| #ffffff (white) | #000000 (black) | Good contrast |
| #fe005b (pink) | #ffffff (white) | Good contrast |
| #000000 (black) | #fe005b (pink) | Good contrast |

## Common Mistakes

❌ **Wrong property names:**
```javascript
// WRONG:
{ color: '#fe005b', content: 'Click me' }

// CORRECT:
{ backgroundColor: '#fe005b', text: 'Click me' }
```

❌ **Missing required fields:**
- All items need: `type`, `id`, `title`
- Mini-apps additionally need: `text`, `backgroundColor`, `textColor`

❌ **Wrong encoding:**
```javascript
// WRONG - toUtf8String instead of toUtf8Bytes:
setData(key, ethers.toUtf8String(uri))

// CORRECT:
setData(key, ethers.toUtf8Bytes(uri))
```

## Transaction Flow

```
Controller Key 
    ↓
KeyManager.execute(payload)
    ↓
UP.setData(LSP28_GRID_KEY, verifiableUri)
    ↓
Grid updated on-chain
```

## CLI Usage

Use the provided script:

```bash
# Use example grid
node scripts/update-grid.js --example

# Load from JSON file
node scripts/update-grid.js --file my-grid.json
```

## References

- `references/lsp28-spec.md` - Full LSP28 specification
- `scripts/update-grid.js` - Complete working example
- LSP28 Standard: https://github.com/lukso-network/LIPs/blob/main/LSPs/LSP-28-TheGrid.md
