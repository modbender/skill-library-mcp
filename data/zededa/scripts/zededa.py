#!/usr/bin/env python3
"""
ZEDEDA OpenClaw Skill — CLI Entrypoint

Usage:
    python3 scripts/zededa.py <service> <command> [arguments...]

Examples:
    python3 scripts/zededa.py node list-devices
    python3 scripts/zededa.py app get-bundle --id abc123
    python3 scripts/zededa.py user list-users
"""

# SECURITY MANIFEST:
# Environment variables accessed: ZEDEDA_API_TOKEN, ZEDEDA_BASE_URL, ZEDEDA_LOG_LEVEL
# External endpoints called: https://zedcontrol.zededa.net/api (default, configurable)
# Local files read: none (unless --body-file is used)
# Local files written: none

from __future__ import annotations

import argparse
import json
import sys

from .client import ZededaClient
from .node_service import NodeService
from .node_cluster_service import NodeClusterService
from .app_service import AppService
from .app_profile_service import AppProfileService
from .storage_service import StorageService
from .network_service import NetworkService
from .orchestration_service import OrchestrationService
from .kubernetes_service import KubernetesService
from .diag_service import DiagService
from .job_service import JobService
from .user_service import UserService
from .errors import ZededaError


def _out(data):
    """Pretty-print JSON response to stdout."""
    print(json.dumps(data, indent=2))


def _load_body(args) -> dict | None:
    """Load JSON body from --body or --body-file."""
    if hasattr(args, "body") and args.body:
        return json.loads(args.body)
    if hasattr(args, "body_file") and args.body_file:
        with open(args.body_file) as f:
            return json.load(f)
    return None


def _add_body_args(parser: argparse.ArgumentParser) -> None:
    grp = parser.add_mutually_exclusive_group()
    grp.add_argument("--body", help="JSON body as string")
    grp.add_argument("--body-file", help="Path to JSON body file")


