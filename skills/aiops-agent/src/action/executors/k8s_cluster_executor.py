"""
Kubernetes cluster-level executor for node and infrastructure operations.

Supports:
- Node cordon/uncordon
- Node drain
- PVC expansion
- PVC snapshots
- Network policy management
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from src.config.settings import get_settings

logger = structlog.get_logger()


class K8sClusterExecutor:
    """
    Executor for Kubernetes cluster-level operations.

    Features:
    - Node cordon/uncordon for maintenance
    - Node drain with configurable options
    - PVC expansion (StorageClass must support it)
    - PVC snapshots (requires VolumeSnapshot CRD)
    - Network policy management
    """

    def __init__(self):
        settings = get_settings()
        self._drain_timeout = settings.k8s_cluster.drain_timeout_seconds
        self._drain_grace_period = settings.k8s_cluster.drain_grace_period
        self._ignore_daemonsets = settings.k8s_cluster.ignore_daemonsets
        self._delete_emptydir = settings.k8s_cluster.delete_emptydir_data
        self._force_drain = settings.k8s_cluster.force_drain

        self._core_api: Optional[client.CoreV1Api] = None
        self._networking_api: Optional[client.NetworkingV1Api] = None
        self._snapshot_api = None  # VolumeSnapshot API
        self._connected = False

    async def connect(self) -> bool:
        """Connect to Kubernetes API."""
        try:
            settings = get_settings()
            if settings.kubernetes.in_cluster:
                config.load_incluster_config()
            else:
                config.load_kube_config(config_file=settings.kubernetes.kubeconfig)

            self._core_api = client.CoreV1Api()
            self._networking_api = client.NetworkingV1Api()

            # Try to initialize snapshot API (optional)
            try:
                self._snapshot_api = client.CustomObjectsApi()
            except Exception:
                logger.warning("VolumeSnapshot API not available")

            self._connected = True
            logger.info("K8s cluster executor connected")
            return True

        except Exception as e:
            logger.error("Failed to connect to Kubernetes", error=str(e))
            return False

    async def _ensure_connected(self) -> bool:
        """Ensure connection to Kubernetes."""
        if not self._connected:
            return await self.connect()
        return True

    async def cordon_node(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Cordon a node (mark as unschedulable).

        Target format: "node/<name>" or just "<name>"

        Parameters:
            None required

        Returns:
            Execution result with previous state for rollback
        """
        if not await self._ensure_connected():
            return {"success": False, "error": "Not connected to Kubernetes"}

        node_name = target.replace("node/", "")

        try:
            # Get current node state
            node = self._core_api.read_node(node_name)
            state_before = {
                "name": node_name,
                "unschedulable": node.spec.unschedulable or False,
            }

            # Already cordoned?
            if node.spec.unschedulable:
                return {
                    "success": True,
                    "state_before": state_before,
                    "message": "Node already cordoned",
                    "rollback_data": state_before,
                }

            # Cordon the node
            body = {"spec": {"unschedulable": True}}
            self._core_api.patch_node(node_name, body)

            logger.info("Node cordoned", node=node_name)

            return {
                "success": True,
                "state_before": state_before,
                "state_after": {"unschedulable": True},
                "rollback_data": state_before,
            }

        except ApiException as e:
            logger.error("Failed to cordon node", node=node_name, error=str(e))
            return {"success": False, "error": str(e)}

    async def uncordon_node(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Uncordon a node (mark as schedulable).

        Target format: "node/<name>" or just "<name>"
        """
        if not await self._ensure_connected():
            return {"success": False, "error": "Not connected to Kubernetes"}

        node_name = target.replace("node/", "")

        try:
            # Get current node state
            node = self._core_api.read_node(node_name)
            state_before = {
                "name": node_name,
                "unschedulable": node.spec.unschedulable or False,
            }

            # Already schedulable?
            if not node.spec.unschedulable:
                return {
                    "success": True,
                    "state_before": state_before,
                    "message": "Node already schedulable",
                    "rollback_data": state_before,
                }

            # Uncordon the node
            body = {"spec": {"unschedulable": False}}
            self._core_api.patch_node(node_name, body)

            logger.info("Node uncordoned", node=node_name)

            return {
                "success": True,
                "state_before": state_before,
                "state_after": {"unschedulable": False},
                "rollback_data": state_before,
            }

        except ApiException as e:
            logger.error("Failed to uncordon node", node=node_name, error=str(e))
            return {"success": False, "error": str(e)}

    async def drain_node(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Drain a node (evict all pods and cordon).

        Target format: "node/<name>" or just "<name>"

        Parameters:
            grace_period: Grace period for pod deletion (default from settings)
            timeout: Drain timeout in seconds (default from settings)
            ignore_daemonsets: Ignore DaemonSet pods (default from settings)
            delete_emptydir_data: Delete pods with emptyDir (default from settings)
            force: Force drain (default from settings)
            dry_run: Just show what would be evicted

        Returns:
            Execution result with evicted pods list
        """
        if not await self._ensure_connected():
            return {"success": False, "error": "Not connected to Kubernetes"}

        node_name = target.replace("node/", "")

        # Parse parameters
        grace_period = parameters.get("grace_period", self._drain_grace_period)
        timeout = parameters.get("timeout", self._drain_timeout)
        ignore_daemonsets = parameters.get("ignore_daemonsets", self._ignore_daemonsets)
        delete_emptydir = parameters.get("delete_emptydir_data", self._delete_emptydir)
        force = parameters.get("force", self._force_drain)
        dry_run = parameters.get("dry_run", False)

        try:
            # First, cordon the node
            cordon_result = await self.cordon_node(target, namespace, {})
            if not cordon_result.get("success"):
                return cordon_result

            # List pods on node
            pods = self._core_api.list_pod_for_all_namespaces(
                field_selector=f"spec.nodeName={node_name}"
            )

            pods_to_evict = []
            pods_skipped = []

            for pod in pods.items:
                # Skip DaemonSet pods
                if ignore_daemonsets:
                    owner_refs = pod.metadata.owner_references or []
                    if any(ref.kind == "DaemonSet" for ref in owner_refs):
                        pods_skipped.append({
                            "name": pod.metadata.name,
                            "namespace": pod.metadata.namespace,
                            "reason": "DaemonSet",
                        })
                        continue

                # Check for local storage (emptyDir)
                has_emptydir = False
                for vol in pod.spec.volumes or []:
                    if vol.empty_dir:
                        has_emptydir = True
                        break

                if has_emptydir and not delete_emptydir:
                    pods_skipped.append({
                        "name": pod.metadata.name,
                        "namespace": pod.metadata.namespace,
                        "reason": "emptyDir volume",
                    })
                    if not force:
                        continue

                pods_to_evict.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                })

            if dry_run:
                was_cordoned = cordon_result.get("state_before", {}).get("unschedulable", False)
                return {
                    "success": True,
                    "dry_run": True,
                    "pods_to_evict": pods_to_evict,
                    "pods_skipped": pods_skipped,
                    "rollback_data": {"node": node_name, "was_cordoned": was_cordoned},
                }

            # Evict pods
            evicted_pods = []
            failed_pods = []

            for pod_info in pods_to_evict:
                try:
                    eviction = client.V1Eviction(
                        metadata=client.V1ObjectMeta(
                            name=pod_info["name"],
                            namespace=pod_info["namespace"],
                        ),
                        delete_options=client.V1DeleteOptions(
                            grace_period_seconds=grace_period,
                        ),
                    )
                    self._core_api.create_namespaced_pod_eviction(
                        pod_info["name"],
                        pod_info["namespace"],
                        eviction,
                    )
                    evicted_pods.append(pod_info)
                except ApiException as e:
                    if e.status == 429:  # Too many requests (PDB)
                        failed_pods.append({**pod_info, "reason": "PDB violation"})
                    else:
                        failed_pods.append({**pod_info, "reason": str(e)})

            # Wait for pods to be deleted (with timeout)
            if evicted_pods:
                await self._wait_for_pods_deleted(evicted_pods, timeout)

            logger.info(
                "Node drained",
                node=node_name,
                evicted=len(evicted_pods),
                failed=len(failed_pods),
                skipped=len(pods_skipped),
            )

            success = len(failed_pods) == 0

            return {
                "success": success,
                "evicted_pods": evicted_pods,
                "failed_pods": failed_pods,
                "skipped_pods": pods_skipped,
                "error": f"Failed to evict {len(failed_pods)} pods" if failed_pods else None,
                "rollback_data": {
                    "node": node_name,
                    "was_cordoned": cordon_result.get("state_before", {}).get("unschedulable", False),
                },
            }

        except Exception as e:
            logger.error("Failed to drain node", node=node_name, error=str(e))
            return {"success": False, "error": str(e)}

    async def _wait_for_pods_deleted(
        self,
        pods: List[Dict[str, str]],
        timeout: int,
    ) -> None:
        """Wait for pods to be deleted."""
        start_time = datetime.utcnow()

        while (datetime.utcnow() - start_time).seconds < timeout:
            remaining = []

            for pod_info in pods:
                try:
                    self._core_api.read_namespaced_pod(
                        pod_info["name"],
                        pod_info["namespace"],
                    )
                    remaining.append(pod_info)
                except ApiException as e:
                    if e.status != 404:
                        remaining.append(pod_info)

            if not remaining:
                return

            pods = remaining
            await asyncio.sleep(2)

        logger.warning(
            "Timeout waiting for pods to delete",
            remaining=len(pods),
        )

    async def expand_pvc(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Expand a PVC (requires StorageClass with allowVolumeExpansion).

        Target format: "pvc/<namespace>/<name>" or "pvc/<name>" (uses default namespace)

        Parameters:
            new_size: New size (e.g., "20Gi") - required
        """
        if not await self._ensure_connected():
            return {"success": False, "error": "Not connected to Kubernetes"}

        # Parse target
        parts = target.replace("pvc/", "").split("/")
        if len(parts) == 2:
            pvc_namespace, pvc_name = parts
        else:
            pvc_namespace = namespace or "default"
            pvc_name = parts[0]

        new_size = parameters.get("new_size")
        if not new_size:
            return {"success": False, "error": "new_size parameter required"}

        try:
            # Get current PVC
            pvc = self._core_api.read_namespaced_persistent_volume_claim(
                pvc_name, pvc_namespace
            )

            current_size = pvc.spec.resources.requests.get("storage", "0")
            state_before = {
                "name": pvc_name,
                "namespace": pvc_namespace,
                "size": current_size,
            }

            # Update PVC size
            pvc.spec.resources.requests["storage"] = new_size
            self._core_api.patch_namespaced_persistent_volume_claim(
                pvc_name, pvc_namespace, pvc
            )

            logger.info(
                "PVC expansion initiated",
                pvc=pvc_name,
                namespace=pvc_namespace,
                old_size=current_size,
                new_size=new_size,
            )

            return {
                "success": True,
                "state_before": state_before,
                "state_after": {"size": new_size},
                "rollback_data": state_before,  # Note: PVC shrinking is not supported
            }

        except ApiException as e:
            logger.error(
                "Failed to expand PVC",
                pvc=pvc_name,
                namespace=pvc_namespace,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def create_pvc_snapshot(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create a VolumeSnapshot for a PVC.

        Target format: "pvc/<namespace>/<name>" or "pvc/<name>"

        Parameters:
            snapshot_class: VolumeSnapshotClass name (optional)
            snapshot_name: Custom snapshot name (optional, auto-generated if not provided)
        """
        if not await self._ensure_connected():
            return {"success": False, "error": "Not connected to Kubernetes"}

        if not self._snapshot_api:
            return {"success": False, "error": "VolumeSnapshot API not available"}

        # Parse target
        parts = target.replace("pvc/", "").split("/")
        if len(parts) == 2:
            pvc_namespace, pvc_name = parts
        else:
            pvc_namespace = namespace or "default"
            pvc_name = parts[0]

        snapshot_class = parameters.get("snapshot_class")
        snapshot_name = parameters.get(
            "snapshot_name",
            f"{pvc_name}-snap-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        )

        try:
            # Create VolumeSnapshot
            snapshot = {
                "apiVersion": "snapshot.storage.k8s.io/v1",
                "kind": "VolumeSnapshot",
                "metadata": {
                    "name": snapshot_name,
                    "namespace": pvc_namespace,
                },
                "spec": {
                    "source": {
                        "persistentVolumeClaimName": pvc_name,
                    },
                },
            }

            if snapshot_class:
                snapshot["spec"]["volumeSnapshotClassName"] = snapshot_class

            self._snapshot_api.create_namespaced_custom_object(
                group="snapshot.storage.k8s.io",
                version="v1",
                namespace=pvc_namespace,
                plural="volumesnapshots",
                body=snapshot,
            )

            logger.info(
                "PVC snapshot created",
                pvc=pvc_name,
                snapshot=snapshot_name,
                namespace=pvc_namespace,
            )

            return {
                "success": True,
                "snapshot_name": snapshot_name,
                "pvc_name": pvc_name,
                "namespace": pvc_namespace,
                "rollback_data": {
                    "snapshot_name": snapshot_name,
                    "namespace": pvc_namespace,
                },
            }

        except ApiException as e:
            logger.error(
                "Failed to create PVC snapshot",
                pvc=pvc_name,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def apply_network_policy(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply a NetworkPolicy.

        Target format: "netpol/<namespace>/<name>" or "netpol/<name>"

        Parameters:
            policy_spec: Full NetworkPolicy spec (required)
        """
        if not await self._ensure_connected():
            return {"success": False, "error": "Not connected to Kubernetes"}

        # Parse target
        parts = target.replace("netpol/", "").replace("network_policy/", "").split("/")
        if len(parts) == 2:
            policy_namespace, policy_name = parts
        else:
            policy_namespace = namespace or "default"
            policy_name = parts[0]

        policy_spec = parameters.get("policy_spec")
        if not policy_spec:
            return {"success": False, "error": "policy_spec parameter required"}

        try:
            # Check if policy exists
            existing_policy = None
            try:
                existing_policy = self._networking_api.read_namespaced_network_policy(
                    policy_name, policy_namespace
                )
            except ApiException as e:
                if e.status != 404:
                    raise

            # Build NetworkPolicy object
            policy = client.V1NetworkPolicy(
                api_version="networking.k8s.io/v1",
                kind="NetworkPolicy",
                metadata=client.V1ObjectMeta(
                    name=policy_name,
                    namespace=policy_namespace,
                ),
                spec=policy_spec,
            )

            if existing_policy:
                # Update existing policy
                state_before = {
                    "name": policy_name,
                    "namespace": policy_namespace,
                    "spec": existing_policy.spec.to_dict(),
                }
                self._networking_api.replace_namespaced_network_policy(
                    policy_name, policy_namespace, policy
                )
                action = "updated"
            else:
                # Create new policy
                state_before = None
                self._networking_api.create_namespaced_network_policy(
                    policy_namespace, policy
                )
                action = "created"

            logger.info(
                f"NetworkPolicy {action}",
                name=policy_name,
                namespace=policy_namespace,
            )

            return {
                "success": True,
                "action": action,
                "state_before": state_before,
                "rollback_data": {
                    "name": policy_name,
                    "namespace": policy_namespace,
                    "previous_spec": state_before.get("spec") if state_before else None,
                    "was_new": existing_policy is None,
                },
            }

        except ApiException as e:
            logger.error(
                "Failed to apply NetworkPolicy",
                name=policy_name,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def remove_network_policy(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Remove a NetworkPolicy.

        Target format: "netpol/<namespace>/<name>" or "netpol/<name>"
        """
        if not await self._ensure_connected():
            return {"success": False, "error": "Not connected to Kubernetes"}

        # Parse target
        parts = target.replace("netpol/", "").replace("network_policy/", "").split("/")
        if len(parts) == 2:
            policy_namespace, policy_name = parts
        else:
            policy_namespace = namespace or "default"
            policy_name = parts[0]

        try:
            # Get current policy for rollback
            policy = self._networking_api.read_namespaced_network_policy(
                policy_name, policy_namespace
            )
            state_before = {
                "name": policy_name,
                "namespace": policy_namespace,
                "spec": policy.spec.to_dict(),
            }

            # Delete the policy
            self._networking_api.delete_namespaced_network_policy(
                policy_name, policy_namespace
            )

            logger.info(
                "NetworkPolicy removed",
                name=policy_name,
                namespace=policy_namespace,
            )

            return {
                "success": True,
                "state_before": state_before,
                "rollback_data": state_before,
            }

        except ApiException as e:
            if e.status == 404:
                return {
                    "success": True,
                    "message": "NetworkPolicy not found",
                }
            logger.error(
                "Failed to remove NetworkPolicy",
                name=policy_name,
                error=str(e),
            )
            return {"success": False, "error": str(e)}
