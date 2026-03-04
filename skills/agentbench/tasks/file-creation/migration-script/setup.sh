#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="$1"

cd "$WORKSPACE"
git init -q

mkdir -p config

# ── config/settings.json (~130 lines) ──────────────────────────────────────────
cat > config/settings.json << 'SETTINGS_EOF'
{
  "app_name": "DataFlow",
  "version": "2.4.1",
  "environments": {
    "development": {
      "database": {
        "host": "localhost",
        "port": 5432,
        "name": "dataflow_dev",
        "user": "dev_user",
        "password_env": "DEV_DB_PASSWORD",
        "pool_size": 5,
        "ssl_mode": "disable",
        "connection_timeout": 10,
        "statement_timeout": 30000,
        "idle_timeout": 600
      },
      "cache": {
        "provider": "redis",
        "host": "localhost",
        "port": 6379,
        "db_number": 0,
        "ttl_seconds": 300,
        "max_connections": 10,
        "key_prefix": "df_dev_"
      },
      "logging": {
        "level": "debug",
        "format": "json",
        "output": "stdout",
        "log_file": null,
        "include_timestamps": true,
        "include_request_id": true,
        "sentry_dsn": null
      },
      "api": {
        "base_url": "http://localhost:8000",
        "rate_limit": 1000,
        "rate_limit_window": 60,
        "cors_origins": ["http://localhost:3000"],
        "auth_provider": "local",
        "jwt_secret_env": "DEV_JWT_SECRET",
        "jwt_expiry_minutes": 1440,
        "api_key_header": "X-Api-Key"
      },
      "features": {
        "enable_websockets": true,
        "enable_graphql": true,
        "enable_batch_processing": false,
        "maintenance_mode": false,
        "debug_toolbar": true
      },
      "storage": {
        "provider": "local",
        "local_path": "/data/uploads/dev",
        "max_file_size_mb": 50,
        "allowed_extensions": ["jpg", "png", "pdf", "csv", "xlsx"],
        "cdn_url": null
      }
    },
    "staging": {
      "database": {
        "host": "staging-db.internal.dataflow.io",
        "port": 5432,
        "name": "dataflow_staging",
        "user": "staging_app",
        "password_env": "STAGING_DB_PASSWORD",
        "pool_size": 10,
        "ssl_mode": "require",
        "connection_timeout": 5,
        "statement_timeout": 15000,
        "idle_timeout": 300
      },
      "cache": {
        "provider": "redis",
        "host": "staging-redis.internal.dataflow.io",
        "port": 6379,
        "db_number": 0,
        "ttl_seconds": 600,
        "max_connections": 20,
        "key_prefix": "df_stg_"
      },
      "logging": {
        "level": "info",
        "format": "json",
        "output": "file",
        "log_file": "/var/log/dataflow/staging.log",
        "include_timestamps": true,
        "include_request_id": true,
        "sentry_dsn": "https://abc123@sentry.io/staging"
      },
      "api": {
        "base_url": "https://staging-api.dataflow.io",
        "rate_limit": 500,
        "rate_limit_window": 60,
        "cors_origins": ["https://staging.dataflow.io"],
        "auth_provider": "oauth2",
        "jwt_secret_env": "STAGING_JWT_SECRET",
        "jwt_expiry_minutes": 60,
        "api_key_header": "X-Api-Key"
      },
      "features": {
        "enable_websockets": true,
        "enable_graphql": true,
        "enable_batch_processing": true,
        "maintenance_mode": false,
        "debug_toolbar": false
      },
      "storage": {
        "provider": "s3",
        "s3_bucket": "dataflow-staging-uploads",
        "s3_region": "us-east-1",
        "max_file_size_mb": 100,
        "allowed_extensions": ["jpg", "png", "pdf", "csv", "xlsx"],
        "cdn_url": "https://cdn-staging.dataflow.io"
      }
    },
    "production": {
      "database": {
        "host": "prod-db-primary.internal.dataflow.io",
        "port": 5432,
        "name": "dataflow_prod",
        "user": "prod_app",
        "password_env": "PROD_DB_PASSWORD",
        "pool_size": 25,
        "ssl_mode": "verify-full",
        "connection_timeout": 3,
        "statement_timeout": 10000,
        "idle_timeout": 120,
        "read_replica_host": "prod-db-replica.internal.dataflow.io"
      },
      "cache": {
        "provider": "redis_cluster",
        "hosts": [
          "prod-redis-1.internal.dataflow.io",
          "prod-redis-2.internal.dataflow.io",
          "prod-redis-3.internal.dataflow.io"
        ],
        "port": 6379,
        "db_number": 0,
        "ttl_seconds": 900,
        "max_connections": 50,
        "key_prefix": "df_prod_"
      },
      "logging": {
        "level": "warn",
        "format": "json",
        "output": "file",
        "log_file": "/var/log/dataflow/production.log",
        "include_timestamps": true,
        "include_request_id": true,
        "sentry_dsn": "https://xyz789@sentry.io/production"
      },
      "api": {
        "base_url": "https://api.dataflow.io",
        "rate_limit": 200,
        "rate_limit_window": 60,
        "cors_origins": ["https://app.dataflow.io", "https://admin.dataflow.io"],
        "auth_provider": "oauth2",
        "jwt_secret_env": "PROD_JWT_SECRET",
        "jwt_expiry_minutes": 30,
        "api_key_header": "X-Api-Key"
      },
      "features": {
        "enable_websockets": true,
        "enable_graphql": true,
        "enable_batch_processing": true,
        "maintenance_mode": false,
        "debug_toolbar": false
      },
      "storage": {
        "provider": "s3",
        "s3_bucket": "dataflow-prod-uploads",
        "s3_region": "us-east-1",
        "max_file_size_mb": 250,
        "allowed_extensions": ["jpg", "png", "pdf", "csv", "xlsx"],
        "cdn_url": "https://cdn.dataflow.io"
      }
    }
  },
  "deprecated_settings": {
    "use_legacy_auth": true,
    "legacy_api_endpoint": "https://legacy-api.dataflow.io/v1",
    "enable_xml_export": false,
    "mongo_connection_string": "mongodb://legacy-mongo.internal.dataflow.io:27017/dataflow_legacy",
    "smtp_relay_host": "smtp-relay.internal.dataflow.io"
  }
}
SETTINGS_EOF

