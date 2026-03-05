#!/usr/bin/env python3
"""
ZEDEDA Edge Node Cluster Service — 13 endpoints

Covers edge node cluster configuration CRUD (by id/name), cluster status,
and cluster events.
"""

from __future__ import annotations
from typing import Any
from .client import ZededaClient
from .errors import NodeClusterServiceError


def _qp(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None and k != "self"}


class NodeClusterService:
    """Edge Node Cluster Service — cluster configs, status, events."""

    def __init__(self, client: ZededaClient):
        self.c = client

    # ======================================================================
    # CLUSTER CONFIGURATION
    # ======================================================================

    def query_edge_node_clusters(self, **kw: Any) -> Any:
        """GET /v1/cluster/policies — Query edge node clusters."""
        return self.c.get("/v1/cluster/policies", query=_qp(kw))

    def create_edge_node_cluster(self, body: dict) -> Any:
        """POST /v1/cluster/policies — Create edge node cluster."""
        return self.c.post("/v1/cluster/policies", body=body)

    def get_edge_node_cluster(self, id: str) -> Any:
        """GET /v1/cluster/policies/id/{id}"""
        return self.c.get(f"/v1/cluster/policies/id/{id}")

    def update_edge_node_cluster(self, id: str, body: dict) -> Any:
        """PUT /v1/cluster/policies/id/{id}"""
        return self.c.put(f"/v1/cluster/policies/id/{id}", body=body)

    def delete_edge_node_cluster(self, id: str) -> Any:
        """DELETE /v1/cluster/policies/id/{id}"""
        return self.c.delete(f"/v1/cluster/policies/id/{id}")

    def get_edge_node_cluster_by_name(self, name: str) -> Any:
        """GET /v1/cluster/policies/name/{name}"""
        return self.c.get(f"/v1/cluster/policies/name/{name}")

    # ======================================================================
    # CLUSTER STATUS
    # ======================================================================

    def query_edge_node_cluster_status(self, **kw: Any) -> Any:
        """GET /v1/cluster/policies/status"""
        return self.c.get("/v1/cluster/policies/status", query=_qp(kw))

    def query_edge_node_cluster_status_config(self, **kw: Any) -> Any:
        """GET /v1/cluster/policies/status-config"""
        return self.c.get("/v1/cluster/policies/status-config", query=_qp(kw))

    def get_edge_node_cluster_status(self, id: str) -> Any:
        """GET /v1/cluster/policies/id/{id}/status"""
        return self.c.get(f"/v1/cluster/policies/id/{id}/status")

    def get_edge_node_cluster_status_by_name(self, name: str) -> Any:
        """GET /v1/cluster/policies/name/{name}/status"""
        return self.c.get(f"/v1/cluster/policies/name/{name}/status")

    # ======================================================================
    # CLUSTER EVENTS
    # ======================================================================

    def get_edge_node_cluster_events(self, objid: str, **kw: Any) -> Any:
        """GET /v1/cluster/policies/id/{objid}/events"""
        return self.c.get(f"/v1/cluster/policies/id/{objid}/events", query=_qp(kw))

    def get_edge_node_cluster_events_by_name(self, objname: str, **kw: Any) -> Any:
        """GET /v1/cluster/policies/name/{objname}/events"""
        return self.c.get(f"/v1/cluster/policies/name/{objname}/events", query=_qp(kw))

    def get_edge_node_cluster_tags(self) -> Any:
        """GET /v1/cluster/policies/tags"""
        return self.c.get("/v1/cluster/policies/tags")
