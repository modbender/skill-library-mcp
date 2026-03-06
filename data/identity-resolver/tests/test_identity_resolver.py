#!/usr/bin/env python3
# Run with: uv run python test_identity_resolver.py
"""
test_identity_resolver.py - Unit tests for identity-resolver

Run with: python3 test_identity_resolver.py

Author: OpenClaw Agent <agent@openclaw.local>
License: MIT
"""

import unittest
import tempfile
import shutil
import json
import os
import sys
from pathlib import Path

# Import from parent scripts/ directory
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from identity import (
    resolve_canonical_id,
    add_channel,
    remove_channel,
    list_identities,
    get_channels,
    is_owner,
    _sanitize_canonical_id,
    _load_identity_map,
    _save_identity_map
)

class TestIdentityResolver(unittest.TestCase):
    """Test suite for identity-resolver core API."""
    
    def setUp(self):
        """Create temporary workspace for each test."""
        self.workspace = tempfile.mkdtemp(prefix="identity-test-")
        self.workspace_path = Path(self.workspace)
        
        # Create USER.md with owner data
        user_md = self.workspace_path / "USER.md"
        user_md.write_text("""# USER.md

- **Name:** Test User
- **Contact Numbers:** 
  - **WhatsApp:** +1234567890 (primary)
  - **Other:** +9876543210, +5555555555
- **Telegram ID:** 123456789
""")
    
    def tearDown(self):
        """Clean up temporary workspace."""
        shutil.rmtree(self.workspace, ignore_errors=True)
    
    # === Sanitization Tests ===
    
    def test_sanitize_canonical_id_valid(self):
        """Test valid canonical ID sanitization."""
        self.assertEqual(_sanitize_canonical_id("alice"), "alice")
        self.assertEqual(_sanitize_canonical_id("alice-123"), "alice-123")
        self.assertEqual(_sanitize_canonical_id("user_42"), "user_42")
    
    def test_sanitize_canonical_id_uppercase(self):
        """Test uppercase gets lowercased."""
        self.assertEqual(_sanitize_canonical_id("BOWEN"), "alice")
        self.assertEqual(_sanitize_canonical_id("Alice"), "alice")
    
    def test_sanitize_canonical_id_special_chars(self):
        """Test special characters removed."""
        self.assertEqual(_sanitize_canonical_id("user@example.com"), "userexamplecom")
        self.assertEqual(_sanitize_canonical_id("alice/bob"), "alicebob")
    
    def test_sanitize_canonical_id_path_traversal(self):
        """Test path traversal patterns sanitized safely."""
        # Path traversal characters removed → safe
        self.assertEqual(_sanitize_canonical_id("../etc/passwd"), "etcpasswd")
        self.assertEqual(_sanitize_canonical_id(".hidden"), "hidden")
        self.assertEqual(_sanitize_canonical_id("a/b"), "ab")
        
        # Empty string rejected
        with self.assertRaises(ValueError):
            _sanitize_canonical_id("")
        
        # Only special chars rejected (becomes empty after sanitization)
        with self.assertRaises(ValueError):
            _sanitize_canonical_id("...")
    
    def test_sanitize_canonical_id_max_length(self):
        """Test max length enforcement."""
        long_id = "a" * 100
        sanitized = _sanitize_canonical_id(long_id)
        self.assertLessEqual(len(sanitized), 64)
    
    # === Auto-Registration Tests ===
    
    def test_resolve_owner_auto_register_telegram(self):
        """Test owner auto-registers from Telegram ID."""
        canonical_id = resolve_canonical_id("telegram", "123456789", self.workspace)
        self.assertEqual(canonical_id, "test")  # From USER.md name
        
        # Verify registered
        identities = list_identities(self.workspace)
        self.assertIn("test", identities)
        self.assertTrue(identities["test"]["is_owner"])
        self.assertIn("telegram:123456789", identities["test"]["channels"])
    
    def test_resolve_owner_auto_register_whatsapp(self):
        """Test owner auto-registers from WhatsApp number."""
        canonical_id = resolve_canonical_id("whatsapp", "+1234567890", self.workspace)
        self.assertEqual(canonical_id, "test")
        
        # Verify all owner numbers work
        self.assertEqual(resolve_canonical_id("whatsapp", "+9876543210", self.workspace), "test")
        self.assertEqual(resolve_canonical_id("whatsapp", "+5555555555", self.workspace), "test")
    
    def test_resolve_owner_multiple_channels_same_canonical(self):
        """Test multiple owner channels resolve to same canonical ID."""
        id1 = resolve_canonical_id("telegram", "123456789", self.workspace)
        id2 = resolve_canonical_id("whatsapp", "+1234567890", self.workspace)
        id3 = resolve_canonical_id("whatsapp", "+9876543210", self.workspace)
        
        self.assertEqual(id1, id2)
        self.assertEqual(id2, id3)
        
        # Verify all channels in one identity
        channels = get_channels(id1, self.workspace)
        self.assertIn("telegram:123456789", channels)
        self.assertIn("whatsapp:+1234567890", channels)
        self.assertIn("whatsapp:+9876543210", channels)
    
    # === Stranger Fallback Tests ===
    
    def test_resolve_stranger_unmapped(self):
        """Test unmapped user returns stranger format."""
        canonical_id = resolve_canonical_id("discord", "unknown#1234", self.workspace)
        self.assertEqual(canonical_id, "stranger:discord:unknown#1234")
    
    def test_resolve_stranger_not_owner(self):
        """Test non-owner number returns stranger format."""
        canonical_id = resolve_canonical_id("whatsapp", "+9999999999", self.workspace)
        self.assertEqual(canonical_id, "stranger:whatsapp:+9999999999")
    
    # === Add/Remove Channel Tests ===
    
    def test_add_channel_new_user(self):
        """Test adding channel creates new user."""
        add_channel("alice", "discord", "alice#1234", self.workspace, "Alice")
        
        identities = list_identities(self.workspace)
        self.assertIn("alice", identities)
        self.assertEqual(identities["alice"]["display_name"], "Alice")
        self.assertIn("discord:alice#1234", identities["alice"]["channels"])
    
    def test_add_channel_existing_user(self):
        """Test adding channel to existing user."""
        add_channel("bob", "telegram", "123456", self.workspace)
        add_channel("bob", "whatsapp", "+1234567890", self.workspace)
        
        channels = get_channels("bob", self.workspace)
        self.assertIn("telegram:123456", channels)
        self.assertIn("whatsapp:+1234567890", channels)
    
    def test_add_channel_idempotent(self):
        """Test adding same channel twice is idempotent."""
        add_channel("carol", "discord", "carol#5678", self.workspace)
        add_channel("carol", "discord", "carol#5678", self.workspace)
        
        channels = get_channels("carol", self.workspace)
        self.assertEqual(channels.count("discord:carol#5678"), 1)
    
    def test_remove_channel(self):
        """Test removing channel mapping."""
        add_channel("dave", "telegram", "999999", self.workspace)
        add_channel("dave", "whatsapp", "+9999999999", self.workspace)
        
        remove_channel("dave", "telegram", "999999", self.workspace)
        
        channels = get_channels("dave", self.workspace)
        self.assertNotIn("telegram:999999", channels)
        self.assertIn("whatsapp:+9999999999", channels)
    
    def test_remove_channel_nonexistent(self):
        """Test removing nonexistent channel is safe."""
        remove_channel("eve", "discord", "eve#0000", self.workspace)
        # Should not raise exception
    
    # === List/Get Tests ===
    
    def test_list_identities_empty(self):
        """Test listing when no identities."""
        identities = list_identities(self.workspace)
        self.assertEqual(identities, {})
    
    def test_list_identities_multiple(self):
        """Test listing multiple identities."""
        add_channel("alice", "telegram", "111", self.workspace)
        add_channel("bob", "whatsapp", "+222", self.workspace)
        
        identities = list_identities(self.workspace)
        self.assertIn("alice", identities)
        self.assertIn("bob", identities)
    
    def test_get_channels_existing_user(self):
        """Test getting channels for existing user."""
        add_channel("frank", "telegram", "123", self.workspace)
        add_channel("frank", "discord", "frank#456", self.workspace)
        
        channels = get_channels("frank", self.workspace)
        self.assertEqual(len(channels), 2)
        self.assertIn("telegram:123", channels)
        self.assertIn("discord:frank#456", channels)
    
    def test_get_channels_nonexistent_user(self):
        """Test getting channels for nonexistent user."""
        channels = get_channels("grace", self.workspace)
        self.assertEqual(channels, [])
    
    # === Ownership Tests ===
    
    def test_is_owner_true(self):
        """Test is_owner returns True for owner."""
        resolve_canonical_id("telegram", "123456789", self.workspace)  # Auto-register owner
        self.assertTrue(is_owner("test", self.workspace))
    
    def test_is_owner_false(self):
        """Test is_owner returns False for non-owner."""
        add_channel("henry", "telegram", "888", self.workspace)
        self.assertFalse(is_owner("henry", self.workspace))
    
    def test_is_owner_nonexistent(self):
        """Test is_owner returns False for nonexistent user."""
        self.assertFalse(is_owner("iris", self.workspace))
    
    # === Thread Safety Tests ===
    
    def test_concurrent_add_channels(self):
        """Test concurrent adds don't corrupt map (basic check)."""
        import threading
        
        def add_channels():
            for i in range(10):
                add_channel(f"user{i}", "telegram", str(1000+i), self.workspace)
        
        threads = [threading.Thread(target=add_channels) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Verify map is valid JSON
        identities = list_identities(self.workspace)
        self.assertIsInstance(identities, dict)
    
    # === Integration Tests ===
    
    def test_full_workflow(self):
        """Test complete workflow: resolve, add, list, remove."""
        # Auto-register owner
        owner_id = resolve_canonical_id("telegram", "123456789", self.workspace)
        self.assertEqual(owner_id, "test")
        
        # Add another user
        add_channel("julia", "discord", "julia#9999", self.workspace, "Julia")
        
        # List all
        identities = list_identities(self.workspace)
        self.assertEqual(len(identities), 2)
        
        # Verify owner
        self.assertTrue(is_owner(owner_id, self.workspace))
        self.assertFalse(is_owner("julia", self.workspace))
        
        # Add channel to existing user
        add_channel("julia", "whatsapp", "+5555555555", self.workspace)
        channels = get_channels("julia", self.workspace)
        self.assertEqual(len(channels), 2)
        
        # Remove channel
        remove_channel("julia", "discord", "julia#9999", self.workspace)
        channels = get_channels("julia", self.workspace)
        self.assertEqual(len(channels), 1)

def run_tests():
    """Run all tests and print summary."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIdentityResolver)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
