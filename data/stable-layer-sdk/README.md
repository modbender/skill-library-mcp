# Stable Layer SDK

TypeScript SDK for minting, burning stablecoins and claiming yield rewards on the Sui blockchain via the Stable Layer protocol.

## Installation

```bash
npx clawhub install stable-layer-sdk
```

## Quick Start

```typescript
import { StableLayerClient } from "stable-layer-sdk";

const client = new StableLayerClient({
  network: "mainnet",
  sender: "0xYOUR_ADDRESS",
});
```

## License

MIT
