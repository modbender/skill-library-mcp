---
name: eSIM
description: Implement and troubleshoot eSIM across consumer activation, carrier integration, and RSP development.
metadata: {"clawdbot":{"emoji":"📱","os":["linux","darwin","win32"]}}
---

## Critical Distinction
- Consumer RSP (SGP.22) and M2M RSP (SGP.02) are completely different architectures — not interchangeable, verify which applies before starting

## Platform API Restrictions
- Apple eSIM APIs require carrier entitlements — third-party apps cannot access without carrier partnership agreement
- Android carrier privilege APIs require signing certificate match — must be signed with carrier's certificate
- No public API exists for arbitrary eSIM provisioning — apps suggesting otherwise will fail App Store/Play Store review

## Activation Code Traps
- Format is `LPA:1$SMDP+address$MatchingId` — parse carefully, some codes omit optional parts
- `$1` suffix means confirmation code required — flow differs, timeout is shorter
- Codes are often one-time use — SM-DP+ rejects reused MatchingId, must generate new code
- QR code is just encoding — the activation code content is what matters

## Certification Requirements
- GSMA SAS (Security Accreditation Scheme) mandatory for production SM-DP+ — cannot go live without it
- Use test eUICCs during development — production EIDs must not touch test environments
- GSMA TS.48 defines RSP test cases — certification testing follows this spec
- Entitlement server is separate from RSP — iOS carrier features require additional integration beyond profile provisioning

## Consumer-Facing Pitfalls
- QR codes expire — typically 24-72 hours, carrier-dependent, users panic when "invalid"
- Deleting profile is permanent on device — must request new activation code from carrier, no local recovery
- Device lock status matters — locked devices reject profiles from non-native carriers
- Regional variants of same phone model may lack eSIM hardware — verify before promising compatibility
- Profile transfer between devices almost never works — expect new activation per device

## Carrier Integration Reality
- MVNOs rarely operate own SM-DP+ — use MNO's infrastructure or aggregators (G+D, IDEMIA, Thales)
- Business agreements required before technical integration — ES2+ access isn't self-service
- Number porting complicates eSIM activation — may require physical SIM first depending on carrier process

## Troubleshooting Specifics
- "Profile already exists" error — delete existing profile before retry, or request new MatchingId from SM-DP+
- Download fails mid-process — ES9+ requires stable HTTPS, retry on better connection, not a code issue
- Profile installed but no service — verify profile is enabled AND set as active line, restart radio