def _add_id(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--id", required=True, help="Resource ID")


def _add_name(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--name", required=True, help="Resource name")


# ──────────────────────────────────────────────────────────────────────────
# NODE SERVICE
# ──────────────────────────────────────────────────────────────────────────

def _register_node(sub):
    svc = sub.add_parser("node", help="Edge Node Service")
    cmds = svc.add_subparsers(dest="command", required=True)

    cmds.add_parser("list-devices", help="List edge nodes")
    p = cmds.add_parser("get-device", help="Get edge node by ID"); _add_id(p)
    p = cmds.add_parser("get-device-by-name", help="Get edge node by name"); _add_name(p)
    p = cmds.add_parser("get-device-by-serial", help="Get edge node by serial"); p.add_argument("--serial", required=True)
    p = cmds.add_parser("create-device", help="Create edge node"); _add_body_args(p)
    p = cmds.add_parser("update-device", help="Update edge node"); _add_id(p); _add_body_args(p)
    p = cmds.add_parser("delete-device", help="Delete edge node"); _add_id(p)
    p = cmds.add_parser("reboot-device", help="Reboot edge node"); _add_id(p)
    p = cmds.add_parser("deactivate-device", help="Deactivate edge node"); _add_id(p)
    p = cmds.add_parser("offboard-device", help="Offboard edge node"); _add_id(p)
    p = cmds.add_parser("attest-device", help="Attest edge node"); _add_id(p)
    p = cmds.add_parser("device-status", help="Get edge node status"); _add_id(p)
    p = cmds.add_parser("device-events", help="Get edge node events"); _add_id(p)
    cmds.add_parser("list-status", help="List all edge node statuses")
    cmds.add_parser("list-models", help="List hardware models")
    p = cmds.add_parser("get-model", help="Get hardware model by ID"); _add_id(p)
    p = cmds.add_parser("create-model", help="Create hardware model"); _add_body_args(p)
    cmds.add_parser("list-projects", help="List projects")
    p = cmds.add_parser("get-project", help="Get project by ID"); _add_id(p)
    p = cmds.add_parser("create-project", help="Create project"); _add_body_args(p)


def _run_node(args, client):
    svc = NodeService(client)
    cmd = args.command
    if cmd == "list-devices": return svc.query_edge_nodes()
    if cmd == "get-device": return svc.get_edge_node(args.id)
    if cmd == "get-device-by-name": return svc.get_edge_node_by_name(args.name)
    if cmd == "get-device-by-serial": return svc.get_edge_node_by_serial(args.serial)
    if cmd == "create-device": return svc.create_edge_node(_load_body(args) or {})
    if cmd == "update-device": return svc.update_edge_node(args.id, _load_body(args) or {})
    if cmd == "delete-device": return svc.delete_edge_node(args.id)
    if cmd == "reboot-device": return svc.reboot_edge_node(args.id)
    if cmd == "deactivate-device": return svc.deactivate_edge_node(args.id)
    if cmd == "offboard-device": return svc.offboard_edge_node(args.id)
    if cmd == "attest-device": return svc.attest_edge_node(args.id)
    if cmd == "device-status": return svc.get_edge_node_status(args.id)
    if cmd == "device-events": return svc.get_edge_node_events(args.id)
    if cmd == "list-status": return svc.query_edge_node_status()
    if cmd == "list-models": return svc.query_hardware_models()
    if cmd == "get-model": return svc.get_hardware_model(args.id)
    if cmd == "create-model": return svc.create_hardware_model(_load_body(args) or {})
    if cmd == "list-projects": return svc.query_projects()
    if cmd == "get-project": return svc.get_project(args.id)
    if cmd == "create-project": return svc.create_project(_load_body(args) or {})


# ──────────────────────────────────────────────────────────────────────────
# APP SERVICE
# ──────────────────────────────────────────────────────────────────────────

def _register_app(sub):
    svc = sub.add_parser("app", help="Edge Application Service")
    cmds = svc.add_subparsers(dest="command", required=True)

    cmds.add_parser("list-bundles", help="List app bundles")
    p = cmds.add_parser("get-bundle", help="Get app bundle"); _add_id(p)
    p = cmds.add_parser("create-bundle", help="Create app bundle"); _add_body_args(p)
    p = cmds.add_parser("delete-bundle", help="Delete app bundle"); _add_id(p)
    cmds.add_parser("list-instances", help="List app instances")
    p = cmds.add_parser("get-instance", help="Get instance"); _add_id(p)
    p = cmds.add_parser("create-instance", help="Create instance"); _add_body_args(p)
    p = cmds.add_parser("delete-instance", help="Delete instance"); _add_id(p)
    p = cmds.add_parser("activate-instance", help="Activate instance"); _add_id(p)
    p = cmds.add_parser("deactivate-instance", help="Deactivate instance"); _add_id(p)
    p = cmds.add_parser("restart-instance", help="Restart instance"); _add_id(p)
    p = cmds.add_parser("refresh-instance", help="Refresh instance"); _add_id(p)
    p = cmds.add_parser("instance-status", help="Instance status"); _add_id(p)
    p = cmds.add_parser("instance-logs", help="Instance logs"); _add_id(p)
    cmds.add_parser("list-images", help="List images")
    p = cmds.add_parser("get-image", help="Get image"); _add_id(p)
    p = cmds.add_parser("create-image", help="Create image"); _add_body_args(p)
    cmds.add_parser("list-datastores", help="List datastores")
    cmds.add_parser("list-volumes", help="List volume instances")


def _run_app(args, client):
    svc = AppService(client)
    cmd = args.command
    if cmd == "list-bundles": return svc.query_edge_application_bundles()
    if cmd == "get-bundle": return svc.get_edge_application_bundle(args.id)
    if cmd == "create-bundle": return svc.create_edge_application_bundle(_load_body(args) or {})
    if cmd == "delete-bundle": return svc.delete_edge_application_bundle(args.id)
    if cmd == "list-instances": return svc.query_edge_application_instances()
    if cmd == "get-instance": return svc.get_edge_application_instance(args.id)
    if cmd == "create-instance": return svc.create_edge_application_instance(_load_body(args) or {})
    if cmd == "delete-instance": return svc.delete_edge_application_instance(args.id)
    if cmd == "activate-instance": return svc.activate_edge_application_instance(args.id)
    if cmd == "deactivate-instance": return svc.deactivate_edge_application_instance(args.id)
    if cmd == "restart-instance": return svc.restart_edge_application_instance(args.id)
    if cmd == "refresh-instance": return svc.refresh_edge_application_instance(args.id)
    if cmd == "instance-status": return svc.get_edge_application_instance_status(args.id)
    if cmd == "instance-logs": return svc.get_edge_application_instance_logs(args.id)
    if cmd == "list-images": return svc.query_images()
    if cmd == "get-image": return svc.get_image(args.id)
    if cmd == "create-image": return svc.create_image(_load_body(args) or {})
    if cmd == "list-datastores": return svc.query_datastores()
    if cmd == "list-volumes": return svc.query_volume_instances()


# ──────────────────────────────────────────────────────────────────────────
# USER SERVICE
# ──────────────────────────────────────────────────────────────────────────

def _register_user(sub):
    svc = sub.add_parser("user", help="User / IAM Service")
    cmds = svc.add_subparsers(dest="command", required=True)

    cmds.add_parser("list-users", help="List users")
    p = cmds.add_parser("get-user", help="Get user"); _add_id(p)
    p = cmds.add_parser("create-user", help="Create user"); _add_body_args(p)
    p = cmds.add_parser("delete-user", help="Delete user"); _add_id(p)
    cmds.add_parser("whoami", help="Get current user")
    cmds.add_parser("list-roles", help="List roles")
    cmds.add_parser("list-enterprises", help="List enterprises")
    cmds.add_parser("enterprise-self", help="Get own enterprise")
    cmds.add_parser("list-realms", help="List realms")
    cmds.add_parser("list-sessions", help="List sessions")
    cmds.add_parser("refresh-session", help="Refresh session")


def _run_user(args, client):
    svc = UserService(client)
    cmd = args.command
    if cmd == "list-users": return svc.query_users()
    if cmd == "get-user": return svc.get_user(args.id)
    if cmd == "create-user": return svc.create_user(_load_body(args) or {})
    if cmd == "delete-user": return svc.delete_user(args.id)
    if cmd == "whoami": return svc.get_user_self()
    if cmd == "list-roles": return svc.query_roles()
    if cmd == "list-enterprises": return svc.query_enterprises()
    if cmd == "enterprise-self": return svc.get_enterprise_self()
    if cmd == "list-realms": return svc.query_realms()
    if cmd == "list-sessions": return svc.query_user_sessions()
    if cmd == "refresh-session": return svc.refresh_user_session()


# ──────────────────────────────────────────────────────────────────────────
# REMAINING SERVICES (compact registration)
# ──────────────────────────────────────────────────────────────────────────

def _register_storage(sub):
    svc = sub.add_parser("storage", help="Storage Service")
    cmds = svc.add_subparsers(dest="command", required=True)
    cmds.add_parser("list-patches", help="List patch envelopes")
    p = cmds.add_parser("get-patch", help="Get patch envelope"); _add_id(p)
    p = cmds.add_parser("create-patch", help="Create patch"); _add_body_args(p)
    cmds.add_parser("list-attestation", help="List attestation policies")
    cmds.add_parser("list-deployment-policies", help="List deployment policies")

def _run_storage(args, client):
    svc = StorageService(client)
    cmd = args.command
    if cmd == "list-patches": return svc.query_patch_envelopes()
    if cmd == "get-patch": return svc.get_patch_envelope(args.id)
    if cmd == "create-patch": return svc.create_patch_envelope(_load_body(args) or {})
    if cmd == "list-attestation": return svc.query_attestation_policies()
    if cmd == "list-deployment-policies": return svc.query_deployment_policies()


def _register_orchestration(sub):
    svc = sub.add_parser("orchestration", help="Orchestration Service")
    cmds = svc.add_subparsers(dest="command", required=True)
    cmds.add_parser("list-clusters", help="List cluster instances")
    p = cmds.add_parser("get-cluster", help="Get cluster"); _add_id(p)
    p = cmds.add_parser("create-cluster", help="Create cluster"); _add_body_args(p)
    cmds.add_parser("list-datastreams", help="List data streams")
    cmds.add_parser("list-plugins", help="List plugins")
    cmds.add_parser("api-usage", help="API usage tracking")

def _run_orchestration(args, client):
    svc = OrchestrationService(client)
    cmd = args.command
    if cmd == "list-clusters": return svc.query_cluster_instances()
    if cmd == "get-cluster": return svc.get_cluster_instance(args.id)
    if cmd == "create-cluster": return svc.create_cluster_instance(_load_body(args) or {})
    if cmd == "list-datastreams": return svc.query_data_streams()
    if cmd == "list-plugins": return svc.query_plugins()
    if cmd == "api-usage": return svc.query_api_usage()


def _register_kubernetes(sub):
    svc = sub.add_parser("k8s", help="Kubernetes Service")
    cmds = svc.add_subparsers(dest="command", required=True)
    cmds.add_parser("list-deployments", help="List K8s deployments")
    cmds.add_parser("list-gitrepos", help="List GitOps repos")
    cmds.add_parser("list-helm-charts", help="List Helm charts")
    cmds.add_parser("list-helm-repos", help="List private Helm repos")
    cmds.add_parser("list-secrets", help="List K8s secrets")
    cmds.add_parser("list-zks", help="List ZKS instances")

def _run_kubernetes(args, client):
    svc = KubernetesService(client)
    cmd = args.command
    if cmd == "list-deployments": return svc.list_deployments()
    if cmd == "list-gitrepos": return svc.list_git_repos()
    if cmd == "list-helm-charts": return svc.list_helm_charts()
    if cmd == "list-helm-repos": return svc.list_private_repos()
    if cmd == "list-secrets": return svc.list_secrets()
    if cmd == "list-zks": return svc.list_zks_instances()


def _register_diag(sub):
    svc = sub.add_parser("diag", help="Diagnostics Service")
    cmds = svc.add_subparsers(dest="command", required=True)
    p = cmds.add_parser("device-config", help="Get device twin config"); _add_id(p)
    p = cmds.add_parser("device-bootstrap", help="Get bootstrap config"); _add_id(p)
    p = cmds.add_parser("device-next-config", help="Get next config"); _add_id(p)
    cmds.add_parser("events", help="Events timeline")
    cmds.add_parser("health", help="Cloud health check")

def _run_diag(args, client):
    svc = DiagService(client)
    cmd = args.command
    if cmd == "device-config": return svc.get_device_twin_config(args.id)
    if cmd == "device-bootstrap": return svc.get_device_twin_bootstrap_config(args.id)
    if cmd == "device-next-config": return svc.get_device_twin_next_config(args.id)
    if cmd == "events": return svc.get_events_timeline()
    if cmd == "health": return svc.check_cloud_health()


def _register_network(sub):
    svc = sub.add_parser("network", help="Network Service")
    cmds = svc.add_subparsers(dest="command", required=True)
    cmds.add_parser("list-networks", help="List networks")
    p = cmds.add_parser("get-network", help="Get network"); _add_id(p)
    p = cmds.add_parser("create-network", help="Create network"); _add_body_args(p)

def _run_network(args, client):
    svc = NetworkService(client)
    cmd = args.command
    if cmd == "list-networks": return svc.query_networks()
    if cmd == "get-network": return svc.get_network(args.id)
    if cmd == "create-network": return svc.create_network(_load_body(args) or {})


def _register_job(sub):
    svc = sub.add_parser("job", help="Job / Bulk Operations Service")
    cmds = svc.add_subparsers(dest="command", required=True)
    cmds.add_parser("list-jobs", help="List jobs")
    p = cmds.add_parser("get-job", help="Get job"); _add_id(p)
    p = cmds.add_parser("create-job", help="Create job"); _add_body_args(p)

def _run_job(args, client):
    svc = JobService(client)
    cmd = args.command
    if cmd == "list-jobs": return svc.query_jobs()
    if cmd == "get-job": return svc.get_job_by_id(args.id)
    if cmd == "create-job": return svc.create_job(_load_body(args) or {})


def _register_cluster(sub):
    svc = sub.add_parser("cluster", help="Edge Node Cluster Service")
    cmds = svc.add_subparsers(dest="command", required=True)
    cmds.add_parser("list-clusters", help="List edge node clusters")
    p = cmds.add_parser("get-cluster", help="Get cluster"); _add_id(p)
    p = cmds.add_parser("create-cluster", help="Create cluster"); _add_body_args(p)

def _run_cluster(args, client):
    svc = NodeClusterService(client)
    cmd = args.command
    if cmd == "list-clusters": return svc.query_edge_node_clusters()
    if cmd == "get-cluster": return svc.get_edge_node_cluster(args.id)
    if cmd == "create-cluster": return svc.create_edge_node_cluster(_load_body(args) or {})


def _register_app_profile(sub):
    svc = sub.add_parser("app-profile", help="App Profile / Policy Service")
    cmds = svc.add_subparsers(dest="command", required=True)
    cmds.add_parser("list-policies", help="List app policies")
    p = cmds.add_parser("get-policy", help="Get policy"); _add_id(p)
    p = cmds.add_parser("create-policy", help="Create policy"); _add_body_args(p)

def _run_app_profile(args, client):
    svc = AppProfileService(client)
    cmd = args.command
    if cmd == "list-policies": return svc.query_app_policies()
    if cmd == "get-policy": return svc.get_app_policy(args.id)
    if cmd == "create-policy": return svc.create_app_policy(_load_body(args) or {})


# ──────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────

SERVICE_REGISTRY = {
    "node": _run_node,
    "app": _run_app,
    "user": _run_user,
    "storage": _run_storage,
    "orchestration": _run_orchestration,
    "k8s": _run_kubernetes,
    "diag": _run_diag,
    "network": _run_network,
    "job": _run_job,
    "cluster": _run_cluster,
    "app-profile": _run_app_profile,
}


def main():
    parser = argparse.ArgumentParser(
        prog="zededa",
        description="ZEDEDA API CLI — Complete edge management skill",
    )
    sub = parser.add_subparsers(dest="service", required=True)

    _register_node(sub)
    _register_app(sub)
    _register_user(sub)
    _register_storage(sub)
    _register_orchestration(sub)
    _register_kubernetes(sub)
    _register_diag(sub)
    _register_network(sub)
    _register_job(sub)
    _register_cluster(sub)
    _register_app_profile(sub)

    args = parser.parse_args()

    try:
        client = ZededaClient()
        runner = SERVICE_REGISTRY[args.service]
        result = runner(args, client)
        if result is not None:
            _out(result)
    except ZededaError as exc:
        print(json.dumps(exc.to_dict(), indent=2), file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
