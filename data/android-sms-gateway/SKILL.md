---
name: android-sms-gateway
description: Self-hosted SMS via Android phone HTTP API. Use when you need to send/receive SMS messages using an Android device as a gateway. Supports popular SMS Gateway apps (SMS Gateway API, SMSGate, etc.). Ideal for security teams wanting full control without third-party SMS providers.
---

# Android SMS Gateway

Self-hosted SMS gateway using an Android phone with HTTP API integration. Full control, no third-party dependencies.

## Overview

This skill enables sending and receiving SMS messages through an Android phone running an SMS Gateway app. The phone exposes a local HTTP API that this skill uses to send messages and check received messages.

### Supported Apps

#### Primary (Original Scripts)
- **SMS Gateway API** (⭐ Recommended) - https://github.com/itsmeichigo/SMSGateway
- **SMSGate** - https://github.com/iamsmgate/smsgate
- **SMS Forwarder** - https://github.com/pppscn/SmsForwarder

#### capcom6/android-sms-gateway (New Scripts)
- **SMS Gateway for Android** - https://github.com/capcom6/android-sms-gateway
  - ✅ End-to-end encryption
  - ✅ Local + Cloud + Private server modes
  - ✅ Multi-device support
  - ✅ Webhooks for incoming messages
  - ✅ Multi-recipient bulk sends

## Quick Start

### Prerequisites

1. Android phone with SMS capability
2. Install SMS Gateway app on the phone
3. Phone and OpenClaw host on same network (or port forwarding)
4. Configure app with API access enabled

### Setup (Once)

```bash
# 1. Install SMS Gateway API app on Android
# Download from: https://github.com/itsmeichigo/SMSGateway/releases

# 2. Configure the app:
# - Enable HTTP API server
# - Set API token/password
# - Note the phone's IP address and port (default: 8080)

# 3. Test connectivity
curl http://PHONE_IP:8080/api/v1/status -H "Authorization: Bearer YOUR_TOKEN"

# 4. Save configuration to TOOLS.md (see Configuration section)
```

## Commands

### Send SMS

```bash
# Basic send
./scripts/send_sms.sh --to "+1234567890" --message "Hello from OpenClaw"

# With config file
./scripts/send_sms.sh --config ~/.openclaw/sms-gateway.json \
  --to "+1234567890" \
  --message "Alert: Security scan complete"

# Via environment variables
export SMS_GATEWAY_URL="http://192.168.1.100:8080"
export SMS_GATEWAY_TOKEN="your-api-token"
./scripts/send_sms.sh --to "+1234567890" --message "Test message"
```

### Check Received Messages

```bash
# List recent received messages
./scripts/receive_sms.sh --limit 10

# Check for new messages since timestamp
./scripts/receive_sms.sh --since "2026-02-22T00:00:00Z"
```

### Check Gateway Status

```bash
# Verify gateway is online
./scripts/check_status.sh
```

### Bulk SMS

```bash
# Send to multiple recipients
./scripts/bulk_sms.sh --recipients "+1234567890,+0987654321" --message "Broadcast message"

# From file (one number per line)
./scripts/bulk_sms.sh --recipients-file ./contacts.txt --message "Alert"
```

## Configuration

### Option 1: Environment Variables

```bash
export SMS_GATEWAY_URL="http://192.168.1.100:8080"
export SMS_GATEWAY_TOKEN="your-api-token"
export SMS_GATEWAY_TIMEOUT="30"
```

### Option 2: Config File

Create `~/.openclaw/sms-gateway.json`:

```json
{
  "gateway_url": "http://192.168.1.100:8080",
  "api_token": "your-api-token",
  "timeout_seconds": 30,
  "default_sender": "+1234567890",
  "retry_count": 3
}
```

### Option 3: Command Line Args

All scripts support `--url` and `--token` flags:

```bash
./scripts/send_sms.sh --url "http://192.168.1.100:8080" --token "token" --to "+1234567890" --message "Hi"
```

---

## capcom6/android-sms-gateway Configuration

### Environment Variables

```bash
export SMS_GATEWAY_URL="http://192.168.1.100:8080"  # Local server
# export SMS_GATEWAY_URL="https://api.sms-gate.app/3rdparty/v1"  # Cloud
export SMS_GATEWAY_USER="your-username"
export SMS_GATEWAY_PASS="your-password"
export SMS_GATEWAY_TIMEOUT="30"
```

### Config File

Create `~/.openclaw/sms-gateway-capcom6.json`:

```json
{
  "gateway_url": "http://192.168.1.100:8080",
  "gateway_user": "your-username",
  "gateway_pass": "your-password",
  "server_mode": "local",
  "timeout_seconds": 30
}
```

### Usage Examples

```bash
# Send SMS
./scripts/send_sms_capcom6.sh --to "+1234567890" --message "Hello"

# Cloud mode
./scripts/send_sms_capcom6.sh --mode cloud --to "+1234567890" --message "Hello"

# Register webhook for incoming SMS
./scripts/register_webhook_capcom6.sh --url "https://your-server.com/webhook"

# Bulk send (multi-recipient in single API call)
./scripts/bulk_sms_capcom6.sh --multi --recipients "+1234567890,+0987654321" --message "Alert"

# Check status
./scripts/check_status_capcom6.sh
```

