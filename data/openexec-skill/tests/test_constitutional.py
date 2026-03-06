import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import datetime
import base64
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app
from openexec.db import init_db
from openexec.crypto import canonical_hash, verify_ed25519_signature
from openexec.clawshield_client import generate_test_keypair, mint_approval_artifact

TEST_TENANT = "tenant-001"

init_db()

client = TestClient(app)

PRIVATE_KEY, PUBLIC_KEY_PEM = generate_test_keypair()

def _make_artifact(action, payload=None, ttl_seconds=300):
    action_request = {"action": action, "payload": payload or {}}
    return mint_approval_artifact(action_request, PRIVATE_KEY, TEST_TENANT, ttl_seconds=ttl_seconds)

class TestCrypto(unittest.TestCase):
    def test_canonical_hash_deterministic(self):
        d = {"b": 2, "a": 1}
        h1 = canonical_hash(d)
        h2 = canonical_hash({"a": 1, "b": 2})
        self.assertEqual(h1, h2)

    def test_ed25519_sign_and_verify(self):
        message = b"test-message"
        signature = PRIVATE_KEY.sign(message)
        sig_b64 = base64.b64encode(signature).decode()
        self.assertTrue(verify_ed25519_signature(PUBLIC_KEY_PEM, message, sig_b64))

    def test_ed25519_rejects_wrong_key(self):
        _, other_pub_pem = generate_test_keypair()
        message = b"test-message"
        signature = PRIVATE_KEY.sign(message)
        sig_b64 = base64.b64encode(signature).decode()
        self.assertFalse(verify_ed25519_signature(other_pub_pem, message, sig_b64))

    def test_ed25519_rejects_tampered_message(self):
        message = b"test-message"
        signature = PRIVATE_KEY.sign(message)
        sig_b64 = base64.b64encode(signature).decode()
        self.assertFalse(verify_ed25519_signature(PUBLIC_KEY_PEM, b"tampered", sig_b64))

class TestApprovalMinting(unittest.TestCase):
    def test_mint_produces_valid_artifact(self):
        action_request = {"action": "echo", "payload": {"msg": "hello"}}
        artifact = mint_approval_artifact(action_request, PRIVATE_KEY, TEST_TENANT)
        self.assertEqual(artifact["tenant_id"], TEST_TENANT)
        self.assertEqual(artifact["action_hash"], canonical_hash(action_request))
        self.assertIn("expires_at", artifact)
        self.assertIn("signature", artifact)

