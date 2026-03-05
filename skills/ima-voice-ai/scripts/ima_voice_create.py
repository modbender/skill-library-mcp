#!/usr/bin/env python3
"""
IMA Voice/Music Creation Script — ima_voice_create.py
Version: 1.0.0

Specialized script for music/audio generation via IMA Open API.
Handles: product list query → virtual param resolution → task create → poll status

Usage:
  python3 ima_voice_create.py \\
    --api-key  ima_xxx \\
    --model-id  sonic \\
    --prompt   "upbeat lo-fi hip hop, 90 BPM"

Supports text_to_music task type only.
Models: Suno (sonic), DouBao BGM (GenBGM), DouBao Song (GenSong)

Logs: ~/.openclaw/logs/ima_skills/ima_create_YYYYMMDD.log
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

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

DEFAULT_BASE_URL = "https://api.imastudio.com"
PREFS_PATH       = os.path.expanduser("~/.openclaw/memory/ima_prefs.json")
TASK_TYPE        = "text_to_music"  # Fixed task type for voice/music generation

# Poll configuration for music generation
POLL_CONFIG = {
    "interval": 5,
    "max_wait": 300,  # Increased for Suno (slow generation, 120-180s typical)
}


# ─── HTTP helpers ─────────────────────────────────────────────────────────────

def make_headers(api_key: str, language: str = "en") -> dict:
    return {
        "Authorization":  f"Bearer {api_key}",
        "Content-Type":   "application/json",
        "x-app-source":   "ima_skills",
        "x_app_language": language,
    }


# ─── Step 1: Product List ─────────────────────────────────────────────────────

def get_product_list(base_url: str, api_key: str,
                     app: str = "ima", platform: str = "web",
                     language: str = "en") -> list:
    """
    GET /open/v1/product/list
    Returns the V2 tree: type=2 are model groups, type=3 are versions (leaves).
    Only type=3 nodes have credit_rules and form_config.
    """
    url     = f"{base_url}/open/v1/product/list"
    params  = {"app": app, "platform": platform, "category": TASK_TYPE}
    headers = make_headers(api_key, language)

    logger.info(f"Query product list: category={TASK_TYPE}, app={app}, platform={platform}")
    
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


# ─── Step 2: Extract Parameters ───────────────────────────────────────────────

def resolve_virtual_param(field: dict) -> dict:
    """
    Handle virtual form fields (is_ui_virtual=True).
    
    Frontend logic (useAgentModeData.ts):
      1. Create sub-forms from ui_params (each has a default value)
      2. Build patch: {ui_param.field: ui_param.value} for each sub-param
      3. Find matching value_mapping rule where source_values == patch
      4. Use target_value as the actual API parameter value
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
      model_version : str   — node["id"]
      form_params   : dict  — resolved form_config defaults (including virtual params)
      rule_attributes : dict — required params from credit_rules[0].attributes
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

    # Extract credit_rules[].attributes (required by backend validation)
    rule_attributes: dict = {}
    if credit_rules:
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
        "model_version":    node.get("id", ""),
        "form_params":      form_params,
        "rule_attributes":  rule_attributes,
    }


# ─── Step 3: Create Task ──────────────────────────────────────────────────────

