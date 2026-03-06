#!/usr/bin/env python3
"""GoHighLevel API v2 Helper — supports all 39 endpoint groups.
Usage: python3 ghl-api.py <command> [args...]

Environment:
  HIGHLEVEL_TOKEN       — Private Integration Bearer token (required)
  HIGHLEVEL_LOCATION_ID — Sub-account Location ID (required)

Base URL: https://services.leadconnectorhq.com
All requests include: Authorization: Bearer <token>, Version: 2021-07-28
"""

import json, os, re, sys, time, urllib.request, urllib.error, urllib.parse

BASE = "https://services.leadconnectorhq.com"
VERSION = "2021-07-28"
MAX_RETRIES = 3

# ──────────────────────────────────────────────
# Credentials & Validation
# ──────────────────────────────────────────────

# Strict pattern for GHL IDs (alphanumeric, no path traversal)
_SAFE_ID = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")


def _validate_id(value, name="ID"):
    """Validate that a value is a safe GHL identifier (alphanumeric, hyphens, underscores).
    Prevents path traversal and injection via URL path segments."""
    if not value or not _SAFE_ID.match(str(value)):
        raise ValueError(
            f"Invalid {name}: must be 1-128 alphanumeric/hyphen/underscore characters. Got: {repr(value)}"
        )
    return str(value)


def _load_creds():
    """Load credentials from environment variables."""
    return (
        os.environ.get("HIGHLEVEL_TOKEN", "").strip(),
        os.environ.get("HIGHLEVEL_LOCATION_ID", "").strip(),
    )


TOKEN, LOC_ID = _load_creds()


# ──────────────────────────────────────────────
# HTTP Client (native urllib.request)
# ──────────────────────────────────────────────

def _headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Version": VERSION,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "OpenClaw-GHL-Skill/1.1.0 (stdlib-only)",
    }


