#!/usr/bin/env python3
"""
Tests for the NEAR QR Code Skill.
Verifies URI building/parsing and QR generation/reading round-trip.
"""

import json
import os
import sys
import tempfile
import unittest

# Ensure the skill module is importable
sys.path.insert(0, os.path.dirname(__file__))

from near_qr import (
    build_address_uri,
    build_payment_uri,
    parse_near_uri,
    generate_address_qr,
    generate_payment_qr,
    read_qr,
)


class TestURIHelpers(unittest.TestCase):
    """Test NEAR URI construction and parsing."""

    def test_address_uri(self):
        uri = build_address_uri("alice.near")
        self.assertEqual(uri, "near:alice.near")

    def test_payment_uri_no_memo(self):
        uri = build_payment_uri("bob.near", "5.0")
        self.assertIn("near:bob.near?", uri)
        self.assertIn("action=transfer", uri)
        self.assertIn("amount=5.0", uri)
        self.assertNotIn("memo", uri)

    def test_payment_uri_with_memo(self):
        uri = build_payment_uri("bob.near", "2.5", memo="Test payment")
        self.assertIn("memo=Test+payment", uri)

    def test_parse_address_uri(self):
        result = parse_near_uri("near:alice.near")
        self.assertEqual(result["type"], "near_address")
        self.assertEqual(result["account"], "alice.near")

    def test_parse_payment_uri(self):
        uri = build_payment_uri("bob.near", "10", memo="Rent")
        result = parse_near_uri(uri)
        self.assertEqual(result["type"], "near_payment")
        self.assertEqual(result["to"], "bob.near")
        self.assertEqual(result["amount"], "10")
        self.assertEqual(result["memo"], "Rent")

    def test_parse_unknown_uri(self):
        result = parse_near_uri("https://example.com")
        self.assertEqual(result["type"], "unknown")


class TestQRGeneration(unittest.TestCase):
    """Test QR code image generation."""

    def test_generate_address_qr_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "test_addr.png")
            result = generate_address_qr("alice.near", output=out)
            self.assertTrue(os.path.exists(result))
            self.assertGreater(os.path.getsize(result), 0)

    def test_generate_payment_qr_creates_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "test_pay.png")
            result = generate_payment_qr("bob.near", "3.0", memo="Hello", output=out)
            self.assertTrue(os.path.exists(result))
            self.assertGreater(os.path.getsize(result), 0)


class TestQRRoundTrip(unittest.TestCase):
    """Test generating then reading back a QR code (requires pyzbar)."""

    def test_address_round_trip(self):
        try:
            from pyzbar.pyzbar import decode as _
        except ImportError:
            self.skipTest("pyzbar not installed — skipping round-trip test")

        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "rt_addr.png")
            generate_address_qr("alice.near", output=out, size=600)
            result = read_qr(out)
            self.assertEqual(result["type"], "near_address")
            self.assertEqual(result["account"], "alice.near")

    def test_payment_round_trip(self):
        try:
            from pyzbar.pyzbar import decode as _
        except ImportError:
            self.skipTest("pyzbar not installed — skipping round-trip test")

        with tempfile.TemporaryDirectory() as tmpdir:
            out = os.path.join(tmpdir, "rt_pay.png")
            generate_payment_qr("bob.near", "7.5", memo="Dinner", output=out, size=600)
            result = read_qr(out)
            self.assertEqual(result["type"], "near_payment")
            self.assertEqual(result["to"], "bob.near")
            self.assertEqual(result["amount"], "7.5")
            self.assertEqual(result["memo"], "Dinner")

    def test_read_nonexistent_file(self):
        result = read_qr("/tmp/nonexistent_qr_image.png")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
