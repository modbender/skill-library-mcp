# SurrealDB Deployment and Operations Guide

This document covers installation, deployment patterns, operational tasks, and monitoring for SurrealDB 3.0.0 across local development, containerized, orchestrated, and cloud environments.

---

## Local Development

### Installation

```bash
# macOS (Homebrew) -- RECOMMENDED
brew install surrealdb/tap/surreal

# Linux (apt / package manager)
# See https://surrealdb.com/docs/surrealdb/installation for distro-specific instructions

# Docker (no host install required)
docker pull surrealdb/surrealdb:v3

# Verify installation
surreal version
```

> **Security note**: SurrealDB's website offers a `curl | sh` installer. For
> auditable installs, prefer your OS package manager (brew, apt, dnf) or Docker.
> If you must use a remote installer, download the script first, review it, then
> execute: `curl -sSf https://install.surrealdb.com -o install.sh && less install.sh && sh install.sh`

### Starting the Server

> **Credential warning**: Examples below use `root/root` for local development.
> For production, use strong credentials and DEFINE USER with least-privilege access.

```bash
# In-memory (data lost on restart, LOCAL DEVELOPMENT ONLY)
surreal start --log trace --user root --pass root memory

# RocksDB persistent storage (local dev)
surreal start --log info --user root --pass root rocksdb:./mydata.db

# SurrealKV persistent storage
surreal start --log info --user root --pass root surrealkv:./mydata.db

# SurrealKV with versioned storage (supports temporal queries)
surreal start --log info --user root --pass root surrealkv+versioned:./mydata.db

# TiKV distributed storage
surreal start --log info --user root --pass root tikv://pd0:2379

# Custom bind address and port (use 127.0.0.1 for local dev, 0.0.0.0 only in containers)
surreal start --bind 127.0.0.1:9000 --user root --pass root memory

# With TLS
surreal start --user root --pass root \
  --web-crt ./cert.pem --web-key ./key.pem \
  memory
```

### CLI Operations

```bash
# Interactive SQL shell
surreal sql \
  --endpoint http://localhost:8000 \
  --username root \
  --password root \
  --namespace test \
  --database test

# Import data from a .surql file
surreal import \
  --endpoint http://localhost:8000 \
  --username root \
  --password root \
  --namespace test \
  --database test \
  data.surql

# Export database to a .surql file
surreal export \
  --endpoint http://localhost:8000 \
  --username root \
  --password root \
  --namespace test \
  --database test \
  > backup.surql

# Check version
surreal version

# Validate a SurrealQL file
surreal validate myfile.surql

# Upgrade storage from v1 to v2 format
surreal upgrade --path ./mydata.db
```

### Configuration Flags Reference

| Flag | Description | Default |
|------|-------------|---------|
| `--bind` | Listen address and port | `0.0.0.0:8000` (use `127.0.0.1:8000` for local dev) |
| `--log` | Log level (none, full, error, warn, info, debug, trace) | `info` |
| `--user` | Root username | Required |
| `--pass` | Root password | Required |
| `--strict` | Strict mode (require explicit namespace/database) | `false` |
| `--web-crt` | Path to TLS certificate | None |
| `--web-key` | Path to TLS private key | None |
| `--client-crt` | Path to client CA certificate (mTLS) | None |
| `--client-key` | Path to client key (mTLS) | None |
| `--no-banner` | Hide startup banner | `false` |
| `--query-timeout` | Maximum query execution time | None |
| `--transaction-timeout` | Maximum transaction duration | None |

---

## Docker Deployment

### Basic Docker Run

```bash
# In-memory
docker run --rm -p 8000:8000 \
  surrealdb/surrealdb:v3 \
  start --log info --user root --pass root memory

# With persistent volume
docker run --rm -p 8000:8000 \
  -v $(pwd)/data:/data \
  surrealdb/surrealdb:v3 \
  start --log info --user root --pass root rocksdb:/data/mydb
```

### Dockerfile

```dockerfile
FROM surrealdb/surrealdb:v3

# Default environment variables
ENV SURREAL_LOG=info
ENV SURREAL_USER=root
ENV SURREAL_PASS=root
ENV SURREAL_BIND=0.0.0.0:8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD surreal version || exit 1

EXPOSE 8000

CMD ["start", "--log", "info", "--user", "root", "--pass", "root", "surrealkv:/data/db"]
```

### Docker Compose -- Single Node

