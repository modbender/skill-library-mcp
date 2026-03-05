"""
Example 4 – LLM Agent Integration (OpenAI / Any API)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Shows how to wrap a real LLM (OpenAI GPT / any API) inside
an AgentMesh agent so multiple LLMs can securely collaborate.

This example uses a mock LLM call so it runs without an API key.
Swap `mock_llm_call` for your real `openai.chat.completions.create(…)`.

Run:
  python examples/04_llm_agents.py
"""

from agentmesh import Agent, LocalHub

# ── Mock LLM (replace with real openai / anthropic / etc.) ───────────────────
def mock_llm_call(system_prompt: str, user_message: str) -> str:
    """Pretend this is calling an LLM API."""
    return f"[LLM response to '{user_message[:40]}…']"

# ── Hub + agents ──────────────────────────────────────────────────────────────
hub = LocalHub()

researcher = Agent("researcher", hub=hub)
writer     = Agent("writer",     hub=hub)
reviewer   = Agent("reviewer",   hub=hub)

# ── Wire up LLM logic to each agent ──────────────────────────────────────────

@researcher.on_message
def on_research_request(msg):
    if msg.type == "task":
        topic    = msg.payload.get("topic", "")
        findings = mock_llm_call(
            system_prompt="You are a research agent.",
            user_message=f"Research this topic: {topic}",
        )
        print(f"  [researcher] Findings: {findings}")
        researcher.send(
            "writer",
            type="findings",
            text=findings,
            topic=topic,
            original_task_id=msg.payload.get("task_id"),
        )

@writer.on_message
def on_write_request(msg):
    if msg.type == "findings":
        draft = mock_llm_call(
            system_prompt="You are a writing agent.",
            user_message=f"Write a report about: {msg.payload.get('topic')}. Findings: {msg.text}",
        )
        print(f"  [writer] Draft: {draft}")
        writer.send(
            "reviewer",
            type="draft",
            text=draft,
            topic=msg.payload.get("topic"),
        )

@reviewer.on_message
def on_review_request(msg):
    if msg.type == "draft":
        review = mock_llm_call(
            system_prompt="You are a quality-review agent.",
            user_message=f"Review this draft: {msg.text}",
        )
        print(f"  [reviewer] Review: {review}")
        reviewer.send(
            "researcher",
            type="done",
            text=f"Pipeline complete. Review: {review}",
        )

final = []
researcher.on_message(lambda m: final.append(m) if m.type == "done" else None)

# ── Kick off the pipeline ──────────────────────────────────────────────────────
# Use a separate "client" agent to kick off the pipeline
print("Starting LLM pipeline…\n")
client = Agent("client", hub=hub)
client.send("researcher", type="task", topic="quantum computing", task_id=1)

# (In a real async app you'd await; here the LocalHub is synchronous)
print()
print("✓ Pipeline complete.  All messages encrypted end-to-end.")
