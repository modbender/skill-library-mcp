# Hippius CLI Commands Reference

**IMPORTANT**: The public IPFS endpoint is deprecated. Most commands require a self-hosted IPFS node. For most users, use the S3 endpoint instead.

## Installation

```bash
pip install hippius
```

## Configuration

Config stored at `~/.hippius/config.json`.

```bash
# View config
hippius config list

# Set HIPPIUS_KEY (API key from console.hippius.com)
hippius config set hippius hippius_key "your_hippius_key"

# Set seed phrase for blockchain operations
hippius config set substrate seed_phrase "your twelve word mnemonic"

# Set IPFS API URL (required for file operations)
hippius config set ipfs api_url http://localhost:5001
hippius config set ipfs local_ipfs true

# Reset to defaults
hippius config reset
```

## Account Management

```bash
hippius account login       # Interactive login with HIPPIUS_KEY
hippius account login-seed  # Interactive login with seed phrase
hippius account list        # List accounts
hippius account info        # Account info
hippius account balance     # Account balance
hippius account switch      # Switch account
```

## File Operations (Require IPFS Node)

All these fail without a configured IPFS node:

```bash
# Store (upload)
hippius store <file_path>
hippius store <file_path> --no-encrypt
hippius store <file_path> --encrypt

# Download
hippius download <CID> <output_path>

# Store directory
hippius store-dir <directory_path>

# Check if CID exists
hippius exists <CID>

# View file content
hippius cat <CID>

# Pin a CID
hippius pin <CID>

# Delete
hippius delete <CID>

# List files
hippius files

# Check credits
hippius credits
```

## Erasure Coding (Require IPFS Node)

```bash
# Erasure code a file
hippius erasure-code <file_path> --k 3 --m 5

# Reconstruct
hippius reconstruct <metadata_CID> <output_path>

# List erasure-coded files
hippius ec-files
```

## Global Options

```
--api-url <URL>       Custom IPFS API URL
--local-ipfs          Use local IPFS node (localhost:5001)
--substrate-url <URL> Custom Substrate WebSocket URL
--verbose / -v        Debug output
--encrypt             Encrypt files
--no-encrypt          Skip encryption
```

## S3 Alternative (Recommended)

Since IPFS endpoint is deprecated, use S3:

```bash
export AWS_ACCESS_KEY_ID="hip_your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"

# Upload
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 cp file.txt s3://my-bucket/file.txt

# Download
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 cp s3://my-bucket/file.txt ./file.txt

# List
aws --endpoint-url https://s3.hippius.com --region decentralized \
    s3 ls s3://my-bucket/
```

## Troubleshooting

**"Public store.hippius.network has been deprecated"**
- Use S3 instead (recommended)
- Or run local IPFS: `ipfs daemon` then `hippius config set ipfs api_url http://localhost:5001`

**Login Issues**
- `hippius account login` expects HIPPIUS_KEY (API key), not seed phrase
- For non-interactive setup, use `hippius config set` directly
