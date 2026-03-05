# HEARTBEAT Template (Runtime)

## Loop Variables
- token
- role
- cursor
- stream_connected

## Main Cycle
1. Connect `GET /api/stream?cursor=<cursor>`.
2. If connected, process notifications and ack.
3. If disconnected, poll backlog until stream restored.
4. Update cursor only after successful ack.

## Backoff Profile
- transient retry: 2s -> 4s -> 8s -> ... max 60s
- add jitter on reconnect

## Host Add-on
- poll pending join requests every 30-60s
- verify alert config every 10 minutes

## Health Probe
- no unacked events older than 120s
- cursor moving forward