def create_task(base_url: str, api_key: str, model_params: dict,
                prompt: str, extra_params: dict | None = None) -> str:
    """
    POST /open/v1/tasks/create
    
    Constructs the full request body for music generation task.
    """
    # Merge parameters in correct priority order
    # Priority (low → high): rule_attributes < form_params < extra_params
    inner: dict = {}
    
    # 1. First merge rule_attributes (required fields from credit_rules)
    rule_attrs = model_params.get("rule_attributes", {})
    if rule_attrs:
        inner.update(rule_attrs)
    
    # 2. Then merge form_config defaults
    inner.update(model_params["form_params"])
    
    # 3. Finally merge user overrides
    if extra_params:
        inner.update(extra_params)

    # Required inner fields
    inner["prompt"]       = prompt
    inner["n"]            = int(inner.get("n", 1))
    inner["input_images"] = []
    inner["cast"]         = {
        "points": model_params["credit"],
        "attribute_id": model_params["attribute_id"]
    }

    payload = {
        "task_type":          TASK_TYPE,
        "enable_multi_model": False,
        "src_img_url":        [],
        "parameters": [{
            "attribute_id":  model_params["attribute_id"],
            "model_id":      model_params["model_id"],
            "model_name":    model_params["model_name"],
            "model_version": model_params["model_version"],
            "app":           "ima",
            "platform":      "web",
            "category":      TASK_TYPE,
            "credit":        model_params["credit"],
            "parameters":    inner,
        }],
    }

    url     = f"{base_url}/open/v1/tasks/create"
    headers = make_headers(api_key)

    logger.info(f"Create task: model={model_params['model_name']}, task_type={TASK_TYPE}, "
                f"credit={model_params['credit']}, attribute_id={model_params['attribute_id']}")

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        code = data.get("code")
        if code not in (0, 200):
            logger.error(f"Task create failed: code={code}, msg={data.get('message')}, "
                        f"attribute_id={model_params['attribute_id']}, credit={model_params['credit']}")
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
              estimated_max: int = 150, on_progress=None) -> dict:
    """
    POST /open/v1/tasks/detail — poll until completion.
    
    Returns the first completed media dict (with url) when done.
    """
    url     = f"{base_url}/open/v1/tasks/detail"
    headers = make_headers(api_key)
    start   = time.time()

    logger.info(f"Poll task started: task_id={task_id}, max_wait={POLL_CONFIG['max_wait']}s")

    last_progress_report = 0
    progress_interval    = 15

    while True:
        elapsed = time.time() - start
        if elapsed > POLL_CONFIG['max_wait']:
            logger.error(f"Task timeout: task_id={task_id}, elapsed={int(elapsed)}s, max_wait={POLL_CONFIG['max_wait']}s")
            raise TimeoutError(
                f"Task {task_id} timed out after {POLL_CONFIG['max_wait']}s. "
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

        # Normalize resource_status: API may return null; treat as 0 (processing)
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

        time.sleep(POLL_CONFIG['interval'])


# ─── User Preference Memory ───────────────────────────────────────────────────

def load_prefs() -> dict:
    try:
        with open(PREFS_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_pref(user_id: str, model_params: dict):
    os.makedirs(os.path.dirname(PREFS_PATH), exist_ok=True)
    prefs = load_prefs()
    key   = f"user_{user_id}"
    prefs.setdefault(key, {})[TASK_TYPE] = {
        "model_id":    model_params["model_id"],
        "model_name":  model_params["model_name"],
        "credit":      model_params["credit"],
        "last_used":   datetime.now(timezone.utc).isoformat(),
    }
    with open(PREFS_PATH, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)


def get_preferred_model_id(user_id: str) -> str | None:
    prefs = load_prefs()
    entry = (prefs.get(f"user_{user_id}") or {}).get(TASK_TYPE)
    return entry.get("model_id") if entry else None


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="IMA Voice/Music Creation Script — specialized for music generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate music with Suno (default, most powerful)
  python3 ima_voice_create.py \\
    --api-key ima_xxx \\
    --model-id sonic \\
    --prompt "upbeat lo-fi hip hop, 90 BPM, no vocals"

  # Generate music with DouBao BGM (background music)
  python3 ima_voice_create.py \\
    --api-key ima_xxx \\
    --model-id GenBGM \\
    --prompt "ambient chill, peaceful"

  # Generate song with DouBao Song
  python3 ima_voice_create.py \\
    --api-key ima_xxx \\
    --model-id GenSong \\
    --prompt "pop ballad, female vocals"

  # List all available music models
  python3 ima_voice_create.py \\
    --api-key ima_xxx \\
    --list-models
    
  # With extra Suno parameters
  python3 ima_voice_create.py \\
    --api-key ima_xxx \\
    --model-id sonic \\
    --prompt "以后都用 Suno" \\
    --extra-params '{"custom_mode": true, "make_instrumental": false}'
""",
    )

    p.add_argument("--api-key",  required=False,
                   help="IMA Open API key (starts with ima_). Can also use IMA_API_KEY env var")
    p.add_argument("--model-id",
                   help="Model ID: sonic (Suno), GenBGM (DouBao BGM), GenSong (DouBao Song)")
    p.add_argument("--version-id",
                   help="Specific version ID — overrides auto-select of latest")
    p.add_argument("--prompt",
                   help="Music generation prompt (required unless --list-models)")
    p.add_argument("--extra-params",
                   help='JSON string of extra parameters, e.g. \'{"custom_mode": true}\'')
    p.add_argument("--language", default="en",
                   help="Language for product labels (en/zh)")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL,
                   help="API base URL")
    p.add_argument("--user-id", default="default",
                   help="User ID for preference memory")
    p.add_argument("--list-models", action="store_true",
                   help="List all available music models and exit")
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
    logger.info(f"Script started: task_type={TASK_TYPE}, model_id={args.model_id or 'auto'}, "
                f"api_key={masked_key}")

    # ── 1. Query product list ──────────────────────────────────────────────────
    print(f"🔍 Querying music models: category={TASK_TYPE}", flush=True)
    try:
        tree = get_product_list(base, apikey, language=args.language)
    except Exception as e:
        logger.error(f"Product list failed: {str(e)}")
        print(f"❌ Product list failed: {e}", file=sys.stderr)
        sys.exit(1)

    # ── List models mode ───────────────────────────────────────────────────────
    if args.list_models:
        models = list_all_models(tree)
        print(f"\nAvailable music models:")
        print(f"{'Name':<28} {'model_id':<34} {'version_id':<44} {'pts':>4}  attr_id")
        print("─" * 120)
        for m in models:
            print(f"{m['name']:<28} {m['model_id']:<34} {m['version_id']:<44} "
                  f"{m['credit']:>4}  {m['attr_id']}")
        sys.exit(0)

    # ── Resolve model_id ───────────────────────────────────────────────────────
    if not args.model_id:
        # Check user preference
        pref_model = get_preferred_model_id(args.user_id)
        if pref_model:
            args.model_id = pref_model
            print(f"💡 Using your preferred model: {pref_model}", flush=True)
        else:
            print("❌ --model-id is required (no saved preference found)", file=sys.stderr)
            print("   Run with --list-models to see available models", file=sys.stderr)
            print("   Recommended: sonic (Suno), GenBGM (DouBao BGM), GenSong (DouBao Song)", file=sys.stderr)
            sys.exit(1)

    if not args.prompt:
        print("❌ --prompt is required", file=sys.stderr)
        sys.exit(1)

    # ── 2. Find model version in tree ─────────────────────────────────────────
    node = find_model_version(tree, args.model_id, args.version_id)
    if not node:
        logger.error(f"Model not found: model_id={args.model_id}")
        available = [f"  {m['model_id']}" for m in list_all_models(tree)]
        print(f"❌ model_id='{args.model_id}' not found.",
              file=sys.stderr)
        print("   Available model_ids:\n" + "\n".join(available), file=sys.stderr)
        sys.exit(1)

    # ── 3. Extract params ──────────────────────────────────────────────────────
    try:
        mp = extract_model_params(node)
    except RuntimeError as e:
        logger.error(f"Param extraction failed: {str(e)}")
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Model found:")
    print(f"   name          = {mp['model_name']}")
    print(f"   model_id      = {mp['model_id']}")
    print(f"   model_version = {mp['model_version']}")
    print(f"   attribute_id  = {mp['attribute_id']}")
    print(f"   credit        = {mp['credit']} pts")

    # Apply extra params
    extra: dict = {}
    if args.extra_params:
        try:
            extra.update(json.loads(args.extra_params))
        except json.JSONDecodeError as e:
            print(f"❌ Invalid --extra-params JSON: {e}", file=sys.stderr)
            sys.exit(1)

    # ── 4. Create task ─────────────────────────────────────────────────────────
    print(f"\n🚀 Creating music generation task…", flush=True)
    try:
        task_id = create_task(base, apikey, mp, args.prompt,
                              extra if extra else None)
    except RuntimeError as e:
        logger.error(f"Task creation failed: {str(e)}")
        print(f"❌ Create task failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ Task created: {task_id}", flush=True)

    # ── 5. Poll for result ─────────────────────────────────────────────────────
    est_max = POLL_CONFIG["max_wait"] // 2  # optimistic estimate
    print(f"\n⏳ Polling… (interval={POLL_CONFIG['interval']}s, max={POLL_CONFIG['max_wait']}s)",
          flush=True)

    try:
        media = poll_task(base, apikey, task_id, estimated_max=est_max)
    except (TimeoutError, RuntimeError) as e:
        logger.error(f"Task polling failed: {str(e)}")
        print(f"\n❌ {e}", file=sys.stderr)
        sys.exit(1)

    # ── 6. Save preference ────────────────────────────────────────────────────
    save_pref(args.user_id, mp)

    # ── 7. Output result ───────────────────────────────────────────────────────
    result_url = media.get("url") or media.get("preview_url") or ""
    duration   = media.get("duration_str") or ""

    print(f"\n✅ Music generation complete!")
    print(f"   URL:      {result_url}")
    if duration:
        print(f"   Duration: {duration}")

    if args.output_json:
        out = {
            "task_id":    task_id,
            "url":        result_url,
            "duration":   duration,
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
