# Solid HTTP Reference

Concrete curl examples for all standard Solid Protocol operations. All examples use these shell variables — set them from the output of `scripts/get-token.sh`:

```bash
TOKEN="eyJhbG..."
POD_URL="https://crawlout.io/example-agent/"
WEBID="https://crawlout.io/example-agent/profile/card#me"
SERVER_URL="https://crawlout.io"
```

## Authentication

Get a Bearer token:

```bash
TOKEN_JSON=$(scripts/get-token.sh --agent example-agent)
TOKEN=$(echo "$TOKEN_JSON" | jq -r '.token')
POD_URL=$(echo "$TOKEN_JSON" | jq -r '.podUrl')
WEBID=$(echo "$TOKEN_JSON" | jq -r '.webId')
```

**Token expiry:** Tokens last 600 seconds (10 minutes). Re-fetch if more than 8 minutes have elapsed since the last `get-token.sh` call.

## Read a Resource

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "${POD_URL}memory/notes.ttl"
```

The server returns the resource body with the appropriate `Content-Type` header.

## Write / Replace a Resource

Use PUT to create or overwrite a resource. Always set the correct `Content-Type`.

**Turtle (RDF):**
```bash
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: text/turtle" \
  --data-raw '@prefix schema: <http://schema.org/>.
<#note-1> a schema:Note;
  schema:text "User prefers bullet-point summaries";
  schema:dateCreated "2024-01-15".' \
  "${POD_URL}memory/notes.ttl"
```

**Plain text:**
```bash
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: text/plain" \
  -d "Key finding: the API rate limit is 100 req/min" \
  "${POD_URL}memory/summary.txt"
```

**JSON:**
```bash
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}' \
  "${POD_URL}memory/data.json"
```

## Delete a Resource

```bash
curl -s -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  "${POD_URL}memory/old-notes.ttl"
```

Returns 200 or 204 on success. 404 if the resource doesn't exist.

## Create a Container

Containers are like directories. Their URLs **must** end with `/`.

```bash
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: text/turtle" \
  -H 'Link: <http://www.w3.org/ns/ldp#BasicContainer>; rel="type"' \
  -d '' \
  "${POD_URL}memory/projects/"
```

## List Container Contents

GET a container URL to see its contents (returned as Turtle with `ldp:contains` triples):

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "${POD_URL}memory/"
```

The response includes `ldp:contains` entries for each resource in the container.

## Append Data (SPARQL Update — INSERT)

Use PATCH with `application/sparql-update` to add triples without replacing the whole resource:

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/sparql-update" \
  -d 'PREFIX schema: <http://schema.org/>
INSERT DATA {
  <#note-2> a schema:Note;
    schema:text "New finding from today";
    schema:dateCreated "2024-06-15".
}' \
  "${POD_URL}memory/notes.ttl"
```

## Modify Data (SPARQL Update — DELETE/INSERT)

Replace specific triples while leaving the rest intact:

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/sparql-update" \
  -d 'PREFIX schema: <http://schema.org/>
DELETE {
  <#note-1> schema:text "User prefers bullet-point summaries".
}
INSERT {
  <#note-1> schema:text "User prefers numbered lists".
}
WHERE {
  <#note-1> schema:text "User prefers bullet-point summaries".
}' \
  "${POD_URL}memory/notes.ttl"
```

## Access Control (WAC)

Solid uses **Web Access Control (WAC)**. Each resource can have an associated `.acl` resource that defines who can do what.

### Discover the ACL URL

```bash
curl -s -I -H "Authorization: Bearer $TOKEN" \
  "${POD_URL}shared/report.ttl" | grep -i 'link.*rel="acl"'
```

The `Link` header contains the ACL URL, e.g.:
```
Link: <https://crawlout.io/example-agent/shared/report.ttl.acl>; rel="acl"
```

If no ACL link is returned, the convention is to append `.acl` to the resource URL.

### Read Existing ACL

```bash
ACL_URL="${POD_URL}shared/report.ttl.acl"
curl -s -H "Authorization: Bearer $TOKEN" "$ACL_URL"
```

Returns 404 if no ACL has been set (resource inherits from parent container).

### Grant Access to Another Agent

Write a complete ACL document. **Always include an owner rule** so you don't lock yourself out.

```bash
ACL_URL="${POD_URL}shared/report.ttl.acl"
GRANTEE_WEBID="https://crawlout.io/example-collaborator/profile/card#me"
RESOURCE_URL="${POD_URL}shared/report.ttl"

curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: text/turtle" \
  --data-raw "@prefix acl: <http://www.w3.org/ns/auth/acl#>.
@prefix foaf: <http://xmlns.com/foaf/0.1/>.

<#owner>
    a acl:Authorization;
    acl:agent <${WEBID}>;
    acl:accessTo <${RESOURCE_URL}>;
    acl:mode acl:Read, acl:Write, acl:Control.

<#grantee>
    a acl:Authorization;
    acl:agent <${GRANTEE_WEBID}>;
    acl:accessTo <${RESOURCE_URL}>;
    acl:mode acl:Read." \
  "$ACL_URL"
```

**Valid modes:** `acl:Read`, `acl:Write`, `acl:Append`, `acl:Control`

### Revoke Access

To revoke a specific agent's access, PUT a new ACL document that omits their rule (keep the owner rule):

```bash
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: text/turtle" \
  --data-raw "@prefix acl: <http://www.w3.org/ns/auth/acl#>.
@prefix foaf: <http://xmlns.com/foaf/0.1/>.

<#owner>
    a acl:Authorization;
    acl:agent <${WEBID}>;
    acl:accessTo <${RESOURCE_URL}>;
    acl:mode acl:Read, acl:Write, acl:Control." \
  "$ACL_URL"
```

### Grant Public Read Access

Allow anyone (unauthenticated) to read a resource:

```bash
curl -s -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: text/turtle" \
  --data-raw "@prefix acl: <http://www.w3.org/ns/auth/acl#>.
@prefix foaf: <http://xmlns.com/foaf/0.1/>.

<#owner>
    a acl:Authorization;
    acl:agent <${WEBID}>;
    acl:accessTo <${RESOURCE_URL}>;
    acl:mode acl:Read, acl:Write, acl:Control.

<#public>
    a acl:Authorization;
    acl:agentClass foaf:Agent;
    acl:accessTo <${RESOURCE_URL}>;
    acl:mode acl:Read." \
  "$ACL_URL"
```

## Tips

- **Use `--data-raw` instead of `-d` for Turtle content.** Curl's `-d` flag treats a leading `@` as a file path reference. Since Turtle content starts with `@prefix`, using `-d` sends empty content. `--data-raw` sends the string literally.
- **Trailing slashes matter:** Container URLs end with `/`, resource URLs don't.
- **Content-Type is required** on PUT and PATCH — the server rejects requests without it.
- **Check HTTP status codes:** 200/201/204 = success, 401 = expired token, 403 = no access, 404 = not found, 409 = conflict.
- **Turtle syntax:** Prefixes with `@prefix`, URIs in `<angle-brackets>`, statements end with `.`