```yaml
version: "3.8"

services:
  surrealdb:
    image: surrealdb/surrealdb:v3
    command: start --log info --user root --pass root surrealkv:/data/db
    ports:
      - "8000:8000"
    volumes:
      - surrealdb-data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "surreal", "version"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 4G
        reservations:
          cpus: "0.5"
          memory: 1G

volumes:
  surrealdb-data:
    driver: local
```

### Docker Compose -- TiKV Cluster

```yaml
version: "3.8"

services:
  pd0:
    image: pingcap/pd:latest
    command:
      - --name=pd0
      - --client-urls=http://0.0.0.0:2379
      - --peer-urls=http://0.0.0.0:2380
      - --advertise-client-urls=http://pd0:2379
      - --advertise-peer-urls=http://pd0:2380
      - --initial-cluster=pd0=http://pd0:2380
      - --data-dir=/data/pd0
    volumes:
      - pd0-data:/data
    ports:
      - "2379:2379"

  tikv0:
    image: pingcap/tikv:latest
    command:
      - --addr=0.0.0.0:20160
      - --advertise-addr=tikv0:20160
      - --pd=pd0:2379
      - --data-dir=/data/tikv0
    volumes:
      - tikv0-data:/data
    depends_on:
      - pd0

  tikv1:
    image: pingcap/tikv:latest
    command:
      - --addr=0.0.0.0:20160
      - --advertise-addr=tikv1:20160
      - --pd=pd0:2379
      - --data-dir=/data/tikv1
    volumes:
      - tikv1-data:/data
    depends_on:
      - pd0

  tikv2:
    image: pingcap/tikv:latest
    command:
      - --addr=0.0.0.0:20160
      - --advertise-addr=tikv2:20160
      - --pd=pd0:2379
      - --data-dir=/data/tikv2
    volumes:
      - tikv2-data:/data
    depends_on:
      - pd0

  surrealdb:
    image: surrealdb/surrealdb:v3
    command: start --log info --user root --pass root tikv://pd0:2379
    ports:
      - "8000:8000"
    depends_on:
      - tikv0
      - tikv1
      - tikv2
    restart: unless-stopped

volumes:
  pd0-data:
  tikv0-data:
  tikv1-data:
  tikv2-data:
```

---

## Kubernetes Deployment

### Helm Chart (Single Node with SurrealKV)

```yaml
# values.yaml
replicaCount: 1

image:
  repository: surrealdb/surrealdb
  tag: v3.0.0
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8000

storage:
  engine: surrealkv
  size: 50Gi
  storageClass: standard

auth:
  rootUsername: root
  rootPassword: ""  # Set via secret
  existingSecret: surrealdb-auth

resources:
  limits:
    cpu: "4"
    memory: 8Gi
  requests:
    cpu: "1"
    memory: 2Gi

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: surrealdb.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: surrealdb-tls
      hosts:
        - surrealdb.example.com
```

### StatefulSet for Persistent Storage

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: surrealdb
  labels:
    app: surrealdb
spec:
  serviceName: surrealdb
  replicas: 1
  selector:
    matchLabels:
      app: surrealdb
  template:
    metadata:
      labels:
        app: surrealdb
    spec:
      containers:
        - name: surrealdb
          image: surrealdb/surrealdb:v3
          args:
            - start
            - --log
            - info
            - --user
            - $(SURREAL_USER)
            - --pass
            - $(SURREAL_PASS)
            - surrealkv:/data/db
          ports:
            - containerPort: 8000
              name: http
          envFrom:
            - secretRef:
                name: surrealdb-auth
          volumeMounts:
            - name: data
              mountPath: /data
          resources:
            limits:
              cpu: "4"
              memory: 8Gi
            requests:
              cpu: "1"
              memory: 2Gi
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: standard
        resources:
          requests:
            storage: 50Gi
```

### Deployment for Stateless Compute (TiKV Backend)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: surrealdb
spec:
  replicas: 3
  selector:
    matchLabels:
      app: surrealdb
  template:
    metadata:
      labels:
        app: surrealdb
    spec:
      containers:
        - name: surrealdb
          image: surrealdb/surrealdb:v3
          args:
            - start
            - --log
            - info
            - --user
            - $(SURREAL_USER)
            - --pass
            - $(SURREAL_PASS)
            - tikv://tikv-pd:2379
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: surrealdb-auth
          resources:
            limits:
              cpu: "2"
              memory: 4Gi
            requests:
              cpu: "500m"
              memory: 1Gi
```

### Service and Ingress

