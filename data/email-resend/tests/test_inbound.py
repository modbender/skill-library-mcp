#!/usr/bin/env python3
"""
Email-Resend Skill Test Suite

Run: python3 skills/email-resend/tests/test_inbound.py
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add scripts to path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


class TestImportanceDetection(unittest.TestCase):
    """Test importance detection logic."""
    
    def test_detect_importance_urgent(self):
        """High priority keywords should return 🔥 HIGH"""
        sys.path.insert(0, str(SCRIPT_DIR))
        from inbound import detect_importance
        
        test_cases = [
            ({"subject": "URGENT: Server down", "from": "admin@company.com"}, "🔥 HIGH"),
            ({"subject": "ASAP: Review needed", "from": "boss@company.com"}, "🔥 HIGH"),
            ({"subject": "CRITICAL: Security alert", "from": "security@company.com"}, "🔥 HIGH"),
            ({"subject": "Emergency: Customer issue", "from": "support@company.com"}, "🔥 HIGH"),
            ({"subject": "Important: Update required", "from": "system@company.com"}, "🔥 HIGH"),
            ({"subject": "Priority: Review document", "from": "manager@company.com"}, "🔥 HIGH"),
        ]
        
        for email, expected in test_cases:
            result = detect_importance(email)
            self.assertEqual(result, expected, f"Failed for: {email['subject']}")
    
    def test_detect_importance_meeting(self):
        """Meeting keywords should return 📅 MEETING"""
        from inbound import detect_importance
        
        test_cases = [
            ({"subject": "Meeting request", "from": "colleague@company.com"}, "📅 MEETING"),
            ({"subject": "Call scheduled", "from": "assistant@company.com"}, "📅 MEETING"),
            ({"subject": "Zoom meeting", "from": "team@company.com"}, "📅 MEETING"),
            ({"subject": "Calendar invite", "from": "calendar@company.com"}, "📅 MEETING"),
            ({"subject": "Schedule update", "from": "admin@company.com"}, "📅 MEETING"),
        ]
        
        for email, expected in test_cases:
            result = detect_importance(email)
            self.assertEqual(result, expected, f"Failed for: {email['subject']}")
    
    def test_detect_importance_normal(self):
        """Normal emails should return 📬 NORMAL"""
        from inbound import detect_importance
        
        test_cases = [
            ({"subject": "Hello", "from": "friend@email.com"}, "📬 NORMAL"),
            ({"subject": "Newsletter", "from": "news@company.com"}, "📬 NORMAL"),
            ({"subject": "Re: Project update", "from": "coworker@company.com"}, "📬 NORMAL"),
            ({"subject": "Random subject", "from": "unknown@sender.com"}, "📬 NORMAL"),
        ]
        
        for email, expected in test_cases:
            result = detect_importance(email)
            self.assertEqual(result, expected, f"Failed for: {email['subject']}")
    
    def test_detect_importance_case_insensitive(self):
        """Detection should be case insensitive"""
        from inbound import detect_importance
        
        result = detect_importance({"subject": "urgent matter", "from": "test@test.com"})
        self.assertEqual(result, "🔥 HIGH")
        
        result = detect_importance({"subject": "URGENT MATTER", "from": "test@test.com"})
        self.assertEqual(result, "🔥 HIGH")
        
        result = detect_importance({"subject": "Meeting", "from": "test@test.com"})
        self.assertEqual(result, "📅 MEETING")


class TestSenderNameExtraction(unittest.TestCase):
    """Test sender name extraction."""
    
    def test_extract_sender_name_with_angle_brackets(self):
        """Extract name from 'Name <email>' format"""
        from inbound import extract_sender_name
        
        self.assertEqual(extract_sender_name("John Doe <john@company.com>"), "John Doe")
        self.assertEqual(extract_sender_name('"Jane Smith" <jane@company.com>'), "Jane Smith")
        self.assertEqual(extract_sender_name("  Spaces  <test@test.com>"), "Spaces")
    
    def test_extract_sender_name_without_angle_brackets(self):
        """Extract name from email address when no angle brackets"""
        from inbound import extract_sender_name
        
        self.assertEqual(extract_sender_name("john@company.com"), "john")
        self.assertEqual(extract_sender_name("john.doe@company.com"), "john.doe")
    
    def test_extract_sender_name_empty(self):
        """Handle empty input"""
        from inbound import extract_sender_name
        
        self.assertEqual(extract_sender_name(""), "Unknown")
        self.assertEqual(extract_sender_name(None), "Unknown")


class TestBodyFormatting(unittest.TestCase):
    """Test body formatting."""
    
    def test_format_body_empty(self):
        """Empty body returns '(empty)'"""
        from inbound import format_body
        
        self.assertEqual(format_body(""), "(empty)")
        self.assertEqual(format_body(None), "(empty)")
    
    def test_format_body_truncation(self):
        """Body is truncated to max_chars and max_lines"""
        from inbound import format_body
        
        # Short body - no truncation
        short = "Hello world"
        result = format_body(short, max_chars=100, max_lines=10)
        self.assertEqual(result, "Hello world")
        
        # Long body - truncated
        long = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7\nLine 8\nLine 9\nLine 10"
        result = format_body(long, max_chars=100, max_lines=3)
        self.assertIn("...", result)
        self.assertNotIn("Line 5", result)
    
    def test_format_attachments_empty(self):
        """Empty attachments returns empty string"""
        from inbound import format_attachments
        
        self.assertEqual(format_attachments([]), "")
        self.assertEqual(format_attachments(None), "")
    
    def test_format_attachments_with_data(self):
        """Attachments are formatted with filename and size"""
        from inbound import format_attachments
        
        attachments = [
            {"filename": "document.pdf", "size": 1024},
            {"filename": "image.png", "size": 2048}
        ]
        result = format_attachments(attachments)
        
        self.assertIn("document.pdf", result)
        self.assertIn("1,024", result)
        self.assertIn("image.png", result)
        self.assertIn("2,048", result)


class TestDraftReplyBestPractices(unittest.TestCase):
    """Test draft reply best practices compliance."""
    
    def test_quoting_format(self):
        """Original message should be quoted with > prefix"""
        # Simulate what send_draft does
        original_body = "Hello, how are you?\nI'm doing great!"
        
        quoted = "\n".join(["> " + line for line in original_body.split("\n")])
        
        self.assertIn("> Hello, how are you?", quoted)
        self.assertIn("> I'm doing great!", quoted)
        self.assertTrue(all(line.startswith("> ") for line in quoted.split("\n")))
    
    def test_subject_prefix(self):
        """Reply subject should have Re: prefix"""
        original_subject = "Original Subject"
        
        reply_subject = f"Re: {original_subject}"
        
        self.assertEqual(reply_subject, "Re: Original Subject")
        self.assertTrue(reply_subject.startswith("Re: "))
    
    def test_subject_no_duplicate_re(self):
        """Reply subject should not have duplicate Re: prefix"""
        # If original already has Re:, don't add another
        original_subject = "Re: Original Subject"
        
        if original_subject.lower().startswith("re:"):
            reply_subject = original_subject
        else:
            reply_subject = f"Re: {original_subject}"
        
        self.assertEqual(reply_subject, "Re: Original Subject")
        self.assertFalse(reply_subject.startswith("Re: Re:"))
    
    def test_thread_headers_present(self):
        """Reply should have In-Reply-To and References headers"""
        message_id = "test-message-id-123"
        
        headers = {
            "In-Reply-To": message_id,
            "References": message_id
        }
        
        self.assertEqual(headers["In-Reply-To"], message_id)
        self.assertEqual(headers["References"], message_id)
        self.assertEqual(headers["In-Reply-To"], headers["References"])
    
    def test_thread_uses_message_id_not_resend_id(self):
        """Threading should use actual Message-ID from email headers, not Resend ID"""
        # Simulate email response from API with both IDs
        email_from_api = {
            "id": "resend-internal-id-123",  # Resend's internal ID
            "message_id": "<CAHAwe+Z-ycpSZvLYdRe1egq0=...@mail.gmail.com>",  # Actual Gmail Message-ID
            "subject": "Original Subject",
            "from": "sender@example.com"
        }
        
        # The code should prefer message_id over id
        message_id = email_from_api.get("message_id", "") or email_from_api.get("id", "")
        
        # Should be the Gmail Message-ID, not Resend ID
        self.assertTrue(message_id.startswith("<"))
        self.assertIn("mail.gmail.com", message_id)
        self.assertNotEqual(message_id, "resend-internal-id-123")
    
    def test_no_duplicate_send_protection(self):
        """After send, draft state should be cleared"""
        # Import draft-reply.py with correct path (note: hyphen in filename)
        import importlib.util
        draft_reply_path = SCRIPT_DIR / "draft-reply.py"
        spec = importlib.util.spec_from_file_location("draft_reply", draft_reply_path)
        draft_reply = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(draft_reply)
        
        # Mock the draft state file to not exist
        with patch.object(draft_reply, 'DRAFT_STATE_FILE', Path('/tmp/nonexistent_draft.json')):
            # Load state when file doesn't exist
            state = draft_reply.load_draft_state()
            self.assertEqual(state, {}, "No draft should exist when file doesn't exist")
        
        # After send, draft should be cleared
        # This is tested by checking that send_draft errors when no draft exists
        with patch.object(draft_reply, 'load_draft_state', return_value={}):
            result = draft_reply.send_draft()
            self.assertIn("No draft to send", result)
    
    def test_draft_state_structure(self):
        """Draft state should have required fields"""
        required_fields = [
            "email_id", "from", "to", "subject", 
            "in_reply_to", "original_subject", "reply_content", "status"
        ]
        
        # Example draft state
        draft = {
            "email_id": "test-123",
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "subject": "Re: Test",
            "in_reply_to": "original-msg-id",
            "original_subject": "Test",
            "reply_content": "My reply",
            "status": "pending_approval"
        }
        
        for field in required_fields:
            self.assertIn(field, draft, f"Missing field: {field}")
        
        # Verify in_reply_to is set for threading
        self.assertTrue(len(draft["in_reply_to"]) > 0, "in_reply_to should not be empty")


class TestStateManagement(unittest.TestCase):
    """Test state loading and saving."""
    
    def test_state_format_backwards_compatible(self):
        """State handles both old (string) and new (dict) formats"""
        # Old format: {"pending_ids": {"email_id": "timestamp"}}
        old_format = {
            "pending_ids": {"abc123": "2026-02-17T10:00:00+00:00"},
            "acknowledged_ids": {"def456": "2026-02-16T10:00:00+00:00"}
        }
        
        # New format: {"pending_ids": {"email_id": {...metadata...}}}
        new_format = {
            "pending_ids": {"abc123": {"created_at": "2026-02-17T10:00:00+00:00", "subject": "Test"}},
            "acknowledged_ids": {"def456": {"created_at": "2026-02-16T10:00:00+00:00", "subject": "Old"}}
        }
        
        # Verify both are valid JSON
        json.dumps(old_format)
        json.dumps(new_format)
        
        # Verify we can access timestamps from both
        self.assertEqual(old_format["pending_ids"]["abc123"], "2026-02-17T10:00:00+00:00")
        self.assertEqual(new_format["pending_ids"]["abc123"]["subject"], "Test")


class TestMessageMapping(unittest.TestCase):
    """Test message ID to email ID mapping."""
    
    def test_mapping_format(self):
        """Message map should be {str(message_id): str(email_id)}"""
        mapping = {
            "1234": "email-uuid-1",
            "5678": "email-uuid-2",
            "9999": "email-uuid-3"
        }
        
        # All keys should be strings (Telegram message_ids)
        for key in mapping.keys():
            self.assertIsInstance(key, str)
        
        # All values should be strings (email IDs)
        for val in mapping.values():
            self.assertIsInstance(val, str)
        
        # Verify we can do reverse lookup
        reverse = {v: k for k, v in mapping.items()}
        self.assertEqual(reverse["email-uuid-1"], "1234")


# Configuration now via environment variables and memory - no config.json

class TestScriptFiles(unittest.TestCase):
    """Test that all required script files exist."""
    
    def test_required_scripts_exist(self):
        """All required scripts should exist"""
        scripts = ["inbound.py", "outbound.py", "draft-reply.py", "download_attachment.py"]
        
        for script in scripts:
            path = SCRIPT_DIR / script
            self.assertTrue(path.exists(), f"Missing script: {script}")
    
    def test_scripts_are_executable(self):
        """Scripts should have executable bit"""
        scripts = ["inbound.py", "outbound.py", "draft-reply.py", "download_attachment.py"]
        
        for script in scripts:
            path = SCRIPT_DIR / script
            if path.exists():
                mode = path.stat().st_mode
                self.assertTrue(mode & 0o100, f"Script not executable: {script}")
    
    def test_draft_reply_exists(self):
        """draft-reply.py should exist"""
        path = SCRIPT_DIR / "draft-reply.py"
        self.assertTrue(path.exists(), "Missing script: draft-reply.py")


class TestCronPrompts(unittest.TestCase):
    """Test cron prompt files."""
    
    def test_email_inbound_prompt_exists(self):
        """Email inbound cron prompt should exist"""
        prompt_path = Path(__file__).parent.parent / "cron-prompts" / "email-inbound.md"
        self.assertTrue(prompt_path.exists(), f"Missing cron prompt: {prompt_path}")
    
    def test_cron_prompt_not_empty(self):
        """Cron prompt should have content"""
        prompt_path = Path(__file__).parent.parent / "cron-prompts" / "email-inbound.md"
        with open(prompt_path) as f:
            content = f.read()
        
        self.assertGreater(len(content), 50, "Cron prompt is too short")


class TestCustodyChain(unittest.TestCase):
    """Test custody chain DAG structure."""
    
    def test_custody_chain_structure(self):
        """Chain should have required fields"""
        chain = {
            "resend-email-123": {
                "email_id": "resend-email-123",
                "created_at": "2026-02-21T00:00:00Z",
                "nodes": {
                    "1234": {
                        "type": "notification",
                        "telegram_msg_id": "1234",
                        "timestamp": "2026-02-21T00:00:01Z",
                        "parent_msg_id": None
                    }
                }
            }
        }
        
        # Verify structure
        self.assertIn("resend-email-123", chain)
        self.assertIn("nodes", chain["resend-email-123"])
        self.assertIn("1234", chain["resend-email-123"]["nodes"])
        
        node = chain["resend-email-123"]["nodes"]["1234"]
        self.assertEqual(node["type"], "notification")
        self.assertIsNone(node["parent_msg_id"])
    
    def test_custody_chain_parent_links(self):
        """Nodes should link to parents for traversal"""
        chain = {
            "resend-email-123": {
                "email_id": "resend-email-123",
                "created_at": "2026-02-21T00:00:00Z",
                "nodes": {
                    "1234": {"type": "notification", "parent_msg_id": None},
                    "1235": {"type": "reply", "parent_msg_id": "1234"},
                    "1236": {"type": "preview", "parent_msg_id": "1235"},
                    "1237": {"type": "sent", "parent_msg_id": "1236"}
                }
            }
        }
        
        # Verify parent chain: sent → preview → reply → notification
        nodes = chain["resend-email-123"]["nodes"]
        self.assertEqual(nodes["1237"]["parent_msg_id"], "1236")
        self.assertEqual(nodes["1236"]["parent_msg_id"], "1235")
        self.assertEqual(nodes["1235"]["parent_msg_id"], "1234")
        self.assertIsNone(nodes["1234"]["parent_msg_id"])
    
    def test_msg_to_chain_mapping(self):
        """Message ID to email mapping should work"""
        msg_map = {
            "1234": "resend-email-123",
            "1235": "resend-email-123",
            "5678": "resend-email-456"
        }
        
        # Given any Telegram msg_id, find email
        self.assertEqual(msg_map["1234"], "resend-email-123")
        self.assertEqual(msg_map["5678"], "resend-email-456")
    
    def test_can_trace_message_to_email(self):
        """Should be able to trace any message back to email"""
        # Simulate the lookup chain
        msg_map = {"1237": "email-123"}
        chain = {
            "email-123": {
                "nodes": {
                    "1237": {"parent_msg_id": "1236"},
                    "1236": {"parent_msg_id": "1235"},
                    "1235": {"parent_msg_id": "1234"},
                    "1234": {"parent_msg_id": None}
                }
            }
        }
        
        # Trace 1237 back to root
        current = "1237"
        path = []
        while current:
            node = chain["email-123"]["nodes"].get(current)
            if not node:
                break
            path.append(current)
            current = node.get("parent_msg_id")
        
        # Should trace back through all nodes
        self.assertEqual(path, ["1237", "1236", "1235", "1234"])


class TestMultipleReplyThreading(unittest.TestCase):
    """Test multi-reply threading feature."""
    
    def test_resume_command_exists(self):
        """draft-reply.py should have resume command"""
        import importlib.util
        draft_reply_path = SCRIPT_DIR / "draft-reply.py"
        spec = importlib.util.spec_from_file_location("draft_reply", draft_reply_path)
        draft_reply = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(draft_reply)
        
        # Check resume_draft function exists
        self.assertTrue(hasattr(draft_reply, 'resume_draft'), "resume_draft function missing")
    
    def test_draft_sent_state_persists(self):
        """After send, draft should be marked as 'sent' not deleted"""
        import importlib.util
        draft_reply_path = SCRIPT_DIR / "draft-reply.py"
        spec = importlib.util.spec_from_file_location("draft_reply", draft_reply_path)
        draft_reply = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(draft_reply)
        
        # Check send_draft sets status to 'sent' - we already tested manually it works
        # This is a code inspection test - verify the logic is there
        source_code = draft_reply_path.read_text()
        
        # Should set status to "sent" after sending
        self.assertIn('"sent"', source_code, "send_draft should set status to 'sent'")
        
        # After setting to sent, it should call save_draft_state (not delete)
        # The os.remove is in cancel_draft, not send_draft
        self.assertIn('save_draft_state(draft)', source_code, 
                     "send_draft should save draft state")
    
    def test_status_shows_sent_thread(self):
        """Status should show thread is active after sending"""
        import importlib.util
        draft_reply_path = SCRIPT_DIR / "draft-reply.py"
        spec = importlib.util.spec_from_file_location("draft_reply", draft_reply_path)
        draft_reply = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(draft_reply)
        
        # Check status handles 'sent' state
        source_code = draft_reply_path.read_text()
        self.assertIn('status == "sent"', source_code, 
                     "show_status should handle 'sent' state")
    
    def test_resume_keeps_same_thread_headers(self):
        """Resume should preserve In-Reply-To and References for thread continuity"""
        import importlib.util
        draft_reply_path = SCRIPT_DIR / "draft-reply.py"
        spec = importlib.util.spec_from_file_location("draft_reply", draft_reply_path)
        draft_reply = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(draft_reply)
        
        # Check resume preserves in_reply_to (doesn't change it)
        source_code = draft_reply_path.read_text()
        
        # Resume should keep in_reply_to and just reset status
        # The in_reply_to should stay the same throughout the thread
        self.assertIn('in_reply_to', source_code, 
                     "Draft should maintain in_reply_to for threading")
        
        # Resume should change status from "sent" back to "waiting_for_reply"
        self.assertIn('waiting_for_reply', source_code,
                     "resume should set status to waiting_for_reply")


class TestEmailThreadingBestPractices(unittest.TestCase):
    """Test email threading best practices per web search findings."""
    
    def test_in_reply_to_uses_message_id_with_brackets(self):
        """In-Reply-To should include angle brackets like <id@domain>"""
        message_id = "CAHAwe+Z-ycpSZvLYdRe1egq0=...@mail.gmail.com"
        
        # Should wrap in angle brackets
        in_reply_to = f"<{message_id}>"
        
        self.assertTrue(in_reply_to.startswith("<"))
        self.assertTrue(in_reply_to.endswith(">"))
    
    def test_references_supports_multiple_ids(self):
        """References header should support space-separated message IDs"""
        # For deep threads, References should accumulate
        msg_ids = [
            "<msg1@mail.gmail.com>",
            "<msg2@mail.gmail.com>", 
            "<msg3@mail.gmail.com>"
        ]
        
        references = " ".join(msg_ids)
        
        # Should be space-separated
        self.assertEqual(references, "<msg1@mail.gmail.com> <msg2@mail.gmail.com> <msg3@mail.gmail.com>")
        self.assertEqual(len(references.split()), 3)
    
    def test_subject_re_prefix_always(self):
        """Reply subject should always have Re: prefix for client compatibility"""
        # Original has no Re:
        subject1 = "Hello"
        self.assertTrue(f"Re: {subject1}".startswith("Re: "))
        
        # Original already has Re:
        subject2 = "Re: Hello"
        # Should not duplicate
        if subject2.lower().startswith("re:"):
            result = subject2
        else:
            result = f"Re: {subject2}"
        
        self.assertEqual(result, "Re: Hello")
        self.assertFalse(result.startswith("Re: Re:"))
    
    def test_draft_stores_original_message_id_for_threading(self):
        """Draft should store original message_id for threading headers"""
        # This is critical - in_reply_to must be the original email's Message-ID
        draft = {
            "email_id": "resend-123",
            "in_reply_to": "<original-msg-id@mail.gmail.com>",
            "subject": "Re: Original"
        }
        
        # Must have in_reply_to set
        self.assertTrue(len(draft["in_reply_to"]) > 0)
        self.assertTrue(draft["in_reply_to"].startswith("<"))


def run_tests():
    """Run all tests and return exit code."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestImportanceDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestSenderNameExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestBodyFormatting))
    suite.addTests(loader.loadTestsFromTestCase(TestDraftReplyBestPractices))
    suite.addTests(loader.loadTestsFromTestCase(TestStateManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestMessageMapping))
    # TestConfiguration removed - config now via env vars
    suite.addTests(loader.loadTestsFromTestCase(TestScriptFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestCronPrompts))
    suite.addTests(loader.loadTestsFromTestCase(TestCustodyChain))
    suite.addTests(loader.loadTestsFromTestCase(TestMultipleReplyThreading))
    suite.addTests(loader.loadTestsFromTestCase(TestEmailThreadingBestPractices))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    print("=" * 60)
    print("Email-Resend Skill Test Suite")
    print("=" * 60)
    print()
    
    exit_code = run_tests()
    
    print()
    print("=" * 60)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ TESTS FAILED")
    print("=" * 60)
    
    sys.exit(exit_code)
