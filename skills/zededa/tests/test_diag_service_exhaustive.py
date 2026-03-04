#!/usr/bin/env python3
"""Exhaustive unit tests for every method in DiagService."""

import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.diag_service import DiagService


def _mock_client():
    c = MagicMock()
    c.get.return_value = {"list": []}
    c.post.return_value = {"id": "new"}
    c.put.return_value = {"ok": True}
    c.delete.return_value = {"ok": True}
    c.patch.return_value = {"ok": True}
    return c


class TestDiagService(unittest.TestCase):
    """One test per method in DiagService (21 methods)."""

    def setUp(self):
        self.mc = _mock_client()
        self.svc = DiagService(self.mc)

    def test_check_cloud_health(self):
        """check_cloud_health -> GET ?"""
        self.svc.check_cloud_health(version="test-version")
        self.mc.get.assert_called()

    def test_check_microservice_health(self):
        """check_microservice_health -> POST /v1/hello"""
        self.svc.check_microservice_health(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/hello", args[0][0])

    def test_get_cloud_audit_log(self):
        """get_cloud_audit_log -> GET /v1/cloud/audit"""
        self.svc.get_cloud_audit_log()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cloud/audit", args[0][0])

    def test_get_cloud_status(self):
        """get_cloud_status -> GET /v1/cloud/status"""
        self.svc.get_cloud_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cloud/status", args[0][0])

    def test_get_device_app_instances_summary(self):
        """get_device_app_instances_summary -> GET /v1/devices/id/{id}/apps/summary"""
        self.svc.get_device_app_instances_summary(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/apps/summary", args[0][0])

    def test_get_device_network_details(self):
        """get_device_network_details -> GET /v1/devices/id/{id}/network"""
        self.svc.get_device_network_details(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/network", args[0][0])

    def test_get_device_status_summary(self):
        """get_device_status_summary -> GET /v1/devices/id/{id}/status/summary"""
        self.svc.get_device_status_summary(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/status/summary", args[0][0])

    def test_get_device_twin_bootstrap_config(self):
        """get_device_twin_bootstrap_config -> GET /v1/devices/id/{id}/config/bootstrap"""
        self.svc.get_device_twin_bootstrap_config(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/config/bootstrap", args[0][0])

    def test_get_device_twin_bootstrap_config_by_name(self):
        """get_device_twin_bootstrap_config_by_name -> GET /v1/devices/name/{name}/config/bootstrap"""
        self.svc.get_device_twin_bootstrap_config_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/name/test-name/config/bootstrap", args[0][0])

    def test_get_device_twin_config(self):
        """get_device_twin_config -> GET /v1/devices/id/{id}/config"""
        self.svc.get_device_twin_config(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/config", args[0][0])

    def test_get_device_twin_config_by_name(self):
        """get_device_twin_config_by_name -> GET /v1/devices/name/{name}/config"""
        self.svc.get_device_twin_config_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/name/test-name/config", args[0][0])

    def test_get_device_twin_next_config(self):
        """get_device_twin_next_config -> GET /v1/devices/id/{id}/config/next"""
        self.svc.get_device_twin_next_config(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/config/next", args[0][0])

    def test_get_device_twin_next_config_by_name(self):
        """get_device_twin_next_config_by_name -> GET /v1/devices/name/{name}/config/next"""
        self.svc.get_device_twin_next_config_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/name/test-name/config/next", args[0][0])

    def test_get_device_twin_offline_config_by_name(self):
        """get_device_twin_offline_config_by_name -> GET /v1/devices/name/{name}/config/offline"""
        self.svc.get_device_twin_offline_config_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/name/test-name/config/offline", args[0][0])

    def test_get_device_twin_offline_next_config(self):
        """get_device_twin_offline_next_config -> GET /v1/devices/id/{id}/config/offline"""
        self.svc.get_device_twin_offline_next_config(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/config/offline", args[0][0])

    def test_get_device_volume_details(self):
        """get_device_volume_details -> GET /v1/devices/id/{id}/volumes"""
        self.svc.get_device_volume_details(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/volumes", args[0][0])

    def test_get_events_timeline(self):
        """get_events_timeline -> GET /v1/events"""
        self.svc.get_events_timeline(objname="test-objname", objid="test-objid", objtype="test-objtype")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/events", args[0][0])

    def test_get_events_top_users(self):
        """get_events_top_users -> GET /v1/events/topUsers"""
        self.svc.get_events_top_users()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/events/topUsers", args[0][0])

    def test_get_resource_metrics_timeline(self):
        """get_resource_metrics_timeline -> GET /v1/events/timeSeries/{mType}"""
        self.svc.get_resource_metrics_timeline(mType="test-mType", objtype="test-objtype", objname="test-objname", startTime="test-startTime", endTime="test-endTime")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/events/timeSeries/test-mType", args[0][0])

    def test_get_resource_metrics_timeline_v2(self):
        """get_resource_metrics_timeline_v2 -> GET /v1/timeSeries/{mType}"""
        self.svc.get_resource_metrics_timeline_v2(mType="test-mType", objtype="test-objtype", objname="test-objname", startTime="test-startTime", endTime="test-endTime")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/timeSeries/test-mType", args[0][0])

    def test_regen_device_config(self):
        """regen_device_config -> PUT /v1/devices/id/{id}/config"""
        self.svc.regen_device_config(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/config", args[0][0])

    def test_method_count(self):
        """Verify expected method count."""
        methods = [m for m in dir(self.svc)
                   if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 21)


if __name__ == "__main__":
    unittest.main()
