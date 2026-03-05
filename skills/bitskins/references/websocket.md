# BitSkins WebSocket API

## Connection

Endpoint: `wss://ws.bitskins.com`

WebSocket can be used to receive real-time updates: balance changes, trade updates, ticket responses, new notifications.

## Authentication

Authorization actions (`WS_AUTH`, `WS_AUTH_APIKEY`, `WS_DEAUTH`) **reset the list of subscribed channels**. If you subscribed to any channel before authenticating, you must subscribe again after authentication.

## Actions

Send JSON messages with these actions:

| Action | Description |
|--------|-------------|
| `WS_AUTH` | Authorize using session token |
| `WS_AUTH_APIKEY` | Authorize using API key |
| `WS_DEAUTH` | Deauthorize session |
| `WS_SUB` | Subscribe to a channel |
| `WS_UNSUB` | Unsubscribe from a channel |
| `WS_UNSUB_ALL` | Unsubscribe from all channels |

### Authorize with API key

```json
{"WS_AUTH_APIKEY": "YOUR_API_KEY"}
```

### Subscribe to a channel

```json
{"WS_SUB": "channel_name"}
```

### Unsubscribe from a channel

```json
{"WS_UNSUB": "channel_name"}
```

### Unsubscribe from all

```json
{"WS_UNSUB_ALL": true}
```

## Channels

| Channel | Description |
|---------|-------------|
| `listed` | New items listed on the market |
| `delisted_or_sold` | Items delisted or sold |
| `price_changed` | Item price changes |
| `extra_info` | Additional item information updates |

## Example: Monitoring new CS2 listings

```javascript
const ws = new WebSocket('wss://ws.bitskins.com');

ws.onopen = () => {
  // Authenticate
  ws.send(JSON.stringify({"WS_AUTH_APIKEY": process.env.BITSKINS_API_KEY}));
  // Subscribe to listings after auth
  setTimeout(() => {
    ws.send(JSON.stringify({"WS_SUB": "listed"}));
  }, 1000);
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```
