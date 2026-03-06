"""
Kubernetes executor for remediation actions.

Handles K8s operations like pod restart, scaling, rollback.
"""

from typing import Any, Dict, List, Optional

import structlog
from kubernetes import client, config
from kubernetes.client.rest import ApiException

from src.config.settings import get_settings

logger = structlog.get_logger()


class KubernetesExecutor:
    """
    Executor for Kubernetes remediation actions.

    Features:
    - Pod restart
    - HPA scaling
    - Deployment rollback
    - ConfigMap rollback
    """

    def __init__(self):
        self._core_api: client.Optional[CoreV1Api] = None
        self._apps_api: client.Optional[AppsV1Api] = None
        self._autoscaling_api: client.Optional[AutoscalingV1Api] = None
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
            self._apps_api = client.AppsV1Api()
            self._autoscaling_api = client.AutoscalingV1Api()
            self._connected = True
            return True
        except Exception as e:
            logger.error("Failed to connect to Kubernetes", error=str(e))
            return False

    async def restart_pod(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Restart a pod by deleting it (assumes controller will recreate).

        Target format: "pod/<pod-name>" or just "<pod-name>"
        """
        if not await self._ensure_connected():
            return {"success": False, "error": "Not connected to Kubernetes"}

        pod_name = target.replace("pod/", "")

        try:
            # Get current pod state for rollback data
            pod = self._core_api.read_namespaced_pod(pod_name, namespace)
            state_before = {
                "name": pod.metadata.name,
                "status": pod.status.phase,
                "restart_count": sum(
                    cs.restart_count
                    for cs in (pod.status.container_statuses or [])
                ),
            }

            # Delete the pod (controller will recreate)
            self._core_api.delete_namespaced_pod(
                pod_name,
                namespace,
                grace_period_seconds=parameters.get("grace_period", 30),
            )

            logger.info(
                "Pod deleted for restart",
                pod=pod_name,
                namespace=namespace,
            )

            return {
                "success": True,
                "state_before": state_before,
                "rollback_data": {"pod_name": pod_name},
            }

        except ApiException as e:
            logger.error(
                "Failed to restart pod",
                pod=pod_name,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def scale_hpa(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Scale an HPA min/max replicas.

        Target format: "hpa/<hpa-name>" or "deployment/<deployment-name>"
        """
        if not await self._ensure_connected():
            return {"success": False, "error": "Not connected to Kubernetes"}

        hpa_name = target.replace("hpa/", "").replace("deployment/", "")

        try:
            # Get current HPA
            hpa = self._autoscaling_api.read_namespaced_horizontal_pod_autoscaler(
                hpa_name, namespace
            )

            state_before = {
                "min_replicas": hpa.spec.min_replicas,
                "max_replicas": hpa.spec.max_replicas,
            }

            # Calculate new values
            scale_factor = parameters.get("scale_factor", 1.5)
            new_min = parameters.get(
                "min_replicas",
                int(hpa.spec.min_replicas * scale_factor),
            )
            new_max = parameters.get(
                "max_replicas",
                int(hpa.spec.max_replicas * scale_factor),
            )

            # Update HPA
            hpa.spec.min_replicas = new_min
            hpa.spec.max_replicas = max(new_max, new_min)

            self._autoscaling_api.patch_namespaced_horizontal_pod_autoscaler(
                hpa_name, namespace, hpa
            )

            logger.info(
                "HPA scaled",
                hpa=hpa_name,
                namespace=namespace,
                new_min=new_min,
                new_max=new_max,
            )

            return {
                "success": True,
                "state_before": state_before,
                "state_after": {
                    "min_replicas": new_min,
                    "max_replicas": max(new_max, new_min),
                },
                "rollback_data": state_before,
            }

        except ApiException as e:
            logger.error(
                "Failed to scale HPA",
                hpa=hpa_name,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def rollback_deployment(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Rollback a deployment to previous revision.

        Target format: "deployment/<deployment-name>"
        """
        if not await self._ensure_connected():
            return {"success": False, "error": "Not connected to Kubernetes"}

        deployment_name = target.replace("deployment/", "")

        try:
            # Get current deployment
            deployment = self._apps_api.read_namespaced_deployment(
                deployment_name, namespace
            )

            current_revision = deployment.metadata.annotations.get(
                "deployment.kubernetes.io/revision", "0"
            )

            state_before = {
                "revision": current_revision,
                "image": deployment.spec.template.spec.containers[0].image
                if deployment.spec.template.spec.containers
                else None,
            }

            # Perform rollback using rollout undo
            # K8s client doesn't have direct rollout undo, so we patch
            target_revision = parameters.get("revision")
            if target_revision:
                # Get specific revision from ReplicaSet
                rs_list = self._apps_api.list_namespaced_replica_set(
                    namespace,
                    label_selector=f"app={deployment_name}",
                )

                for rs in rs_list.items:
                    rs_revision = rs.metadata.annotations.get(
                        "deployment.kubernetes.io/revision", ""
                    )
                    if rs_revision == str(target_revision):
                        # Found target revision, apply its spec
                        deployment.spec.template = rs.spec.template
                        break

            else:
                # Just restart pods by updating annotation
                if deployment.spec.template.metadata.annotations is None:
                    deployment.spec.template.metadata.annotations = {}
                deployment.spec.template.metadata.annotations[
                    "kubectl.kubernetes.io/restartedAt"
                ] = str(int(__import__("time").time()))

            self._apps_api.patch_namespaced_deployment(
                deployment_name, namespace, deployment
            )

            logger.info(
                "Deployment rollback initiated",
                deployment=deployment_name,
                namespace=namespace,
            )

            return {
                "success": True,
                "state_before": state_before,
                "rollback_data": {"previous_revision": current_revision},
            }

        except ApiException as e:
            logger.error(
                "Failed to rollback deployment",
                deployment=deployment_name,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def rollback_configmap(
        self,
        target: str,
        namespace: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Rollback a ConfigMap to previous version.

        Note: K8s doesn't version ConfigMaps, so this needs external state.
        """
        if not await self._ensure_connected():
            return {"success": False, "error": "Not connected to Kubernetes"}

        configmap_name = target.replace("configmap/", "")

        # ConfigMap rollback requires the previous data to be provided
        previous_data = parameters.get("previous_data")
        if not previous_data:
            return {
                "success": False,
                "error": "No previous_data provided for ConfigMap rollback",
            }

        try:
            configmap = self._core_api.read_namespaced_config_map(
                configmap_name, namespace
            )

            state_before = {"data": dict(configmap.data or {})}

            # Apply previous data
            configmap.data = previous_data

            self._core_api.patch_namespaced_config_map(
                configmap_name, namespace, configmap
            )

            logger.info(
                "ConfigMap rolled back",
                configmap=configmap_name,
                namespace=namespace,
            )

            return {
                "success": True,
                "state_before": state_before,
                "rollback_data": {"previous_data": state_before["data"]},
            }

        except ApiException as e:
            logger.error(
                "Failed to rollback ConfigMap",
                configmap=configmap_name,
                error=str(e),
            )
            return {"success": False, "error": str(e)}

    async def _ensure_connected(self) -> bool:
        """Ensure we're connected to Kubernetes."""
        if not self._connected:
            return await self.connect()
        return True