```yaml
apiVersion: v1
kind: Service
metadata:
  name: surrealdb
spec:
  type: ClusterIP
  ports:
    - port: 8000
      targetPort: 8000
      protocol: TCP
      name: http
  selector:
    app: surrealdb
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: surrealdb
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
    nginx.ingress.kubernetes.io/websocket-services: surrealdb
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - surrealdb.example.com
      secretName: surrealdb-tls
  rules:
    - host: surrealdb.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: surrealdb
                port:
                  number: 8000
```

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: surrealdb
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: surrealdb
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## Distributed Deployment (TiKV)

TiKV provides distributed, transactional key-value storage for SurrealDB. In this architecture, SurrealDB compute nodes are stateless and connect to a shared TiKV cluster.

### Architecture

```
                    Load Balancer
                    /     |     \
            SurrealDB  SurrealDB  SurrealDB
            (compute)  (compute)  (compute)
                    \     |     /
                     TiKV Cluster
                    /     |     \
              TiKV-0   TiKV-1   TiKV-2
                    \     |     /
                   PD (Placement Driver)
                   /       |       \
                PD-0     PD-1     PD-2
```

### Component Configuration

**Placement Driver (PD)** -- manages cluster metadata and scheduling:

```bash
pd-server \
  --name=pd0 \
  --data-dir=/var/lib/pd \
  --client-urls=http://0.0.0.0:2379 \
  --peer-urls=http://0.0.0.0:2380 \
  --advertise-client-urls=http://pd0:2379 \
  --advertise-peer-urls=http://pd0:2380 \
  --initial-cluster="pd0=http://pd0:2380,pd1=http://pd1:2380,pd2=http://pd2:2380"
```

**TiKV Nodes** -- store data:

```bash
tikv-server \
  --addr=0.0.0.0:20160 \
  --advertise-addr=tikv0:20160 \
  --data-dir=/var/lib/tikv \
  --pd=pd0:2379,pd1:2379,pd2:2379
```

**SurrealDB Compute Nodes** -- stateless query processing:

```bash
surreal start \
  --log info \
  --user root \
  --pass root \
  --bind 0.0.0.0:8000 \
  tikv://pd0:2379,pd1:2379,pd2:2379
```

### Fault Tolerance

TiKV uses Raft consensus and maintains 3 replicas by default. The cluster can tolerate `replicas - 1` failures (1 failure with 3 replicas). Since SurrealDB compute nodes are stateless, they can be freely added or removed without data implications.

### Network Topology Considerations

- PD nodes communicate on port 2379 (client) and 2380 (peer)
- TiKV nodes communicate on port 20160
- SurrealDB nodes need access to PD nodes only (not directly to TiKV)
- Place TiKV nodes in the same datacenter for low latency
- For cross-region, configure TiKV placement rules to control replica locations

---

## Cloud Deployment

### SurrealDB Cloud (Managed Service)

SurrealDB Cloud is the managed database service available at app.surrealdb.com. It provides:

- Provisioning via web console or API
- Automatic backups
- Scaling controls
- Monitoring dashboard
- No infrastructure management

Connect using standard SDK connection strings with the provided cloud endpoint.

### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name surrealdb-cluster \
  --region us-east-1 \
  --nodegroup-name standard \
  --node-type m5.xlarge \
  --nodes 3

# Install SurrealDB using Kubernetes manifests or Helm
kubectl apply -f surrealdb-statefulset.yaml
```

Use `gp3` storage class for EBS-backed persistent volumes. For TiKV deployments, use the TiKV Operator for Kubernetes.

### Google GKE

```bash
# Create GKE cluster
gcloud container clusters create surrealdb-cluster \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n2-standard-4

# Deploy SurrealDB
kubectl apply -f surrealdb-statefulset.yaml
```

Use `standard-rwo` storage class for SSD-backed persistent volumes on GKE.

### Azure AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group surrealdb-rg \
  --name surrealdb-cluster \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --generate-ssh-keys

# Deploy SurrealDB
kubectl apply -f surrealdb-statefulset.yaml
```

Use `managed-premium` storage class for premium SSD volumes on AKS.

---

## Operational Tasks

### Backup and Restore

```bash
# Export a database (backup)
surreal export \
  --endpoint http://localhost:8000 \
  --username root \
  --password root \
  --namespace production \
  --database app \
  > backup_$(date +%Y%m%d_%H%M%S).surql

# Import a database (restore)
surreal import \
  --endpoint http://localhost:8000 \
  --username root \
  --password root \
  --namespace production \
  --database app \
  backup_20260219_120000.surql
```

