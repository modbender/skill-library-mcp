# 🎭 Sideload Avatar Generator

Generate 3D avatars from text prompts or reference images using [Sideload.gg](https://sideload.gg).

**$2 per avatar. Pay-per-use. No API key. No subscription.**

Payment is handled via the [x402 protocol](https://x402.org) — an open standard by Coinbase for HTTP-native payments using USDC on Base. Works with any x402-compatible wallet.

## Output Formats

Every generation produces:
- **GLB** — Universal 3D model (Three.js, Unity, Unreal, web)
- **VRM** — Avatar standard (VRChat, VTubing, [@pixiv/three-vrm](https://github.com/pixiv/three-vrm))
- **MML** — [Metaverse Markup Language](https://mml.io) document for virtual worlds
- **PNG** — Processed reference image

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/DirectiveCreator/sideload-avatar-generator.git
cd sideload-avatar-generator
npm install

# 2. Check the cost
node scripts/generate.js --probe

# 3. Sign an x402 payment with your wallet, then generate!
node scripts/generate.js --prompt "A cyberpunk samurai with glowing red armor" --x402-token <token>
```

## Usage

### From text
```bash
node scripts/generate.js --prompt "An anime sorceress with silver hair and a golden staff" --x402-token <token>
```

### From image
```bash
node scripts/generate.js --image https://example.com/character.png --x402-token <token>
node scripts/generate.js --image ./my-photo.jpg --x402-token <token>
```

### Check cost
```bash
node scripts/generate.js --probe
```

### Check a job
```bash
node scripts/status.js avt-a1b2c3d4
```

### Options

| Flag | Description |
|------|-------------|
| `--prompt "text"` | Text description of the avatar |
| `--image <url-or-path>` | Reference image (URL or local file) |
| `--output <name>` | Custom filename for downloads |
| `--no-download` | Skip downloading result files |
| `--x402-token <token>` | x402 payment token (required for generation) |
| `--probe` | Check cost without generating |

## Rendering with Three.js

Generated VRM avatars work directly with [@pixiv/three-vrm](https://github.com/pixiv/three-vrm):

```javascript
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { VRMLoaderPlugin } from '@pixiv/three-vrm';

const loader = new GLTFLoader();
loader.register((parser) => new VRMLoaderPlugin(parser));

loader.load('https://aiml.sideload.gg/models/avt-xxx.vrm', (gltf) => {
  const vrm = gltf.userData.vrm;
  scene.add(vrm.scene);
});
```

## API

Full API reference: [SIDELOAD-API.md](./SIDELOAD-API.md) | [sideload.gg/agents/raw](https://sideload.gg/agents/raw)

```
POST https://sideload.gg/api/agent/generate
Content-Type: application/json
x-payment: <x402_payment_token>

{ "type": "text", "prompt": "A futuristic robot" }
```

Returns a `jobId` — poll `GET /api/agent/generate/{jobId}/status` until complete.

## x402 Payment

This skill uses [x402](https://x402.org), an open payment protocol by Coinbase:

1. Your request hits the API → gets back `402 Payment Required` with price info
2. Your wallet signs a one-time USDC authorization (locally, key never leaves your machine)
3. Request retries with the signed payment → API delivers the avatar

**No API keys. No accounts. No subscriptions.** Just a wallet with USDC on Base.

Sign a payment with your own wallet and pass it via `--x402-token`. This skill never handles private keys — use any x402-compatible client ([Coinbase x402 SDK](https://github.com/coinbase/x402), [Thirdweb x402](https://portal.thirdweb.com/payments/x402), hardware wallet, etc.).

## Rate Limits

- 10 generations per 30 minutes per wallet
- $2 USDC per generation

## Related

- [awesome-mml](https://github.com/DirectiveCreator/awesome-mml) — Curated MML resources for the metaverse
- [@pixiv/three-vrm](https://github.com/pixiv/three-vrm) — Three.js VRM avatar loader
- [x402 Protocol](https://x402.org) — HTTP-native payments
- [VRM Specification](https://vrm.dev/en/) — 3D avatar standard
- [MML](https://mml.io) — Metaverse Markup Language

## License

MIT
