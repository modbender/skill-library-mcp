#!/usr/bin/env python3
"""
ZEDEDA App Profile Service — 21 endpoints

Covers application policy CRUD (by id/name), status queries,
events, and resource metrics.
"""

from __future__ import annotations
from typing import Any
from .client import ZededaClient
from .errors import AppProfileServiceError


def _qp(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None and k != "self"}


class AppProfileService:
    """App Profile / Policy Service."""

    def __init__(self, client: ZededaClient):
        self.c = client

    # ======================================================================
    # APPLICATION POLICY CONFIGURATION
    # ======================================================================

    def query_app_policies(self, **kw: Any) -> Any:
        """GET /v1/apps/policies"""
        return self.c.get("/v1/apps/policies", query=_qp(kw))

    def create_app_policy(self, body: dict) -> Any:
        """POST /v1/apps/policies"""
        return self.c.post("/v1/apps/policies", body=body)

    def get_app_policy(self, id: str) -> Any:
        """GET /v1/apps/policies/id/{id}"""
        return self.c.get(f"/v1/apps/policies/id/{id}")

    def update_app_policy(self, id: str, body: dict) -> Any:
        """PUT /v1/apps/policies/id/{id}"""
        return self.c.put(f"/v1/apps/policies/id/{id}", body=body)

    def delete_app_policy(self, id: str) -> Any:
        """DELETE /v1/apps/policies/id/{id}"""
        return self.c.delete(f"/v1/apps/policies/id/{id}")

    def get_app_policy_by_name(self, name: str) -> Any:
        """GET /v1/apps/policies/name/{name}"""
        return self.c.get(f"/v1/apps/policies/name/{name}")

    # ======================================================================
    # APPLICATION POLICY STATUS
    # ======================================================================

    def query_app_policy_status(self, **kw: Any) -> Any:
        """GET /v1/apps/policies/status"""
        return self.c.get("/v1/apps/policies/status", query=_qp(kw))

    def query_app_policy_status_config(self, **kw: Any) -> Any:
        """GET /v1/apps/policies/status-config"""
        return self.c.get("/v1/apps/policies/status-config", query=_qp(kw))

    def get_app_policy_status(self, id: str) -> Any:
        """GET /v1/apps/policies/id/{id}/status"""
        return self.c.get(f"/v1/apps/policies/id/{id}/status")

    def get_app_policy_status_by_name(self, name: str) -> Any:
        """GET /v1/apps/policies/name/{name}/status"""
        return self.c.get(f"/v1/apps/policies/name/{name}/status")

    # ======================================================================
    # APPLICATION POLICY EVENTS
    # ======================================================================

    def get_app_policy_events(self, objid: str, **kw: Any) -> Any:
        """GET /v1/apps/policies/id/{objid}/events"""
        return self.c.get(f"/v1/apps/policies/id/{objid}/events", query=_qp(kw))

    def get_app_policy_events_by_name(self, objname: str, **kw: Any) -> Any:
        """GET /v1/apps/policies/name/{objname}/events"""
        return self.c.get(f"/v1/apps/policies/name/{objname}/events", query=_qp(kw))

    # ======================================================================
    # APPLICATION POLICY RESOURCE METRICS
    # ======================================================================

    def get_app_policy_resource_metrics_by_id(self, objid: str, mType: str,
                                               **kw: Any) -> Any:
        """GET /v1/apps/policies/id/{objid}/timeSeries/{mType}"""
        return self.c.get(f"/v1/apps/policies/id/{objid}/timeSeries/{mType}", query=_qp(kw))

    def get_app_policy_resource_metrics_by_name(self, objname: str, mType: str,
                                                 **kw: Any) -> Any:
        """GET /v1/apps/policies/name/{objname}/timeSeries/{mType}"""
        return self.c.get(f"/v1/apps/policies/name/{objname}/timeSeries/{mType}", query=_qp(kw))

    # ======================================================================
    # APPLICATION POLICY GLOBAL
    # ======================================================================

    def query_global_app_policies(self, **kw: Any) -> Any:
        """GET /v1/apps/policies/global"""
        return self.c.get("/v1/apps/policies/global", query=_qp(kw))

    def get_global_app_policy(self, id: str) -> Any:
        """GET /v1/apps/policies/global/id/{id}"""
        return self.c.get(f"/v1/apps/policies/global/id/{id}")

    def get_global_app_policy_by_name(self, name: str) -> Any:
        """GET /v1/apps/policies/global/name/{name}"""
        return self.c.get(f"/v1/apps/policies/global/name/{name}")

    # ======================================================================
    # APP POLICY IMPORT
    # ======================================================================

    def import_app_policy(self, id: str) -> Any:
        """PUT /v1/apps/policies/id/{id}/import"""
        return self.c.put(f"/v1/apps/policies/id/{id}/import")

    def get_app_policy_tags(self) -> Any:
        """GET /v1/apps/policies/tags"""
        return self.c.get("/v1/apps/policies/tags")
