"""
LangChain integration example — automatic cost tracking for LLM calls.

This shows how to plug agentfinobs into any LangChain agent so that
every LLM call is automatically recorded as a financial transaction.

Run:
    pip install langchain-openai agentfinobs
    export OPENAI_API_KEY=sk-...
    python examples/langchain_tracked.py

Note: This example works without actually calling OpenAI —
it demonstrates the handler wiring. For a real run, set your API key.
"""

from agentfinobs import ObservabilityStack, ConsoleExporter
from agentfinobs.integrations.langchain import AgentFinObsHandler


def main():
    # 1. Create observability stack
    obs = ObservabilityStack.create(
        agent_id="langchain-agent",
        budget_rules=[
            {"name": "session", "max_amount": 5.0, "window_seconds": 0},
        ],
        total_budget=50.0,
        exporters=[ConsoleExporter()],
    )

    # 2. Create the callback handler
    handler = AgentFinObsHandler(
        obs_stack=obs,
        agent_id="langchain-agent",
        default_cost_per_1k_input=0.003,   # fallback pricing
        default_cost_per_1k_output=0.015,
    )

    # 3. Show how it would work with LangChain
    print("=== AgentFinObs + LangChain Integration ===\n")
    print("To use with a real LangChain model:\n")
    print("    from langchain_openai import ChatOpenAI")
    print("    llm = ChatOpenAI(model='gpt-4o', callbacks=[handler])")
    print("    result = llm.invoke('What is 2+2?')")
    print("")
    print("Every LLM call will automatically:")
    print("  - Record amount (estimated from token count)")
    print("  - Tag with model name, token counts, latency")
    print("  - Check budget before spending")
    print("  - Fire alerts if anomalous")
    print("")

    # 4. Simulate what the handler does (without real LLM call)
    print("--- Simulating 3 LLM calls ---\n")

    # Mock LangChain response object
    class MockResponse:
        def __init__(self, model, prompt_tokens, completion_tokens):
            self.llm_output = {
                "token_usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                },
                "model_name": model,
            }

    calls = [
        ("gpt-4o", 500, 200),
        ("gpt-4o", 1200, 800),
        ("claude-3-haiku", 300, 150),
    ]

    for model, inp, out in calls:
        handler.on_chat_model_start(
            serialized={"name": model},
            messages=[[]],
            run_id=f"run-{handler.call_count}",
        )
        handler.on_llm_end(
            response=MockResponse(model, inp, out),
            run_id=f"run-{handler.call_count}",
        )

    # 5. Show results
    snap = obs.snapshot()
    print(f"\n=== After {handler.call_count} LLM calls ===")
    print(f"Total LLM spend: ${snap.total_spent:.4f}")
    print(f"Budget remaining: ${5.0 - snap.total_spent:.4f}")

    ok, reason = obs.can_spend(1.0)
    print(f"Can spend $1 more? {'YES' if ok else 'NO: ' + reason}")


if __name__ == "__main__":
    main()
