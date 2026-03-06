#!/usr/bin/env python3
"""
IMA Image Creation Script — ima_image_create.py
Version: 1.0.0

Specialized script for image generation via IMA Open API.
Handles: product list query → virtual param resolution → task create → poll status

Usage:
  python3 ima_image_create.py \\
    --api-key  ima_xxx \\
    --task-type text_to_image \\
    --model-id  doubao-seedream-4.5 \\
    --prompt   "a cute puppy running on grass"

Supports image generation only:
  text_to_image | image_to_image

Production Models (as of 2026-02-27):
  - SeeDream 4.5 (doubao-seedream-4.5) — 5 pts, default recommended
  - Nano Banana Pro (gemini-3-pro-image) — 10/10/18 pts for 1K/2K/4K

Logs: ~/.openclaw/logs/ima_skills/ima_create_YYYYMMDD.log
"""

import argparse
import hashlib
import json
import mimetypes
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("requests not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)

# Import logger module
try:
    from ima_logger import setup_logger, cleanup_old_logs
    logger = setup_logger("ima_skills")
    cleanup_old_logs(days=7)
except ImportError:
    # Fallback: create basic logger if ima_logger not available
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-5s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger("ima_skills")

# ─── Constants ────────────────────────────────────────────────────────────────

# Primary API endpoint (owned by IMA Studio)
DEFAULT_BASE_URL = "https://api.imastudio.com"

# Image upload endpoint (owned by IMA Studio)
# Used for: image_to_image tasks
# Purpose: Upload images to OSS to obtain CDN URLs for image generation
# See SECURITY.md for full domain disclosure and privacy implications
DEFAULT_IM_BASE_URL = "https://imapi.liveme.com"

PREFS_PATH = os.path.expanduser("~/.openclaw/memory/ima_prefs.json")

# Poll interval (seconds) and max wait (seconds) per task type
# Image generation only
POLL_CONFIG = {
    "text_to_image":  {"interval": 5, "max_wait": 180},
    "image_to_image": {"interval": 5, "max_wait": 180},
}

# App Key configuration (for OSS upload authentication)
# These are shared keys used by all IMA skill-based uploads
# NOT a secret - visible in public source code
# Used to generate request signatures for imapi.liveme.com upload API
# See SECURITY.md § "Credentials" for security implications
APP_ID = "webAgent"
APP_KEY = "32jdskjdk320eew"

# Note: APP_UID and APP_TOKEN should be configured via environment variables
# They can be obtained from: POST /api/v3/login/app → data.user_id & data.token


# ─── HTTP helpers ─────────────────────────────────────────────────────────────

def make_headers(api_key: str, language: str = "en") -> dict:
    return {
        "Authorization":  f"Bearer {api_key}",
        "Content-Type":   "application/json",
        "x-app-source":   "ima_skills",
        "x_app_language": language,
    }


# ─── Image Upload (OSS) ───────────────────────────────────────────────────────

def _gen_sign() -> tuple[str, str, str]:
    """
    Generate per-request (sign, timestamp, nonce) for IM authentication.
    
    Returns:
        (sign, timestamp, nonce)
    """
    nonce = uuid.uuid4().hex[:21]
    ts = str(int(time.time()))
    raw = f"{APP_ID}|{APP_KEY}|{ts}|{nonce}"
    sign = hashlib.sha1(raw.encode()).hexdigest().upper()
    return sign, ts, nonce


def get_upload_token(api_key: str, suffix: str, 
                     content_type: str, im_base_url: str = DEFAULT_IM_BASE_URL) -> dict:
    """
    Step 1: Get presigned upload URL from IM platform (imapi.liveme.com).
    
    **Security Note**: This function sends your IMA API key to imapi.liveme.com,
    which is IMA Studio's dedicated image upload service (separate from the main API).
    
    Why the API key is sent here:
    - imapi.liveme.com is owned and operated by IMA Studio
    - The upload service authenticates requests using the same IMA API key
    - This allows secure, authenticated image uploads without separate credentials
    - Images are stored in IMA's OSS infrastructure and returned as CDN URLs
    
    The two-domain architecture separates concerns:
    - api.imastudio.com: Image generation API (task orchestration)
    - imapi.liveme.com: Media storage API (large file uploads)
    
    See SECURITY.md § "Network Endpoints Used" for full disclosure.
    
    Calls GET /api/rest/oss/getuploadtoken with exactly 11 params.
    
    Args:
        api_key: IMA API key (used as both appUid and cmimToken for authentication)
        suffix: File extension (jpeg, png, mp4, etc.)
        content_type: MIME type (image/jpeg, video/mp4, etc.)
        im_base_url: IM upload service URL (default: https://imapi.liveme.com)
    
    Returns:
        dict with keys:
        - "ful": Presigned PUT URL for uploading raw bytes
        - "fdl": CDN download URL for the uploaded file
    
    Raises:
        RuntimeError: If upload token request fails
    """
    sign, ts, nonce = _gen_sign()
    
    url = f"{im_base_url}/api/rest/oss/getuploadtoken"
    params = {
        # Use IMA API key for both appUid and cmimToken
        "appUid": api_key,
        "appId": APP_ID,
        "appKey": APP_KEY,
        "cmimToken": api_key,
        "sign": sign,
        "timestamp": ts,
        "nonce": nonce,
        # File params
        "fService": "privite",
        "fType": "picture",  # picture / video / audio
        "fSuffix": suffix,
        "fContentType": content_type,
    }
    
    logger.info(f"Getting upload token: suffix={suffix}, content_type={content_type}")
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("code") not in (0, 200):
            raise RuntimeError(f"Get upload token failed: {data.get('message')}")
        
        token_data = data.get("data", {})
        logger.info(f"Upload token obtained: fdl={token_data.get('fdl', '')[:50]}...")
        return token_data
    
    except requests.RequestException as e:
        logger.error(f"Failed to get upload token: {e}")
        raise RuntimeError(f"Failed to get upload token: {e}")


def upload_to_oss(image_bytes: bytes, content_type: str, ful: str) -> None:
    """
    Step 2: PUT image bytes to the presigned OSS URL.
    
    Args:
        image_bytes: Raw image bytes
        content_type: MIME type (e.g., image/jpeg)
        ful: Presigned PUT URL from get_upload_token
    """
    logger.info(f"Uploading {len(image_bytes)} bytes to OSS...")
    
    try:
        resp = requests.put(ful, data=image_bytes, 
                           headers={"Content-Type": content_type}, 
                           timeout=60)
        resp.raise_for_status()
        logger.info("Upload to OSS successful")
    
    except requests.RequestException as e:
        logger.error(f"Failed to upload to OSS: {e}")
        raise RuntimeError(f"Failed to upload to OSS: {e}")


def prepare_image_url(source: str | bytes, api_key: str,
                      im_base_url: str = DEFAULT_IM_BASE_URL) -> str:
    """
    Full workflow: convert any image source to a public HTTPS CDN URL.
    
    - If source is already a public HTTPS URL → return as-is
    - If source is a local file path or bytes → upload to OSS first
    
    Args:
        source: File path (str), raw bytes, or already-public HTTPS URL
        api_key: IMA API key (used directly for upload authentication)
        im_base_url: IM platform base URL
    
    Returns:
        Public HTTPS CDN URL ready to use as input_images value
    """
    # Already a public URL → use directly, no upload needed
    if isinstance(source, str) and source.startswith("https://"):
        logger.info(f"Image is already a public URL: {source[:50]}...")
        return source
    
    # Need to upload
    if not api_key:
        raise RuntimeError("Local image upload requires IMA API key (--api-key)")
    
    # Read file bytes
    if isinstance(source, str):
        # Local file path
        if not os.path.isfile(source):
            raise RuntimeError(f"Image file not found: {source}")
        
        ext = Path(source).suffix.lstrip(".").lower() or "jpeg"
        with open(source, "rb") as f:
            image_bytes = f.read()
        content_type = mimetypes.guess_type(source)[0] or "image/jpeg"
        logger.info(f"Read local file: {source} ({len(image_bytes)} bytes)")
    
    else:
        # Raw bytes
        image_bytes = source
        ext = "jpeg"
        content_type = "image/jpeg"
        logger.info(f"Using raw image bytes ({len(image_bytes)} bytes)")
    
    # Step 1: Get presigned URL using API key
    token_data = get_upload_token(api_key, ext, content_type, im_base_url)
    ful = token_data.get("ful")
    fdl = token_data.get("fdl")
    
    if not ful or not fdl:
        raise RuntimeError("Upload token missing 'ful' or 'fdl' field")
    
    # Step 2: Upload to OSS
    upload_to_oss(image_bytes, content_type, ful)
    
    # Step 3: Return CDN URL
    logger.info(f"Image uploaded successfully: {fdl[:50]}...")
    return fdl


# ─── Step 1: Product List ─────────────────────────────────────────────────────

def get_product_list(base_url: str, api_key: str, category: str,
                     app: str = "ima", platform: str = "web",
                     language: str = "en") -> list:
    """
    GET /open/v1/product/list
    Returns the V2 tree: type=2 are model groups, type=3 are versions (leaves).
    Only type=3 nodes have credit_rules and form_config.
    """
    url     = f"{base_url}/open/v1/product/list"
    params  = {"app": app, "platform": platform, "category": category}
    headers = make_headers(api_key, language)

    logger.info(f"Query product list: category={category}, app={app}, platform={platform}")
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        code = data.get("code")
        if code not in (0, 200):
            error_msg = f"Product list API error: code={code}, msg={data.get('message')}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        products_count = len(data.get("data") or [])
        logger.info(f"Product list retrieved successfully: {products_count} groups found")
        return data.get("data") or []
        
    except requests.RequestException as e:
        logger.error(f"Product list request failed: {str(e)}")
        raise


def find_model_version(product_tree: list, target_model_id: str,
                       target_version_id: str | None = None) -> dict | None:
    """
    Walk the V2 tree and find a type=3 leaf node matching target_model_id.
    If target_version_id is given, match exactly; otherwise return the last
    (usually newest) matching version.

    Key insight from imagent.bot frontend:
      modelItem.key       → node["id"]          (= model_version in create request)
      modelItem.modelCodeId → node["model_id"]   (= model_id in create request)
      modelItem.name      → node["name"]         (= model_name in create request)
    """
    candidates = []

    def walk(nodes: list):
        for node in nodes:
            if node.get("type") == "3":
                mid = node.get("model_id", "")
                vid = node.get("id", "")
                if mid == target_model_id:
                    if target_version_id is None or vid == target_version_id:
                        candidates.append(node)
            children = node.get("children") or []
            walk(children)

    walk(product_tree)

    if not candidates:
        logger.error(f"Model not found: model_id={target_model_id}, version_id={target_version_id}")
        return None
    
    # Return last match — product list is ordered oldest→newest, last = newest
    selected = candidates[-1]
    logger.info(f"Model found: {selected.get('name')} (model_id={target_model_id}, version_id={selected.get('id')})")
    return selected


def list_all_models(product_tree: list) -> list[dict]:
    """Flatten tree to a list of {name, model_id, version_id, credit} dicts."""
    result = []

    def walk(nodes):
        for node in nodes:
            if node.get("type") == "3":
                cr = (node.get("credit_rules") or [{}])[0]
                result.append({
                    "name":       node.get("name", ""),
                    "model_id":   node.get("model_id", ""),
                    "version_id": node.get("id", ""),
                    "credit":     cr.get("points", 0),
                    "attr_id":    cr.get("attribute_id", 0),
                })
            walk(node.get("children") or [])

    walk(product_tree)
    return result


# ─── Step 2: Extract Parameters (including virtual param resolution) ──────────

def resolve_virtual_param(field: dict) -> dict:
    """
    Handle virtual form fields (is_ui_virtual=True).

    Frontend logic (useAgentModeData.ts):
      1. Create sub-forms from ui_params (each has a default value)
      2. Build patch: {ui_param.field: ui_param.value} for each sub-param
      3. Find matching value_mapping rule where source_values == patch
      4. Use target_value as the actual API parameter value

    If is_ui_virtual is not exposed by Open API, fall through to default value.
    """
    field_name     = field.get("field")
    ui_params      = field.get("ui_params") or []
    value_mapping  = field.get("value_mapping") or {}
    mapping_rules  = value_mapping.get("mapping_rules") or []
    default_value  = field.get("value")

    if not field_name:
        return {}

    if ui_params and mapping_rules:
        # Build patch from ui_params default values
        patch = {}
        for ui in ui_params:
            ui_field = ui.get("field") or ui.get("id", "")
            patch[ui_field] = ui.get("value")

        # Find matching mapping rule
        for rule in mapping_rules:
            source = rule.get("source_values") or {}
            if all(patch.get(k) == v for k, v in source.items()):
                return {field_name: rule.get("target_value")}

    # Fallback: use the field's own default value
    if default_value is not None:
        return {field_name: default_value}
    return {}


def extract_model_params(node: dict) -> dict:
    """
    Extract everything needed for the create task request from a product list leaf node.

    Returns:
      attribute_id  : int   — from credit_rules[0].attribute_id
      credit        : int   — from credit_rules[0].points
      model_id      : str   — node["model_id"]
      model_name    : str   — node["name"]
      model_version : str   — node["id"]  ← CRITICAL: this is what backend calls model_version_id
      form_params   : dict  — resolved form_config defaults (including virtual params)
    """
    credit_rules = node.get("credit_rules") or []
    if not credit_rules:
        raise RuntimeError(
            f"No credit_rules found for model '{node.get('model_id')}' "
            f"version '{node.get('id')}'. Cannot determine attribute_id or credit."
        )

    cr = credit_rules[0]
    attribute_id = cr.get("attribute_id", 0)
    credit       = cr.get("points", 0)

    if attribute_id == 0:
        raise RuntimeError(
            f"attribute_id is 0 for model '{node.get('model_id')}'. "
            "This will cause 'Invalid product attribute' error."
        )

    # Build form_config defaults
    form_params: dict = {}
    for field in (node.get("form_config") or []):
        fname = field.get("field")
        if not fname:
            continue

        is_virtual = field.get("is_ui_virtual", False)
        if is_virtual:
            # Apply virtual param resolution (frontend logic)
            resolved = resolve_virtual_param(field)
            form_params.update(resolved)
        else:
            fvalue = field.get("value")
            if fvalue is not None:
                form_params[fname] = fvalue

    # ✅ FIX for error 6009: Extract credit_rules[].attributes (required by backend validation)
    # Backend积分校验要求请求参数必须包含规则的attributes字段，否则MatchScore < 1.0 → 错误6009
    rule_attributes: dict = {}
    if credit_rules:
        # Use first rule's attributes as defaults
        first_rule_attrs = credit_rules[0].get("attributes", {})
        
        # Filter out {"default": "enabled"} marker (not an actual parameter)
        for key, value in first_rule_attrs.items():
            if not (key == "default" and value == "enabled"):
                rule_attributes[key] = value

    logger.info(f"Params extracted: model={node.get('model_id')}, attribute_id={attribute_id}, "
                f"credit={credit}, rule_attrs={len(rule_attributes)} fields")

    return {
        "attribute_id":     attribute_id,
        "credit":           credit,
        "model_id":         node.get("model_id", ""),
        "model_name":       node.get("name", ""),
        "model_version":    node.get("id", ""),   # ← version_id from product list
        "form_params":      form_params,
        "rule_attributes":  rule_attributes,  # ✅ NEW: required params from attributes
        "all_credit_rules": credit_rules,     # For smart selection
    }


def select_credit_rule_by_params(credit_rules: list, user_params: dict) -> dict | None:
    """
    Select the best credit_rule matching user parameters.
    
    CRITICAL FIX (error 6010): Must match ALL attributes in credit_rule, not just user params.
    Backend validation checks if request params match the rule's attributes exactly.
    
    Strategy:
    1. Try exact match: ALL rule attributes match user params (bidirectional)
    2. Try partial match: rule attributes are subset of user params
    3. Fallback: first rule (default)
    
    Returns the selected credit_rule or None if credit_rules is empty.
    """
    if not credit_rules:
        return None
    
    if not user_params:
        return credit_rules[0]
    
    # Normalize user params (handle bool → lowercase string for JSON compatibility)
    def normalize_value(v):
        if isinstance(v, bool):
            return str(v).lower()  # False → "false", True → "true"
        return str(v).strip()
    
    normalized_user = {
        k.lower().strip(): normalize_value(v)
        for k, v in user_params.items()
    }
    
    # Try exact match: ALL rule attributes must match user params
    # This ensures backend validation passes (error 6010 prevention)
    for cr in credit_rules:
        attrs = cr.get("attributes", {})
        if not attrs:
            continue
        
        normalized_attrs = {
            k.lower().strip(): normalize_value(v)
            for k, v in attrs.items()
        }
        
        # CRITICAL: Check if ALL rule attributes are in user params AND match
        # (Not just if user params are in rule attributes)
        if all(normalized_user.get(k) == v for k, v in normalized_attrs.items()):
            return cr
    
    # Try partial match (at least some attributes match)
    best_match = None
    best_match_count = 0
    
    for cr in credit_rules:
        attrs = cr.get("attributes", {})
        if not attrs:
            continue
        
        normalized_attrs = {
            k.lower().strip(): normalize_value(v)
            for k, v in attrs.items()
        }
        
        # Count how many attributes match
        match_count = sum(1 for k, v in normalized_attrs.items() 
                         if normalized_user.get(k) == v)
        
        if match_count > best_match_count:
            best_match_count = match_count
            best_match = cr
    
    if best_match:
        return best_match
    
    # Fallback to first rule
    return credit_rules[0]


# ─── Step 3: Create Task ──────────────────────────────────────────────────────

def create_task(base_url: str, api_key: str,
                task_type: str, model_params: dict,
                prompt: str,
                input_images: list[str] | None = None,
                extra_params: dict | None = None) -> str:
    """
    POST /open/v1/tasks/create

    Constructs the full request body as the imagent.bot frontend does:
      parameters[i].model_version = modelItem.key = node["id"] (version_id)
      parameters[i].attribute_id  = creditInfo.attributeId
      parameters[i].credit        = creditInfo.credits
      parameters[i].parameters    = { ...form_config_defaults,
                                       prompt, input_images, cast, n }
    
    NEW: Supports smart credit_rule selection based on user params (e.g., size: "4K").
    """
    if input_images is None:
        input_images = []

    # Smart credit_rule selection based on user params
    all_rules = model_params.get("all_credit_rules", [])
    if extra_params and all_rules:
        # Extract params that might be in attributes
        # CRITICAL: ONLY include keys that actually appear in credit_rules.attributes
        # Image credit_rules.attributes: size, quality, n
        candidate_params = {k: v for k, v in extra_params.items() 
                          if k in ["size", "quality", "n"]}
        # ⚠️ REMOVED: resolution, sample_image_size (form_config defaults, not in attributes)
        if candidate_params:
            selected_rule = select_credit_rule_by_params(all_rules, candidate_params)
            if selected_rule:
                attribute_id = selected_rule.get("attribute_id", model_params["attribute_id"])
                credit = selected_rule.get("points", model_params["credit"])
                print(f"🎯 Smart credit_rule selection: {candidate_params} → attribute_id={attribute_id}, credit={credit} pts", flush=True)
            else:
                attribute_id = model_params["attribute_id"]
                credit = model_params["credit"]
        else:
            attribute_id = model_params["attribute_id"]
            credit = model_params["credit"]
    else:
        attribute_id = model_params["attribute_id"]
        credit = model_params["credit"]

    # ✅ FIX for error 6009: Merge parameters in correct priority order
    # Priority (low → high): rule_attributes < form_params < extra_params
    # This ensures backend validation always gets required fields from attributes
    inner: dict = {}
    
    # 1. First merge rule_attributes (required fields from credit_rules, lowest priority)
    rule_attrs = model_params.get("rule_attributes", {})
    if rule_attrs:
        inner.update(rule_attrs)
    
    # 2. Then merge form_config defaults (optional fields, medium priority)
    inner.update(model_params["form_params"])
    
    # 3. Finally merge user overrides (highest priority, can override everything)
    if extra_params:
        inner.update(extra_params)

    # Required inner fields (always set these)
    inner["prompt"]       = prompt
    inner["n"]            = int(inner.get("n", 1))
    inner["input_images"] = input_images
    inner["cast"]         = {"points": credit, "attribute_id": attribute_id}

    payload = {
        "task_type":          task_type,
        "enable_multi_model": False,
        "src_img_url":        input_images,
        "parameters": [{
            "attribute_id":  attribute_id,
            "model_id":      model_params["model_id"],
            "model_name":    model_params["model_name"],
            "model_version": model_params["model_version"],   # ← version_id (NOT model_id!)
            "app":           "ima",
            "platform":      "web",
            "category":      task_type,
            "credit":        credit,
            "parameters":    inner,
        }],
    }

    url     = f"{base_url}/open/v1/tasks/create"
    headers = make_headers(api_key)

    logger.info(f"Create task: model={model_params['model_name']}, task_type={task_type}, "
                f"credit={credit}, attribute_id={attribute_id}")

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        code = data.get("code")
        if code not in (0, 200):
            logger.error(f"Task create failed: code={code}, msg={data.get('message')}, "
                        f"attribute_id={attribute_id}, credit={credit}")
            raise RuntimeError(
                f"Create task failed — code={code} "
                f"message={data.get('message')} "
                f"request={json.dumps(payload, ensure_ascii=False)}"
            )

        task_id = (data.get("data") or {}).get("id")
        if not task_id:
            logger.error("Task create failed: no task_id in response")
            raise RuntimeError(f"No task_id in response: {data}")

        logger.info(f"Task created: task_id={task_id}")
        return task_id
        
    except requests.RequestException as e:
        logger.error(f"Task create request failed: {str(e)}")
        raise


# ─── Step 4: Poll Task Status ─────────────────────────────────────────────────

def poll_task(base_url: str, api_key: str, task_id: str,
              estimated_max: int = 120,
              poll_interval: int = 5,
              max_wait: int = 600,
              on_progress=None) -> dict:
    """
    POST /open/v1/tasks/detail — poll until completion.

    - resource_status (int or null): 0=processing, 1=done, 2=failed, 3=deleted.
      null is treated as 0.
    - status (string): "pending" | "processing" | "success" | "failed".
      When resource_status==1, treat status=="failed" as failure; "success" (or "completed") as success.
    - Stop only when ALL medias have resource_status == 1 and no status == "failed".
    - Returns the first completed media dict (with url) when all are done.
    """
    url     = f"{base_url}/open/v1/tasks/detail"
    headers = make_headers(api_key)
    start   = time.time()

    logger.info(f"Poll task started: task_id={task_id}, max_wait={max_wait}s")

    last_progress_report = 0
    progress_interval    = 15 if poll_interval <= 5 else 30

    while True:
        elapsed = time.time() - start
        if elapsed > max_wait:
            logger.error(f"Task timeout: task_id={task_id}, elapsed={int(elapsed)}s, max_wait={max_wait}s")
            raise TimeoutError(
                f"Task {task_id} timed out after {max_wait}s. "
                "Check the IMA dashboard for status."
            )

        resp = requests.post(url, json={"task_id": task_id},
                             headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        code = data.get("code")
        if code not in (0, 200):
            raise RuntimeError(f"Poll error — code={code} msg={data.get('message')}")

        task   = data.get("data") or {}
        medias = task.get("medias") or []

        # Normalize resource_status: API may return null (Go *int); treat as 0 (processing)
        def _rs(m):
            v = m.get("resource_status")
            return 0 if (v is None or v == "") else int(v)

        # 1. Fail fast: any media failed or deleted → raise
        for media in medias:
            rs = _rs(media)
            if rs == 2:
                err = media.get("error_msg") or media.get("remark") or "unknown"
                logger.error(f"Task failed: task_id={task_id}, resource_status=2, error={err}")
                raise RuntimeError(f"Generation failed (resource_status=2): {err}")
            if rs == 3:
                logger.error(f"Task deleted: task_id={task_id}")
                raise RuntimeError("Task was deleted")

        # 2. Success only when ALL medias have resource_status == 1 (and none failed)
        # status is one of: "pending", "processing", "success", "failed"
        if medias and all(_rs(m) == 1 for m in medias):
            for media in medias:
                if (media.get("status") or "").strip().lower() == "failed":
                    err = media.get("error_msg") or media.get("remark") or "unknown"
                    logger.error(f"Task failed: task_id={task_id}, status=failed, error={err}")
                    raise RuntimeError(f"Generation failed: {err}")
            # All done and no failure → also wait for URL to be populated
            first_media = medias[0]
            result_url = first_media.get("url") or first_media.get("watermark_url")
            if result_url:
                elapsed_time = int(time.time() - start)
                logger.info(f"Task completed: task_id={task_id}, elapsed={elapsed_time}s, url={result_url[:80]}")
                return first_media
            # else: URL not ready yet, keep polling

        # Report progress periodically
        if elapsed - last_progress_report >= progress_interval:
            pct = min(95, int(elapsed / estimated_max * 100))
            msg = f"⏳ {int(elapsed)}s elapsed … {pct}%"
            if elapsed > estimated_max:
                msg += "  (taking longer than expected, please wait…)"
            if on_progress:
                on_progress(pct, int(elapsed), msg)
            else:
                print(msg, flush=True)
            last_progress_report = elapsed

        time.sleep(poll_interval)


# ─── User Preference Memory ───────────────────────────────────────────────────

def load_prefs() -> dict:
    try:
        with open(PREFS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_pref(user_id: str, task_type: str, model_params: dict):
    os.makedirs(os.path.dirname(PREFS_PATH), exist_ok=True)
    prefs = load_prefs()
    key   = f"user_{user_id}"
    prefs.setdefault(key, {})[task_type] = {
        "model_id":    model_params["model_id"],
        "model_name":  model_params["model_name"],
        "credit":      model_params["credit"],
        "last_used":   datetime.now(timezone.utc).isoformat(),
    }
    with open(PREFS_PATH, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)


def get_preferred_model_id(user_id: str, task_type: str) -> str | None:
    prefs = load_prefs()
    entry = (prefs.get(f"user_{user_id}") or {}).get(task_type)
    return entry.get("model_id") if entry else None


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="IMA Image Creation Script — specialized for image generation via Open API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Text to image (SeeDream 4.5 — newest default)
  python3 ima_image_create.py \\
    --api-key ima_xxx --task-type text_to_image \\
    --model-id doubao-seedream-4.5 --prompt "a cute puppy"

  # Text to image with size override
  python3 ima_image_create.py \\
    --api-key ima_xxx --task-type text_to_image \\
    --model-id doubao-seedream-4.5 --prompt "city skyline" --size 2k

  # Image to image (style transfer)
  python3 ima_image_create.py \\
    --api-key ima_xxx --task-type image_to_image \\
    --model-id doubao-seedream-4.5 --prompt "turn into oil painting style" \\
    --input-images https://example.com/photo.jpg

  # List all models for a category
  python3 ima_image_create.py \\
    --api-key ima_xxx --task-type text_to_image --list-models
""",
    )

    p.add_argument("--api-key",  required=False,
                   help="IMA Open API key (starts with ima_). Can also use IMA_API_KEY env var")
    p.add_argument("--task-type", required=True,
                   choices=list(POLL_CONFIG.keys()),
                   help="Task type: text_to_image or image_to_image")
    p.add_argument("--model-id",
                   help="Model ID from product list (e.g. doubao-seedream-4.5)")
    p.add_argument("--version-id",
                   help="Specific version ID — overrides auto-select of latest")
    p.add_argument("--prompt",
                   help="Generation prompt (required unless --list-models)")
    p.add_argument("--input-images", nargs="*", default=[],
                   help="Input image URLs or local file paths (required for image_to_image). "
                        "Local files will be automatically uploaded using the API key.")
    p.add_argument("--size",
                   help="Override size parameter (e.g. 4k, 2k, 2048x2048)")
    p.add_argument("--extra-params",
                   help='JSON string of extra inner parameters, e.g. \'{"n":2}\'')
    p.add_argument("--language", default="en",
                   help="Language for product labels (en/zh)")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL,
                   help="API base URL")
    p.add_argument("--user-id", default="default",
                   help="User ID for preference memory")
    p.add_argument("--list-models", action="store_true",
                   help="List all available models for --task-type and exit")
    p.add_argument("--output-json", action="store_true",
                   help="Output final result as JSON (for agent parsing)")

    return p


def main():
    args   = build_parser().parse_args()
    base   = args.base_url
    
    # Get API key from args or environment variable
    apikey = args.api_key or os.getenv("IMA_API_KEY")
    if not apikey:
        logger.error("API key is required. Use --api-key or set IMA_API_KEY environment variable")
        sys.exit(1)

    start_time = time.time()
    masked_key = f"{apikey[:10]}..." if len(apikey) > 10 else "***"
    logger.info(f"Script started: task_type={args.task_type}, model_id={args.model_id or 'auto'}, "
                f"api_key={masked_key}")

    # ── 1. Query product list ──────────────────────────────────────────────────
    print(f"🔍 Querying product list: category={args.task_type}", flush=True)
    try:
        tree = get_product_list(base, apikey, args.task_type,
                                language=args.language)
    except Exception as e:
        logger.error(f"Product list failed: {str(e)}")
        print(f"❌ Product list failed: {e}", file=sys.stderr)
        sys.exit(1)

    # ── List models mode ───────────────────────────────────────────────────────
    if args.list_models:
        models = list_all_models(tree)
        print(f"\nAvailable models for '{args.task_type}':")
        print(f"{'Name':<28} {'model_id':<34} {'version_id':<44} {'pts':>4}  attr_id")
        print("─" * 120)
        for m in models:
            print(f"{m['name']:<28} {m['model_id']:<34} {m['version_id']:<44} "
                  f"{m['credit']:>4}  {m['attr_id']}")
        sys.exit(0)

    # ── Resolve model_id ───────────────────────────────────────────────────────
    if not args.model_id:
        # Check user preference
        pref_model = get_preferred_model_id(args.user_id, args.task_type)
        if pref_model:
            args.model_id = pref_model
            print(f"💡 Using your preferred model: {pref_model}", flush=True)
        else:
            print("❌ --model-id is required (no saved preference found)", file=sys.stderr)
            print("   Run with --list-models to see available models", file=sys.stderr)
            sys.exit(1)

    if not args.prompt:
        print("❌ --prompt is required", file=sys.stderr)
        sys.exit(1)

    # ── 2. Find model version in tree ─────────────────────────────────────────
    node = find_model_version(tree, args.model_id, args.version_id)
    if not node:
        logger.error(f"Model not found: model_id={args.model_id}, task_type={args.task_type}")
        available = [f"  {m['model_id']}" for m in list_all_models(tree)]
        print(f"❌ model_id='{args.model_id}' not found for task_type='{args.task_type}'.",
              file=sys.stderr)
        print("   Available model_ids:\n" + "\n".join(available), file=sys.stderr)
        sys.exit(1)

    # ── 3. Extract params (including virtual param resolution) ────────────────
    try:
        mp = extract_model_params(node)
    except RuntimeError as e:
        logger.error(f"Param extraction failed: {str(e)}")
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Model found:")
    print(f"   name          = {mp['model_name']}")
    print(f"   model_id      = {mp['model_id']}")
    print(f"   model_version = {mp['model_version']}   ← version_id from product list")
    print(f"   attribute_id  = {mp['attribute_id']}")
    print(f"   credit        = {mp['credit']} pts")
    print(f"   form_params   = {json.dumps(mp['form_params'], ensure_ascii=False)}")

    # Apply overrides
    extra: dict = {}
    if args.size:
        extra["size"] = args.size
    if args.extra_params:
        try:
            extra.update(json.loads(args.extra_params))
        except json.JSONDecodeError as e:
            print(f"❌ Invalid --extra-params JSON: {e}", file=sys.stderr)
            sys.exit(1)

    # ── 4. Process input images (upload if needed) ────────────────────────────
    processed_images: list[str] = []
    if args.input_images:
        im_base = os.getenv("IMA_IM_BASE_URL", DEFAULT_IM_BASE_URL)
        
        print(f"\n📤 Processing {len(args.input_images)} input image(s)…", flush=True)
        for i, img_source in enumerate(args.input_images, 1):
            try:
                # Use API key directly for upload authentication
                img_url = prepare_image_url(img_source, apikey, im_base)
                processed_images.append(img_url)
                
                if img_source.startswith("https://"):
                    print(f"   [{i}] Using URL directly: {img_url[:60]}...")
                else:
                    print(f"   [{i}] Uploaded: {os.path.basename(img_source) if isinstance(img_source, str) else 'bytes'} → {img_url[:60]}...")
            
            except RuntimeError as e:
                logger.error(f"Failed to process image {i}: {e}")
                print(f"❌ Failed to process image [{i}]: {e}", file=sys.stderr)
                sys.exit(1)
        
        print(f"✅ All {len(processed_images)} image(s) ready")

    # ── 5. Create task ─────────────────────────────────────────────────────────
    print(f"\n🚀 Creating task…", flush=True)
    try:
        task_id = create_task(base, apikey, args.task_type, mp,
                              args.prompt, processed_images,
                              extra if extra else None)
    except RuntimeError as e:
        logger.error(f"Task creation failed: {str(e)}")
        print(f"❌ Create task failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Task created: {task_id}", flush=True)

    # ── 6. Poll for result ─────────────────────────────────────────────────────
    cfg        = POLL_CONFIG.get(args.task_type, {"interval": 5, "max_wait": 300})
    est_max    = cfg["max_wait"] // 2   # optimistic estimate = half of max_wait
    print(f"\n⏳ Polling… (interval={cfg['interval']}s, max={cfg['max_wait']}s)",
          flush=True)

    try:
        media = poll_task(base, apikey, task_id,
                          estimated_max=est_max,
                          poll_interval=cfg["interval"],
                          max_wait=cfg["max_wait"])
    except (TimeoutError, RuntimeError) as e:
        logger.error(f"Task polling failed: {str(e)}")
        print(f"\n❌ {e}", file=sys.stderr)
        sys.exit(1)

    # ── 6. Save preference ────────────────────────────────────────────────────
    save_pref(args.user_id, args.task_type, mp)

    # ── 7. Output result ───────────────────────────────────────────────────────
    result_url = media.get("url") or media.get("preview_url") or ""
    cover_url  = media.get("cover_url") or ""

    print(f"\n✅ Generation complete!")
    print(f"   URL:   {result_url}")
    if cover_url:
        print(f"   Cover: {cover_url}")

    if args.output_json:
        out = {
            "task_id":    task_id,
            "url":        result_url,
            "cover_url":  cover_url,
            "model_id":   mp["model_id"],
            "model_name": mp["model_name"],
            "credit":     mp["credit"],
        }
        print("\n" + json.dumps(out, ensure_ascii=False, indent=2))

    total_time = int(time.time() - start_time)
    logger.info(f"Script completed: total_time={total_time}s, task_id={task_id}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
