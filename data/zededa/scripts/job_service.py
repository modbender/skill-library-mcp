#!/usr/bin/env python3
"""
ZEDEDA Job Service — 17 endpoints

Covers bulk job operations: create/query/update/delete jobs, bulk import
apps & hardware models, bulk update edge node base OS, deployment tags,
and project targets.
"""

from __future__ import annotations
from typing import Any
from .client import ZededaClient
from .errors import JobServiceError


def _qp(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None and k != "self"}


class JobService:
    """Job / Bulk Operations Service."""

    def __init__(self, client: ZededaClient):
        self.c = client

    # ======================================================================
    # JOB CRUD
    # ======================================================================

    def query_jobs(self, **kw: Any) -> Any:
        """GET /v1/jobs — Query jobs."""
        return self.c.get("/v1/jobs", query=_qp(kw))

    def create_job(self, body: dict) -> Any:
        """POST /v1/jobs — Create a job."""
        return self.c.post("/v1/jobs", body=body)

    def get_job_by_id(self, id: str) -> Any:
        """GET /v1/jobs/id/{id} — Get job (simple)."""
        return self.c.get(f"/v1/jobs/id/{id}")

    def update_job(self, id: str, body: dict) -> Any:
        """PUT /v1/jobs/id/{id} — Update a job."""
        return self.c.put(f"/v1/jobs/id/{id}", body=body)

    def get_job(self, id: str, objectType: str) -> Any:
        """GET /v1/jobs/id/{id}/objectType/{objectType}"""
        return self.c.get(f"/v1/jobs/id/{id}/objectType/{objectType}")

    def delete_job(self, id: str, objectType: str) -> Any:
        """DELETE /v1/jobs/id/{id}/objectType/{objectType}"""
        return self.c.delete(f"/v1/jobs/id/{id}/objectType/{objectType}")

    def get_job_by_name(self, name: str, objectType: str) -> Any:
        """GET /v1/jobs/name/{name}/objectType/{objectType}"""
        return self.c.get(f"/v1/jobs/name/{name}/objectType/{objectType}")

    # ======================================================================
    # BULK APPLICATION OPERATIONS
    # ======================================================================

    def bulk_import_edge_applications(self, body: dict) -> Any:
        """PUT /v1/jobs/apps/bundles/import — Bulk import edge applications."""
        return self.c.put("/v1/jobs/apps/bundles/import", body=body)

    def bulk_create_edge_application_instances(self, body: dict) -> Any:
        """PUT /v1/jobs/apps/instances/create — Bulk create app instances."""
        return self.c.put("/v1/jobs/apps/instances/create", body=body)

    def bulk_refresh_edge_application_instances(self, body: dict) -> Any:
        """PUT /v1/jobs/apps/instances/refresh — Bulk refresh app instances."""
        return self.c.put("/v1/jobs/apps/instances/refresh", body=body)

    def bulk_refresh_and_purge_edge_application_instances(self, body: dict) -> Any:
        """PUT /v1/jobs/apps/instances/refresh/purge — Bulk refresh+purge."""
        return self.c.put("/v1/jobs/apps/instances/refresh/purge", body=body)

    # ======================================================================
    # BULK DEVICE OPERATIONS
    # ======================================================================

    def bulk_update_edge_node_base_os(self, body: dict) -> Any:
        """PUT /v1/jobs/devices/baseos/upgrade — Bulk base-OS upgrade."""
        return self.c.put("/v1/jobs/devices/baseos/upgrade", body=body)

    def bulk_update_edge_node_base_os_retry(self, body: dict) -> Any:
        """PUT /v1/jobs/devices/baseos/upgrade/retry — Retry bulk upgrade."""
        return self.c.put("/v1/jobs/devices/baseos/upgrade/retry", body=body)

    def bulk_update_edge_node_deployment_tag(self, body: dict) -> Any:
        """PUT /v1/jobs/devices/deployment/tags — Bulk update deployment tags."""
        return self.c.put("/v1/jobs/devices/deployment/tags", body=body)

    def bulk_update_edge_node_project(self, body: dict) -> Any:
        """PUT /v1/jobs/devices/project/target — Bulk update project target."""
        return self.c.put("/v1/jobs/devices/project/target", body=body)

    def bulk_update_edge_node_tags(self, body: dict) -> Any:
        """PUT /v1/jobs/devices/tags — Bulk update device tags."""
        return self.c.put("/v1/jobs/devices/tags", body=body)

    # ======================================================================
    # BULK HARDWARE MODEL OPERATIONS
    # ======================================================================

    def bulk_import_hardware_models(self, body: dict) -> Any:
        """PUT /v1/jobs/models/import — Bulk import hardware models."""
        return self.c.put("/v1/jobs/models/import", body=body)
