---
name: open-wallet
description: Use https://tx.steer.fun to have a user execute a wallet action (send a transaction or sign a message) with their own wallet via a shareable URL. Use when an agent needs the user to approve/execute a JSON-RPC request (e.g. eth_sendTransaction, personal_sign, eth_signTypedData_v4, wallet_sendCalls) and return the result (tx hash/signature) back to the agent, optionally via redirect_url.
---

# Open Wallet (tx.steer.fun)

Generate a link the user opens in their browser. The page shows the request, prompts them to connect their wallet, switches to the requested chainId, then executes the JSON-RPC request.

## Build The Link

Base URL:

`https://tx.steer.fun/`

Query params:

- `method`: JSON-RPC method name.
- `chainId`: integer chain id to execute on (the app will switch chains before execution).
- `params`: URL-encoded JSON (either an object or an array).
- `redirect_url` (optional): where to redirect after success/failure with the result.

redirect_url modes:

- Default: the app appends `resultType`/`result` (or `error`) query params to `redirect_url`.
- Template mode: if `redirect_url` contains `{{...}}`, the app replaces placeholders instead of appending query params.

Notes:

- If `params` is a JSON array, it is treated as the exact JSON-RPC `params` array.
- If `params` is a JSON object, the app will map it to common method shapes (e.g. fill `from` from the connected wallet when possible).
- Avoid double-encoding: `params` should be encoded exactly once (e.g. `encodeURIComponent(JSON.stringify(params))`). If you see `%2522` in the URL, it was encoded twice.

## Common Flows

### Sign A Message (personal_sign)

Use a JSON object:

```text
https://tx.steer.fun/?method=personal_sign&chainId=1&params=%7B%22message%22%3A%22hello%22%7D
```

Expected result: signature string.

### Send A Transaction (eth_sendTransaction)

Use a JSON object (the app will set `from` from the connected wallet if omitted):

```text
https://tx.steer.fun/?method=eth_sendTransaction&chainId=1&params=%7B%22to%22%3A%220x4c5Ce72478D6Ce160cb31Dd25fe6a15DC269592D%22%2C%22data%22%3A%220xd09de08a%22%7D
```

Expected result: tx hash.

### Typed Data Sign (eth_signTypedData_v4)

Provide `{ address, typedData }`:

```text
https://tx.steer.fun/?method=eth_signTypedData_v4&chainId=1&params=%7B%22address%22%3A%220xYourAddress%22%2C%22typedData%22%3A%7B%22types%22%3A%7B%7D%2C%22domain%22%3A%7B%7D%2C%22primaryType%22%3A%22%22%2C%22message%22%3A%7B%7D%7D%7D
```

Expected result: signature string.

### Batch Calls (wallet_sendCalls)

Provide `{ calls: [{ to, data }, ...] }` (and optionally `from`):

```text
https://tx.steer.fun/?method=wallet_sendCalls&chainId=1&params=%7B%22calls%22%3A%5B%7B%22to%22%3A%220x0000000000000000000000000000000000000000%22%2C%22data%22%3A%220x%22%7D%5D%7D
```

Expected result: wallet-dependent (often an id or tx hash).

## Getting The Result Back

### Option A: No redirect_url (manual copy)

If you omit `redirect_url`, the page shows a copyable response (or error) after execution.

In your message to the user, ask them to paste back:

- the tx hash / signature string, or
- the full JSON response (if it returns an object).

### Option B: redirect_url (automatic return)

If you include `redirect_url`, the app redirects after success or failure.

It appends query params (default mode):

- On success:
  - `resultType=string` and `result=<value>` OR
  - `resultType=json` and `result=<JSON.stringify(value)>`
- On failure:
  - `error=<message>`

Template mode (no bridge, good for messaging apps):

- If `redirect_url` contains `{{...}}`, placeholders are replaced and no query params are appended.
- Placeholders:
  - `{{result}}`: URL-encoded result string (or URL-encoded `JSON.stringify(result)`)
  - `{{result_raw}}`: unencoded result string (or `JSON.stringify(result)`)
  - `{{resultType}}`: `string` or `json`
  - `{{error}}`: URL-encoded error message
  - `{{error_raw}}`: unencoded error message

Implementation note for agents:

- Consider generating a “compose draft” deep link into your chat with the user and using that as `redirect_url` so, after approval, the user lands in a pre-filled message back to you containing the result.

Example (Telegram share):

Note: Telegram's share endpoint works best when you include both `url=` and `text=`. If you omit `url=`, it may redirect to telegram.org instead of showing the share UI.

```text
https://tx.steer.fun/?method=personal_sign&chainId=1&params=%7B%22message%22%3A%22hello%22%7D&redirect_url=https%3A%2F%2Ft.me%2Fshare%2Furl%3Furl%3Dhttps%253A%252F%252Ftx.steer.fun%252F%26text%3DSignature%253A%2520%7B%7Bresult%7D%7D
```

## Safety Checks

- Always show the user what the request does in plain language (what contract, what function, what chain, what value) before asking them to open the link.
- Prefer least-privilege requests; avoid requesting permissions you do not need.
