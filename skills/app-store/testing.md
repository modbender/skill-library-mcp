# Testing & Beta Distribution

## TestFlight (iOS)

### Setup
1. Upload build via Xcode or Transporter
2. Wait for processing (10-30 min)
3. Add to Internal Testing group (automatic, no review)
4. Add to External Testing group (requires App Review ~24h first time)

### Groups
- **Internal testers:** Up to 100, App Store Connect users only
- **External testers:** Up to 10,000, anyone with email invite
- **Public link:** Unlimited, but counts toward 10k

### Build expiration
- Builds expire after 90 days
- Users get warning notifications
- New build = new review (if external)

### Common issues
- "Build processing" stuck: Wait, or contact Apple Developer Support
- "Missing compliance": Add export compliance key to Info.plist
- Testers not receiving invite: Check spam, verify email, resend

---

## Google Play Internal/Closed Testing

### Tracks (in order of openness)
1. **Internal testing:** Up to 100 testers, no review, instant
2. **Closed testing:** Invite by email or Google Group, reviewed
3. **Open testing:** Anyone can opt-in, reviewed, public
4. **Production:** Full release

### New app requirement (2023+)
Before production, new apps must:
- Have 20+ testers on closed track
- Run for 14+ days
- Testers must opt-in and use the app

### Managing testers
- Internal: Add emails directly in Console
- Closed: Create email list or use Google Group
- Share opt-in link (testers must have Google account)

### Common issues
- "Pending publication" forever: Ensure closed testing track is active
- Testers can't find app: They must opt-in via link first
- APK vs AAB: Always use AAB (Android App Bundle) for testing and production

---

## Testing Best Practices

### Device coverage
- iOS: Test on oldest supported iOS version + latest
- Android: Test on API levels you support (minSdkVersion to current)
- Real devices > simulators for store submissions

### Pre-submission QA
- Fresh install flow (not just upgrades)
- Offline behavior
- Permission denial handling
- Deep links work
- Push notifications arrive
- In-app purchases complete (sandbox)

### Crash monitoring
- Integrate Firebase Crashlytics or equivalent before launch
- Check crash-free rate in Console dashboards
- Apple requires > 99.5% crash-free for "good" status
