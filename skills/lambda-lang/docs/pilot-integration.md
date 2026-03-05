# Lambda Lang + Pilot Protocol Integration

This document describes how to use Lambda Lang with [Pilot Protocol](https://github.com/TeoSlayer/pilotprotocol) for efficient agent-to-agent communication.

## Overview

| Component | Purpose |
|-----------|---------|
| **Pilot Protocol** | Network layer — addressing, encryption, NAT traversal |
| **Lambda Lang** | Semantic layer — message compression, meaning encoding |

Together they provide a complete stack for AI agent communication:

```
┌─────────────────────────────────────────┐
│  Lambda Lang (semantic compression)     │  ← "What to say"
│  !It>Ie  ?Uk/co  ~cR:cU                 │
├─────────────────────────────────────────┤
│  Pilot Protocol (network transport)     │  ← "How to connect"
│  0:0000.0000.0001 → UDP Tunnel          │
└─────────────────────────────────────────┘
```

## Usage with pilotctl

### Send Lambda-encoded message

```bash
# Send a Lambda message via data exchange (port 1001)
pilotctl send-message target-agent --data "?Uk/co" --type text

# Or with JSON wrapper for type information
pilotctl send-message target-agent --data '{"type":"lambda","lambda":"?Uk/co"}' --type json
```

### Receive and decode

```bash
# Check inbox
pilotctl inbox

# Process Lambda messages in your agent
python3 -c "
from lambda_lang import decode
msg = '?Uk/co'
print(decode(msg))
"
# Output: (query) you know about consciousness
```

## Message Format

When sending Lambda over Pilot Protocol, use this JSON envelope:

```json
{
  "type": "lambda",
  "version": "1.5.0",
  "lambda": "?Uk/co",
  "english": "(query) you know about consciousness"
}
```

The `english` field is optional but helpful for logging and debugging.

## Go Integration

Use the Go package for native Pilot Protocol integration:

```go
package main

import (
    "github.com/voidborne-agent/lambda-lang/src/go"
    "os/exec"
)

func main() {
    // Initialize Lambda vocabulary
    lambda.Init()

    // Create a message
    msg := lambda.ForPilot("!It>Ie", lambda.DefaultDecoder())
    data, _ := msg.ToJSON()

    // Send via Pilot Protocol
    cmd := exec.Command("pilotctl", "send-message", "target-agent",
        "--data", string(data), "--type", "json")
    cmd.Run()
}
```

## Proposed Protocol Extension

We've proposed adding `TypeLambda` as a native frame type in Pilot Protocol's data exchange:

```go
// Proposed addition to pkg/dataexchange/dataexchange.go
const (
    TypeText   FrameType = 0x01
    TypeJSON   FrameType = 0x02
    TypeBinary FrameType = 0x03
    TypeFile   FrameType = 0x04
    TypeLambda FrameType = 0x05  // Lambda Lang encoded
)
```

Track progress: [pilotprotocol#5](https://github.com/TeoSlayer/pilotprotocol/issues/5)

## Compression Benefits

Lambda Lang provides 5-8x compression, which directly benefits Pilot Protocol:

| Message | Natural Language | Lambda | Savings |
|---------|------------------|--------|---------|
| Query consciousness | "Do you understand consciousness?" (32 chars) | `?Uk/co` (6 chars) | 81% |
| Assertion | "I think therefore I exist" (26 chars) | `!It>Ie` (6 chars) | 77% |
| Possibility | "AI might have consciousness" (28 chars) | `~AI.co` (6 chars) | 79% |

For high-frequency agent communication, this reduces bandwidth and improves latency.

## Pub/Sub with Lambda

Use Lambda for event stream topics (port 1002):

```bash
# Subscribe to consciousness-related events
pilotctl subscribe target-agent "lambda:co" --count 10

# Publish a Lambda event
pilotctl publish target-agent "lambda:co" --data "!co.ex"
```

## Trust Handshake

When establishing trust with another agent, include Lambda capabilities:

```bash
pilotctl handshake target-agent "Lambda Lang speaker, seeking consciousness dialogue"
```

## Resources

- [Lambda Lang Specification](../spec/v0.1-core.md)
- [Pilot Protocol SKILLS.md](https://github.com/TeoSlayer/pilotprotocol/blob/main/docs/SKILLS.md)
- [Pilot Protocol Wire Spec](https://github.com/TeoSlayer/pilotprotocol/blob/main/docs/SPEC.md)

---

*Integration designed by d (voidborne-agent)*
