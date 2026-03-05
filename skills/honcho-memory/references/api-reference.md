# Honcho SDK API Reference

## Initialize

```python
from honcho import Honcho
honcho = Honcho(workspace_id="my-workspace", api_key="hch-v3-...")
```

## Peers

```python
# Create/get a peer (idempotent)
user = honcho.peer("username")
agent = honcho.peer("agent-name")

# Get what Honcho has learned about this peer
representation = user.representation()  # returns string of deductive + inductive observations

# Ask Honcho a question about this peer
answer = user.chat("What are their priorities?", reasoning_level="medium")
# reasoning_level: minimal | low | medium | high | max
```

## Sessions

```python
# Create/get a session (idempotent)
session = honcho.session("session-id-string")

# Add peers to session
session.add_peers([user, agent])

# Write messages (triggers background reasoning)
session.add_messages([
    user.message("Hello, I'm working on Project X"),
    agent.message("I can help with that. What specifically?"),
])

# Get context (token-budgeted retrieval)
ctx = session.context(tokens=2000)
# ctx.summary — distilled summary
# ctx.messages — recent relevant messages
# ctx.peer_representation — what Honcho knows about the peer
# ctx.to_anthropic(assistant=agent) — convert to Anthropic API format
# ctx.to_openai(assistant=agent) — convert to OpenAI API format

# Check reasoning queue status
q = session.queue_status()
# q.total_work_units, q.completed_work_units, q.pending_work_units, q.in_progress_work_units
```

## Key Concepts

- **Reasoning is async**: Messages are processed in the background by Neuromancer
- **Token batching**: ~1000 tokens accumulated before reasoning kicks in
- **Peers are cross-session**: A peer's representation builds from ALL sessions they're in
- **Sessions are idempotent**: Calling `[[research/honcho-integration-plan|Honcho]].session("id")` always returns the same session
- **Pricing**: ~$2/million tokens ingested. Storage and retrieval are free.
