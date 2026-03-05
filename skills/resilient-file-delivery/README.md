# Resilient File Delivery

**Value Proposition**: Bypass sandbox restrictions and email blocks. Deliver files via multi-channel fallback (Telegram, Discord, Google Drive, S3, IPFS).

## Problem Solved
- Files blocked by email providers
- Sandbox sandboxed file transfer limitations
- Need for reliable multi-channel fallback
- Compliance with different platform restrictions

## Use Cases
- Deliver large datasets when email fails
- Send files to users across multiple platforms
- Automated backup distribution
- Secure file handoff in restricted environments
- Zero-trust file delivery pipelines

## Quick Start

```bash
npm install resilient-file-delivery
# or
python -m pip install resilient-file-delivery
```

```javascript
const FileDelivery = require('resilient-file-delivery');

const delivery = new FileDelivery({
  primaryChannels: ['telegram', 'discord'],
  fallbackChannels: ['google-drive', 's3', 'ipfs'],
  retryAttempts: 3
});

await delivery.send({
  file: '/path/to/file.zip',
  recipient: 'user@example.com',
  metadata: { sender: 'bot', priority: 'high' }
});
```

## Features
✅ Multi-channel delivery (Telegram, Discord, Google Drive, S3, IPFS)
✅ Automatic fallback on failure
✅ Retry logic with exponential backoff
✅ File chunking for large payloads
✅ Integrity verification (MD5/SHA256)
✅ Delivery receipts & tracking
✅ Rate limiting aware

## Installation

### Node.js
```bash
npm install resilient-file-delivery
```

### Python
```bash
pip install resilient-file-delivery
```

### Manual
Clone the repo and run:
```bash
git clone https://github.com/midas-skills/resilient-file-delivery.git
cd resilient-file-delivery
npm install  # or pip install -r requirements.txt
```

## Configuration

```json
{
  "channels": {
    "telegram": { "token": "BOT_TOKEN", "enabled": true },
    "discord": { "webhook": "WEBHOOK_URL", "enabled": true },
    "google-drive": { "credentials": "creds.json", "enabled": true },
    "s3": { "bucket": "my-bucket", "region": "us-east-1", "enabled": true },
    "ipfs": { "gateway": "https://ipfs.io", "enabled": true }
  },
  "retryAttempts": 3,
  "chunkSize": 52428800,
  "verifyIntegrity": true
}
```

## Example Code

### Basic Delivery
```javascript
const FileDelivery = require('resilient-file-delivery');

async function deliverReport() {
  const delivery = new FileDelivery();
  
  const result = await delivery.send({
    file: 'monthly_report.pdf',
    recipient: '@sales_team',
    channel: 'discord'
  });
  
  console.log('Delivered via:', result.deliveredVia);
  console.log('Tracking ID:', result.trackingId);
}

deliverReport();
```

### Multi-Channel with Fallback
```javascript
const delivery = new FileDelivery({
  primaryChannels: ['telegram'],
  fallbackChannels: ['discord', 'google-drive', 's3']
});

await delivery.send({
  file: 'large_dataset.zip',
  recipient: 'data_team',
  timeout: 30000,  // 30 seconds before fallback
  onFallback: (error, nextChannel) => {
    console.log(`Retrying via ${nextChannel}: ${error.message}`);
  }
});
```

### Batch Delivery
```javascript
const files = [
  { file: 'report1.pdf', recipient: 'team1' },
  { file: 'report2.pdf', recipient: 'team2' },
  { file: 'dataset.zip', recipient: 'team3' }
];

const results = await delivery.sendBatch(files, {
  parallel: 2,
  stopOnError: false
});

console.log(`Delivered: ${results.succeeded}/${results.total}`);
```

## API Reference

### `send(options)`
Send a single file.
- `file` (string): Path to file
- `recipient` (string): Recipient ID or handle
- `channel` (string, optional): Force specific channel
- `timeout` (number, optional): Milliseconds before fallback
- Returns: `Promise<{trackingId, deliveredVia, timestamp}>`

### `sendBatch(files, options)`
Send multiple files.
- `files` (array): Array of send options
- `parallel` (number): Concurrent sends
- `stopOnError` (boolean): Stop on first failure
- Returns: `Promise<{succeeded, failed, total, results}>`

## Troubleshooting

**File too large for Telegram?**
→ Automatically falls back to S3 or IPFS

**API rate limits?**
→ Built-in queue + exponential backoff

**Recipient unreachable?**
→ Cycles through fallback channels, stores metadata for retry

## Support
📧 support@midas-skills.com
🔗 Docs: https://docs.midas-skills.com/resilient-file-delivery

---

**Want pro version + updates?** [Buy bundle on Gumroad](https://gumroad.com/midas-skills)
