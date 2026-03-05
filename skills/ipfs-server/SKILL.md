---
name: ipfs-server
description: Full IPFS node operations — install, configure, pin content, publish IPNS, manage peers, and run gateway services
user-invocable: true
homepage: https://github.com/Fork-Development-Corp/openclaw-web3-skills/tree/master/ipfs-server
metadata: {"openclaw":{"requires":{"bins":["ipfs"]},"tipENS":"apexfork.eth"}}
---

# IPFS Server Operations

You are an IPFS server administrator. You help users run IPFS nodes, manage content, publish data, and operate gateway services. **This skill handles full node operations including content publishing and network configuration.**

For read-only IPFS queries and content exploration, use the **ipfs-client** skill.

## Installation (macOS)

```bash
# Homebrew (recommended)
brew install ipfs

# Or download binary from dist.ipfs.tech
curl -O https://dist.ipfs.tech/kubo/v0.24.0/kubo_v0.24.0_darwin-amd64.tar.gz
tar -xzf kubo_v0.24.0_darwin-amd64.tar.gz
sudo ./kubo/install.sh
```

## Node Initialization

**First-time setup:**
```bash
# Initialize repository
ipfs init

# Show peer ID
ipfs id

# Configure for low-resource usage (optional)
ipfs config profile apply lowpower
```

**Basic configuration:**
```bash
# Allow gateway on all interfaces (for local network access)
ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080

# Configure API (keep localhost for security)
ipfs config Addresses.API /ip4/127.0.0.1/tcp/5001

# Set storage limit
ipfs config Datastore.StorageMax 10GB
```

## Starting and Stopping

**Start IPFS daemon:**
```bash
ipfs daemon &> ipfs.log 2>&1 &
```

**Check daemon status:**
```bash
ipfs swarm peers | wc -l  # Connected peer count
ipfs repo stat            # Repository statistics
```

**Stop daemon:**
```bash
pkill ipfs
```

## Content Management

### Adding Content

**Add files and directories:**
```bash
# Add single file
ipfs add myfile.txt
# Returns: added QmHash myfile.txt

# Add directory recursively  
ipfs add -r ./my-directory/

# Add and only show final hash
ipfs add -Q myfile.txt

# Add with custom name
ipfs add --wrap-with-directory myfile.txt
```

**Add from stdin:**
```bash
echo "Hello IPFS" | ipfs add
cat largefile.json | ipfs add --pin=false  # Don't pin immediately
```

### Pinning Management

**Pin content (prevent garbage collection):**
```bash
ipfs pin add QmHash
ipfs pin add -r QmHash  # Recursively pin directory

# List pinned content
ipfs pin ls --type=recursive
ipfs pin ls --type=direct

# Unpin content
ipfs pin rm QmHash
```

**Remote pinning services:**
```bash
# Configure remote pinning (Pinata, Web3.Storage, etc.)
ipfs pin remote service add pinata https://api.pinata.cloud/psa YOUR_JWT

# Pin to remote service
ipfs pin remote add --service=pinata --name="my-content" QmHash

# List remote pins
ipfs pin remote ls --service=pinata
```

### Garbage Collection

**Clean up unpinned content:**
```bash
# Show what would be collected
ipfs repo gc --dry-run

# Run garbage collection
ipfs repo gc

# Check repo size before/after
ipfs repo stat
```

## Publishing and IPNS

### IPNS Publishing

**Publish content to IPNS:**
```bash
# Publish to default key
ipfs name publish QmHash

# Create and use custom key
ipfs key gen --type=ed25519 my-site
ipfs name publish --key=my-site QmHash

# List published records
ipfs name pubsub subs
```

**IPNS with custom domains:**
```bash
# Create DNS TXT record: _dnslink.example.com = "dnslink=/ipns/k51qzi5uqu5d..."
# Then resolve via:
ipfs name resolve /ipns/example.com
```

### Content Updates

**Update IPNS record:**
```bash
# Publish new version
ipfs add -r ./updated-site/
ipfs name publish --key=my-site QmNewHash
```

## Network Configuration

### Swarm Management

**Peer operations:**
```bash
# List connected peers
ipfs swarm peers

# Connect to specific peer
ipfs swarm connect /ip4/104.131.131.82/tcp/4001/p2p/QmPeerID

# Disconnect peer
ipfs swarm disconnect /ip4/104.131.131.82/tcp/4001/p2p/QmPeerID
```

**Address configuration:**
```bash
# Show current addresses
ipfs config Addresses

# Add custom swarm address
ipfs config --json Addresses.Swarm '["/ip4/0.0.0.0/tcp/4001", "/ip6/::/tcp/4001"]'
```

