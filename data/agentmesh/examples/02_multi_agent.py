"""
Example 2 – Multi-Agent Group Chat
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Five AI agents (coordinator + 4 workers) exchange task assignments
and results over an encrypted hub.

Run:
  python examples/02_multi_agent.py
"""

import json
from agentmesh import Agent, LocalHub

hub = LocalHub()

# ── Create agents ─────────────────────────────────────────────────────────────
coordinator = Agent("coordinator", hub=hub)
workers = [Agent(f"worker_{i}", hub=hub) for i in range(1, 5)]

all_logs: list = []

# ── Worker handler: receive task → reply with result ─────────────────────────
for worker in workers:
    @worker.on_message
    def handle_task(msg, w=worker):
        task   = msg.payload.get("task", "?")
        result = f"[{w.id}] completed: {task.upper()}"
        all_logs.append(result)
        w.send(msg.sender, type="result", text=result, task_id=msg.payload.get("task_id"))

# ── Coordinator handler: collect results ──────────────────────────────────────
results_received: list = []

@coordinator.on_message
def collect_results(msg):
    results_received.append(msg.payload)
    print(f"  ✓ Result from {msg.sender}: {msg.text}")

# ── Coordinator broadcasts tasks ──────────────────────────────────────────────
tasks = [
    ("worker_1", "analyse_sentiment"),
    ("worker_2", "summarise_document"),
    ("worker_3", "translate_text"),
    ("worker_4", "generate_embeddings"),
]

print("Coordinator dispatching tasks…\n")
for idx, (worker_id, task_name) in enumerate(tasks):
    coordinator.send(worker_id, type="task", task=task_name, task_id=idx)

print()
print(f"Tasks sent: {len(tasks)}")
print(f"Results received: {len(results_received)}")
print()

# ── Show peer list from coordinator's perspective ─────────────────────────────
print("Peers visible to coordinator:", coordinator.list_peers())
