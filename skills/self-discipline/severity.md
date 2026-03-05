# Severity Assessment — Self Discipline

How to determine the severity of an incident.

## Quick Assessment Matrix

| Signal | Points |
|--------|--------|
| User uses "never" or "always" | +2 |
| User asks "why did you..." | +1 |
| User expresses frustration | +1 |
| User mentions consequences | +2 |
| This has happened before | +2 |
| Involves external system (prod, API) | +2 |
| Involves security/credentials | → CRITICAL |
| Involves data loss | → CRITICAL |
| Involves money/billing | → CRITICAL |

**Score:**
- 1-2: 🟢 LOW
- 3-4: 🟡 MEDIUM  
- 5+: 🔴 CRITICAL

## Automatic CRITICAL Triggers

These skip the scoring — automatic CRITICAL:

| Trigger | Why |
|---------|-----|
| Security breach (any) | Cannot be undone |
| Credentials exposed | Requires rotation |
| Production affected | User's users affected |
| Data deleted/corrupted | May be unrecoverable |
| Financial impact | Legal/business consequences |
| Repeat of previous incident | System isn't working |

## Severity Levels Detailed

### 🔴 CRITICAL

**Indicators:**
- User is visibly upset
- Real-world consequences occurred
- Security or data integrity compromised
- Affects user's users/customers
- Would damage trust if repeated

**Required response:**
1. Full root cause analysis
2. Flow verification
3. MANDATORY validator creation
4. User confirmation of fix

### 🟡 MEDIUM

**Indicators:**
- User frustrated but not angry
- Time wasted
- Output was wrong but no permanent harm
- Preference violated repeatedly

**Required response:**
1. Full root cause analysis
2. Flow verification
3. Instruction fix (add/move rule)
4. Optional validator

### 🟢 LOW

**Indicators:**
- User mildly annoyed
- Minor preference violated
- One-time occurrence
- Easy to correct

**Required response:**
1. Log the incident
2. Monitor for recurrence
3. Promote if happens again

## When Uncertain

**Default to one level higher.** It's better to over-respond than under-respond.

If you're unsure whether something is MEDIUM or CRITICAL:
- Treat it as CRITICAL
- Ask the user: "This seems serious — should I create a validator to prevent this?"
- User's response informs future severity assessment
