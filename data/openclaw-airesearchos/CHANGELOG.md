# Changelog

## 1.0.0

Initial release.

- API key authentication (Bearer token, `/api/v1/` endpoints)
- x402 USDC payment authentication (Base mainnet, `/api/x402/` endpoints)
- Research modes: scan ($0.50 / 10 credits), due diligence ($1.50 / 25 credits), mission critical ($5.00 / 100 credits)
- Clarifying questions flow (API key path)
- Polling script with progress reporting
- x402 payment helper with `--max-payment` safety limit
- Credits balance and research history (API key path)
- Full error handling for all API error codes
- Security: credential protection, output sanitization, prompt injection defense
