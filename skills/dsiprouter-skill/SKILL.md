---
name: dsiprouter
description: Call the dSIPRouter REST API using the Postman collection (curl + jq).
metadata: {"openclaw":{"emoji":"📡","requires":{"bins":["curl","jq"],"env":["DSIP_ADDR","DSIP_TOKEN"]}}}
---

# dSIPRouter API skill

This skill is generated from the Postman collection and provides:
- a safe `curl` calling convention
- a `bin/dsiprouter.sh` helper CLI with subcommands for the collection’s requests
- example payloads (where present in Postman)

## Required environment

- `DSIP_ADDR` — hostname/IP of your dSIPRouter node (no scheme)
- `DSIP_TOKEN` — API bearer token
- Optional: `DSIP_INSECURE=1` to allow self-signed TLS (adds `-k`)

Base URL:
- `https://$DSIP_ADDR:5000/api/v1`

Auth header:
- `Authorization: Bearer $DSIP_TOKEN`

## Safe calling convention

```bash
dsip_api() {
  local method="$1"; shift
  local path="$1"; shift

  local insecure=()
  if [ "${DSIP_INSECURE:-}" = "1" ]; then insecure=(-k); fi

  curl "${insecure[@]}" --silent --show-error --fail-with-body \
    --connect-timeout 5 --max-time 30 \
    -H "Authorization: Bearer ${DSIP_TOKEN}" \
    -H "Content-Type: application/json" \
    -X "${method}" "https://${DSIP_ADDR}:5000${path}" \
    "$@"
}
```

## Preferred usage: the bundled helper CLI

```bash
# list subcommands
dsiprouter.sh help

# list endpoint groups
dsiprouter.sh endpointgroups:list | jq .

# create inbound mapping with your own JSON payload
dsiprouter.sh inboundmapping:create '{"did":"13132222223","servers":["#22"],"name":"Taste Pizzabar"}' | jq .

# or send the Postman sample body
dsiprouter.sh inboundmapping:create --sample | jq .
```

## Kamailio

```bash
dsiprouter.sh kamailio:stats | jq .
dsiprouter.sh kamailio:reload | jq .
```

## Endpoint catalog (from Postman)

### endpointgroups
- `endpointgroups:list` → **GET** `/api/v1/endpointgroups`
- `endpointgroups:get` → **GET** `/api/v1/endpointgroups/9` — Get a single endpointgroup
- `endpointgroups:create` → **POST** `/api/v1/endpointgroups` — Create an endpointgroup
- `endpointgroups:create_1` → **POST** `/api/v1/endpointgroups` — Create an endpointgroup
- `endpointgroups:create_2` → **POST** `/api/v1/endpointgroups` — Create an endpointgroup
- `endpointgroups:create_3` → **POST** `/api/v1/endpointgroups` — Create an endpointgroup
- `endpointgroups:delete` → **DELETE** `/api/v1/endpointgroups/53` — Delete endpointgroup
- `endpointgroups:update` → **PUT** `/api/v1/endpointgroups/34` — Update an endpointgroup

### kamailio
- `kamailio:reload` → **POST** `/api/v1/reload/kamailio` — Trigger a reload of Kamailio.  This is needed after changes are made
- `kamailio:list` → **GET** `/api/v1/kamailio/stats` — Obtain call statistics

### inboundmapping
- `inboundmapping:list` → **GET** `/api/v1/inboundmapping` — Get a list of inboundmappings
- `inboundmapping:create` → **POST** `/api/v1/inboundmapping` — Create new inboundmapping
- `inboundmapping:update` → **PUT** `/api/v1/inboundmapping?did=13132222223` — Create new inboundmapping
- `inboundmapping:delete` → **DELETE** `/api/v1/inboundmapping?did=13132222223` — Create new inboundmapping

### leases
- `leases:list` → **GET** `/api/v1/lease/endpoint?email=mack@goflyball.com&ttl=5m` — Get a single endpointgroup
- `leases:list_1` → **GET** `/api/v1/lease/endpoint?email=mack@goflyball.com&ttl=1m&type=ip&auth_ip=172.145.24.2` — Get a single endpointgroup
- `leases:revoke` → **DELETE** `/api/v1/lease/endpoint/34/revoke` — Get a single endpointgroup

### carriergroups
- `carriergroups:list` → **GET** `/api/v1/carriergroups`
- `carriergroups:create` → **POST** `/api/v1/carriergroups`

### auth
- `auth:create` → **POST** `/api/v1/auth/user`
- `auth:update` → **PUT** `/api/v1/auth/user/2`
- `auth:delete` → **DELETE** `/api/v1/auth/user/2`
- `auth:list` → **GET** `/api/v1/auth/user`
- `auth:login` → **POST** `/api/v1/auth/login`

### cdr
- `cdr:get` → **GET** `/api/v1/cdrs/endpointgroups/17?type=csv&dtfilter=2022-09-14&email=True`
- `cdr:get_1` → **GET** `/api/v1/cdrs/endpoint/54`

## Included files

- `bin/dsiprouter.sh`