### Save to TOOLS.md

Add your configuration to `TOOLS.md` for reference:

```markdown
### Android SMS Gateway

- **App:** SMS Gateway API (itsmeichigo/SMSGateway)
- **Phone:** Samsung Galaxy, IP: 192.168.1.100
- **Port:** 8080
- **Token:** Stored in ~/.openclaw/sms-gateway.json (chmod 600)
```

## API Reference

See [references/api_reference.md](references/api_reference.md) for detailed API endpoints for each supported app.

## Security Considerations

### Network Security

- **LAN only:** Keep gateway on local network when possible
- **Firewall:** Restrict access to gateway port
- **HTTPS:** Use HTTPS if exposing externally (requires app support)
- **VPN:** Use VPN for remote access instead of port forwarding

### capcom6-Specific Security

| Feature | Benefit |
|---------|---------|
| **E2E Encryption** | Message content encrypted before API transit |
| **Private Server** | Deploy your own backend (no cloud dependency) |
| **Basic Auth** | Standard HTTP authentication |
| **Webhooks** | Incoming messages pushed directly from device |

**Recommendation:** Use capcom6's private server mode for maximum security:
https://docs.sms-gate.app/getting-started/private-server/

### Authentication

- **Strong tokens:** Use random API tokens (32+ chars)
- **Token rotation:** Rotate tokens periodically
- **File permissions:** `chmod 600 ~/.openclaw/sms-gateway.json`

### Rate Limiting

- **Avoid spam:** Implement sending limits in your workflows
- **Carrier limits:** Respect SMS carrier rate limits (~1 msg/sec)
- **Queue system:** Use queue for bulk sends

## Troubleshooting

### Gateway Not Responding

```bash
# Check phone connectivity
ping PHONE_IP

# Check API endpoint
curl -v http://PHONE_IP:8080/api/v1/status

# Check app is running (on phone)
# - Open SMS Gateway app
# - Verify server is started
# - Check logs in app
```

### Authentication Failed

```bash
# Verify token
curl -v http://PHONE_IP:8080/api/v1/status -H "Authorization: Bearer YOUR_TOKEN"

# Check token format (some apps use different auth headers)
# See references/api_reference.md for app-specific auth
```

### Message Not Sent

```bash
# Check phone signal
# Check SMS balance/plan
# Check app logs
# Verify recipient number format (include country code)
```

## Usage Examples

### Security Alert System

```bash
# Send alert when scan detects issues
./scripts/send_sms.sh --to "+1234567890" \
  --message "🛡️ ALERT: Vulnerability found on 192.168.1.50"
```

### Two-Factor Auth Codes

```bash
# Send 2FA code (integrate with your auth system)
CODE=$(openssl rand -base64 6 | tr -d '/+=' | head -c 6)
./scripts/send_sms.sh --to "$USER_PHONE" \
  --message "Your verification code: $CODE"
```

### Scheduled Reminders

```bash
# Cron job for daily security reminder
# crontab -e
0 9 * * * /path/to/send_sms.sh --to "+1234567890" --message "Daily security check: Review logs"
```

### Monitoring Integration

```bash
# Nagios/Zabbix alert script
#!/bin/bash
STATUS=$1
if [ "$STATUS" != "OK" ]; then
  ./scripts/send_sms.sh --to "+1234567890" --message "MONITOR ALERT: $STATUS"
fi
```

## Scripts

### Original (itsmeichigo/SMSGateway)

- `scripts/send_sms.sh` - Send single SMS
- `scripts/receive_sms.sh` - Fetch received messages
- `scripts/check_status.sh` - Check gateway health
- `scripts/bulk_sms.sh` - Send to multiple recipients

### capcom6/android-sms-gateway

- `scripts/send_sms_capcom6.sh` - Send single SMS
- `scripts/register_webhook_capcom6.sh` - Register webhook for incoming SMS
- `scripts/check_status_capcom6.sh` - Check gateway health
- `scripts/bulk_sms_capcom6.sh` - Send to multiple recipients (supports multi-recipient API)

## References

- [API Reference](references/api_reference.md) - Detailed API docs for each app
- [SMS Gateway API](https://github.com/itsmeichigo/SMSGateway) - Primary supported app
- [SMSGate](https://github.com/iamsmgate/smsgate) - Alternative app
- [SMS Forwarder](https://github.com/pppscn/SmsForwarder) - Alternative with forwarding

## Notes

- **Message encoding:** Scripts handle UTF-8 for international characters
- **Long messages:** Automatically split for messages > 160 chars (GSM) or > 70 chars (Unicode)
- **Delivery reports:** Some apps support delivery callbacks (see api_reference.md)
- **Dual SIM:** Specify SIM slot if phone has dual SIM (app-dependent)
