# Authentication

## API keys
- ElevenLabs uses API keys for authentication.
- Send the key in the `xi-api-key` header on every request.
- Keys can be scoped and quota-limited; treat them as secrets.

## Single-use tokens
- Use single-use tokens when you must call from a client context.
- Tokens are time-limited and reduce key exposure risk.
