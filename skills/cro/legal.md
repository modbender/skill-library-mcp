# CRO Legal Compliance

## Dark Patterns — Now Illegal

### EU (Digital Services Act, Article 25)
Since February 2024, explicitly banned:
- Interfaces that deceive or manipulate users
- Aggressive pop-ups and confusing consent buttons
- Confirm-shaming ("No thanks, I don't want to save money")
- Pre-checked boxes for additional services
- Hidden costs revealed at checkout (drip pricing)
- Fake urgency ("Only 2 left!" if false)
- Asymmetric choices (big "Accept" vs tiny "Decline")

**Penalty:** Up to 6% of global annual revenue

### California (CPRA)
Any UI that "subverts or impairs user choice":
- Opting out cannot be harder than opting in
- Must honor Global Privacy Control (GPC) signals
- Asymmetric friction invalidates consent

## A/B Testing & Consent

### Key Rule
Most A/B testing tools use cookies or identifiers = need consent BEFORE running tests in EU.

### What This Means
- Cannot A/B test users who haven't consented
- "Legitimate interest" does NOT cover analytics cookies
- The cookie banner itself CAN be A/B tested, but ALL variants must provide valid consent

### Valid Consent Requirements (All Variants)
1. Freely given (no coercion)
2. Specific (know what they're consenting to)
3. Informed (clear language)
4. Unambiguous (explicit action)

### Testing Without Consent
Only possible with:
- Truly anonymized data (no identifiers)
- Server-side testing without cookies
- First-party random assignment (no persistence)

## Price Display (EU Omnibus Directive)

### Requirements
- Show total price including taxes upfront
- No drip pricing (fees revealed at checkout)
- Price reduction claims must reference lowest price in prior 30 days

### Examples
❌ "Was €100, now €50" (if never actually sold at €100)
❌ Showing €50 then adding €15 "service fee" at checkout
✅ "€50" with all fees included from start
✅ "Was €80 (30-day low), now €50" with real history

## Testimonials (FTC Endorsement Guides)

### Requirements
- Must reflect genuine, recent experience
- Atypical results need disclaimer about typical outcomes
- Material connections must be disclosed (paid, gifted)
- Cannot cherry-pick only positive reviews

### Disclosure Examples
- "Sponsored", "Paid partnership", "Gifted product"
- Clear and conspicuous (not in tiny footer text)

## Personalization & GDPR

### When Personalizing Prices/Content
- Need legal basis: consent OR legitimate interest
- Must disclose when prices are personalized
- Users have right to opt out of profiling

### Legitimate Interest Requirements
1. Documented balancing test
2. User can reasonably expect it
3. Impact on user is proportionate
4. Easy opt-out available

## Urgency & Scarcity Rules

### What's Illegal
- Countdown timers that reset
- "Limited stock" claims that are false
- Inventory numbers that don't reflect reality
- "X people viewing this" if fabricated

### What's Allowed
- Real inventory counts (if accurate)
- Genuine sale end dates
- True "last chance" offers

## Compliance Checklist

Before launching any CRO change:
- [ ] Does it manipulate or deceive? → Remove
- [ ] Does it require consent? → Check banner covers it
- [ ] Are price claims accurate? → Verify with 30-day data
- [ ] Are testimonials real? → Check documentation
- [ ] Is urgency genuine? → Verify inventory/dates
- [ ] Can users easily undo/opt-out? → Test the reverse flow

## Documentation Requirements (GDPR Accountability)

Keep records of:
- Why each CRO change was made
- What data it uses
- Legal basis for processing
- Results of balancing tests (for legitimate interest)
- Test results and decisions
