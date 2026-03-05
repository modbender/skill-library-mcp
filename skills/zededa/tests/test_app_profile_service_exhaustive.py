#!/usr/bin/env python3
"""Exhaustive unit tests for every method in AppProfileService."""

import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.app_profile_service import AppProfileService


def _mock_client():
    c = MagicMock()
    c.get.return_value = {"list": []}
    c.post.return_value = {"id": "new"}
    c.put.return_value = {"ok": True}
    c.delete.return_value = {"ok": True}
    c.patch.return_value = {"ok": True}
    return c


class TestAppProfileService(unittest.TestCase):
    """One test per method in AppProfileService (19 methods)."""

    def setUp(self):
        self.mc = _mock_client()
        self.svc = AppProfileService(self.mc)

    def test_create_app_policy(self):
        """create_app_policy -> POST /v1/apps/policies"""
        self.svc.create_app_policy(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/apps/policies", args[0][0])

    def test_delete_app_policy(self):
        """delete_app_policy -> DELETE /v1/apps/policies/id/{id}"""
        self.svc.delete_app_policy(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/apps/policies/id/test-id", args[0][0])

    def test_get_app_policy(self):
        """get_app_policy -> GET /v1/apps/policies/id/{id}"""
        self.svc.get_app_policy(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/id/test-id", args[0][0])

    def test_get_app_policy_by_name(self):
        """get_app_policy_by_name -> GET /v1/apps/policies/name/{name}"""
        self.svc.get_app_policy_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/name/test-name", args[0][0])

    def test_get_app_policy_events(self):
        """get_app_policy_events -> GET /v1/apps/policies/id/{objid}/events"""
        self.svc.get_app_policy_events(objid="test-objid")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/id/test-objid/events", args[0][0])

    def test_get_app_policy_events_by_name(self):
        """get_app_policy_events_by_name -> GET /v1/apps/policies/name/{objname}/events"""
        self.svc.get_app_policy_events_by_name(objname="test-objname")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/name/test-objname/events", args[0][0])

    def test_get_app_policy_resource_metrics_by_id(self):
        """get_app_policy_resource_metrics_by_id -> GET /v1/apps/policies/id/{objid}/timeSeries/{mType}"""
        self.svc.get_app_policy_resource_metrics_by_id(objid="test-objid", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/id/test-objid/timeSeries/test-mType", args[0][0])

    def test_get_app_policy_resource_metrics_by_name(self):
        """get_app_policy_resource_metrics_by_name -> GET /v1/apps/policies/name/{objname}/timeSeries/{mType}"""
        self.svc.get_app_policy_resource_metrics_by_name(objname="test-objname", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/name/test-objname/timeSeries/test-mType", args[0][0])

    def test_get_app_policy_status(self):
        """get_app_policy_status -> GET /v1/apps/policies/id/{id}/status"""
        self.svc.get_app_policy_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/id/test-id/status", args[0][0])

    def test_get_app_policy_status_by_name(self):
        """get_app_policy_status_by_name -> GET /v1/apps/policies/name/{name}/status"""
        self.svc.get_app_policy_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/name/test-name/status", args[0][0])

    def test_get_app_policy_tags(self):
        """get_app_policy_tags -> GET /v1/apps/policies/tags"""
        self.svc.get_app_policy_tags()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/tags", args[0][0])

    def test_get_global_app_policy(self):
        """get_global_app_policy -> GET /v1/apps/policies/global/id/{id}"""
        self.svc.get_global_app_policy(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/global/id/test-id", args[0][0])

    def test_get_global_app_policy_by_name(self):
        """get_global_app_policy_by_name -> GET /v1/apps/policies/global/name/{name}"""
        self.svc.get_global_app_policy_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/global/name/test-name", args[0][0])

    def test_import_app_policy(self):
        """import_app_policy -> PUT /v1/apps/policies/id/{id}/import"""
        self.svc.import_app_policy(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/policies/id/test-id/import", args[0][0])

    def test_query_app_policies(self):
        """query_app_policies -> GET /v1/apps/policies"""
        self.svc.query_app_policies()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies", args[0][0])

    def test_query_app_policy_status(self):
        """query_app_policy_status -> GET /v1/apps/policies/status"""
        self.svc.query_app_policy_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/status", args[0][0])

    def test_query_app_policy_status_config(self):
        """query_app_policy_status_config -> GET /v1/apps/policies/status-config"""
        self.svc.query_app_policy_status_config()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/status-config", args[0][0])

    def test_query_global_app_policies(self):
        """query_global_app_policies -> GET /v1/apps/policies/global"""
        self.svc.query_global_app_policies()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/policies/global", args[0][0])

    def test_update_app_policy(self):
        """update_app_policy -> PUT /v1/apps/policies/id/{id}"""
        self.svc.update_app_policy(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/policies/id/test-id", args[0][0])

    def test_method_count(self):
        """Verify expected method count."""
        methods = [m for m in dir(self.svc)
                   if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 19)


if __name__ == "__main__":
    unittest.main()
