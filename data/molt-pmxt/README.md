# Molt PMXT

A specialized toolset for navigating and interacting with prediction markets (Polymarket, Kalshi, etc.) using `pmxtjs`.

## Structure

- `src/index.ts`: Entry point exporting all tools.
- `src/tools.ts`: Core logic for API interactions via `pmxtjs`.
- `src/types.ts`: TypeScript interfaces for consistent data structures.
- `SKILL.md`: Operational guide for AI agents.

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Build the project:
   ```bash
   npx tsc
   ```

3. usage (Example):
   ```typescript
   import { getPolymarketMarkets } from "./src";

   const markets = await getPolymarketMarkets("Trump");
   console.log(markets);
   ```

## Development

- Use `npm run dev` (if configured) or `npx ts-node src/index.ts` for quick testing.