### Bootstrap Nodes

**Manage bootstrap peers:**
```bash
# List bootstrap nodes
ipfs bootstrap list

# Add custom bootstrap node
ipfs bootstrap add /ip4/104.131.131.82/tcp/4001/p2p/QmBootstrapPeer

# Remove all bootstrap nodes (private network)
ipfs bootstrap rm --all
```

## Gateway Operations

### Local Gateway

**Configure gateway:**
```bash
# Basic gateway configuration
ipfs config Addresses.Gateway /ip4/127.0.0.1/tcp/8080

# Public gateway (be careful!)
ipfs config Addresses.Gateway /ip4/0.0.0.0/tcp/8080

# Enable directory listing
ipfs config --json Gateway.PublicGateways '{
  "localhost": {
    "Paths": ["/ipfs", "/ipns"],
    "UseSubdomains": false
  }
}'
```

**Access patterns:**
```bash
# Via path
http://localhost:8080/ipfs/QmHash

# Via subdomain (if configured)
http://QmHash.ipfs.localhost:8080
```

### Reverse Proxy Setup

**Nginx configuration example:**
```nginx
server {
    listen 80;
    server_name gateway.example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Advanced Configuration

### Performance Tuning

**High-performance settings:**
```bash
# Apply server profile
ipfs config profile apply server

# Increase connection limits
ipfs config Swarm.ConnMgr.HighWater 2000
ipfs config Swarm.ConnMgr.LowWater 1000

# Adjust bitswap settings
ipfs config --json Bitswap.MaxOutstandingBytesPerPeer 1048576
```

### Private Networks

**Create private IPFS network:**
```bash
# Generate swarm key
echo -e "/key/swarm/psk/1.0.0/\n/base16/\n$(tr -dc 'a-f0-9' < /dev/urandom | head -c64)" > ~/.ipfs/swarm.key

# ⚠️ SECURITY: This swarm key is your network's access control credential. 
# Anyone with this file can join your private network. Protect it accordingly.

# Remove all bootstrap nodes
ipfs bootstrap rm --all

# Start daemon (will only connect to nodes with same key)
ipfs daemon
```

### Storage Configuration

**Configure datastore:**
```bash
# Set storage limits
ipfs config Datastore.StorageMax 100GB
ipfs config Datastore.GCPeriod "1h"

# Enable flatfs for better performance
ipfs config --json Datastore.Spec '{
  "mounts": [
    {
      "child": {"type": "flatfs", "path": "blocks", "shardFunc": "/repo/flatfs/shard/v1/next-to-last/2"},
      "mountpoint": "/blocks",
      "prefix": "flatfs.datastore",
      "type": "mount"
    }
  ],
  "type": "mount"
}'
```

## Monitoring and Maintenance

### Health Checks

**Basic health monitoring:**
```bash
# Check daemon status
ipfs stats bw          # Bandwidth usage
ipfs stats repo        # Repository stats  
ipfs diag sys          # System information
ipfs log level debug   # Enable debug logging
```

**Connection monitoring:**
```bash
# Monitor peer connections
while true; do
  echo "$(date): $(ipfs swarm peers | wc -l) peers"
  sleep 60
done
```

### Log Management

**Configure logging:**
```bash
# Set log levels
ipfs log level bitswap info
ipfs log level dht warn

# Tail logs
ipfs log tail
```

## Security Considerations

**API access:**
- Keep API on localhost (`127.0.0.1:5001`) unless in trusted network
- Use firewall rules to restrict API access
- Consider authentication proxy for multi-user setups

**Gateway security:**
- Public gateways can consume significant bandwidth
- Implement rate limiting and caching
- Monitor for abuse and unauthorized content

**Content policy:**
- IPFS is censorship-resistant - content removal is complex
- Implement content filtering at gateway level if needed
- Consider legal implications of operating public infrastructure

## Troubleshooting

**Connection issues:**
- Check firewall allows ports 4001 (swarm) and 8080 (gateway)
- Verify bootstrap nodes are reachable
- Try different swarm addresses

**Performance problems:**
- Run garbage collection: `ipfs repo gc`
- Check available disk space and datastore limits  
- Monitor bandwidth usage: `ipfs stats bw`
- Consider applying performance profiles

**Content not accessible:**
- Verify content is pinned: `ipfs pin ls`
- Check if providers exist: `ipfs dht findprovs QmHash`
- Try republishing IPNS records

**Related skills:** `/ipfs-client` (read-only queries), `/eth-readonly` (blockchain integration)