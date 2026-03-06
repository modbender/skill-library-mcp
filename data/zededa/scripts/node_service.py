#!/usr/bin/env python3
"""
ZEDEDA Edge Node Service — 90 endpoints

Covers edge node CRUD, status, events, metrics, attestation, base OS
management, hardware models (system models), projects / resource groups
(v1 + v2 deployments), PCR templates, and device interface tags.
"""

from __future__ import annotations
from typing import Any
from .client import ZededaClient
from .errors import NodeServiceError

# ── Standard pagination / filter query helpers ────────────────────────────

_STD_LIST = (
    "summary", "namePattern", "next.pageToken", "next.orderBy",
    "next.pageNum", "next.pageSize", "next.totalPages",
)

def _qp(local: dict[str, Any], *extra_keys: str) -> dict[str, Any]:
    """Build a query-param dict, dropping None values."""
    return {k: v for k, v in local.items() if v is not None and k != "self"}


class NodeService:
    """Edge Node Service – devices, hardware models, projects, brands."""

    def __init__(self, client: ZededaClient):
        self.c = client

    # ======================================================================
    # BRANDS
    # ======================================================================

    # GET /v1/brands
    def query_brands(self, **kw: Any) -> Any:
        """Query all brands."""
        return self.c.get("/v1/brands", query=_qp(kw))

    # POST /v1/brands
    def create_brand(self, body: dict) -> Any:
        """Create a brand."""
        return self.c.post("/v1/brands", body=body)

    # GET /v1/brands/id/{id}
    def get_brand(self, id: str) -> Any:
        """Get brand by ID."""
        return self.c.get(f"/v1/brands/id/{id}")

    # PUT /v1/brands/id/{id}
    def update_brand(self, id: str, body: dict) -> Any:
        """Update a brand."""
        return self.c.put(f"/v1/brands/id/{id}", body=body)

    # DELETE /v1/brands/id/{id}
    def delete_brand(self, id: str) -> Any:
        """Delete a brand."""
        return self.c.delete(f"/v1/brands/id/{id}")

    # GET /v1/brands/name/{name}
    def get_brand_by_name(self, name: str) -> Any:
        """Get brand by name."""
        return self.c.get(f"/v1/brands/name/{name}")

    # GET /v1/brands/global
    def query_global_brands(self, **kw: Any) -> Any:
        """Query global brands."""
        return self.c.get("/v1/brands/global", query=_qp(kw))

    # GET /v1/brands/global/id/{id}
    def get_global_brand(self, id: str) -> Any:
        """Get a global brand by ID."""
        return self.c.get(f"/v1/brands/global/id/{id}")

    # GET /v1/brands/global/name/{name}
    def get_global_brand_by_name(self, name: str) -> Any:
        """Get a global brand by name."""
        return self.c.get(f"/v1/brands/global/name/{name}")

    # ======================================================================
    # EDGE NODE CONFIGURATION
    # ======================================================================

    # GET /v1/devices
    def query_edge_nodes(self, *, summary: bool | None = None,
                         namePattern: str | None = None,
                         next_pageToken: str | None = None,
                         next_orderBy: str | None = None,
                         next_pageNum: int | None = None,
                         next_pageSize: int | None = None,
                         next_totalPages: int | None = None,
                         **kw: Any) -> Any:
        """Query all edge node configurations."""
        q = {"summary": summary, "namePattern": namePattern,
             "next.pageToken": next_pageToken, "next.orderBy": next_orderBy,
             "next.pageNum": next_pageNum, "next.pageSize": next_pageSize,
             "next.totalPages": next_totalPages}
        return self.c.get("/v1/devices", query=_qp(q))

    # POST /v1/devices
    def create_edge_node(self, body: dict) -> Any:
        """Create a new edge node configuration."""
        return self.c.post("/v1/devices", body=body)

    # GET /v1/devices/id/{id}
    def get_edge_node(self, id: str) -> Any:
        """Get edge node configuration by ID."""
        return self.c.get(f"/v1/devices/id/{id}")

    # PUT /v1/devices/id/{id}
    def update_edge_node(self, id: str, body: dict) -> Any:
        """Update an edge node configuration."""
        return self.c.put(f"/v1/devices/id/{id}", body=body)

    # DELETE /v1/devices/id/{id}
    def delete_edge_node(self, id: str) -> Any:
        """Delete an edge node."""
        return self.c.delete(f"/v1/devices/id/{id}")

    # PUT /v1/devices/id/{id}/attest
    def attest_edge_node(self, id: str) -> Any:
        """Attest an edge node."""
        return self.c.put(f"/v1/devices/id/{id}/attest")

    # PUT /v1/devices/id/{id}/activate
    def activate_edge_node(self, id: str) -> Any:
        """Activate an edge node."""
        return self.c.put(f"/v1/devices/id/{id}/activate")

    # PUT /v1/devices/id/{id}/apply
    def apply_edge_node_config(self, id: str) -> Any:
        """Apply configuration to an edge node."""
        return self.c.put(f"/v1/devices/id/{id}/apply")

    # GET /v1/devices/id/{id}/attestation
    def get_edge_node_attestation(self, id: str) -> Any:
        """Get attestation status for an edge node."""
        return self.c.get(f"/v1/devices/id/{id}/attestation")

    # PUT /v1/devices/id/{id}/baseos/upgrade/retry
    def update_edge_node_base_os_retry(self, id: str, body: dict) -> Any:
        """Retry base-OS update on an edge node."""
        return self.c.put(f"/v1/devices/id/{id}/baseos/upgrade/retry", body=body)

    # PUT /v1/devices/id/{id}/deactivate
    def deactivate_edge_node(self, id: str) -> Any:
        """Deactivate / offboard an edge node."""
        return self.c.put(f"/v1/devices/id/{id}/deactivate")

    # PUT /v1/devices/id/{id}/debug/enable
    def enable_edge_node_debug(self, id: str) -> Any:
        """Enable debug mode on an edge node."""
        return self.c.put(f"/v1/devices/id/{id}/debug/enable")

    # PUT /v1/devices/id/{id}/debug/disable
    def disable_edge_node_debug(self, id: str) -> Any:
        """Disable debug mode on an edge node."""
        return self.c.put(f"/v1/devices/id/{id}/debug/disable")

    # PUT /v1/devices/id/{id}/edgeview/enable
    def enable_edge_node_edgeview(self, id: str, body: dict | None = None) -> Any:
        """Enable edge-view on an edge node."""
        return self.c.put(f"/v1/devices/id/{id}/edgeview/enable", body=body)

    # PUT /v1/devices/id/{id}/edgeview/disable
    def disable_edge_node_edgeview(self, id: str) -> Any:
        """Disable edge-view on an edge node."""
        return self.c.put(f"/v1/devices/id/{id}/edgeview/disable")

    # GET /v1/devices/id/{id}/edgeview/clientscript
    def get_edge_node_edgeview_clientscript(self, id: str) -> Any:
        """Get edge-view client script for a node."""
        return self.c.get(f"/v1/devices/id/{id}/edgeview/clientscript")

    # PUT /v1/devices/id/{id}/offboard
    def offboard_edge_node(self, id: str) -> Any:
        """Offboard an edge node."""
        return self.c.put(f"/v1/devices/id/{id}/offboard")

    # GET /v1/devices/id/{id}/onboarding
    def get_edge_node_onboarding(self, id: str) -> Any:
        """Get onboarding status for an edge node."""
        return self.c.get(f"/v1/devices/id/{id}/onboarding")

    # PUT /v1/devices/id/{id}/preparepoweroff
    def prepare_edge_node_poweroff(self, id: str) -> Any:
        """Prepare an edge node for power off."""
        return self.c.put(f"/v1/devices/id/{id}/preparepoweroff")

    # PUT /v1/devices/id/{id}/publish
    def publish_edge_node(self, id: str, body: dict) -> Any:
        """Publish an edge node base OS (UpdateEdgeNodeBaseOS4)."""
        return self.c.put(f"/v1/devices/id/{id}/publish", body=body)

    # PUT /v1/devices/id/{id}/reboot
    def reboot_edge_node(self, id: str) -> Any:
        """Reboot an edge node."""
        return self.c.put(f"/v1/devices/id/{id}/reboot")

    # GET /v1/devices/id/{id}/suimage
    def get_edge_node_single_use_eve_image(self, id: str) -> Any:
        """Get single-use EVE image details for an edge node."""
        return self.c.get(f"/v1/devices/id/{id}/suimage")

    # POST /v1/devices/id/{id}/suimage
    def create_edge_node_single_use_eve_image(self, id: str, body: dict) -> Any:
        """Create a single-use EVE image for an edge node."""
        return self.c.post(f"/v1/devices/id/{id}/suimage", body=body)

    # GET /v1/devices/id/{id}/suimage/link
    def get_edge_node_single_use_eve_image_download_link(self, id: str) -> Any:
        """Get download link for single-use EVE image."""
        return self.c.get(f"/v1/devices/id/{id}/suimage/link")

    # PUT /v1/devices/id/{id}/unpublish
    def unpublish_edge_node(self, id: str) -> Any:
        """Unpublish edge node base OS (UpdateEdgeNodeBaseOS3)."""
        return self.c.put(f"/v1/devices/id/{id}/unpublish")

    # GET /v1/devices/name/{name}
    def get_edge_node_by_name(self, name: str) -> Any:
        """Get edge node configuration by name."""
        return self.c.get(f"/v1/devices/name/{name}")

    # GET /v1/devices/serial/{serialno}
    def get_edge_node_by_serial(self, serialno: str) -> Any:
        """Get edge node configuration by serial number."""
        return self.c.get(f"/v1/devices/serial/{serialno}")

    # GET /v1/devices/interfaces/tags
    def get_device_interface_tags(self) -> Any:
        """Get all device interface tags."""
        return self.c.get("/v1/devices/interfaces/tags")

    # GET /v1/devices/tags
    def get_device_tags(self) -> Any:
        """Get all device tags."""
        return self.c.get("/v1/devices/tags")

    # ======================================================================
    # EDGE NODE STATUS
    # ======================================================================

    # GET /v1/devices/status
    def query_edge_node_status(self, *, summary: bool | None = None,
                                namePattern: str | None = None,
                                projectName: str | None = None,
                                projectNamePattern: str | None = None,
                                fields: str | None = None,
                                next_pageToken: str | None = None,
                                next_orderBy: str | None = None,
                                next_pageNum: int | None = None,
                                next_pageSize: int | None = None,
                                next_totalPages: int | None = None,
                                runState: str | None = None,
                                clusterName: str | None = None,
                                load: str | None = None,
                                **kw: Any) -> Any:
        """Query edge node status list."""
        q = {"summary": summary, "namePattern": namePattern,
             "projectName": projectName, "projectNamePattern": projectNamePattern,
             "fields": fields, "next.pageToken": next_pageToken,
             "next.orderBy": next_orderBy, "next.pageNum": next_pageNum,
             "next.pageSize": next_pageSize, "next.totalPages": next_totalPages,
             "runState": runState, "clusterName": clusterName, "load": load}
        return self.c.get("/v1/devices/status", query=_qp(q))

    # GET /v1/devices/status-config
    def get_device_status_config(self, **kw: Any) -> Any:
        """Query edge node status with config."""
        return self.c.get("/v1/devices/status-config", query=_qp(kw))

    # GET /v1/devices/status/locations
    def get_device_status_location(self, **kw: Any) -> Any:
        """Get device status locations."""
        return self.c.get("/v1/devices/status/locations", query=_qp(kw))

    # GET /v1/devices/id/{id}/status
    def get_edge_node_status(self, id: str) -> Any:
        """Get edge node status by ID."""
        return self.c.get(f"/v1/devices/id/{id}/status")

    # GET /v1/devices/id/{id}/status/edgeview
    def get_edge_node_edgeview_status(self, id: str) -> Any:
        """Get edge-view status for a node by ID."""
        return self.c.get(f"/v1/devices/id/{id}/status/edgeview")

    # GET /v1/devices/id/{id}/status/info
    def get_edge_node_info(self, id: str) -> Any:
        """Get edge node hardware/software info by ID."""
        return self.c.get(f"/v1/devices/id/{id}/status/info")

    # GET /v1/devices/id/{id}/status/metrics/raw
    def get_edge_node_raw_status(self, id: str) -> Any:
        """Get raw metrics status for a node by ID."""
        return self.c.get(f"/v1/devices/id/{id}/status/metrics/raw")

    # GET /v1/devices/name/{name}/status
    def get_edge_node_status_by_name(self, name: str) -> Any:
        """Get edge node status by name."""
        return self.c.get(f"/v1/devices/name/{name}/status")

    # GET /v1/devices/name/{name}/status/edgeview
    def get_edge_node_edgeview_status_by_name(self, name: str) -> Any:
        """Get edge-view status for a node by name."""
        return self.c.get(f"/v1/devices/name/{name}/status/edgeview")

    # GET /v1/devices/name/{name}/status/info
    def get_edge_node_info_by_name(self, name: str) -> Any:
        """Get edge node info by name."""
        return self.c.get(f"/v1/devices/name/{name}/status/info")

    # GET /v1/devices/name/{name}/status/metrics/raw
    def get_edge_node_raw_status_by_name(self, name: str) -> Any:
        """Get raw metrics for a node by name."""
        return self.c.get(f"/v1/devices/name/{name}/status/metrics/raw")

    # ======================================================================
    # EDGE NODE EVENTS & METRICS
    # ======================================================================

    # GET /v1/devices/id/{objid}/events
    def get_edge_node_events(self, objid: str, **kw: Any) -> Any:
        """Get events for an edge node by ID."""
        return self.c.get(f"/v1/devices/id/{objid}/events", query=_qp(kw))

    # GET /v1/devices/name/{objname}/events
    def get_edge_node_events_by_name(self, objname: str, **kw: Any) -> Any:
        """Get events for an edge node by name."""
        return self.c.get(f"/v1/devices/name/{objname}/events", query=_qp(kw))

    # GET /v1/devices/id/{objid}/timeSeries/{mType}
    def get_edge_node_resource_metrics_by_id(self, objid: str, mType: str,
                                              **kw: Any) -> Any:
        """Get resource metrics time-series for a node by ID."""
        return self.c.get(f"/v1/devices/id/{objid}/timeSeries/{mType}", query=_qp(kw))

    # GET /v1/devices/name/{objname}/timeSeries/{mType}
    def get_edge_node_resource_metrics_by_name(self, objname: str, mType: str,
                                                **kw: Any) -> Any:
        """Get resource metrics time-series for a node by name."""
        return self.c.get(f"/v1/devices/name/{objname}/timeSeries/{mType}", query=_qp(kw))

    # ======================================================================
    # HARDWARE MODELS (SYS MODELS)
    # ======================================================================

    # GET /v1/sysmodels
    def query_hardware_models(self, **kw: Any) -> Any:
        """Query all hardware models."""
        return self.c.get("/v1/sysmodels", query=_qp(kw))

    # POST /v1/sysmodels
    def create_hardware_model(self, body: dict) -> Any:
        """Create a hardware model."""
        return self.c.post("/v1/sysmodels", body=body)

    # GET /v1/sysmodels/id/{id}
    def get_hardware_model(self, id: str) -> Any:
        """Get hardware model by ID."""
        return self.c.get(f"/v1/sysmodels/id/{id}")

    # PUT /v1/sysmodels/id/{id}
    def update_hardware_model(self, id: str, body: dict) -> Any:
        """Update a hardware model."""
        return self.c.put(f"/v1/sysmodels/id/{id}", body=body)

    # DELETE /v1/sysmodels/id/{id}
    def delete_hardware_model(self, id: str) -> Any:
        """Delete a hardware model."""
        return self.c.delete(f"/v1/sysmodels/id/{id}")

    # PUT /v1/sysmodels/id/{id}/import
    def import_hardware_model(self, id: str) -> Any:
        """Import a global hardware model into the enterprise."""
        return self.c.put(f"/v1/sysmodels/id/{id}/import")

    # GET /v1/sysmodels/name/{name}
    def get_hardware_model_by_name(self, name: str) -> Any:
        """Get hardware model by name."""
        return self.c.get(f"/v1/sysmodels/name/{name}")

    # GET /v1/sysmodels/global
    def query_global_hardware_models(self, **kw: Any) -> Any:
        """Query global (shared) hardware models."""
        return self.c.get("/v1/sysmodels/global", query=_qp(kw))

    # GET /v1/sysmodels/global/id/{id}
    def get_global_hardware_model(self, id: str) -> Any:
        """Get a global hardware model by ID."""
        return self.c.get(f"/v1/sysmodels/global/id/{id}")

    # GET /v1/sysmodels/global/name/{name}
    def get_global_hardware_model_by_name(self, name: str) -> Any:
        """Get a global hardware model by name."""
        return self.c.get(f"/v1/sysmodels/global/name/{name}")

    # ======================================================================
    # PCR TEMPLATES
    # ======================================================================

    # GET /v1/sysmodels/id/{id}/pcrtemplates
    def get_pcr_templates(self, id: str) -> Any:
        """Get PCR templates for a hardware model."""
        return self.c.get(f"/v1/sysmodels/id/{id}/pcrtemplates")

    # POST /v1/sysmodels/id/{id}/pcrtemplates
    def create_pcr_templates(self, id: str, body: dict) -> Any:
        """Create PCR templates for a hardware model."""
        return self.c.post(f"/v1/sysmodels/id/{id}/pcrtemplates", body=body)

    # GET /v1/sysmodels/id/{modelId}/pcrtemplates/name/{name}
    def get_pcr_template_by_name(self, modelId: str, name: str) -> Any:
        """Get a specific PCR template by model ID and name."""
        return self.c.get(f"/v1/sysmodels/id/{modelId}/pcrtemplates/name/{name}")

    # PUT /v1/pcrtemplate/id/{id}
    def update_pcr_template(self, id: str, body: dict) -> Any:
        """Update a PCR template."""
        return self.c.put(f"/v1/pcrtemplate/id/{id}", body=body)

    # GET /v1/pcrtemplates/id/{id}
    def get_pcr_template_by_id(self, id: str) -> Any:
        """Get a PCR template by its own ID."""
        return self.c.get(f"/v1/pcrtemplates/id/{id}")

    # DELETE /v1/pcrtemplates/id/{id}
    def delete_pcr_template(self, id: str) -> Any:
        """Delete a PCR template (HardwareModel_DeleteEdgeNode)."""
        return self.c.delete(f"/v1/pcrtemplates/id/{id}")

    # ======================================================================
    # PROJECTS / RESOURCE GROUPS
    # ======================================================================

    # GET /v1/projects
    def query_projects(self, **kw: Any) -> Any:
        """Query all projects / resource groups."""
        return self.c.get("/v1/projects", query=_qp(kw))

    # POST /v1/projects
    def create_project(self, body: dict) -> Any:
        """Create a new project / resource group."""
        return self.c.post("/v1/projects", body=body)

    # GET /v1/projects/id/{id}
    def get_project(self, id: str) -> Any:
        """Get project by ID."""
        return self.c.get(f"/v1/projects/id/{id}")

    # PUT /v1/projects/id/{id}
    def update_project(self, id: str, body: dict) -> Any:
        """Update a project."""
        return self.c.put(f"/v1/projects/id/{id}", body=body)

    # DELETE /v1/projects/id/{id}
    def delete_project(self, id: str) -> Any:
        """Delete a project."""
        return self.c.delete(f"/v1/projects/id/{id}")

    # GET /v1/projects/name/{name}
    def get_project_by_name(self, name: str) -> Any:
        """Get project by name."""
        return self.c.get(f"/v1/projects/name/{name}")

    # GET /v1/projects/tags
    def get_project_tags(self) -> Any:
        """Get all project tags."""
        return self.c.get("/v1/projects/tags")

    # -- Project status -----------------------------------------------------

    # GET /v1/projects/status
    def query_project_status(self, **kw: Any) -> Any:
        """Query project status list."""
        return self.c.get("/v1/projects/status", query=_qp(kw))

    # GET /v1/projects/status-config
    def query_project_status_config(self, **kw: Any) -> Any:
        """Query project status with config."""
        return self.c.get("/v1/projects/status-config", query=_qp(kw))

    # GET /v1/projects/id/{id}/status
    def get_project_status_by_id(self, id: str) -> Any:
        """Get project status by ID."""
        return self.c.get(f"/v1/projects/id/{id}/status")

    # GET /v1/projects/name/{name}/status
    def get_project_status_by_name(self, name: str) -> Any:
        """Get project status by name."""
        return self.c.get(f"/v1/projects/name/{name}/status")

    # -- Project events & metrics -------------------------------------------

    # GET /v1/projects/id/{objid}/events
    def get_project_events(self, objid: str, **kw: Any) -> Any:
        """Get events for a project by ID."""
        return self.c.get(f"/v1/projects/id/{objid}/events", query=_qp(kw))

    # GET /v1/projects/name/{objname}/events
    def get_project_events_by_name(self, objname: str, **kw: Any) -> Any:
        """Get events for a project by name."""
        return self.c.get(f"/v1/projects/name/{objname}/events", query=_qp(kw))

    # GET /v1/projects/id/{objid}/timeSeries/{mType}
    def get_project_resource_metrics_by_id(self, objid: str, mType: str,
                                            **kw: Any) -> Any:
        """Get resource metrics for a project by ID."""
        return self.c.get(f"/v1/projects/id/{objid}/timeSeries/{mType}", query=_qp(kw))

    # GET /v1/projects/name/{objname}/timeSeries/{mType}
    def get_project_resource_metrics_by_name(self, objname: str, mType: str,
                                              **kw: Any) -> Any:
        """Get resource metrics for a project by name."""
        return self.c.get(f"/v1/projects/name/{objname}/timeSeries/{mType}", query=_qp(kw))

    # ======================================================================
    # PROJECTS V2 (Resource Group V2 / Deployments)
    # ======================================================================

    # POST /v2/projects
    def create_project_v2(self, body: dict) -> Any:
        """Create a project using V2 API."""
        return self.c.post("/v2/projects", body=body)

    # GET /v2/projects/id/{projectId}/deployments
    def get_deployments_by_project_id(self, projectId: str) -> Any:
        """List deployments for a project (v2)."""
        return self.c.get(f"/v2/projects/id/{projectId}/deployments")

    # POST /v2/projects/id/{projectId}/deployments
    def create_deployment(self, projectId: str, body: dict) -> Any:
        """Create a deployment in a project (v2)."""
        return self.c.post(f"/v2/projects/id/{projectId}/deployments", body=body)

    # DELETE /v2/projects/id/{projectId}/deployments
    def delete_all_deployments(self, projectId: str) -> Any:
        """Delete all deployments for a project (v2)."""
        return self.c.delete(f"/v2/projects/id/{projectId}/deployments")

    # GET /v2/projects/id/{projectId}/deployments/id/{id}
    def get_deployment_by_id(self, projectId: str, id: str) -> Any:
        """Get a specific deployment by project and deployment ID (v2)."""
        return self.c.get(f"/v2/projects/id/{projectId}/deployments/id/{id}")

    # PUT /v2/projects/id/{projectId}/deployments/id/{id}
    def update_deployment(self, projectId: str, id: str, body: dict) -> Any:
        """Update a deployment (v2)."""
        return self.c.put(f"/v2/projects/id/{projectId}/deployments/id/{id}", body=body)

    # DELETE /v2/projects/id/{projectId}/deployments/id/{id}
    def delete_deployment(self, projectId: str, id: str) -> Any:
        """Delete a specific deployment (v2)."""
        return self.c.delete(f"/v2/projects/id/{projectId}/deployments/id/{id}")
