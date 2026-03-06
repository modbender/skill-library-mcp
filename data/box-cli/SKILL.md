---
description: Box CLI skill for working with files, folders, metadata,
  search, and Box AI in headless environments.
homepage: "https://developer.box.com/guides/cli/"
metadata:
  openclaw:
    emoji: 📦
    install:
    - bins:
      - box
      global: true
      id: npm
      kind: npm
      label: Install Box CLI (npm)
      package: "@box/cli"
    requires:
      bins:
      - box
name: box
---

# box

Use the official `box` CLI to interact with the Box API from OpenClaw.

This skill is designed for headless deployments (e.g. Railway, CI,
servers). It does not use OAuth login flows or short-lived developer
tokens.

Instead, it expects Bring Your Own Credentials using:

-   Client Credentials Grant (CCG) --- recommended
-   JWT Server Auth --- optional

------------------------------------------------------------------------

# 🔐 Authentication (Bring Your Own Credentials)

This skill does not manage authentication automatically.

You must provide credentials before using Box commands.

⚠️ Never commit credential files (CCG JSON or JWT JSON) to git.

Add the following to your `.gitignore`:

    box-ccg.json
    box-jwt.json
    .secrets/

------------------------------------------------------------------------

## 🔑 User-Provided JSON Configuration (Required)

Users must supply their own Box CCG configuration file.\
The skill does **not** generate credentials or manage secrets.

Your file should look like:

``` json
{
  "boxAppSettings": {
    "clientID": "client_id_here",
    "clientSecret": "client_secret_here"
  },
  "enterpriseID": "enterprise_id_here"
}
```

This file can be named `box-ccg.json` and placed in your deployment
environment before registering it with Box CLI.

------------------------------------------------------------------------

## Option A --- Provide a CCG Config File (Recommended)

Create a Box Custom App using:

Server Authentication (Client Credentials Grant)

You will need:

-   clientID
-   clientSecret
-   enterpriseID

Create your config file in a secure location outside the workspace, e.g.:

/data/.secrets/box-ccg.json

⚠️ Avoid storing credentials inside the workspace directory — it may be tracked by git or accessible to other tools.

With:

{ "boxAppSettings": { "clientID": "YOUR_CLIENT_ID", "clientSecret":
"YOUR_CLIENT_SECRET" }, "enterpriseID": "YOUR_ENTERPRISE_ID" }

Secure it:

chmod 600 /data/.secrets/box-ccg.json

Register it:

box configure:environments:add /data/.secrets/box-ccg.json --ccg-auth
--name ccg --set-as-current box configure:environments:set-current ccg

Optional: Run as a managed user instead of the service account:

box configure:environments:add /data/.secrets/box-ccg.json --ccg-auth
--ccg-user "USER_ID" --name ccg-user --set-as-current

------------------------------------------------------------------------

## Option B --- Use Environment Variables (.env supported)

Set:

BOX_CLIENT_ID BOX_CLIENT_SECRET BOX_ENTERPRISE_ID

Generate config:

mkdir -p /data/.secrets

cat <<EOF > /data/.secrets/box-ccg.json
{
  "boxAppSettings": {
    "clientID": "$BOX_CLIENT_ID",
    "clientSecret": "$BOX_CLIENT_SECRET"
  },
  "enterpriseID": "$BOX_ENTERPRISE_ID"
}
EOF

chmod 600 /data/.secrets/box-ccg.json

Then register:

box configure:environments:add /data/.secrets/box-ccg.json --ccg-auth
--name ccg --set-as-current

------------------------------------------------------------------------

## Option C --- JWT Server Auth (Alternative)

If using JWT:

box configure:environments:add /data/.secrets/box-jwt.json --name jwt
--set-as-current

------------------------------------------------------------------------

# ✅ Verify Authentication

box configure:environments:get --current box users:get me

Note: With CCG, you are authenticated as either: - The service account,
or - A managed user (if --ccg-user is used)

Access depends on that identity's permissions.

------------------------------------------------------------------------

# 📂 Common Operations

## Browse Folders

box folders:get 0 box folders:list-items 0 --json

## Upload

box files:upload ./report.pdf --parent-id 0

## Download

box files:download 123456789 --destination ./downloads --create-path

## Search

box search "quarterly plan" --type file

## Metadata

box files:metadata:get-all 123456789 box files:metadata:add 123456789
--template-key employeeRecord --data "department=Sales"

------------------------------------------------------------------------

# 🤖 Box AI Usage (No Local LLM Downloads)

This skill supports using Box AI directly via the Box platform.

AI operations run within Box, respecting: - File permissions -
Enterprise security - Data governance - Audit controls

No file download + local LLM inference required.

------------------------------------------------------------------------

## Ask Questions About a File

box ai:ask --item-id 123456789 --item-type file --prompt "Summarize this
document and identify risks."

------------------------------------------------------------------------

## Extract Structured Data

box ai:extract-structured --item-id 123456789 --item-type file --schema
'{"fields":\[{"name":"invoice_number","type":"string"},{"name":"total","type":"number"}\]}'

------------------------------------------------------------------------

## Extract Text

box ai:extract --item-id 123456789 --item-type file

------------------------------------------------------------------------

# 🧠 Tips for Agents & Automation

Use JSON output when parsing results:

box folders:list-items 0 --json

Prefer CCG for headless deployments because:

-   No browser required
-   No expiring developer tokens
-   Suitable for automation
-   Works cleanly in Railway

------------------------------------------------------------------------

# 🔒 Security Notes

-   Do not commit credential files.
-   Restrict file permissions (chmod 600).
-   Use least-privilege app scopes.
-   Avoid granting broad enterprise-wide access to service accounts.
-   Prefer a dedicated demo folder when showcasing functionality.

------------------------------------------------------------------------

# 🚀 Deployment Notes (Railway / CI)

-   Ensure /data/workspace is writable (for file operations).
-   Ensure /data/.secrets exists and is writable (for credential storage).
-   Box CLI stores environments in \~/.box.
-   If containers are ephemeral, re-run configure step on deploy.
-   Use Railway Variables instead of pasting secrets into chat.

------------------------------------------------------------------------

This skill exposes the full surface area of the Box CLI.

Explore commands:

box --help box folders --help box files --help box ai --help
