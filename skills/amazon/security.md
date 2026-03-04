# Security Protocols

## Credential Handling

**Storage rules:**
- NEVER store Amazon password in agent memory
- Use OS keychain/secrets manager for any stored credentials
- Session tokens expire — don't persist indefinitely
- 2FA codes are one-time — never cache

**Authentication flow:**
- Agent initiates login context
- Human enters credentials directly to Amazon
- Agent receives session (not credentials)
- Session has limited scope and duration

## Payment Security

**Before any purchase:**
- Display full total including tax/shipping
- Show payment method to be charged
- Confirm shipping address
- Wait for explicit human approval

**Never automate:**
- Adding new payment methods
- Changing default payment
- One-click purchases (too risky)
- Gift card redemption

**Red flags to catch:**
- Price significantly different from expected
- Unusual shipping address
- High-value purchase from new seller
- Multiple orders in short period

## Account Protection

**Monitor for:**
- Unrecognized devices in security settings
- Failed login attempts
- Order confirmation for things not ordered
- Address changes not initiated by user

**If compromise suspected:**
- Change password immediately
- Review and end all sessions
- Check for unauthorized orders
- Enable/verify 2FA

## Automation Safety

**Rate limiting:**
- Don't hammer Amazon with requests
- Implement exponential backoff on errors
- Spread operations across time

**Session management:**
- Respect session timeouts
- Re-authenticate cleanly when expired
- Don't force session extension

**Seller account specifics:**
- Higher security — linked to bank accounts
- More aggressive bot detection
- API keys where available (Product Advertising API, SP-API)

## Data Protection

**Don't store:**
- Full credit card numbers
- Amazon account passwords
- Social security / tax IDs
- Bank routing numbers

**OK to store:**
- Order history summaries
- Product watchlists (ASINs)
- Price history data
- Non-sensitive preferences

## Phishing Awareness

**Common Amazon phishing patterns:**
- "Your order couldn't be shipped"
- "Account locked — verify now"
- "You won a prize"
- "Unusual sign-in detected" (ironic)

**Always verify:**
- Check sender domain carefully
- Don't click links — go to Amazon directly
- Amazon never asks for password via email
- When in doubt, check order history directly
