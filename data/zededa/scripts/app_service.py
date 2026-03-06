#!/usr/bin/env python3
"""
ZEDEDA Edge Application Service — 80 endpoints

Covers edge application bundles, app instances (CRUD, lifecycle),
image management (upload, chunked, baseos), artifacts, datastores,
and volume instances.
"""

from __future__ import annotations
from typing import Any
from .client import ZededaClient
from .errors import AppServiceError


def _qp(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None and k != "self"}


class AppService:
    """Edge Application Service — bundles, instances, images, artifacts,
    datastores, and volume instances."""

    def __init__(self, client: ZededaClient):
        self.c = client

    # ======================================================================
    # EDGE APPLICATION BUNDLES
    # ======================================================================

    # GET /v1/apps
    def query_edge_application_bundles(self, **kw: Any) -> Any:
        """Query edge application bundles."""
        return self.c.get("/v1/apps", query=_qp(kw))

    # POST /v1/apps
    def create_edge_application_bundle(self, body: dict) -> Any:
        """Create an edge application bundle."""
        return self.c.post("/v1/apps", body=body)

    # GET /v1/apps/id/{id}
    def get_edge_application_bundle(self, id: str) -> Any:
        """Get application bundle by ID."""
        return self.c.get(f"/v1/apps/id/{id}")

    # PUT /v1/apps/id/{id}
    def update_edge_application_bundle(self, id: str, body: dict) -> Any:
        """Update an application bundle."""
        return self.c.put(f"/v1/apps/id/{id}", body=body)

    # DELETE /v1/apps/id/{id}
    def delete_edge_application_bundle(self, id: str) -> Any:
        """Delete an application bundle."""
        return self.c.delete(f"/v1/apps/id/{id}")

    # GET /v1/apps/name/{name}
    def get_edge_application_bundle_by_name(self, name: str) -> Any:
        """Get application bundle by name."""
        return self.c.get(f"/v1/apps/name/{name}")

    # GET /v1/apps/global
    def query_global_edge_application_bundles(self, **kw: Any) -> Any:
        """Query global edge application bundles."""
        return self.c.get("/v1/apps/global", query=_qp(kw))

    # GET /v1/apps/global/id/{id}
    def get_global_edge_application_bundle(self, id: str) -> Any:
        """Get a global edge application bundle by ID."""
        return self.c.get(f"/v1/apps/global/id/{id}")

    # GET /v1/apps/global/name/{name}
    def get_global_edge_application_bundle_by_name(self, name: str) -> Any:
        """Get global application bundle by name."""
        return self.c.get(f"/v1/apps/global/name/{name}")

    # ======================================================================
    # EDGE APPLICATION INSTANCES
    # ======================================================================

    # GET /v1/apps/instances
    def query_edge_application_instances(self, **kw: Any) -> Any:
        """Query edge application instances."""
        return self.c.get("/v1/apps/instances", query=_qp(kw))

    # POST /v1/apps/instances
    def create_edge_application_instance(self, body: dict) -> Any:
        """Create an edge application instance."""
        return self.c.post("/v1/apps/instances", body=body)

    # GET /v1/apps/instances/id/{id}
    def get_edge_application_instance(self, id: str) -> Any:
        """Get application instance by ID."""
        return self.c.get(f"/v1/apps/instances/id/{id}")

    # PUT /v1/apps/instances/id/{id}
    def update_edge_application_instance(self, id: str, body: dict) -> Any:
        """Update an application instance."""
        return self.c.put(f"/v1/apps/instances/id/{id}", body=body)

    # DELETE /v1/apps/instances/id/{id}
    def delete_edge_application_instance(self, id: str) -> Any:
        """Delete an application instance."""
        return self.c.delete(f"/v1/apps/instances/id/{id}")

    # PUT /v1/apps/instances/id/{id}/activate
    def activate_edge_application_instance(self, id: str) -> Any:
        """Activate an application instance."""
        return self.c.put(f"/v1/apps/instances/id/{id}/activate")

    # PUT /v1/apps/instances/id/{id}/deactivate
    def deactivate_edge_application_instance(self, id: str) -> Any:
        """Deactivate an application instance."""
        return self.c.put(f"/v1/apps/instances/id/{id}/deactivate")

    # PUT /v1/apps/instances/id/{id}/edgeview
    def start_edge_application_instance_debug(self, id: str, body: dict) -> Any:
        """Start edge-view debug for an app instance."""
        return self.c.put(f"/v1/apps/instances/id/{id}/edgeview", body=body)

    # PUT /v1/apps/instances/id/{id}/edgeview/stop
    def stop_edge_application_instance_debug(self, id: str) -> Any:
        """Stop edge-view debug for an app instance."""
        return self.c.put(f"/v1/apps/instances/id/{id}/edgeview/stop")

    # PUT /v1/apps/instances/id/{id}/publish
    def publish_edge_application_instance(self, id: str, body: dict) -> Any:
        """Publish an application instance."""
        return self.c.put(f"/v1/apps/instances/id/{id}/publish", body=body)

    # PUT /v1/apps/instances/id/{id}/refresh
    def refresh_edge_application_instance(self, id: str) -> Any:
        """Refresh an application instance."""
        return self.c.put(f"/v1/apps/instances/id/{id}/refresh")

    # PUT /v1/apps/instances/id/{id}/refresh/purge
    def refresh_purge_edge_application_instance(self, id: str) -> Any:
        """Refresh and purge an application instance."""
        return self.c.put(f"/v1/apps/instances/id/{id}/refresh/purge")

    # PUT /v1/apps/instances/id/{id}/restart
    def restart_edge_application_instance(self, id: str) -> Any:
        """Restart an application instance."""
        return self.c.put(f"/v1/apps/instances/id/{id}/restart")

    # PUT /v1/apps/instances/id/{id}/unpublish
    def unpublish_edge_application_instance(self, id: str) -> Any:
        """Unpublish an application instance."""
        return self.c.put(f"/v1/apps/instances/id/{id}/unpublish")

    # GET /v1/apps/instances/name/{name}
    def get_edge_application_instance_by_name(self, name: str) -> Any:
        """Get application instance by name."""
        return self.c.get(f"/v1/apps/instances/name/{name}")

    # -- App instance status ------------------------------------------------

    # GET /v1/apps/instances/status
    def query_edge_application_instance_status(self, **kw: Any) -> Any:
        """Query application instance status list."""
        return self.c.get("/v1/apps/instances/status", query=_qp(kw))

    # GET /v1/apps/instances/status-config
    def query_edge_application_instance_status_config(self, **kw: Any) -> Any:
        """Query application instance status with config."""
        return self.c.get("/v1/apps/instances/status-config", query=_qp(kw))

    # GET /v1/apps/instances/id/{id}/status
    def get_edge_application_instance_status(self, id: str) -> Any:
        """Get application instance status by ID."""
        return self.c.get(f"/v1/apps/instances/id/{id}/status")

    # GET /v1/apps/instances/name/{name}/status
    def get_edge_application_instance_status_by_name(self, name: str) -> Any:
        """Get application instance status by name."""
        return self.c.get(f"/v1/apps/instances/name/{name}/status")

    # -- App instance events & metrics --------------------------------------

    # GET /v1/apps/instances/id/{objid}/events
    def get_edge_application_instance_events(self, objid: str, **kw: Any) -> Any:
        """Get events for an app instance by ID."""
        return self.c.get(f"/v1/apps/instances/id/{objid}/events", query=_qp(kw))

    # GET /v1/apps/instances/name/{objname}/events
    def get_edge_application_instance_events_by_name(self, objname: str, **kw: Any) -> Any:
        """Get events for an app instance by name."""
        return self.c.get(f"/v1/apps/instances/name/{objname}/events", query=_qp(kw))

    # GET /v1/apps/instances/id/{objid}/timeSeries/{mType}
    def get_edge_application_instance_resource_metrics_by_id(self, objid: str, mType: str, **kw: Any) -> Any:
        """Get resource metrics for an app instance by ID."""
        return self.c.get(f"/v1/apps/instances/id/{objid}/timeSeries/{mType}", query=_qp(kw))

    # GET /v1/apps/instances/name/{objname}/timeSeries/{mType}
    def get_edge_application_instance_resource_metrics_by_name(self, objname: str, mType: str, **kw: Any) -> Any:
        """Get resource metrics for an app instance by name."""
        return self.c.get(f"/v1/apps/instances/name/{objname}/timeSeries/{mType}", query=_qp(kw))

    # -- App instance logs --------------------------------------------------

    # GET /v1/apps/instances/id/{id}/logs
    def get_edge_application_instance_logs(self, id: str, **kw: Any) -> Any:
        """Get logs for an application instance by ID."""
        return self.c.get(f"/v1/apps/instances/id/{id}/logs", query=_qp(kw))

    # ======================================================================
    # IMAGE CONFIGURATION
    # ======================================================================

    # GET /v1/apps/images
    def query_images(self, **kw: Any) -> Any:
        """Query application images."""
        return self.c.get("/v1/apps/images", query=_qp(kw))

    # POST /v1/apps/images
    def create_image(self, body: dict) -> Any:
        """Create an image configuration."""
        return self.c.post("/v1/apps/images", body=body)

    # GET /v1/apps/images/id/{id}
    def get_image(self, id: str) -> Any:
        """Get image by ID."""
        return self.c.get(f"/v1/apps/images/id/{id}")

    # PUT /v1/apps/images/id/{id}
    def update_image(self, id: str, body: dict) -> Any:
        """Update an image configuration."""
        return self.c.put(f"/v1/apps/images/id/{id}", body=body)

    # DELETE /v1/apps/images/id/{id}
    def delete_image(self, id: str) -> Any:
        """Delete an image."""
        return self.c.delete(f"/v1/apps/images/id/{id}")

    # PUT /v1/apps/images/id/{id}/uplink
    def uplink_image(self, id: str) -> Any:
        """Uplink an image."""
        return self.c.put(f"/v1/apps/images/id/{id}/uplink")

    # GET /v1/apps/images/name/{name}
    def get_image_by_name(self, name: str) -> Any:
        """Get image by name."""
        return self.c.get(f"/v1/apps/images/name/{name}")

    # PUT /v1/apps/images/name/{name}/upload/chunked
    def upload_image_chunked(self, name: str, body: dict) -> Any:
        """Upload an image using chunked upload."""
        return self.c.put(f"/v1/apps/images/name/{name}/upload/chunked", body=body)

    # PUT /v1/apps/images/name/{name}/upload/file
    def upload_image_file(self, name: str, body: dict) -> Any:
        """Upload an image file."""
        return self.c.put(f"/v1/apps/images/name/{name}/upload/file", body=body)

    # GET /v1/apps/images/projects
    def query_image_project_list(self, **kw: Any) -> Any:
        """Query image project list."""
        return self.c.get("/v1/apps/images/projects", query=_qp(kw))

    # -- Base OS images -----------------------------------------------------

    # GET /v1/apps/images/baseos
    def query_baseos_images(self, **kw: Any) -> Any:
        """Query base-OS images."""
        return self.c.get("/v1/apps/images/baseos", query=_qp(kw))

    # PUT /v1/apps/images/baseos/latest
    def mark_eve_image_latest(self, body: dict) -> Any:
        """Mark an EVE image as latest."""
        return self.c.put("/v1/apps/images/baseos/latest", body=body)

    # GET /v1/apps/images/baseos/latest/hwclass/{imageArch}
    def get_latest_image_version(self, imageArch: str) -> Any:
        """Get latest image version for a hardware architecture."""
        return self.c.get(f"/v1/apps/images/baseos/latest/hwclass/{imageArch}")

    # PUT /v1/apps/images/baseos/latest/hwclass/{imageArch}
    def mark_eve_image_latest_by_arch(self, imageArch: str, body: dict) -> Any:
        """Mark an EVE image as latest for a specific architecture."""
        return self.c.put(f"/v1/apps/images/baseos/latest/hwclass/{imageArch}", body=body)

    # ======================================================================
    # ARTIFACT MANAGER
    # ======================================================================

    # GET /v1/artifacts
    def query_artifacts(self, **kw: Any) -> Any:
        """Query artifacts."""
        return self.c.get("/v1/artifacts", query=_qp(kw))

    # POST /v1/artifacts
    def create_artifact(self, body: dict) -> Any:
        """Create an artifact."""
        return self.c.post("/v1/artifacts", body=body)

    # GET /v1/artifacts/id/{id}
    def get_artifact_stream(self, id: str) -> Any:
        """Get artifact stream by ID."""
        return self.c.get(f"/v1/artifacts/id/{id}")

    # DELETE /v1/artifacts/id/{id}
    def delete_artifact(self, id: str) -> Any:
        """Delete an artifact."""
        return self.c.delete(f"/v1/artifacts/id/{id}")

    # PUT /v1/artifacts/id/{id}/upload/chunked
    def upload_artifact(self, id: str, body: dict) -> Any:
        """Upload an artifact using chunked upload."""
        return self.c.put(f"/v1/artifacts/id/{id}/upload/chunked", body=body)

    # GET /v1/artifacts/id/{id}/url
    def get_artifact_signed_url(self, id: str) -> Any:
        """Get artifact signed download URL."""
        return self.c.get(f"/v1/artifacts/id/{id}/url")

    # ======================================================================
    # DATASTORE CONFIGURATION
    # ======================================================================

    # GET /v1/datastores
    def query_datastores(self, **kw: Any) -> Any:
        """Query datastores."""
        return self.c.get("/v1/datastores", query=_qp(kw))

    # POST /v1/datastores
    def create_datastore(self, body: dict) -> Any:
        """Create a datastore."""
        return self.c.post("/v1/datastores", body=body)

    # GET /v1/datastores/id/{id}
    def get_datastore(self, id: str) -> Any:
        """Get datastore by ID."""
        return self.c.get(f"/v1/datastores/id/{id}")

    # PUT /v1/datastores/id/{id}
    def update_datastore(self, id: str, body: dict) -> Any:
        """Update a datastore."""
        return self.c.put(f"/v1/datastores/id/{id}", body=body)

    # DELETE /v1/datastores/id/{id}
    def delete_datastore(self, id: str) -> Any:
        """Delete a datastore."""
        return self.c.delete(f"/v1/datastores/id/{id}")

    # GET /v1/datastores/name/{name}
    def get_datastore_by_name(self, name: str) -> Any:
        """Get datastore by name."""
        return self.c.get(f"/v1/datastores/name/{name}")

    # GET /v1/datastores/projects
    def query_datastore_project_list(self, **kw: Any) -> Any:
        """Query datastore project list."""
        return self.c.get("/v1/datastores/projects", query=_qp(kw))

    # ======================================================================
    # VOLUME INSTANCE CONFIGURATION
    # ======================================================================

    # GET /v1/volumes/instances
    def query_volume_instances(self, **kw: Any) -> Any:
        """Query volume instances."""
        return self.c.get("/v1/volumes/instances", query=_qp(kw))

    # POST /v1/volumes/instances
    def create_volume_instance(self, body: dict) -> Any:
        """Create a volume instance."""
        return self.c.post("/v1/volumes/instances", body=body)

    # GET /v1/volumes/instances/id/{id}
    def get_volume_instance(self, id: str) -> Any:
        """Get volume instance by ID."""
        return self.c.get(f"/v1/volumes/instances/id/{id}")

    # PUT /v1/volumes/instances/id/{id}
    def update_volume_instance(self, id: str, body: dict) -> Any:
        """Update a volume instance."""
        return self.c.put(f"/v1/volumes/instances/id/{id}", body=body)

    # DELETE /v1/volumes/instances/id/{id}
    def delete_volume_instance(self, id: str) -> Any:
        """Delete a volume instance."""
        return self.c.delete(f"/v1/volumes/instances/id/{id}")

    # GET /v1/volumes/instances/name/{name}
    def get_volume_instance_by_name(self, name: str) -> Any:
        """Get volume instance by name."""
        return self.c.get(f"/v1/volumes/instances/name/{name}")

    # -- Volume instance status ---------------------------------------------

    # GET /v1/volumes/instances/status
    def query_volume_instance_status(self, **kw: Any) -> Any:
        """Query volume instance status list."""
        return self.c.get("/v1/volumes/instances/status", query=_qp(kw))

    # GET /v1/volumes/instances/status-config
    def query_volume_instance_status_config(self, **kw: Any) -> Any:
        """Query volume instance status with config."""
        return self.c.get("/v1/volumes/instances/status-config", query=_qp(kw))

    # GET /v1/volumes/instances/id/{id}/status
    def get_volume_instance_status(self, id: str) -> Any:
        """Get volume instance status by ID."""
        return self.c.get(f"/v1/volumes/instances/id/{id}/status")

    # GET /v1/volumes/instances/name/{name}/status
    def get_volume_instance_status_by_name(self, name: str) -> Any:
        """Get volume instance status by name."""
        return self.c.get(f"/v1/volumes/instances/name/{name}/status")

    # -- Volume instance events ---------------------------------------------

    # GET /v1/volumes/instances/id/{objid}/events
    def get_volume_instance_events(self, objid: str, **kw: Any) -> Any:
        """Get events for a volume instance by ID."""
        return self.c.get(f"/v1/volumes/instances/id/{objid}/events", query=_qp(kw))

    # GET /v1/volumes/instances/name/{objname}/events
    def get_volume_instance_events_by_name(self, objname: str, **kw: Any) -> Any:
        """Get events for a volume instance by name."""
        return self.c.get(f"/v1/volumes/instances/name/{objname}/events", query=_qp(kw))

    # ======================================================================
    # ADDITIONAL APP BUNDLE ENDPOINTS
    # ======================================================================

    # GET /beta/apps
    def query_edge_application_bundles_beta(self, **kw: Any) -> Any:
        """Query edge application bundles (beta)."""
        return self.c.get("/beta/apps", query=_qp(kw))

    # GET /v1/apps/id/{id}/projects
    def get_edge_application_bundle_projects(self, id: str) -> Any:
        """Get projects for an app bundle."""
        return self.c.get(f"/v1/apps/id/{id}/projects")

    # ======================================================================
    # ADDITIONAL APP INSTANCE ENDPOINTS
    # ======================================================================

    # PUT /v1/apps/instances/id/{id}/console/remote
    def connect_to_edge_application_instance(self, id: str) -> Any:
        """Connect to remote console of app instance."""
        return self.c.put(f"/v1/apps/instances/id/{id}/console/remote")

    # GET /v1/apps/instances/id/{id}/flowlog/classification
    def get_edge_application_instance_traffic_flows(self, id: str, **kw: Any) -> Any:
        """Get traffic flow classification for app instance by ID."""
        return self.c.get(f"/v1/apps/instances/id/{id}/flowlog/classification", query=_qp(kw))

    # GET /v1/apps/instances/id/{id}/flowlog/toptalkers
    def get_edge_application_instance_top_talkers(self, id: str, **kw: Any) -> Any:
        """Get top talkers for app instance by ID."""
        return self.c.get(f"/v1/apps/instances/id/{id}/flowlog/toptalkers", query=_qp(kw))

    # GET /v1/apps/instances/id/{id}/opaque-status
    def get_edge_application_instance_opaque_status(self, id: str) -> Any:
        """Get opaque status for app instance by ID."""
        return self.c.get(f"/v1/apps/instances/id/{id}/opaque-status")

    # GET /v1/apps/instances/id/{id}/snapshots
    def get_app_instance_snapshots(self, id: str) -> Any:
        """Get snapshots for an app instance."""
        return self.c.get(f"/v1/apps/instances/id/{id}/snapshots")

    # GET /v1/apps/instances/id/{appInstanceId}/snapshot/name/{name}
    def get_app_instance_snapshot(self, appInstanceId: str, name: str) -> Any:
        """Get a specific snapshot by name."""
        return self.c.get(f"/v1/apps/instances/id/{appInstanceId}/snapshot/name/{name}")

    # DELETE /v1/apps/instances/id/{appInstanceId}/snapshot/name/{name}
    def delete_app_instance_snapshot(self, appInstanceId: str, name: str) -> Any:
        """Delete a specific snapshot by name."""
        return self.c.delete(f"/v1/apps/instances/id/{appInstanceId}/snapshot/name/{name}")

    # GET /v1/apps/instances/snapshot/id/{id}
    def get_app_instance_snapshot_by_id(self, id: str) -> Any:
        """Get a snapshot by its own ID."""
        return self.c.get(f"/v1/apps/instances/snapshot/id/{id}")

    # GET /v1/apps/instances/snapshot/id/{id}/state
    def get_app_instance_snapshot_state(self, id: str) -> Any:
        """Get snapshot state by ID."""
        return self.c.get(f"/v1/apps/instances/snapshot/id/{id}/state")

    # GET /v1/apps/instances/name/{name}/flowlog/classification
    def get_edge_application_instance_traffic_flows_by_name(self, name: str, **kw: Any) -> Any:
        """Get traffic flow classification by name."""
        return self.c.get(f"/v1/apps/instances/name/{name}/flowlog/classification", query=_qp(kw))

    # GET /v1/apps/instances/name/{name}/flowlog/toptalkers
    def get_edge_application_instance_top_talkers_by_name(self, name: str, **kw: Any) -> Any:
        """Get top talkers by name."""
        return self.c.get(f"/v1/apps/instances/name/{name}/flowlog/toptalkers", query=_qp(kw))

    # GET /v1/apps/instances/name/{name}/opaque-status
    def get_edge_application_instance_opaque_status_by_name(self, name: str) -> Any:
        """Get opaque status for app instance by name."""
        return self.c.get(f"/v1/apps/instances/name/{name}/opaque-status")

    # POST /v1/apps/instances/patch-reference-update
    def update_patch_envelope_reference(self, body: dict) -> Any:
        """Update patch envelope reference for app instance."""
        return self.c.post("/v1/apps/instances/patch-reference-update", body=body)

    # GET /v1/apps/instances/tags
    def get_application_interface_tags(self) -> Any:
        """Get application interface tags."""
        return self.c.get("/v1/apps/instances/tags")

    # ======================================================================
    # PATCH ENVELOPE (App-level)
    # ======================================================================

    # GET /v1/patch-envelope
    def query_patch_envelopes_v1(self, **kw: Any) -> Any:
        """GET /v1/patch-envelope — Query patch envelopes."""
        return self.c.get("/v1/patch-envelope", query=_qp(kw))

    # POST /v1/patch-envelope
    def create_patch_envelope_v1(self, body: dict) -> Any:
        """POST /v1/patch-envelope — Create patch envelope."""
        return self.c.post("/v1/patch-envelope", body=body)

    # GET /v1/patch-envelope/id/{id}
    def get_patch_envelope_v1(self, id: str) -> Any:
        """GET /v1/patch-envelope/id/{id}"""
        return self.c.get(f"/v1/patch-envelope/id/{id}")

    # PUT /v1/patch-envelope/id/{id}
    def update_patch_envelope_v1(self, id: str, body: dict) -> Any:
        """PUT /v1/patch-envelope/id/{id}"""
        return self.c.put(f"/v1/patch-envelope/id/{id}", body=body)

    # DELETE /v1/patch-envelope/id/{id}
    def delete_patch_envelope_v1(self, id: str) -> Any:
        """DELETE /v1/patch-envelope/id/{id}"""
        return self.c.delete(f"/v1/patch-envelope/id/{id}")

    # GET /v1/patch-envelope/name/{name}
    def get_patch_envelope_by_name_v1(self, name: str) -> Any:
        """GET /v1/patch-envelope/name/{name}"""
        return self.c.get(f"/v1/patch-envelope/name/{name}")

    # GET /v1/patch-envelope/status
    def get_patch_envelope_status_v1(self, **kw: Any) -> Any:
        """GET /v1/patch-envelope/status"""
        return self.c.get("/v1/patch-envelope/status", query=_qp(kw))

    # ======================================================================
    # V2 APP INSTANCES
    # ======================================================================

    # GET /v2/apps/instances
    def query_edge_application_instances_v2(self, **kw: Any) -> Any:
        """Query app instances (v2)."""
        return self.c.get("/v2/apps/instances", query=_qp(kw))

    # POST /v2/apps/instances
    def create_edge_application_instance_v2(self, body: dict) -> Any:
        """Create app instance (v2)."""
        return self.c.post("/v2/apps/instances", body=body)

    # GET /v2/apps/instances/id/{id}
    def get_edge_application_instance_v2(self, id: str) -> Any:
        """Get app instance by ID (v2)."""
        return self.c.get(f"/v2/apps/instances/id/{id}")

    # PUT /v2/apps/instances/id/{id}
    def update_edge_application_instance_v2(self, id: str, body: dict) -> Any:
        """Update app instance (v2)."""
        return self.c.put(f"/v2/apps/instances/id/{id}", body=body)

    # DELETE /v2/apps/instances/id/{id}
    def delete_edge_application_instance_v2(self, id: str) -> Any:
        """Delete app instance (v2)."""
        return self.c.delete(f"/v2/apps/instances/id/{id}")

    # PUT /v2/apps/instances/id/{id}/activate
    def activate_edge_application_instance_v2(self, id: str) -> Any:
        """Activate app instance (v2)."""
        return self.c.put(f"/v2/apps/instances/id/{id}/activate")

    # PUT /v2/apps/instances/id/{id}/deactivate
    def deactivate_edge_application_instance_v2(self, id: str) -> Any:
        """Deactivate app instance (v2)."""
        return self.c.put(f"/v2/apps/instances/id/{id}/deactivate")

    # PUT /v2/apps/instances/id/{id}/console/remote
    def connect_to_edge_application_instance_v2(self, id: str) -> Any:
        """Remote console (v2)."""
        return self.c.put(f"/v2/apps/instances/id/{id}/console/remote")

    # PUT /v2/apps/instances/id/{id}/refresh
    def refresh_edge_application_instance_v2(self, id: str) -> Any:
        """Refresh app instance (v2)."""
        return self.c.put(f"/v2/apps/instances/id/{id}/refresh")

    # PUT /v2/apps/instances/id/{id}/refresh/purge
    def refresh_purge_edge_application_instance_v2(self, id: str) -> Any:
        """Refresh and purge app instance (v2)."""
        return self.c.put(f"/v2/apps/instances/id/{id}/refresh/purge")

    # PUT /v2/apps/instances/id/{id}/restart
    def restart_edge_application_instance_v2(self, id: str) -> Any:
        """Restart app instance (v2)."""
        return self.c.put(f"/v2/apps/instances/id/{id}/restart")

    # GET /v2/apps/instances/id/{id}/status
    def get_edge_application_instance_status_v2(self, id: str) -> Any:
        """Get app instance status (v2)."""
        return self.c.get(f"/v2/apps/instances/id/{id}/status")

    # GET /v2/apps/instances/id/{id}/flowlog/classification
    def get_edge_application_instance_traffic_flows_v2(self, id: str, **kw: Any) -> Any:
        """Get traffic flows (v2)."""
        return self.c.get(f"/v2/apps/instances/id/{id}/flowlog/classification", query=_qp(kw))

    # GET /v2/apps/instances/id/{id}/flowlog/toptalkers
    def get_edge_application_instance_top_talkers_v2(self, id: str, **kw: Any) -> Any:
        """Get top talkers (v2)."""
        return self.c.get(f"/v2/apps/instances/id/{id}/flowlog/toptalkers", query=_qp(kw))

    # GET /v2/apps/instances/id/{id}/logs
    def get_edge_application_instance_logs_v2(self, id: str, **kw: Any) -> Any:
        """Get logs (v2)."""
        return self.c.get(f"/v2/apps/instances/id/{id}/logs", query=_qp(kw))

    # GET /v2/apps/instances/id/{id}/opaque-status
    def get_edge_application_instance_opaque_status_v2(self, id: str) -> Any:
        """Get opaque status (v2)."""
        return self.c.get(f"/v2/apps/instances/id/{id}/opaque-status")

    # GET /v2/apps/instances/id/{objid}/events
    def get_edge_application_instance_events_v2(self, objid: str, **kw: Any) -> Any:
        """Get events (v2)."""
        return self.c.get(f"/v2/apps/instances/id/{objid}/events", query=_qp(kw))

    # GET /v2/apps/instances/id/{objid}/timeSeries/{mType}
    def get_edge_application_instance_resource_metrics_by_id_v2(self, objid: str, mType: str, **kw: Any) -> Any:
        """Get resource metrics (v2)."""
        return self.c.get(f"/v2/apps/instances/id/{objid}/timeSeries/{mType}", query=_qp(kw))

    # GET /v2/apps/instances/name/{name}
    def get_edge_application_instance_by_name_v2(self, name: str) -> Any:
        """Get app instance by name (v2)."""
        return self.c.get(f"/v2/apps/instances/name/{name}")

    # GET /v2/apps/instances/name/{name}/flowlog/classification
    def get_edge_application_instance_traffic_flows_by_name_v2(self, name: str, **kw: Any) -> Any:
        """Get traffic flows by name (v2)."""
        return self.c.get(f"/v2/apps/instances/name/{name}/flowlog/classification", query=_qp(kw))

    # GET /v2/apps/instances/name/{name}/flowlog/toptalkers
    def get_edge_application_instance_top_talkers_by_name_v2(self, name: str, **kw: Any) -> Any:
        """Get top talkers by name (v2)."""
        return self.c.get(f"/v2/apps/instances/name/{name}/flowlog/toptalkers", query=_qp(kw))

    # GET /v2/apps/instances/name/{name}/opaque-status
    def get_edge_application_instance_opaque_status_by_name_v2(self, name: str) -> Any:
        """Get opaque status by name (v2)."""
        return self.c.get(f"/v2/apps/instances/name/{name}/opaque-status")

    # GET /v2/apps/instances/name/{name}/status
    def get_edge_application_instance_status_by_name_v2(self, name: str) -> Any:
        """Get app instance status by name (v2)."""
        return self.c.get(f"/v2/apps/instances/name/{name}/status")

    # GET /v2/apps/instances/name/{objname}/events
    def get_edge_application_instance_events_by_name_v2(self, objname: str, **kw: Any) -> Any:
        """Get events by name (v2)."""
        return self.c.get(f"/v2/apps/instances/name/{objname}/events", query=_qp(kw))

    # GET /v2/apps/instances/name/{objname}/timeSeries/{mType}
    def get_edge_application_instance_resource_metrics_by_name_v2(self, objname: str, mType: str, **kw: Any) -> Any:
        """Get resource metrics by name (v2)."""
        return self.c.get(f"/v2/apps/instances/name/{objname}/timeSeries/{mType}", query=_qp(kw))

    # POST /v2/apps/instances/patch-reference-update
    def update_patch_envelope_reference_v2(self, body: dict) -> Any:
        """Update patch envelope reference (v2)."""
        return self.c.post("/v2/apps/instances/patch-reference-update", body=body)

    # GET /v2/apps/instances/status
    def query_edge_application_instance_status_v2(self, **kw: Any) -> Any:
        """Query app instance status (v2)."""
        return self.c.get("/v2/apps/instances/status", query=_qp(kw))

    # GET /v2/apps/instances/status-config
    def query_edge_application_instance_status_config_v2(self, **kw: Any) -> Any:
        """Query app instance status config (v2)."""
        return self.c.get("/v2/apps/instances/status-config", query=_qp(kw))