For automated backups, create a cron job or Kubernetes CronJob:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: surrealdb-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: surrealdb/surrealdb:v3
              command:
                - /bin/sh
                - -c
                - |
                  surreal export \
                    --endpoint http://surrealdb:8000 \
                    --username $SURREAL_USER \
                    --password $SURREAL_PASS \
                    --namespace production \
                    --database app \
                    > /backups/backup_$(date +%Y%m%d_%H%M%S).surql
              envFrom:
                - secretRef:
                    name: surrealdb-auth
              volumeMounts:
                - name: backup-storage
                  mountPath: /backups
          volumes:
            - name: backup-storage
              persistentVolumeClaim:
                claimName: backup-pvc
          restartPolicy: OnFailure
```

### Version Upgrades

When upgrading from SurrealDB v2 to v3:

1. Export data from v2 instance using `surreal export`.
2. Stop the v2 server.
3. Start the v3 server.
4. Import data using `surreal import`.
5. Test thoroughly in a staging environment first.

For storage format upgrades:

```bash
surreal upgrade --path ./mydata.db
```

### TLS/SSL Configuration

```bash
# Server-side TLS
surreal start \
  --web-crt /etc/ssl/surrealdb/cert.pem \
  --web-key /etc/ssl/surrealdb/key.pem \
  --user root --pass root \
  surrealkv:/data/db

# Mutual TLS (mTLS)
surreal start \
  --web-crt /etc/ssl/surrealdb/cert.pem \
  --web-key /etc/ssl/surrealdb/key.pem \
  --client-crt /etc/ssl/surrealdb/ca.pem \
  --client-key /etc/ssl/surrealdb/client-key.pem \
  --user root --pass root \
  surrealkv:/data/db
```

### Log Management

```bash
# Log levels (from least to most verbose)
# none -> full -> error -> warn -> info -> debug -> trace

# Production (standard)
surreal start --log info ...

# Debugging
surreal start --log debug ...

# Full trace (development only, very verbose)
surreal start --log trace ...
```

---

## High Availability

### Stateless Compute with TiKV

For high availability, deploy SurrealDB as stateless compute nodes backed by a TiKV cluster:

1. Run 3+ PD nodes for metadata HA.
2. Run 3+ TiKV nodes for data HA (Raft replication).
3. Run 2+ SurrealDB compute nodes behind a load balancer.
4. SurrealDB nodes can be added/removed without affecting data.

### Load Balancer Configuration

Place a load balancer (NGINX, HAProxy, cloud LB) in front of SurrealDB compute nodes:

```nginx
# NGINX configuration for SurrealDB
upstream surrealdb {
    server surrealdb-0:8000;
    server surrealdb-1:8000;
    server surrealdb-2:8000;
}

server {
    listen 443 ssl;
    server_name surrealdb.example.com;

    ssl_certificate /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    location / {
        proxy_pass http://surrealdb;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 3600s;
        proxy_send_timeout 3600s;
    }
}
```

The `Upgrade` and `Connection` headers are required for WebSocket support.

### Health Check Endpoints

SurrealDB exposes a `/health` endpoint for load balancers and orchestration health checks. Use this endpoint in your liveness and readiness probes.

### Failover Procedures

With TiKV:
- If a TiKV node fails, Raft automatically promotes a replica. No manual intervention needed for single-node failures.
- If a SurrealDB compute node fails, the load balancer routes traffic to healthy nodes. Replace the failed node.
- If a PD node fails, remaining PD nodes continue operation (quorum-based).

---

## Monitoring

### Prometheus Metrics

SurrealDB exposes metrics in Prometheus format. Configure Prometheus to scrape the metrics endpoint:

```yaml
# prometheus.yml
scrape_configs:
  - job_name: "surrealdb"
    static_configs:
      - targets:
          - "surrealdb-0:8000"
          - "surrealdb-1:8000"
          - "surrealdb-2:8000"
    metrics_path: /metrics
    scrape_interval: 15s
```

### Grafana Dashboard

Create dashboards tracking:
- Query throughput (queries per second)
- Query latency (p50, p95, p99)
- Active connections (WebSocket and HTTP)
- Memory usage
- CPU utilization
- Storage size and growth rate
- Error rates by type
- Live query subscription count

### Alert Configuration

Set alerts for:
- Query latency exceeding thresholds (e.g., p99 > 500ms)
- Error rate spikes (> 1% of requests)
- Memory usage above 80% of limit
- Disk usage above 85% of capacity
- No healthy instances (all health checks failing)
- TiKV replication lag (if using distributed storage)

### Performance Baselines

Establish baselines during normal operation and alert on deviations:
- Average query latency under normal load
- Typical memory and CPU utilization
- Normal connection count ranges
- Expected query throughput
