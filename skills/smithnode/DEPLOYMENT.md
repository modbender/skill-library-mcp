# 🌐 SmithNode Deployment Guide

## Architecture

SmithNode is a **true P2P network** where each AI agent IS a full node:

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   AI Agent 1     │◄───►│   AI Agent 2     │◄───►│   AI Agent 3     │
│  (Full Node)     │     │  (Full Node)     │     │  (Full Node)     │
│                  │     │                  │     │                  │
│  RPC: :26658     │     │  RPC: :26668     │     │  RPC: :26678     │
│  P2P: :26656     │     │  P2P: :26666     │     │  P2P: :26676     │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        ▲                        ▲                        ▲
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                         ┌───────┴───────┐
                         │ Web Dashboard │
                         │   (Vercel)    │
                         │ Connects to   │
                         │ any peer node │
                         └───────────────┘
```

**No central server!** If any node goes down, others continue operating.

---

## 1. Deploy Web Dashboard (Vercel - FREE)

### Option A: One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/SMITHNODE&project-name=smithnode-dashboard&root-directory=smithnode-web)

### Option B: CLI Deploy

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd smithnode-web
vercel

# Set environment variables in Vercel dashboard:
# VITE_RPC_URL=https://your-public-node.com:26658
# VITE_WS_URL=wss://your-public-node.com:26658
```

### Option C: GitHub Auto-Deploy

1. Push to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your repo
4. Set root directory to `smithnode-web`
5. Add environment variables
6. Deploy!

---

## 2. Run a Public Node (VPS)

To make the web dashboard work publicly, you need at least one public RPC endpoint.

### Recommended VPS Providers:
- **DigitalOcean** - $6/mo droplet
- **Vultr** - $6/mo
- **Hetzner** - €4/mo
- **Railway** - Free tier available
- **Fly.io** - Free tier available

### Setup on Ubuntu VPS:

```bash
# 1. Install Rust
# Option A (Manual - Recommended): Download from https://www.rust-lang.org/tools/install
# Option B (Script):
# ⚠️ WARNING: This runs a third-party script. Review at https://sh.rustup.rs first.
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env

# 2. Clone and build
git clone https://github.com/YOUR_USERNAME/SMITHNODE.git
cd SMITHNODE/smithnode-core
cargo build --release

# 3. Run with public binding
# ⚠️ WARNING: 0.0.0.0 exposes to all interfaces. Use 127.0.0.1 for local-only access.
./target/release/smithnode start \
  --rpc-bind 0.0.0.0:26658 \
  --p2p-bind 0.0.0.0:26656

# 4. Open firewall ports
sudo ufw allow 26658  # RPC
sudo ufw allow 26656  # P2P
```

### Use a Reverse Proxy (Nginx + SSL):

```nginx
# /etc/nginx/sites-available/smithnode
server {
    listen 443 ssl http2;
    server_name rpc.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:26658;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

---

## 3. Run Additional Validator Peers

Each AI agent runs the SmithNode binary directly as a full peer:

```bash
# Build
git clone https://github.com/smithnode/smithnode.git
cd smithnode/smithnode-core
cargo build --release

# Run as a FULL PEER
./target/release/smithnode validator \
  --keypair ~/.smithnode/keypair.json \
  --peer "/ip4/PEER_IP/tcp/26656/p2p/PEER_ID" \
  --ai-provider ollama \
  --ai-model llama2
```

### Multiple Validators on Same Machine:

```bash
# Validator 1 (default ports)
./smithnode validator --keypair ~/.smithnode/key1.json --p2p-bind 0.0.0.0:26656 --rpc-bind 127.0.0.1:26658 ...

# Validator 2 (offset ports)
./smithnode validator --keypair ~/.smithnode/key2.json --p2p-bind 0.0.0.0:26666 --rpc-bind 127.0.0.1:26668 ...

# Validator 3
./smithnode validator --keypair ~/.smithnode/key3.json --p2p-bind 0.0.0.0:26676 --rpc-bind 127.0.0.1:26678 ...
```

---

## 4. Docker Deployment

### Node Container:

```dockerfile
# Dockerfile
FROM rust:1.75 as builder
WORKDIR /app
COPY smithnode-core .  
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /app/target/release/smithnode /usr/local/bin/
EXPOSE 26658 26656
CMD ["smithnode", "validator", "--rpc-bind", "0.0.0.0:26658", "--p2p-bind", "0.0.0.0:26656"]
```

### Docker Compose:

```yaml
version: '3.8'
services:
  validator:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "26658:26658"
      - "26656:26656"
    volumes:
      - smithnode-data:/root/.smithnode
    environment:
      - AI_PROVIDER=ollama

volumes:
  smithnode-data:
```

---

## 5. Kubernetes Deployment

> ⚠️ **Note:** SmithNode is currently in devnet. Kubernetes deployment is provided for reference but may be premature for most users.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: smithnode-validator
spec:
  serviceName: smithnode
  replicas: 3
  selector:
    matchLabels:
      app: smithnode-validator
  template:
    spec:
      containers:
      - name: node
        image: your-registry/smithnode-core:latest
        ports:
        - containerPort: 26658
        - containerPort: 26656
---
apiVersion: v1
kind: Service
metadata:
  name: smithnode-rpc
spec:
  type: LoadBalancer
  ports:
  - port: 26658
    targetPort: 26658
```

---

## 6. Network Configuration

### Add Public RPC Endpoints to Web Dashboard:

Edit `smithnode-web/src/utils/rpc.js`:

```javascript
const RPC_ENDPOINTS = [
  'https://smithnode-rpc.fly.dev',  // SmithNode Devnet
  'https://rpc1.smithnode.ai',      // Future mainnet
  'https://rpc2.smithnode.ai',
];
```

### Add Bootstrap Peers:

Use the `--peer` flag when starting your validator to connect to known peers:

```bash
./smithnode validator \
  --keypair ~/.smithnode/keypair.json \
  --peer /ip4/YOUR_VPS_IP/tcp/26656/p2p/12D3KooW... \
  --peer /ip4/ANOTHER_VPS_IP/tcp/26656/p2p/12D3KooW... \
  --ai-provider ollama
```

---

## 7. Monitoring

### Health Check Endpoint:

```bash
curl https://rpc.yourdomain.com -X POST \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"smithnode_status","params":[],"id":1}'
```

### Prometheus Metrics (TODO):

Coming soon - node will expose `/metrics` endpoint.

---

## Quick Start Checklist

- [ ] Deploy at least 1 public node on VPS
- [ ] Configure SSL with nginx/caddy
- [ ] Deploy web dashboard to Vercel
- [ ] Set `VITE_RPC_URL` environment variable
- [ ] Run AI validators with `--peer` flag pointed at bootstrap
- [ ] Share bootstrap peer addresses with community

---

## FAQ

**Q: Do I need RPC if it's P2P?**
A: Yes, RPC is how clients (web dashboard, wallets) query the blockchain. But each peer can run its own RPC - there's no central server.

**Q: What if the main node goes down?**
A: Other agents continue operating. As long as at least one peer is online, the network survives.

**Q: How do agents find each other?**
A: Via bootstrap peers and mDNS (local network discovery). Add public bootstrap peers for internet-wide connectivity.

**Q: Can I run multiple agents?**
A: Yes! Each validator with its own keypair and ports becomes a full peer. They auto-discover each other on the same network via mDNS.
