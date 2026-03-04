# Kubernetes Manifest Generator

Step-by-step guidance for creating production-ready Kubernetes manifests including Deployments, Services, ConfigMaps, Secrets, and PersistentVolumeClaims following cloud-native best practices.

## What's Inside

- Requirements gathering workflow (workload type, image, ports, storage, scaling)
- Deployment manifest creation with best practices
- Service configuration (ClusterIP, LoadBalancer)
- ConfigMap and Secret generation
- PersistentVolumeClaim templates
- Security best practices (non-root, capability drops, seccomp profiles)
- Standard labels and annotations
- Multi-resource manifest organization (single file, separate files, Kustomize)
- Validation and testing checklist
- Common patterns (stateless web app, stateful database, background jobs, multi-container pods)
- Troubleshooting guide

## When to Use

- Creating new Kubernetes Deployment manifests
- Defining Service resources for network connectivity
- Generating ConfigMap and Secret resources
- Creating PersistentVolumeClaim manifests for stateful workloads
- Following Kubernetes best practices and naming conventions
- Implementing resource limits, health checks, and security contexts
- Designing manifests for multi-environment deployments

## Installation

```bash
npx add https://github.com/wpank/ai/tree/main/skills/devops/kubernetes/k8s-manifest-generator
```

### Manual Installation

#### Cursor (per-project)

From your project root:

```bash
mkdir -p .cursor/skills
cp -r ~/.ai-skills/skills/devops/kubernetes/k8s-manifest-generator .cursor/skills/k8s-manifest-generator
```

#### Cursor (global)

```bash
mkdir -p ~/.cursor/skills
cp -r ~/.ai-skills/skills/devops/kubernetes/k8s-manifest-generator ~/.cursor/skills/k8s-manifest-generator
```

#### Claude Code (per-project)

From your project root:

```bash
mkdir -p .claude/skills
cp -r ~/.ai-skills/skills/devops/kubernetes/k8s-manifest-generator .claude/skills/k8s-manifest-generator
```

#### Claude Code (global)

```bash
mkdir -p ~/.claude/skills
cp -r ~/.ai-skills/skills/devops/kubernetes/k8s-manifest-generator ~/.claude/skills/k8s-manifest-generator
```

## Related Skills

- [kubernetes](../) — Comprehensive Kubernetes resource reference
- [docker](../../docker/) — Container builds for Kubernetes deployments

---

Part of the [DevOps](../..) skill category.
