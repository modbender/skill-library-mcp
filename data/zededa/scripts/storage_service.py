#!/usr/bin/env python3
"""
ZEDEDA Storage Service — 40 endpoints

Covers patch envelopes, deployment attestation policies, and deployment
policies (CRUD, status, runtime config).
"""

from __future__ import annotations
from typing import Any
from .client import ZededaClient
from .errors import StorageServiceError


def _qp(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None and k != "self"}


class StorageService:
    """Storage Service — patch envelopes, attestation, deployment policies."""

    def __init__(self, client: ZededaClient):
        self.c = client

    # ======================================================================
    # PATCH ENVELOPES
    # ======================================================================

    # GET /v1/patches
    def query_patch_envelopes(self, **kw: Any) -> Any:
        """Query patch envelopes."""
        return self.c.get("/v1/patches", query=_qp(kw))

    # POST /v1/patches
    def create_patch_envelope(self, body: dict) -> Any:
        """Create a patch envelope."""
        return self.c.post("/v1/patches", body=body)

    # GET /v1/patches/id/{id}
    def get_patch_envelope(self, id: str) -> Any:
        """Get patch envelope by ID."""
        return self.c.get(f"/v1/patches/id/{id}")

    # PUT /v1/patches/id/{id}
    def update_patch_envelope(self, id: str, body: dict) -> Any:
        """Update a patch envelope."""
        return self.c.put(f"/v1/patches/id/{id}", body=body)

    # DELETE /v1/patches/id/{id}
    def delete_patch_envelope(self, id: str) -> Any:
        """Delete a patch envelope."""
        return self.c.delete(f"/v1/patches/id/{id}")

    # GET /v1/patches/name/{name}
    def get_patch_envelope_by_name(self, name: str) -> Any:
        """Get patch envelope by name."""
        return self.c.get(f"/v1/patches/name/{name}")

    # -- Patch envelope status ----------------------------------------------

    # GET /v1/patches/status
    def query_patch_envelope_status(self, **kw: Any) -> Any:
        """Query patch envelope status list."""
        return self.c.get("/v1/patches/status", query=_qp(kw))

    # GET /v1/patches/status-config
    def query_patch_envelope_status_config(self, **kw: Any) -> Any:
        """Query patch envelope status with config."""
        return self.c.get("/v1/patches/status-config", query=_qp(kw))

    # GET /v1/patches/id/{id}/status
    def get_patch_envelope_status(self, id: str) -> Any:
        """Get patch envelope status by ID."""
        return self.c.get(f"/v1/patches/id/{id}/status")

    # GET /v1/patches/name/{name}/status
    def get_patch_envelope_status_by_name(self, name: str) -> Any:
        """Get patch envelope status by name."""
        return self.c.get(f"/v1/patches/name/{name}/status")

    # -- Patch envelope events & policies -----------------------------------

    # GET /v1/patches/id/{objid}/events
    def get_patch_envelope_events(self, objid: str, **kw: Any) -> Any:
        """Get events for a patch envelope by ID."""
        return self.c.get(f"/v1/patches/id/{objid}/events", query=_qp(kw))

    # GET /v1/patches/name/{objname}/events
    def get_patch_envelope_events_by_name(self, objname: str, **kw: Any) -> Any:
        """Get events for a patch envelope by name."""
        return self.c.get(f"/v1/patches/name/{objname}/events", query=_qp(kw))

    # GET /v1/patches/referenceupdate/id/{referenceUpdateId}
    def get_patch_reference_update(self, referenceUpdateId: str) -> Any:
        """Get patch reference update by ID."""
        return self.c.get(f"/v1/patches/referenceupdate/id/{referenceUpdateId}")

    # ======================================================================
    # DEPLOYMENT ATTESTATION POLICIES
    # ======================================================================

    # GET /v1/attestation/policies
    def query_attestation_policies(self, **kw: Any) -> Any:
        """Query deployment attestation policies."""
        return self.c.get("/v1/attestation/policies", query=_qp(kw))

    # POST /v1/attestation/policies
    def create_attestation_policy(self, body: dict) -> Any:
        """Create a deployment attestation policy."""
        return self.c.post("/v1/attestation/policies", body=body)

    # GET /v1/attestation/policies/id/{id}
    def get_attestation_policy(self, id: str) -> Any:
        """Get attestation policy by ID."""
        return self.c.get(f"/v1/attestation/policies/id/{id}")

    # PUT /v1/attestation/policies/id/{id}
    def update_attestation_policy(self, id: str, body: dict) -> Any:
        """Update an attestation policy."""
        return self.c.put(f"/v1/attestation/policies/id/{id}", body=body)

    # DELETE /v1/attestation/policies/id/{id}
    def delete_attestation_policy(self, id: str) -> Any:
        """Delete an attestation policy."""
        return self.c.delete(f"/v1/attestation/policies/id/{id}")

    # GET /v1/attestation/policies/name/{name}
    def get_attestation_policy_by_name(self, name: str) -> Any:
        """Get attestation policy by name."""
        return self.c.get(f"/v1/attestation/policies/name/{name}")

    # -- Attestation policy status ------------------------------------------

    # GET /v1/attestation/policies/status
    def query_attestation_policy_status(self, **kw: Any) -> Any:
        """Query attestation policy status list."""
        return self.c.get("/v1/attestation/policies/status", query=_qp(kw))

    # GET /v1/attestation/policies/status-config
    def query_attestation_policy_status_config(self, **kw: Any) -> Any:
        """Query attestation policy status with config."""
        return self.c.get("/v1/attestation/policies/status-config", query=_qp(kw))

    # GET /v1/attestation/policies/id/{id}/status
    def get_attestation_policy_status(self, id: str) -> Any:
        """Get attestation policy status by ID."""
        return self.c.get(f"/v1/attestation/policies/id/{id}/status")

    # GET /v1/attestation/policies/name/{name}/status
    def get_attestation_policy_status_by_name(self, name: str) -> Any:
        """Get attestation policy status by name."""
        return self.c.get(f"/v1/attestation/policies/name/{name}/status")

    # ======================================================================
    # DEPLOYMENT POLICIES
    # ======================================================================

    # GET /v1/deployment/policies
    def query_deployment_policies(self, **kw: Any) -> Any:
        """Query deployment policies."""
        return self.c.get("/v1/deployment/policies", query=_qp(kw))

    # POST /v1/deployment/policies
    def create_deployment_policy(self, body: dict) -> Any:
        """Create a deployment policy."""
        return self.c.post("/v1/deployment/policies", body=body)

    # GET /v1/deployment/policies/id/{id}
    def get_deployment_policy(self, id: str) -> Any:
        """Get deployment policy by ID."""
        return self.c.get(f"/v1/deployment/policies/id/{id}")

    # PUT /v1/deployment/policies/id/{id}
    def update_deployment_policy(self, id: str, body: dict) -> Any:
        """Update a deployment policy."""
        return self.c.put(f"/v1/deployment/policies/id/{id}", body=body)

    # DELETE /v1/deployment/policies/id/{id}
    def delete_deployment_policy(self, id: str) -> Any:
        """Delete a deployment policy."""
        return self.c.delete(f"/v1/deployment/policies/id/{id}")

    # GET /v1/deployment/policies/name/{name}
    def get_deployment_policy_by_name(self, name: str) -> Any:
        """Get deployment policy by name."""
        return self.c.get(f"/v1/deployment/policies/name/{name}")

    # -- Deployment policy status -------------------------------------------

    # GET /v1/deployment/policies/status
    def query_deployment_policy_status(self, **kw: Any) -> Any:
        """Query deployment policy status list."""
        return self.c.get("/v1/deployment/policies/status", query=_qp(kw))

    # GET /v1/deployment/policies/status-config
    def query_deployment_policy_status_config(self, **kw: Any) -> Any:
        """Query deployment policy status with config."""
        return self.c.get("/v1/deployment/policies/status-config", query=_qp(kw))

    # GET /v1/deployment/policies/id/{id}/status
    def get_deployment_policy_status(self, id: str) -> Any:
        """Get deployment policy status by ID."""
        return self.c.get(f"/v1/deployment/policies/id/{id}/status")

    # GET /v1/deployment/policies/name/{name}/status
    def get_deployment_policy_status_by_name(self, name: str) -> Any:
        """Get deployment policy status by name."""
        return self.c.get(f"/v1/deployment/policies/name/{name}/status")
