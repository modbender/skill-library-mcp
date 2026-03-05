#!/usr/bin/env python3
"""Exhaustive unit tests for every method in NodeClusterService."""

import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.node_cluster_service import NodeClusterService


def _mock_client():
    c = MagicMock()
    c.get.return_value = {"list": []}
    c.post.return_value = {"id": "new"}
    c.put.return_value = {"ok": True}
    c.delete.return_value = {"ok": True}
    c.patch.return_value = {"ok": True}
    return c


class TestNodeClusterService(unittest.TestCase):
    """One test per method in NodeClusterService (13 methods)."""

    def setUp(self):
        self.mc = _mock_client()
        self.svc = NodeClusterService(self.mc)

    def test_create_edge_node_cluster(self):
        """create_edge_node_cluster -> POST /v1/cluster/policies"""
        self.svc.create_edge_node_cluster(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/cluster/policies", args[0][0])

    def test_delete_edge_node_cluster(self):
        """delete_edge_node_cluster -> DELETE /v1/cluster/policies/id/{id}"""
        self.svc.delete_edge_node_cluster(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/cluster/policies/id/test-id", args[0][0])

    def test_get_edge_node_cluster(self):
        """get_edge_node_cluster -> GET /v1/cluster/policies/id/{id}"""
        self.svc.get_edge_node_cluster(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/policies/id/test-id", args[0][0])

    def test_get_edge_node_cluster_by_name(self):
        """get_edge_node_cluster_by_name -> GET /v1/cluster/policies/name/{name}"""
        self.svc.get_edge_node_cluster_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/policies/name/test-name", args[0][0])

    def test_get_edge_node_cluster_events(self):
        """get_edge_node_cluster_events -> GET /v1/cluster/policies/id/{objid}/events"""
        self.svc.get_edge_node_cluster_events(objid="test-objid")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/policies/id/test-objid/events", args[0][0])

    def test_get_edge_node_cluster_events_by_name(self):
        """get_edge_node_cluster_events_by_name -> GET /v1/cluster/policies/name/{objname}/events"""
        self.svc.get_edge_node_cluster_events_by_name(objname="test-objname")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/policies/name/test-objname/events", args[0][0])

    def test_get_edge_node_cluster_status(self):
        """get_edge_node_cluster_status -> GET /v1/cluster/policies/id/{id}/status"""
        self.svc.get_edge_node_cluster_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/policies/id/test-id/status", args[0][0])

    def test_get_edge_node_cluster_status_by_name(self):
        """get_edge_node_cluster_status_by_name -> GET /v1/cluster/policies/name/{name}/status"""
        self.svc.get_edge_node_cluster_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/policies/name/test-name/status", args[0][0])

    def test_get_edge_node_cluster_tags(self):
        """get_edge_node_cluster_tags -> GET /v1/cluster/policies/tags"""
        self.svc.get_edge_node_cluster_tags()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/policies/tags", args[0][0])

    def test_query_edge_node_cluster_status(self):
        """query_edge_node_cluster_status -> GET /v1/cluster/policies/status"""
        self.svc.query_edge_node_cluster_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/policies/status", args[0][0])

    def test_query_edge_node_cluster_status_config(self):
        """query_edge_node_cluster_status_config -> GET /v1/cluster/policies/status-config"""
        self.svc.query_edge_node_cluster_status_config()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/policies/status-config", args[0][0])

    def test_query_edge_node_clusters(self):
        """query_edge_node_clusters -> GET /v1/cluster/policies"""
        self.svc.query_edge_node_clusters()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/policies", args[0][0])

    def test_update_edge_node_cluster(self):
        """update_edge_node_cluster -> PUT /v1/cluster/policies/id/{id}"""
        self.svc.update_edge_node_cluster(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/cluster/policies/id/test-id", args[0][0])

    def test_method_count(self):
        """Verify expected method count."""
        methods = [m for m in dir(self.svc)
                   if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 13)


if __name__ == "__main__":
    unittest.main()
