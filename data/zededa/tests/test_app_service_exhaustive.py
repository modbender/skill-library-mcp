#!/usr/bin/env python3
"""Exhaustive unit tests for every method in AppService."""

import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.app_service import AppService


def _mock_client():
    c = MagicMock()
    c.get.return_value = {"list": []}
    c.post.return_value = {"id": "new"}
    c.put.return_value = {"ok": True}
    c.delete.return_value = {"ok": True}
    c.patch.return_value = {"ok": True}
    return c


class TestAppService(unittest.TestCase):
    """One test per method in AppService (123 methods)."""

    def setUp(self):
        self.mc = _mock_client()
        self.svc = AppService(self.mc)

    def test_activate_edge_application_instance(self):
        """activate_edge_application_instance -> PUT /v1/apps/instances/id/{id}/activate"""
        self.svc.activate_edge_application_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/instances/id/test-id/activate", args[0][0])

    def test_activate_edge_application_instance_v2(self):
        """activate_edge_application_instance_v2 -> PUT /v2/apps/instances/id/{id}/activate"""
        self.svc.activate_edge_application_instance_v2(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v2/apps/instances/id/test-id/activate", args[0][0])

    def test_connect_to_edge_application_instance(self):
        """connect_to_edge_application_instance -> PUT /v1/apps/instances/id/{id}/console/remote"""
        self.svc.connect_to_edge_application_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/instances/id/test-id/console/remote", args[0][0])

    def test_connect_to_edge_application_instance_v2(self):
        """connect_to_edge_application_instance_v2 -> PUT /v2/apps/instances/id/{id}/console/remote"""
        self.svc.connect_to_edge_application_instance_v2(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v2/apps/instances/id/test-id/console/remote", args[0][0])

    def test_create_artifact(self):
        """create_artifact -> POST /v1/artifacts"""
        self.svc.create_artifact(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/artifacts", args[0][0])

    def test_create_datastore(self):
        """create_datastore -> POST /v1/datastores"""
        self.svc.create_datastore(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/datastores", args[0][0])

    def test_create_edge_application_bundle(self):
        """create_edge_application_bundle -> POST /v1/apps"""
        self.svc.create_edge_application_bundle(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/apps", args[0][0])

    def test_create_edge_application_instance(self):
        """create_edge_application_instance -> POST /v1/apps/instances"""
        self.svc.create_edge_application_instance(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/apps/instances", args[0][0])

    def test_create_edge_application_instance_v2(self):
        """create_edge_application_instance_v2 -> POST /v2/apps/instances"""
        self.svc.create_edge_application_instance_v2(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v2/apps/instances", args[0][0])

    def test_create_image(self):
        """create_image -> POST /v1/apps/images"""
        self.svc.create_image(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/apps/images", args[0][0])

    def test_create_patch_envelope_v1(self):
        """create_patch_envelope_v1 -> POST /v1/patch-envelope"""
        self.svc.create_patch_envelope_v1(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/patch-envelope", args[0][0])

    def test_create_volume_instance(self):
        """create_volume_instance -> POST /v1/volumes/instances"""
        self.svc.create_volume_instance(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/volumes/instances", args[0][0])

    def test_deactivate_edge_application_instance(self):
        """deactivate_edge_application_instance -> PUT /v1/apps/instances/id/{id}/deactivate"""
        self.svc.deactivate_edge_application_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/instances/id/test-id/deactivate", args[0][0])

    def test_deactivate_edge_application_instance_v2(self):
        """deactivate_edge_application_instance_v2 -> PUT /v2/apps/instances/id/{id}/deactivate"""
        self.svc.deactivate_edge_application_instance_v2(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v2/apps/instances/id/test-id/deactivate", args[0][0])

    def test_delete_app_instance_snapshot(self):
        """delete_app_instance_snapshot -> DELETE /v1/apps/instances/id/{appInstanceId}/snapshot/name/{name}"""
        self.svc.delete_app_instance_snapshot(appInstanceId="test-appInstanceId", name="test-name")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/apps/instances/id/test-appInstanceId/snapshot/name/test-name", args[0][0])

    def test_delete_artifact(self):
        """delete_artifact -> DELETE /v1/artifacts/id/{id}"""
        self.svc.delete_artifact(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/artifacts/id/test-id", args[0][0])

    def test_delete_datastore(self):
        """delete_datastore -> DELETE /v1/datastores/id/{id}"""
        self.svc.delete_datastore(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/datastores/id/test-id", args[0][0])

    def test_delete_edge_application_bundle(self):
        """delete_edge_application_bundle -> DELETE /v1/apps/id/{id}"""
        self.svc.delete_edge_application_bundle(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/apps/id/test-id", args[0][0])

    def test_delete_edge_application_instance(self):
        """delete_edge_application_instance -> DELETE /v1/apps/instances/id/{id}"""
        self.svc.delete_edge_application_instance(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/apps/instances/id/test-id", args[0][0])

    def test_delete_edge_application_instance_v2(self):
        """delete_edge_application_instance_v2 -> DELETE /v2/apps/instances/id/{id}"""
        self.svc.delete_edge_application_instance_v2(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v2/apps/instances/id/test-id", args[0][0])

    def test_delete_image(self):
        """delete_image -> DELETE /v1/apps/images/id/{id}"""
        self.svc.delete_image(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/apps/images/id/test-id", args[0][0])

    def test_delete_patch_envelope_v1(self):
        """delete_patch_envelope_v1 -> DELETE /v1/patch-envelope/id/{id}"""
        self.svc.delete_patch_envelope_v1(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/patch-envelope/id/test-id", args[0][0])

    def test_delete_volume_instance(self):
        """delete_volume_instance -> DELETE /v1/volumes/instances/id/{id}"""
        self.svc.delete_volume_instance(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/volumes/instances/id/test-id", args[0][0])

    def test_get_app_instance_snapshot(self):
        """get_app_instance_snapshot -> GET /v1/apps/instances/id/{appInstanceId}/snapshot/name/{name}"""
        self.svc.get_app_instance_snapshot(appInstanceId="test-appInstanceId", name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/id/test-appInstanceId/snapshot/name/test-name", args[0][0])

    def test_get_app_instance_snapshot_by_id(self):
        """get_app_instance_snapshot_by_id -> GET /v1/apps/instances/snapshot/id/{id}"""
        self.svc.get_app_instance_snapshot_by_id(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/snapshot/id/test-id", args[0][0])

    def test_get_app_instance_snapshot_state(self):
        """get_app_instance_snapshot_state -> GET /v1/apps/instances/snapshot/id/{id}/state"""
        self.svc.get_app_instance_snapshot_state(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/snapshot/id/test-id/state", args[0][0])

    def test_get_app_instance_snapshots(self):
        """get_app_instance_snapshots -> GET /v1/apps/instances/id/{id}/snapshots"""
        self.svc.get_app_instance_snapshots(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/id/test-id/snapshots", args[0][0])

    def test_get_application_interface_tags(self):
        """get_application_interface_tags -> GET /v1/apps/instances/tags"""
        self.svc.get_application_interface_tags()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/tags", args[0][0])

    def test_get_artifact_signed_url(self):
        """get_artifact_signed_url -> GET /v1/artifacts/id/{id}/url"""
        self.svc.get_artifact_signed_url(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/artifacts/id/test-id/url", args[0][0])

    def test_get_artifact_stream(self):
        """get_artifact_stream -> GET /v1/artifacts/id/{id}"""
        self.svc.get_artifact_stream(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/artifacts/id/test-id", args[0][0])

    def test_get_datastore(self):
        """get_datastore -> GET /v1/datastores/id/{id}"""
        self.svc.get_datastore(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/datastores/id/test-id", args[0][0])

    def test_get_datastore_by_name(self):
        """get_datastore_by_name -> GET /v1/datastores/name/{name}"""
        self.svc.get_datastore_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/datastores/name/test-name", args[0][0])

    def test_get_edge_application_bundle(self):
        """get_edge_application_bundle -> GET /v1/apps/id/{id}"""
        self.svc.get_edge_application_bundle(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/id/test-id", args[0][0])

    def test_get_edge_application_bundle_by_name(self):
        """get_edge_application_bundle_by_name -> GET /v1/apps/name/{name}"""
        self.svc.get_edge_application_bundle_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/name/test-name", args[0][0])

    def test_get_edge_application_bundle_projects(self):
        """get_edge_application_bundle_projects -> GET /v1/apps/id/{id}/projects"""
        self.svc.get_edge_application_bundle_projects(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/id/test-id/projects", args[0][0])

    def test_get_edge_application_instance(self):
        """get_edge_application_instance -> GET /v1/apps/instances/id/{id}"""
        self.svc.get_edge_application_instance(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/id/test-id", args[0][0])

    def test_get_edge_application_instance_by_name(self):
        """get_edge_application_instance_by_name -> GET /v1/apps/instances/name/{name}"""
        self.svc.get_edge_application_instance_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/name/test-name", args[0][0])

    def test_get_edge_application_instance_by_name_v2(self):
        """get_edge_application_instance_by_name_v2 -> GET /v2/apps/instances/name/{name}"""
        self.svc.get_edge_application_instance_by_name_v2(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/name/test-name", args[0][0])

    def test_get_edge_application_instance_events(self):
        """get_edge_application_instance_events -> GET /v1/apps/instances/id/{objid}/events"""
        self.svc.get_edge_application_instance_events(objid="test-objid")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/id/test-objid/events", args[0][0])

    def test_get_edge_application_instance_events_by_name(self):
        """get_edge_application_instance_events_by_name -> GET /v1/apps/instances/name/{objname}/events"""
        self.svc.get_edge_application_instance_events_by_name(objname="test-objname")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/name/test-objname/events", args[0][0])

    def test_get_edge_application_instance_events_by_name_v2(self):
        """get_edge_application_instance_events_by_name_v2 -> GET /v2/apps/instances/name/{objname}/events"""
        self.svc.get_edge_application_instance_events_by_name_v2(objname="test-objname")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/name/test-objname/events", args[0][0])

    def test_get_edge_application_instance_events_v2(self):
        """get_edge_application_instance_events_v2 -> GET /v2/apps/instances/id/{objid}/events"""
        self.svc.get_edge_application_instance_events_v2(objid="test-objid")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/id/test-objid/events", args[0][0])

    def test_get_edge_application_instance_logs(self):
        """get_edge_application_instance_logs -> GET /v1/apps/instances/id/{id}/logs"""
        self.svc.get_edge_application_instance_logs(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/id/test-id/logs", args[0][0])

    def test_get_edge_application_instance_logs_v2(self):
        """get_edge_application_instance_logs_v2 -> GET /v2/apps/instances/id/{id}/logs"""
        self.svc.get_edge_application_instance_logs_v2(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/id/test-id/logs", args[0][0])

    def test_get_edge_application_instance_opaque_status(self):
        """get_edge_application_instance_opaque_status -> GET /v1/apps/instances/id/{id}/opaque-status"""
        self.svc.get_edge_application_instance_opaque_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/id/test-id/opaque-status", args[0][0])

    def test_get_edge_application_instance_opaque_status_by_name(self):
        """get_edge_application_instance_opaque_status_by_name -> GET /v1/apps/instances/name/{name}/opaque-status"""
        self.svc.get_edge_application_instance_opaque_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/name/test-name/opaque-status", args[0][0])

    def test_get_edge_application_instance_opaque_status_by_name_v2(self):
        """get_edge_application_instance_opaque_status_by_name_v2 -> GET /v2/apps/instances/name/{name}/opaque-status"""
        self.svc.get_edge_application_instance_opaque_status_by_name_v2(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/name/test-name/opaque-status", args[0][0])

    def test_get_edge_application_instance_opaque_status_v2(self):
        """get_edge_application_instance_opaque_status_v2 -> GET /v2/apps/instances/id/{id}/opaque-status"""
        self.svc.get_edge_application_instance_opaque_status_v2(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/id/test-id/opaque-status", args[0][0])

    def test_get_edge_application_instance_resource_metrics_by_id(self):
        """get_edge_application_instance_resource_metrics_by_id -> GET /v1/apps/instances/id/{objid}/timeSeries/{mType}"""
        self.svc.get_edge_application_instance_resource_metrics_by_id(objid="test-objid", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/id/test-objid/timeSeries/test-mType", args[0][0])

    def test_get_edge_application_instance_resource_metrics_by_id_v2(self):
        """get_edge_application_instance_resource_metrics_by_id_v2 -> GET /v2/apps/instances/id/{objid}/timeSeries/{mType}"""
        self.svc.get_edge_application_instance_resource_metrics_by_id_v2(objid="test-objid", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/id/test-objid/timeSeries/test-mType", args[0][0])

    def test_get_edge_application_instance_resource_metrics_by_name(self):
        """get_edge_application_instance_resource_metrics_by_name -> GET /v1/apps/instances/name/{objname}/timeSeries/{mType}"""
        self.svc.get_edge_application_instance_resource_metrics_by_name(objname="test-objname", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/name/test-objname/timeSeries/test-mType", args[0][0])

    def test_get_edge_application_instance_resource_metrics_by_name_v2(self):
        """get_edge_application_instance_resource_metrics_by_name_v2 -> GET /v2/apps/instances/name/{objname}/timeSeries/{mType}"""
        self.svc.get_edge_application_instance_resource_metrics_by_name_v2(objname="test-objname", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/name/test-objname/timeSeries/test-mType", args[0][0])

    def test_get_edge_application_instance_status(self):
        """get_edge_application_instance_status -> GET /v1/apps/instances/id/{id}/status"""
        self.svc.get_edge_application_instance_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/id/test-id/status", args[0][0])

    def test_get_edge_application_instance_status_by_name(self):
        """get_edge_application_instance_status_by_name -> GET /v1/apps/instances/name/{name}/status"""
        self.svc.get_edge_application_instance_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/name/test-name/status", args[0][0])

    def test_get_edge_application_instance_status_by_name_v2(self):
        """get_edge_application_instance_status_by_name_v2 -> GET /v2/apps/instances/name/{name}/status"""
        self.svc.get_edge_application_instance_status_by_name_v2(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/name/test-name/status", args[0][0])

    def test_get_edge_application_instance_status_v2(self):
        """get_edge_application_instance_status_v2 -> GET /v2/apps/instances/id/{id}/status"""
        self.svc.get_edge_application_instance_status_v2(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/id/test-id/status", args[0][0])

    def test_get_edge_application_instance_top_talkers(self):
        """get_edge_application_instance_top_talkers -> GET /v1/apps/instances/id/{id}/flowlog/toptalkers"""
        self.svc.get_edge_application_instance_top_talkers(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/id/test-id/flowlog/toptalkers", args[0][0])

    def test_get_edge_application_instance_top_talkers_by_name(self):
        """get_edge_application_instance_top_talkers_by_name -> GET /v1/apps/instances/name/{name}/flowlog/toptalkers"""
        self.svc.get_edge_application_instance_top_talkers_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/name/test-name/flowlog/toptalkers", args[0][0])

    def test_get_edge_application_instance_top_talkers_by_name_v2(self):
        """get_edge_application_instance_top_talkers_by_name_v2 -> GET /v2/apps/instances/name/{name}/flowlog/toptalkers"""
        self.svc.get_edge_application_instance_top_talkers_by_name_v2(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/name/test-name/flowlog/toptalkers", args[0][0])

    def test_get_edge_application_instance_top_talkers_v2(self):
        """get_edge_application_instance_top_talkers_v2 -> GET /v2/apps/instances/id/{id}/flowlog/toptalkers"""
        self.svc.get_edge_application_instance_top_talkers_v2(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/id/test-id/flowlog/toptalkers", args[0][0])

    def test_get_edge_application_instance_traffic_flows(self):
        """get_edge_application_instance_traffic_flows -> GET /v1/apps/instances/id/{id}/flowlog/classification"""
        self.svc.get_edge_application_instance_traffic_flows(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/id/test-id/flowlog/classification", args[0][0])

    def test_get_edge_application_instance_traffic_flows_by_name(self):
        """get_edge_application_instance_traffic_flows_by_name -> GET /v1/apps/instances/name/{name}/flowlog/classification"""
        self.svc.get_edge_application_instance_traffic_flows_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/name/test-name/flowlog/classification", args[0][0])

    def test_get_edge_application_instance_traffic_flows_by_name_v2(self):
        """get_edge_application_instance_traffic_flows_by_name_v2 -> GET /v2/apps/instances/name/{name}/flowlog/classification"""
        self.svc.get_edge_application_instance_traffic_flows_by_name_v2(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/name/test-name/flowlog/classification", args[0][0])

    def test_get_edge_application_instance_traffic_flows_v2(self):
        """get_edge_application_instance_traffic_flows_v2 -> GET /v2/apps/instances/id/{id}/flowlog/classification"""
        self.svc.get_edge_application_instance_traffic_flows_v2(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/id/test-id/flowlog/classification", args[0][0])

    def test_get_edge_application_instance_v2(self):
        """get_edge_application_instance_v2 -> GET /v2/apps/instances/id/{id}"""
        self.svc.get_edge_application_instance_v2(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/id/test-id", args[0][0])

    def test_get_global_edge_application_bundle(self):
        """get_global_edge_application_bundle -> GET /v1/apps/global/id/{id}"""
        self.svc.get_global_edge_application_bundle(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/global/id/test-id", args[0][0])

    def test_get_global_edge_application_bundle_by_name(self):
        """get_global_edge_application_bundle_by_name -> GET /v1/apps/global/name/{name}"""
        self.svc.get_global_edge_application_bundle_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/global/name/test-name", args[0][0])

    def test_get_image(self):
        """get_image -> GET /v1/apps/images/id/{id}"""
        self.svc.get_image(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/images/id/test-id", args[0][0])

    def test_get_image_by_name(self):
        """get_image_by_name -> GET /v1/apps/images/name/{name}"""
        self.svc.get_image_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/images/name/test-name", args[0][0])

    def test_get_latest_image_version(self):
        """get_latest_image_version -> GET /v1/apps/images/baseos/latest/hwclass/{imageArch}"""
        self.svc.get_latest_image_version(imageArch="test-imageArch")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/images/baseos/latest/hwclass/test-imageArch", args[0][0])

    def test_get_patch_envelope_by_name_v1(self):
        """get_patch_envelope_by_name_v1 -> GET /v1/patch-envelope/name/{name}"""
        self.svc.get_patch_envelope_by_name_v1(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patch-envelope/name/test-name", args[0][0])

    def test_get_patch_envelope_status_v1(self):
        """get_patch_envelope_status_v1 -> GET /v1/patch-envelope/status"""
        self.svc.get_patch_envelope_status_v1()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patch-envelope/status", args[0][0])

    def test_get_patch_envelope_v1(self):
        """get_patch_envelope_v1 -> GET /v1/patch-envelope/id/{id}"""
        self.svc.get_patch_envelope_v1(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patch-envelope/id/test-id", args[0][0])

    def test_get_volume_instance(self):
        """get_volume_instance -> GET /v1/volumes/instances/id/{id}"""
        self.svc.get_volume_instance(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/volumes/instances/id/test-id", args[0][0])

    def test_get_volume_instance_by_name(self):
        """get_volume_instance_by_name -> GET /v1/volumes/instances/name/{name}"""
        self.svc.get_volume_instance_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/volumes/instances/name/test-name", args[0][0])

    def test_get_volume_instance_events(self):
        """get_volume_instance_events -> GET /v1/volumes/instances/id/{objid}/events"""
        self.svc.get_volume_instance_events(objid="test-objid")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/volumes/instances/id/test-objid/events", args[0][0])

    def test_get_volume_instance_events_by_name(self):
        """get_volume_instance_events_by_name -> GET /v1/volumes/instances/name/{objname}/events"""
        self.svc.get_volume_instance_events_by_name(objname="test-objname")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/volumes/instances/name/test-objname/events", args[0][0])

    def test_get_volume_instance_status(self):
        """get_volume_instance_status -> GET /v1/volumes/instances/id/{id}/status"""
        self.svc.get_volume_instance_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/volumes/instances/id/test-id/status", args[0][0])

    def test_get_volume_instance_status_by_name(self):
        """get_volume_instance_status_by_name -> GET /v1/volumes/instances/name/{name}/status"""
        self.svc.get_volume_instance_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/volumes/instances/name/test-name/status", args[0][0])

    def test_mark_eve_image_latest(self):
        """mark_eve_image_latest -> PUT /v1/apps/images/baseos/latest"""
        self.svc.mark_eve_image_latest(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/images/baseos/latest", args[0][0])

    def test_mark_eve_image_latest_by_arch(self):
        """mark_eve_image_latest_by_arch -> PUT /v1/apps/images/baseos/latest/hwclass/{imageArch}"""
        self.svc.mark_eve_image_latest_by_arch(imageArch="test-imageArch", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/images/baseos/latest/hwclass/test-imageArch", args[0][0])

    def test_publish_edge_application_instance(self):
        """publish_edge_application_instance -> PUT /v1/apps/instances/id/{id}/publish"""
        self.svc.publish_edge_application_instance(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/instances/id/test-id/publish", args[0][0])

    def test_query_artifacts(self):
        """query_artifacts -> GET /v1/artifacts"""
        self.svc.query_artifacts()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/artifacts", args[0][0])

    def test_query_baseos_images(self):
        """query_baseos_images -> GET /v1/apps/images/baseos"""
        self.svc.query_baseos_images()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/images/baseos", args[0][0])

    def test_query_datastore_project_list(self):
        """query_datastore_project_list -> GET /v1/datastores/projects"""
        self.svc.query_datastore_project_list()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/datastores/projects", args[0][0])

    def test_query_datastores(self):
        """query_datastores -> GET /v1/datastores"""
        self.svc.query_datastores()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/datastores", args[0][0])

    def test_query_edge_application_bundles(self):
        """query_edge_application_bundles -> GET /v1/apps"""
        self.svc.query_edge_application_bundles()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps", args[0][0])

    def test_query_edge_application_bundles_beta(self):
        """query_edge_application_bundles_beta -> GET /beta/apps"""
        self.svc.query_edge_application_bundles_beta()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/beta/apps", args[0][0])

    def test_query_edge_application_instance_status(self):
        """query_edge_application_instance_status -> GET /v1/apps/instances/status"""
        self.svc.query_edge_application_instance_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/status", args[0][0])

    def test_query_edge_application_instance_status_config(self):
        """query_edge_application_instance_status_config -> GET /v1/apps/instances/status-config"""
        self.svc.query_edge_application_instance_status_config()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances/status-config", args[0][0])

    def test_query_edge_application_instance_status_config_v2(self):
        """query_edge_application_instance_status_config_v2 -> GET /v2/apps/instances/status-config"""
        self.svc.query_edge_application_instance_status_config_v2()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/status-config", args[0][0])

    def test_query_edge_application_instance_status_v2(self):
        """query_edge_application_instance_status_v2 -> GET /v2/apps/instances/status"""
        self.svc.query_edge_application_instance_status_v2()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances/status", args[0][0])

    def test_query_edge_application_instances(self):
        """query_edge_application_instances -> GET /v1/apps/instances"""
        self.svc.query_edge_application_instances()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/instances", args[0][0])

    def test_query_edge_application_instances_v2(self):
        """query_edge_application_instances_v2 -> GET /v2/apps/instances"""
        self.svc.query_edge_application_instances_v2()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/apps/instances", args[0][0])

    def test_query_global_edge_application_bundles(self):
        """query_global_edge_application_bundles -> GET /v1/apps/global"""
        self.svc.query_global_edge_application_bundles()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/global", args[0][0])

    def test_query_image_project_list(self):
        """query_image_project_list -> GET /v1/apps/images/projects"""
        self.svc.query_image_project_list()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/images/projects", args[0][0])

    def test_query_images(self):
        """query_images -> GET /v1/apps/images"""
        self.svc.query_images()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/apps/images", args[0][0])

    def test_query_patch_envelopes_v1(self):
        """query_patch_envelopes_v1 -> GET /v1/patch-envelope"""
        self.svc.query_patch_envelopes_v1()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/patch-envelope", args[0][0])

    def test_query_volume_instance_status(self):
        """query_volume_instance_status -> GET /v1/volumes/instances/status"""
        self.svc.query_volume_instance_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/volumes/instances/status", args[0][0])

    def test_query_volume_instance_status_config(self):
        """query_volume_instance_status_config -> GET /v1/volumes/instances/status-config"""
        self.svc.query_volume_instance_status_config()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/volumes/instances/status-config", args[0][0])

    def test_query_volume_instances(self):
        """query_volume_instances -> GET /v1/volumes/instances"""
        self.svc.query_volume_instances()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/volumes/instances", args[0][0])

    def test_refresh_edge_application_instance(self):
        """refresh_edge_application_instance -> PUT /v1/apps/instances/id/{id}/refresh"""
        self.svc.refresh_edge_application_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/instances/id/test-id/refresh", args[0][0])

    def test_refresh_edge_application_instance_v2(self):
        """refresh_edge_application_instance_v2 -> PUT /v2/apps/instances/id/{id}/refresh"""
        self.svc.refresh_edge_application_instance_v2(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v2/apps/instances/id/test-id/refresh", args[0][0])

    def test_refresh_purge_edge_application_instance(self):
        """refresh_purge_edge_application_instance -> PUT /v1/apps/instances/id/{id}/refresh/purge"""
        self.svc.refresh_purge_edge_application_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/instances/id/test-id/refresh/purge", args[0][0])

    def test_refresh_purge_edge_application_instance_v2(self):
        """refresh_purge_edge_application_instance_v2 -> PUT /v2/apps/instances/id/{id}/refresh/purge"""
        self.svc.refresh_purge_edge_application_instance_v2(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v2/apps/instances/id/test-id/refresh/purge", args[0][0])

    def test_restart_edge_application_instance(self):
        """restart_edge_application_instance -> PUT /v1/apps/instances/id/{id}/restart"""
        self.svc.restart_edge_application_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/instances/id/test-id/restart", args[0][0])

    def test_restart_edge_application_instance_v2(self):
        """restart_edge_application_instance_v2 -> PUT /v2/apps/instances/id/{id}/restart"""
        self.svc.restart_edge_application_instance_v2(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v2/apps/instances/id/test-id/restart", args[0][0])

    def test_start_edge_application_instance_debug(self):
        """start_edge_application_instance_debug -> PUT /v1/apps/instances/id/{id}/edgeview"""
        self.svc.start_edge_application_instance_debug(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/instances/id/test-id/edgeview", args[0][0])

    def test_stop_edge_application_instance_debug(self):
        """stop_edge_application_instance_debug -> PUT /v1/apps/instances/id/{id}/edgeview/stop"""
        self.svc.stop_edge_application_instance_debug(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/instances/id/test-id/edgeview/stop", args[0][0])

    def test_unpublish_edge_application_instance(self):
        """unpublish_edge_application_instance -> PUT /v1/apps/instances/id/{id}/unpublish"""
        self.svc.unpublish_edge_application_instance(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/instances/id/test-id/unpublish", args[0][0])

    def test_update_datastore(self):
        """update_datastore -> PUT /v1/datastores/id/{id}"""
        self.svc.update_datastore(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/datastores/id/test-id", args[0][0])

    def test_update_edge_application_bundle(self):
        """update_edge_application_bundle -> PUT /v1/apps/id/{id}"""
        self.svc.update_edge_application_bundle(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/id/test-id", args[0][0])

    def test_update_edge_application_instance(self):
        """update_edge_application_instance -> PUT /v1/apps/instances/id/{id}"""
        self.svc.update_edge_application_instance(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/instances/id/test-id", args[0][0])

    def test_update_edge_application_instance_v2(self):
        """update_edge_application_instance_v2 -> PUT /v2/apps/instances/id/{id}"""
        self.svc.update_edge_application_instance_v2(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v2/apps/instances/id/test-id", args[0][0])

    def test_update_image(self):
        """update_image -> PUT /v1/apps/images/id/{id}"""
        self.svc.update_image(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/images/id/test-id", args[0][0])

    def test_update_patch_envelope_reference(self):
        """update_patch_envelope_reference -> POST /v1/apps/instances/patch-reference-update"""
        self.svc.update_patch_envelope_reference(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/apps/instances/patch-reference-update", args[0][0])

    def test_update_patch_envelope_reference_v2(self):
        """update_patch_envelope_reference_v2 -> POST /v2/apps/instances/patch-reference-update"""
        self.svc.update_patch_envelope_reference_v2(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v2/apps/instances/patch-reference-update", args[0][0])

    def test_update_patch_envelope_v1(self):
        """update_patch_envelope_v1 -> PUT /v1/patch-envelope/id/{id}"""
        self.svc.update_patch_envelope_v1(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/patch-envelope/id/test-id", args[0][0])

    def test_update_volume_instance(self):
        """update_volume_instance -> PUT /v1/volumes/instances/id/{id}"""
        self.svc.update_volume_instance(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/volumes/instances/id/test-id", args[0][0])

    def test_uplink_image(self):
        """uplink_image -> PUT /v1/apps/images/id/{id}/uplink"""
        self.svc.uplink_image(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/images/id/test-id/uplink", args[0][0])

    def test_upload_artifact(self):
        """upload_artifact -> PUT /v1/artifacts/id/{id}/upload/chunked"""
        self.svc.upload_artifact(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/artifacts/id/test-id/upload/chunked", args[0][0])

    def test_upload_image_chunked(self):
        """upload_image_chunked -> PUT /v1/apps/images/name/{name}/upload/chunked"""
        self.svc.upload_image_chunked(name="test-name", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/images/name/test-name/upload/chunked", args[0][0])

    def test_upload_image_file(self):
        """upload_image_file -> PUT /v1/apps/images/name/{name}/upload/file"""
        self.svc.upload_image_file(name="test-name", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/apps/images/name/test-name/upload/file", args[0][0])

    def test_method_count(self):
        """Verify expected method count."""
        methods = [m for m in dir(self.svc)
                   if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 123)


if __name__ == "__main__":
    unittest.main()
