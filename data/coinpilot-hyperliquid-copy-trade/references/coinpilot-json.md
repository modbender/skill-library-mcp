## coinpilot.json format

By default, the CLI reads credentials from `tmp/coinpilot.json` (or `COINPILOT_CONFIG_PATH` if set):

```
{
  "apiKey": "EXPERIMENTAL_API_KEY",
  "apiBaseUrl": "https://api.coinpilot.bot",
  "userId": "did:privy:...",
  "wallets": [
    {
      "index": 0,
      "address": "0x...",
      "privateKey": "0x...",
      "isPrimary": true
    },
    {
      "index": 1,
      "address": "0x...",
      "privateKey": "0x...",
      "isPrimary": false
    }
  ]
}
```

Rules:

- Exactly one primary wallet (`isPrimary: true`) and it must be `index: 0`.
- Include between 2 and 10 wallets total: 1 primary + 1-9 subwallets.
- Subwallets must use unique indexes in the range `1-9`.
- `apiBaseUrl` is optional. When provided, it overrides the default Coinpilot API base URL and must include the scheme (e.g. `https://`).
