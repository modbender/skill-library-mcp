#!/usr/bin/env python3
"""Tests for rlm_redact.redact_secrets."""
import os
import sys
import unittest

# Allow importing from scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from rlm_redact import redact_secrets, REDACTED


class TestRedactSecrets(unittest.TestCase):
    """Validate that common secret patterns are redacted while normal text is preserved."""

    # ------------------------------------------------------------------
    # PEM blocks
    # ------------------------------------------------------------------
    def test_pem_private_key(self):
        text = (
            "config start\n"
            "-----BEGIN RSA PRIVATE KEY-----\n"
            "MIIBogIBAAJBALRi+0x8...\n"
            "-----END RSA PRIVATE KEY-----\n"
            "config end"
        )
        result = redact_secrets(text)
        self.assertNotIn("MIIBogIBAAJBALRi", result)
        self.assertIn(REDACTED, result)
        self.assertIn("config start", result)
        self.assertIn("config end", result)

    # ------------------------------------------------------------------
    # Bearer / Authorization tokens
    # ------------------------------------------------------------------
    def test_bearer_token(self):
        text = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.test.sig"
        result = redact_secrets(text)
        self.assertNotIn("eyJhbGciOiJIUzI1NiJ9", result)
        self.assertIn("Bearer", result)
        self.assertIn(REDACTED, result)

    def test_basic_auth(self):
        text = "Authorization: Basic dXNlcjpwYXNz"
        result = redact_secrets(text)
        self.assertNotIn("dXNlcjpwYXNz", result)
        self.assertIn("Basic", result)

    # ------------------------------------------------------------------
    # AWS credentials
    # ------------------------------------------------------------------
    def test_aws_access_key_id(self):
        text = "aws_access_key_id = AKIAIOSFODNN7EXAMPLE"
        result = redact_secrets(text)
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", result)
        self.assertIn(REDACTED, result)

    def test_aws_secret_access_key(self):
        text = "aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        result = redact_secrets(text)
        self.assertNotIn("wJalrXUtnFEMI", result)

    # ------------------------------------------------------------------
    # Generic password / secret / token assignments
    # ------------------------------------------------------------------
    def test_password_assignment_double_quotes(self):
        text = 'db_password = "s3cretP@ss!"'
        result = redact_secrets(text)
        self.assertNotIn("s3cretP@ss!", result)
        self.assertIn(REDACTED, result)

    def test_secret_assignment_single_quotes(self):
        text = "SECRET='my-app-secret-value'"
        result = redact_secrets(text)
        self.assertNotIn("my-app-secret-value", result)

    def test_api_key_colon(self):
        text = "api_key: sk-abc123xyz"
        result = redact_secrets(text)
        self.assertNotIn("sk-abc123xyz", result)

    def test_token_equals(self):
        text = "TOKEN=ghp_1234567890abcdef"
        result = redact_secrets(text)
        self.assertNotIn("ghp_1234567890abcdef", result)

    def test_password_with_spaces_in_quotes(self):
        """Quoted values with spaces should be fully redacted."""
        text = 'password = "my secret value"'
        result = redact_secrets(text)
        self.assertNotIn("my secret value", result)
        self.assertIn(REDACTED, result)

    # ------------------------------------------------------------------
    # Connection strings
    # ------------------------------------------------------------------
    def test_connection_string_pwd(self):
        text = "Server=db.example.com;Database=app;User=admin;pwd=hunter2;"
        result = redact_secrets(text)
        self.assertNotIn("hunter2", result)
        self.assertIn("Server=db.example.com", result)

    # ------------------------------------------------------------------
    # Hex-encoded secrets
    # ------------------------------------------------------------------
    def test_hex_secret_32_chars(self):
        text = "signing_key: 0123456789abcdef0123456789abcdef end"
        result = redact_secrets(text)
        self.assertNotIn("0123456789abcdef0123456789abcdef", result)

    def test_hex_secret_uppercase(self):
        """Uppercase hex strings should also be redacted."""
        text = "key: 0123456789ABCDEF0123456789ABCDEF end"
        result = redact_secrets(text)
        self.assertNotIn("0123456789ABCDEF0123456789ABCDEF", result)
        self.assertIn(REDACTED, result)

    # ------------------------------------------------------------------
    # Non-sensitive text preserved
    # ------------------------------------------------------------------
    def test_normal_text_unchanged(self):
        text = (
            "The quick brown fox jumps over the lazy dog.\n"
            "Line count: 42\n"
            "Status: OK\n"
        )
        result = redact_secrets(text)
        self.assertEqual(result, text)

    def test_code_preserved(self):
        text = (
            "def hello(name):\n"
            "    return f'Hello, {name}!'\n"
        )
        result = redact_secrets(text)
        self.assertEqual(result, text)

    def test_short_hex_not_redacted(self):
        """Hex strings shorter than 32 chars should NOT be redacted."""
        text = "commit abc123 merged"
        result = redact_secrets(text)
        self.assertEqual(result, text)

    # ------------------------------------------------------------------
    # Multiple secrets in one text
    # ------------------------------------------------------------------
    def test_multiple_secrets(self):
        text = (
            "password = 'topsecret'\n"
            "Authorization: Bearer eyToken123\n"
            "normal line here\n"
        )
        result = redact_secrets(text)
        self.assertNotIn("topsecret", result)
        self.assertNotIn("eyToken123", result)
        self.assertIn("normal line here", result)
        # Verify each line was independently redacted
        lines = result.strip().split('\n')
        redacted_lines = [l for l in lines if REDACTED in l]
        self.assertEqual(len(redacted_lines), 2,
                         "Expected exactly 2 lines to contain redactions")


if __name__ == '__main__':
    unittest.main()
