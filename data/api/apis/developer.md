# Index

| API | Line |
|-----|------|
| GitHub | 2 |
| GitLab | 97 |
| Bitbucket | 169 |
| Vercel | 243 |
| Netlify | 342 |
| Railway | 411 |
| Render | 490 |
| Fly.io | 560 |
| DigitalOcean | 644 |
| Heroku | 723 |
| Cloudflare | 804 |
| CircleCI | 899 |
| PagerDuty | 982 |
| LaunchDarkly | 1074 |
| Statsig | 1226 |

---

# GitHub

## Base URL
```
https://api.github.com
```

## Authentication
```bash
curl https://api.github.com/user \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /user | GET | Current user |
| /repos/:owner/:repo | GET | Get repo |
| /repos/:owner/:repo/issues | GET | List issues |
| /repos/:owner/:repo/issues | POST | Create issue |
| /repos/:owner/:repo/pulls | GET | List PRs |
| /repos/:owner/:repo/pulls | POST | Create PR |
| /repos/:owner/:repo/contents/:path | GET | Get file content |
| /search/repositories | GET | Search repos |

## Quick Examples

### List Repos
```bash
curl https://api.github.com/user/repos \
  -H "Authorization: Bearer $GITHUB_TOKEN"
```

### Create Issue
```bash
curl -X POST https://api.github.com/repos/OWNER/REPO/issues \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bug report",
    "body": "Description here",
    "labels": ["bug"]
  }'
```

### Create Pull Request
```bash
curl -X POST https://api.github.com/repos/OWNER/REPO/pulls \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New feature",
    "head": "feature-branch",
    "base": "main",
    "body": "PR description"
  }'
```

### Get File Content
```bash
curl https://api.github.com/repos/OWNER/REPO/contents/README.md \
  -H "Authorization: Bearer $GITHUB_TOKEN"
# Content is base64 encoded
```

### Search Repositories
```bash
curl "https://api.github.com/search/repositories?q=language:python+stars:>1000" \
  -H "Authorization: Bearer $GITHUB_TOKEN"
```

## Common Traps

- File content is base64 encoded
- Rate limit: 5000 req/hour (authenticated)
- Pagination via Link header, not body
- Accept header affects response format
- Some endpoints require specific scopes

## Rate Limits

- Authenticated: 5000 requests/hour
- Unauthenticated: 60 requests/hour
- Search: 30 requests/minute

Check with:
```bash
curl -I https://api.github.com/users/octocat
# X-RateLimit-Remaining header
```

## Official Docs
https://docs.github.com/en/rest
# GitLab

Self-hosted and cloud Git repository management with CI/CD pipelines.

## Base URL
`https://gitlab.com/api/v4`

For self-hosted: `https://your-gitlab-instance.com/api/v4`

## Authentication
Personal Access Token or OAuth token via header.

```bash
# Using Personal Access Token
curl "https://gitlab.com/api/v4/projects" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN"

# Using OAuth token
curl "https://gitlab.com/api/v4/projects" \
  -H "Authorization: Bearer $OAUTH_TOKEN"
```

## Core Endpoints

### List Projects
```bash
curl "https://gitlab.com/api/v4/projects" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN"
```

### Get Project Details
```bash
curl "https://gitlab.com/api/v4/projects/:id" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN"
```

### List Merge Requests
```bash
curl "https://gitlab.com/api/v4/projects/:id/merge_requests" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN"
```

### Trigger Pipeline
```bash
curl -X POST "https://gitlab.com/api/v4/projects/:id/pipeline" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ref": "main"}'
```

### List Repository Files
```bash
curl "https://gitlab.com/api/v4/projects/:id/repository/tree" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN"
```

## Rate Limits
- Unauthenticated: 500 requests per minute
- Authenticated: 2,000 requests per minute
- GitLab.com may have different limits per plan

## Gotchas
- Project IDs can be numeric ID or URL-encoded namespace/project path (e.g., `diaspora%2Fdiaspora`)
- Namespaced paths must be URL-encoded (`/` becomes `%2F`)
- `id` vs `iid`: `id` is globally unique, `iid` is project-scoped (use `iid` for issues/MRs)
- File paths and branch names with `/` must be URL-encoded
- Pagination uses `page` and `per_page` params (max 100 per page)

