# 🌐 NadName Agent

Register .nad names on Monad blockchain via Nad Name Service (NNS).

## Quick Start

```bash
# Install dependencies
npm install

# Check name availability
node scripts/check-name.js myname

# Register name (set PRIVATE_KEY first)
export PRIVATE_KEY="0x..."
node scripts/register-name.js --name myname

# List owned names
node scripts/my-names.js
```

## Security Features

✅ No hardcoded private keys  
✅ Environment variable or encrypted keystore only  
✅ No auto-detection of external wallet paths  
✅ Proper file permissions (600) for sensitive data  
✅ AES-256-GCM encryption for managed keystores  

## Documentation

See [SKILL.md](SKILL.md) for complete documentation and usage examples.

## Important Notes

- **Permanent ownership**: .nad names never expire
- **One-time fee**: No renewal costs
- **NFT-based**: Names are tradeable NFTs
- **Emoji support**: Use 🦞.nad or 你好.nad
- **Monad blockchain**: Fast and cheap transactions