"""
Tests for agentfinobs SDK.
"""

import time
import unittest

from agentfinobs import (
    ObservabilityStack,
    SpendTracker,
    BudgetManager,
    MetricsEngine,
    AnomalyDetector,
    AgentTx,
    BudgetRule,
    AlertSeverity,
    PaymentRail,
    TxStatus,
)


class TestSpendTracker(unittest.TestCase):
    def test_record_and_query(self):
        tracker = SpendTracker(agent_id="test-agent")
        tx = tracker.record(amount=10.0, task_id="t1", description="test spend")

        self.assertEqual(tx.agent_id, "test-agent")
        self.assertEqual(tx.amount, 10.0)
        self.assertEqual(tx.status, TxStatus.PENDING)
        self.assertEqual(tracker.count, 1)

    def test_settle(self):
        tracker = SpendTracker(agent_id="test")
        tx = tracker.record(amount=5.0, task_id="t1")
        tracker.settle(tx.tx_id, revenue=8.0)

        settled = tracker.get(tx.tx_id)
        self.assertEqual(settled.revenue, 8.0)
        self.assertEqual(settled.pnl, 3.0)
        self.assertEqual(settled.status, TxStatus.CONFIRMED)

    def test_recent(self):
        tracker = SpendTracker(agent_id="test")
        for i in range(10):
            tracker.record(amount=float(i), task_id=f"t{i}")

        recent = tracker.recent(5)
        self.assertEqual(len(recent), 5)
        self.assertEqual(recent[-1].amount, 9.0)

    def test_query_by_task(self):
        tracker = SpendTracker(agent_id="test")
        tracker.record(amount=1.0, task_id="alpha")
        tracker.record(amount=2.0, task_id="beta")
        tracker.record(amount=3.0, task_id="alpha")

        alpha_txs = tracker.query(task_id="alpha")
        self.assertEqual(len(alpha_txs), 2)
        self.assertEqual(sum(tx.amount for tx in alpha_txs), 4.0)

    def test_listener(self):
        tracker = SpendTracker(agent_id="test")
        received = []
        tracker.add_listener(lambda tx: received.append(tx))

        tracker.record(amount=1.0)
        tracker.record(amount=2.0)

        self.assertEqual(len(received), 2)

    def test_max_history(self):
        tracker = SpendTracker(agent_id="test", max_history=5)
        for i in range(10):
            tracker.record(amount=float(i))

        self.assertEqual(tracker.count, 5)
        recent = tracker.recent(10)
        self.assertEqual(len(recent), 5)
        # Should only have the last 5 (amounts 5-9)
        self.assertEqual(recent[0].amount, 5.0)


class TestBudgetManager(unittest.TestCase):
    def test_basic_budget_enforcement(self):
        budget = BudgetManager()
        budget.add_rule(BudgetRule(
            name="test_limit",
            max_amount=10.0,
            window_seconds=0,  # lifetime
            severity=AlertSeverity.WARNING,
        ))

        ok, _ = budget.check_can_spend(5.0)
        self.assertTrue(ok)

        # Simulate spending
        tx = AgentTx(amount=8.0)
        budget.on_tx(tx)

        ok, reason = budget.check_can_spend(5.0)
        self.assertFalse(ok)
        self.assertIn("test_limit", reason)

    def test_halt_on_breach(self):
        budget = BudgetManager()
        budget.add_rule(BudgetRule(
            name="hard_limit",
            max_amount=5.0,
            window_seconds=0,
            severity=AlertSeverity.CRITICAL,
            halt_on_breach=True,
        ))

        tx = AgentTx(amount=10.0)
        budget.on_tx(tx)

        self.assertTrue(budget.is_halted)
        self.assertIn("hard_limit", budget.halt_reason)

    def test_headroom(self):
        budget = BudgetManager()
        budget.add_rule(BudgetRule(
            name="cap", max_amount=100.0, window_seconds=0
        ))

        tx = AgentTx(amount=30.0)
        budget.on_tx(tx)

        headroom = budget.headroom()
        self.assertAlmostEqual(headroom["cap"], 70.0)

    def test_alert_callback(self):
        budget = BudgetManager()
        budget.add_rule(BudgetRule(
            name="low_cap", max_amount=1.0, window_seconds=0
        ))

        alerts_received = []
        budget.add_alert_callback(lambda a: alerts_received.append(a))

        tx = AgentTx(amount=5.0)
        budget.on_tx(tx)

        self.assertEqual(len(alerts_received), 1)
        self.assertIn("low_cap", alerts_received[0].message)


