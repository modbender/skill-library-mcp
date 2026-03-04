#!/usr/bin/env python3
"""
ZEDEDA Orchestration Service — 37 endpoints

Covers cluster instances (CRUD, lifecycle, kubeconfig), data streams,
third-party plugins, Azure deployments, and API usage tracking.
"""

from __future__ import annotations
from typing import Any
from .client import ZededaClient
from .errors import OrchestrationServiceError


def _qp(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None and k != "self"}


class OrchestrationService:
    """Orchestration Service — cluster instances, data streams, plugins."""

    def __init__(self, client: ZededaClient):
        self.c = client

    # ======================================================================
    # CLUSTER INSTANCES
    # ======================================================================

    def query_cluster_instances(self, **kw: Any) -> Any:
        """GET /v1/cluster/instances"""
        return self.c.get("/v1/cluster/instances", query=_qp(kw))

    def create_cluster_instance(self, body: dict) -> Any:
        """POST /v1/cluster/instances"""
        return self.c.post("/v1/cluster/instances", body=body)

    def get_cluster_instance(self, id: str) -> Any:
        """GET /v1/cluster/instances/id/{id}"""
        return self.c.get(f"/v1/cluster/instances/id/{id}")

    def update_cluster_instance(self, id: str, body: dict) -> Any:
        """PUT /v1/cluster/instances/id/{id}"""
        return self.c.put(f"/v1/cluster/instances/id/{id}", body=body)

    def delete_cluster_instance(self, id: str) -> Any:
        """DELETE /v1/cluster/instances/id/{id}"""
        return self.c.delete(f"/v1/cluster/instances/id/{id}")

    def activate_cluster_instance(self, id: str) -> Any:
        """PUT /v1/cluster/instances/id/{id}/activate"""
        return self.c.put(f"/v1/cluster/instances/id/{id}/activate")

    def deactivate_cluster_instance(self, id: str) -> Any:
        """PUT /v1/cluster/instances/id/{id}/deactivate"""
        return self.c.put(f"/v1/cluster/instances/id/{id}/deactivate")

    def refresh_cluster_instance(self, id: str) -> Any:
        """PUT /v1/cluster/instances/id/{id}/refresh"""
        return self.c.put(f"/v1/cluster/instances/id/{id}/refresh")

    def refresh_purge_cluster_instance(self, id: str) -> Any:
        """PUT /v1/cluster/instances/id/{id}/refresh/purge"""
        return self.c.put(f"/v1/cluster/instances/id/{id}/refresh/purge")

    def restart_cluster_instance(self, id: str) -> Any:
        """PUT /v1/cluster/instances/id/{id}/restart"""
        return self.c.put(f"/v1/cluster/instances/id/{id}/restart")

    def get_cluster_instance_by_name(self, name: str) -> Any:
        """GET /v1/cluster/instances/name/{name}"""
        return self.c.get(f"/v1/cluster/instances/name/{name}")

    # -- Cluster instance status --------------------------------------------

    def query_cluster_instance_status(self, **kw: Any) -> Any:
        """GET /v1/cluster/instances/status"""
        return self.c.get("/v1/cluster/instances/status", query=_qp(kw))

    def query_cluster_instance_status_config(self, **kw: Any) -> Any:
        """GET /v1/cluster/instances/status-config"""
        return self.c.get("/v1/cluster/instances/status-config", query=_qp(kw))

    def get_cluster_instance_status(self, id: str) -> Any:
        """GET /v1/cluster/instances/id/{id}/status"""
        return self.c.get(f"/v1/cluster/instances/id/{id}/status")

    def get_cluster_instance_status_by_name(self, name: str) -> Any:
        """GET /v1/cluster/instances/name/{name}/status"""
        return self.c.get(f"/v1/cluster/instances/name/{name}/status")

    # -- Cluster instance kubeconfig ----------------------------------------

    def get_cluster_instance_kubeconfig_by_id(self, id: str) -> Any:
        """GET /v1/cluster/instances/id/{id}/status/kubeconfig"""
        return self.c.get(f"/v1/cluster/instances/id/{id}/status/kubeconfig")

    def download_cluster_instance_kubeconfig_by_id(self, id: str) -> Any:
        """GET /v1/cluster/instances/id/{id}/status/kubeconfig/download"""
        return self.c.get(f"/v1/cluster/instances/id/{id}/status/kubeconfig/download")

    def get_cluster_instance_kubeconfig_by_name(self, name: str) -> Any:
        """GET /v1/cluster/instances/name/{name}/status/kubeconfig"""
        return self.c.get(f"/v1/cluster/instances/name/{name}/status/kubeconfig")

    def download_cluster_instance_kubeconfig_by_name(self, name: str) -> Any:
        """GET /v1/cluster/instances/name/{name}/status/kubeconfig/download"""
        return self.c.get(f"/v1/cluster/instances/name/{name}/status/kubeconfig/download")

    # -- Cluster instance events & tags -------------------------------------

    def get_cluster_instance_events(self, objid: str, **kw: Any) -> Any:
        """GET /v1/cluster/instances/id/{objid}/events"""
        return self.c.get(f"/v1/cluster/instances/id/{objid}/events", query=_qp(kw))

    def get_cluster_instance_events_by_name(self, objname: str, **kw: Any) -> Any:
        """GET /v1/cluster/instances/name/{objname}/events"""
        return self.c.get(f"/v1/cluster/instances/name/{objname}/events", query=_qp(kw))

    def get_cluster_instance_tags(self) -> Any:
        """GET /v1/cluster/instances/tags"""
        return self.c.get("/v1/cluster/instances/tags")

    # ======================================================================
    # DATA STREAMS
    # ======================================================================

    def query_data_streams(self, **kw: Any) -> Any:
        """GET /v1/datastreams"""
        return self.c.get("/v1/datastreams", query=_qp(kw))

    def create_data_stream(self, body: dict) -> Any:
        """POST /v1/datastreams"""
        return self.c.post("/v1/datastreams", body=body)

    def get_data_stream_by_id(self, id: str) -> Any:
        """GET /v1/datastreams/id/{id}"""
        return self.c.get(f"/v1/datastreams/id/{id}")

    def update_data_stream(self, id: str, body: dict) -> Any:
        """PUT /v1/datastreams/id/{id}"""
        return self.c.put(f"/v1/datastreams/id/{id}", body=body)

    def delete_data_stream(self, id: str) -> Any:
        """DELETE /v1/datastreams/id/{id}"""
        return self.c.delete(f"/v1/datastreams/id/{id}")

    def get_data_stream_by_name(self, name: str) -> Any:
        """GET /v1/datastreams/name/{name}"""
        return self.c.get(f"/v1/datastreams/name/{name}")

    # ======================================================================
    # THIRD-PARTY PLUGINS
    # ======================================================================

    def query_plugins(self, **kw: Any) -> Any:
        """GET /v1/plugins"""
        return self.c.get("/v1/plugins", query=_qp(kw))

    def create_plugin(self, body: dict) -> Any:
        """POST /v1/plugins"""
        return self.c.post("/v1/plugins", body=body)

    def get_plugin_by_id(self, id: str) -> Any:
        """GET /v1/plugins/id/{id}"""
        return self.c.get(f"/v1/plugins/id/{id}")

    def update_plugin(self, id: str, body: dict) -> Any:
        """PUT /v1/plugins/id/{id}"""
        return self.c.put(f"/v1/plugins/id/{id}", body=body)

    def delete_plugin(self, id: str) -> Any:
        """DELETE /v1/plugins/id/{id}"""
        return self.c.delete(f"/v1/plugins/id/{id}")

    def get_plugin_by_name(self, name: str) -> Any:
        """GET /v1/plugins/name/{name}"""
        return self.c.get(f"/v1/plugins/name/{name}")

    # ======================================================================
    # AZURE DEPLOYMENTS
    # ======================================================================

    def delete_azure_deployment_policy(self, policyId: str) -> Any:
        """DELETE /v1/azure/deployment/policyid/{policyId}"""
        return self.c.delete(f"/v1/azure/deployment/policyid/{policyId}")

    def get_azure_module_policy(self, modulePolicyId: str) -> Any:
        """GET /v1/azure/edgedevice/modulepolicyid/{modulePolicyId}"""
        return self.c.get(f"/v1/azure/edgedevice/modulepolicyid/{modulePolicyId}")

    # ======================================================================
    # API USAGE TRACKING
    # ======================================================================

    def query_api_usage(self, **kw: Any) -> Any:
        """GET /v1/apiusage"""
        return self.c.get("/v1/apiusage", query=_qp(kw))
