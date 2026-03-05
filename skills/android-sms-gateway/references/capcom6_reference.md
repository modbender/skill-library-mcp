# capcom6/android-sms-gateway Quick Reference

## API Differences from itsmeichigo/SMSGateway

| Feature | itsmeichigo | capcom6 |
|---------|-------------|---------|
| **Auth** | Bearer Token | Basic Auth (user:pass) |
| **Send Endpoint** | `/api/v1/send` | `/message` |
| **Receive** | Poll `/api/v1/messages/received` | Webhooks only |
| **Status** | `/api/v1/status` | No dedicated endpoint |
| **Bulk Send** | Individual calls | Multi-recipient in single call |
| **Encryption** | None documented | E2E encryption |
| **Server Modes** | Local only | Local + Cloud + Private |

## capcom6 API Endpoints

### Local Server
```
Base URL: http://<DEVICE_IP>:8080
```

### Cloud Server
```
Base URL: https://api.sms-gate.app/3rdparty/v1
```

### Send SMS
```bash
curl -X POST http://IP:8080/message \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{
    "textMessage": {"text": "Hello"},
    "phoneNumbers": ["+1234567890"]
  }'
```

### Register Webhook
```bash
curl -X POST http://IP:8080/webhooks \
  -u username:password \
  -H "Content-Type: application/json" \
  -d '{
    "id": "unique-id",
    "url": "https://your-server.com/webhook",
    "event": "sms:received"
  }'
```

### Webhook Payload (Incoming SMS)
```json
{
  "event": "sms:received",
  "payload": {
    "messageId": "msg_12345abcde",
    "message": "Received SMS text",
    "phoneNumber": "+1234567890",
    "simNumber": 1,
    "receivedAt": "2024-06-07T11:41:31.000+07:00"
  }
}
```

## Scripts

| Script | Purpose |
|--------|---------|
| `send_sms_capcom6.sh` | Send single SMS |
| `bulk_sms_capcom6.sh` | Bulk send (use `--multi` for single API call) |
| `register_webhook_capcom6.sh` | Register webhook for incoming SMS |
| `check_status_capcom6.sh` | Check gateway connectivity |

## Configuration

### Environment Variables
```bash
export SMS_GATEWAY_URL="http://192.168.1.100:8080"
export SMS_GATEWAY_USER="username"
export SMS_GATEWAY_PASS="password"
```

### Config File (~/.openclaw/sms-gateway-capcom6.json)
```json
{
  "gateway_url": "http://192.168.1.100:8080",
  "gateway_user": "username",
  "gateway_pass": "password",
  "server_mode": "local"
}
```

## Setup Steps

1. **Install App**
   - Download from: https://github.com/capcom6/android-sms-gateway/releases
   - Install on Android device

2. **Configure App**
   - Open app → Enable Local Server or Cloud Server
   - Note credentials (username/password displayed in app)

3. **Test Connectivity**
   ```bash
   ./scripts/check_status_capcom6.sh
   ```

4. **Send Test SMS**
   ```bash
   ./scripts/send_sms_capcom6.sh --to "+1234567890" --message "Test"
   ```

5. **Setup Webhook (Optional)**
   ```bash
   ./scripts/register_webhook_capcom6.sh --url "https://your-server.com/webhook"
   ```

## Security Best Practices

1. **Use Local Server** when possible (no external dependencies)
2. **Deploy Private Server** for production (https://docs.sms-gate.app/getting-started/private-server/)
3. **Firewall Rules** - Restrict port 8080 to trusted IPs
4. **Strong Credentials** - App generates random credentials by default
5. **HTTPS** - Use private server with TLS for external access