class TestMetricsEngine(unittest.TestCase):
    def test_basic_metrics(self):
        engine = MetricsEngine(budget_total=1000.0)

        now = time.time()
        txs = [
            AgentTx(amount=10.0, revenue=15.0, task_id="t1",
                    status=TxStatus.CONFIRMED, created_at=now - 100),
            AgentTx(amount=20.0, revenue=18.0, task_id="t2",
                    status=TxStatus.CONFIRMED, created_at=now - 50),
            AgentTx(amount=5.0, revenue=0.0, task_id="t3",
                    status=TxStatus.FAILED, created_at=now),
        ]

        snap = engine.compute(txs)

        self.assertEqual(snap.tx_count, 3)
        self.assertAlmostEqual(snap.total_spent, 35.0)
        self.assertAlmostEqual(snap.total_revenue, 33.0)
        self.assertAlmostEqual(snap.total_pnl, -2.0)

        # 2 unique tasks
        self.assertAlmostEqual(snap.avg_cost_per_tx, 35.0 / 3)

        # ROI = -2/35 * 100
        self.assertAlmostEqual(snap.roi_pct, -2.0 / 35.0 * 100)

        # Win rate: 1 win (t1), 2 losses (t2, t3)
        self.assertAlmostEqual(snap.win_rate_pct, 1.0 / 3 * 100, places=1)

    def test_empty_txs(self):
        engine = MetricsEngine()
        snap = engine.compute([])
        self.assertEqual(snap.tx_count, 0)
        self.assertIsNone(snap.roi_pct)

    def test_burn_rate(self):
        engine = MetricsEngine(budget_total=100.0)

        now = time.time()
        txs = [
            AgentTx(amount=10.0, created_at=now - 7200),  # 2h ago
            AgentTx(amount=10.0, created_at=now),
        ]

        snap = engine.compute(txs)
        # 20 spent over 2 hours = 10/hour
        self.assertAlmostEqual(snap.burn_rate_per_hour, 10.0, places=0)
        # (100 - 20) / 10 = 8 hours runway
        self.assertAlmostEqual(snap.estimated_runway_hours, 8.0, places=0)


class TestAnomalyDetector(unittest.TestCase):
    def test_detects_spike(self):
        detector = AnomalyDetector(
            window_size=50, z_threshold=2.5, min_samples=10, cooldown_seconds=0
        )

        # Feed normal transactions
        for _ in range(20):
            tx = AgentTx(amount=10.0, agent_id="test")
            detector.on_tx(tx)

        # Feed anomalous transaction (10x normal)
        spike_tx = AgentTx(amount=100.0, agent_id="test")
        detector.on_tx(spike_tx)

        alerts = detector.get_alerts()
        self.assertTrue(len(alerts) > 0)
        self.assertIn("Anomalous", alerts[-1].message)

    def test_no_alert_for_normal(self):
        detector = AnomalyDetector(
            window_size=50, z_threshold=3.0, min_samples=10, cooldown_seconds=0
        )

        for _ in range(30):
            tx = AgentTx(amount=10.0, agent_id="test")
            detector.on_tx(tx)

        alerts = detector.get_alerts()
        self.assertEqual(len(alerts), 0)

    def test_stats(self):
        detector = AnomalyDetector()
        for i in range(5):
            detector.on_tx(AgentTx(amount=float(i + 1)))

        stats = detector.stats()
        self.assertEqual(stats["n"], 5)
        self.assertAlmostEqual(stats["mean"], 3.0)


class TestObservabilityStack(unittest.TestCase):
    def test_full_flow(self):
        obs = ObservabilityStack.create(
            agent_id="integration-test",
            budget_rules=[
                {"name": "cap", "max_amount": 100, "window_seconds": 0},
            ],
            total_budget=500.0,
        )

        # Track spending
        tx1 = obs.track(amount=10.0, task_id="task-1", description="API call")
        tx2 = obs.track(amount=20.0, task_id="task-1", description="Another call")

        # Settle
        obs.settle(tx1.tx_id, revenue=15.0)
        obs.settle(tx2.tx_id, revenue=25.0)

        # Check metrics
        snap = obs.snapshot()
        self.assertEqual(snap.tx_count, 2)
        self.assertAlmostEqual(snap.total_spent, 30.0)
        self.assertAlmostEqual(snap.total_revenue, 40.0)
        self.assertAlmostEqual(snap.total_pnl, 10.0)

        # Budget headroom
        ok, _ = obs.can_spend(50.0)
        self.assertTrue(ok)

        ok, _ = obs.can_spend(80.0)
        self.assertFalse(ok)

    def test_payment_rail(self):
        obs = ObservabilityStack.create(agent_id="rail-test")
        tx = obs.track(
            amount=5.0,
            rail=PaymentRail.X402_USDC,
            counterparty="some-api-provider",
        )
        self.assertEqual(tx.rail, PaymentRail.X402_USDC)

        snap = obs.snapshot()
        self.assertIn("x402_usdc", snap.spend_by_rail)


