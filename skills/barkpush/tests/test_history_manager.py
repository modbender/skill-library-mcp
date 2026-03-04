import tempfile
import unittest
from pathlib import Path

from bark_push.history_manager import HistoryManager, new_history_record


class TestHistoryManager(unittest.TestCase):
    def test_fifo_trim(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "history.json"
            hm = HistoryManager(history_path=path, limit=2)
            for i in range(3):
                rec = new_history_record(
                    push_id=f"id_{i}",
                    device_keys=["k"],
                    user_aliases=["u"],
                    title="t",
                    subtitle="",
                    body="b",
                    content_type="text_only",
                    parameters={},
                    status="success",
                    success_count=1,
                    failed_count=0,
                    failed_users=[],
                    error_messages={},
                    bark_response={},
                )
                hm.upsert(rec)
            recent = hm.list_recent(limit=10)
            self.assertEqual(len(recent), 2)
            ids = {r.id for r in recent}
            self.assertNotIn("id_0", ids)


if __name__ == "__main__":
    unittest.main()
