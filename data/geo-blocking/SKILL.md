---
name: Geo-Blocking Skills
description: Skills for geographic restrictions and regional compliance.
---

# Geo-Blocking Skills

Skills for geographic restrictions and regional compliance.

## Essential Skills

### 1. Geo Shield
**Skill ID**: `geo-shield`

**Purpose**: Country-based content filtering and compliance

**Features**:
- IP geolocation
- VPN/proxy detection
- Tor exit node detection
- Regional law compliance (GDPR, local censorship)
- Custom geo-rules

**Installation**:
```bash
npm install @clawhub/geo-shield
```

**Use Cases**:
- GDPR compliance (EU)
- Local content laws (Germany hate speech, etc.)
- Regional restrictions
- Government mandates

**Examples**:
- EU: Block sites without GDPR compliance
- Germany: Stricter hate speech rules
- China: Government-mandated blocks
- Australia: Extreme violence filtering

---

*For parental controls, see [PARENTAL_CONTROLS.md](PARENTAL_CONTROLS.md).*
