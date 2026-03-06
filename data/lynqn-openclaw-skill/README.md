# LYNQN OpenClaw Skill

Integrate LYNQN's sharing, QR generation, and URL shortening capabilities into your OpenClaw agents.

## Installation

```bash
openclaw skill install lynqn
```

Or install manually:
```bash
git clone https://github.com/lynqn/lynqn-openclaw-skill
cd lynqn-openclaw-skill
npm install
```

## Commands

### Share Text
Create shareable text or code snippets with automatic QR codes.

```bash
/lynqn share <text> [--syntax] [--expires 1d|1w|1m|3m]
```

**Examples:**
```bash
/lynqn share Hello world!
/lynqn share const x = 5; console.log(x); --syntax --expires 1w
/lynqn share "API Key: abc123" --expires 1d
```

**Options:**
- `--syntax`: Enable syntax highlighting for code
- `--expires`: Set expiration time (1d, 1w, 1m, 3m)

### Generate QR Code
Generate QR codes from any text or URL.

```bash
/lynqn qr <content> [--size 200-800] [--error L|M|Q|H]
```

**Examples:**
```bash
/lynqn qr https://example.com
/lynqn qr "Wi-Fi: MyNetwork, Password: 12345" --size 400 --error H
```

**Options:**
- `--size`: QR code size in pixels (200-800)
- `--error`: Error correction level (L=7%, M=15%, Q=25%, H=30%)

### Shorten URL
Convert long URLs into short, shareable links.

```bash
/lynqn shorten <url>
```

**Examples:**
```bash
/lynqn shorten https://example.com/very/long/path/here
```

### Get Stats
View LYNQN platform statistics.

```bash
/lynqn stats
```

## Direct API Access

For custom integrations, use the LYNQN REST API:

### Create Share
```bash
POST https://lynqn.io/api/share
Content-Type: application/json

{
  "content": "Your text here",
  "format": "text",  // or "code"
  "expiresIn": 604800  // seconds (1 week = 604800)
}

# Response
{
  "id": "abc123"
}

# Access at: https://lynqn.io/s/abc123
```

### Shorten URL
```bash
POST https://lynqn.io/api/shorten
Content-Type: application/json

{
  "url": "https://example.com/long/path"
}

# Response
{
  "id": "xyz789",
  "shortUrl": "https://lynqn.io/l/xyz789",
  "originalUrl": "https://example.com/long/path",
  "clicks": 0,
  "createdAt": 1707000000000
}
```

### Get Statistics
```bash
GET https://lynqn.io/api/stats

# Response
{
  "total": 15623
}
```

## Configuration

Set environment variables in your OpenClaw config:

```env
LYNQN_API_URL=https://lynqn.io/api
```

## Rate Limits

- **Free tier**: 100 requests per hour
- **With $LYNQN tokens**: Priority access (coming soon)

## Token Integration

Hold $LYNQN tokens to unlock:
- Priority API rate limits
- Extended expiration times (up to 1 year)
- Analytics dashboard
- Premium agent features

Learn more: https://lynqn.io/tokenomics

## Use Cases

- **Code Sharing**: Share code snippets with teammates
- **Event Coordination**: Generate QR codes for event check-ins
- **Link Management**: Shorten URLs for social media
- **Data Sync**: Quickly share text between devices
- **Presentation Tools**: Create scannable QR codes for slides
- **Automated Reporting**: Agents can share logs and reports

## Examples

### Share a code snippet
```javascript
const code = `
function hello() {
  console.log('Hello from LYNQN!');
}
`;

agent.run('/lynqn share ' + code + ' --syntax --expires 1w');
```

### Batch URL shortening
```javascript
const urls = [
  'https://example.com/page1',
  'https://example.com/page2',
  'https://example.com/page3'
];

for (const url of urls) {
  await agent.run('/lynqn shorten ' + url);
}
```

### Generate QR for Wi-Fi
```javascript
const wifiInfo = 'WIFI:T:WPA;S:MyNetwork;P:password123;;';
agent.run(`/lynqn qr "${wifiInfo}" --size 400 --error H`);
```

## Support

- Website: https://lynqn.io
- Agents: https://lynqn.io/agents
- Issues: https://github.com/lynqn/lynqn-openclaw-skill/issues

## License

MIT

## Contributing

Contributions welcome! Please read our contributing guidelines before submitting PRs.

## Changelog

### v1.0.0 (2026-02-16)
- Initial release
- Text sharing with QR codes
- QR code generation
- URL shortening
- Platform statistics
