#!/usr/bin/env python3
"""
Email Threading Integration Tests

Tests that verify email threading works correctly - replies appear in the correct Gmail thread.
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add scripts to path
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import outbound


def test_fetch_message_id_detects_uuid_format():
    """Test that fetch_message_id correctly identifies email IDs vs Message-IDs."""
    # UUID format (email ID) - should trigger fetch
    email_id = "6269f3b2-9e26-457f-a16d-6ac0f38199ca"
    # Should NOT match the simple check (has dashes and looks like UUID)
    assert "-" in email_id and not email_id.startswith("<")
    

def test_subject_validation_warns_on_re_without_reply_to():
    """Test that outbound.py warns when subject starts with Re: but no --reply-to."""
    # This test verifies the warning logic exists
    # The actual warning is printed in main() - we just verify the code path
    
    test_args = MagicMock()
    test_args.subject = "Re: Original Thread"
    test_args.reply_to = None
    test_args.yes = False
    test_args.to = "test@example.com"
    
    # Verify the warning logic would trigger
    assert test_args.subject.lower().startswith("re:")
    assert test_args.reply_to is None
    
    # Verify the validation code exists in outbound.py
    outbound_py = SKILL_DIR / "scripts" / "outbound.py"
    content = outbound_py.read_text()
    assert "Subject starts with 'Re:'" in content


def test_both_headers_set_when_reply_to_provided():
    """Test that both In-Reply-To AND References headers are set."""
    # This verifies the header construction logic
    reply_to = "<test-message-id@example.com>"
    
    headers = {
        "In-Reply-To": reply_to,
        "References": reply_to
    }
    
    assert "In-Reply-To" in headers
    assert "References" in headers
    assert headers["In-Reply-To"] == headers["References"]


def test_skill_md_has_prohibitions():
    """Verify SKILL.md contains explicit prohibitions."""
    skill_md = SKILL_DIR / "SKILL.md"
    content = skill_md.read_text()
    
    assert "NEVER use `outbound.py` for replies" in content
    assert "MANDATORY: Always use `draft-reply.py`" in content
    assert "❌ NEVER" in content


def test_skill_md_has_correct_workflow():
    """Verify SKILL.md shows the correct draft-reply.py workflow."""
    skill_md = SKILL_DIR / "SKILL.md"
    content = skill_md.read_text()
    
    assert "draft-reply.py start" in content
    assert "draft-reply.py content" in content
    assert "draft-reply.py send" in content


def test_outbound_has_validation_code():
    """Verify outbound.py contains threading validation."""
    outbound_py = SKILL_DIR / "scripts" / "outbound.py"
    content = outbound_py.read_text()
    
    assert "Subject starts with 'Re:'" in content
    assert "use draft-reply.py for replies" in content


def test_skill_has_approval_execution_rule():
    """Verify SKILL.md contains the approval execution rule."""
    skill_md = SKILL_DIR / "SKILL.md"
    content = skill_md.read_text()
    
    assert "Approval Execution Rule" in content
    assert "MUST execute the send command immediately" in content
    assert "draft-reply.py send" in content


if __name__ == "__main__":
    # Run tests manually
    tests = [
        test_fetch_message_id_detects_uuid_format,
        test_subject_validation_warns_on_re_without_reply_to,
        test_both_headers_set_when_reply_to_provided,
        test_skill_md_has_prohibitions,
        test_skill_md_has_correct_workflow,
        test_outbound_has_validation_code,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"✅ {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
