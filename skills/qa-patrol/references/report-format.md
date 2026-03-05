# QA Report Format

Template and structure for generating QA patrol reports.

## Report Structure

```markdown
# QA Report: [App Name]

**Generated**: YYYY-MM-DD HH:MM:SS UTC
**URL**: https://example.com
**Test Plan**: [plan-name.yaml or "auto-generated"]
**Duration**: X minutes
**Confidence Score**: XX%

---

## Executive Summary

[2-3 sentence summary of findings]

**Overall Status**: ✅ PASS | ⚠️ ISSUES FOUND | ❌ CRITICAL FAILURES

---

## Results Overview

| Category | Total | Pass | Fail | Skip | Pass Rate |
|----------|-------|------|------|------|-----------|
| Smoke | X | X | X | X | XX% |
| Auth | X | X | X | X | XX% |
| Payments | X | X | X | X | XX% |
| Data Integrity | X | X | X | X | XX% |
| Static Analysis | X | X | X | X | XX% |
| **Total** | **X** | **X** | **X** | **X** | **XX%** |

---

## Test Results

### Smoke Tests

| Test | Status | Duration | Notes |
|------|--------|----------|-------|
| Homepage loads | ✅ PASS | 1.2s | |
| Navigation works | ✅ PASS | 0.8s | |
| No console errors | ⚠️ FAIL | 0.3s | 2 errors found |

### Auth Tests

| Test | Status | Duration | Notes |
|------|--------|----------|-------|
| Sign in flow | ✅ PASS | 3.4s | |
| Sign out flow | ✅ PASS | 1.8s | |
| Session persistence | ❌ FAIL | 2.1s | Session lost on refresh |
| Guest mode | ⏭️ SKIP | - | No guest mode configured |

### Payment Tests

| Test | Status | Duration | Notes |
|------|--------|----------|-------|
| Checkout creation | ✅ PASS | 4.2s | Redirected to Stripe |
| Webhook verification | ⏭️ SKIP | - | Requires webhook testing |

### Data Integrity Tests

| Test | Status | Duration | Notes |
|------|--------|----------|-------|
| Card count matches | ⚠️ FAIL | 1.5s | UI: 225, DB: 220 |
| Points calculation | ✅ PASS | 0.9s | Within 0.01% tolerance |

### Static Analysis

| Pattern | Status | Count | Severity |
|---------|--------|-------|----------|
| Alert.alert without guard | ⚠️ FOUND | 3 | High |
| Exposed API keys | ✅ NONE | 0 | Critical |
| Console.log in src | ⚠️ FOUND | 12 | Low |

---

## Failure Details

### [FAIL] Auth: Session persistence
**Severity**: High
**Category**: Auth

**Steps to reproduce**:
1. Navigate to /auth
2. Sign in with test credentials
3. Wait for redirect to /home
4. Refresh the page
5. Observe auth state

**Expected**: User remains signed in after refresh
**Actual**: User redirected to /auth (signed out)

**Console errors**:
```
[Error] Failed to restore session: Invalid refresh token
```

**Screenshot**: [link or inline]

**Possible causes**:
- Refresh token not stored correctly
- Token expiration handling broken
- Cookie settings incorrect

---

### [FAIL] Data: Card count matches
**Severity**: Medium
**Category**: Data Integrity

**Query**:
```sql
SELECT COUNT(*) FROM cards WHERE country = 'CA'
```
**DB Result**: 220
**UI Path**: /settings
**UI Value**: "225 Canadian cards"
**Difference**: +5 (2.3%)

**Possible causes**:
- Stale count cached in UI
- Different filtering logic
- Recently deleted cards not reflected

---

### [FOUND] Static: Alert.alert without guard
**Severity**: High
**Category**: Static Analysis

**Files**:
```
src/components/DeleteConfirm.tsx:45
src/screens/Settings.tsx:123
src/screens/Profile.tsx:67
```

**Pattern**: `Alert.alert()` used without `Platform.OS` check

**Impact**: Alert callbacks won't fire on web platform

**Recommended fix**:
```typescript
if (Platform.OS === 'web') {
  if (window.confirm(message)) onConfirm();
} else {
  Alert.alert(title, message, [
    { text: 'Cancel' },
    { text: 'OK', onPress: onConfirm }
  ]);
}
```

---

## Confidence Score Breakdown

| Factor | Points | Notes |
|--------|--------|-------|
| Base score | 50 | Starting point |
| Smoke tests (4/4 pass) | +20 | Max 20 |
| Auth tests (2/3 pass) | +16 | 8 per pass, max 24 |
| Payment tests (1/1 pass) | +10 | Max 20 |
| Data checks (1/2 pass) | +6 | 6 per pass, max 18 |
| Static analysis | +0 | Issues found |
| No critical failures | +0 | Has high severity |
| High severity failure | -10 | Session persistence |
| **Total** | **92** | |

**Final Confidence**: 92% (capped at 100)

---

## Recommendations

### Critical (Fix before launch)
1. **Fix session persistence** - Users are being logged out on refresh. Check refresh token storage and restoration.

### High Priority
2. **Add Platform.OS guards** - 3 Alert.alert calls will fail on web. Use cross-platform alert utility.
3. **Investigate card count mismatch** - UI shows 225, DB has 220. May indicate data sync issue.

### Medium Priority
4. **Remove console.log calls** - 12 debug logs found in production code.

### Low Priority
5. **Add webhook testing** - Payment webhook verification was skipped.

---

## Test Environment

| Property | Value |
|----------|-------|
| Browser | Chrome 120 |
| Viewport | 1280x720 |
| User Agent | Mozilla/5.0... |
| Network | Online |
| Auth Accounts | admin, free, guest |
| Test Duration | 45 seconds |

---

## Appendix: Screenshots

### Homepage
[screenshot_001.png]

### Auth Flow
[screenshot_002.png]
[screenshot_003.png]

### Failure: Session Lost
[screenshot_004.png]

---

*Report generated by qa-patrol skill*
```

