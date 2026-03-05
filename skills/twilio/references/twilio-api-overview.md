# Twilio API Overview

## 1) Base URL
- Twilio REST API base: `https://api.twilio.com/2010-04-01`
- Served over HTTPS only.

## 2) Authentication
- HTTP Basic auth with API Key + Secret (recommended for production).
- Account SID + Auth Token can be used for local testing.

## 3) Core surfaces (common)
- Messaging (SMS/MMS, WhatsApp via Messaging API)
- Voice (Calls API)
- Conversations (omni-channel threads)
- Verify (OTP/verification)
- SendGrid (email, separate API domain)
