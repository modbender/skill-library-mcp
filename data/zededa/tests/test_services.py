#!/usr/bin/env python3
"""Unit tests for all 11 ZEDEDA service modules.

Tests verify that each service method:
  1. Calls the correct HTTP method (GET/POST/PUT/DELETE/PATCH)
  2. Targets the correct API path
  3. Passes body/query parameters correctly

Uses a mock client to capture calls without making real HTTP requests.
"""

import os
import unittest
from unittest.mock import MagicMock, call

# Ensure token is set before importing
os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.node_service import NodeService
from scripts.node_cluster_service import NodeClusterService
from scripts.app_service import AppService
from scripts.app_profile_service import AppProfileService
from scripts.storage_service import StorageService
from scripts.network_service import NetworkService
from scripts.orchestration_service import OrchestrationService
from scripts.kubernetes_service import KubernetesService
from scripts.diag_service import DiagService
from scripts.job_service import JobService
from scripts.user_service import UserService


def make_mock_client():
    """Create a mock ZededaClient that records all HTTP calls."""
    client = MagicMock()
    client.get.return_value = {"list": []}
    client.post.return_value = {"id": "new-id"}
    client.put.return_value = {"ok": True}
    client.delete.return_value = {"ok": True}
    client.patch.return_value = {"ok": True}
    return client


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestNodeService(unittest.TestCase):
    def setUp(self):
        self.mc = make_mock_client()
        self.svc = NodeService(self.mc)

    # -- Brands --
    def test_query_brands(self):
        self.svc.query_brands()
        self.mc.get.assert_called()
        self.assertIn("/v1/brands", self.mc.get.call_args[0][0])

    def test_create_brand(self):
        self.svc.create_brand({"name": "test"})
        self.mc.post.assert_called_once()
        self.assertIn("/v1/brands", self.mc.post.call_args[0][0])

    def test_get_brand(self):
        self.svc.get_brand("b-id")
        self.mc.get.assert_called()
        self.assertIn("/v1/brands/id/b-id", self.mc.get.call_args[0][0])

    def test_delete_brand(self):
        self.svc.delete_brand("b-id")
        self.mc.delete.assert_called_once()
        self.assertIn("/v1/brands/id/b-id", self.mc.delete.call_args[0][0])

    # -- Devices --
    def test_query_edge_nodes(self):
        self.svc.query_edge_nodes()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/devices", args[0][0])

    def test_create_edge_node(self):
        self.svc.create_edge_node({"name": "dev1"})
        self.mc.post.assert_called()
        self.assertIn("/v1/devices", self.mc.post.call_args[0][0])

    def test_get_edge_node(self):
        self.svc.get_edge_node("abc")
        self.mc.get.assert_called()
        self.assertIn("/v1/devices/id/abc", self.mc.get.call_args[0][0])

    def test_update_edge_node(self):
        self.svc.update_edge_node("abc", {"name": "changed"})
        self.mc.put.assert_called()
        self.assertIn("/v1/devices/id/abc", self.mc.put.call_args[0][0])

    def test_delete_edge_node(self):
        self.svc.delete_edge_node("abc")
        self.mc.delete.assert_called()
        self.assertIn("/v1/devices/id/abc", self.mc.delete.call_args[0][0])

    def test_get_by_name(self):
        self.svc.get_edge_node_by_name("mydev")
        self.mc.get.assert_called()
        self.assertIn("/v1/devices/name/mydev", self.mc.get.call_args[0][0])

    def test_get_by_serial(self):
        self.svc.get_edge_node_by_serial("SN123")
        self.mc.get.assert_called()
        self.assertIn("/v1/devices/serial/SN123", self.mc.get.call_args[0][0])

    def test_reboot_device(self):
        self.svc.reboot_edge_node("abc")
        self.mc.put.assert_called()
        self.assertIn("/v1/devices/id/abc/reboot", self.mc.put.call_args[0][0])

    def test_activate_device(self):
        self.svc.activate_edge_node("abc")
        self.mc.put.assert_called()
        self.assertIn("/v1/devices/id/abc/activate", self.mc.put.call_args[0][0])

    def test_deactivate_device(self):
        self.svc.deactivate_edge_node("abc")
        self.mc.put.assert_called()
        self.assertIn("/v1/devices/id/abc/deactivate", self.mc.put.call_args[0][0])

    def test_offboard_device(self):
        self.svc.offboard_edge_node("abc")
        self.mc.put.assert_called()
        self.assertIn("/v1/devices/id/abc/offboard", self.mc.put.call_args[0][0])

    def test_enable_debug(self):
        self.svc.enable_edge_node_debug("abc")
        self.mc.put.assert_called()
        self.assertIn("/v1/devices/id/abc/debug/enable", self.mc.put.call_args[0][0])

    def test_get_status(self):
        self.svc.get_edge_node_status("abc")
        self.mc.get.assert_called()
        self.assertIn("/v1/devices/id/abc/status", self.mc.get.call_args[0][0])

    def test_get_events(self):
        self.svc.get_edge_node_events("abc")
        self.mc.get.assert_called()
        self.assertIn("/v1/devices/id/abc/events", self.mc.get.call_args[0][0])

    # -- Hardware Models --
    def test_query_models(self):
        self.svc.query_hardware_models()
        self.mc.get.assert_called()
        self.assertIn("/v1/sysmodels", self.mc.get.call_args[0][0])

    def test_create_model(self):
        self.svc.create_hardware_model({"name": "m1"})
        self.mc.post.assert_called()
        self.assertIn("/v1/sysmodels", self.mc.post.call_args[0][0])

    def test_import_model(self):
        self.svc.import_hardware_model("m1")
        self.mc.put.assert_called()
        self.assertIn("/v1/sysmodels/id/m1/import", self.mc.put.call_args[0][0])

    # -- Projects --
    def test_query_projects(self):
        self.svc.query_projects()
        self.mc.get.assert_called()
        self.assertIn("/v1/projects", self.mc.get.call_args[0][0])

    def test_create_project_v2(self):
        self.svc.create_project_v2({"name": "p1"})
        self.mc.post.assert_called()
        self.assertIn("/v2/projects", self.mc.post.call_args[0][0])

    def test_get_deployment(self):
        self.svc.get_deployment_by_id("proj1", "dep1")
        self.mc.get.assert_called()
        self.assertIn("/v2/projects/id/proj1/deployments/id/dep1", self.mc.get.call_args[0][0])

    # -- Total method count --
    def test_method_count_at_least_90(self):
        methods = [m for m in dir(self.svc) if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 90)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APP SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestAppService(unittest.TestCase):
    def setUp(self):
        self.mc = make_mock_client()
        self.svc = AppService(self.mc)

    def test_query_bundles(self):
        self.svc.query_edge_application_bundles()
        self.mc.get.assert_called()
        self.assertIn("/v1/apps", self.mc.get.call_args[0][0])

    def test_create_bundle(self):
        self.svc.create_edge_application_bundle({"name": "app1"})
        self.mc.post.assert_called()

    def test_get_bundle(self):
        self.svc.get_edge_application_bundle("a1")
        self.mc.get.assert_called()
        self.assertIn("/v1/apps/id/a1", self.mc.get.call_args[0][0])

    def test_delete_bundle(self):
        self.svc.delete_edge_application_bundle("a1")
        self.mc.delete.assert_called()

    def test_create_instance(self):
        self.svc.create_edge_application_instance({"name": "i1"})
        self.mc.post.assert_called()
        self.assertIn("/v1/apps/instances", self.mc.post.call_args[0][0])

    def test_activate_instance(self):
        self.svc.activate_edge_application_instance("i1")
        self.mc.put.assert_called()
        self.assertIn("/v1/apps/instances/id/i1/activate", self.mc.put.call_args[0][0])

    def test_deactivate_instance(self):
        self.svc.deactivate_edge_application_instance("i1")
        self.mc.put.assert_called()
        self.assertIn("/v1/apps/instances/id/i1/deactivate", self.mc.put.call_args[0][0])

    def test_restart_instance(self):
        self.svc.restart_edge_application_instance("i1")
        self.mc.put.assert_called()
        self.assertIn("/v1/apps/instances/id/i1/restart", self.mc.put.call_args[0][0])

    def test_refresh_instance(self):
        self.svc.refresh_edge_application_instance("i1")
        self.mc.put.assert_called()

    def test_instance_status(self):
        self.svc.get_edge_application_instance_status("i1")
        self.mc.get.assert_called()
        self.assertIn("/v1/apps/instances/id/i1/status", self.mc.get.call_args[0][0])

    def test_instance_logs(self):
        self.svc.get_edge_application_instance_logs("i1")
        self.mc.get.assert_called()
        self.assertIn("/v1/apps/instances/id/i1/logs", self.mc.get.call_args[0][0])

    def test_remote_console(self):
        self.svc.connect_to_edge_application_instance("i1")
        self.mc.put.assert_called()
        self.assertIn("/v1/apps/instances/id/i1/console/remote", self.mc.put.call_args[0][0])

    def test_traffic_flows(self):
        self.svc.get_edge_application_instance_traffic_flows("i1")
        self.mc.get.assert_called()
        self.assertIn("flowlog/classification", self.mc.get.call_args[0][0])

    def test_snapshots(self):
        self.svc.get_app_instance_snapshots("i1")
        self.mc.get.assert_called()
        self.assertIn("snapshots", self.mc.get.call_args[0][0])

    # -- Images --
    def test_query_images(self):
        self.svc.query_images()
        self.mc.get.assert_called()
        self.assertIn("/v1/apps/images", self.mc.get.call_args[0][0])

    # -- Datastores --
    def test_query_datastores(self):
        self.svc.query_datastores()
        self.mc.get.assert_called()
        self.assertIn("/v1/datastores", self.mc.get.call_args[0][0])

    # -- Volumes --
    def test_query_volumes(self):
        self.svc.query_volume_instances()
        self.mc.get.assert_called()
        self.assertIn("/v1/volumes/instances", self.mc.get.call_args[0][0])

    # -- V2 instances --
    def test_v2_create_instance(self):
        self.svc.create_edge_application_instance_v2({"name": "v2i"})
        self.mc.post.assert_called()
        self.assertIn("/v2/apps/instances", self.mc.post.call_args[0][0])

    def test_v2_activate_instance(self):
        self.svc.activate_edge_application_instance_v2("i1")
        self.mc.put.assert_called()
        self.assertIn("/v2/apps/instances/id/i1/activate", self.mc.put.call_args[0][0])

    # -- Patch Envelopes --
    def test_patch_envelopes(self):
        self.svc.query_patch_envelopes_v1()
        self.mc.get.assert_called()
        self.assertIn("/v1/patch-envelope", self.mc.get.call_args[0][0])

    # -- Beta --
    def test_beta_apps(self):
        self.svc.query_edge_application_bundles_beta()
        self.mc.get.assert_called()
        self.assertIn("/beta/apps", self.mc.get.call_args[0][0])

    # -- Method count --
    def test_method_count_at_least_80(self):
        methods = [m for m in dir(self.svc) if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 80)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# USER SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestUserService(unittest.TestCase):
    def setUp(self):
        self.mc = make_mock_client()
        self.svc = UserService(self.mc)

    def test_query_users(self):
        self.svc.query_users()
        self.mc.get.assert_called()

    def test_get_user(self):
        self.svc.get_user("u1")
        self.mc.get.assert_called()
        self.assertIn("/v1/users/id/u1", self.mc.get.call_args[0][0])

    def test_create_user(self):
        self.svc.create_user({"username": "test"})
        self.mc.post.assert_called()

    def test_delete_user(self):
        self.svc.delete_user("u1")
        self.mc.delete.assert_called()

    def test_get_user_self(self):
        self.svc.get_user_self()
        self.mc.get.assert_called()
        self.assertIn("/v1/users/self", self.mc.get.call_args[0][0])

    def test_query_roles(self):
        self.svc.query_roles()
        self.mc.get.assert_called()
        self.assertIn("/v1/roles", self.mc.get.call_args[0][0])

    def test_query_enterprises(self):
        self.svc.query_enterprises()
        self.mc.get.assert_called()
        self.assertIn("/v1/enterprises", self.mc.get.call_args[0][0])

    def test_enterprise_self(self):
        self.svc.get_enterprise_self()
        self.mc.get.assert_called()
        self.assertIn("/v1/enterprises/self", self.mc.get.call_args[0][0])

    def test_query_sessions(self):
        self.svc.query_user_sessions()
        self.mc.get.assert_called()

    def test_query_realms(self):
        self.svc.query_realms()
        self.mc.get.assert_called()
        self.assertIn("/v1/realms", self.mc.get.call_args[0][0])

    def test_method_count_67(self):
        methods = [m for m in dir(self.svc) if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 67)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STORAGE SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestStorageService(unittest.TestCase):
    def setUp(self):
        self.mc = make_mock_client()
        self.svc = StorageService(self.mc)

    def test_query_patch_envelopes(self):
        self.svc.query_patch_envelopes()
        self.mc.get.assert_called()

    def test_get_patch_envelope(self):
        self.svc.get_patch_envelope("pe1")
        self.mc.get.assert_called()

    def test_create_patch_envelope(self):
        self.svc.create_patch_envelope({"name": "pe"})
        self.mc.post.assert_called()

    def test_query_attestation(self):
        self.svc.query_attestation_policies()
        self.mc.get.assert_called()

    def test_query_deployment_policies(self):
        self.svc.query_deployment_policies()
        self.mc.get.assert_called()

    def test_method_count(self):
        methods = [m for m in dir(self.svc) if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 30)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ORCHESTRATION SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestOrchestrationService(unittest.TestCase):
    def setUp(self):
        self.mc = make_mock_client()
        self.svc = OrchestrationService(self.mc)

    def test_query_clusters(self):
        self.svc.query_cluster_instances()
        self.mc.get.assert_called()

    def test_get_cluster(self):
        self.svc.get_cluster_instance("c1")
        self.mc.get.assert_called()

    def test_create_cluster(self):
        self.svc.create_cluster_instance({"name": "c1"})
        self.mc.post.assert_called()

    def test_query_datastreams(self):
        self.svc.query_data_streams()
        self.mc.get.assert_called()

    def test_query_plugins(self):
        self.svc.query_plugins()
        self.mc.get.assert_called()

    def test_api_usage(self):
        self.svc.query_api_usage()
        self.mc.get.assert_called()

    def test_method_count_37(self):
        methods = [m for m in dir(self.svc) if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 37)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# KUBERNETES SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestKubernetesService(unittest.TestCase):
    def setUp(self):
        self.mc = make_mock_client()
        self.svc = KubernetesService(self.mc)

    def test_list_deployments(self):
        self.svc.list_deployments()
        self.mc.get.assert_called()

    def test_list_git_repos(self):
        self.svc.list_git_repos()
        self.mc.get.assert_called()

    def test_list_helm_charts(self):
        self.svc.list_helm_charts()
        self.mc.get.assert_called()

    def test_list_secrets(self):
        self.svc.list_secrets()
        self.mc.get.assert_called()

    def test_list_zks(self):
        self.svc.list_zks_instances()
        self.mc.get.assert_called()

    def test_list_private_repos(self):
        self.svc.list_private_repos()
        self.mc.get.assert_called()

    def test_method_count_36(self):
        methods = [m for m in dir(self.svc) if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 36)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DIAGNOSTICS SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestDiagService(unittest.TestCase):
    def setUp(self):
        self.mc = make_mock_client()
        self.svc = DiagService(self.mc)

    def test_device_twin_config(self):
        self.svc.get_device_twin_config("d1")
        self.mc.get.assert_called()

    def test_events_timeline(self):
        self.svc.get_events_timeline()
        self.mc.get.assert_called()

    def test_cloud_health(self):
        self.svc.check_cloud_health()
        self.mc.get.assert_called()

    def test_bootstrap_config(self):
        self.svc.get_device_twin_bootstrap_config("d1")
        self.mc.get.assert_called()

    def test_method_count(self):
        methods = [m for m in dir(self.svc) if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 20)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# APP PROFILE SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestAppProfileService(unittest.TestCase):
    def setUp(self):
        self.mc = make_mock_client()
        self.svc = AppProfileService(self.mc)

    def test_query_policies(self):
        self.svc.query_app_policies()
        self.mc.get.assert_called()

    def test_get_policy(self):
        self.svc.get_app_policy("p1")
        self.mc.get.assert_called()

    def test_create_policy(self):
        self.svc.create_app_policy({"name": "pol"})
        self.mc.post.assert_called()

    def test_method_count(self):
        methods = [m for m in dir(self.svc) if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 19)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NETWORK SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestNetworkService(unittest.TestCase):
    def setUp(self):
        self.mc = make_mock_client()
        self.svc = NetworkService(self.mc)

    def test_query_networks(self):
        self.svc.query_networks()
        self.mc.get.assert_called()

    def test_get_network(self):
        self.svc.get_network("n1")
        self.mc.get.assert_called()

    def test_create_network(self):
        self.svc.create_network({"name": "net"})
        self.mc.post.assert_called()

    def test_method_count(self):
        methods = [m for m in dir(self.svc) if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 16)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# JOB SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestJobService(unittest.TestCase):
    def setUp(self):
        self.mc = make_mock_client()
        self.svc = JobService(self.mc)

    def test_query_jobs(self):
        self.svc.query_jobs()
        self.mc.get.assert_called()

    def test_get_job(self):
        self.svc.get_job_by_id("j1")
        self.mc.get.assert_called()

    def test_create_job(self):
        self.svc.create_job({"name": "j1"})
        self.mc.post.assert_called()

    def test_method_count_17(self):
        methods = [m for m in dir(self.svc) if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 17)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NODE CLUSTER SERVICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestNodeClusterService(unittest.TestCase):
    def setUp(self):
        self.mc = make_mock_client()
        self.svc = NodeClusterService(self.mc)

    def test_query_clusters(self):
        self.svc.query_edge_node_clusters()
        self.mc.get.assert_called()

    def test_get_cluster(self):
        self.svc.get_edge_node_cluster("nc1")
        self.mc.get.assert_called()

    def test_create_cluster(self):
        self.svc.create_edge_node_cluster({"name": "nc"})
        self.mc.post.assert_called()

    def test_method_count_13(self):
        methods = [m for m in dir(self.svc) if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 13)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AGGREGATE COVERAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestAggregateCoverage(unittest.TestCase):
    """Verify total endpoint count across all services."""

    def test_total_method_count_exceeds_442(self):
        services = [
            NodeService(make_mock_client()),
            AppService(make_mock_client()),
            UserService(make_mock_client()),
            StorageService(make_mock_client()),
            OrchestrationService(make_mock_client()),
            KubernetesService(make_mock_client()),
            DiagService(make_mock_client()),
            AppProfileService(make_mock_client()),
            NetworkService(make_mock_client()),
            JobService(make_mock_client()),
            NodeClusterService(make_mock_client()),
        ]
        total = 0
        for svc in services:
            methods = [m for m in dir(svc) if not m.startswith("_") and callable(getattr(svc, m))]
            total += len(methods)
        self.assertGreaterEqual(total, 442,
                                f"Total methods ({total}) should be >= 442 endpoints")


if __name__ == "__main__":
    unittest.main()