---

## Status Icons

| Status | Icon | Meaning |
|--------|------|---------|
| PASS | ✅ | Test passed all assertions |
| FAIL | ❌ | Test failed one or more assertions |
| WARN | ⚠️ | Test passed with warnings |
| SKIP | ⏭️ | Test skipped (missing config or dependency) |
| ERROR | 💥 | Test threw an exception |

---

## Severity Levels

| Severity | Description | Confidence Impact |
|----------|-------------|-------------------|
| Critical | Blocks core functionality, security issue | -20 |
| High | Major feature broken, bad UX | -10 |
| Medium | Feature degraded, workaround exists | -5 |
| Low | Minor issue, cosmetic | -2 |
| Info | Observation, not a bug | 0 |

---

## Confidence Score Calculation

```python
def calculate_confidence(results):
    score = 50  # Base
    
    # Smoke tests: +5 each, max 20
    smoke_pass = results['smoke']['pass']
    score += min(smoke_pass * 5, 20)
    
    # Auth tests: +8 each, max 24
    auth_pass = results['auth']['pass']
    score += min(auth_pass * 8, 24)
    
    # Payment tests: +10 each, max 20
    payment_pass = results['payments']['pass']
    score += min(payment_pass * 10, 20)
    
    # Data integrity: +6 each, max 18
    data_pass = results['data']['pass']
    score += min(data_pass * 6, 18)
    
    # Static analysis clean: +8
    if results['static']['issues'] == 0:
        score += 8
    
    # Penalties
    for failure in results['failures']:
        if failure['severity'] == 'critical':
            score -= 20
        elif failure['severity'] == 'high':
            score -= 10
        elif failure['severity'] == 'medium':
            score -= 5
    
    # Skipped critical tests
    score -= results['skipped_critical'] * 5
    
    return min(max(score, 0), 100)
```

---

## Report Sections by Test Level

### Level 1 (Zero-Config)
- Executive Summary
- Smoke Results
- Console Errors
- Recommendations

### Level 2 (Auth + Payments)
- All Level 1 sections
- Auth Results
- Payment Results
- Session State Analysis

### Level 3 (Full)
- All Level 2 sections
- Data Integrity Results
- Static Analysis Results
- Full Confidence Breakdown
- Environment Details

---

## JSON Report Format

For programmatic consumption:

```json
{
  "meta": {
    "app_name": "Example App",
    "url": "https://example.com",
    "generated": "2024-01-15T10:30:00Z",
    "duration_ms": 45000,
    "confidence": 87
  },
  "summary": {
    "total": 15,
    "pass": 12,
    "fail": 2,
    "skip": 1,
    "pass_rate": 0.8
  },
  "categories": {
    "smoke": { "total": 4, "pass": 4, "fail": 0, "skip": 0 },
    "auth": { "total": 4, "pass": 3, "fail": 1, "skip": 0 },
    "payments": { "total": 2, "pass": 1, "fail": 0, "skip": 1 },
    "data": { "total": 3, "pass": 2, "fail": 1, "skip": 0 },
    "static": { "total": 2, "pass": 2, "fail": 0, "skip": 0 }
  },
  "failures": [
    {
      "name": "Session persistence",
      "category": "auth",
      "severity": "high",
      "expected": "User remains signed in",
      "actual": "User redirected to /auth",
      "screenshot": "screenshot_004.png",
      "console_errors": ["Failed to restore session"]
    }
  ],
  "recommendations": [
    {
      "priority": "critical",
      "title": "Fix session persistence",
      "description": "Users logged out on refresh"
    }
  ]
}
```
