#!/usr/bin/env python3
"""Exhaustive unit tests for every method in KubernetesService."""

import os
import unittest
from unittest.mock import MagicMock

os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token")

from scripts.kubernetes_service import KubernetesService


def _mock_client():
    c = MagicMock()
    c.get.return_value = {"list": []}
    c.post.return_value = {"id": "new"}
    c.put.return_value = {"ok": True}
    c.delete.return_value = {"ok": True}
    c.patch.return_value = {"ok": True}
    return c


class TestKubernetesService(unittest.TestCase):
    """One test per method in KubernetesService (36 methods)."""

    def setUp(self):
        self.mc = _mock_client()
        self.svc = KubernetesService(self.mc)

    def test_create_cluster_group(self):
        """create_cluster_group -> POST /v1/zks/cluster/groups"""
        self.svc.create_cluster_group(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/zks/cluster/groups", args[0][0])

    def test_create_deployment(self):
        """create_deployment -> POST /v1/cluster/instances/kubernetes/deployments"""
        self.svc.create_deployment(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/deployments", args[0][0])

    def test_create_git_repo(self):
        """create_git_repo -> POST /v1/cluster/instances/kubernetes/gitrepos"""
        self.svc.create_git_repo(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/gitrepos", args[0][0])

    def test_create_helm_chart(self):
        """create_helm_chart -> POST /v1/cluster/instances/kubernetes/helm/charts"""
        self.svc.create_helm_chart()
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/helm/charts", args[0][0])

    def test_create_private_repo(self):
        """create_private_repo -> POST /v1/cluster/instances/kubernetes/helm/repository"""
        self.svc.create_private_repo(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/helm/repository", args[0][0])

    def test_create_secret(self):
        """create_secret -> POST /v1/cluster/instances/kubernetes/secrets"""
        self.svc.create_secret(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/secrets", args[0][0])

    def test_create_zks_instance(self):
        """create_zks_instance -> POST /v1/zks/instances"""
        self.svc.create_zks_instance(body={"test": True})
        self.mc.post.assert_called()
        args = self.mc.post.call_args
        self.assertIn("/v1/zks/instances", args[0][0])

    def test_delete_cluster_group(self):
        """delete_cluster_group -> DELETE /v1/zks/cluster/groups/id/{clusterGroupId}"""
        self.svc.delete_cluster_group(clusterGroupId="test-clusterGroupId")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/zks/cluster/groups/id/test-clusterGroupId", args[0][0])

    def test_delete_deployment(self):
        """delete_deployment -> DELETE /v1/cluster/instances/kubernetes/deployments/id/{deploymentId}"""
        self.svc.delete_deployment(deploymentId="test-deploymentId")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/deployments/id/test-deploymentId", args[0][0])

    def test_delete_git_repo(self):
        """delete_git_repo -> DELETE /v1/cluster/instances/kubernetes/gitrepos/id/{gitrepoId}"""
        self.svc.delete_git_repo(gitrepoId="test-gitrepoId")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/gitrepos/id/test-gitrepoId", args[0][0])

    def test_delete_helm_chart(self):
        """delete_helm_chart -> DELETE /v1/cluster/instances/kubernetes/helm/charts/name/{chartName}"""
        self.svc.delete_helm_chart(chartName="test-chartName")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/helm/charts/name/test-chartName", args[0][0])

    def test_delete_private_repo(self):
        """delete_private_repo -> DELETE /v1/cluster/instances/kubernetes/helm/repository/id/{privateRepoId}"""
        self.svc.delete_private_repo(privateRepoId="test-privateRepoId")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/helm/repository/id/test-privateRepoId", args[0][0])

    def test_delete_zks_instance(self):
        """delete_zks_instance -> DELETE /v1/zks/instances/id/{zksId}"""
        self.svc.delete_zks_instance(zksId="test-zksId")
        self.mc.delete.assert_called()
        args = self.mc.delete.call_args
        self.assertIn("/v1/zks/instances/id/test-zksId", args[0][0])

    def test_get_cluster_group_manifest(self):
        """get_cluster_group_manifest -> GET /v1/zks/cluster/groups/manifest"""
        self.svc.get_cluster_group_manifest()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/zks/cluster/groups/manifest", args[0][0])

    def test_get_cluster_groups_status(self):
        """get_cluster_groups_status -> GET /v1/zks/cluster/groups/status"""
        self.svc.get_cluster_groups_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/zks/cluster/groups/status", args[0][0])

    def test_get_deployment(self):
        """get_deployment -> GET /v1/cluster/instances/kubernetes/deployments/id/{deploymentId}"""
        self.svc.get_deployment(deploymentId="test-deploymentId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/deployments/id/test-deploymentId", args[0][0])

    def test_get_git_repo(self):
        """get_git_repo -> GET /v1/cluster/instances/kubernetes/gitrepos/id/{gitrepoId}"""
        self.svc.get_git_repo(gitrepoId="test-gitrepoId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/gitrepos/id/test-gitrepoId", args[0][0])

    def test_get_helm_chart(self):
        """get_helm_chart -> GET ?"""
        self.svc.get_helm_chart(chartName="test-chartName", chartVersion="test-chartVersion", repoIdentifier="test-repoIdentifier")
        self.mc.get.assert_called()

    def test_get_private_repo(self):
        """get_private_repo -> GET /v1/cluster/instances/kubernetes/helm/repository/id/{privateRepoId}"""
        self.svc.get_private_repo(privateRepoId="test-privateRepoId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/helm/repository/id/test-privateRepoId", args[0][0])

    def test_get_private_repo_charts(self):
        """get_private_repo_charts -> GET /v1/cluster/instances/kubernetes/helm/repository/id/{privateRepoId}/charts"""
        self.svc.get_private_repo_charts(privateRepoId="test-privateRepoId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/helm/repository/id/test-privateRepoId/charts", args[0][0])

    def test_get_secret(self):
        """get_secret -> GET /v1/cluster/instances/kubernetes/secrets/id/{secretId}"""
        self.svc.get_secret(secretId="test-secretId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/secrets/id/test-secretId", args[0][0])

    def test_get_zks_instance(self):
        """get_zks_instance -> GET /v1/zks/instances/id/{zksId}"""
        self.svc.get_zks_instance(zksId="test-zksId")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/zks/instances/id/test-zksId", args[0][0])

    def test_get_zks_instance_by_name(self):
        """get_zks_instance_by_name -> GET /v1/zks/instances/name/{zksName}"""
        self.svc.get_zks_instance_by_name(zksName="test-zksName")
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/zks/instances/name/test-zksName", args[0][0])

    def test_get_zks_instances_status(self):
        """get_zks_instances_status -> GET /v1/zks/instances/status"""
        self.svc.get_zks_instances_status()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/zks/instances/status", args[0][0])

    def test_list_deployments(self):
        """list_deployments -> GET /v1/cluster/instances/kubernetes/deployments"""
        self.svc.list_deployments()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/deployments", args[0][0])

    def test_list_git_repos(self):
        """list_git_repos -> GET /v1/cluster/instances/kubernetes/gitrepos"""
        self.svc.list_git_repos()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/gitrepos", args[0][0])

    def test_list_helm_charts(self):
        """list_helm_charts -> GET /v1/cluster/instances/kubernetes/helm/charts"""
        self.svc.list_helm_charts()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/helm/charts", args[0][0])

    def test_list_private_repos(self):
        """list_private_repos -> GET /v1/cluster/instances/kubernetes/helm/repository"""
        self.svc.list_private_repos()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/helm/repository", args[0][0])

    def test_list_secrets(self):
        """list_secrets -> GET /v1/cluster/instances/kubernetes/secrets"""
        self.svc.list_secrets()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/secrets", args[0][0])

    def test_list_zks_instances(self):
        """list_zks_instances -> GET /v1/zks/instances"""
        self.svc.list_zks_instances()
        self.mc.get.assert_called()
        args = self.mc.get.call_args
        self.assertIn("/v1/zks/instances", args[0][0])

    def test_update_deployment(self):
        """update_deployment -> PUT /v1/cluster/instances/kubernetes/deployments/id/{deploymentId}"""
        self.svc.update_deployment(deploymentId="test-deploymentId", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/deployments/id/test-deploymentId", args[0][0])

    def test_update_git_repo(self):
        """update_git_repo -> PUT /v1/cluster/instances/kubernetes/gitrepos/id/{gitrepoId}"""
        self.svc.update_git_repo(gitrepoId="test-gitrepoId", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/gitrepos/id/test-gitrepoId", args[0][0])

    def test_update_helm_chart(self):
        """update_helm_chart -> PUT ?"""
        self.svc.update_helm_chart(chartName="test-chartName", chartVersion="test-chartVersion", body={"test": True})
        self.mc.put.assert_called()

    def test_update_private_repo(self):
        """update_private_repo -> PUT /v1/cluster/instances/kubernetes/helm/repository/id/{id}"""
        self.svc.update_private_repo(id="test-id", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/cluster/instances/kubernetes/helm/repository/id/test-id", args[0][0])

    def test_update_zks_instance_nodes(self):
        """update_zks_instance_nodes -> PUT /v1/zks/instances/id/{zksId}/nodes"""
        self.svc.update_zks_instance_nodes(zksId="test-zksId", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/zks/instances/id/test-zksId/nodes", args[0][0])

    def test_upgrade_zks_instance(self):
        """upgrade_zks_instance -> PUT /v1/zks/instances/id/{zksId}/upgrade"""
        self.svc.upgrade_zks_instance(zksId="test-zksId", body={"test": True})
        self.mc.put.assert_called()
        args = self.mc.put.call_args
        self.assertIn("/v1/zks/instances/id/test-zksId/upgrade", args[0][0])

    def test_method_count(self):
        """Verify expected method count."""
        methods = [m for m in dir(self.svc)
                   if not m.startswith("_") and callable(getattr(self.svc, m))]
        self.assertGreaterEqual(len(methods), 36)


if __name__ == "__main__":
    unittest.main()
