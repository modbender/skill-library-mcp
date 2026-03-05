#!/usr/bin/env python3
"""
Email Attachment Downloader Tests

Tests for the download_attachment.py script.
"""

import json
import os
import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

# Add scripts to path
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))


def test_script_exists():
    """Verify download_attachment.py exists."""
    script_path = SKILL_DIR / "scripts" / "download_attachment.py"
    assert script_path.exists(), "download_attachment.py should exist"


def test_script_has_list_function():
    """Verify script has list_attachments function."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "download_attachment", 
        SKILL_DIR / "scripts" / "download_attachment.py"
    )
    module = importlib.util.module_from_spec(spec)
    
    # Check the source has the function defined
    source = (SKILL_DIR / "scripts" / "download_attachment.py").read_text()
    assert "def list_attachments" in source
    assert "def download_attachment_url" in source


def test_script_uses_correct_api_path():
    """Verify script uses /emails/receiving/{email_id}/attachments path."""
    source = (SKILL_DIR / "scripts" / "download_attachment.py").read_text()
    assert "/emails/receiving/" in source, "Should use /emails/receiving/ path"


def test_script_handles_attachment_download():
    """Verify script has download functionality."""
    source = (SKILL_DIR / "scripts" / "download_attachment.py").read_text()
    assert "download_url" in source
    assert "requests.get" in source


def test_script_has_cli_argument_parsing():
    """Verify script has CLI arguments."""
    source = (SKILL_DIR / "scripts" / "download_attachment.py").read_text()
    assert "argparse" in source
    assert "--list" in source or "-l" in source
    assert "--output-dir" in source or "-o" in source


def test_skill_md_documents_attachment_download():
    """Verify SKILL.md documents the attachment feature."""
    skill_md = SKILL_DIR / "SKILL.md"
    content = skill_md.read_text()
    
    # Should mention download_attachment or attachments
    assert "attachment" in content.lower()


def test_outbound_has_attachment_argument():
    """Verify outbound.py supports --attachment flag."""
    source = (SKILL_DIR / "scripts" / "outbound.py").read_text()
    assert "--attachment" in source or "-a" in source
    assert "attachments" in source.lower()
    assert "base64" in source


def test_outbound_attachment_content_types():
    """Verify outbound.py handles common content types."""
    source = (SKILL_DIR / "scripts" / "outbound.py").read_text()
    assert "application/pdf" in source
    assert "text/calendar" in source
    assert "application/vnd.apple.pkpass" in source


def test_outbound_send_email_accepts_attachments():
    """Verify send_email function accepts attachments parameter."""
    source = (SKILL_DIR / "scripts" / "outbound.py").read_text()
    # Check function signature includes attachments
    assert "def send_email" in source
    assert "attachments: list" in source or "attachments=" in source


def test_draft_reply_has_acknowledge_function():
    """Verify draft-reply.py has acknowledge_email function."""
    source = (SKILL_DIR / "scripts" / "draft-reply.py").read_text()
    assert "def acknowledge_email" in source
    assert "load_state" in source
    assert "save_state" in source


def test_draft_reply_calls_acknowledge_after_send():
    """Verify draft-reply.py calls acknowledge_email after sending."""
    source = (SKILL_DIR / "scripts" / "draft-reply.py").read_text()
    # Check that acknowledge_email is called after successful send
    assert "acknowledge_email(email_id)" in source


@unittest.skip("Demo test - expects specific ClawCon event files")
def test_clawcon_attachments_worked():
    """Integration test: Verify ClawCon attachments were actually downloaded."""
    attachments_dir = Path.home() / ".openclaw" / "workspace" / "temp" / "clawcon-attachments"
    
    pkpass = attachments_dir / "ClawCon_Austin.pkpass"
    ics = attachments_dir / "invite.ics"
    
    assert pkpass.exists(), "ClawCon pkpass should exist"
    assert ics.exists(), "invite.ics should exist"
    
    # Verify sizes match expected
    assert pkpass.stat().st_size == 12986, "pkpass size mismatch"
    assert ics.stat().st_size == 1313, "ics size mismatch"


if __name__ == "__main__":
    tests = [
        test_script_exists,
        test_script_has_list_function,
        test_script_uses_correct_api_path,
        test_script_handles_attachment_download,
        test_script_has_cli_argument_parsing,
        test_skill_md_documents_attachment_download,
        test_clawcon_attachments_worked,
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
