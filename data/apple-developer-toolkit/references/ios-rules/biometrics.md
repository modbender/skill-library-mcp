---
description: "Implementation rules for biometrics"
---
# Biometrics

BIOMETRIC AUTHENTICATION (Face ID / Touch ID):
- import LocalAuthentication; LAContext().evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics)
- Requires NSFaceIDUsageDescription permission (add CONFIG_CHANGES)
- Check canEvaluatePolicy first; fall back to passcode if biometrics unavailable
- LAContext().biometryType to detect .faceID vs .touchID vs .none
- Always provide manual unlock alternative (PIN/password)