# ── MIGRATION_GUIDE.md ─────────────────────────────────────────────────────────
cat > MIGRATION_GUIDE.md << 'GUIDE_EOF'
# Configuration Migration Guide: JSON v2.x to YAML v3.0

This guide describes how to migrate the legacy `config/settings.json` (v2.x format)
to the new per-environment YAML configuration files (v3.0 format). The migration
script should read the JSON file and produce one YAML file per environment, plus
a migration report.

## Output Files

- `config/development.yaml`
- `config/staging.yaml`
- `config/production.yaml`
- `migration-report.md`

---

## Field Mapping Reference

### Top-Level Application Metadata

| Old Path (JSON)        | New Path (YAML)               | Notes                              |
|------------------------|-------------------------------|------------------------------------|
| `app_name`             | `application.name`            | Direct rename                      |
| `version`              | `application.config_version`  | Set to `"3.0"` (not the old value) |

Each output YAML file must include the `application` block at the top.

### Database (`environments.{env}.database` -> `persistence.database`)

| Old Path                    | New Path                                     | Notes                                |
|-----------------------------|----------------------------------------------|--------------------------------------|
| `database.host`             | `persistence.database.primary_host`          | Renamed                              |
| `database.port`             | `persistence.database.port`                  | Unchanged                            |
| `database.name`             | `persistence.database.name`                  | Unchanged                            |
| `database.user`             | `persistence.database.credentials.username`  | Moved into credentials block         |
| `database.password_env`     | `persistence.database.credentials.password_env` | Moved into credentials block      |
| `database.pool_size`        | `persistence.database.connection_pool.size`  | Moved into connection_pool block     |
| `database.connection_timeout` | `persistence.database.connection_pool.timeout_seconds` | Renamed, moved          |
| `database.statement_timeout` | `persistence.database.connection_pool.statement_timeout_ms` | Renamed, moved       |
| `database.idle_timeout`     | `persistence.database.connection_pool.idle_timeout_seconds` | Renamed, moved        |
| `database.ssl_mode`         | `persistence.database.tls.mode`              | Renamed section                      |
| `database.read_replica_host`| `persistence.database.replicas[0].host`      | Wrapped in replicas list             |

