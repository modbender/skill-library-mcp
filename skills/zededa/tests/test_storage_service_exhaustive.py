#!/usr/bin/env python3
"""Exhaustive unit tests for every method in StorageService."""

import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.storage_service import StorageService


def _mock_client():
    c = MagicMock()
    c.get.return_value = {"list": []}
    c.post.return_value = {"id": "new"}
    c.put.return_value = {"ok": True}
    c.delete.return_value = {"ok": True}
    c.patch.return_value = {"ok": True}
    return c


class TestStorageService(unittest.TestCase):
    """One test per method in StorageService (33 methods)."""

    def setUp(self):
        self.mc = _mock_client()
        self.svc = StorageService(self.mc)

    def test_create_attestation_policy(self):
        """create_attestation_policy -> POST /v1/attestation/policies"""
        self.svc.create_attestation_policy(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/attestation/policies", args[0][0])

    def test_create_deployment_policy(self):
        """create_deployment_policy -> POST /v1/deployment/policies"""
        self.svc.create_deployment_policy(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/deployment/policies", args[0][0])

    def test_create_patch_envelope(self):
        """create_patch_envelope -> POST /v1/patches"""
        self.svc.create_patch_envelope(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/patches", args[0][0])

    def test_delete_attestation_policy(self):
        """delete_attestation_policy -> DELETE /v1/attestation/policies/id/{id}"""
        self.svc.delete_attestation_policy(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/attestation/policies/id/test-id", args[0][0])

    def test_delete_deployment_policy(self):
        """delete_deployment_policy -> DELETE /v1/deployment/policies/id/{id}"""
        self.svc.delete_deployment_policy(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/deployment/policies/id/test-id", args[0][0])

    def test_delete_patch_envelope(self):
        """delete_patch_envelope -> DELETE /v1/patches/id/{id}"""
        self.svc.delete_patch_envelope(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/patches/id/test-id", args[0][0])

    def test_get_attestation_policy(self):
        """get_attestation_policy -> GET /v1/attestation/policies/id/{id}"""
        self.svc.get_attestation_policy(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/attestation/policies/id/test-id", args[0][0])

    def test_get_attestation_policy_by_name(self):
        """get_attestation_policy_by_name -> GET /v1/attestation/policies/name/{name}"""
        self.svc.get_attestation_policy_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/attestation/policies/name/test-name", args[0][0])

    def test_get_attestation_policy_status(self):
        """get_attestation_policy_status -> GET /v1/attestation/policies/id/{id}/status"""
        self.svc.get_attestation_policy_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/attestation/policies/id/test-id/status", args[0][0])

    def test_get_attestation_policy_status_by_name(self):
        """get_attestation_policy_status_by_name -> GET /v1/attestation/policies/name/{name}/status"""
        self.svc.get_attestation_policy_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/attestation/policies/name/test-name/status", args[0][0])

    def test_get_deployment_policy(self):
        """get_deployment_policy -> GET /v1/deployment/policies/id/{id}"""
        self.svc.get_deployment_policy(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/deployment/policies/id/test-id", args[0][0])

    def test_get_deployment_policy_by_name(self):
        """get_deployment_policy_by_name -> GET /v1/deployment/policies/name/{name}"""
        self.svc.get_deployment_policy_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/deployment/policies/name/test-name", args[0][0])

    def test_get_deployment_policy_status(self):
        """get_deployment_policy_status -> GET /v1/deployment/policies/id/{id}/status"""
        self.svc.get_deployment_policy_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/deployment/policies/id/test-id/status", args[0][0])

    def test_get_deployment_policy_status_by_name(self):
        """get_deployment_policy_status_by_name -> GET /v1/deployment/policies/name/{name}/status"""
        self.svc.get_deployment_policy_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/deployment/policies/name/test-name/status", args[0][0])

    def test_get_patch_envelope(self):
        """get_patch_envelope -> GET /v1/patches/id/{id}"""
        self.svc.get_patch_envelope(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patches/id/test-id", args[0][0])

    def test_get_patch_envelope_by_name(self):
        """get_patch_envelope_by_name -> GET /v1/patches/name/{name}"""
        self.svc.get_patch_envelope_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patches/name/test-name", args[0][0])

    def test_get_patch_envelope_events(self):
        """get_patch_envelope_events -> GET /v1/patches/id/{objid}/events"""
        self.svc.get_patch_envelope_events(objid="test-objid")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patches/id/test-objid/events", args[0][0])

    def test_get_patch_envelope_events_by_name(self):
        """get_patch_envelope_events_by_name -> GET /v1/patches/name/{objname}/events"""
        self.svc.get_patch_envelope_events_by_name(objname="test-objname")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patches/name/test-objname/events", args[0][0])

    def test_get_patch_envelope_status(self):
        """get_patch_envelope_status -> GET /v1/patches/id/{id}/status"""
        self.svc.get_patch_envelope_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patches/id/test-id/status", args[0][0])

    def test_get_patch_envelope_status_by_name(self):
        """get_patch_envelope_status_by_name -> GET /v1/patches/name/{name}/status"""
        self.svc.get_patch_envelope_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patches/name/test-name/status", args[0][0])

    def test_get_patch_reference_update(self):
        """get_patch_reference_update -> GET /v1/patches/referenceupdate/id/{referenceUpdateId}"""
        self.svc.get_patch_reference_update(referenceUpdateId="test-referenceUpdateId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patches/referenceupdate/id/test-referenceUpdateId", args[0][0])

    def test_query_attestation_policies(self):
        """query_attestation_policies -> GET /v1/attestation/policies"""
        self.svc.query_attestation_policies()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/attestation/policies", args[0][0])

    def test_query_attestation_policy_status(self):
        """query_attestation_policy_status -> GET /v1/attestation/policies/status"""
        self.svc.query_attestation_policy_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/attestation/policies/status", args[0][0])

    def test_query_attestation_policy_status_config(self):
        """query_attestation_policy_status_config -> GET /v1/attestation/policies/status-config"""
        self.svc.query_attestation_policy_status_config()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/attestation/policies/status-config", args[0][0])

    def test_query_deployment_policies(self):
        """query_deployment_policies -> GET /v1/deployment/policies"""
        self.svc.query_deployment_policies()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/deployment/policies", args[0][0])

    def test_query_deployment_policy_status(self):
        """query_deployment_policy_status -> GET /v1/deployment/policies/status"""
        self.svc.query_deployment_policy_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/deployment/policies/status", args[0][0])

    def test_query_deployment_policy_status_config(self):
        """query_deployment_policy_status_config -> GET /v1/deployment/policies/status-config"""
        self.svc.query_deployment_policy_status_config()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/deployment/policies/status-config", args[0][0])

    def test_query_patch_envelope_status(self):
        """query_patch_envelope_status -> GET /v1/patches/status"""
        self.svc.query_patch_envelope_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patches/status", args[0][0])

    def test_query_patch_envelope_status_config(self):
        """query_patch_envelope_status_config -> GET /v1/patches/status-config"""
        self.svc.query_patch_envelope_status_config()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patches/status-config", args[0][0])

    def test_query_patch_envelopes(self):
        """query_patch_envelopes -> GET /v1/patches"""
        self.svc.query_patch_envelopes()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patches", args[0][0])

    def test_update_attestation_policy(self):
        """update_attestation_policy -> PUT /v1/attestation/policies/id/{id}"""
        self.svc.update_attestation_policy(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/attestation/policies/id/test-id", args[0][0])

    def test_update_deployment_policy(self):
        """update_deployment_policy -> PUT /v1/deployment/policies/id/{id}"""
        self.svc.update_deployment_policy(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/deployment/policies/id/test-id", args[0][0])

    def test_update_patch_envelope(self):
        """update_patch_envelope -> PUT /v1/patches/id/{id}"""
        self.svc.update_patch_envelope(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/patches/id/test-id", args[0][0])

    def test_method_count(self):
        """Verify expected method count."""
        methods = [m for m in dir(self.svc)
                   if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 33)


if __name__ == "__main__":
    unittest.main()
