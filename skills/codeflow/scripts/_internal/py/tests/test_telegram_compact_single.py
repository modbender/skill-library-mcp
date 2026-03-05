import os
import sys
import unittest


SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, SCRIPT_DIR)

from platforms import telegram as tg


class TelegramCompactSingleMessageTests(unittest.TestCase):
    def setUp(self):
        tg.BOT_TOKEN = "test-token"
        tg.CHAT_ID = "123"
        tg.THREAD_ID = ""
        tg.SILENT = True
        tg.TRACK_EDIT_GROUPS = True
        tg.EDIT_GROUPS_MAX = 64
        tg._EDIT_GROUPS.clear()

    def test_post_single_truncates_and_sends_once(self):
        sent: list[str] = []

        def fake_send_message(text: str):
            sent.append(text)
            return 111

        orig = tg._send_message
        tg._send_message = fake_send_message
        try:
            long_text = "HEADER\n" + ("x" * (tg.MAX_TEXT * 2))
            mid = tg.post_single(long_text)
            self.assertEqual(mid, 111)
            self.assertEqual(len(sent), 1)
            self.assertLessEqual(len(sent[0]), tg.MAX_TEXT)
            self.assertTrue(sent[0].startswith("HEADER\n"))
        finally:
            tg._send_message = orig

    def test_edit_single_clears_tail_and_truncates(self):
        deleted: list[int] = []
        edited: list[tuple[int, str]] = []

        tg._EDIT_GROUPS[999] = {"tail_ids": [1001, 1002], "chunks": ["a", "b", "c"]}

        def fake_delete_message(mid: int) -> bool:
            deleted.append(int(mid))
            return True

        def fake_edit_message(mid: int, text: str) -> bool:
            edited.append((int(mid), text))
            return True

        orig_delete = tg._delete_message
        orig_edit = tg._edit_message
        tg._delete_message = fake_delete_message
        tg._edit_message = fake_edit_message
        try:
            long_text = "HEADER\n" + ("y" * (tg.MAX_TEXT * 2))
            ok = tg.edit_single(999, long_text)
            self.assertTrue(ok)
            self.assertEqual(deleted, [1001, 1002])
            self.assertNotIn(999, tg._EDIT_GROUPS)
            self.assertEqual(len(edited), 1)
            self.assertEqual(edited[0][0], 999)
            self.assertLessEqual(len(edited[0][1]), tg.MAX_TEXT)
            self.assertTrue(edited[0][1].startswith("HEADER\n"))
        finally:
            tg._delete_message = orig_delete
            tg._edit_message = orig_edit

    def test_post_paginates_long_text_without_loss(self):
        sent: list[str] = []

        def fake_send_message(text: str):
            sent.append(text)
            return 200 + (len(sent) - 1)

        orig = tg._send_message
        tg._send_message = fake_send_message
        try:
            long_text = "Z" * (tg.MAX_TEXT * 2 + 50)
            anchor = tg.post(long_text)
            self.assertEqual(anchor, 200)
            self.assertGreaterEqual(len(sent), 2)
            self.assertEqual("".join(sent), long_text)

            state = tg._EDIT_GROUPS.get(200)
            self.assertIsInstance(state, dict)
            self.assertEqual(state.get("chunks"), sent)
            self.assertEqual(state.get("tail_ids"), list(range(201, 200 + len(sent))))
        finally:
            tg._send_message = orig

    def test_edit_groups_are_lru_capped(self):
        # Ensure long sessions don't retain unbounded chunks/tail_ids in memory.
        tg.TRACK_EDIT_GROUPS = True
        tg.EDIT_GROUPS_MAX = 2

        next_id = 1000

        def fake_send_message(text: str):
            nonlocal next_id
            mid = next_id
            next_id += 1
            return mid

        orig = tg._send_message
        tg._send_message = fake_send_message
        try:
            long_text = "Z" * (tg.MAX_TEXT * 2 + 50)
            anchors = [tg.post(long_text), tg.post(long_text), tg.post(long_text)]

            self.assertLessEqual(len(tg._EDIT_GROUPS), 2)
            self.assertNotIn(int(anchors[0]), tg._EDIT_GROUPS)
            self.assertIn(int(anchors[1]), tg._EDIT_GROUPS)
            self.assertIn(int(anchors[2]), tg._EDIT_GROUPS)
        finally:
            tg._send_message = orig


if __name__ == "__main__":
    unittest.main()
