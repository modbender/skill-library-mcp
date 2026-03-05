#!/usr/bin/env python3
"""Exhaustive unit tests for every method in OrchestrationService."""

import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.orchestration_service import OrchestrationService


def _mock_client():
    c = MagicMock()
    c.get.return_value = {"list": []}
    c.post.return_value = {"id": "new"}
    c.put.return_value = {"ok": True}
    c.delete.return_value = {"ok": True}
    c.patch.return_value = {"ok": True}
    return c


class TestOrchestrationService(unittest.TestCase):
    """One test per method in OrchestrationService (37 methods)."""

    def setUp(self):
        self.mc = _mock_client()
        self.svc = OrchestrationService(self.mc)

    def test_activate_cluster_instance(self):
        """activate_cluster_instance -> PUT /v1/cluster/instances/id/{id}/activate"""
        self.svc.activate_cluster_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/cluster/instances/id/test-id/activate", args[0][0])

    def test_create_cluster_instance(self):
        """create_cluster_instance -> POST /v1/cluster/instances"""
        self.svc.create_cluster_instance(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/cluster/instances", args[0][0])

    def test_create_data_stream(self):
        """create_data_stream -> POST /v1/datastreams"""
        self.svc.create_data_stream(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/datastreams", args[0][0])

    def test_create_plugin(self):
        """create_plugin -> POST /v1/plugins"""
        self.svc.create_plugin(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/plugins", args[0][0])

    def test_deactivate_cluster_instance(self):
        """deactivate_cluster_instance -> PUT /v1/cluster/instances/id/{id}/deactivate"""
        self.svc.deactivate_cluster_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/cluster/instances/id/test-id/deactivate", args[0][0])

    def test_delete_azure_deployment_policy(self):
        """delete_azure_deployment_policy -> DELETE /v1/azure/deployment/policyid/{policyId}"""
        self.svc.delete_azure_deployment_policy(policyId="test-policyId")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/azure/deployment/policyid/test-policyId", args[0][0])

    def test_delete_cluster_instance(self):
        """delete_cluster_instance -> DELETE /v1/cluster/instances/id/{id}"""
        self.svc.delete_cluster_instance(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/cluster/instances/id/test-id", args[0][0])

    def test_delete_data_stream(self):
        """delete_data_stream -> DELETE /v1/datastreams/id/{id}"""
        self.svc.delete_data_stream(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/datastreams/id/test-id", args[0][0])

    def test_delete_plugin(self):
        """delete_plugin -> DELETE /v1/plugins/id/{id}"""
        self.svc.delete_plugin(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/plugins/id/test-id", args[0][0])

    def test_download_cluster_instance_kubeconfig_by_id(self):
        """download_cluster_instance_kubeconfig_by_id -> GET /v1/cluster/instances/id/{id}/status/kubeconfig/download"""
        self.svc.download_cluster_instance_kubeconfig_by_id(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/id/test-id/status/kubeconfig/download", args[0][0])

    def test_download_cluster_instance_kubeconfig_by_name(self):
        """download_cluster_instance_kubeconfig_by_name -> GET /v1/cluster/instances/name/{name}/status/kubeconfig/download"""
        self.svc.download_cluster_instance_kubeconfig_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/name/test-name/status/kubeconfig/download", args[0][0])

    def test_get_azure_module_policy(self):
        """get_azure_module_policy -> GET /v1/azure/edgedevice/modulepolicyid/{modulePolicyId}"""
        self.svc.get_azure_module_policy(modulePolicyId="test-modulePolicyId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/azure/edgedevice/modulepolicyid/test-modulePolicyId", args[0][0])

    def test_get_cluster_instance(self):
        """get_cluster_instance -> GET /v1/cluster/instances/id/{id}"""
        self.svc.get_cluster_instance(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/id/test-id", args[0][0])

    def test_get_cluster_instance_by_name(self):
        """get_cluster_instance_by_name -> GET /v1/cluster/instances/name/{name}"""
        self.svc.get_cluster_instance_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/name/test-name", args[0][0])

    def test_get_cluster_instance_events(self):
        """get_cluster_instance_events -> GET /v1/cluster/instances/id/{objid}/events"""
        self.svc.get_cluster_instance_events(objid="test-objid")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/id/test-objid/events", args[0][0])

    def test_get_cluster_instance_events_by_name(self):
        """get_cluster_instance_events_by_name -> GET /v1/cluster/instances/name/{objname}/events"""
        self.svc.get_cluster_instance_events_by_name(objname="test-objname")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/name/test-objname/events", args[0][0])

    def test_get_cluster_instance_kubeconfig_by_id(self):
        """get_cluster_instance_kubeconfig_by_id -> GET /v1/cluster/instances/id/{id}/status/kubeconfig"""
        self.svc.get_cluster_instance_kubeconfig_by_id(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/id/test-id/status/kubeconfig", args[0][0])

    def test_get_cluster_instance_kubeconfig_by_name(self):
        """get_cluster_instance_kubeconfig_by_name -> GET /v1/cluster/instances/name/{name}/status/kubeconfig"""
        self.svc.get_cluster_instance_kubeconfig_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/name/test-name/status/kubeconfig", args[0][0])

    def test_get_cluster_instance_status(self):
        """get_cluster_instance_status -> GET /v1/cluster/instances/id/{id}/status"""
        self.svc.get_cluster_instance_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/id/test-id/status", args[0][0])

    def test_get_cluster_instance_status_by_name(self):
        """get_cluster_instance_status_by_name -> GET /v1/cluster/instances/name/{name}/status"""
        self.svc.get_cluster_instance_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/name/test-name/status", args[0][0])

    def test_get_cluster_instance_tags(self):
        """get_cluster_instance_tags -> GET /v1/cluster/instances/tags"""
        self.svc.get_cluster_instance_tags()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/tags", args[0][0])

    def test_get_data_stream_by_id(self):
        """get_data_stream_by_id -> GET /v1/datastreams/id/{id}"""
        self.svc.get_data_stream_by_id(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/datastreams/id/test-id", args[0][0])

    def test_get_data_stream_by_name(self):
        """get_data_stream_by_name -> GET /v1/datastreams/name/{name}"""
        self.svc.get_data_stream_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/datastreams/name/test-name", args[0][0])

    def test_get_plugin_by_id(self):
        """get_plugin_by_id -> GET /v1/plugins/id/{id}"""
        self.svc.get_plugin_by_id(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/plugins/id/test-id", args[0][0])

    def test_get_plugin_by_name(self):
        """get_plugin_by_name -> GET /v1/plugins/name/{name}"""
        self.svc.get_plugin_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/plugins/name/test-name", args[0][0])

    def test_query_api_usage(self):
        """query_api_usage -> GET /v1/apiusage"""
        self.svc.query_api_usage()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apiusage", args[0][0])

    def test_query_cluster_instance_status(self):
        """query_cluster_instance_status -> GET /v1/cluster/instances/status"""
        self.svc.query_cluster_instance_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/status", args[0][0])

    def test_query_cluster_instance_status_config(self):
        """query_cluster_instance_status_config -> GET /v1/cluster/instances/status-config"""
        self.svc.query_cluster_instance_status_config()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/status-config", args[0][0])

    def test_query_cluster_instances(self):
        """query_cluster_instances -> GET /v1/cluster/instances"""
        self.svc.query_cluster_instances()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances", args[0][0])

    def test_query_data_streams(self):
        """query_data_streams -> GET /v1/datastreams"""
        self.svc.query_data_streams()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/datastreams", args[0][0])

    def test_query_plugins(self):
        """query_plugins -> GET /v1/plugins"""
        self.svc.query_plugins()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/plugins", args[0][0])

    def test_refresh_cluster_instance(self):
        """refresh_cluster_instance -> PUT /v1/cluster/instances/id/{id}/refresh"""
        self.svc.refresh_cluster_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/cluster/instances/id/test-id/refresh", args[0][0])

    def test_refresh_purge_cluster_instance(self):
        """refresh_purge_cluster_instance -> PUT /v1/cluster/instances/id/{id}/refresh/purge"""
        self.svc.refresh_purge_cluster_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/cluster/instances/id/test-id/refresh/purge", args[0][0])

    def test_restart_cluster_instance(self):
        """restart_cluster_instance -> PUT /v1/cluster/instances/id/{id}/restart"""
        self.svc.restart_cluster_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/cluster/instances/id/test-id/restart", args[0][0])

    def test_update_cluster_instance(self):
        """update_cluster_instance -> PUT /v1/cluster/instances/id/{id}"""
        self.svc.update_cluster_instance(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/cluster/instances/id/test-id", args[0][0])

    def test_update_data_stream(self):
        """update_data_stream -> PUT /v1/datastreams/id/{id}"""
        self.svc.update_data_stream(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/datastreams/id/test-id", args[0][0])

    def test_update_plugin(self):
        """update_plugin -> PUT /v1/plugins/id/{id}"""
        self.svc.update_plugin(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/plugins/id/test-id", args[0][0])

    def test_method_count(self):
        """Verify expected method count."""
        methods = [m for m in dir(self.svc)
                   if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 37)


if __name__ == "__main__":
    unittest.main()
