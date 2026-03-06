---
name: Age Verification Skills
description: Skills for age verification and age-appropriate content filtering.
---

# Age Verification Skills

Skills for age verification and age-appropriate content filtering.

## Essential Skills

### 1. Age Guard
**Skill ID**: `age-guard`

**Purpose**: Verify user age and enforce age restrictions

**Features**:
- Document verification (ID, passport)
- Face-based age estimation
- Third-party verification (Yoti, Jumio)
- Age gate UI components
- Parental consent workflows

**Installation**:
```bash
npm install @clawhub/age-guard
```

**Methods**:
1. **Self-reported**: Honor system (basic)
2. **Document verification**: ID scanning
3. **Face estimation**: Computer vision
4. **Third-party**: Yoti, Jumio APIs
5. **Parental PIN**: For children

**Use Cases**:
- COPPA compliance (children < 13)
- Age-restricted content
- Parental control enforcement

---

*For geo-blocking, see [GEO_BLOCKING.md](GEO_BLOCKING.md).*
