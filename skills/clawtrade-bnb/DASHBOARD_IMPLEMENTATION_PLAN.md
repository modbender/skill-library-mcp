# Yield Farming Agent Dashboard - Implementation Plan

## Overview
Build a real-time visual dashboard for observing agent loop execution: READ → DECIDE → EXECUTE → RECORD

## Architecture

### Event System
- Agent emits structured events to JSONL log file
- Events: `market_snapshot`, `portfolio_snapshot`, `decision`, `execution_record`, `errors`
- Timestamps: UNIX epoch (no fabrication), deterministic key ordering
- Dashboard watches JSONL file for new events and renders in real-time

### Tech Stack
- **Frontend:** Vite + React + TypeScript
- **Dev Server:** Vite dev server (port 5173)
- **File Watching:** Chokidar for JSONL file monitoring
- **State Management:** React hooks (simple, no Redux needed)

## Implementation Steps

1. **Create Dashboard Folder Structure**
   - `/dashboard` - root dashboard app
   - `/dashboard/src` - React + TypeScript source
   - `/dashboard/public` - static assets
   - `/dashboard/vite.config.ts` - Vite configuration
   - `/dashboard/tsconfig.json` - TypeScript config
   - `/dashboard/package.json` - dependencies

2. **Agent Instrumentation (Minimal)**
   - Add `EventEmitter` utility to agent
   - Emit events as JSON with deterministic key ordering
   - Log events to `events.jsonl` (append-only)
   - Keep main agent logic completely unchanged

3. **Event Schema**
   - Deterministic field ordering
   - UNIX timestamps
   - Structured payloads for each event type
   - Schema validation on emit

4. **Dashboard UI Components**
   - **Loop Viewer:** READ → DECIDE → EXECUTE → RECORD pipeline
   - **Vaults Table:** APR, fees, risk, net_apr, pending_rewards
   - **Portfolio Table:** Allocations, balances, shares
   - **Execution Timeline:** Records with JSON inspector
   - **Determinism Panel:** Schema validation, key ordering, string amounts
   - **Errors Panel:** Real-time error/warning display

5. **Development Scripts**
   - `dashboard:dev` - Start Vite dev server + agent
   - `dashboard:build` - Build for production
   - `dashboard:watch` - Watch events.jsonl for changes

6. **Testing**
   - Verify events.jsonl is properly formatted
   - Test real-time file watching
   - Verify hash computation matches
   - Check determinism panel validations

## File Tree Structure

```
yield-farming-agent/
├── index.js (agent logic - UNCHANGED)
├── events.js (NEW - event emission)
├── events.jsonl (NEW - appended by agent)
├── package.json (UPDATED - add dashboard scripts)
├── dashboard/ (NEW)
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── App.css
│   │   ├── components/
│   │   │   ├── LoopViewer.tsx
│   │   │   ├── VaultsTable.tsx
│   │   │   ├── PortfolioTable.tsx
│   │   │   ├── ExecutionTimeline.tsx
│   │   │   ├── JSONInspector.tsx
│   │   │   ├── DeterminismPanel.tsx
│   │   │   └── ErrorsPanel.tsx
│   │   ├── hooks/
│   │   │   └── useEventStream.ts
│   │   ├── types/
│   │   │   └── events.ts
│   │   ├── utils/
│   │   │   ├── validators.ts
│   │   │   └── formatters.ts
│   │   └── styles/
│   │       ├── index.css
│   │       └── components.css
│   └── public/
│       └── favicon.ico
```

## Run Commands

```bash
# Development (agent + dashboard)
npm run dashboard:dev

# Build dashboard for production
npm run dashboard:build

# Run agent only (no dashboard)
npm start

# Test agent (no dashboard)
npm test
```

## Key Features

✅ Real-time event streaming via JSONL  
✅ Deterministic timestamps (UNIX epoch)  
✅ Stable key ordering in all JSON  
✅ String amounts for financial precision  
✅ Hash validation (decision_hash, execution_hash)  
✅ Live pipeline visualization (READ → DECIDE → EXECUTE → RECORD)  
✅ Complete vaults & portfolio visibility  
✅ JSON inspector for detailed record inspection  
✅ Determinism validation panel  
✅ Error/warning real-time alerts  

## Minimal Agent Changes

Only added:
- `events.js` - event emission utility
- Modified agent startup to emit events
- No changes to core decision logic or hashing
- No changes to existing scripts or configs
