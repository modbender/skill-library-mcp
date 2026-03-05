# Memory Template — Google Play Store

Create `~/google-play-store/memory.md` with this structure:

```markdown
# Google Play Store Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD
integration: pending

## Workflow
<!-- Organization name, team size, release cadence -->
<!-- NO credentials, keys, or secrets here -->

## Apps
<!-- Package names and high-level status -->
<!-- com.example.app - production, stable -->
<!-- com.example.beta - closed testing -->

## CI/CD
<!-- Manual uploads vs CI/CD -->
<!-- Tool names only: Fastlane, GitHub Actions, etc. -->
<!-- NO secrets, tokens, or passwords stored here -->

## Preferences
<!-- Release cadence, rollout strategy -->
<!-- Notification preferences -->

## Lessons Learned
<!-- Past rejections and how they were fixed -->
<!-- Gotchas specific to their apps -->

---
*Updated: YYYY-MM-DD*
```

## Per-App Notes

For each app, create `~/google-play-store/apps/{package-name}.md`:

```markdown
# {App Name}

## Info
package: com.example.app
track: production
signing: google-managed
target_sdk: 34

## Releases
<!-- Recent release history -->
- YYYY-MM-DD: v1.2.0 (versionCode 2025022501)
- YYYY-MM-DD: v1.1.0 rollout halted at 5%

## Rejections
<!-- If any, with resolution -->

## ASO
<!-- Keywords tracking, screenshot strategy -->

## Notes
<!-- App-specific observations -->
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Gather context from conversations |
| `complete` | Enough context | Work normally |
| `paused` | User said "not now" | Don't ask, use what you have |

## Key Principles

- Learn from conversations, don't interrogate
- Update `last` on each interaction
- Most users stay `ongoing` indefinitely