**Note**: If `read_replica_host` is present (production only), create a `replicas`
list with a single entry: `- host: <value>`, `role: read`. If it is absent, omit the
`replicas` key entirely.

### Cache (`environments.{env}.cache` -> `persistence.cache`)

| Old Path              | New Path                                   | Notes                               |
|-----------------------|--------------------------------------------|---------------------------------------|
| `cache.provider`      | `persistence.cache.backend`                | Renamed                              |
| `cache.host`          | `persistence.cache.connection.host`        | Moved into connection block           |
| `cache.hosts`         | `persistence.cache.connection.hosts`       | Moved into connection block (cluster) |
| `cache.port`          | `persistence.cache.connection.port`        | Moved into connection block           |
| `cache.db_number`     | `persistence.cache.connection.database`    | Renamed                              |
| `cache.max_connections`| `persistence.cache.connection.pool_size`  | Renamed                              |
| `cache.ttl_seconds`   | `persistence.cache.defaults.ttl_seconds`   | Moved into defaults block            |
| `cache.key_prefix`    | `persistence.cache.defaults.key_prefix`    | Moved into defaults block            |

**Note**: Use `connection.host` for single-server setups and `connection.hosts` for
cluster setups. Include whichever is present in the source; do not include both.

### Logging (`environments.{env}.logging` -> `observability.logging`)

| Old Path                  | New Path                                    | Notes                          |
|---------------------------|---------------------------------------------|--------------------------------|
| `logging.level`           | `observability.logging.level`               | Unchanged                      |
| `logging.format`          | `observability.logging.format`              | Unchanged                      |
| `logging.output`          | `observability.logging.sink.type`           | Renamed, moved into sink block |
| `logging.log_file`        | `observability.logging.sink.path`           | Renamed, moved into sink block |
| `logging.include_timestamps` | `observability.logging.fields.timestamp` | Renamed, moved into fields     |
| `logging.include_request_id` | `observability.logging.fields.request_id`| Renamed, moved into fields     |
| `logging.sentry_dsn`      | `observability.logging.error_tracking.dsn` | Moved into error_tracking      |

**Note**: If `log_file` is `null` and output is `stdout`, omit `sink.path` from the
YAML. Similarly, if `sentry_dsn` is `null`, omit the entire `error_tracking` block.
Null values should never appear in the output YAML.

### API (`environments.{env}.api` -> split: `server` + `security`)

The old `api` block is split across two top-level sections:

**Server settings:**

| Old Path              | New Path                              | Notes                         |
|-----------------------|---------------------------------------|-------------------------------|
| `api.base_url`        | `server.base_url`                    | Moved to server block         |
| `api.rate_limit`      | `server.rate_limiting.requests`      | Renamed, restructured         |
| `api.rate_limit_window`| `server.rate_limiting.window_seconds`| Renamed, restructured         |
| `api.cors_origins`    | `server.cors.allowed_origins`        | Renamed, restructured         |

**Security settings:**

| Old Path              | New Path                                  | Notes                     |
|-----------------------|-------------------------------------------|---------------------------|
| `api.auth_provider`   | `security.authentication.provider`        | Restructured              |
| `api.jwt_secret_env`  | `security.jwt.secret_env`                 | Moved into jwt block      |
| `api.jwt_expiry_minutes`| `security.jwt.expiry_minutes`           | Moved into jwt block      |
| `api.api_key_header`  | `security.api_key.header_name`            | Renamed, restructured     |

