# Networking Checklist (UE Multiplayer)

## Authority
- Server is authoritative for health, damage, targeting state, cooldowns.
- Client only requests actions; server validates range/LOS/team rules.

## Replication
- Replicate target selection as an Actor reference or NetId, not every tick.
- Use RepNotify to update UI/target ring on clients.

## Performance
- Avoid Tick for targeting scans; prefer timed checks or event-driven updates.
- Keep overlap/trace frequency bounded (e.g., on Tab press, or every X ms max).

## Testing
- PIE with 2 clients: target selection syncs + ring updates.
- Dedicated server: no client-only assumptions.
- Simulated latency: no desync on target changes.