#!/usr/bin/env python3
"""Exhaustive unit tests for every method in NodeService."""

import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.node_service import NodeService


def _mock_client():
    c = MagicMock()
    c.get.return_value = {"list": []}
    c.post.return_value = {"id": "new"}
    c.put.return_value = {"ok": True}
    c.delete.return_value = {"ok": True}
    c.patch.return_value = {"ok": True}
    return c


class TestNodeService(unittest.TestCase):
    """One test per method in NodeService (91 methods)."""

    def setUp(self):
        self.mc = _mock_client()
        self.svc = NodeService(self.mc)

    def test_activate_edge_node(self):
        """activate_edge_node -> PUT /v1/devices/id/{id}/activate"""
        self.svc.activate_edge_node(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/activate", args[0][0])

    def test_apply_edge_node_config(self):
        """apply_edge_node_config -> PUT /v1/devices/id/{id}/apply"""
        self.svc.apply_edge_node_config(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/apply", args[0][0])

    def test_attest_edge_node(self):
        """attest_edge_node -> PUT /v1/devices/id/{id}/attest"""
        self.svc.attest_edge_node(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/attest", args[0][0])

    def test_create_brand(self):
        """create_brand -> POST /v1/brands"""
        self.svc.create_brand(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/brands", args[0][0])

    def test_create_deployment(self):
        """create_deployment -> POST /v2/projects/id/{projectId}/deployments"""
        self.svc.create_deployment(projectId="test-projectId", body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v2/projects/id/test-projectId/deployments", args[0][0])

    def test_create_edge_node(self):
        """create_edge_node -> POST /v1/devices"""
        self.svc.create_edge_node(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/devices", args[0][0])

    def test_create_edge_node_single_use_eve_image(self):
        """create_edge_node_single_use_eve_image -> POST /v1/devices/id/{id}/suimage"""
        self.svc.create_edge_node_single_use_eve_image(id="test-id", body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/devices/id/test-id/suimage", args[0][0])

    def test_create_hardware_model(self):
        """create_hardware_model -> POST /v1/sysmodels"""
        self.svc.create_hardware_model(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/sysmodels", args[0][0])

    def test_create_pcr_templates(self):
        """create_pcr_templates -> POST /v1/sysmodels/id/{id}/pcrtemplates"""
        self.svc.create_pcr_templates(id="test-id", body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/sysmodels/id/test-id/pcrtemplates", args[0][0])

    def test_create_project(self):
        """create_project -> POST /v1/projects"""
        self.svc.create_project(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/projects", args[0][0])

    def test_create_project_v2(self):
        """create_project_v2 -> POST /v2/projects"""
        self.svc.create_project_v2(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v2/projects", args[0][0])

    def test_deactivate_edge_node(self):
        """deactivate_edge_node -> PUT /v1/devices/id/{id}/deactivate"""
        self.svc.deactivate_edge_node(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/deactivate", args[0][0])

    def test_delete_all_deployments(self):
        """delete_all_deployments -> DELETE /v2/projects/id/{projectId}/deployments"""
        self.svc.delete_all_deployments(projectId="test-projectId")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v2/projects/id/test-projectId/deployments", args[0][0])

    def test_delete_brand(self):
        """delete_brand -> DELETE /v1/brands/id/{id}"""
        self.svc.delete_brand(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/brands/id/test-id", args[0][0])

    def test_delete_deployment(self):
        """delete_deployment -> DELETE /v2/projects/id/{projectId}/deployments/id/{id}"""
        self.svc.delete_deployment(projectId="test-projectId", id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v2/projects/id/test-projectId/deployments/id/test-id", args[0][0])

    def test_delete_edge_node(self):
        """delete_edge_node -> DELETE /v1/devices/id/{id}"""
        self.svc.delete_edge_node(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/devices/id/test-id", args[0][0])

    def test_delete_hardware_model(self):
        """delete_hardware_model -> DELETE /v1/sysmodels/id/{id}"""
        self.svc.delete_hardware_model(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/sysmodels/id/test-id", args[0][0])

    def test_delete_pcr_template(self):
        """delete_pcr_template -> DELETE /v1/pcrtemplates/id/{id}"""
        self.svc.delete_pcr_template(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/pcrtemplates/id/test-id", args[0][0])

    def test_delete_project(self):
        """delete_project -> DELETE /v1/projects/id/{id}"""
        self.svc.delete_project(id="test-id")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/projects/id/test-id", args[0][0])

    def test_disable_edge_node_debug(self):
        """disable_edge_node_debug -> PUT /v1/devices/id/{id}/debug/disable"""
        self.svc.disable_edge_node_debug(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/debug/disable", args[0][0])

    def test_disable_edge_node_edgeview(self):
        """disable_edge_node_edgeview -> PUT /v1/devices/id/{id}/edgeview/disable"""
        self.svc.disable_edge_node_edgeview(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/edgeview/disable", args[0][0])

    def test_enable_edge_node_debug(self):
        """enable_edge_node_debug -> PUT /v1/devices/id/{id}/debug/enable"""
        self.svc.enable_edge_node_debug(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/debug/enable", args[0][0])

    def test_enable_edge_node_edgeview(self):
        """enable_edge_node_edgeview -> PUT /v1/devices/id/{id}/edgeview/enable"""
        self.svc.enable_edge_node_edgeview(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/edgeview/enable", args[0][0])

    def test_get_brand(self):
        """get_brand -> GET /v1/brands/id/{id}"""
        self.svc.get_brand(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/brands/id/test-id", args[0][0])

    def test_get_brand_by_name(self):
        """get_brand_by_name -> GET /v1/brands/name/{name}"""
        self.svc.get_brand_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/brands/name/test-name", args[0][0])

    def test_get_deployment_by_id(self):
        """get_deployment_by_id -> GET /v2/projects/id/{projectId}/deployments/id/{id}"""
        self.svc.get_deployment_by_id(projectId="test-projectId", id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/projects/id/test-projectId/deployments/id/test-id", args[0][0])

    def test_get_deployments_by_project_id(self):
        """get_deployments_by_project_id -> GET /v2/projects/id/{projectId}/deployments"""
        self.svc.get_deployments_by_project_id(projectId="test-projectId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v2/projects/id/test-projectId/deployments", args[0][0])

    def test_get_device_interface_tags(self):
        """get_device_interface_tags -> GET /v1/devices/interfaces/tags"""
        self.svc.get_device_interface_tags()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/interfaces/tags", args[0][0])

    def test_get_device_status_config(self):
        """get_device_status_config -> GET /v1/devices/status-config"""
        self.svc.get_device_status_config()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/status-config", args[0][0])

    def test_get_device_status_location(self):
        """get_device_status_location -> GET /v1/devices/status/locations"""
        self.svc.get_device_status_location()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/status/locations", args[0][0])

    def test_get_device_tags(self):
        """get_device_tags -> GET /v1/devices/tags"""
        self.svc.get_device_tags()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/tags", args[0][0])

    def test_get_edge_node(self):
        """get_edge_node -> GET /v1/devices/id/{id}"""
        self.svc.get_edge_node(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id", args[0][0])

    def test_get_edge_node_attestation(self):
        """get_edge_node_attestation -> GET /v1/devices/id/{id}/attestation"""
        self.svc.get_edge_node_attestation(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/attestation", args[0][0])

    def test_get_edge_node_by_name(self):
        """get_edge_node_by_name -> GET /v1/devices/name/{name}"""
        self.svc.get_edge_node_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/name/test-name", args[0][0])

    def test_get_edge_node_by_serial(self):
        """get_edge_node_by_serial -> GET /v1/devices/serial/{serialno}"""
        self.svc.get_edge_node_by_serial(serialno="test-serialno")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/serial/test-serialno", args[0][0])

    def test_get_edge_node_edgeview_clientscript(self):
        """get_edge_node_edgeview_clientscript -> GET /v1/devices/id/{id}/edgeview/clientscript"""
        self.svc.get_edge_node_edgeview_clientscript(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/edgeview/clientscript", args[0][0])

    def test_get_edge_node_edgeview_status(self):
        """get_edge_node_edgeview_status -> GET /v1/devices/id/{id}/status/edgeview"""
        self.svc.get_edge_node_edgeview_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/status/edgeview", args[0][0])

    def test_get_edge_node_edgeview_status_by_name(self):
        """get_edge_node_edgeview_status_by_name -> GET /v1/devices/name/{name}/status/edgeview"""
        self.svc.get_edge_node_edgeview_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/name/test-name/status/edgeview", args[0][0])

    def test_get_edge_node_events(self):
        """get_edge_node_events -> GET /v1/devices/id/{objid}/events"""
        self.svc.get_edge_node_events(objid="test-objid")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-objid/events", args[0][0])

    def test_get_edge_node_events_by_name(self):
        """get_edge_node_events_by_name -> GET /v1/devices/name/{objname}/events"""
        self.svc.get_edge_node_events_by_name(objname="test-objname")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/name/test-objname/events", args[0][0])

    def test_get_edge_node_info(self):
        """get_edge_node_info -> GET /v1/devices/id/{id}/status/info"""
        self.svc.get_edge_node_info(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/status/info", args[0][0])

    def test_get_edge_node_info_by_name(self):
        """get_edge_node_info_by_name -> GET /v1/devices/name/{name}/status/info"""
        self.svc.get_edge_node_info_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/name/test-name/status/info", args[0][0])

    def test_get_edge_node_onboarding(self):
        """get_edge_node_onboarding -> GET /v1/devices/id/{id}/onboarding"""
        self.svc.get_edge_node_onboarding(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/onboarding", args[0][0])

    def test_get_edge_node_raw_status(self):
        """get_edge_node_raw_status -> GET /v1/devices/id/{id}/status/metrics/raw"""
        self.svc.get_edge_node_raw_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/status/metrics/raw", args[0][0])

    def test_get_edge_node_raw_status_by_name(self):
        """get_edge_node_raw_status_by_name -> GET /v1/devices/name/{name}/status/metrics/raw"""
        self.svc.get_edge_node_raw_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/name/test-name/status/metrics/raw", args[0][0])

    def test_get_edge_node_resource_metrics_by_id(self):
        """get_edge_node_resource_metrics_by_id -> GET /v1/devices/id/{objid}/timeSeries/{mType}"""
        self.svc.get_edge_node_resource_metrics_by_id(objid="test-objid", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-objid/timeSeries/test-mType", args[0][0])

    def test_get_edge_node_resource_metrics_by_name(self):
        """get_edge_node_resource_metrics_by_name -> GET /v1/devices/name/{objname}/timeSeries/{mType}"""
        self.svc.get_edge_node_resource_metrics_by_name(objname="test-objname", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/name/test-objname/timeSeries/test-mType", args[0][0])

    def test_get_edge_node_single_use_eve_image(self):
        """get_edge_node_single_use_eve_image -> GET /v1/devices/id/{id}/suimage"""
        self.svc.get_edge_node_single_use_eve_image(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/suimage", args[0][0])

    def test_get_edge_node_single_use_eve_image_download_link(self):
        """get_edge_node_single_use_eve_image_download_link -> GET /v1/devices/id/{id}/suimage/link"""
        self.svc.get_edge_node_single_use_eve_image_download_link(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/suimage/link", args[0][0])

    def test_get_edge_node_status(self):
        """get_edge_node_status -> GET /v1/devices/id/{id}/status"""
        self.svc.get_edge_node_status(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/id/test-id/status", args[0][0])

    def test_get_edge_node_status_by_name(self):
        """get_edge_node_status_by_name -> GET /v1/devices/name/{name}/status"""
        self.svc.get_edge_node_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/name/test-name/status", args[0][0])

    def test_get_global_brand(self):
        """get_global_brand -> GET /v1/brands/global/id/{id}"""
        self.svc.get_global_brand(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/brands/global/id/test-id", args[0][0])

    def test_get_global_brand_by_name(self):
        """get_global_brand_by_name -> GET /v1/brands/global/name/{name}"""
        self.svc.get_global_brand_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/brands/global/name/test-name", args[0][0])

    def test_get_global_hardware_model(self):
        """get_global_hardware_model -> GET /v1/sysmodels/global/id/{id}"""
        self.svc.get_global_hardware_model(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sysmodels/global/id/test-id", args[0][0])

    def test_get_global_hardware_model_by_name(self):
        """get_global_hardware_model_by_name -> GET /v1/sysmodels/global/name/{name}"""
        self.svc.get_global_hardware_model_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sysmodels/global/name/test-name", args[0][0])

    def test_get_hardware_model(self):
        """get_hardware_model -> GET /v1/sysmodels/id/{id}"""
        self.svc.get_hardware_model(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sysmodels/id/test-id", args[0][0])

    def test_get_hardware_model_by_name(self):
        """get_hardware_model_by_name -> GET /v1/sysmodels/name/{name}"""
        self.svc.get_hardware_model_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sysmodels/name/test-name", args[0][0])

    def test_get_pcr_template_by_id(self):
        """get_pcr_template_by_id -> GET /v1/pcrtemplates/id/{id}"""
        self.svc.get_pcr_template_by_id(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/pcrtemplates/id/test-id", args[0][0])

    def test_get_pcr_template_by_name(self):
        """get_pcr_template_by_name -> GET /v1/sysmodels/id/{modelId}/pcrtemplates/name/{name}"""
        self.svc.get_pcr_template_by_name(modelId="test-modelId", name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sysmodels/id/test-modelId/pcrtemplates/name/test-name", args[0][0])

    def test_get_pcr_templates(self):
        """get_pcr_templates -> GET /v1/sysmodels/id/{id}/pcrtemplates"""
        self.svc.get_pcr_templates(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sysmodels/id/test-id/pcrtemplates", args[0][0])

    def test_get_project(self):
        """get_project -> GET /v1/projects/id/{id}"""
        self.svc.get_project(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects/id/test-id", args[0][0])

    def test_get_project_by_name(self):
        """get_project_by_name -> GET /v1/projects/name/{name}"""
        self.svc.get_project_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects/name/test-name", args[0][0])

    def test_get_project_events(self):
        """get_project_events -> GET /v1/projects/id/{objid}/events"""
        self.svc.get_project_events(objid="test-objid")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects/id/test-objid/events", args[0][0])

    def test_get_project_events_by_name(self):
        """get_project_events_by_name -> GET /v1/projects/name/{objname}/events"""
        self.svc.get_project_events_by_name(objname="test-objname")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects/name/test-objname/events", args[0][0])

    def test_get_project_resource_metrics_by_id(self):
        """get_project_resource_metrics_by_id -> GET /v1/projects/id/{objid}/timeSeries/{mType}"""
        self.svc.get_project_resource_metrics_by_id(objid="test-objid", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects/id/test-objid/timeSeries/test-mType", args[0][0])

    def test_get_project_resource_metrics_by_name(self):
        """get_project_resource_metrics_by_name -> GET /v1/projects/name/{objname}/timeSeries/{mType}"""
        self.svc.get_project_resource_metrics_by_name(objname="test-objname", mType="test-mType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects/name/test-objname/timeSeries/test-mType", args[0][0])

    def test_get_project_status_by_id(self):
        """get_project_status_by_id -> GET /v1/projects/id/{id}/status"""
        self.svc.get_project_status_by_id(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects/id/test-id/status", args[0][0])

    def test_get_project_status_by_name(self):
        """get_project_status_by_name -> GET /v1/projects/name/{name}/status"""
        self.svc.get_project_status_by_name(name="test-name")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects/name/test-name/status", args[0][0])

    def test_get_project_tags(self):
        """get_project_tags -> GET /v1/projects/tags"""
        self.svc.get_project_tags()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects/tags", args[0][0])

    def test_import_hardware_model(self):
        """import_hardware_model -> PUT /v1/sysmodels/id/{id}/import"""
        self.svc.import_hardware_model(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/sysmodels/id/test-id/import", args[0][0])

    def test_offboard_edge_node(self):
        """offboard_edge_node -> PUT /v1/devices/id/{id}/offboard"""
        self.svc.offboard_edge_node(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/offboard", args[0][0])

    def test_prepare_edge_node_poweroff(self):
        """prepare_edge_node_poweroff -> PUT /v1/devices/id/{id}/preparepoweroff"""
        self.svc.prepare_edge_node_poweroff(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/preparepoweroff", args[0][0])

    def test_publish_edge_node(self):
        """publish_edge_node -> PUT /v1/devices/id/{id}/publish"""
        self.svc.publish_edge_node(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/publish", args[0][0])

    def test_query_brands(self):
        """query_brands -> GET /v1/brands"""
        self.svc.query_brands()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/brands", args[0][0])

    def test_query_edge_node_status(self):
        """query_edge_node_status -> GET /v1/devices/status"""
        self.svc.query_edge_node_status(namePattern="test-namePattern", projectName="test-projectName", projectNamePattern="test-projectNamePattern", fields="test-fields", next_pageToken="test-next_pageToken", next_orderBy="test-next_orderBy", next_pageNum="test-next_pageNum", next_pageSize="test-next_pageSize", next_totalPages="test-next_totalPages", runState="test-runState", clusterName="test-clusterName", load="test-load")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices/status", args[0][0])

    def test_query_edge_nodes(self):
        """query_edge_nodes -> GET /v1/devices"""
        self.svc.query_edge_nodes(namePattern="test-namePattern", next_pageToken="test-next_pageToken", next_orderBy="test-next_orderBy", next_pageNum="test-next_pageNum", next_pageSize="test-next_pageSize", next_totalPages="test-next_totalPages")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices", args[0][0])

    def test_query_global_brands(self):
        """query_global_brands -> GET /v1/brands/global"""
        self.svc.query_global_brands()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/brands/global", args[0][0])

    def test_query_global_hardware_models(self):
        """query_global_hardware_models -> GET /v1/sysmodels/global"""
        self.svc.query_global_hardware_models()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sysmodels/global", args[0][0])

    def test_query_hardware_models(self):
        """query_hardware_models -> GET /v1/sysmodels"""
        self.svc.query_hardware_models()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/sysmodels", args[0][0])

    def test_query_project_status(self):
        """query_project_status -> GET /v1/projects/status"""
        self.svc.query_project_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects/status", args[0][0])

    def test_query_project_status_config(self):
        """query_project_status_config -> GET /v1/projects/status-config"""
        self.svc.query_project_status_config()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects/status-config", args[0][0])

    def test_query_projects(self):
        """query_projects -> GET /v1/projects"""
        self.svc.query_projects()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/projects", args[0][0])

    def test_reboot_edge_node(self):
        """reboot_edge_node -> PUT /v1/devices/id/{id}/reboot"""
        self.svc.reboot_edge_node(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/reboot", args[0][0])

    def test_unpublish_edge_node(self):
        """unpublish_edge_node -> PUT /v1/devices/id/{id}/unpublish"""
        self.svc.unpublish_edge_node(id="test-id")
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/unpublish", args[0][0])

    def test_update_brand(self):
        """update_brand -> PUT /v1/brands/id/{id}"""
        self.svc.update_brand(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/brands/id/test-id", args[0][0])

    def test_update_deployment(self):
        """update_deployment -> PUT /v2/projects/id/{projectId}/deployments/id/{id}"""
        self.svc.update_deployment(projectId="test-projectId", id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v2/projects/id/test-projectId/deployments/id/test-id", args[0][0])

    def test_update_edge_node(self):
        """update_edge_node -> PUT /v1/devices/id/{id}"""
        self.svc.update_edge_node(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id", args[0][0])

    def test_update_edge_node_base_os_retry(self):
        """update_edge_node_base_os_retry -> PUT /v1/devices/id/{id}/baseos/upgrade/retry"""
        self.svc.update_edge_node_base_os_retry(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/devices/id/test-id/baseos/upgrade/retry", args[0][0])

    def test_update_hardware_model(self):
        """update_hardware_model -> PUT /v1/sysmodels/id/{id}"""
        self.svc.update_hardware_model(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/sysmodels/id/test-id", args[0][0])

    def test_update_pcr_template(self):
        """update_pcr_template -> PUT /v1/pcrtemplate/id/{id}"""
        self.svc.update_pcr_template(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/pcrtemplate/id/test-id", args[0][0])

    def test_update_project(self):
        """update_project -> PUT /v1/projects/id/{id}"""
        self.svc.update_project(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/projects/id/test-id", args[0][0])

    def test_method_count(self):
        """Verify expected method count."""
        methods = [m for m in dir(self.svc)
                   if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 91)


if __name__ == "__main__":
    unittest.main()
