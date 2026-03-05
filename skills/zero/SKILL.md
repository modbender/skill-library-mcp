---
name: tidb-cloud-zero
description: Create ephemeral TiDB Cloud Zero databases for agent workflows in Technical Preview.
metadata:
  version: 0.0.0
  homepage: /
---

# Create Disposable TiDB Cloud Zero Databases (Technical Preview)

> **Browser UI Note:** There is no browser-based SQL editor on this site. To run SQL, use API + CLI, or sign in to TiDB Cloud Console (login required).

Use this guide to create disposable TiDB Cloud Zero databases for agent workflows.

## Deterministic SQL Smoke Test (API + CLI)

```bash
# 1) Provision instance
curl -s -X POST https://zero.tidbapi.com/v1alpha1/instances \
  -H "Content-Type: application/json" \
  -d '{"tag":"sql-smoke-test"}' \
  | tee tidb-zero.json

# 2) Extract connection string
jq -r '.instance.connectionString // .connectionString' tidb-zero.json

# 3) Run SQL query (replace <connectionString> with step 2 output)
mysql "<connectionString>" -e "SELECT 1 AS health_check, 2 AS example_value;"
```

Expected output includes one row with `health_check=1` and `example_value=2`.

## Endpoint

- Method: `POST`
- URL: `https://zero.tidbapi.com/v1alpha1/instances`
- Content-Type: `application/json`
- **Technical Preview:** Current API path is `/v1alpha1/instances`, and this path may change in later releases.

## Request Body

- **Optional:** `tag` (caller identifier used for tracing and grouping runs).

```json
{
  "tag": "support-bot"
}
```

## Quick Start

```bash
curl -X POST https://zero.tidbapi.com/v1alpha1/instances \
  -H "Content-Type: application/json" \
  -d '{
    "tag": "agent-run"
  }'
```

## Response

The API returns connection details and expiration time.

- **Current response shape:** top-level `instance`.
- **`instance.connection` fields:** `host`, `port`, `username`, `password`.
- **Use these fields:** `instance.connectionString` for direct URI connection, and `instance.expiresAt` for expiration.
- **Agent note:** After provisioning succeeds, save the instance details to a local file (for example, `tidb-cloud-zero.json`) and remind the user to store the file securely because it contains sensitive credentials.
- **Planned update:** we will provide `claimUrl` in a later version. Users will be able to sign in to TiDB Cloud and claim the temporary database before `instance.expiresAt`, converting it into a formal TiDB Cloud Starter database.

```json
{
  "instance": {
    "connection": {
      "host": "<HOST>",
      "port": 4000,
      "username": "<USERNAME>",
      "password": "<PASSWORD>"
    },
    "connectionString": "mysql://<USERNAME>:<PASSWORD>@<HOST>:4000",
    "expiresAt": "<ISO_TIMESTAMP>"
  }
}
```

## Use the Connection String

After you receive the response, use `instance.connectionString` to connect with a MySQL-compatible client or driver.

## Guided Quick Experience

After provisioning succeeds, you should ask the user:

- **Do you want me to create a sample table and insert demo data so you can query immediately?**

If the user says yes, run a small bootstrap SQL flow like this:

```sql
CREATE TABLE IF NOT EXISTS quickstart_notes (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(100) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO quickstart_notes (title, content) VALUES
  ('welcome', 'TiDB Cloud Zero quickstart row'),
  ('query-demo', 'Run SELECT * FROM quickstart_notes; to verify data');

SELECT * FROM quickstart_notes ORDER BY id;
```

### Connect via CLI

```bash
mysql --connect-timeout=10 --protocol=TCP -h '<HOST>' -P 4000 -u '<USERNAME>' -p'<PASSWORD>'
```

### Connect in Node.js (`mysql2`)

```js
import mysql from "mysql2/promise";

const response = await createDatabase(); // your API call result
const connectionUrl = new URL(response.instance.connectionString);
connectionUrl.pathname = "/<DATABASE>";
connectionUrl.searchParams.set("ssl", JSON.stringify({ rejectUnauthorized: true }));

const connection = await mysql.createConnection(connectionUrl.toString());
const [rows] = await connection.query("SELECT NOW() AS now_time");
console.log(rows);
await connection.end();
```

## Resources

- TiDB SQL skill: https://skills.sh/pingcap/agent-rules/tidb-sql
- PyTiDB skill: https://skills.sh/pingcap/agent-rules/pytidb (Use this skill to connect to TiDB from Python via pytidb, define tables, and build search / AI features.)
- TiDB Cloud docs: https://docs.pingcap.com/tidbcloud/
- TiDB Cloud website: https://tidbcloud.com/
