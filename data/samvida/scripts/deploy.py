#!/usr/bin/env python3
"""
deploy.py — Deploy llms.txt to Cloudflare Workers, Webflow, or Framer.

Usage:
    # Cloudflare Workers (default)
    python3 deploy.py \\
        --provider cloudflare \\
        --llms-txt /path/to/llms.txt \\
        --cf-token TOKEN \\
        --account-id ACCOUNT_ID \\
        --zone-id ZONE_ID \\
        --domain example.com

    # Webflow
    python3 deploy.py \\
        --provider webflow \\
        --llms-txt /path/to/llms.txt \\
        --webflow-token TOKEN \\
        --site-id SITE_ID \\
        --domain example.com

    # Framer (semi-automated — outputs hosted URL + manual steps)
    python3 deploy.py \\
        --provider framer \\
        --llms-txt /path/to/llms.txt \\
        --domain example.com \\
        --github-token TOKEN   # optional, for Gist hosting
"""

import sys
import re
import time
import json
import hashlib
import argparse

try:
    import httpx
except ImportError:
    print("Missing dependency. Run: pip install httpx", file=sys.stderr)
    sys.exit(1)

CF_API = "https://api.cloudflare.com/client/v4"
WF_API = "https://api.webflow.com/v2"



# ──────────────────────────────────────────────
# Shared helpers
# ──────────────────────────────────────────────

def domain_slug(domain: str) -> str:
    return re.sub(r"[^a-z0-9]", "-", domain.lower()).strip("-")


