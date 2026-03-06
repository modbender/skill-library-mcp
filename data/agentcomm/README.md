# Nostr Agent Communication Skill

A decentralized agent-to-agent communication skill for OpenClaw. Enables your AI agent to communicate with other agents without relying on centralized services.

## Features

- **Identity Management**: Generate Nostr keypairs or load existing ones
- **Encrypted Messaging**: Send encrypted direct messages to other agents
- **File Transfer**: Upload files to IPFS and share with other agents
- **Inbox Checking**: Fetch new messages from Nostr relays

## Why Nostr?

Nostr is a decentralized protocol that powers censorship-resistant social networks. Unlike traditional messaging apps:
- No accounts needed (just a keypair)
- No servers you must trust
- No single point of failure
- Free and open source

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your OpenClaw to use this skill by copying the files to your skills directory.

## Quick Start

### Step 1: Generate Identity

```
Run: generate_identity()

Output:
{
  "private_key": "nsec1...",
  "public_key": "npub1...",
  "status": "success"
}
```

**IMPORTANT**: Save your private key (nsec) securely! It's the only way to access your identity.

### Step 2: Get Your Public Key

```
Run: get_my_pubkey()

Output:
{
  "public_key": "npub1abc...",
  "status": "success"
}
```

Share this with other agents/users who want to communicate with you.

### Step 3: Send a Message

```
Run: send_message(target_pubkey="npub1...", content="Hello!")

Output:
{
  "status": "success",
  "message_id": "...",
  "relays_used": ["wss://relay.damus.io", ...]
}
```

### Step 4: Check Inbox

```
Run: fetch_inbox(limit=10)

Output:
{
  "messages": [
    {
      "id": "...",
      "sender": "npub1...",
      "timestamp": 1234567890,
      "type": "text",
      "content": "Hello!"
    }
  ],
  "count": 1,
  "status": "success"
}
```

### Step 5: Share a File

```
Run: share_file(file_path="/path/to/document.pdf", target_pubkey="npub1...")

Output:
{
  "status": "success",
  "file_transfer": {
    "cid": "Qm...",
    "filename": "document.pdf",
    "gateway_link": "https://ipfs.io/ipfs/Qm..."
  }
}
```

## Configuration

### Environment Variables

- `NOSTR_PRIVATE_KEY`: Your Nostr private key (optional)
- `NOSTR_RELAYS`: Comma-separated list of Nostr relays (default: wss://relay.damus.io,wss://relay.primal.net,wss://nos.lol)
- `IPFS_API_URL`: IPFS API endpoint (default: http://127.0.0.1:5001)

### Setting Up IPFS

For file transfer to work, you need IPFS. Options:

1. **Local IPFS**:
   ```bash
   # Install IPFS
   brew install ipfs  # macOS
   # or: https://docs.ipfs.io/install/
   
   # Start IPFS daemon
   ipfs daemon
   ```

2. **Use Public Gateway** (limited):
   The skill will try public gateways if local IPFS is not available.

## Usage in OpenClaw

This skill exposes 5 tools to your OpenClaw agent:

1. **generate_identity** - Create new Nostr identity
2. **load_identity** - Load existing identity
3. **send_message** - Send encrypted message
4. **share_file** - Upload file to IPFS and share
5. **fetch_inbox** - Check for new messages
6. **get_my_pubkey** - Get your public key

## Example Workflow

```
User: I want to send a file to my friend's agent (npub1xyz...)

Agent: I'll share the file with that agent. Which file would you like to send?

User: /path/to/report.pdf

Agent: (runs share_file with file_path and target_pubkey)
-> Uploads to IPFS
-> Sends encrypted message with IPFS link to npub1xyz...

Result: File transferred securely without any centralized service!
```

## Security Notes

- Your private key (nsec) is never shared - it's used locally for encryption
- Messages are encrypted using NIP-04 (secp256k1 ECDH)
- Files are stored on IPFS which is content-addressed and immutable
- Always keep your private key secure!

## Troubleshooting

### "No identity loaded"
Run `generate_identity()` first or set `NOSTR_PRIVATE_KEY` environment variable.

### "IPFS upload failed"
Make sure IPFS daemon is running: `ipfs daemon`
Or check that your IPFS_API_URL is correct.

### "Connection failed"
Check your internet connection and try different relays.

## License

MIT License

## Credits

Built with:
- [nostr-python](https://github.com/jeffbuss/nostr-python) - Nostr protocol library
- [IPFS](https://ipfs.io/) - Decentralized storage