class TestExporters(unittest.TestCase):
    def test_jsonl_exporter(self):
        import tempfile
        import os
        import json

        from agentfinobs import JsonlExporter

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "test.jsonl")
            exporter = JsonlExporter(path)

            tx = AgentTx(amount=42.0, agent_id="exp-test", task_id="t1")
            exporter.export_tx(tx)
            exporter.export_tx(AgentTx(amount=7.0))

            with open(path) as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)
            first = json.loads(lines[0])
            self.assertAlmostEqual(first["amount"], 42.0)

    def test_console_exporter(self):
        import io
        import contextlib

        from agentfinobs import ConsoleExporter

        exporter = ConsoleExporter(color=False)
        tx = AgentTx(amount=5.0, counterparty="openai", description="GPT call")

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exporter.export_tx(tx)

        output = buf.getvalue()
        self.assertIn("$5.0000", output)
        self.assertIn("openai", output)

    def test_multi_exporter(self):
        from agentfinobs import MultiExporter, BaseExporter

        received_a = []
        received_b = []

        class FakeA(BaseExporter):
            def export_tx(self, tx):
                received_a.append(tx)

        class FakeB(BaseExporter):
            def export_tx(self, tx):
                received_b.append(tx)

        multi = MultiExporter([FakeA(), FakeB()])
        tx = AgentTx(amount=1.0)
        multi.export_tx(tx)

        self.assertEqual(len(received_a), 1)
        self.assertEqual(len(received_b), 1)

    def test_multi_exporter_isolates_errors(self):
        from agentfinobs import MultiExporter, BaseExporter

        received = []

        class BadExporter(BaseExporter):
            def export_tx(self, tx):
                raise RuntimeError("boom")

        class GoodExporter(BaseExporter):
            def export_tx(self, tx):
                received.append(tx)

        multi = MultiExporter([BadExporter(), GoodExporter()])
        tx = AgentTx(amount=1.0)
        multi.export_tx(tx)  # should not raise

        self.assertEqual(len(received), 1)

    def test_tracker_with_exporter(self):
        from agentfinobs import BaseExporter

        exported = []

        class CapturingExporter(BaseExporter):
            def export_tx(self, tx):
                exported.append(tx)

        tracker = SpendTracker(agent_id="test", exporters=[CapturingExporter()])
        tracker.record(amount=10.0, task_id="t1")
        tracker.record(amount=20.0, task_id="t2")

        # 2 records = 2 exports
        self.assertEqual(len(exported), 2)
        self.assertAlmostEqual(exported[0].amount, 10.0)

    def test_tracker_settle_exports(self):
        from agentfinobs import BaseExporter

        exported = []

        class CapturingExporter(BaseExporter):
            def export_tx(self, tx):
                exported.append(tx)

        tracker = SpendTracker(agent_id="test", exporters=[CapturingExporter()])
        tx = tracker.record(amount=5.0)
        tracker.settle(tx.tx_id, revenue=8.0)

        # 1 record + 1 settle = 2 exports
        self.assertEqual(len(exported), 2)
        # Second export should have the settled state
        self.assertAlmostEqual(exported[1].revenue, 8.0)

    def test_stack_with_exporters(self):
        from agentfinobs import BaseExporter

        exported = []

        class CapturingExporter(BaseExporter):
            def export_tx(self, tx):
                exported.append(tx)

        obs = ObservabilityStack.create(
            agent_id="exp-stack-test",
            exporters=[CapturingExporter()],
        )
        obs.track(amount=1.0)
        obs.track(amount=2.0)

        self.assertEqual(len(exported), 2)


class TestAgentTx(unittest.TestCase):
    def test_pnl_and_roi(self):
        tx = AgentTx(amount=10.0, revenue=15.0)
        self.assertAlmostEqual(tx.pnl, 5.0)
        self.assertAlmostEqual(tx.roi, 0.5)

    def test_zero_amount_roi(self):
        tx = AgentTx(amount=0.0, revenue=5.0)
        self.assertIsNone(tx.roi)

    def test_to_dict(self):
        tx = AgentTx(amount=10.0, agent_id="a1", task_id="t1")
        d = tx.to_dict()
        self.assertEqual(d["amount"], 10.0)
        self.assertEqual(d["agent_id"], "a1")
        self.assertIn("tx_id", d)


if __name__ == "__main__":
    unittest.main()
