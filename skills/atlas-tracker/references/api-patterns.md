# Atlas Tracker REST API Patterns

Use when you need to search nodes or fetch data directly via HTTP (not covered by plugin tools).

## Auth

Basic Auth with MD5-hashed password:
```bash
AUTH=$(echo -n "user@example.com:$(echo -n 'password' | md5sum | awk '{print $1}')" | base64 -w0)
curl -H "Authorization: Basic $AUTH" https://app.redforester.com/api/...
```

## Get map list
```bash
GET /api/maps
# Returns array of maps with id, name, root_node_id
```

## Search nodes in a map
```bash
POST /api/search
body: {"query": "search text", "map_ids": ["<mapId>"]}
# Returns: {"hits": [{"id": "...", "score": 9.1, "map_id": "..."}, ...]}
# Then read each candidate: GET /api/nodes/<nodeId>
```

## Get a single node
```bash
GET /api/nodes/<nodeId>
# Title is at: body.properties.global.title (HTML string)
```

## Notes
- Search returns only {id, score} — always fetch full node to confirm title
- 404 on node = wrong ID or no access
- 403 on write = node owned by another user