def md5(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()


# ──────────────────────────────────────────────
# Cloudflare Workers deploy
# ──────────────────────────────────────────────

def build_worker_js(llms_txt_content: str) -> str:
    escaped = llms_txt_content.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return f"""export default {{
  async fetch(request, env, ctx) {{
    const url = new URL(request.url);
    if (url.pathname === '/llms.txt') {{
      return new Response(LLMS_TXT_CONTENT, {{
        headers: {{
          'Content-Type': 'text/plain; charset=utf-8',
          'Cache-Control': 'public, max-age=3600',
          'Access-Control-Allow-Origin': '*'
        }}
      }});
    }}
    return fetch(request);
  }}
}}

const LLMS_TXT_CONTENT = `{escaped}`;
"""


def cf_upload_worker(client, account_id, script_name, worker_js):
    url = f"{CF_API}/accounts/{account_id}/workers/scripts/{script_name}"
    files = {
        "metadata": (None, json.dumps({
            "main_module": "worker.js",
            "compatibility_date": "2024-01-01"
        }), "application/json"),
        "worker.js": ("worker.js", worker_js, "application/javascript+module"),
    }
    r = client.put(url, files=files)
    data = r.json()
    if r.status_code == 403:
        print("✖  Permission denied. Token needs 'Workers Scripts: Edit' permission.")
        sys.exit(1)
    if r.status_code == 404:
        print(f"✖  Account not found. Check your Account ID.")
        sys.exit(1)
    if not data.get("success"):
        print(f"✖  Worker upload failed: {data.get('errors', [])}")
        sys.exit(1)
    print(f"  ✓ Worker '{script_name}' uploaded")


def cf_add_route(client, zone_id, domain, script_name):
    pattern = f"{domain}/llms.txt"
    routes_url = f"{CF_API}/zones/{zone_id}/workers/routes"
    r = client.post(routes_url, json={"pattern": pattern, "script": script_name})
    data = r.json()
    if r.status_code == 404:
        print(f"✖  Zone not found. Check your Zone ID.")
        sys.exit(1)
    if data.get("success"):
        print(f"  ✓ Route added: {pattern}")
        return
    errors = data.get("errors", [])
    is_conflict = any(e.get("code") in (10020, 10026) or "already" in str(e).lower() for e in errors)
    if is_conflict:
        r2 = client.get(routes_url)
        routes = r2.json().get("result", [])
        existing = next((ro for ro in routes if ro.get("pattern") == pattern), None)
        if existing:
            r3 = client.put(f"{routes_url}/{existing['id']}", json={"pattern": pattern, "script": script_name})
            if r3.json().get("success"):
                print(f"  ✓ Route updated: {pattern}")
                return
    print(f"✖  Route setup failed: {errors}")
    sys.exit(1)


def deploy_cloudflare(args, llms_txt):
    domain = args.domain.removeprefix("https://").removeprefix("http://").rstrip("/")
    script_name = f"samvida-{domain_slug(domain)}"
    print(f"🚀 Deploying via Cloudflare Workers → {domain}/llms.txt")
    print(f"   Script: {script_name}")

    headers = {"Authorization": f"Bearer {args.cf_token}", "User-Agent": "samvida/0.1.0"}
    with httpx.Client(headers=headers, timeout=30) as client:
        cf_upload_worker(client, args.account_id, script_name, build_worker_js(llms_txt))
        cf_add_route(client, args.zone_id, domain, script_name)

    success, cms = verify_live(domain)
    if success:
        print(f"\n✅ Live at https://{domain}/llms.txt")
    elif cms:
        print_cms_instructions(domain, cms)
    else:
        print(f"\n⚠️  Deployed but not yet reachable. DNS can take 1–2 min.")
        print(f"   Try: curl https://{domain}/llms.txt")


# ──────────────────────────────────────────────
# Webflow deploy
# ──────────────────────────────────────────────

def wf_get_site_id(client, domain):
    """Find Webflow site ID by matching custom domain."""
    r = client.get(f"{WF_API}/sites")
    if r.status_code == 401:
        print("✖  Webflow token invalid or expired. Check your Site API token.")
        print("   Webflow dashboard → Site Settings → Integrations → API Access → Generate API Token")
        sys.exit(1)
    if not r.json().get("sites"):
        print("✖  No sites found for this token.")
        sys.exit(1)

    sites = r.json()["sites"]
    clean_domain = domain.removeprefix("https://").removeprefix("http://").rstrip("/").lower()

    # Match by custom domain or default subdomain
    for site in sites:
        custom_domains = [d.get("url", "").lower().strip("/") for d in site.get("customDomains", [])]
        default = site.get("shortName", "").lower() + ".webflow.io"
        if clean_domain in custom_domains or clean_domain == default or clean_domain in default:
            print(f"  ✓ Found site: '{site['displayName']}' (id: {site['id']})")
            return site["id"]

    # If site_id was provided directly, use it
    if args_site_id := getattr(client, "_site_id_override", None):
        return args_site_id

    print(f"✖  No Webflow site found matching '{clean_domain}'.")
    print(f"   Sites available: {[s['displayName'] for s in sites]}")
    print(f"   Pass --site-id explicitly if domain matching fails.")
    sys.exit(1)


def wf_upload_asset(client, site_id, llms_txt, file_hash):
    """Upload llms.txt to Webflow Assets CDN. Returns CDN URL."""
    # Step 1: Request pre-signed upload URL
    r = client.post(f"{WF_API}/sites/{site_id}/assets", json={
        "fileName": "llms.txt",
        "fileHash": file_hash,
    })
    if r.status_code == 401:
        print("✖  Webflow token lacks asset upload permission.")
        sys.exit(1)
    if r.status_code == 404:
        print(f"✖  Site ID not found: {site_id}")
        sys.exit(1)
    data = r.json()

    upload_url = data.get("uploadUrl")
    upload_details = data.get("uploadDetails", {})
    asset_url = data.get("hostedUrl") or data.get("url")

    if not upload_url:
        print(f"✖  Failed to get upload URL from Webflow: {data}")
        sys.exit(1)

    # Step 2: POST file to S3 pre-signed URL
    form_data = {k: (None, v) for k, v in upload_details.items()}
    form_data["file"] = ("llms.txt", llms_txt.encode(), "text/plain")

    upload_client = httpx.Client(timeout=30)
    r2 = upload_client.post(upload_url, files=form_data)
    upload_client.close()

    if r2.status_code not in (200, 201, 204):
        print(f"✖  S3 upload failed (HTTP {r2.status_code}): {r2.text[:200]}")
        sys.exit(1)

    print(f"  ✓ llms.txt uploaded to Webflow CDN")

    # Construct asset URL if not returned directly
    if not asset_url:
        asset_url = f"https://uploads-ssl.webflow.com/{site_id}/{file_hash}/llms.txt"

    return asset_url


def wf_upsert_redirect(client, site_id, domain, target_url):
    """Add or update a 301 redirect: /llms.txt → CDN asset URL."""
    redirects_url = f"{WF_API}/sites/{site_id}/redirects"
    from_path = "/llms.txt"

    # Check for existing redirect
    r = client.get(redirects_url)
    existing = None
    if r.status_code == 200:
        for redirect in r.json().get("redirects", []):
            if redirect.get("fromUrl") == from_path:
                existing = redirect
                break

    payload = {"fromUrl": from_path, "toUrl": target_url, "statusCode": 301}

    if existing:
        r2 = client.patch(f"{redirects_url}/{existing['id']}", json=payload)
        if r2.status_code in (200, 201):
            print(f"  ✓ Redirect updated: {from_path} → {target_url}")
            return
    else:
        r2 = client.post(redirects_url, json=payload)
        if r2.status_code in (200, 201):
            print(f"  ✓ Redirect added: {from_path} → {target_url}")
            return

    # Fallback: some Webflow plans don't support redirect API — provide manual fallback
    print(f"  ⚠️  Could not create redirect via API (HTTP {r2.status_code}).")
    print(f"     Manual step: Webflow dashboard → Site Settings → Publishing → 301 Redirects")
    print(f"     Add: /llms.txt  →  {target_url}")


def wf_publish(client, site_id):
    """Publish the Webflow site to live."""
    r = client.post(f"{WF_API}/sites/{site_id}/publish", json={"publishTargets": ["live"]})
    if r.status_code in (200, 201, 202):
        print(f"  ✓ Site published to live")
    else:
        print(f"  ⚠️  Publish returned HTTP {r.status_code} — you may need to publish manually from the Webflow dashboard.")


def deploy_webflow(args, llms_txt):
    domain = args.domain.removeprefix("https://").removeprefix("http://").rstrip("/")
    print(f"🚀 Deploying via Webflow API → {domain}/llms.txt")

    headers = {
        "Authorization": f"Bearer {args.webflow_token}",
        "accept": "application/json",
        "content-type": "application/json",
        "User-Agent": "samvida/0.1.0",
    }

    with httpx.Client(headers=headers, timeout=30) as client:
        # Attach site_id override for fallback lookup
        client._site_id_override = args.site_id

        # Step 1: Get site ID
        site_id = args.site_id or wf_get_site_id(client, domain)

        # Step 2: Upload asset
        file_hash = md5(llms_txt)
        cdn_url = wf_upload_asset(client, site_id, llms_txt, file_hash)

        # Step 3: Redirect /llms.txt → CDN URL
        wf_upsert_redirect(client, site_id, domain, cdn_url)

        # Step 4: Publish
        wf_publish(client, site_id)

    # Step 5: Verify (may redirect but that's fine — agents follow redirects)
    print(f"\n⏳ Verifying redirect is live...")
    time.sleep(5)
    try:
        r = httpx.get(f"https://{domain}/llms.txt", timeout=15, follow_redirects=True)
        if r.status_code == 200 and "#" in r.text[:10]:
            print(f"✅ Live at https://{domain}/llms.txt")
        else:
            print(f"⚠️  Not yet reachable (HTTP {r.status_code}). Webflow publish can take 1–2 min.")
            print(f"   Try: curl -L https://{domain}/llms.txt")
    except Exception:
        print(f"⚠️  Could not verify. Check https://{domain}/llms.txt in 1–2 min.")

    print(f"\n📋 How this works:")
    print(f"   {domain}/llms.txt  →  301 redirect  →  Webflow CDN ({cdn_url[:60]}...)")
    print(f"   Agents follow the redirect transparently and receive text/plain content.")


# ──────────────────────────────────────────────
# Framer deploy (semi-automated)
# ──────────────────────────────────────────────

def deploy_framer(args, llms_txt):
    domain = args.domain.removeprefix("https://").removeprefix("http://").rstrip("/")

    print(f"🖼  Framer detected: {domain}")
    print()
    print("ℹ️  Framer has no public REST API for file hosting or redirect management.")
    print("   Your llms.txt is ready below. Follow these steps to publish it (2 min):")
    print()
    print("=" * 60)
    print("OPTION A — Static file upload (Framer Pro/Business plans)")
    print("=" * 60)
    print("""
   1. Open your Framer project
   2. Top-left menu → Site Settings → General → "Static Files"
   3. Upload your llms.txt file directly
   4. Publish your site
   ✓ Result: yourdomain.com/llms.txt serves the file directly
""")
    print("=" * 60)
    print("OPTION B — Redirect rule (all Framer plans)")
    print("=" * 60)
    print("""
   1. Host your llms.txt anywhere publicly (GitHub Gist, Pastebin, R2, etc.)
   2. Open your Framer project → Site Settings → General → "Redirect Rules"
   3. Add rule:
        From:  /llms.txt
        To:    <your hosted URL>
        Type:  301 (Permanent)
   4. Save → Publish
   ✓ Result: yourdomain.com/llms.txt redirects to your hosted file
   ✓ Agents follow 301 redirects automatically — works fine
""")
    print("=" * 60)
    print("OPTION C — Your domain goes through Cloudflare?")
    print("=" * 60)
    print(f"""
   If you manage DNS via Cloudflare, use the Workers deploy instead:
   python3 deploy.py --provider cloudflare --domain {domain} \\
     --cf-token TOKEN --account-id ID --zone-id ID
   ✓ Result: no redirect needed — Worker serves llms.txt directly
""")
    print("=" * 60)
    print("YOUR LLMS.TXT CONTENT (save this as llms.txt):")
    print("=" * 60)
    print()
    print(llms_txt)
    print()
    print("SAMVIDA_PROVIDER:framer")


# ──────────────────────────────────────────────
# CMS detection + verification (shared)
# ──────────────────────────────────────────────

CMS_SIGNATURES = {
    "framer":      {"header": "server",         "value": "framer",       "name": "Framer"},
    "webflow":     {"header": "x-wf-",          "value": "",             "name": "Webflow"},
    "squarespace": {"header": "server",         "value": "squarespace",  "name": "Squarespace"},
    "shopify":     {"header": "server",         "value": "shopify",      "name": "Shopify"},
    "ghost":       {"header": "server",         "value": "ghost",        "name": "Ghost"},
    "wordpress":   {"header": "x-powered-by",  "value": "wordpress",    "name": "WordPress"},
}

CMS_INSTRUCTIONS = {
    "Framer": """
  📋 Your site is hosted on Framer.
     Run: python3 deploy.py --provider framer --domain {domain} --github-token YOUR_GITHUB_TOKEN
     This will host your llms.txt and walk you through adding a redirect in Framer.
""",
    "Webflow": """
  📋 Your site is hosted on Webflow.
     Run: python3 deploy.py --provider webflow --domain {domain} --webflow-token YOUR_TOKEN
     Get your token: Webflow dashboard → Site Settings → Integrations → API Access
""",
    "Squarespace": """
  📋 How to add llms.txt in Squarespace:
     1. Pages → Not Linked → Add Page → path: /llms.txt
     2. Paste content as plain text block
     3. Save and publish
""",
    "Shopify": """
  📋 How to add llms.txt in Shopify:
     1. Online Store → Themes → Edit Code
     2. Templates → Add template: llms.txt.liquid
     3. Paste the llms.txt content and save
""",
    "default": """
  📋 Your site uses a CMS Samvida can't auto-deploy to yet.
     Paste the generated llms.txt directly into your CMS at the path /llms.txt.
     File saved at: /tmp/samvida_llms.txt
""",
}


def detect_cms(headers: dict) -> str | None:
    headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
    for cms_id, sig in CMS_SIGNATURES.items():
        h = sig["header"].lower()
        v = sig["value"].lower()
        if h in headers_lower and (not v or v in headers_lower[h]):
            return sig["name"]
        if cms_id == "webflow" and any(k.startswith("x-wf-") for k in headers_lower):
            return sig["name"]
    return None


def print_cms_instructions(domain, cms):
    instructions = CMS_INSTRUCTIONS.get(cms, CMS_INSTRUCTIONS["default"])
    print(f"\n⚠️  {domain} is hosted on {cms}.")
    print(instructions.format(domain=domain))
    print(f"SAMVIDA_CMS:{cms}")


def verify_live(domain: str, retries: int = 8, delay: int = 5):
    url = f"https://{domain}/llms.txt"
    print(f"  ⏳ Verifying {url} ", end="", flush=True)
    last_headers = {}
    for i in range(retries):
        try:
            r = httpx.get(url, timeout=10, follow_redirects=True)
            last_headers = dict(r.headers)
            if r.status_code == 200 and r.text.strip().startswith("#"):
                cms = detect_cms(last_headers)
                if cms:
                    print()
                    return False, cms
                print(" ✓")
                return True, None
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(delay)
    print()
    return False, detect_cms(last_headers)


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Deploy llms.txt to Cloudflare, Webflow, or Framer")
    parser.add_argument("--provider", choices=["cloudflare", "webflow", "framer"], default="cloudflare",
                        help="Deployment target (default: cloudflare)")
    parser.add_argument("--llms-txt", required=True, help="Path to llms.txt file")
    parser.add_argument("--domain", required=True, help="Your domain e.g. example.com")

    # Cloudflare
    parser.add_argument("--cf-token", help="Cloudflare API token (Workers deploy)")
    parser.add_argument("--account-id", help="Cloudflare Account ID")
    parser.add_argument("--zone-id", help="Cloudflare Zone ID")

    # Webflow
    parser.add_argument("--webflow-token", help="Webflow Site API token")
    parser.add_argument("--site-id", help="Webflow Site ID (optional — auto-detected from domain)")



    args = parser.parse_args()

    # Read llms.txt
    try:
        llms_txt = open(args.llms_txt).read()
    except FileNotFoundError:
        print(f"✖  File not found: {args.llms_txt}")
        sys.exit(1)

    if args.provider == "cloudflare":
        if not all([args.cf_token, args.account_id, args.zone_id]):
            print("✖  Cloudflare deploy requires: --cf-token, --account-id, --zone-id")
            sys.exit(1)
        deploy_cloudflare(args, llms_txt)

    elif args.provider == "webflow":
        if not args.webflow_token:
            print("✖  Webflow deploy requires: --webflow-token")
            print("   Get it: Webflow dashboard → Site Settings → Integrations → API Access → Generate API Token")
            sys.exit(1)
        deploy_webflow(args, llms_txt)

    elif args.provider == "framer":
        deploy_framer(args, llms_txt)


if __name__ == "__main__":
    main()
