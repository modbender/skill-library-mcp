#!/usr/bin/env python3
"""Exhaustive unit tests for every method in JobService."""

import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.job_service import JobService


def _mock_client():
    c = MagicMock()
    c.get.return_value = {"list": []}
    c.post.return_value = {"id": "new"}
    c.put.return_value = {"ok": True}
    c.delete.return_value = {"ok": True}
    c.patch.return_value = {"ok": True}
    return c


class TestJobService(unittest.TestCase):
    """One test per method in JobService (17 methods)."""

    def setUp(self):
        self.mc = _mock_client()
        self.svc = JobService(self.mc)

    def test_bulk_create_edge_application_instances(self):
        """bulk_create_edge_application_instances -> PUT /v1/jobs/apps/instances/create"""
        self.svc.bulk_create_edge_application_instances(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/jobs/apps/instances/create", args[0][0])

    def test_bulk_import_edge_applications(self):
        """bulk_import_edge_applications -> PUT /v1/jobs/apps/bundles/import"""
        self.svc.bulk_import_edge_applications(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/jobs/apps/bundles/import", args[0][0])

    def test_bulk_import_hardware_models(self):
        """bulk_import_hardware_models -> PUT /v1/jobs/models/import"""
        self.svc.bulk_import_hardware_models(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/jobs/models/import", args[0][0])

    def test_bulk_refresh_and_purge_edge_application_instances(self):
        """bulk_refresh_and_purge_edge_application_instances -> PUT /v1/jobs/apps/instances/refresh/purge"""
        self.svc.bulk_refresh_and_purge_edge_application_instances(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/jobs/apps/instances/refresh/purge", args[0][0])

    def test_bulk_refresh_edge_application_instances(self):
        """bulk_refresh_edge_application_instances -> PUT /v1/jobs/apps/instances/refresh"""
        self.svc.bulk_refresh_edge_application_instances(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/jobs/apps/instances/refresh", args[0][0])

    def test_bulk_update_edge_node_base_os(self):
        """bulk_update_edge_node_base_os -> PUT /v1/jobs/devices/baseos/upgrade"""
        self.svc.bulk_update_edge_node_base_os(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/jobs/devices/baseos/upgrade", args[0][0])

    def test_bulk_update_edge_node_base_os_retry(self):
        """bulk_update_edge_node_base_os_retry -> PUT /v1/jobs/devices/baseos/upgrade/retry"""
        self.svc.bulk_update_edge_node_base_os_retry(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/jobs/devices/baseos/upgrade/retry", args[0][0])

    def test_bulk_update_edge_node_deployment_tag(self):
        """bulk_update_edge_node_deployment_tag -> PUT /v1/jobs/devices/deployment/tags"""
        self.svc.bulk_update_edge_node_deployment_tag(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/jobs/devices/deployment/tags", args[0][0])

    def test_bulk_update_edge_node_project(self):
        """bulk_update_edge_node_project -> PUT /v1/jobs/devices/project/target"""
        self.svc.bulk_update_edge_node_project(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/jobs/devices/project/target", args[0][0])

    def test_bulk_update_edge_node_tags(self):
        """bulk_update_edge_node_tags -> PUT /v1/jobs/devices/tags"""
        self.svc.bulk_update_edge_node_tags(body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/jobs/devices/tags", args[0][0])

    def test_create_job(self):
        """create_job -> POST /v1/jobs"""
        self.svc.create_job(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/jobs", args[0][0])

    def test_delete_job(self):
        """delete_job -> DELETE /v1/jobs/id/{id}/objectType/{objectType}"""
        self.svc.delete_job(id="test-id", objectType="test-objectType")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/jobs/id/test-id/objectType/test-objectType", args[0][0])

    def test_get_job(self):
        """get_job -> GET /v1/jobs/id/{id}/objectType/{objectType}"""
        self.svc.get_job(id="test-id", objectType="test-objectType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/jobs/id/test-id/objectType/test-objectType", args[0][0])

    def test_get_job_by_id(self):
        """get_job_by_id -> GET /v1/jobs/id/{id}"""
        self.svc.get_job_by_id(id="test-id")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/jobs/id/test-id", args[0][0])

    def test_get_job_by_name(self):
        """get_job_by_name -> GET /v1/jobs/name/{name}/objectType/{objectType}"""
        self.svc.get_job_by_name(name="test-name", objectType="test-objectType")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/jobs/name/test-name/objectType/test-objectType", args[0][0])

    def test_query_jobs(self):
        """query_jobs -> GET /v1/jobs"""
        self.svc.query_jobs()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/jobs", args[0][0])

    def test_update_job(self):
        """update_job -> PUT /v1/jobs/id/{id}"""
        self.svc.update_job(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/jobs/id/test-id", args[0][0])

    def test_method_count(self):
        """Verify expected method count."""
        methods = [m for m in dir(self.svc)
                   if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 17)


if __name__ == "__main__":
    unittest.main()
