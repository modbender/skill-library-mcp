Deploy (Vercel)

1) Create a new Git repo and copy this folder contents into it.
2) In Vercel Project Settings → Environment Variables, set:
   - DATABASE_URL (Supabase Transaction Pooler connection string)
   - COST_CENTS_PER_CALL=25
   - FEE_BPS=250
   - FEE_ETH_ADDRESS=...
   - FEE_BTC_ADDRESS=...
   - WEBHOOK_SHARED_SECRET=... (demo provider)
   - COINBASE_COMMERCE_WEBHOOK_SECRET=...
   - BTCPAY_WEBHOOK_SECRET=...
   - ADMIN_TOKEN=...
3) Deploy.
4) Point api.vms0.com to the Vercel project domain (CNAME).

Routes (public):
- /health
- /v1/balance (GET)
- /v1/transform/:name (POST)
- /v1/payments/webhook/:provider (POST)
- /v1/admin/create-key (POST)
- /v1/admin/stats (GET)

(Internally implemented as Next.js API routes under /api/* via rewrites.)
