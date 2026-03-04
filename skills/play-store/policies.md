# Policy Compliance — Play Store

## High-Risk Policy Areas

### Deceptive Behavior
**Violations:**
- Misleading claims about functionality
- Hidden charges or subscription traps
- Fake reviews or ratings manipulation
- Impersonating another app or company

**Consequences:** Immediate removal, potential developer ban.

### User Data
**Requirements:**
- Privacy policy URL required
- Disclose all data collection in Data Safety section
- Secure transmission (HTTPS)
- Allow account deletion if accounts exist
- No selling personal data

**Data Safety Section:**
- Must be accurate and complete
- Update when data practices change
- Covers collection, sharing, security

### Restricted Content

| Content Type | Rule |
|--------------|------|
| Sexual content | No nudity, no sexual services |
| Violence | ESRB T equivalent max without warnings |
| Hate speech | Zero tolerance |
| Gambling | Licensed regions only |
| Alcohol/drugs | Age-gating required |
| Firearms | Restricted, no sales facilitation |

### Intellectual Property
- No copyrighted assets without license
- No trademark infringement
- No celebrity likeness without consent
- No impersonation

## Technical Requirements

### Current Requirements (2024+)
| Requirement | Details |
|-------------|---------|
| Target API | 33+ for new apps, 31+ for updates |
| 64-bit | Required for all apps |
| App bundle | AAB format required |
| Billing | Play Billing for digital goods |
| Permissions | Justify all dangerous permissions |

### Permission Best Practices
- Request at point of use, not on install
- Explain why before system dialog
- Graceful degradation if denied
- Never block core functionality for optional permissions

## Review Process

### Timeline
| Track | Typical Review |
|-------|----------------|
| Internal | Immediate |
| Closed testing | Hours to 1 day |
| Open testing | Hours to 1 day |
| Production (new) | 1-7 days |
| Production (update) | Hours to 3 days |

### Common Rejection Reasons
1. Missing privacy policy
2. Insufficient app functionality
3. Misleading metadata
4. Crashes on common devices
5. Broken core features
6. Policy violations in description

### Appeal Process
1. Read rejection reason carefully
2. Fix the specific issue cited
3. Submit appeal with explanation
4. Wait up to 7 days
5. Escalate if needed (Play Console Help)

## Account Health

### Metrics That Matter
| Metric | Threshold | Consequence |
|--------|-----------|-------------|
| Crash rate | >1.09% | Warning |
| ANR rate | >0.47% | Warning |
| Policy strikes | 3 | Account termination |
| Bad behavior | Pattern | Ban |

### Maintaining Good Standing
- Respond to policy emails promptly
- Fix violations within deadline
- Don't repeat same violation
- Monitor vitals dashboard weekly
