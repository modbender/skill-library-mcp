# PCI Compliance & Data Security

## What the Agent NEVER Handles
- Credit/debit card numbers (PAN)
- CVV/CVC security codes
- Social Security Numbers (SSN)
- Bank account or routing numbers
- Tax ID / EIN (collected via secure AGMS form only)
- Raw card expiration dates

## What the Agent CAN Handle
- Vault tokens (opaque IDs like `2017013276`)
- Transaction IDs
- Customer names and emails
- Payment amounts and descriptions
- Business name, contact info (for lead capture only)

## How Card Data is Protected
1. **Tokenization**: Cards are stored in the gateway's PCI-compliant vault. The agent only sees vault token IDs.
2. **Hosted Payment Pages**: Invoice/payment links redirect customers to a secure hosted payment form. Card data never touches our servers.
3. **Encryption at Rest**: Gateway API keys are encrypted with AES-256-GCM before storage.
4. **TLS in Transit**: All API calls use HTTPS. The proxy enforces TLS.

## Onboarding Security
- Sensitive merchant data (SSN, Tax ID, banking) is collected ONLY through the secure AGMS application form at `https://agms.com/get-started/`
- The agent collects basic lead info only (name, email, phone, business type)
- The AGMS form uses HTTPS, reCAPTCHA, and PCI DSS compliant infrastructure

## Rate Limiting
- 60 requests/min global
- 5 requests/min on authentication endpoints
- Prevents brute force and abuse
