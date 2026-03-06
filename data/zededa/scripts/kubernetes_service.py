#!/usr/bin/env python3
"""
ZEDEDA Kubernetes Service — 36 endpoints

Covers Kubernetes deployments, GitOps repos, Helm charts & private repos,
Kubernetes secrets, ZKS cluster instances, and cluster groups.
"""

from __future__ import annotations
from typing import Any
from .client import ZededaClient
from .errors import KubernetesServiceError


def _qp(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None and k != "self"}


class KubernetesService:
    """Kubernetes Service — deployments, GitOps, Helm, secrets, ZKS, groups."""

    def __init__(self, client: ZededaClient):
        self.c = client

    # ======================================================================
    # KUBERNETES DEPLOYMENTS
    # ======================================================================

    def list_deployments(self, **kw: Any) -> Any:
        """GET /v1/cluster/instances/kubernetes/deployments"""
        return self.c.get("/v1/cluster/instances/kubernetes/deployments", query=_qp(kw))

    def create_deployment(self, body: dict) -> Any:
        """POST /v1/cluster/instances/kubernetes/deployments"""
        return self.c.post("/v1/cluster/instances/kubernetes/deployments", body=body)

    def get_deployment(self, deploymentId: str) -> Any:
        """GET /v1/cluster/instances/kubernetes/deployments/id/{deploymentId}"""
        return self.c.get(f"/v1/cluster/instances/kubernetes/deployments/id/{deploymentId}")

    def update_deployment(self, deploymentId: str, body: dict) -> Any:
        """PUT /v1/cluster/instances/kubernetes/deployments/id/{deploymentId}"""
        return self.c.put(f"/v1/cluster/instances/kubernetes/deployments/id/{deploymentId}", body=body)

    def delete_deployment(self, deploymentId: str) -> Any:
        """DELETE /v1/cluster/instances/kubernetes/deployments/id/{deploymentId}"""
        return self.c.delete(f"/v1/cluster/instances/kubernetes/deployments/id/{deploymentId}")

    # ======================================================================
    # GIT REPOS (GitOps)
    # ======================================================================

    def list_git_repos(self, **kw: Any) -> Any:
        """GET /v1/cluster/instances/kubernetes/gitrepos"""
        return self.c.get("/v1/cluster/instances/kubernetes/gitrepos", query=_qp(kw))

    def create_git_repo(self, body: dict) -> Any:
        """POST /v1/cluster/instances/kubernetes/gitrepos"""
        return self.c.post("/v1/cluster/instances/kubernetes/gitrepos", body=body)

    def get_git_repo(self, gitrepoId: str) -> Any:
        """GET /v1/cluster/instances/kubernetes/gitrepos/id/{gitrepoId}"""
        return self.c.get(f"/v1/cluster/instances/kubernetes/gitrepos/id/{gitrepoId}")

    def update_git_repo(self, gitrepoId: str, body: dict) -> Any:
        """PUT /v1/cluster/instances/kubernetes/gitrepos/id/{gitrepoId}"""
        return self.c.put(f"/v1/cluster/instances/kubernetes/gitrepos/id/{gitrepoId}", body=body)

    def delete_git_repo(self, gitrepoId: str) -> Any:
        """DELETE /v1/cluster/instances/kubernetes/gitrepos/id/{gitrepoId}"""
        return self.c.delete(f"/v1/cluster/instances/kubernetes/gitrepos/id/{gitrepoId}")

    # ======================================================================
    # HELM CHARTS
    # ======================================================================

    def list_helm_charts(self, **kw: Any) -> Any:
        """GET /v1/cluster/instances/kubernetes/helm/charts"""
        return self.c.get("/v1/cluster/instances/kubernetes/helm/charts", query=_qp(kw))

    def create_helm_chart(self) -> Any:
        """POST /v1/cluster/instances/kubernetes/helm/charts"""
        return self.c.post("/v1/cluster/instances/kubernetes/helm/charts")

    def get_helm_chart(self, chartName: str, chartVersion: str,
                       *, repoIdentifier: str | None = None) -> Any:
        """GET /v1/cluster/instances/kubernetes/helm/charts/name/{chartName}/version/{chartVersion}"""
        q = {"repoIdentifier": repoIdentifier}
        return self.c.get(
            f"/v1/cluster/instances/kubernetes/helm/charts/name/{chartName}/version/{chartVersion}",
            query=_qp(q),
        )

    def update_helm_chart(self, chartName: str, chartVersion: str, body: dict | None = None) -> Any:
        """PUT /v1/cluster/instances/kubernetes/helm/charts/name/{chartName}/version/{chartVersion}"""
        return self.c.put(
            f"/v1/cluster/instances/kubernetes/helm/charts/name/{chartName}/version/{chartVersion}",
            body=body,
        )

    def delete_helm_chart(self, chartName: str) -> Any:
        """DELETE /v1/cluster/instances/kubernetes/helm/charts/name/{chartName}"""
        return self.c.delete(f"/v1/cluster/instances/kubernetes/helm/charts/name/{chartName}")

    # ======================================================================
    # PRIVATE HELM REPOSITORIES
    # ======================================================================

    def list_private_repos(self, **kw: Any) -> Any:
        """GET /v1/cluster/instances/kubernetes/helm/repository"""
        return self.c.get("/v1/cluster/instances/kubernetes/helm/repository", query=_qp(kw))

    def create_private_repo(self, body: dict) -> Any:
        """POST /v1/cluster/instances/kubernetes/helm/repository"""
        return self.c.post("/v1/cluster/instances/kubernetes/helm/repository", body=body)

    def get_private_repo(self, privateRepoId: str) -> Any:
        """GET /v1/cluster/instances/kubernetes/helm/repository/id/{privateRepoId}"""
        return self.c.get(f"/v1/cluster/instances/kubernetes/helm/repository/id/{privateRepoId}")

    def update_private_repo(self, id: str, body: dict) -> Any:
        """PUT /v1/cluster/instances/kubernetes/helm/repository/id/{id}"""
        return self.c.put(f"/v1/cluster/instances/kubernetes/helm/repository/id/{id}", body=body)

    def delete_private_repo(self, privateRepoId: str) -> Any:
        """DELETE /v1/cluster/instances/kubernetes/helm/repository/id/{privateRepoId}"""
        return self.c.delete(f"/v1/cluster/instances/kubernetes/helm/repository/id/{privateRepoId}")

    def get_private_repo_charts(self, privateRepoId: str) -> Any:
        """GET /v1/cluster/instances/kubernetes/helm/repository/id/{privateRepoId}/charts"""
        return self.c.get(f"/v1/cluster/instances/kubernetes/helm/repository/id/{privateRepoId}/charts")

    # ======================================================================
    # KUBERNETES SECRETS
    # ======================================================================

    def list_secrets(self, **kw: Any) -> Any:
        """GET /v1/cluster/instances/kubernetes/secrets"""
        return self.c.get("/v1/cluster/instances/kubernetes/secrets", query=_qp(kw))

    def create_secret(self, body: dict) -> Any:
        """POST /v1/cluster/instances/kubernetes/secrets"""
        return self.c.post("/v1/cluster/instances/kubernetes/secrets", body=body)

    def get_secret(self, secretId: str) -> Any:
        """GET /v1/cluster/instances/kubernetes/secrets/id/{secretId}"""
        return self.c.get(f"/v1/cluster/instances/kubernetes/secrets/id/{secretId}")

    # ======================================================================
    # ZKS CLUSTER INSTANCES
    # ======================================================================

    def list_zks_instances(self, **kw: Any) -> Any:
        """GET /v1/zks/instances"""
        return self.c.get("/v1/zks/instances", query=_qp(kw))

    def create_zks_instance(self, body: dict) -> Any:
        """POST /v1/zks/instances"""
        return self.c.post("/v1/zks/instances", body=body)

    def get_zks_instance(self, zksId: str) -> Any:
        """GET /v1/zks/instances/id/{zksId}"""
        return self.c.get(f"/v1/zks/instances/id/{zksId}")

    def delete_zks_instance(self, zksId: str) -> Any:
        """DELETE /v1/zks/instances/id/{zksId}"""
        return self.c.delete(f"/v1/zks/instances/id/{zksId}")

    def update_zks_instance_nodes(self, zksId: str, body: dict) -> Any:
        """PUT /v1/zks/instances/id/{zksId}/nodes"""
        return self.c.put(f"/v1/zks/instances/id/{zksId}/nodes", body=body)

    def upgrade_zks_instance(self, zksId: str, body: dict) -> Any:
        """PUT /v1/zks/instances/id/{zksId}/upgrade"""
        return self.c.put(f"/v1/zks/instances/id/{zksId}/upgrade", body=body)

    def get_zks_instance_by_name(self, zksName: str) -> Any:
        """GET /v1/zks/instances/name/{zksName}"""
        return self.c.get(f"/v1/zks/instances/name/{zksName}")

    def get_zks_instances_status(self, **kw: Any) -> Any:
        """GET /v1/zks/instances/status"""
        return self.c.get("/v1/zks/instances/status", query=_qp(kw))

    # ======================================================================
    # CLUSTER GROUPS
    # ======================================================================

    def create_cluster_group(self, body: dict) -> Any:
        """POST /v1/zks/cluster/groups"""
        return self.c.post("/v1/zks/cluster/groups", body=body)

    def delete_cluster_group(self, clusterGroupId: str) -> Any:
        """DELETE /v1/zks/cluster/groups/id/{clusterGroupId}"""
        return self.c.delete(f"/v1/zks/cluster/groups/id/{clusterGroupId}")

    def get_cluster_group_manifest(self, **kw: Any) -> Any:
        """GET /v1/zks/cluster/groups/manifest"""
        return self.c.get("/v1/zks/cluster/groups/manifest", query=_qp(kw))

    def get_cluster_groups_status(self, **kw: Any) -> Any:
        """GET /v1/zks/cluster/groups/status"""
        return self.c.get("/v1/zks/cluster/groups/status", query=_qp(kw))
