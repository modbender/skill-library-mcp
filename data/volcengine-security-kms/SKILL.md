---
name: volcengine-security-kms
description: Key lifecycle management with Volcengine KMS. Use when users need key creation, rotation policies, encryption/decryption workflows, or key permission troubleshooting.
---

# volcengine-security-kms

Operate KMS keys with lifecycle awareness and least-privilege access checks.

## Execution Checklist

1. Confirm key purpose, algorithm, and usage scope.
2. Create or select key and validate policy bindings.
3. Execute encrypt/decrypt/sign task.
4. Return key metadata, operation result, and audit hints.

## Safety Rules

- Never expose plaintext secrets in logs.
- Rotate keys according to policy windows.
- Validate caller permissions before key operations.

## References

- `references/sources.md`
