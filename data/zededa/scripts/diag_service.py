#!/usr/bin/env python3
"""
ZEDEDA Diagnostics Service — 23 endpoints

Covers device twin configuration (current, bootstrap, next, offline),
events timeline, resource metrics, top users, and cloud health checks.
"""

from __future__ import annotations
from typing import Any
from .client import ZededaClient
from .errors import DiagServiceError


def _qp(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None and k != "self"}


class DiagService:
    """Diagnostics Service — device twin config, events, metrics, health."""

    def __init__(self, client: ZededaClient):
        self.c = client

    # ======================================================================
    # DEVICE TWIN CONFIG — by ID
    # ======================================================================

    def get_device_twin_config(self, id: str) -> Any:
        """GET /v1/devices/id/{id}/config — Current twin config."""
        return self.c.get(f"/v1/devices/id/{id}/config")

    def regen_device_config(self, id: str) -> Any:
        """PUT /v1/devices/id/{id}/config — Regenerate config."""
        return self.c.put(f"/v1/devices/id/{id}/config")

    def get_device_twin_bootstrap_config(self, id: str) -> Any:
        """GET /v1/devices/id/{id}/config/bootstrap"""
        return self.c.get(f"/v1/devices/id/{id}/config/bootstrap")

    def get_device_twin_next_config(self, id: str) -> Any:
        """GET /v1/devices/id/{id}/config/next"""
        return self.c.get(f"/v1/devices/id/{id}/config/next")

    def get_device_twin_offline_next_config(self, id: str) -> Any:
        """GET /v1/devices/id/{id}/config/offline"""
        return self.c.get(f"/v1/devices/id/{id}/config/offline")

    # ======================================================================
    # DEVICE TWIN CONFIG — by Name
    # ======================================================================

    def get_device_twin_config_by_name(self, name: str) -> Any:
        """GET /v1/devices/name/{name}/config"""
        return self.c.get(f"/v1/devices/name/{name}/config")

    def get_device_twin_bootstrap_config_by_name(self, name: str) -> Any:
        """GET /v1/devices/name/{name}/config/bootstrap"""
        return self.c.get(f"/v1/devices/name/{name}/config/bootstrap")

    def get_device_twin_next_config_by_name(self, name: str) -> Any:
        """GET /v1/devices/name/{name}/config/next"""
        return self.c.get(f"/v1/devices/name/{name}/config/next")

    def get_device_twin_offline_config_by_name(self, name: str) -> Any:
        """GET /v1/devices/name/{name}/config/offline"""
        return self.c.get(f"/v1/devices/name/{name}/config/offline")

    # ======================================================================
    # CLOUD DIAGNOSTICS
    # ======================================================================

    def check_cloud_health(self, *, version: str | None = None) -> Any:
        """GET /v1/cloud/health/version/{version} — Cloud health check."""
        path = f"/v1/cloud/health/version/{version}" if version else "/v1/cloud/health"
        return self.c.get(path)

    def check_microservice_health(self, body: dict) -> Any:
        """POST /v1/hello — Check microservice health."""
        return self.c.post("/v1/hello", body=body)

    def get_cloud_status(self) -> Any:
        """GET /v1/cloud/status"""
        return self.c.get("/v1/cloud/status")

    def get_cloud_audit_log(self, **kw: Any) -> Any:
        """GET /v1/cloud/audit"""
        return self.c.get("/v1/cloud/audit", query=_qp(kw))

    # ======================================================================
    # EVENTS TIMELINE
    # ======================================================================

    def get_events_timeline(self, *, objname: str | None = None,
                            objid: str | None = None,
                            objtype: str | None = None,
                            **kw: Any) -> Any:
        """GET /v1/events — Query events timeline."""
        q = {"objname": objname, "objid": objid, "objtype": objtype, **kw}
        return self.c.get("/v1/events", query=_qp(q))

    def get_events_top_users(self) -> Any:
        """GET /v1/events/topUsers — Top API users."""
        return self.c.get("/v1/events/topUsers")

    # ======================================================================
    # RESOURCE METRICS
    # ======================================================================

    def get_resource_metrics_timeline(self, mType: str, *,
                                      objtype: str | None = None,
                                      objname: str | None = None,
                                      startTime: str | None = None,
                                      endTime: str | None = None,
                                      **kw: Any) -> Any:
        """GET /v1/events/timeSeries/{mType}"""
        q = {"objtype": objtype, "objname": objname,
             "startTime": startTime, "endTime": endTime, **kw}
        return self.c.get(f"/v1/events/timeSeries/{mType}", query=_qp(q))

    def get_resource_metrics_timeline_v2(self, mType: str, *,
                                          objtype: str | None = None,
                                          objname: str | None = None,
                                          startTime: str | None = None,
                                          endTime: str | None = None,
                                          **kw: Any) -> Any:
        """GET /v1/timeSeries/{mType}"""
        q = {"objtype": objtype, "objname": objname,
             "startTime": startTime, "endTime": endTime, **kw}
        return self.c.get(f"/v1/timeSeries/{mType}", query=_qp(q))

    # ======================================================================
    # DEVICE STATUS FIELDS (diag-specific)
    # ======================================================================

    def get_device_status_summary(self, id: str) -> Any:
        """GET /v1/devices/id/{id}/status/summary — Device status summary."""
        return self.c.get(f"/v1/devices/id/{id}/status/summary")

    def get_device_app_instances_summary(self, id: str) -> Any:
        """GET /v1/devices/id/{id}/apps/summary — App instances summary."""
        return self.c.get(f"/v1/devices/id/{id}/apps/summary")

    def get_device_network_details(self, id: str) -> Any:
        """GET /v1/devices/id/{id}/network — Network details for a device."""
        return self.c.get(f"/v1/devices/id/{id}/network")

    def get_device_volume_details(self, id: str) -> Any:
        """GET /v1/devices/id/{id}/volumes — Volume details for a device."""
        return self.c.get(f"/v1/devices/id/{id}/volumes")
