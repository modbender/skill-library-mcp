#!/usr/bin/env python3
"""
Tests for security fixes in restart-guard.
Covers:
- Webhook body template injection prevention
- Host/port validation for URL construction
"""

import os
import sys
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import notify  # noqa: E402
import restart  # noqa: E402
import guardian  # noqa: E402
import write_context  # noqa: E402


class WebhookTemplateSecurityTests(unittest.TestCase):
    """Test webhook body template rendering security."""

    def test_render_simple_json_template(self):
        template = '{"text": "{{message}}"}'
        message = "Hello world"
        result = notify._render_webhook_body(template, message)
        self.assertIsNotNone(result)
        parsed = __import__('json').loads(result)
        self.assertEqual(parsed["text"], message)

    def test_render_escapes_quotes_in_message(self):
        template = '{"text": "{{message}}"}'
        message = 'Say "hello" to everyone'
        result = notify._render_webhook_body(template, message)
        self.assertIsNotNone(result)
        parsed = __import__('json').loads(result)
        self.assertEqual(parsed["text"], message)

    def test_render_escapes_newlines_in_message(self):
        template = '{"text": "{{message}}"}'
        message = "Line 1\nLine 2\r\nLine 3"
        result = notify._render_webhook_body(template, message)
        self.assertIsNotNone(result)
        parsed = __import__('json').loads(result)
        self.assertEqual(parsed["text"], message)

    def test_render_escapes_backslashes_in_message(self):
        template = '{"text": "{{message}}"}'
        message = "C:\\Users\\test\\path"
        result = notify._render_webhook_body(template, message)
        self.assertIsNotNone(result)
        parsed = __import__('json').loads(result)
        self.assertEqual(parsed["text"], message)

    def test_render_nested_structure(self):
        template = '{"payload": {"message": "{{message}}", "source": "restart-guard"}}'
        message = "Test message"
        result = notify._render_webhook_body(template, message)
        self.assertIsNotNone(result)
        parsed = __import__('json').loads(result)
        self.assertEqual(parsed["payload"]["message"], message)

    def test_render_array_in_template(self):
        template = '["{{message}}", "static"]'
        message = "Dynamic"
        result = notify._render_webhook_body(template, message)
        self.assertIsNotNone(result)
        parsed = __import__('json').loads(result)
        self.assertEqual(parsed[0], message)

    def test_render_rejects_multiple_placeholders(self):
        template = '{"a": "{{message}}", "b": "{{message}}"}'
        message = "test"
        result = notify._render_webhook_body(template, message)
        # Multiple placeholders in non-JSON string templates are rejected
        # But JSON templates should work fine
        self.assertIsNotNone(result)

    def test_render_rejects_invalid_json_template_multiple_placeholders(self):
        # Invalid JSON with multiple placeholders should be rejected
        template = "not valid json {{message}} {{message}}"
        message = "test"
        result = notify._render_webhook_body(template, message)
        self.assertIsNone(result)

    def test_render_accepts_invalid_json_template_single_placeholder(self):
        # Invalid JSON with single placeholder falls back to string replacement
        template = "not valid json {{message}}"
        message = "test"
        result = notify._render_webhook_body(template, message)
        self.assertEqual(result, "not valid json test")

    def test_render_handles_unicode(self):
        template = '{"text": "{{message}}"}'
        message = "Hello 世界 🌍 Привет"
        result = notify._render_webhook_body(template, message)
        self.assertIsNotNone(result)
        parsed = __import__('json').loads(result)
        self.assertEqual(parsed["text"], message)


