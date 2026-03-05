# Index

| API | Line |
|-----|------|
| Supabase | 2 |
| Firebase | 115 |
| PlanetScale | 216 |
| Neon | 285 |
| Upstash | 355 |
| MongoDB Atlas | 425 |
| Fauna | 509 |
| Xata | 593 |
| Convex | 678 |
| Appwrite | 749 |

---

# Supabase

## Base URL
```
https://{project-ref}.supabase.co
```

## Authentication
```bash
# For database operations
curl https://{project-ref}.supabase.co/rest/v1/todos \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /rest/v1/:table | GET | Select rows |
| /rest/v1/:table | POST | Insert rows |
| /rest/v1/:table | PATCH | Update rows |
| /rest/v1/:table | DELETE | Delete rows |
| /auth/v1/signup | POST | Sign up user |
| /auth/v1/token | POST | Sign in user |
| /storage/v1/object/:bucket/:path | POST | Upload file |

## Database Examples

### Select Rows
```bash
curl "https://{ref}.supabase.co/rest/v1/todos?select=*" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY"
```

### Select with Filter
```bash
curl "https://{ref}.supabase.co/rest/v1/todos?status=eq.done&select=id,title" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY"
```

### Insert Row
```bash
curl -X POST "https://{ref}.supabase.co/rest/v1/todos" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"title": "New task", "status": "pending"}'
```

### Update Row
```bash
curl -X PATCH "https://{ref}.supabase.co/rest/v1/todos?id=eq.1" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

### Delete Row
```bash
curl -X DELETE "https://{ref}.supabase.co/rest/v1/todos?id=eq.1" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Authorization: Bearer $SUPABASE_KEY"
```

## Filter Operators

| Operator | Example | Meaning |
|----------|---------|---------|
| eq | `?status=eq.done` | Equals |
| neq | `?status=neq.done` | Not equals |
| gt, lt | `?age=gt.18` | Greater/less than |
| gte, lte | `?age=gte.18` | Greater/less or equal |
| like | `?name=like.*john*` | Pattern match |
| in | `?id=in.(1,2,3)` | In list |
| is | `?deleted=is.null` | Is null |

## Auth Examples

### Sign Up
```bash
curl -X POST "https://{ref}.supabase.co/auth/v1/signup" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Sign In
```bash
curl -X POST "https://{ref}.supabase.co/auth/v1/token?grant_type=password" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

## Common Traps

- Both apikey AND Authorization headers needed
- Use anon key for client, service_role for server
- Filter syntax is PostgREST: `column=operator.value`
- Add `Prefer: return=representation` to get inserted/updated data
- RLS (Row Level Security) affects what you can access

## Rate Limits

Depends on plan. Free tier: 500 requests/hour

## Official Docs
https://supabase.com/docs/reference/javascript/introduction
# Firebase

## Firestore REST API

### Base URL
```
https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents
```

### Authentication
```bash
curl "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/users" \
  -H "Authorization: Bearer $FIREBASE_TOKEN"
```

### Get Document
```bash
curl "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/users/user123" \
  -H "Authorization: Bearer $FIREBASE_TOKEN"
```

### Create Document
```bash
curl -X POST "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/users?documentId=user123" \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "name": {"stringValue": "John"},
      "age": {"integerValue": "30"},
      "active": {"booleanValue": true}
    }
  }'
```

### Update Document
```bash
curl -X PATCH "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents/users/user123?updateMask.fieldPaths=name" \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "fields": {
      "name": {"stringValue": "Jane"}
    }
  }'
```

### Query Documents
```bash
curl -X POST "https://firestore.googleapis.com/v1/projects/$PROJECT_ID/databases/(default)/documents:runQuery" \
  -H "Authorization: Bearer $FIREBASE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "structuredQuery": {
      "from": [{"collectionId": "users"}],
      "where": {
        "fieldFilter": {
          "field": {"fieldPath": "active"},
          "op": "EQUAL",
          "value": {"booleanValue": true}
        }
      }
    }
  }'
```

## Realtime Database REST API

### Base URL
```
https://{project}.firebaseio.com
```

### Get Data
```bash
curl "https://$PROJECT_ID.firebaseio.com/users/user123.json?auth=$FIREBASE_TOKEN"
```

