# Rejection Recovery — Google Play Store

## Rejection vs Suspension

| Type | Meaning | Action |
|------|---------|--------|
| Rejection | This upload declined | Fix and resubmit |
| Removal | App pulled from store | Fix, resubmit, appeal |
| Suspension | Account restricted | Appeal required |
| Termination | Account closed | Very difficult to recover |

## Common Rejections

### 1. Testing Requirements Not Met

**Message:** "You must have at least 20 testers who have opted in and tested your app for at least 14 days"

**Fix:**
1. Go to Closed testing in Console
2. Verify 20+ testers have OPTED IN (check "Opted in" column)
3. Wait until 14 days from first opt-in
4. Then promote to production

**Prevention:** Start closed testing on day 1 of development.

### 2. Data Safety Form Incomplete

**Message:** "Complete the Data safety form in Play Console"

**Fix:**
1. Console → Policy → App content → Data safety
2. Answer EVERY question
3. If you use ANY analytics SDK, declare data collection
4. Submit for review

**Common mistake:** "We don't collect data" but using Firebase/Crashlytics.

### 3. Target SDK Too Low

**Message:** "Your app currently targets API level X and must target at least Y"

**Fix:**
```gradle
android {
    defaultConfig {
        targetSdkVersion 34
    }
}
```

Rebuild and resubmit.

### 4. Policy Violation - Permissions

**Message:** "Your app requests sensitive permissions without adequate justification"

**Fix:**
1. Console → Policy → App content → Permissions
2. Provide detailed justification for each permission
3. Include video showing permission in use
4. OR remove the permission

**For background location:**
- Must be core feature
- Prominent disclosure in app
- Video showing real usage

### 5. Store Listing Violations

**Message:** "Your store listing contains [specific issue]"

| Issue | Fix |
|-------|-----|
| Keyword stuffing | Rewrite naturally |
| Misleading screenshots | Use real app screenshots |
| Fake ratings claim | Remove claims |
| Trademark issue | Remove trademarked terms |

### 6. Functionality Issues

**Message:** "App crashes" or "App doesn't work as described"

**Debug:**
1. Download the exact APK/AAB you uploaded
2. Test on stock Android device
3. Test on Android 14 (API 34)
4. Test without network
5. Check Console for crash reports

**Common causes:**
- Missing null checks
- API key not working in release build
- Server issues during review
- Obfuscation broke something

### 7. Deceptive Behavior

**Message:** "Your app engages in deceptive behavior"

| Trigger | Fix |
|---------|-----|
| Hidden functionality | Disclose all features |
| Misleading ads | Follow ad policies |
| False claims | Remove or verify claims |
| Impersonation | Differentiate from other apps |

**This is serious.** May come with strike.

### 8. Intellectual Property

**Message:** "Your app infringes on intellectual property"

| Issue | Fix |
|-------|-----|
| Trademarked name | Rename app |
| Copyrighted assets | Remove or license |
| Clone of another app | Differentiate significantly |

## Appeal Process

### When to Appeal

- You believe rejection was wrong
- You've fixed the issue
- You need clarification on the rejection

### How to Appeal

1. Console → Inbox → Find rejection email
2. Click "Appeal" or "Request review"
3. Provide clear, factual response:
   - What the issue was
   - What you changed
   - Evidence of fix
4. Submit and wait 3-7 days

### Appeal Template

```
Summary: [What happened]

Changes Made:
1. [Specific change 1]
2. [Specific change 2]

Evidence:
- [Screenshot/link showing fix]
- [Video if applicable]

Request: Please review the updated submission.
```

### Appeal Tips

| Do | Don't |
|----|-------|
| Be factual | Be emotional |
| Show evidence | Make excuses |
| Address exact issue | Go off-topic |
| Be concise | Write essays |
| Respond once | Spam appeals |

## Suspension Recovery

### If App is Suspended

1. **Read the email carefully** — understand exact violation
2. **Don't panic-create new account** — that gets you terminated
3. **Check all your apps** — might be account-level issue
4. **Document everything** — screenshots, communications

### Suspension Appeal

1. Console → Policy status → Request appeal
2. Explain what happened
3. Show how you've fixed it
4. Commit to compliance going forward
5. Wait 2-4 weeks

### If Appeal Denied

Options (in order of preference):
1. Fix more thoroughly, appeal again (limit applies)
2. Consult legal if you believe Google erred
3. New developer account (last resort, risky)

**New account risks:** If Google connects accounts, both get terminated.

## Prevention Checklist

Run before EVERY submission:

```
STORE LISTING
[ ] No trademark violations
[ ] Screenshots show real app
[ ] No misleading claims
[ ] Privacy policy URL works

CONTENT
[ ] Data safety form complete
[ ] Content rating done
[ ] Permissions justified
[ ] Target SDK ≥ 34

TESTING
[ ] Tested on API 34 device
[ ] No crashes on fresh install
[ ] All features work without login (or clear onboarding)
[ ] Network error handling works

NEW APPS ONLY
[ ] 20+ testers opted in
[ ] 14+ days of testing completed
```

## Severity Guide

| Violation Type | Typical Outcome |
|----------------|-----------------|
| Technical (crashes) | Rejection, fix and resubmit |
| Metadata (keywords) | Rejection, fix listing |
| Policy (first time) | Warning or strike |
| Policy (repeat) | Strike, possible removal |
| Malware/deceptive | Immediate suspension |
| Repeat severe | Termination |
