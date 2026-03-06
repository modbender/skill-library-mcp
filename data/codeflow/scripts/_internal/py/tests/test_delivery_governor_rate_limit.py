import io
import os
import sys
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, SCRIPT_DIR)

from delivery_errors import DeliveryRateLimited
from delivery_governor import DeliveryGovernor


class _FakeClock:
    def __init__(self, start: float = 0.0):
        self.t = float(start)
        self.sleeps: list[float] = []

    def now(self) -> float:
        return float(self.t)

    def sleep(self, seconds: float) -> None:
        sec = float(seconds)
        self.sleeps.append(sec)
        self.t += sec


class _RateLimitOncePlatform:
    MAX_TEXT = 50
    SUPPORTS_EDIT = True

    def __init__(self, *, retry_after: float):
        self.retry_after = float(retry_after)
        self.calls: list[tuple[str, str]] = []
        self._rate_limit_next = True

    def post_single_governed(self, text: str, name=None) -> int:
        self.calls.append(("post_single", text))
        if self._rate_limit_next:
            self._rate_limit_next = False
            raise DeliveryRateLimited(
                platform="telegram",
                op="post_single",
                code=429,
                retry_after=self.retry_after,
                reason="Too Many Requests",
            )
        return 123

    def edit_single_governed(self, message_id: int, text: str) -> bool:
        self.calls.append(("edit_single", text))
        return True


class DeliveryGovernorRateLimitTests(unittest.TestCase):
    def test_telegram_post_is_paginated_without_loss(self):
        class _RecordingPlatform:
            MAX_TEXT = 10
            SUPPORTS_EDIT = True

            def __init__(self):
                self.sent: list[str] = []
                self._mid = 1

            def post_single_governed(self, text: str, name=None) -> int:
                self.sent.append(text)
                mid = self._mid
                self._mid += 1
                return mid

            def edit_single_governed(self, message_id: int, text: str) -> bool:
                return True

        clock = _FakeClock()
        plat = _RecordingPlatform()
        gov = DeliveryGovernor(
            plat,
            platform_name="telegram",
            stream_log=io.StringIO(),
            delivery_stats={},
            clock=clock.now,
            sleeper=clock.sleep,
        )

        text = "A\n" + ("b" * 25) + "\nC\n"
        gov.submit_final(text)
        gov.flush()

        self.assertGreater(len(plat.sent), 1)
        self.assertTrue(all(len(x) <= plat.MAX_TEXT for x in plat.sent))
        self.assertEqual("".join(plat.sent), text)

    def test_flush_sleeps_retry_after_plus_one_no_cap(self):
        clock = _FakeClock()
        plat = _RateLimitOncePlatform(retry_after=23.5)
        stats: dict = {}

        gov = DeliveryGovernor(
            plat,
            platform_name="telegram",
            stream_log=io.StringIO(),
            delivery_stats=stats,
            clock=clock.now,
            sleeper=clock.sleep,
        )

        gov.submit_final("FINAL")
        gov.tick(max_ops=1)  # triggers rate limit and schedules retry
        self.assertEqual(len(plat.calls), 1)

        gov.flush()
        self.assertEqual(len(plat.calls), 2)
        self.assertEqual(clock.sleeps, [24.5])

    def test_flush_sleeps_retry_after_plus_one_when_retry_after_is_smaller(self):
        clock = _FakeClock()
        plat = _RateLimitOncePlatform(retry_after=2.0)
        gov = DeliveryGovernor(
            plat,
            platform_name="telegram",
            stream_log=io.StringIO(),
            delivery_stats={},
            clock=clock.now,
            sleeper=clock.sleep,
        )

        gov.submit_final("FINAL")
        gov.tick(max_ops=1)  # 429
        gov.flush()
        self.assertEqual(len(plat.calls), 2)
        self.assertEqual(clock.sleeps, [3.0])

    def test_rate_limit_blocks_requests_until_window_and_priority_final_first(self):
        clock = _FakeClock()
        plat = _RateLimitOncePlatform(retry_after=17.0)
        gov = DeliveryGovernor(
            plat,
            platform_name="telegram",
            stream_log=io.StringIO(),
            delivery_stats={},
            clock=clock.now,
            sleeper=clock.sleep,
        )

        gov.submit_state("think", "STATE")
        gov.tick(max_ops=1)  # attempt -> 429
        self.assertEqual([c[1] for c in plat.calls], ["STATE"])

        # Still within window: no more calls.
        gov.tick(max_ops=10)
        self.assertEqual(len(plat.calls), 1)

        # Enqueue a final message while rate-limited.
        gov.submit_final("FINAL")

        # Before window opens: still blocked.
        clock.t = 17.9
        gov.tick(max_ops=10)
        self.assertEqual(len(plat.calls), 1)

        # At window: final > state (state retry still pending).
        clock.t = 18.0
        gov.tick(max_ops=1)
        gov.tick(max_ops=1)
        self.assertEqual([c[1] for c in plat.calls], ["STATE", "FINAL", "STATE"])

    def test_state_latest_wins_while_rate_limited(self):
        clock = _FakeClock()
        plat = _RateLimitOncePlatform(retry_after=10.0)
        gov = DeliveryGovernor(
            plat,
            platform_name="telegram",
            stream_log=io.StringIO(),
            delivery_stats={},
            clock=clock.now,
            sleeper=clock.sleep,
        )

        gov.submit_state("cmd", "S1")
        gov.tick(max_ops=1)  # 429 on first attempt, pending remains

        # Still within window: multiple updates collapse to latest.
        clock.t = 1.0
        gov.submit_state("cmd", "S2")
        gov.tick(max_ops=10)
        gov.submit_state("cmd", "S3")
        gov.tick(max_ops=10)

        # At window: only the latest pending payload should be sent.
        clock.t = 11.0
        gov.tick(max_ops=10)

        # Calls: first attempt S1 (429), then successful S3.
        self.assertEqual([c[1] for c in plat.calls], ["S1", "S3"])

    def test_state_truncates_only_when_exceeding_platform_limit(self):
        class _SmallLimitPlatform:
            MAX_TEXT = 30
            SUPPORTS_EDIT = True

            def __init__(self):
                self.calls: list[tuple[str, str]] = []
                self._mid = 1

            def post_single_governed(self, text: str, name=None) -> int:
                self.calls.append(("post_single", text))
                mid = self._mid
                self._mid += 1
                return mid

            def edit_single_governed(self, message_id: int, text: str) -> bool:
                self.calls.append(("edit_single", text))
                return True

        clock = _FakeClock()
        plat = _SmallLimitPlatform()
        gov = DeliveryGovernor(
            plat,
            platform_name="telegram",
            stream_log=io.StringIO(),
            delivery_stats={},
            clock=clock.now,
            sleeper=clock.sleep,
        )

        gov.submit_state("think", "HEADER")
        gov.tick(max_ops=10)
        self.assertEqual(len(plat.calls), 1)
        self.assertNotIn("…(truncated)", plat.calls[0][1])

        # Snapshot pushes over MAX_TEXT -> governor truncates.
        gov.submit_state("think", "HEADER\n" + ("X" * 200))
        gov.tick(max_ops=10)
        self.assertEqual(len(plat.calls), 2)
        self.assertLessEqual(len(plat.calls[1][1]), plat.MAX_TEXT)
        self.assertIn("…(truncated)", plat.calls[1][1])


if __name__ == "__main__":
    unittest.main()
