#!/usr/bin/env python3
"""
ZEDEDA Network Service — 18 endpoints

Covers network configuration CRUD (by id/name), network status queries,
events, and resource metrics.
"""

from __future__ import annotations
from typing import Any
from .client import ZededaClient
from .errors import NetworkServiceError


def _qp(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None and k != "self"}


class NetworkService:
    """Network Service — network configs, status, events, metrics."""

    def __init__(self, client: ZededaClient):
        self.c = client

    # ======================================================================
    # NETWORK CONFIGURATION
    # ======================================================================

    def query_networks(self, **kw: Any) -> Any:
        """GET /v1/networks"""
        return self.c.get("/v1/networks", query=_qp(kw))

    def create_network(self, body: dict) -> Any:
        """POST /v1/networks"""
        return self.c.post("/v1/networks", body=body)

    def get_network(self, id: str) -> Any:
        """GET /v1/networks/id/{id}"""
        return self.c.get(f"/v1/networks/id/{id}")

    def update_network(self, id: str, body: dict) -> Any:
        """PUT /v1/networks/id/{id}"""
        return self.c.put(f"/v1/networks/id/{id}", body=body)

    def delete_network(self, id: str) -> Any:
        """DELETE /v1/networks/id/{id}"""
        return self.c.delete(f"/v1/networks/id/{id}")

    def get_network_by_name(self, name: str) -> Any:
        """GET /v1/networks/name/{name}"""
        return self.c.get(f"/v1/networks/name/{name}")

    # ======================================================================
    # NETWORK STATUS
    # ======================================================================

    def query_network_status(self, **kw: Any) -> Any:
        """GET /v1/networks/status"""
        return self.c.get("/v1/networks/status", query=_qp(kw))

    def query_network_status_config(self, **kw: Any) -> Any:
        """GET /v1/networks/status-config"""
        return self.c.get("/v1/networks/status-config", query=_qp(kw))

    def get_network_status(self, id: str) -> Any:
        """GET /v1/networks/id/{id}/status"""
        return self.c.get(f"/v1/networks/id/{id}/status")

    def get_network_status_by_name(self, name: str) -> Any:
        """GET /v1/networks/name/{name}/status"""
        return self.c.get(f"/v1/networks/name/{name}/status")

    # ======================================================================
    # NETWORK EVENTS
    # ======================================================================

    def get_network_events(self, objid: str, **kw: Any) -> Any:
        """GET /v1/networks/id/{objid}/events"""
        return self.c.get(f"/v1/networks/id/{objid}/events", query=_qp(kw))

    def get_network_events_by_name(self, objname: str, **kw: Any) -> Any:
        """GET /v1/networks/name/{objname}/events"""
        return self.c.get(f"/v1/networks/name/{objname}/events", query=_qp(kw))

    # ======================================================================
    # NETWORK RESOURCE METRICS
    # ======================================================================

    def get_network_resource_metrics_by_id(self, objid: str, mType: str,
                                            **kw: Any) -> Any:
        """GET /v1/networks/id/{objid}/timeSeries/{mType}"""
        return self.c.get(f"/v1/networks/id/{objid}/timeSeries/{mType}", query=_qp(kw))

    def get_network_resource_metrics_by_name(self, objname: str, mType: str,
                                              **kw: Any) -> Any:
        """GET /v1/networks/name/{objname}/timeSeries/{mType}"""
        return self.c.get(f"/v1/networks/name/{objname}/timeSeries/{mType}", query=_qp(kw))

    # ======================================================================
    # NETWORK TAGS & PROJECTS
    # ======================================================================

    def get_network_tags(self) -> Any:
        """GET /v1/networks/tags"""
        return self.c.get("/v1/networks/tags")

    def query_network_projects(self, **kw: Any) -> Any:
        """GET /v1/networks/projects"""
        return self.c.get("/v1/networks/projects", query=_qp(kw))