class TestConstitutionalExecution(unittest.TestCase):
    @patch.dict(os.environ, {
        "OPENEXEC_MODE": "clawshield",
        "CLAWSHIELD_PUBLIC_KEY": PUBLIC_KEY_PEM,
        "CLAWSHIELD_TENANT_ID": TEST_TENANT,
    })
    def test_valid_artifact_executes(self):
        artifact = _make_artifact("echo", {"msg": "constitutional"})
        resp = client.post("/execute", json={
            "action": "echo",
            "payload": {"msg": "constitutional"},
            "nonce": "ed25519-valid-1",
            "approval_artifact": artifact
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["approved"])
        self.assertEqual(data["result"]["echo"]["msg"], "constitutional")

    @patch.dict(os.environ, {
        "OPENEXEC_MODE": "clawshield",
        "CLAWSHIELD_PUBLIC_KEY": PUBLIC_KEY_PEM,
        "CLAWSHIELD_TENANT_ID": TEST_TENANT,
    })
    def test_missing_artifact_rejected(self):
        resp = client.post("/execute", json={
            "action": "echo",
            "payload": {"msg": "no-artifact"},
            "nonce": "ed25519-missing-1"
        })
        self.assertEqual(resp.status_code, 403)

    @patch.dict(os.environ, {
        "OPENEXEC_MODE": "clawshield",
        "CLAWSHIELD_PUBLIC_KEY": PUBLIC_KEY_PEM,
        "CLAWSHIELD_TENANT_ID": TEST_TENANT,
    })
    def test_tampered_payload_rejected(self):
        artifact = _make_artifact("echo", {"msg": "original"})
        resp = client.post("/execute", json={
            "action": "echo",
            "payload": {"msg": "tampered"},
            "nonce": "ed25519-tamper-1",
            "approval_artifact": artifact
        })
        self.assertEqual(resp.status_code, 403)
        self.assertIn("hash mismatch", resp.json()["detail"])

    @patch.dict(os.environ, {
        "OPENEXEC_MODE": "clawshield",
        "CLAWSHIELD_PUBLIC_KEY": PUBLIC_KEY_PEM,
        "CLAWSHIELD_TENANT_ID": "wrong-tenant",
    })
    def test_tenant_mismatch_rejected(self):
        artifact = _make_artifact("echo", {"msg": "hello"})
        resp = client.post("/execute", json={
            "action": "echo",
            "payload": {"msg": "hello"},
            "nonce": "ed25519-tenant-1",
            "approval_artifact": artifact
        })
        self.assertEqual(resp.status_code, 403)
        self.assertIn("Tenant mismatch", resp.json()["detail"])

    @patch.dict(os.environ, {
        "OPENEXEC_MODE": "clawshield",
        "CLAWSHIELD_TENANT_ID": TEST_TENANT,
    })
    def test_missing_public_key_rejected(self):
        artifact = _make_artifact("echo", {"msg": "hello"})
        resp = client.post("/execute", json={
            "action": "echo",
            "payload": {"msg": "hello"},
            "nonce": "ed25519-nokey-1",
            "approval_artifact": artifact
        })
        self.assertEqual(resp.status_code, 403)
        self.assertIn("CLAWSHIELD_PUBLIC_KEY not configured", resp.json()["detail"])

    @patch.dict(os.environ, {
        "OPENEXEC_MODE": "clawshield",
        "CLAWSHIELD_PUBLIC_KEY": generate_test_keypair()[1],
        "CLAWSHIELD_TENANT_ID": TEST_TENANT,
    })
    def test_wrong_public_key_rejected(self):
        artifact = _make_artifact("echo", {"msg": "hello"})
        resp = client.post("/execute", json={
            "action": "echo",
            "payload": {"msg": "hello"},
            "nonce": "ed25519-wrongkey-1",
            "approval_artifact": artifact
        })
        self.assertEqual(resp.status_code, 403)
        self.assertIn("Invalid signature", resp.json()["detail"])

    @patch.dict(os.environ, {
        "OPENEXEC_MODE": "clawshield",
        "CLAWSHIELD_PUBLIC_KEY": PUBLIC_KEY_PEM,
        "CLAWSHIELD_TENANT_ID": TEST_TENANT,
    })
    def test_expired_artifact_rejected(self):
        artifact = _make_artifact("echo", {"msg": "hello"}, ttl_seconds=-60)
        resp = client.post("/execute", json={
            "action": "echo",
            "payload": {"msg": "hello"},
            "nonce": "ed25519-expired-1",
            "approval_artifact": artifact
        })
        self.assertEqual(resp.status_code, 403)
        self.assertIn("expired", resp.json()["detail"])

class TestHealthEndpoint(unittest.TestCase):
    @patch.dict(os.environ, {"OPENEXEC_MODE": "clawshield"})
    def test_health_clawshield_mode(self):
        resp = client.get("/health")
        data = resp.json()
        self.assertEqual(data["exec_mode"], "clawshield")
        self.assertEqual(data["signature_verification"], "enabled")

    @patch.dict(os.environ, {"OPENEXEC_MODE": "demo"})
    def test_health_demo_mode(self):
        resp = client.get("/health")
        data = resp.json()
        self.assertEqual(data["exec_mode"], "demo")
        self.assertEqual(data["signature_verification"], "disabled")
        self.assertEqual(data["restriction"], "open")
        self.assertIn("warning", data)

    @patch.dict(os.environ, {"OPENEXEC_ALLOWED_ACTIONS": "echo,add"})
    def test_health_restricted_mode(self):
        resp = client.get("/health")
        data = resp.json()
        self.assertEqual(data["restriction"], "restricted")
        self.assertEqual(data["allow_list"], ["echo", "add"])
        self.assertNotIn("warning", data)

    def test_health_open_mode_warning(self):
        os.environ.pop("OPENEXEC_ALLOWED_ACTIONS", None)
        resp = client.get("/health")
        data = resp.json()
        self.assertEqual(data["restriction"], "open")
        self.assertEqual(data["warning"], "No execution allow-list configured")

if __name__ == "__main__":
    unittest.main()
