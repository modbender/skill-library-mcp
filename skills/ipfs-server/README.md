# ipfs-server

Full IPFS node operations — install, configure, pin content, publish IPNS, manage peers, and run gateway services.

## Quick Start

```bash
# Install IPFS
brew install ipfs

# Initialize and start node
ipfs init
ipfs daemon &> ipfs.log 2>&1 &

# Add and pin content
ipfs add myfile.txt
ipfs pin add QmHash
```

## Key Features

- **🚀 Full node operations:** Content publishing, pinning, IPNS publishing
- **🌐 Gateway services:** Run local or public IPFS HTTP gateways
- **🔧 Network management:** Peer connections, bootstrap nodes, private networks
- **📌 Content lifecycle:** Add, pin, garbage collect, remote pinning services
- **🔐 Security:** Private networks, API access control, content policies

## Requirements

- IPFS CLI (`kubo` implementation)
- Sufficient storage and bandwidth for node operations

See [SKILL.md](./SKILL.md) for complete documentation.