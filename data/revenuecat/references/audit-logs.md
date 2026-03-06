# Audit Log

Operations about audit logs.

## Endpoints

### GET /projects/{project_id}/audit_logs

List audit logs

- **Params:** project_id (path, required) — ID of the project (e.g., "proj1ab2c3d4")
- **Query:** starting_after (query, optional) — Cursor for pagination. Returns audit logs after the specified audit log ID, using descending order by audit log ID. (e.g., "log1ab2c3d4e5"), start_date (query, optional) — Start date for the data range (ISO 8601 format) (e.g., "2024-01-01"), end_date (query, optional) — End date for the data range (ISO 8601 format) (e.g., "2024-12-31"), limit (query, optional, default: 20) (e.g., 10)
- **Response:**
  - object: enum: list (required) — String representing the object's type. Objects of the same type share the same value. Always has the value `list`.
  - items: array (required) — Details about each audit log.
  - next_page: string, nullable (required) — URL to access the next page of the project's audit logs. If not present / null, there is no next page. (e.g., "/v2/projects/proj1ab2c3d4/audit_logs?starting_after=log1ab2c3d4e5")
  - url: string (required) — The URL where this list can be accessed. (e.g., "/v2/projects/proj1ab2c3d4/audit_logs")
- **Status:** public
