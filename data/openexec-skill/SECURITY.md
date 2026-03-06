# OpenExec Security Model

OpenExec is a deterministic execution boundary for AI systems.
It enforces signed approvals, replay protection, and receipt generation.

This document defines its security assumptions, threat model, and operator responsibilities.

---

## 1. Security Philosophy

OpenExec is a boundary, not a sandbox.

It enforces:

- Deterministic execution
- Approval verification (Ed25519)
- Replay protection
- Receipt integrity
- Explicit action allow-listing

It does NOT provide:

- OS-level sandboxing
- Process isolation
- Network firewalling
- Policy decision logic
- Infrastructure hardening

Those are operator responsibilities.

---

## 2. Minimal Threat Model

### Assets Protected

- Execution integrity
- Approval authenticity
- Receipt authenticity
- Deterministic replay resistance

### Trust Assumptions

OpenExec assumes:

1. The host system is trusted.
2. The `CLAWSHIELD_PUBLIC_KEY` is correct and authentic.
3. Operators configure `OPENEXEC_ALLOWED_ACTIONS` appropriately.
4. The database destination (if remote) is trusted.

### Out of Scope

OpenExec does not attempt to defend against:

- Host OS compromise
- Malicious container runtime
- Supply-chain compromise of Python packages
- Root-level privilege escalation
- Side-channel attacks
- Memory inspection attacks

These must be mitigated at the infrastructure layer.

---

## 3. Network Model

OpenExec:

- Performs no outbound HTTP, RPC, or governance calls during execution.
- Verifies signatures locally.
- Uses local SQLite by default.
- Only performs outbound DB network I/O if `OPENEXEC_DB_URL` is explicitly configured to a remote database.

Inbound HTTP is required for proposal submission and receipt verification.

Operators must:

- Bind to `127.0.0.1` unless intentionally exposed.
- Place behind a firewall or reverse proxy if externally reachable.
- Use TLS if deployed outside localhost.

---

## 4. Execution Privilege Model

Registered handlers execute with the privileges of the hosting process.

OpenExec does not:

- Drop privileges
- Apply seccomp
- Enforce syscall filtering
- Restrict filesystem access

Operators must:

- Avoid running as root
- Use container or VM isolation
- Restrict allowed actions via `OPENEXEC_ALLOWED_ACTIONS`
- Avoid registering unsafe handlers

---

## 5. Database & Persistence Model

Default:

```
sqlite:///openexec.db
```

If `OPENEXEC_DB_URL` is set to a remote database:

- Outbound network I/O occurs
- Data leaves the host
- Trust shifts to the DB operator

Operators are responsible for:

- Database authentication
- TLS configuration
- Backup policies
- Log rotation
- Data retention controls

---

## 6. Production Hardening Checklist

Before deploying OpenExec in production:

- [ ] Bind to `127.0.0.1` or restrict network exposure
- [ ] Place behind firewall or reverse proxy
- [ ] Use TLS termination
- [ ] Pin dependencies (already enforced in `requirements.txt`)
- [ ] Run inside container or VM
- [ ] Do NOT run as root
- [ ] Configure `OPENEXEC_ALLOWED_ACTIONS`
- [ ] Provide valid `CLAWSHIELD_PUBLIC_KEY`
- [ ] Protect `CLAWSHIELD_TENANT_ID` appropriately
- [ ] Audit all registered execution handlers
- [ ] Confirm remote DB trust (if used)
- [ ] Implement log rotation & monitoring

---

## 7. Reporting Security Issues

If you discover a vulnerability:

- Open a private issue if possible
- Or contact the repository maintainer directly

Please provide:

- Version
- Steps to reproduce
- Expected behavior
- Observed behavior
- Environment details

---

## 8. Threat Mapping (STRIDE-Lite)

| Threat | Mitigation |
|--------|------------|
| Spoofed approval | Ed25519 signature verification |
| Replay attack | Nonce registry + receipt hashing |
| Parameter mutation | Approval hash binding |
| Silent execution | Mandatory receipt emission |
| Privilege escalation | Operator-enforced allow-list |
| Network exfiltration | No outbound HTTP/RPC during execution |
| Remote DB misuse | Explicit operator configuration required |

---

## 9. Code Loading Model

OpenExec does not perform dynamic code loading.

Specifically:

- No runtime module imports based on user input
- No use of importlib for dynamic resolution
- No plugin discovery from filesystem
- No remote code fetching
- No execution of downloaded artifacts
- No handler registration via API

All execution handlers must be statically defined in source code
and registered during application startup.

There is no runtime extension mechanism.

---

## 10. Code Execution Primitives

OpenExec does not use:

- `eval()`
- `exec()`
- `compile()`
- `ast`-based dynamic execution
- `subprocess` execution of user input
- `os.system()`
- `pickle` deserialization of untrusted input

User input is never interpreted as executable code.

All execution flows invoke statically defined Python callables.

---

## 11. Handler Registry Model

Execution handlers are:

- Defined statically in source
- Registered at application startup
- Not modifiable at runtime
- Not extensible via API
- Not loadable from remote sources

The registry is sealed at boot.

Operators may modify source code intentionally,
but there is no dynamic registration surface exposed to users.

---

## 12. Self-Modification

OpenExec does not modify its own code,
write executable files,
or alter system configuration.

It does not install packages at runtime.
It does not download additional modules.
It does not mutate its own execution graph.

---

## 13. Remote Code Execution Clarification

OpenExec can execute registered Python handlers.
This is an intentional architectural boundary design.

However:

- Handlers must be statically defined
- No dynamic code evaluation is supported
- No user-supplied code execution is possible
- No runtime code injection primitives exist

Execution is deterministic and bounded to registered callables only.

---

OpenExec is intentionally minimal.
Security guarantees are explicit and bounded.
Operators must provide infrastructure isolation.
