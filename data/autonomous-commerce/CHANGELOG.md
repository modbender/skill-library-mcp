# Changelog

All notable changes to the Autonomous Commerce skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-11

### Added
- Initial release of Autonomous Commerce skill
- Complete OpenAI Skills format documentation (SKILL.md)
- Amazon.com purchase automation script
- Cryptographic proof generation system
- ClawPay escrow integration
- Security guardrails (pre-saved payment/address only)
- Edge case handling (out of stock, budget exceeded, payment declined)
- Negative examples for proper skill routing
- Templates for order confirmation and proof generation
- Real-world proof: $68.97 Amazon purchase (Feb 6, 2026)
- Delivery confirmation (Feb 9, 2026)
- 5 screenshots of evidence (PII redacted)
- Production-ready package.json and npm scripts

### Proven Capability
- **Date:** Feb 6, 2026
- **Orders:** #114-3614425-6361022, #114-1580758-4713047
- **Amount:** $68.97 (2 orders, 8 items)
- **Proof Hash:** `0x876d4ddfd420463a8361e302e3fb31621836012e6358da87a911e7e667dd0239`
- **Delivery:** Confirmed Feb 9, 2026
- **Status:** SUCCESS

### Security
- Agent uses pre-saved payment methods only
- Agent uses pre-saved shipping addresses only
- Agent CANNOT add new credentials
- Budget caps enforced via escrow
- All purchases logged with proof hashes
- Screenshots captured for verification

## [Unreleased]

### Planned for 1.1.0
- Multi-retailer support (eBay, Walmart, Target)
- International shipping
- Gift purchase capability (separate delivery address)

### Planned for 1.2.0
- Price tracking (buy when price drops)
- Inventory monitoring (buy when back in stock)
- Recurring purchase automation

### Planned for 2.0.0
- Cross-retailer price comparison
- Bulk purchase coordination
- Return/refund automation
- Warranty tracking

---

## Development History

**Feb 6, 2026:** First autonomous purchase executed ($68.97 Amazon)  
**Feb 9, 2026:** Delivery confirmed, capability proven  
**Feb 11, 2026:** Skill packaged in OpenAI Skills format, ready for publication

---

*This is the ONLY agent skill with proven real-world commerce capability.*