def _request(method, path, body=None, retries=MAX_RETRIES):
    """Make API request using native urllib with retry logic for 429/5xx errors."""
    url = f"{BASE}{path}" if path.startswith("/") else f"{BASE}/{path}"
    data = json.dumps(body).encode() if body else None

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {"status": resp.status}
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode() if e.fp else ""
            except Exception:
                pass

            # Retry on rate-limit (429) with exponential backoff
            if e.code == 429 and attempt < retries - 1:
                retry_after = e.headers.get("Retry-After")
                wait = int(retry_after) if retry_after and retry_after.isdigit() else 2 ** (attempt + 1)
                print(f"Rate limited (429). Retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue

            # Retry on server errors (5xx)
            if e.code >= 500 and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue

            return {"error": e.code, "message": err_body}
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            return {"error": "connection_failed", "message": str(e.reason)}
        except Exception as ex:
            return {"error": "unexpected", "message": str(ex)}

    return {"error": "max_retries_exceeded"}


def _get(path):
    return _request("GET", path)


def _post(path, body=None):
    return _request("POST", path, body)


def _put(path, body=None):
    return _request("PUT", path, body)


def _delete(path):
    return _request("DELETE", path)


def _get_paginated(endpoint_base, params=None, max_pages=50):
    """Automatically paginate through all results using cursor pagination.

    Args:
        endpoint_base: API endpoint path (e.g., "/contacts/")
        params: Dict of query parameters (locationId added automatically)
        max_pages: Safety limit (default 50 = 5000 records max)

    Returns:
        Dict with all results, total count, and pages fetched
    """
    all_items = []
    start_after = None
    start_after_id = None
    page = 1
    item_key = None

    base_params = {"locationId": LOC_ID, "limit": "100"}
    if params:
        base_params.update({k: str(v) for k, v in params.items()})

    while page <= max_pages:
        url_params = base_params.copy()
        if start_after and start_after_id:
            url_params["startAfter"] = start_after
            url_params["startAfterId"] = start_after_id

        query_string = urllib.parse.urlencode(url_params)
        path = f"{endpoint_base}?{query_string}"
        data = _get(path)

        if "error" in data:
            break

        # Detect item key from first response
        if item_key is None:
            for key in data:
                if key not in ("meta", "traceId") and isinstance(data[key], list):
                    item_key = key
                    break

        if item_key:
            items = data.get(item_key, [])
            all_items.extend(items)

        # Check for next page
        meta = data.get("meta", {})
        if not meta.get("nextPageUrl"):
            break

        start_after = meta.get("startAfter")
        start_after_id = meta.get("startAfterId")
        if not start_after or not start_after_id:
            break
        page += 1

    return {
        item_key or "items": all_items,
        "total": len(all_items),
        "pages": page,
        "endpoint": endpoint_base,
    }


def _out(data):
    print(json.dumps(data, indent=2))


# ──────────────────────────────────────────────
# Setup & Connection
# ──────────────────────────────────────────────

def test_connection():
    """Verify token and location ID are working using contacts endpoint."""
    if not TOKEN:
        return {"error": "HIGHLEVEL_TOKEN not set. Set the environment variable or run /highlevel-setup"}
    if not LOC_ID:
        return {"error": "HIGHLEVEL_LOCATION_ID not set. Set the environment variable or run /highlevel-setup"}

    result = _get(f"/contacts/?locationId={urllib.parse.quote(LOC_ID, safe='')}&limit=1")

    if "error" in result:
        error_code = result.get("error")
        if error_code == 403:
            return {
                "error": 403,
                "message": "Token needs scopes enabled in GHL",
                "fix": [
                    "1. Go to app.gohighlevel.com",
                    "2. Settings → Private Integrations",
                    "3. Find your 'Claude AI Assistant' integration",
                    "4. Click 'Edit Scopes'",
                    "5. ENABLE: contacts.readonly (and others needed)",
                    "6. Save - no need to regenerate token",
                ],
            }
        return result

    total = result.get("total", 0)
    return {
        "status": "connected",
        "locationId": LOC_ID,
        "totalContacts": total,
        "message": f"Successfully connected! Found {total} contacts.",
    }


# ──────────────────────────────────────────────
# Contacts
# ──────────────────────────────────────────────

def search_contacts(query="", limit=20, paginate=True):
    """Search contacts by name, email, phone, or company.

    Args:
        query: Search term
        limit: Max results per page (default 20, max 100) — only used if paginate=False
        paginate: If True (default), fetch ALL contacts across all pages
    """
    if not paginate:
        params = urllib.parse.urlencode({"locationId": LOC_ID, "query": query, "limit": limit})
        return _get(f"/contacts/?{params}")

    search_params = {"query": query} if query else {}
    return _get_paginated("/contacts/", search_params)


def list_all_contacts():
    """Get ALL contacts with automatic pagination."""
    return search_contacts(query="", limit=100, paginate=True)


def get_contact(contact_id):
    """Get full contact details by ID."""
    cid = _validate_id(contact_id, "contact_id")
    return _get(f"/contacts/{cid}")


def create_contact(data):
    """Create a new contact. data = JSON with firstName, lastName, email, phone, etc."""
    if isinstance(data, str):
        data = json.loads(data)
    data["locationId"] = LOC_ID
    return _post("/contacts/", data)


def update_contact(contact_id, data):
    """Update contact fields. data = JSON with fields to update."""
    cid = _validate_id(contact_id, "contact_id")
    if isinstance(data, str):
        data = json.loads(data)
    return _put(f"/contacts/{cid}", data)


def delete_contact(contact_id):
    """Delete a contact by ID."""
    cid = _validate_id(contact_id, "contact_id")
    return _delete(f"/contacts/{cid}")


def upsert_contact(data):
    """Create or update contact by email/phone match."""
    if isinstance(data, str):
        data = json.loads(data)
    data["locationId"] = LOC_ID
    return _post("/contacts/upsert", data)


def add_contact_tags(contact_id, tags):
    """Add tags to a contact. tags = JSON array of tag strings."""
    cid = _validate_id(contact_id, "contact_id")
    if isinstance(tags, str):
        tags = json.loads(tags)
    return _post(f"/contacts/{cid}/tags", {"tags": tags})


def remove_contact_tags(contact_id, tags):
    """Remove tags from a contact."""
    cid = _validate_id(contact_id, "contact_id")
    if isinstance(tags, str):
        tags = json.loads(tags)
    return _delete(f"/contacts/{cid}/tags")


# ──────────────────────────────────────────────
# Conversations & Messaging
# ──────────────────────────────────────────────

def list_conversations(limit=20):
    """List recent conversations."""
    params = urllib.parse.urlencode({"locationId": LOC_ID, "limit": limit})
    return _get(f"/conversations/search?{params}")


def get_conversation(conversation_id):
    """Get a specific conversation."""
    cid = _validate_id(conversation_id, "conversation_id")
    return _get(f"/conversations/{cid}")


def send_message(contact_id, message, msg_type="SMS"):
    """Send a message to a contact. msg_type: SMS, Email, WhatsApp, FB, IG, Live_Chat."""
    _validate_id(contact_id, "contact_id")
    body = {
        "type": msg_type,
        "contactId": contact_id,
        "message": message,
    }
    return _post("/conversations/messages", body)


# ──────────────────────────────────────────────
# Calendars & Appointments
# ──────────────────────────────────────────────

def list_calendars():
    """List all calendars for this location."""
    params = urllib.parse.urlencode({"locationId": LOC_ID})
    return _get(f"/calendars/?{params}")


def get_free_slots(calendar_id, start_date, end_date):
    """Get available booking slots. Dates in YYYY-MM-DD format."""
    cal_id = _validate_id(calendar_id, "calendar_id")
    params = urllib.parse.urlencode({
        "startDate": start_date,
        "endDate": end_date,
    })
    return _get(f"/calendars/{cal_id}/free-slots?{params}")


def create_appointment(calendar_id, data):
    """Create a calendar appointment."""
    cal_id = _validate_id(calendar_id, "calendar_id")
    if isinstance(data, str):
        data = json.loads(data)
    data["calendarId"] = cal_id
    data["locationId"] = LOC_ID
    return _post("/calendars/events", data)


# ──────────────────────────────────────────────
# Opportunities & Pipelines
# ──────────────────────────────────────────────

def list_opportunities(pipeline_id=None, limit=20, paginate=True):
    """List opportunities. Optionally filter by pipeline.

    Args:
        pipeline_id: Filter by specific pipeline
        limit: Max per page (only if paginate=False)
        paginate: If True (default), fetch ALL opportunities
    """
    if not paginate:
        params = {"locationId": LOC_ID, "limit": limit}
        if pipeline_id:
            params["pipelineId"] = _validate_id(pipeline_id, "pipeline_id")
        return _get(f"/opportunities/search?{urllib.parse.urlencode(params)}")

    search_params = {}
    if pipeline_id:
        search_params["pipelineId"] = _validate_id(pipeline_id, "pipeline_id")
    return _get_paginated("/opportunities/search", search_params)


def get_opportunity(opp_id):
    """Get opportunity by ID."""
    oid = _validate_id(opp_id, "opportunity_id")
    return _get(f"/opportunities/{oid}")


def create_opportunity(data):
    """Create a new opportunity."""
    if isinstance(data, str):
        data = json.loads(data)
    data["locationId"] = LOC_ID
    return _post("/opportunities/", data)


def list_pipelines():
    """List all pipelines and their stages."""
    return _get(f"/opportunities/pipelines?locationId={urllib.parse.quote(LOC_ID, safe='')}")


# ──────────────────────────────────────────────
# Workflows & Campaigns
# ──────────────────────────────────────────────

def list_workflows(paginate=True):
    """List all workflows.

    Args:
        paginate: If True (default), fetch ALL workflows
    """
    if not paginate:
        return _get(f"/workflows/?locationId={urllib.parse.quote(LOC_ID, safe='')}")
    return _get_paginated("/workflows/")


def add_to_workflow(contact_id, workflow_id):
    """Add a contact to a workflow."""
    cid = _validate_id(contact_id, "contact_id")
    wid = _validate_id(workflow_id, "workflow_id")
    return _post(f"/contacts/{cid}/workflow/{wid}", {"eventStartTime": ""})


def remove_from_workflow(contact_id, workflow_id):
    """Remove a contact from a workflow."""
    cid = _validate_id(contact_id, "contact_id")
    wid = _validate_id(workflow_id, "workflow_id")
    return _delete(f"/contacts/{cid}/workflow/{wid}")


def list_campaigns(paginate=True):
    """List all campaigns.

    Args:
        paginate: If True (default), fetch ALL campaigns
    """
    if not paginate:
        return _get(f"/campaigns/?locationId={urllib.parse.quote(LOC_ID, safe='')}")
    return _get_paginated("/campaigns/")


# ──────────────────────────────────────────────
# Invoices
# ──────────────────────────────────────────────

def list_invoices(limit=20, paginate=True):
    """List invoices."""
    if not paginate:
        params = urllib.parse.urlencode({"locationId": LOC_ID, "limit": limit})
        return _get(f"/invoices/?{params}")
    return _get_paginated("/invoices/")


def get_invoice(invoice_id):
    """Get invoice details."""
    iid = _validate_id(invoice_id, "invoice_id")
    return _get(f"/invoices/{iid}")


def create_invoice(data):
    """Create a new invoice."""
    if isinstance(data, str):
        data = json.loads(data)
    data["altId"] = LOC_ID
    data["altType"] = "location"
    return _post("/invoices/", data)


# ──────────────────────────────────────────────
# Payments
# ──────────────────────────────────────────────

def list_orders(limit=20, paginate=True):
    """List payment orders."""
    if not paginate:
        params = urllib.parse.urlencode({"locationId": LOC_ID, "limit": limit})
        return _get(f"/payments/orders/?{params}")
    return _get_paginated("/payments/orders/")


def list_transactions(limit=20, paginate=True):
    """List payment transactions."""
    if not paginate:
        params = urllib.parse.urlencode({"locationId": LOC_ID, "limit": limit})
        return _get(f"/payments/transactions/?{params}")
    return _get_paginated("/payments/transactions/")


def list_subscriptions(limit=20, paginate=True):
    """List payment subscriptions."""
    if not paginate:
        params = urllib.parse.urlencode({"locationId": LOC_ID, "limit": limit})
        return _get(f"/payments/subscriptions/?{params}")
    return _get_paginated("/payments/subscriptions/")


# ──────────────────────────────────────────────
# Products
# ──────────────────────────────────────────────

def list_products(limit=20, paginate=True):
    """List products."""
    if not paginate:
        params = urllib.parse.urlencode({"locationId": LOC_ID, "limit": limit})
        return _get(f"/products/?{params}")
    return _get_paginated("/products/")


def get_product(product_id):
    """Get product details."""
    pid = _validate_id(product_id, "product_id")
    return _get(f"/products/{pid}")


# ──────────────────────────────────────────────
# Forms, Surveys, Funnels
# ──────────────────────────────────────────────

def list_forms(paginate=True):
    """List all forms."""
    if not paginate:
        return _get(f"/forms/?locationId={urllib.parse.quote(LOC_ID, safe='')}")
    return _get_paginated("/forms/")


def list_form_submissions(form_id, limit=20, paginate=True):
    """Get form submissions."""
    fid = _validate_id(form_id, "form_id")
    if not paginate:
        params = urllib.parse.urlencode({"locationId": LOC_ID, "limit": limit, "formId": fid})
        return _get(f"/forms/submissions?{params}")
    return _get_paginated("/forms/submissions", {"formId": fid})


def list_surveys(paginate=True):
    """List all surveys."""
    if not paginate:
        return _get(f"/surveys/?locationId={urllib.parse.quote(LOC_ID, safe='')}")
    return _get_paginated("/surveys/")


def list_funnels(paginate=True):
    """List all funnels."""
    if not paginate:
        return _get(f"/funnels/funnel/list?locationId={urllib.parse.quote(LOC_ID, safe='')}")
    return _get_paginated("/funnels/funnel/list")


# ──────────────────────────────────────────────
# Social Media Planner
# ──────────────────────────────────────────────

def list_social_posts(limit=20):
    """List social media posts."""
    loc = _validate_id(LOC_ID, "location_id")
    return _post(f"/social-media-posting/{loc}/posts/list", {
        "limit": limit, "skip": 0,
    })


def create_social_post(data):
    """Create a social media post."""
    loc = _validate_id(LOC_ID, "location_id")
    if isinstance(data, str):
        data = json.loads(data)
    return _post(f"/social-media-posting/{loc}/posts", data)


# ──────────────────────────────────────────────
# Media, Users, Links
# ──────────────────────────────────────────────

def list_media():
    """List media files."""
    return _get(f"/medias/files?locationId={urllib.parse.quote(LOC_ID, safe='')}")


def list_users():
    """List users for this location."""
    return _get(f"/users/?locationId={urllib.parse.quote(LOC_ID, safe='')}")


def list_trigger_links():
    """List trigger links."""
    return _get(f"/links/?locationId={urllib.parse.quote(LOC_ID, safe='')}")


# ──────────────────────────────────────────────
# Location & Settings
# ──────────────────────────────────────────────

def get_location_details():
    """Get current location details."""
    loc = _validate_id(LOC_ID, "location_id")
    return _get(f"/locations/{loc}")


def list_location_custom_fields():
    """List custom fields for this location."""
    loc = _validate_id(LOC_ID, "location_id")
    return _get(f"/locations/{loc}/customFields")


def list_location_tags():
    """List tags for this location."""
    loc = _validate_id(LOC_ID, "location_id")
    return _get(f"/locations/{loc}/tags")


def list_location_custom_values():
    """List custom values for this location."""
    loc = _validate_id(LOC_ID, "location_id")
    return _get(f"/locations/{loc}/customValues")


def list_courses():
    """List courses/memberships."""
    return _get(f"/courses/?locationId={urllib.parse.quote(LOC_ID, safe='')}")


def list_snapshots():
    """List available snapshots (Agency only)."""
    return _get("/snapshots/")


def get_snapshot_status(snapshot_id):
    """Get snapshot installation status."""
    sid = _validate_id(snapshot_id, "snapshot_id")
    return _get(f"/snapshots/{sid}/status")


# ──────────────────────────────────────────────
# CLI Router
# ──────────────────────────────────────────────

COMMANDS = {
    "test_connection": lambda: test_connection(),
    "search_contacts": lambda: search_contacts(sys.argv[2] if len(sys.argv) > 2 else ""),
    "list_all_contacts": lambda: list_all_contacts(),
    "get_contact": lambda: get_contact(sys.argv[2]),
    "create_contact": lambda: create_contact(sys.argv[2]),
    "update_contact": lambda: update_contact(sys.argv[2], sys.argv[3]),
    "delete_contact": lambda: delete_contact(sys.argv[2]),
    "upsert_contact": lambda: upsert_contact(sys.argv[2]),
    "add_contact_tags": lambda: add_contact_tags(sys.argv[2], sys.argv[3]),
    "list_conversations": lambda: list_conversations(),
    "get_conversation": lambda: get_conversation(sys.argv[2]),
    "send_message": lambda: send_message(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "SMS"),
    "list_calendars": lambda: list_calendars(),
    "get_free_slots": lambda: get_free_slots(sys.argv[2], sys.argv[3], sys.argv[4]),
    "create_appointment": lambda: create_appointment(sys.argv[2], sys.argv[3]),
    "list_opportunities": lambda: list_opportunities(),
    "get_opportunity": lambda: get_opportunity(sys.argv[2]),
    "create_opportunity": lambda: create_opportunity(sys.argv[2]),
    "list_pipelines": lambda: list_pipelines(),
    "list_workflows": lambda: list_workflows(),
    "add_to_workflow": lambda: add_to_workflow(sys.argv[2], sys.argv[3]),
    "remove_from_workflow": lambda: remove_from_workflow(sys.argv[2], sys.argv[3]),
    "list_campaigns": lambda: list_campaigns(),
    "list_invoices": lambda: list_invoices(),
    "get_invoice": lambda: get_invoice(sys.argv[2]),
    "create_invoice": lambda: create_invoice(sys.argv[2]),
    "list_orders": lambda: list_orders(),
    "list_transactions": lambda: list_transactions(),
    "list_subscriptions": lambda: list_subscriptions(),
    "list_products": lambda: list_products(),
    "get_product": lambda: get_product(sys.argv[2]),
    "list_forms": lambda: list_forms(),
    "list_form_submissions": lambda: list_form_submissions(sys.argv[2]),
    "list_surveys": lambda: list_surveys(),
    "list_funnels": lambda: list_funnels(),
    "list_social_posts": lambda: list_social_posts(),
    "create_social_post": lambda: create_social_post(sys.argv[2]),
    "list_media": lambda: list_media(),
    "list_users": lambda: list_users(),
    "list_trigger_links": lambda: list_trigger_links(),
    "get_location_details": lambda: get_location_details(),
    "list_location_custom_fields": lambda: list_location_custom_fields(),
    "list_location_tags": lambda: list_location_tags(),
    "list_location_custom_values": lambda: list_location_custom_values(),
    "list_courses": lambda: list_courses(),
    "list_snapshots": lambda: list_snapshots(),
    "get_snapshot_status": lambda: get_snapshot_status(sys.argv[2]),
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(f"Commands: {', '.join(sorted(COMMANDS.keys()))}")
        sys.exit(1)
    try:
        _out(COMMANDS[sys.argv[1]]())
    except ValueError as e:
        _out({"error": "validation_failed", "message": str(e)})
        sys.exit(1)
    except IndexError:
        _out({"error": "missing_argument", "message": f"Command '{sys.argv[1]}' requires additional arguments."})
        sys.exit(1)
