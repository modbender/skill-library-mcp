---
name: Parental Controls Skills
description: Skills for parent/guardian management and monitoring.
---

# Parental Controls Skills

Skills for parent/guardian management and monitoring.

## Essential Skills

### 1. Parent Portal
**Skill ID**: `parent-portal`

**Purpose**: Guardian interface for monitoring and configuration

**Features**:
- Weekly activity reports
- Real-time alerts (high-risk content)
- Settings lock (PIN protection)
- Screen time management
- Content review dashboard
- Whitelist/blacklist management

**Installation**: Download from ClawHub

**Configuration**:
```javascript
{
  "skill": "parent-portal",
  "settings": {
    "pinProtection": true,
    "weeklyReports": true,
    "realTimeAlerts": true,
    "categories": ["csam", "self-harm", "high-nsfw"],
    "alertEmail": "parent@example.com"
  }
}
```

**Features**:
- **Activity Dashboard**: See what was blocked and when
- **PIN Lock**: Children can't disable protection
- **Reports**: Weekly summary emails (opt-in)
- **Alerts**: Immediate notification for critical content

**Use Cases**:
- Family internet safety
- School monitoring (with consent)
- Child protection

---

*For complete skill index, see [RECOMMENDED_SKILLS.md](../RECOMMENDED_SKILLS.md).*
