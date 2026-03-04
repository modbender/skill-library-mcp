# Design: Agent Teleport

**Role:** Migration Utility
**Mechanism:** Tarball -> BLOB -> SQL -> New Host.
**Security:** DSN acts as the "Private Key". Anyone with DSN can restore.
