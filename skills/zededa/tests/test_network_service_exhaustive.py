#!/usr/bin/env python3
"""Exhaustive unit tests for every method in NetworkService."""

import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.network_service import NetworkService


def _mock_client():
    c = MagicMock()
    c.get.return_value = {"list": []}
    c.post.return_value = {"id": "new"}
    c.put.return_value = {"ok": True}
    c.delete.return_value = {"ok": True}
    c.patch.return_value = {"ok": True}
    return c


class TestNetworkService(unittest.TestCase):
    """One test per method in NetworkService (16 methods)."""

    def setUp(self):
        self.mc = _mock_client()
        self.svc = NetworkService(self.mc)

    def test_create_network(self):
        """create_network -> POST /v1/networks"""
        self.svc.create_network(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/networks", args[0][0])

    def test_delete_network(self):
        """delete_network -> DELETE /v1/networks/id/{id}"""
        self.svc.delete_network(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/networks/id/test-id", args[0][0])

    def test_get_network(self):
        """get_network -> GET /v1/networks/id/{id}"""
        self.svc.get_network(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/id/test-id", args[0][0])

    def test_get_network_by_name(self):
        """get_network_by_name -> GET /v1/networks/name/{name}"""
        self.svc.get_network_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/name/test-name", args[0][0])

    def test_get_network_events(self):
        """get_network_events -> GET /v1/networks/id/{objid}/events"""
        self.svc.get_network_events(objid="test-objid")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/id/test-objid/events", args[0][0])

    def test_get_network_events_by_name(self):
        """get_network_events_by_name -> GET /v1/networks/name/{objname}/events"""
        self.svc.get_network_events_by_name(objname="test-objname")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/name/test-objname/events", args[0][0])

    def test_get_network_resource_metrics_by_id(self):
        """get_network_resource_metrics_by_id -> GET /v1/networks/id/{objid}/timeSeries/{mType}"""
        self.svc.get_network_resource_metrics_by_id(objid="test-objid", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/id/test-objid/timeSeries/test-mType", args[0][0])

    def test_get_network_resource_metrics_by_name(self):
        """get_network_resource_metrics_by_name -> GET /v1/networks/name/{objname}/timeSeries/{mType}"""
        self.svc.get_network_resource_metrics_by_name(objname="test-objname", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/name/test-objname/timeSeries/test-mType", args[0][0])

    def test_get_network_status(self):
        """get_network_status -> GET /v1/networks/id/{id}/status"""
        self.svc.get_network_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/id/test-id/status", args[0][0])

    def test_get_network_status_by_name(self):
        """get_network_status_by_name -> GET /v1/networks/name/{name}/status"""
        self.svc.get_network_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/name/test-name/status", args[0][0])

    def test_get_network_tags(self):
        """get_network_tags -> GET /v1/networks/tags"""
        self.svc.get_network_tags()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/tags", args[0][0])

    def test_query_network_projects(self):
        """query_network_projects -> GET /v1/networks/projects"""
        self.svc.query_network_projects()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/projects", args[0][0])

    def test_query_network_status(self):
        """query_network_status -> GET /v1/networks/status"""
        self.svc.query_network_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/status", args[0][0])

    def test_query_network_status_config(self):
        """query_network_status_config -> GET /v1/networks/status-config"""
        self.svc.query_network_status_config()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks/status-config", args[0][0])

    def test_query_networks(self):
        """query_networks -> GET /v1/networks"""
        self.svc.query_networks()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/networks", args[0][0])

    def test_update_network(self):
        """update_network -> PUT /v1/networks/id/{id}"""
        self.svc.update_network(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/networks/id/test-id", args[0][0])

    def test_method_count(self):
        """Verify expected method count."""
        methods = [m for m in dir(self.svc)
                   if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 16)


if __name__ == "__main__":
    unittest.main()
