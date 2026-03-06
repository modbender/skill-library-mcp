# storacha-upload

OpenClaw skill for uploading, managing, and retrieving files on IPFS via Storacha decentralized storage.

## What It Does

- Upload files and directories to IPFS via Storacha
- Retrieve files using CID-based gateway URLs
- Manage storage spaces and delegations
- Check storage usage and account status
- Full authentication and setup guidance

## Example Commands

Say any of these to your OpenClaw agent:

- "Upload report.pdf to IPFS"
- "Store this file on Storacha"
- "Show my Storacha storage usage"
- "Create a new Storacha space called Projects"
- "List my uploaded files"
- "Get the IPFS link for my last upload"
- "Remove CID bafyBEI... from my uploads"
- "Check my Storacha setup"
- "Share an IPFS link for this file"
- "Back up this directory to decentralized storage"

## First-Time Setup

1. Install the CLI: `npm install -g @storacha/cli`
2. Log in: `storacha login your@email.com` (check email for verification link)
3. Create a space: `storacha space create "MyFiles"`
4. Upload: `storacha up ./myfile.txt`

## Requirements

- **Node.js** v18 or higher — [nodejs.org](https://nodejs.org)
- **Storacha CLI** — `npm install -g @storacha/cli`
- **Storacha account** — free at [console.storacha.network](https://console.storacha.network)

## Plans

| Plan | Price | Storage | Egress | Overage |
|---|---|---|---|---|
| Mild (Free) | $0/month | 5 GB | 5 GB | $0.15/GB |
| Medium | $10/month | 100 GB | 100 GB | $0.05/GB |
| Extra Spicy | $100/month | 2 TB | 2 TB | $0.03/GB |

## Troubleshooting

| Problem | Solution |
|---|---|
| `command not found: storacha` | Run `npm install -g @storacha/cli` |
| `no proofs available for resource` | Re-login with `storacha login` or switch spaces |
| `Not registered with provider` | Check `storacha space info`, re-register via console |
| Upload hangs or times out | Check internet connection, retry |
| `usage/report` permission error | Informational only — uploads still work |
| No spaces listed | Create one: `storacha space create "MyFiles"` |
| Storage limit errors | Upgrade plan or remove old uploads with `storacha rm CID` |

## Links

- [Storacha Documentation](https://docs.storacha.network)
- [Storacha Console](https://console.storacha.network)
- [Storacha CLI Reference](https://github.com/storacha/storacha/tree/main/packages/cli)
- [IPFS Gateway](https://storacha.link)
- [ClawHub](https://clawhub.ai)
