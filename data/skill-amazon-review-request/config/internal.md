# Internal — Jarvis Ops Context (gitignored)

## Credentials
- SP-API: ~/amazon-sp-api.json (or SP_API_PATH env)
- Supabase: ~/supabase-api.json (or SUPABASE_API_PATH env)

## Supabase
- Table: review_requests
- Fields: order_id, asin, status, attempted_at, error

## Eligibility
- Orders delivered >5 days, not already in Supabase
- Max window: 30 days (Amazon requirement)