### Set Data
```bash
curl -X PUT "https://$PROJECT_ID.firebaseio.com/users/user123.json?auth=$FIREBASE_TOKEN" \
  -d '{"name": "John", "age": 30}'
```

### Update Data
```bash
curl -X PATCH "https://$PROJECT_ID.firebaseio.com/users/user123.json?auth=$FIREBASE_TOKEN" \
  -d '{"age": 31}'
```

## Common Traps

- Firestore uses typed values (stringValue, integerValue, etc.)
- Realtime DB is simpler but less powerful
- Token can be Firebase ID token or service account
- Collection/document path is in the URL
- updateMask required for partial updates in Firestore

## Official Docs
- Firestore: https://firebase.google.com/docs/firestore/reference/rest
- Realtime DB: https://firebase.google.com/docs/database/rest/start
# PlanetScale

Serverless MySQL database platform with branching, deploy requests, and automatic scaling.

## Base URL
`https://api.planetscale.com/v1`

## Authentication
Service token authentication via `Authorization` header with format `SERVICE_TOKEN_ID:SERVICE_TOKEN`.

```bash
# Example auth
curl https://api.planetscale.com/v1/organizations \
  -H "Authorization: $SERVICE_TOKEN_ID:$SERVICE_TOKEN"
```

Create service tokens in Dashboard → Settings → Service tokens. The token is only shown once at creation.

## Core Endpoints

### List Organizations
```bash
curl https://api.planetscale.com/v1/organizations \
  -H "Authorization: $SERVICE_TOKEN_ID:$SERVICE_TOKEN"
```

### List Databases
```bash
curl https://api.planetscale.com/v1/organizations/{org}/databases \
  -H "Authorization: $SERVICE_TOKEN_ID:$SERVICE_TOKEN"
```

### Create Branch
```bash
curl -X POST https://api.planetscale.com/v1/organizations/{org}/databases/{db}/branches \
  -H "Authorization: $SERVICE_TOKEN_ID:$SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "feature-branch", "parent_branch": "main"}'
```

### Create Deploy Request
```bash
curl -X POST https://api.planetscale.com/v1/organizations/{org}/databases/{db}/deploy-requests \
  -H "Authorization: $SERVICE_TOKEN_ID:$SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"branch": "feature-branch", "into_branch": "main"}'
```

### Create Connection String (Password)
```bash
curl -X POST https://api.planetscale.com/v1/organizations/{org}/databases/{db}/branches/{branch}/passwords \
  -H "Authorization: $SERVICE_TOKEN_ID:$SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-connection", "role": "reader"}'
```

## Rate Limits
Not publicly documented. Standard API rate limiting applies.

## Gotchas
- API is for **management only** — does NOT provide direct database access (use connection strings or serverless driver)
- Service tokens require granular permissions (organization + database level)
- Token secret shown only once at creation — save it immediately
- OAuth also supported for user-level access (different from service tokens)