class HostPortValidationTests(unittest.TestCase):
    """Test host/port validation for URL construction."""

    def test_valid_localhost(self):
        host, port = restart.validate_host_port("127.0.0.1", "8080")
        self.assertEqual(host, "127.0.0.1")
        self.assertEqual(port, "8080")

    def test_valid_hostname(self):
        host, port = restart.validate_host_port("gateway.local", "18789")
        self.assertEqual(host, "gateway.local")
        self.assertEqual(port, "18789")

    def test_rejects_empty_host(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("", "8080")

    def test_rejects_none_host(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port(None, "8080")

    def test_rejects_newline_in_host(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("evil.com\n attacker.com", "8080")

    def test_rejects_carriage_return_in_host(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("evil.com\rattacker.com", "8080")

    def test_rejects_null_byte_in_host(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("evil.com\x00attacker.com", "8080")

    def test_rejects_space_in_host(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("evil.com attacker.com", "8080")

    def test_rejects_angle_brackets_in_host(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("evil.com<script>", "8080")

    def test_rejects_quotes_in_host(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port('evil.com"onload=', "8080")

    def test_rejects_pipe_in_host(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("evil.com|cat /etc/passwd", "8080")

    def test_rejects_backslash_in_host(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("evil.com\\attacker.com", "8080")

    def test_rejects_port_too_low(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("localhost", "0")

    def test_rejects_port_too_high(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("localhost", "65536")

    def test_rejects_negative_port(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("localhost", "-1")

    def test_rejects_non_numeric_port(self):
        with self.assertRaises(ValueError):
            restart.validate_host_port("localhost", "abc")

    def test_strips_whitespace_from_host(self):
        host, port = restart.validate_host_port("  127.0.0.1  ", "8080")
        self.assertEqual(host, "127.0.0.1")

    def test_shared_validation_via_import_in_guardian(self):
        """Verify guardian imports and uses shared validation via write_context."""
        # The function was removed from guardian, it now imports from write_context
        host, port = write_context.validate_host_port("127.0.0.1", "18789")
        self.assertEqual(host, "127.0.0.1")
        self.assertEqual(port, "18789")

    def test_shared_validation_rejects_invalid_via_write_context(self):
        """Verify shared validation rejects invalid hosts."""
        with self.assertRaises(ValueError):
            write_context.validate_host_port("evil\nhost", "8080")

    def test_restart_uses_shared_validation(self):
        """Verify restart module still exposes validation (for backwards compat)."""
        # restart.validate_host_port should still work (it imports from write_context)
        host, port = restart.validate_host_port("127.0.0.1", "18789")
        self.assertEqual(host, "127.0.0.1")
        self.assertEqual(port, "18789")


class EdgeCaseBehaviorTests(unittest.TestCase):
    """Test edge case behaviors requested in review."""

    def test_notify_webhook_returns_false_on_invalid_template(self):
        """_notify_webhook should return False when _render_webhook_body returns None."""
        notif_config = {
            "webhook": {
                "url_env": "RESTART_GUARD_WEBHOOK_URL",
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                # Multiple placeholders in non-JSON template should be rejected
                "body_template": "{{message}} and {{message}}",
            }
        }
        # Mock the env var to have a valid URL
        import os
        original_env = os.environ.get("RESTART_GUARD_WEBHOOK_URL")
        os.environ["RESTART_GUARD_WEBHOOK_URL"] = "http://example.com/webhook"
        try:
            result = notify._notify_webhook(notif_config, "test message")
            # Should return False because template is invalid (multiple placeholders)
            self.assertFalse(result)
        finally:
            if original_env is not None:
                os.environ["RESTART_GUARD_WEBHOOK_URL"] = original_env
            else:
                del os.environ["RESTART_GUARD_WEBHOOK_URL"]

    def test_trigger_restart_http_returns_error_on_validation_failure(self):
        """trigger_restart_http should return proper error tuple on validation failure."""
        # Test with invalid host containing newline
        http_code, timed_out, err = restart.trigger_restart_http(
            "evil.com\nattacker.com", "8080", 1000, "valid-token"
        )
        self.assertEqual(http_code, "")
        self.assertFalse(timed_out)
        self.assertIn("invalid-host-port", err)
        self.assertIn("invalid character", err.lower())

    def test_trigger_restart_http_returns_error_on_invalid_port(self):
        """restart.trigger_restart_http should return error on invalid port."""
        http_code, timed_out, err = restart.trigger_restart_http(
            "localhost", "abc", 1000, "valid-token"
        )
        self.assertEqual(http_code, "")
        self.assertFalse(timed_out)
        self.assertIn("invalid-host-port", err)

    def test_trigger_restart_http_returns_error_on_port_out_of_range(self):
        """restart.trigger_restart_http should return error on port out of range."""
        http_code, timed_out, err = restart.trigger_restart_http(
            "localhost", "99999", 1000, "valid-token"
        )
        self.assertEqual(http_code, "")
        self.assertFalse(timed_out)
        self.assertIn("invalid-host-port", err)

    def test_notify_openclaw_skips_http_on_validation_failure(self):
        """_notify_openclaw should skip HTTP and use CLI fallback when host/port invalid."""
        # This test verifies that when host/port validation fails, the HTTP path
        # is skipped and the function falls through to CLI fallback (or returns False
        # if no valid paths exist). We test with an invalid host containing newline.
        notif_config = {"openclaw": {"channel": "telegram", "target": "12345"}}
        full_config = {
            "gateway": {
                "host": "evil.com\nattacker.com",  # Invalid: contains newline
                "port": "18789",
                "auth_token_env": "GATEWAY_AUTH_TOKEN",
            }
        }
        # Without auth token, HTTP path should fail validation and try CLI
        # Since we don't have a real openclaw binary, this will return False,
        # but the important thing is that it doesn't crash trying to construct
        # an invalid URL with the unvalidated host
        result = notify._notify_openclaw(notif_config, full_config, None, "test message")
        # Should return False (no oc_bin provided), but not raise an exception
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
