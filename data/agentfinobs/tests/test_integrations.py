"""
Tests for LangChain integration and CLI entry point.
"""

import json
import os
import tempfile
import time
import unittest

from agentfinobs import ObservabilityStack, SpendTracker, AgentTx, TxStatus
from agentfinobs.integrations.langchain import AgentFinObsHandler


class MockLLMResponse:
    """Mimics langchain's LLMResult enough for our handler."""

    def __init__(self, model="gpt-4o", prompt_tokens=100, completion_tokens=50):
        self.llm_output = {
            "token_usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
            },
            "model_name": model,
        }


class TestAgentFinObsHandler(unittest.TestCase):
    def setUp(self):
        self.tracker = SpendTracker(agent_id="test-lc")
        self.handler = AgentFinObsHandler(
            tracker=self.tracker,
            agent_id="test-lc",
        )

    def test_basic_llm_tracking(self):
        self.handler.on_llm_start(
            serialized={}, prompts=["Hello"], run_id="r1"
        )
        self.handler.on_llm_end(
            response=MockLLMResponse("gpt-4o", 500, 200),
            run_id="r1",
        )

        self.assertEqual(self.tracker.count, 1)
        tx = self.tracker.recent(1)[0]
        self.assertGreater(tx.amount, 0)
        self.assertEqual(tx.counterparty, "gpt-4o")
        self.assertIn("500", tx.tags.get("input_tokens", ""))
        self.assertIn("200", tx.tags.get("output_tokens", ""))

    def test_chat_model_tracking(self):
        self.handler.on_chat_model_start(
            serialized={}, messages=[[]], run_id="r2"
        )
        self.handler.on_llm_end(
            response=MockLLMResponse("claude-3-haiku", 300, 150),
            run_id="r2",
        )

        self.assertEqual(self.tracker.count, 1)
        tx = self.tracker.recent(1)[0]
        self.assertEqual(tx.counterparty, "claude-3-haiku")

    def test_error_tracking(self):
        self.handler.on_llm_start(
            serialized={}, prompts=["test"], run_id="r3"
        )
        self.handler.on_llm_error(
            error=RuntimeError("API timeout"),
            run_id="r3",
        )

        self.assertEqual(self.tracker.count, 1)
        tx = self.tracker.recent(1)[0]
        self.assertEqual(tx.amount, 0.0)
        self.assertEqual(tx.status, TxStatus.FAILED)
        self.assertIn("timeout", tx.description.lower())

    def test_cost_estimation_gpt4o(self):
        cost = self.handler.estimate_cost("gpt-4o", 1000, 1000)
        # gpt-4o: $0.0025/1k input + $0.01/1k output = $0.0125
        self.assertAlmostEqual(cost, 0.0125)

    def test_cost_estimation_unknown_model(self):
        cost = self.handler.estimate_cost("some-new-model", 1000, 1000)
        # Falls back to defaults: $0.003 + $0.015 = $0.018
        self.assertAlmostEqual(cost, 0.018)

    def test_multiple_calls(self):
        for i in range(5):
            rid = f"multi-{i}"
            self.handler.on_chat_model_start(
                serialized={}, messages=[[]], run_id=rid
            )
            self.handler.on_llm_end(
                response=MockLLMResponse("gpt-4o-mini", 200, 100),
                run_id=rid,
            )

        self.assertEqual(self.tracker.count, 5)
        self.assertEqual(self.handler.call_count, 5)

    def test_works_with_obs_stack(self):
        obs = ObservabilityStack.create(agent_id="lc-stack-test")
        handler = AgentFinObsHandler(obs_stack=obs, agent_id="lc-stack")

        handler.on_chat_model_start(
            serialized={}, messages=[[]], run_id="s1"
        )
        handler.on_llm_end(
            response=MockLLMResponse("gpt-4o", 100, 50),
            run_id="s1",
        )

        self.assertEqual(obs.tracker.count, 1)

    def test_requires_tracker_or_stack(self):
        with self.assertRaises(ValueError):
            AgentFinObsHandler()

    def test_latency_tag(self):
        self.handler.on_llm_start(
            serialized={}, prompts=["test"], run_id="lat1"
        )
        time.sleep(0.05)  # 50ms
        self.handler.on_llm_end(
            response=MockLLMResponse("gpt-4o", 100, 50),
            run_id="lat1",
        )

        tx = self.tracker.recent(1)[0]
        latency_ms = int(tx.tags.get("latency_ms", "0"))
        self.assertGreater(latency_ms, 30)  # at least 30ms


class TestCLI(unittest.TestCase):
    def test_version(self):
        import subprocess
        result = subprocess.run(
            ["python", "-m", "agentfinobs", "version"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("agentfinobs", result.stdout)
        self.assertIn("0.1.0", result.stdout)

    def test_demo(self):
        import subprocess
        result = subprocess.run(
            ["python", "-m", "agentfinobs", "demo"],
            capture_output=True, text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Final Metrics", result.stdout)
        self.assertIn("Transactions", result.stdout)

    def test_status_with_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test_txs.jsonl")
            # Write some sample transactions
            now = time.time()
            with open(path, "w") as f:
                for i in range(5):
                    tx = {
                        "tx_id": f"tx-{i}",
                        "agent_id": "cli-test",
                        "task_id": f"task-{i}",
                        "amount": 10.0,
                        "revenue": 12.0 if i % 2 == 0 else 8.0,
                        "status": "confirmed",
                        "created_at": now - (5 - i) * 60,
                        "counterparty": "openai",
                        "description": f"Test tx {i}",
                    }
                    f.write(json.dumps(tx) + "\n")

            import subprocess
            result = subprocess.run(
                ["python", "-m", "agentfinobs", "status", path, "--budget", "100"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("Transactions", result.stdout)
            self.assertIn("5", result.stdout)
            self.assertIn("$50.00", result.stdout)

    def test_status_missing_file(self):
        import subprocess
        result = subprocess.run(
            ["python", "-m", "agentfinobs", "status", "/nonexistent.jsonl"],
            capture_output=True, text=True,
        )
        self.assertIn("not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
