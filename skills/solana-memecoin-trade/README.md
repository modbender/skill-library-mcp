# Solana Memecoin Guardian v2 (OpenClaw Skill Project)

This is a **TypeScript project skeleton** implementing BOTH:
1) **Selective Copy-Trade Engine** (smart wallet follower)  
2) **AI Self-Analysis Engine** (rule-based signals)

It runs in **paper mode** by default.

## Quick start
```bash
npm install
cp .env.example .env
npm run dev -- --mode paper --minutes 10
```

## What’s implemented in this bundle
✅ Shared Risk Gate (safe-by-default)  
✅ AI Engine (candidate scan + buy in paper mode)  
✅ Copy-Trade Engine (event handler + filters + anti-chase + budget)  
✅ Position Monitor (SL/TP1/TP2/Trailing)  
✅ Rug Alarms (LP drop proxy + impact proxy + holder spike placeholder)  
✅ Risk Budget Split (copy vs AI daily budget)  

## What is still a stub (you must wire)
- Real Pump.fun candidate feed (endpoints change)
- Real smart wallet stream/polling (Helius/Shyft/RPC logs)
- Real on-chain meta (mint/freeze authority + holders distribution)
- Live swap execution (Jupiter / your router)

Paper mode is safe: it will not send transactions.

---
⚠️ Memecoins are extremely risky. Audit everything.
