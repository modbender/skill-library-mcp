# Policy Compliance — Google Play Store

## Data Safety Section

### Required for ALL Apps

Even if your app collects nothing, you MUST complete the form.

| Question | If You Don't Collect |
|----------|---------------------|
| Does your app collect data? | Select "No" |
| Does your app share data? | Select "No" |
| Security practices | Still complete this |

### Data Types to Declare

| Category | Examples | If Using Analytics SDK |
|----------|----------|----------------------|
| Location | GPS, IP-based | Probably yes |
| Personal info | Name, email, phone | If login exists |
| Financial | Payment, purchase history | If IAP exists |
| Health & fitness | Steps, heart rate | If fitness app |
| Messages | SMS, chat | If messaging |
| Photos/videos | Camera, gallery access | If media app |
| Audio | Mic recordings | If voice features |
| Files | Docs, downloads | If file access |
| App activity | Views, taps, interactions | Almost always yes |
| Device IDs | AAID, IMEI | If analytics |
| Diagnostics | Crash logs, performance | Almost always yes |

### Common SDKs and Their Data

| SDK | Collects |
|-----|----------|
| Firebase Analytics | App activity, device ID, diagnostics |
| Crashlytics | Diagnostics, device info |
| Google Ads | Device ID, app activity |
| Facebook SDK | Device ID, app activity, personal info |
| AppsFlyer | Device ID, app activity |

**Rule:** If you use an SDK, read its data disclosure docs.

## Permissions

### Dangerous Permissions

| Permission | Scrutiny | Required Justification |
|------------|----------|----------------------|
| CAMERA | High | Show camera feature in screenshots |
| LOCATION | High | Core feature, explain in description |
| MICROPHONE | High | Core feature, explain in description |
| CONTACTS | Very High | Rarely approved, must be essential |
| CALL_LOG | Very High | Default dialer apps only |
| SMS | Very High | Default SMS apps only |
| STORAGE | Medium | Scoped storage preferred |
| BODY_SENSORS | High | Health apps with justification |

### Background Location

**Extra requirements:**
- Declaration form with video showing feature
- Must be core to app function
- Prominent in-app disclosure
- User consent before request

**If rejected:** Remove the permission or become a location-focused app.

### Permission Declaration Form

Console → Policy → App content → Permissions

For each sensitive permission:
1. Describe exactly how used
2. Link to feature in app
3. Provide video demonstration
4. Explain why runtime alternatives don't work

## Content Rating

### Questionnaire Topics

| Topic | Truthful Answers |
|-------|-----------------|
| Violence | Mild cartoon, realistic combat, blood |
| Sexual content | Nudity, suggestive, explicit |
| Language | Profanity level |
| Substances | Drugs, alcohol, tobacco |
| Gambling | Real money, simulated |
| User interaction | Chat, sharing, user content |

### Consequences of Underrating

| Issue | Consequence |
|-------|-------------|
| User reports mature content | Review + potential strike |
| Age-restricted content undeclared | App removal |
| COPPA violation (kids) | Legal liability |

### Updating Rating

Required when you add:
- User-generated content
- Chat features
- Mature themes
- Gambling elements

## Target Audience

### Children Apps

If ANY appeal to children under 13:

| Requirement | Details |
|-------------|---------|
| Families Policy | Strict ad rules apply |
| Teacher Approved | Optional certification |
| Content restrictions | No mature themes |
| Behavioral targeting | Prohibited |
| Personal data | Minimal, with consent |

### Safe Declaration

If NOT targeting children:
- Console → App content → Target audience
- Select "Not designed for children"
- Don't use child-appealing elements

## API Requirements

### Target SDK (2024)

| Deadline | Requirement |
|----------|-------------|
| Aug 2024 | API 34 for new apps |
| Nov 2024 | API 34 for updates |

### Deprecated APIs

| API | Status | Alternative |
|-----|--------|-------------|
| MANAGE_EXTERNAL_STORAGE | Restricted | Scoped storage, SAF |
| REQUEST_INSTALL_PACKAGES | Restricted | Play Feature Delivery |
| QUERY_ALL_PACKAGES | Restricted | Declare specific packages |
| Non-SDK interfaces | Blocked | Use public APIs |

## Advertising Policies

### Interstitial Ads

| Rule | Requirement |
|------|-------------|
| Close button | Visible within 5 seconds |
| Timing | Not during app loading |
| Frequency | Cannot impair usability |
| After IAP | Prohibited |
| Lock screen | Prohibited |

### Rewarded Ads

| Rule | Requirement |
|------|-------------|
| User consent | Must be opt-in |
| Clear exchange | Show what user gets |
| Delivery | Must deliver reward |

### Deceptive Ads

**Prohibited:**
- Fake system alerts
- Fake close buttons
- Auto-redirects
- Ads mimicking app UI

**Consequence:** Strike or suspension

## Account Standing

### Warning Levels

| Level | Impact | Recovery |
|-------|--------|----------|
| Warning | Notice only | Acknowledge |
| Strike | Feature restrictions | Time-based decay |
| Suspension | App removed | Appeal |
| Termination | Account closed | Nearly impossible |

### Strike Triggers

| Violation | Severity |
|-----------|----------|
| Policy violation (first) | Warning or strike |
| Repeat violation | Strike |
| Malware | Immediate suspension |
| Deceptive behavior | Strike or suspension |
| Impersonation | Suspension |
| Illegal content | Termination |

### Maintaining Standing

1. Respond to policy emails within 7 days
2. Never create accounts to evade enforcement
3. Fix issues before escalation
4. Use Policy Center for guidance
5. Appeal with evidence, not emotion
