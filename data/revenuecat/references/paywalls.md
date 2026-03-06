# Paywall

Operations about paywalls.

## Endpoints

### POST /projects/{project_id}/paywalls

Create a paywall

- **Params:** project_id (path, required) — ID of the project (e.g., "proj1ab2c3d4")
- **Body:**
  - offering_id: string (required) — The ID of the offering the paywall will be created for. (e.g., "ofrng123456789a")
- **Response:**
  - object: enum: paywall (required) — String representing the object's type. Objects of the same type share the same value.
  - id: string (required) — The id of the paywall (e.g., "pw123456789abcdef")
  - name: string, nullable (required) — The name of the paywall (e.g., "My Awesome Paywall")
  - offering_id: string (required) — The ID of the offering the paywall is for. (e.g., "ofrng123456789a")
  - created_at: integer(int64) (required) — The date the paywall was created at in ms since epoch (e.g., 1658399423658)
  - published_at: integer(int64), nullable (required) — The date the paywall was published at in ms since epoch (e.g., 1658399423958)
  - offering: object, nullable — The offering associated with this paywall. Expandable.
  - components: object, nullable — Published and draft components configurations for this paywall. Expandable.
- **Status:** public

### GET /projects/{project_id}/paywalls

Get a list of paywalls

- **Params:** project_id (path, required) — ID of the project (e.g., "proj1ab2c3d4")
- **Query:** starting_after (query, optional) (e.g., "ent12354"), limit (query, optional, default: 20) (e.g., 10), expand (query, optional) — Specifies which fields in the response should be expanded. Accepted values are: `items.offering` (requires `project_configuration:offerings:read` permission).
- **Response:**
  - object: enum: list (required) — String representing the object's type. Objects of the same type share the same value. Always has the value `list`.
  - items: array (required) — Details about each object.
  - next_page: string, nullable (required) — URL to access the next page of the project's paywalls. If not present / null, there is no next page (e.g., "/v2/projects/proj1ab2c3d4/paywalls?starting_after=pwXXXXXXXXXXXXXX")
  - url: string (required) — The URL where this list can be accessed. (e.g., "/v2/projects/proj1ab2c3d4/paywalls")
- **Status:** public

### DELETE /projects/{project_id}/paywalls/{paywall_id}

Delete a paywall

- **Params:** project_id (path, required) — ID of the project (e.g., "proj1ab2c3d4"), paywall_id (path, required) — ID of the paywall (e.g., "pwXXXXXXXXXXXXXX")
- **Response:**
  - object: enum: app, customer, entitlement, offering, package, paywall, product, virtual_currency, webhook_integration (required) — The type of the deleted object
  - id: string (required) — The ID of the deleted object
  - deleted_at: integer(int64) (required) — The date when the object was deleted in ms since epoch (e.g., 1658399423658)
- **Status:** public

### GET /projects/{project_id}/paywalls/{paywall_id}

Get a paywall

- **Params:** project_id (path, required) — ID of the project (e.g., "proj1ab2c3d4"), paywall_id (path, required) — ID of the paywall (e.g., "pwXXXXXXXXXXXXXX")
- **Query:** expand (query, optional) — Specifies which fields in the response should be expanded. Accepted values are: `offering` (requires `project_configuration:offerings:read` permission), `components` (requires `project_configuration:offerings:read` permission).
- **Response:**
  - object: enum: paywall (required) — String representing the object's type. Objects of the same type share the same value.
  - id: string (required) — The id of the paywall (e.g., "pw123456789abcdef")
  - name: string, nullable (required) — The name of the paywall (e.g., "My Awesome Paywall")
  - offering_id: string (required) — The ID of the offering the paywall is for. (e.g., "ofrng123456789a")
  - created_at: integer(int64) (required) — The date the paywall was created at in ms since epoch (e.g., 1658399423658)
  - published_at: integer(int64), nullable (required) — The date the paywall was published at in ms since epoch (e.g., 1658399423958)
  - offering: object, nullable — The offering associated with this paywall. Expandable.
  - components: object, nullable — Published and draft components configurations for this paywall. Expandable.
- **Status:** public
