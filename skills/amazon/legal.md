# Legal & Compliance

## Amazon Terms of Service — Key Restrictions

**Prohibited automation:**
- Bots that click/interact as if human without disclosure
- Automated purchasing without proper auth flow
- Scraping at scale without API license
- Circumventing CAPTCHAs or bot detection

**Gray areas (proceed with caution):**
- Price monitoring (ok at reasonable rate)
- Review aggregation (public data, rate-limited)
- Wishlist management (personal account only)

**Explicitly allowed:**
- Using Product Advertising API (with credentials)
- SP-API for sellers (with seller credentials)
- Affiliate link generation (Associates program)
- Manual operations assisted by AI

## Affiliate Compliance

**FTC requirements:**
- Clear, conspicuous disclosure
- Before consumer interacts with links
- "Material connection" must be stated

**Amazon Associates Operating Agreement:**
- No links in email/SMS/offline materials
- No misleading claims about products
- No fake urgency ("only 2 left!" if not true)
- No price claims (prices change without notice)

**Consequences of violation:**
- Commission clawback
- Account termination
- Ban from program (permanent)

## Seller Compliance

**Restricted activities:**
- Review manipulation (asking for positive reviews)
- Fake orders to inflate sales rank
- Keyword stuffing with competitor brands
- Buying own products for reviews

**Intellectual property:**
- Don't use trademarked terms unless authorized
- Images must be owned or licensed
- No copying competitor listing content

**Account health:**
- Policy violations accumulate
- Account suspension can be permanent
- Appeals process exists but difficult

## Data & Privacy

**User data handling:**
- Don't collect more than needed
- Secure storage required
- GDPR/CCPA compliance if applicable
- No selling/sharing purchase history

**API terms:**
- Data from APIs has usage restrictions
- Can't build competing product database
- Attribution required in some cases

## Jurisdictional Differences

**US (amazon.com):**
- FTC guidelines apply
- State tax nexus considerations
- CCPA for California users

**EU (amazon.de, .fr, .co.uk, etc.):**
- GDPR consent requirements
- VAT handling for sellers
- Different affiliate commission structures
- Cookie consent requirements

**Best practice:**
- Default to strictest jurisdiction rules
- Localize disclosures by market
- Consult local regs for selling

## Safe Automation Patterns

**Do:**
- Use official APIs when available
- Implement rate limiting
- Log all automated actions
- Require human confirmation for transactions

**Don't:**
- Impersonate human browsing
- Scale beyond personal use without APIs
- Automate anything TOS explicitly prohibits
- Store credentials in code or plain text
