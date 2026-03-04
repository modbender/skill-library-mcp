# CapRover API Reference

Base URL: `https://<captain-domain>`
Auth header: `x-captain-auth: <token>`
All bodies: `Content-Type: application/json`
SSL: often self-signed → disable verification in HTTP clients

## Table of Contents
1. [Authentication](#authentication)
2. [App Management](#app-management)
3. [Deploy](#deploy)
4. [Logs](#logs)
5. [System / Cluster](#system--cluster)
6. [Docker Registry](#docker-registry)

---

## Authentication

### POST `/api/v2/login`
```json
Request:  { "password": "str" }
Response: { "status": 100, "data": { "token": "str" } }
```
Token is a JWT valid for the session. Always re-authenticate at script start.

---

## App Management

### GET `/api/v2/user/apps/appDefinitions`
Returns all apps and their current definitions.

```json
Response:
{
  "data": {
    "appDefinitions": [
      {
        "appName": "str",
        "imageName": "str",
        "instanceCount": 1,
        "ports": [{ "hostPort": 25565, "containerPort": 7777 }],
        "volumes": [{ "containerPath": "/data", "volumeName": "myapp-data" }],
        "envVars": [{ "key": "str", "value": "str" }],
        "serviceUpdateOverride": "json-string-or-empty",
        "hasPersistentData": false,
        "notExposeAsSubDomain": false,
        "customDomain": [],
        "deployedVersion": 3
      }
    ]
  }
}
```

### POST `/api/v2/user/apps/appDefinitions/register`
Create a new app.
```json
Request:  { "appName": "str", "hasPersistentData": false }
Response: { "status": 100, "description": "App created", "data": {} }
```

### POST `/api/v2/user/apps/appDefinitions/update`
Update app settings. All fields are optional — only provided fields are updated.

```json
Request:
{
  "appName": "str",                          // required
  "imageName": "str",                        // optional — pre-built image
  "instanceCount": 1,                        // optional
  "envVars": [{ "key": "str", "value": "str" }],   // optional — replaces all envvars
  "ports": [{ "hostPort": 25565, "containerPort": 7777 }],  // optional — ⚠️ may 500
  "volumes": [{ "containerPath": "/data", "volumeName": "myapp-data" }],  // optional
  "serviceUpdateOverride": "json-str",       // optional — raw Docker Swarm ServiceSpec fragment
  "notExposeAsSubDomain": false,             // optional
  "hasPersistentData": false,                // optional
  "forceSsl": false,                         // optional
  "websocketSupport": false,                 // optional
  "containerHttpPort": 80,                   // optional — for HTTP apps
  "description": "str"                       // optional
}
```

> ⚠️ Sending `"serviceUpdateOverride": ""` clears it completely, removing any Docker Swarm overrides (including volume mounts).

### POST `/api/v2/user/apps/appDefinitions/delete`
```json
Request:  { "appName": "str", "volumes": [] }
```
Pass volume names in `volumes` to also delete associated volumes.

---

## Deploy

### POST `/api/v2/user/apps/appData/<appName>` — Deploy from Dockerfile tar

Multipart form upload of a `.tar.gz` containing `captain-definition` + `Dockerfile` + files.

```
Content-Type: multipart/form-data; boundary=<boundary>
x-captain-auth: <token>

--<boundary>
Content-Disposition: form-data; name="sourceFile"; filename="app.tar.gz"
Content-Type: application/octet-stream

<binary tar data>
--<boundary>--
```

`captain-definition` (JSON file at tar root):
```json
{ "schemaVersion": 2, "dockerfilePath": "./Dockerfile" }
```

Response:
```json
{ "status": 100, "description": "Deploy is done", "data": {} }
```

Build logs appear immediately after in the build logs endpoint.

### POST `/api/v2/user/apps/appData/<appName>/redeploy`
Force redeploy of current image (no tar needed):
```json
Request:  { "appName": "str", "gitHash": "" }
```

---

## Logs

### GET `/api/v2/user/apps/appData/<appName>`
Build logs (from most recent deploy/build):
```json
Response:
{
  "data": {
    "logs": {
      "lines": ["Step 1/5 : FROM ...", "Successfully built ..."],
      "firstLineNumber": 0
    }
  }
}
```

### GET `/api/v2/user/apps/appData/<appName>/logs`
Runtime logs (Docker container stdout/stderr):
```json
Response: { "data": { "logs": "<raw-text-with-timestamps>" } }
```

Raw format: each line prefixed with a Docker log header byte + timestamp.
Strip control bytes: `re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw)`

---

## System / Cluster

### GET `/api/v2/user/system/info`
Cluster info, node list:
```json
{
  "data": {
    "nodes": [
      {
        "id": "n5ru6s7t5hv8q8cjx9vytw6lk",
        "hostname": "rodney",
        "role": "manager",
        "status": "Ready",
        "resources": {
          "nanoCpu": 4000000000,
          "memoryBytes": 24069836800
        }
      }
    ]
  }
}
```

### GET `/api/v2/user/system/info` also returns CapRover version, Docker version, etc.

---

## Docker Registry

### GET `/api/v2/user/registries`
List configured Docker registries.

### POST `/api/v2/user/registries`
Add a registry (Docker Hub, ECR, GCR, etc.):
```json
{
  "serverAddress": "registry.hub.docker.com",
  "username": "str",
  "password": "str",
  "registryDomain": "str"
}
```

---

## serviceUpdateOverride — Docker Swarm Service Spec

The `serviceUpdateOverride` field accepts a **JSON string** (not object) with a fragment of the Docker Service Spec. It is merged into the service spec at deploy time.

Common use cases:

### Named volume mounts
```json
{
  "TaskTemplate": {
    "ContainerSpec": {
      "Mounts": [
        {
          "Type": "volume",
          "Source": "captain--myapp-data",
          "Target": "/data"
        }
      ]
    }
  }
}
```

CapRover names volumes: `captain--<appname>-<volumename>` when created via the volumes API.
For manually created volumes, use the exact Docker volume name.

### Override container args / command
```json
{
  "TaskTemplate": {
    "ContainerSpec": {
      "Args": ["-worldname", "Terraria", "-autocreate", "3"]
    }
  }
}
```
> ⚠️ `Args` overrides CMD in the Dockerfile. `Command` overrides ENTRYPOINT.

### Publish ports (TCP/UDP — for non-HTTP services)
```json
{
  "EndpointSpec": {
    "Ports": [
      { "Protocol": "tcp", "PublishedPort": 25565, "TargetPort": 7777 }
    ]
  }
}
```
> ⚠️ This may return HTTP 500 from CapRover API (known bug). Prefer setting ports via the `ports` field at app creation time.

### Resource limits
```json
{
  "TaskTemplate": {
    "Resources": {
      "Limits": { "NanoCPUs": 2000000000, "MemoryBytes": 2147483648 }
    }
  }
}
```
