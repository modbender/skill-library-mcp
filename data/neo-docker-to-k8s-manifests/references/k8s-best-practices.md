# Kubernetes Best Practices for Docker-to-K8s Conversion

## Resource Management

- Always set resource requests AND limits on every container
- Requests should be set to typical usage; limits to burst capacity
- Use LimitRange objects to enforce defaults at the namespace level
- Memory limits should be at least 1.5x memory requests for JVM-based apps
- CPU requests should reflect average usage, not peak

### Heuristics by Application Type

| Type | CPU Request | CPU Limit | Memory Request | Memory Limit |
|------|------------|-----------|----------------|--------------|
| Node.js | 100m | 500m | 128Mi | 512Mi |
| Python | 100m | 500m | 128Mi | 512Mi |
| Go | 50m | 300m | 64Mi | 256Mi |
| Java | 250m | 1000m | 512Mi | 1024Mi |
| .NET | 200m | 800m | 256Mi | 768Mi |
| Nginx | 50m | 200m | 32Mi | 128Mi |

## Health Checks

### Liveness Probe
- Detects deadlocked or unresponsive containers
- Should check internal state, NOT external dependencies
- Use HTTP GET for web apps, TCP socket for non-HTTP, exec for everything else

### Readiness Probe
- Determines if the container can accept traffic
- CAN check external dependencies (database, cache)
- Should return unhealthy during warm-up phase

### Startup Probe
- For slow-starting containers (e.g., Java/Spring)
- Prevents liveness probe from killing the container during startup
- failureThreshold * periodSeconds = maximum startup time

## Security

- Run containers as non-root (`runAsNonRoot: true`)
- Use read-only root filesystem when possible
- Drop all capabilities, add only what's needed
- Set `allowPrivilegeEscalation: false`
- Use `seccompProfile: RuntimeDefault`

## Networking

- Use ClusterIP services by default
- Use Ingress for HTTP traffic routing
- Set proper port names for Istio/service mesh compatibility

## Labels and Annotations

- Always set `app` label for service selectors
- Use standard Kubernetes labels: `app.kubernetes.io/name`, `app.kubernetes.io/version`
- Add annotations for monitoring, logging, and ingress configuration

## Volumes

- Convert Docker named volumes to PersistentVolumeClaims
- Convert bind mounts to ConfigMaps or Secrets where appropriate
- Use `ReadWriteOnce` access mode by default
- Consider `ReadOnlyMany` for shared static content