## Links
- [Docs](https://planetscale.com/docs/concepts/planetscale-api-oauth-applications)
- [API Reference](https://api-docs.planetscale.com/reference)
- [Service Tokens](https://planetscale.com/docs/api/reference/service-tokens)
# Neon

Serverless Postgres with branching, autoscaling, and instant provisioning.

## Base URL
`https://console.neon.tech/api/v2`

## Authentication
Bearer token via `Authorization` header. Create API keys in Neon Console → Account Settings → API keys.

```bash
# Example auth
curl https://console.neon.tech/api/v2/projects \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $NEON_API_KEY"
```

Three API key types: Personal (all your projects), Organization (team projects), Project-scoped (single project).

## Core Endpoints

### List Projects
```bash
curl https://console.neon.tech/api/v2/projects \
  -H "Authorization: Bearer $NEON_API_KEY"
```

### Create Project
```bash
curl -X POST https://console.neon.tech/api/v2/projects \
  -H "Authorization: Bearer $NEON_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"project": {"name": "my-project", "region_id": "aws-us-east-2"}}'
```

### Create Branch
```bash
curl -X POST https://console.neon.tech/api/v2/projects/{project_id}/branches \
  -H "Authorization: Bearer $NEON_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"branch": {"name": "dev-branch"}}'
```

### Get Connection URI
```bash
curl https://console.neon.tech/api/v2/projects/{project_id}/connection_uri \
  -H "Authorization: Bearer $NEON_API_KEY"
```

### Poll Operation Status
```bash
curl https://console.neon.tech/api/v2/projects/{project_id}/operations/{operation_id} \
  -H "Authorization: Bearer $NEON_API_KEY"
```

## Rate Limits
- **700 requests per minute** (~11/second)
- **40 requests per second** burst limit per route
- Returns HTTP 429 when exceeded

## Gotchas
- Many operations are **asynchronous** — response includes `operations` array with status
- Poll operation status before proceeding with dependent requests
- API key tokens shown only once — store securely
- Pagination uses cursor-based approach with `limit` and `cursor` params

## Links
- [Docs](https://neon.tech/docs/reference/api-reference)
- [API Reference](https://api-docs.neon.tech/reference/getting-started-with-neon-api)
- [OpenAPI Spec](https://neon.tech/api_spec/release/v2.json)
# Upstash

Serverless Redis and Kafka with REST API access.

## Base URL
Per-database URL from Upstash Console (e.g., `https://us1-merry-cat-32748.upstash.io`)

## Authentication
Bearer token via `Authorization` header. Get endpoint URL and token from Upstash Console → Database → REST API section.

```bash
# Example auth
curl https://us1-merry-cat-32748.upstash.io/set/foo/bar \
  -H "Authorization: Bearer $UPSTASH_TOKEN"
```

Alternative: Pass token as `_token` query parameter.

## Core Endpoints

### SET Command
```bash
curl https://$UPSTASH_ENDPOINT/set/mykey/myvalue \
  -H "Authorization: Bearer $UPSTASH_TOKEN"
```

### GET Command
```bash
curl https://$UPSTASH_ENDPOINT/get/mykey \
  -H "Authorization: Bearer $UPSTASH_TOKEN"
```

### SET with Expiry
```bash
curl https://$UPSTASH_ENDPOINT/set/mykey/myvalue/EX/100 \
  -H "Authorization: Bearer $UPSTASH_TOKEN"
```

### POST JSON/Binary Value
```bash
curl -X POST -d '{"name":"john"}' https://$UPSTASH_ENDPOINT/set/user:1 \
  -H "Authorization: Bearer $UPSTASH_TOKEN"
```

### Pipeline (Multiple Commands)
```bash
curl -X POST https://$UPSTASH_ENDPOINT/pipeline \
  -H "Authorization: Bearer $UPSTASH_TOKEN" \
  -d '[["SET", "foo", "bar"], ["GET", "foo"], ["INCR", "counter"]]'
```

### Command in Body
```bash
curl -X POST -d '["SET", "foo", "bar", "EX", 100]' https://$UPSTASH_ENDPOINT \
  -H "Authorization: Bearer $UPSTASH_TOKEN"
```

## Rate Limits
Depends on plan. Check Upstash Console for your database limits.

## Gotchas
- URL path follows Redis protocol: `REST_URL/COMMAND/arg1/arg2/.../argN`
- Response is JSON with `result` field on success, `error` field on failure
- For binary responses, set `Upstash-Encoding: base64` header
- For RESP2 format, set `Upstash-Response-Format: resp2` header
- POST body is appended as last parameter — use query params for additional args after value

## Links
- [Docs](https://upstash.com/docs/redis/features/restapi)
- [Redis Commands Reference](https://redis.io/commands)
# MongoDB Atlas

MongoDB Atlas Administration API for managing clusters, users, and infrastructure.

## Base URL
`https://cloud.mongodb.com/api/atlas/v2`

## Authentication
Digest authentication with public/private API key pair. Create keys in Atlas → Organization/Project → Access Manager → API Keys.

```bash
# Example auth (using --digest flag)
curl --digest -u "$ATLAS_PUBLIC_KEY:$ATLAS_PRIVATE_KEY" \
  https://cloud.mongodb.com/api/atlas/v2/groups
```

## Core Endpoints

### List Projects (Groups)
```bash
curl --digest -u "$ATLAS_PUBLIC_KEY:$ATLAS_PRIVATE_KEY" \
  https://cloud.mongodb.com/api/atlas/v2/groups
```

### Get Cluster
```bash
curl --digest -u "$ATLAS_PUBLIC_KEY:$ATLAS_PRIVATE_KEY" \
  https://cloud.mongodb.com/api/atlas/v2/groups/{groupId}/clusters/{clusterName}
```

### Create Cluster
```bash
curl -X POST --digest -u "$ATLAS_PUBLIC_KEY:$ATLAS_PRIVATE_KEY" \
  -H "Content-Type: application/json" \
  https://cloud.mongodb.com/api/atlas/v2/groups/{groupId}/clusters \
  -d '{
    "name": "myCluster",
    "clusterType": "REPLICASET",
    "replicationSpecs": [{
      "regionConfigs": [{
        "providerName": "AWS",
        "regionName": "US_EAST_1",
        "electableSpecs": {"instanceSize": "M10", "nodeCount": 3}
      }]
    }]
  }'
```

### Create Database User
```bash
curl -X POST --digest -u "$ATLAS_PUBLIC_KEY:$ATLAS_PRIVATE_KEY" \
  -H "Content-Type: application/json" \
  https://cloud.mongodb.com/api/atlas/v2/groups/{groupId}/databaseUsers \
  -d '{
    "databaseName": "admin",
    "username": "myUser",
    "password": "securePassword123",
    "roles": [{"roleName": "readWrite", "databaseName": "mydb"}]
  }'
```

### Add IP to Access List
```bash
curl -X POST --digest -u "$ATLAS_PUBLIC_KEY:$ATLAS_PRIVATE_KEY" \
  -H "Content-Type: application/json" \
  https://cloud.mongodb.com/api/atlas/v2/groups/{groupId}/accessList \
  -d '[{"ipAddress": "192.168.1.1", "comment": "My IP"}]'
```

## Rate Limits
- 100 requests per minute per API key
- Pagination: 100 items per page default, max 500

## Gotchas
- Uses **Digest authentication**, not Bearer tokens — requires `--digest` flag in curl
- API manages infrastructure only — does NOT access database data (use MongoDB drivers for that)
- "Groups" = Projects in Atlas UI terminology
- IP access list required before connecting to clusters
- Dates returned as ISO-8601 UTC strings
- Invalid fields rejected (not ignored) — returns 400 error

## Links
- [Docs](https://www.mongodb.com/docs/atlas/api/atlas-admin-api-ref/)
- [API Reference](https://www.mongodb.com/docs/atlas/reference/api-resources-spec/)
# Fauna

Serverless document database with native GraphQL and FQL query language.

## Base URL
`https://db.fauna.com`

Regional endpoints:
- US: `https://db.us.fauna.com`
- EU: `https://db.eu.fauna.com`

## Authentication
Bearer token via `Authorization` header using a Fauna secret key.

```bash
# Example auth
curl https://db.fauna.com/query/1 \
  -H "Authorization: Bearer $FAUNA_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"query": "Collection.all()"}'
```

Create keys in Fauna Dashboard → Database → Keys.

## Core Endpoints

### Execute FQL Query
```bash
curl -X POST https://db.fauna.com/query/1 \
  -H "Authorization: Bearer $FAUNA_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"query": "Collection.all()"}'
```

### Create Document
```bash
curl -X POST https://db.fauna.com/query/1 \
  -H "Authorization: Bearer $FAUNA_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"query": "users.create({ name: \"John\", email: \"john@example.com\" })"}'
```

### Read Document
```bash
curl -X POST https://db.fauna.com/query/1 \
  -H "Authorization: Bearer $FAUNA_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"query": "users.byId(\"123456789\")"}'
```

### Query with Arguments
```bash
curl -X POST https://db.fauna.com/query/1 \
  -H "Authorization: Bearer $FAUNA_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "users.where(.email == $email)",
    "arguments": {"email": "john@example.com"}
  }'
```

### GraphQL Endpoint
```bash
curl -X POST https://graphql.fauna.com/graphql \
  -H "Authorization: Bearer $FAUNA_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ allUsers { data { name email } } }"}'
```

## Rate Limits
Based on plan. Free tier: 100K read ops, 50K write ops, 500K compute ops per day.

## Gotchas
- Uses **FQL (Fauna Query Language)** — not SQL, has its own syntax
- All operations go through `/query/1` endpoint with FQL in request body
- Keys have different roles: admin, server, client — choose appropriate scope
- Regional endpoints for data residency requirements
- GraphQL requires schema upload before use
- Transactions are ACID-compliant and globally distributed

## Links
- [Docs](https://docs.fauna.com/fauna/current/)
- [FQL Reference](https://docs.fauna.com/fauna/current/reference/fql/)
- [HTTP API](https://docs.fauna.com/fauna/current/reference/http/)
# Xata

Serverless Postgres with built-in full-text search, vector search, and file attachments.

## Base URL
`https://api.xata.tech` (Control Plane)
`https://{workspace}.{region}.xata.sh` (Data Plane)

## Authentication
Bearer token via `Authorization` header using API key from Xata settings.

```bash
# Example auth
curl https://api.xata.tech/organizations \
  -H "Authorization: Bearer $XATA_API_KEY"
```

## Core Endpoints

### List Organizations
```bash
curl https://api.xata.tech/organizations \
  -H "Authorization: Bearer $XATA_API_KEY"
```

### List Databases
```bash
curl https://api.xata.tech/workspaces/{workspace}/databases \
  -H "Authorization: Bearer $XATA_API_KEY"
```

### Query Records (Data Plane)
```bash
curl -X POST https://{workspace}.{region}.xata.sh/db/{database}:{branch}/tables/{table}/query \
  -H "Authorization: Bearer $XATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "columns": ["id", "name", "email"],
    "filter": {"email": {"$contains": "@example.com"}},
    "page": {"size": 20}
  }'
```

### Full-Text Search
```bash
curl -X POST https://{workspace}.{region}.xata.sh/db/{database}:{branch}/tables/{table}/search \
  -H "Authorization: Bearer $XATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "search term",
    "fuzziness": 1
  }'
```

### Insert Record
```bash
curl -X POST https://{workspace}.{region}.xata.sh/db/{database}:{branch}/tables/{table}/data \
  -H "Authorization: Bearer $XATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com"}'
```

### SQL Query (Postgres Wire Protocol)
```bash
curl -X POST https://{workspace}.{region}.xata.sh/db/{database}:{branch}/sql \
  -H "Authorization: Bearer $XATA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"statement": "SELECT * FROM users WHERE email = $1", "params": ["john@example.com"]}'
```

## Rate Limits
Based on plan. Check dashboard for workspace limits.

## Gotchas
- Two separate APIs: **Control Plane** (api.xata.tech) for management, **Data Plane** (workspace.region.xata.sh) for data
- Database URLs include branch: `{database}:{branch}`
- Full Postgres compatibility via wire protocol — use any Postgres client
- Built-in full-text and vector search without external services
- File attachments stored directly in records
- Branch-based development workflow similar to Git

## Links
- [Docs](https://xata.io/docs)
- [API Reference](https://xata.io/docs/api-reference)
- [REST API Guide](https://xata.io/docs/sdk/rest)
# Convex

Backend platform with real-time database, serverless functions, and automatic caching.

## Base URL
Per-deployment URL from Convex Dashboard (e.g., `https://acoustic-panther-728.convex.cloud`)

## Authentication
Two auth methods:
- **User auth**: Bearer token from auth provider (Clerk, Auth0, etc.)
- **Admin auth**: `Convex <deploy_key>` header for full access

```bash
# User auth
curl https://$CONVEX_URL/api/query \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"path": "messages:list", "args": {}, "format": "json"}'

# Admin auth (deploy key)
curl https://$CONVEX_URL/api/query \
  -H "Authorization: Convex $DEPLOY_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path": "messages:list", "args": {}, "format": "json"}'
```

## Core Endpoints

### Query Function
```bash
curl -X POST https://$CONVEX_URL/api/query \
  -H "Content-Type: application/json" \
  -d '{"path": "messages:list", "args": {}, "format": "json"}'
```

### Mutation Function
```bash
curl -X POST https://$CONVEX_URL/api/mutation \
  -H "Content-Type: application/json" \
  -d '{"path": "messages:send", "args": {"body": "Hello!"}, "format": "json"}'
```

### Action Function
```bash
curl -X POST https://$CONVEX_URL/api/action \
  -H "Content-Type: application/json" \
  -d '{"path": "actions:processImage", "args": {"url": "https://..."}, "format": "json"}'
```

### Run Function (Alternative URL format)
```bash
curl -X POST https://$CONVEX_URL/api/run/messages/list \
  -H "Content-Type: application/json" \
  -d '{"args": {}, "format": "json"}'
```

## Rate Limits
Based on plan. Check Convex Dashboard for usage limits.

## Gotchas
- Functions defined in code, called via HTTP — function path format: `module:functionName`
- Alternative URL format uses `/api/run/{module}/{function}` with `/` instead of `:`
- Only `json` format currently supported for values
- Response includes `logLines` array for debugging
- Queries are cached automatically, mutations trigger reactive updates
- Deploy key gives **full read/write access** — keep it secret

## Links
- [Docs](https://docs.convex.dev)
- [HTTP API](https://docs.convex.dev/http-api)
- [Function Reference](https://docs.convex.dev/functions)
# Appwrite

Open-source backend-as-a-service with auth, databases, storage, and serverless functions.

## Base URL
`https://cloud.appwrite.io/v1` (Appwrite Cloud)
`https://[YOUR_HOSTNAME]/v1` (Self-hosted)

## Authentication
Two auth methods:
- **Client/JWT**: Session cookies or JWT token via `X-Appwrite-JWT` header
- **Server**: API key via `X-Appwrite-Key` header

```bash
# Server auth (API key)
curl https://cloud.appwrite.io/v1/databases/{databaseId}/collections/{collectionId}/documents \
  -H "Content-Type: application/json" \
  -H "X-Appwrite-Project: $PROJECT_ID" \
  -H "X-Appwrite-Key: $API_KEY"
```

Required headers for all requests:
- `X-Appwrite-Project: [PROJECT_ID]`
- `Content-Type: application/json`

## Core Endpoints

### Create Session (Email/Password)
```bash
curl -X POST https://cloud.appwrite.io/v1/account/sessions/email \
  -H "Content-Type: application/json" \
  -H "X-Appwrite-Project: $PROJECT_ID" \
  -d '{"email": "user@example.com", "password": "password"}'
```

### Get Current User
```bash
curl https://cloud.appwrite.io/v1/account \
  -H "X-Appwrite-Project: $PROJECT_ID" \
  -H "X-Appwrite-JWT: $JWT_TOKEN"
```

### List Documents
```bash
curl https://cloud.appwrite.io/v1/databases/{databaseId}/collections/{collectionId}/documents \
  -H "X-Appwrite-Project: $PROJECT_ID" \
  -H "X-Appwrite-Key: $API_KEY"
```

### Create Document
```bash
curl -X POST https://cloud.appwrite.io/v1/databases/{databaseId}/collections/{collectionId}/documents \
  -H "Content-Type: application/json" \
  -H "X-Appwrite-Project: $PROJECT_ID" \
  -H "X-Appwrite-Key: $API_KEY" \
  -d '{
    "documentId": "unique()",
    "data": {"name": "John", "email": "john@example.com"},
    "permissions": ["read(\"any\")"]
  }'
```

### Upload File
```bash
curl -X POST https://cloud.appwrite.io/v1/storage/buckets/{bucketId}/files \
  -H "X-Appwrite-Project: $PROJECT_ID" \
  -H "X-Appwrite-Key: $API_KEY" \
  -F "fileId=unique()" \
  -F "file=@/path/to/file.jpg"
```

## Rate Limits
Based on plan. Self-hosted: configurable. Cloud: check dashboard.

## Gotchas
- Project ID required in **every request** via `X-Appwrite-Project` header
- API keys are for **server-side only** — never expose in client code
- File uploads use `multipart/form-data`, not JSON
- Large files (>5MB) use chunked uploads with `Content-Range` and `X-Appwrite-ID` headers
- Permissions use string format: `read("any")`, `write("user:123")`
- Session cookies include `_legacy` variant for browser compatibility

## Links
- [Docs](https://appwrite.io/docs)
- [REST API](https://appwrite.io/docs/apis/rest)
- [API Reference](https://appwrite.io/docs/references)
