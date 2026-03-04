# Deployment Guide - Yield Farming Agent

## Local Development

### Option 1: Full Stack (API + Dashboard)
```bash
npm install
npm run dev
```
Visit: http://localhost:3001

### Option 2: Dashboard Only (with local API)
Terminal 1 - API:
```bash
npm run dev
```

Terminal 2 - Dashboard (hot reload):
```bash
npm run dev:dashboard
```

---

## Vercel Deployment

### Prerequisites
- GitHub repo connected to Vercel
- Environment variables configured (if needed)

### Setup Steps

1. **Connect GitHub Repo**
   - Visit https://vercel.com/new
   - Import `https://github.com/open-web-academy/yieldvault-agent-bnb`
   - Vercel auto-detects `vercel.json`

2. **Configure**
   - Root Directory: `/` (auto-detected)
   - Build Command: `cd dashboard && npm install && npm run build` (auto-detected)
   - Output Directory: `dashboard/dist` (auto-detected)

3. **Deploy**
   - Click "Deploy"
   - API routes `/api/*` → `api/logs.js`
   - Static files → `dashboard/dist`

4. **Access Dashboard**
   - URL: `https://your-deployment.vercel.app`
   - API Health: `https://your-deployment.vercel.app/api/health`
   - Logs: `https://your-deployment.vercel.app/api/logs`

---

## Architecture

```
┌─────────────────────────────────────────┐
│   Vercel (Frontend + API)               │
├─────────────────────────────────────────┤
│ Dashboard (React/Vite/TS)               │
│   ↓ fetch('/api/logs')                  │
│ Express API (node api/logs.js)          │
│   ↓ reads execution-log.jsonl           │
│ Execution Log (JSONL)                   │
└─────────────────────────────────────────┘
```

---

## Real-Time Updates

Dashboard polls `/api/logs` every 2 seconds:
- Displays last 10 execution records
- Shows: Timestamp, Vault, Action, State Hash
- Auto-updates as scheduler writes events

---

## Troubleshooting

### "Error connecting to API"
- Check CORS headers (enabled in api/logs.js)
- Verify API endpoint is running
- Check browser console for network errors

### Build fails on Vercel
- Ensure `dashboard/tsconfig.json` has `"jsx": "react-jsx"`
- Check `package.json` dependencies are listed
- View Vercel build logs for details

### No logs appearing
- Verify `execution-log.jsonl` exists in root
- Check scheduler is writing events
- Manually test: `curl http://localhost:3001/api/logs`

---

## Production Checklist

- [ ] Remove `.env` file (use Vercel Secrets)
- [ ] Test API endpoint responds with logs
- [ ] Verify CORS works for cross-origin requests
- [ ] Set `NODE_ENV=production`
- [ ] Monitor Vercel analytics/logs
- [ ] Implement log rotation (prevent unbounded growth)

