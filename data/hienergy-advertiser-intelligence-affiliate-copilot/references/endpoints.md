# HiEnergy endpoint reference

Base URL used by client:

- Root: `https://app.hienergy.ai`
- API base path: `/api/v1`

Client methods map to endpoints:

- `get_advertisers` -> `GET /advertisers`
- `get_advertisers_by_domain` -> `GET /advertisers/search_by_domain`
- `get_affiliate_programs` -> `GET /affiliate_programs`
- `find_deals` -> `GET /deals`
- `get_advertiser_details` -> `GET /advertisers/{id}`
- `get_program_details` -> `GET /affiliate_programs/{id}`
- `get_deal_details` -> `GET /deals/{id}`
- `get_transactions` -> `GET /transactions`
- `get_transaction_details` -> `GET /transactions/{id}`
- `get_contacts` -> `GET /contacts`
- `get_contact_details` -> `GET /contacts/{id}`

Auth:

- `X-Api-Key: <HIENERGY_API_KEY>`
- `Content-Type: application/json`

Recommended troubleshooting:

- 401/403: invalid or missing API key
- 404: endpoint path mismatch or API version mismatch
- 429: reduce rate / retry with backoff
- 5xx: transient upstream issue; retry and capture response