## Links
- [Docs](https://docs.gitlab.com/ee/api/)
- [API Reference](https://docs.gitlab.com/ee/api/rest/)
- [Authentication Guide](https://docs.gitlab.com/ee/api/rest/authentication.html)
# Bitbucket

Atlassian's Git repository hosting service with CI/CD via Pipelines.

## Base URL
`https://api.bitbucket.org/2.0`

## Authentication
App passwords, OAuth 2.0, or repository/workspace access tokens.

```bash
# Using App Password (Basic Auth)
curl "https://api.bitbucket.org/2.0/repositories/{workspace}" \
  -u "username:app_password"

# Using OAuth 2.0 Bearer Token
curl "https://api.bitbucket.org/2.0/repositories/{workspace}" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Core Endpoints

### List Repositories
```bash
curl "https://api.bitbucket.org/2.0/repositories/{workspace}" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Get Repository
```bash
curl "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### List Pull Requests
```bash
curl "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Create Pull Request
```bash
curl -X POST "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pullrequests" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "PR Title",
    "source": {"branch": {"name": "feature-branch"}},
    "destination": {"branch": {"name": "main"}}
  }'
```

### List Pipelines
```bash
curl "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo_slug}/pipelines" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Rate Limits
- 1,000 requests per hour per user
- Some endpoints have stricter limits

## Gotchas
- Workspace and repo identifiers are slugs (URL-friendly names), not UUIDs
- Access tokens are scoped: repository, project, or workspace level
- Access tokens cannot be viewed after creation—only name and scopes visible
- App passwords require 2FA to be disabled for creation
- Pagination uses `page` and `pagelen` (max 100)
- UUID format includes curly braces: `{...}`

## Links
- [Docs](https://developer.atlassian.com/cloud/bitbucket/)
- [API Reference](https://developer.atlassian.com/cloud/bitbucket/rest/intro/)
- [Authentication](https://developer.atlassian.com/cloud/bitbucket/rest/intro/#authentication)
# Vercel

## Base URL
```
https://api.vercel.com
```

## Authentication
```bash
curl https://api.vercel.com/v9/projects \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /v9/projects | GET | List projects |
| /v9/projects | POST | Create project |
| /v13/deployments | GET | List deployments |
| /v13/deployments | POST | Create deployment |
| /v6/domains | GET | List domains |
| /v5/projects/:id/env | GET | Get env vars |

## Quick Examples

### List Projects
```bash
curl "https://api.vercel.com/v9/projects?limit=10" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

### Get Project
```bash
curl "https://api.vercel.com/v9/projects/$PROJECT_NAME" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

### List Deployments
```bash
curl "https://api.vercel.com/v13/deployments?projectId=$PROJECT_ID&limit=10" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

### Get Deployment
```bash
curl "https://api.vercel.com/v13/deployments/$DEPLOYMENT_ID" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

### Create Deployment (from Git)
```bash
curl -X POST https://api.vercel.com/v13/deployments \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-project",
    "gitSource": {
      "type": "github",
      "ref": "main",
      "repoId": "123456"
    }
  }'
```

### Get Environment Variables
```bash
curl "https://api.vercel.com/v10/projects/$PROJECT_ID/env" \
  -H "Authorization: Bearer $VERCEL_TOKEN"
```

### Create Environment Variable
```bash
curl -X POST "https://api.vercel.com/v10/projects/$PROJECT_ID/env" \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "key": "API_KEY",
    "value": "secret",
    "target": ["production", "preview"],
    "type": "encrypted"
  }'
```

## Common Traps

- API versions vary per endpoint (v5, v9, v13, etc.)
- Team deployments need `teamId` query param
- Deployment URLs are `{id}.vercel.app` or custom domain
- Env vars have `target` (production/preview/development)
- Rate limits are per-account, not per-token

## Rate Limits

- 100 requests/minute for most endpoints
- Deploy: 100 deploys/day (free tier)

## Official Docs
https://vercel.com/docs/rest-api
# Netlify

## Base URL
```
https://api.netlify.com/api/v1
```

## Authentication
```bash
curl https://api.netlify.com/api/v1/sites \
  -H "Authorization: Bearer $NETLIFY_TOKEN"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /sites | GET | List sites |
| /sites | POST | Create site |
| /sites/:id | GET | Get site |
| /sites/:id/deploys | GET | List deploys |
| /deploys/:id | GET | Get deploy |

## List Sites
```bash
curl "https://api.netlify.com/api/v1/sites" \
  -H "Authorization: Bearer $NETLIFY_TOKEN"
```

## Create Deploy
```bash
curl -X POST "https://api.netlify.com/api/v1/sites/$SITE_ID/deploys" \
  -H "Authorization: Bearer $NETLIFY_TOKEN" \
  -H "Content-Type: application/zip" \
  --data-binary @deploy.zip
```

## Get Deploy Status
```bash
curl "https://api.netlify.com/api/v1/deploys/$DEPLOY_ID" \
  -H "Authorization: Bearer $NETLIFY_TOKEN"
```

## Trigger Build Hook
```bash
curl -X POST "https://api.netlify.com/build_hooks/$HOOK_ID"
```

## Set Environment Variable
```bash
curl -X PATCH "https://api.netlify.com/api/v1/sites/$SITE_ID" \
  -H "Authorization: Bearer $NETLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "build_settings": {
      "env": {"API_KEY": "value"}
    }
  }'
```

## Common Traps

- Deploy with ZIP requires Content-Type: application/zip
- Build hooks don't need auth (public URLs)
- Site ID is in the URL or API response
- Rate limit: 500 requests/minute

## Official Docs
https://docs.netlify.com/api/get-started/
# Railway

App deployment platform with instant deploys from GitHub.

## Base URL
`https://backboard.railway.com/graphql/v2`

**Note:** Railway uses a GraphQL API, not REST.

## Authentication
Bearer token via Authorization header. Project tokens use a different header.

```bash
# Account or Workspace token
curl -X POST "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { me { name email } }"}'

# Project token (different header!)
curl -X POST "https://backboard.railway.com/graphql/v2" \
  -H "Project-Access-Token: $PROJECT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { projectToken { projectId environmentId } }"}'
```

## Core Endpoints

### Get Current User
```bash
curl -X POST "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { me { name email } }"}'
```

### List Projects
```bash
curl -X POST "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { projects { edges { node { id name } } } }"}'
```

### Get Project Details
```bash
curl -X POST "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "query { project(id: \"PROJECT_ID\") { name services { edges { node { id name } } } } }"}'
```

### Trigger Deployment
```bash
curl -X POST "https://backboard.railway.com/graphql/v2" \
  -H "Authorization: Bearer $RAILWAY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { serviceInstanceRedeploy(serviceId: \"SERVICE_ID\", environmentId: \"ENV_ID\") }"}'
```

## Rate Limits
- Free: 100 requests/hour
- Hobby: 1,000 requests/hour, 10 requests/second
- Pro: 10,000 requests/hour, 50 requests/second
- Enterprise: Custom

Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

## Gotchas
- **GraphQL only** — no REST API available
- Project tokens use `Project-Access-Token` header, NOT `Authorization: Bearer`
- Account tokens access all workspaces; workspace tokens are scoped
- Introspection supported — use Postman/Insomnia to explore schema
- GraphiQL playground available at `https://railway.com/graphiql`

## Links
- [Docs](https://docs.railway.com/)
- [API Reference](https://docs.railway.com/reference/public-api)
- [GraphiQL Playground](https://railway.com/graphiql)
# Render

Cloud platform for deploying web services, static sites, and databases.

## Base URL
`https://api.render.com/v1`

## Authentication
API key via Bearer token.

```bash
curl "https://api.render.com/v1/services?limit=20" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

## Core Endpoints

### List Services
```bash
curl "https://api.render.com/v1/services?limit=20" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

### Get Service Details
```bash
curl "https://api.render.com/v1/services/{serviceId}" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

### Trigger Deploy
```bash
curl -X POST "https://api.render.com/v1/services/{serviceId}/deploys" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"clearCache": "do_not_clear"}'
```

### List Environment Variables
```bash
curl "https://api.render.com/v1/services/{serviceId}/env-vars" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

### Suspend Service
```bash
curl -X POST "https://api.render.com/v1/services/{serviceId}/suspend" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

### Resume Service
```bash
curl -X POST "https://api.render.com/v1/services/{serviceId}/resume" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

## Rate Limits
Not publicly documented. Use reasonable request rates.

## Gotchas
- API keys are secret — only shown once at creation
- Service IDs are prefixed with service type (e.g., `srv-`, `web-`, `pserv-`)
- PATCH requests require specific format — check docs
- OpenAPI spec available but may change (backward compatible, not spec stable)
- Deploys can take time — poll deploy status endpoint

## Links
- [Docs](https://render.com/docs/api)
- [API Reference](https://api-docs.render.com/reference/introduction)
- [OpenAPI Spec](https://api-docs.render.com/openapi/6140fb3daeae351056086186)
# Fly.io

Edge deployment platform running apps close to users globally.

## Base URL
- Public: `https://api.machines.dev`
- Internal (within Fly network): `http://_api.internal:4280`

## Authentication
Bearer token via Authorization header.

```bash
# Get token via flyctl
export FLY_API_TOKEN=$(fly tokens deploy)

curl "https://api.machines.dev/v1/apps" \
  -H "Authorization: Bearer $FLY_API_TOKEN"
```

## Core Endpoints

### List Apps
```bash
curl "https://api.machines.dev/v1/apps?org_slug=personal" \
  -H "Authorization: Bearer $FLY_API_TOKEN"
```

### Create App
```bash
curl -X POST "https://api.machines.dev/v1/apps" \
  -H "Authorization: Bearer $FLY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"app_name": "my-app", "org_slug": "personal"}'
```

### List Machines
```bash
curl "https://api.machines.dev/v1/apps/{app_name}/machines" \
  -H "Authorization: Bearer $FLY_API_TOKEN"
```

### Create Machine
```bash
curl -X POST "https://api.machines.dev/v1/apps/{app_name}/machines" \
  -H "Authorization: Bearer $FLY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "image": "nginx:latest",
      "guest": {"cpu_kind": "shared", "cpus": 1, "memory_mb": 256}
    }
  }'
```

### Start Machine
```bash
curl -X POST "https://api.machines.dev/v1/apps/{app_name}/machines/{machine_id}/start" \
  -H "Authorization: Bearer $FLY_API_TOKEN"
```

### Stop Machine
```bash
curl -X POST "https://api.machines.dev/v1/apps/{app_name}/machines/{machine_id}/stop" \
  -H "Authorization: Bearer $FLY_API_TOKEN"
```

## Rate Limits
- 1 request/second per action per machine (burst up to 3/s)
- Get Machine: 5 req/s (burst up to 10/s)
- App deletions: 100/minute

Scoped per Machine ID or App ID depending on endpoint.

## Gotchas
- `flyctl` is required to generate tokens — `fly tokens deploy`
- Internal endpoint only works from within Fly's WireGuard network
- Machines are VMs, not containers — they have their own lifecycle
- Apps must exist before creating machines
- Token types: deploy tokens (app-scoped) vs personal tokens (account-wide)

## Links
- [Docs](https://fly.io/docs/machines/api/)
- [API Reference](https://docs.machines.dev/)
- [Working with Machines API](https://fly.io/docs/machines/api/working-with-machines-api/)
# DigitalOcean

Cloud infrastructure provider for Droplets, Kubernetes, databases, and more.

## Base URL
`https://api.digitalocean.com/v2`

## Authentication
Personal Access Token via Bearer header.

```bash
curl "https://api.digitalocean.com/v2/droplets" \
  -H "Authorization: Bearer $DO_TOKEN" \
  -H "Content-Type: application/json"
```

## Core Endpoints

### List Droplets
```bash
curl "https://api.digitalocean.com/v2/droplets" \
  -H "Authorization: Bearer $DO_TOKEN"
```

### Create Droplet
```bash
curl -X POST "https://api.digitalocean.com/v2/droplets" \
  -H "Authorization: Bearer $DO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-droplet",
    "region": "nyc3",
    "size": "s-1vcpu-1gb",
    "image": "ubuntu-22-04-x64"
  }'
```

### Get Droplet
```bash
curl "https://api.digitalocean.com/v2/droplets/{droplet_id}" \
  -H "Authorization: Bearer $DO_TOKEN"
```

### Delete Droplet
```bash
curl -X DELETE "https://api.digitalocean.com/v2/droplets/{droplet_id}" \
  -H "Authorization: Bearer $DO_TOKEN"
```

### List Domains
```bash
curl "https://api.digitalocean.com/v2/domains" \
  -H "Authorization: Bearer $DO_TOKEN"
```

### Create DNS Record
```bash
curl -X POST "https://api.digitalocean.com/v2/domains/{domain}/records" \
  -H "Authorization: Bearer $DO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type": "A", "name": "www", "data": "1.2.3.4"}'
```

## Rate Limits
- 5,000 requests per hour
- Headers: `Ratelimit-Limit`, `Ratelimit-Remaining`, `Ratelimit-Reset`

## Gotchas
- Droplet actions are async — poll the action endpoint for completion
- IDs are integers, not UUIDs
- Pagination uses `page` and `per_page` (default 20, max 200)
- SSH keys must be added before Droplet creation to include them
- Some resources require scoped tokens — check API token permissions
- Spaces API is separate and S3-compatible (different auth)

## Links
- [Docs](https://docs.digitalocean.com/reference/api/)
- [API Reference](https://docs.digitalocean.com/reference/api/api-reference/)
- [Create Access Token](https://docs.digitalocean.com/reference/api/create-personal-access-token/)
# Heroku

Platform-as-a-Service for deploying, managing, and scaling apps.

## Base URL
`https://api.heroku.com`

## Authentication
OAuth token or API key via Bearer header. Requires specific Accept header.

```bash
curl "https://api.heroku.com/apps" \
  -H "Accept: application/vnd.heroku+json; version=3" \
  -H "Authorization: Bearer $HEROKU_API_KEY"
```

## Core Endpoints

### List Apps
```bash
curl "https://api.heroku.com/apps" \
  -H "Accept: application/vnd.heroku+json; version=3" \
  -H "Authorization: Bearer $HEROKU_API_KEY"
```

### Get App Info
```bash
curl "https://api.heroku.com/apps/{app_id_or_name}" \
  -H "Accept: application/vnd.heroku+json; version=3" \
  -H "Authorization: Bearer $HEROKU_API_KEY"
```

### Create App
```bash
curl -X POST "https://api.heroku.com/apps" \
  -H "Accept: application/vnd.heroku+json; version=3" \
  -H "Authorization: Bearer $HEROKU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-app", "region": "us"}'
```

### Scale Dynos
```bash
curl -X PATCH "https://api.heroku.com/apps/{app}/formation" \
  -H "Accept: application/vnd.heroku+json; version=3" \
  -H "Authorization: Bearer $HEROKU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"updates": [{"type": "web", "quantity": 2}]}'
```

### Set Config Vars
```bash
curl -X PATCH "https://api.heroku.com/apps/{app}/config-vars" \
  -H "Accept: application/vnd.heroku+json; version=3" \
  -H "Authorization: Bearer $HEROKU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"KEY": "value"}'
```

### Restart All Dynos
```bash
curl -X DELETE "https://api.heroku.com/apps/{app}/dynos" \
  -H "Accept: application/vnd.heroku+json; version=3" \
  -H "Authorization: Bearer $HEROKU_API_KEY"
```

## Rate Limits
- 4,500 requests per hour per account
- Some endpoints have lower limits (e.g., OAuth token creation)

## Gotchas
- **Must include** `Accept: application/vnd.heroku+json; version=3` header
- Resources can be referenced by `id` (UUID) or `name`
- ETag caching supported — use `If-None-Match` for conditional requests
- Large lists return 206 Partial Content — use `Range` header for pagination
- API keys can be retrieved with `heroku auth:token` CLI command

## Links
- [Docs](https://devcenter.heroku.com/articles/platform-api-reference)
- [API Reference](https://devcenter.heroku.com/articles/platform-api-reference)
- [Quick Start](https://devcenter.heroku.com/articles/platform-api-quickstart)
# Cloudflare

## Base URL
```
https://api.cloudflare.com/client/v4
```

## Authentication
```bash
# API Token (recommended)
curl https://api.cloudflare.com/client/v4/user \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"

# Global API Key (legacy)
curl https://api.cloudflare.com/client/v4/user \
  -H "X-Auth-Email: user@example.com" \
  -H "X-Auth-Key: $CLOUDFLARE_API_KEY"
```

## Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /zones | GET | List zones |
| /zones/:id/dns_records | GET | List DNS records |
| /zones/:id/dns_records | POST | Create DNS record |
| /zones/:id/purge_cache | POST | Purge cache |
| /accounts/:id/workers/scripts | GET | List Workers |

## Quick Examples

### List Zones
```bash
curl "https://api.cloudflare.com/client/v4/zones" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

### List DNS Records
```bash
curl "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

### Create DNS Record
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "A",
    "name": "subdomain",
    "content": "1.2.3.4",
    "ttl": 3600,
    "proxied": true
  }'
```

### Update DNS Record
```bash
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/$RECORD_ID" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "5.6.7.8"}'
```

### Purge Cache (Everything)
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"purge_everything": true}'
```

### Purge Specific URLs
```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"files": ["https://example.com/page1", "https://example.com/page2"]}'
```

## Common Traps

- Zone ID is NOT the domain name (find via /zones)
- `proxied: true` enables Cloudflare CDN (orange cloud)
- API tokens are scoped, global key has full access
- Responses have `success`, `errors`, `result` structure
- TTL of 1 = automatic (proxied records)

## Rate Limits

- 1200 requests/5 minutes per user

## Official Docs
https://developers.cloudflare.com/api/
# CircleCI

Continuous Integration and Delivery platform.

## Base URL
`https://circleci.com/api/v2`

## Authentication
Personal API token via header or Basic Auth.

```bash
# Header authentication (recommended)
curl "https://circleci.com/api/v2/me" \
  -H "Circle-Token: $CIRCLE_TOKEN"

# Basic Auth
curl "https://circleci.com/api/v2/me" \
  -u "$CIRCLE_TOKEN:"
```

## Core Endpoints

### Get Current User
```bash
curl "https://circleci.com/api/v2/me" \
  -H "Circle-Token: $CIRCLE_TOKEN"
```

### Trigger Pipeline
```bash
curl -X POST "https://circleci.com/api/v2/project/{project_slug}/pipeline" \
  -H "Circle-Token: $CIRCLE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"branch": "main"}'
```

### Get Pipeline
```bash
curl "https://circleci.com/api/v2/pipeline/{pipeline_id}" \
  -H "Circle-Token: $CIRCLE_TOKEN"
```

### List Workflows for Pipeline
```bash
curl "https://circleci.com/api/v2/pipeline/{pipeline_id}/workflow" \
  -H "Circle-Token: $CIRCLE_TOKEN"
```

### Get Workflow Jobs
```bash
curl "https://circleci.com/api/v2/workflow/{workflow_id}/job" \
  -H "Circle-Token: $CIRCLE_TOKEN"
```

### Approve Job
```bash
curl -X POST "https://circleci.com/api/v2/workflow/{workflow_id}/approve/{approval_request_id}" \
  -H "Circle-Token: $CIRCLE_TOKEN"
```

### Rerun Workflow
```bash
curl -X POST "https://circleci.com/api/v2/workflow/{workflow_id}/rerun" \
  -H "Circle-Token: $CIRCLE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"from_failed": true}'
```

## Rate Limits
- Standard rate limits apply per account
- HTTP 429 returned when exceeded

## Gotchas
- Project slug format: `{vcs_type}/{org}/{repo}` (e.g., `gh/myorg/myrepo` or `bb/myorg/myrepo`)
- `gh` = GitHub, `bb` = Bitbucket
- Personal API tokens created in User Settings > Personal API Tokens
- Pagination uses `page-token` query parameter
- Some endpoints require organization/project context via query params

## Links
- [Docs](https://circleci.com/docs/)
- [API Reference](https://circleci.com/docs/api/v2/)
- [API v2 Overview](https://circleci.com/docs/api-intro/)
# PagerDuty

Incident management and on-call scheduling platform.

## Base URL
- REST API: `https://api.pagerduty.com`
- Events API: `https://events.pagerduty.com/v2/enqueue`

## Authentication
REST API uses API token; Events API uses integration/routing key.

```bash
# REST API - API Token
curl "https://api.pagerduty.com/users" \
  -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  -H "Content-Type: application/json"

# Events API - Integration Key
curl -X POST "https://events.pagerduty.com/v2/enqueue" \
  -H "Content-Type: application/json" \
  -d '{
    "routing_key": "$INTEGRATION_KEY",
    "event_action": "trigger",
    "payload": {
      "summary": "Server down",
      "severity": "critical",
      "source": "monitoring"
    }
  }'
```

## Core Endpoints

### List Services
```bash
curl "https://api.pagerduty.com/services" \
  -H "Authorization: Token token=$PAGERDUTY_API_KEY"
```

### List Incidents
```bash
curl "https://api.pagerduty.com/incidents" \
  -H "Authorization: Token token=$PAGERDUTY_API_KEY"
```

### Get Incident
```bash
curl "https://api.pagerduty.com/incidents/{incident_id}" \
  -H "Authorization: Token token=$PAGERDUTY_API_KEY"
```

### Acknowledge Incident
```bash
curl -X PUT "https://api.pagerduty.com/incidents/{incident_id}" \
  -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"incident": {"type": "incident_reference", "status": "acknowledged"}}'
```

### Trigger Event
```bash
curl -X POST "https://events.pagerduty.com/v2/enqueue" \
  -H "Content-Type: application/json" \
  -d '{
    "routing_key": "YOUR_INTEGRATION_KEY",
    "event_action": "trigger",
    "dedup_key": "unique-alert-key",
    "payload": {
      "summary": "Alert description",
      "severity": "warning",
      "source": "my-app"
    }
  }'
```

## Rate Limits
- REST API: Rate limits enforced per account (varies by plan)
- Events API: Higher throughput limits

## Gotchas
- **Two different APIs**: REST for management, Events for alerts
- REST API key format: `Token token=YOUR_KEY` (not Bearer!)
- Events API uses 32-character integration keys (not REST API keys)
- User token keys are scoped to user permissions
- General access keys can be read-only or full access
- `dedup_key` in Events API groups related alerts

## Links
- [Docs](https://developer.pagerduty.com/)
- [REST API Reference](https://developer.pagerduty.com/api-reference/)
- [Events API](https://developer.pagerduty.com/docs/events-api-v2/overview/)
- [API Access Keys](https://support.pagerduty.com/docs/api-access-keys)
# LaunchDarkly

Feature flag and feature management platform.

## Base URL
`https://app.launchdarkly.com/api/v2`

## Authentication
Access token via Authorization header.

```bash
curl "https://app.launchdarkly.com/api/v2/flags/{projectKey}" \
  -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN"
```

## Core Endpoints

### List Feature Flags
```bash
curl "https://app.launchdarkly.com/api/v2/flags/{projectKey}" \
  -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN"
```

### Get Feature Flag
```bash
curl "https://app.launchdarkly.com/api/v2/flags/{projectKey}/{flagKey}" \
  -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN"
```

### Update Feature Flag
```bash
curl -X PATCH "https://app.launchdarkly.com/api/v2/flags/{projectKey}/{flagKey}" \
  -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"op": "replace", "path": "/environments/production/on", "value": true}]'
```

### List Projects
```bash
curl "https://app.launchdarkly.com/api/v2/projects" \
  -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN"
```

### List Environments
```bash
curl "https://app.launchdarkly.com/api/v2/projects/{projectKey}/environments" \
  -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN"
```

### Evaluate Flag for User (Server-side)
```bash
curl -X POST "https://app.launchdarkly.com/api/v2/flags/{projectKey}/{flagKey}/eval" \
  -H "Authorization: $LAUNCHDARKLY_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"environmentKey": "production", "user": {"key": "user123"}}'
```

## Rate Limits
- Varies by endpoint and plan
- Rate limit headers included in responses

## Gotchas
- **Three key types**: Access tokens (API), SDK keys (server SDKs), Client-side IDs (browser/mobile)
- SDK keys and client IDs **cannot** access REST API
- PATCH requests use JSON Patch format (array of operations)
- Flag keys are case-sensitive
- `expand` parameter for including related resources in responses
- Summary vs detailed representations — follow `_links` for full data

## Links
- [Docs](https://docs.launchdarkly.com/)
- [API Reference](https://apidocs.launchdarkly.com/)
- [API Access Tokens](https://docs.launchdarkly.com/home/account-security/api-access-tokens)
# Split (Harness Feature Flags)

Feature flags and experimentation platform (acquired by Harness).

## Base URL
`https://api.split.io/internal/api/v2`

**Note:** Split is now part of Harness. New projects may use Harness Feature Flags API instead.

## Authentication
Admin API key via Authorization header.

```bash
curl "https://api.split.io/internal/api/v2/splits" \
  -H "Authorization: Bearer $SPLIT_API_KEY"
```

## Core Endpoints

### List Splits (Feature Flags)
```bash
curl "https://api.split.io/internal/api/v2/splits?wsId={workspaceId}" \
  -H "Authorization: Bearer $SPLIT_API_KEY"
```

### Get Split
```bash
curl "https://api.split.io/internal/api/v2/splits/{splitName}?wsId={workspaceId}" \
  -H "Authorization: Bearer $SPLIT_API_KEY"
```

### List Environments
```bash
curl "https://api.split.io/internal/api/v2/environments?wsId={workspaceId}" \
  -H "Authorization: Bearer $SPLIT_API_KEY"
```

### List Workspaces
```bash
curl "https://api.split.io/internal/api/v2/workspaces" \
  -H "Authorization: Bearer $SPLIT_API_KEY"
```

### Create Split
```bash
curl -X POST "https://api.split.io/internal/api/v2/splits?wsId={workspaceId}" \
  -H "Authorization: Bearer $SPLIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-feature",
    "description": "My new feature flag",
    "trafficTypeName": "user"
  }'
```

### Add Split to Environment
```bash
curl -X POST "https://api.split.io/internal/api/v2/splits/{splitName}/environments/{envName}" \
  -H "Authorization: Bearer $SPLIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"treatments": [{"name": "on"}, {"name": "off"}], "defaultTreatment": "off"}'
```

## Rate Limits
- Varies by plan
- Contact Split/Harness for specific limits

## Gotchas
- **Split is now Harness Feature Flags** — documentation may redirect
- Workspace ID (`wsId`) required for most endpoints
- "Splits" are feature flags in Split terminology
- "Treatments" are the values a flag can return
- Traffic types define the entity being targeted (user, account, etc.)
- Admin API is different from SDK API — use Admin API for CRUD operations

## Links
- [Docs](https://help.split.io/)
- [Admin API Reference](https://docs.split.io/reference/introduction-to-admin-api)
- [Harness Feature Flags](https://developer.harness.io/docs/feature-flags)
# Statsig

Feature flags, A/B testing, and product analytics platform.

## Base URL
- Console API (CRUD): `https://statsigapi.net`
- HTTP API (evaluation): `https://api.statsig.com/v1`

## Authentication
API keys via header. Different keys for different purposes.

```bash
# Console API (management)
curl "https://statsigapi.net/console/v1/gates" \
  -H "STATSIG-API-KEY: $STATSIG_CONSOLE_KEY" \
  -H "STATSIG-API-VERSION: 20240601"

# HTTP API (evaluation)
curl -X POST "https://api.statsig.com/v1/check_gate" \
  -H "statsig-api-key: $STATSIG_SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"gateName": "my_gate", "user": {"userID": "user123"}}'
```

## Core Endpoints

### List Feature Gates (Console API)
```bash
curl "https://statsigapi.net/console/v1/gates" \
  -H "STATSIG-API-KEY: $STATSIG_CONSOLE_KEY"
```

### Create Feature Gate (Console API)
```bash
curl -X POST "https://statsigapi.net/console/v1/gates" \
  -H "STATSIG-API-KEY: $STATSIG_CONSOLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "my_new_gate", "description": "My feature gate"}'
```

### Check Gate (HTTP API)
```bash
curl -X POST "https://api.statsig.com/v1/check_gate" \
  -H "statsig-api-key: $STATSIG_SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "gateName": "my_gate",
    "user": {"userID": "user123", "email": "user@example.com"}
  }'
```

### Get Config (HTTP API)
```bash
curl -X POST "https://api.statsig.com/v1/get_config" \
  -H "statsig-api-key: $STATSIG_SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d '{"configName": "my_config", "user": {"userID": "user123"}}'
```

### Log Event (HTTP API)
```bash
curl -X POST "https://api.statsig.com/v1/log_event" \
  -H "statsig-api-key: $STATSIG_SERVER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {"userID": "user123"},
    "eventName": "purchase",
    "value": 9.99,
    "metadata": {"item": "subscription"}
  }'
```

## Rate Limits
- Console API: ~100 requests/10 seconds, ~900 requests/15 minutes per project
- HTTP API: Higher limits, designed for production traffic

## Gotchas
- **Two APIs**: Console API for management, HTTP API for evaluation
- **Three key types**: Server-side secret, Client-SDK, Console API — don't mix them
- All HTTP API calls use POST method (even for reads)
- SDKs are recommended over HTTP API for better performance
- `STATSIG-API-VERSION` header recommended for Console API
- Exposure events logged automatically — attribute experiments correctly

## Links
- [Docs](https://docs.statsig.com/)
- [HTTP API](https://docs.statsig.com/http-api)
- [Console API](https://docs.statsig.com/console-api/introduction)
- [OpenAPI Spec](https://api.statsig.com/openapi/20240601.json)