### Features (`environments.{env}.features`)

Feature flags are simplified and some are relocated:

| Old Path                      | New Path                       | Notes                              |
|-------------------------------|--------------------------------|------------------------------------|
| `features.enable_websockets`  | `features.websockets`          | Simplified name (drop `enable_`)   |
| `features.enable_graphql`     | `features.graphql`             | Simplified name (drop `enable_`)   |
| `features.enable_batch_processing` | `features.batch_processing` | Simplified name (drop `enable_`) |
| `features.maintenance_mode`   | `server.maintenance_mode`      | Moved to server block              |
| `features.debug_toolbar`      | **DEPRECATED** -- drop entirely| Do not include in output; log in migration report |

### Storage (`environments.{env}.storage` -> `storage`)

| Old Path                 | New Path                       | Notes                              |
|--------------------------|--------------------------------|------------------------------------|
| `storage.provider`       | `storage.backend`              | Renamed                            |
| `storage.local_path`     | `storage.local.path`           | Only when backend is "local"       |
| `storage.s3_bucket`      | `storage.s3.bucket`            | Only when backend is "s3"          |
| `storage.s3_region`      | `storage.s3.region`            | Only when backend is "s3"          |
| `storage.max_file_size_mb`| `storage.limits.max_file_size_mb` | Moved into limits block         |
| `storage.allowed_extensions` | `storage.limits.allowed_extensions` | Moved into limits block      |
| `storage.cdn_url`        | `storage.cdn.base_url`         | Moved into cdn block               |

**Note**: Only include `storage.local` when backend is `"local"`, and only include
`storage.s3` when backend is `"s3"`. If `cdn_url` is `null`, omit the `cdn` block.

### Deprecated Settings (`deprecated_settings` -> DROPPED)

The entire `deprecated_settings` block must be **dropped** from the output YAML files.
None of these settings should appear in any environment configuration.

Each deprecated setting must be logged in the migration report with its old value:

- `use_legacy_auth` -- legacy authentication flag, superseded by `security.authentication.provider`
- `legacy_api_endpoint` -- old API endpoint, no longer needed
- `enable_xml_export` -- XML export removed in v3.0
- `mongo_connection_string` -- MongoDB backend removed in v3.0
- `smtp_relay_host` -- email relay moved to external service configuration

---

## Migration Report Format

The script must produce a `migration-report.md` file with the following sections:

1. **Header**: "# Configuration Migration Report"
2. **Summary**: Number of environments migrated, config version change (2.4.1 -> 3.0)
3. **Per-Environment Section**: For each environment, list:
   - Output file path
   - Number of settings migrated
   - Any environment-specific notes (e.g., production has read replicas)
4. **Deprecated Settings Dropped**: List every deprecated setting with its old value
   and the reason it was removed
5. **Warnings**: Any items that need manual review, including:
   - `debug_toolbar` was dropped (was `true` in development)
   - Password environment variables should be verified
   - `legacy_auth` was enabled -- confirm OAuth2 migration is complete

---

## General Rules

1. **Null values**: Never write `null` or `~` into YAML. If a value is null, omit the
   key entirely.
2. **Booleans**: Use `true`/`false` (lowercase YAML booleans), not `"true"`/`"false"`.
3. **Per-environment files**: Each environment gets its own YAML file. Do not combine
   environments into a single file.
4. **Comments**: YAML comments (lines starting with `#`) are encouraged to explain
   non-obvious mappings or warn about values that may need attention.
5. **Key ordering**: Follow the section order: `application`, `persistence`, `observability`,
   `server`, `security`, `features`, `storage`.
6. **Lists**: Use YAML block sequence syntax (dash-space) rather than flow syntax.
GUIDE_EOF

git add -A
git commit -q -m "initial: add legacy config and migration guide"
