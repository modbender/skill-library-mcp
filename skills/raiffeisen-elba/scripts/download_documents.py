#!/usr/bin/env python3
"""
Download all collected documents via API
"""
import sys
import json
import re
import requests
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from elba import load_credentials, login, URL_DOCUMENTS, PROFILE_DIR, _safe_output_path, _safe_download_filename, WORKSPACE_ROOT

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed")
    sys.exit(1)

def get_bearer_token_from_browser(page):
    """Extract bearer token from browser"""
    print("[token] Extracting bearer token...", flush=True)
    
    # First try localStorage/sessionStorage
    token = page.evaluate("""() => {
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            const value = localStorage.getItem(key);
            if (value && (value.includes('Bearer') || key.includes('token') || key.includes('auth'))) {
                try {
                    const parsed = JSON.parse(value);
                    if (parsed.access_token) return parsed.access_token;
                    if (parsed.token) return parsed.token;
                } catch {
                    if (typeof value === 'string' && value.match(/^[A-Za-z0-9_-]{20,}$/)) {
                        return value;
                    }
                }
            }
        }
        
        for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            const value = sessionStorage.getItem(key);
            if (value && (value.includes('Bearer') || key.includes('token') || key.includes('auth'))) {
                try {
                    const parsed = JSON.parse(value);
                    if (parsed.access_token) return parsed.access_token;
                    if (parsed.token) return parsed.token;
                } catch {
                    if (typeof value === 'string' && value.match(/^[A-Za-z0-9_-]{20,}$/)) {
                        return value;
                    }
                }
            }
        }
        return null;
    }""")
    
    if token:
        print(f"[token] Found token in storage: {token[:20]}...", flush=True)
        return token
    
    # If not found, capture from network request
    print("[token] Token not in storage, capturing from API request...", flush=True)
    captured_token = {'value': None}
    
    def handle_request(route, request):
        auth_header = request.headers.get('authorization', '')
        if auth_header.startswith('Bearer '):
            captured_token['value'] = auth_header[7:]
            print(f"[token] Captured from request: {captured_token['value'][:20]}...", flush=True)
        route.continue_()
    
    page.route('**/api/**', handle_request)
    
    # Trigger a request by navigating to documents
    page.goto(URL_DOCUMENTS, wait_until="domcontentloaded")
    time.sleep(3)
    
    page.unroute('**/api/**')
    
    return captured_token['value']

def _safe_filename_component(value, default="file"):
    """Sanitize a string for safe use in filenames."""
    s = str(value or "").strip()
    if not s:
        return default
    s = s.replace("/", "_").replace("\\", "_")
    s = re.sub(r'\.\.+', '.', s)
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)
    s = s.strip("._-")
    return (s or default)[:80]


def download_document(doc, token, cookies, output_dir):
    """Download a single document"""
    system_id = doc['systemId']
    doc_id = doc['dokumentenId']
    version_id = doc.get('versionsId')
    file_name = _safe_filename_component(doc.get('dateiName', doc_id))
    date = _safe_filename_component(doc.get('erstellungsDatum', '')[:10], default="unknown")
    
    # Construct filename: YYYY-MM-DD_filename.pdf
    safe_filename = f"{date}_{file_name}.pdf"
    output_path = output_dir / safe_filename
    
    # Skip if already downloaded
    if output_path.exists():
        print(f"[skip] {safe_filename} (already exists)", flush=True)
        return True
    
    # Signed documents (EAZWIEN, etc.) don't use versionsId in URL
    if version_id is None or system_id == "EAZWIEN":
        url = f"https://mein.elba.raiffeisen.at/api/bankingquer-dokumentenablage/dokumentenablage-ui/rest/dokumente/{system_id}/{doc_id}/download"
    else:
        url = f"https://mein.elba.raiffeisen.at/api/bankingquer-dokumentenablage/dokumentenablage-ui/rest/dokumente/{system_id}/{doc_id}/{version_id}/download"
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3 Safari/605.1.15"
    }
    
    try:
        response = requests.post(url, json={}, headers=headers, cookies=cookies)
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            size_kb = len(response.content) / 1024
            print(f"[ok] {safe_filename} ({size_kb:.1f} KB)", flush=True)
            return True
        else:
            print(f"[error] {safe_filename} - HTTP {response.status_code}", flush=True)
            return False
    except Exception as e:
        print(f"[error] {safe_filename} - {e}", flush=True)
        return False

def main():
    # Check if we have the API response
    api_file = Path("elba_documents_api.json")
    if not api_file.exists():
        print("ERROR: elba_documents_api.json not found. Run collect_via_api.py first.")
        sys.exit(1)
    
    # Load documents
    with open(api_file, 'r') as f:
        documents = json.load(f)
    
    print(f"[main] Loaded {len(documents)} documents from {api_file}")
    
    # Create output directory (sandboxed to workspace)
    output_dir = _safe_output_path(str(WORKSPACE_ROOT / "raiffeisen-elba" / "downloads"), WORKSPACE_ROOT)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[main] Downloading to: {output_dir.absolute()}")
    
    # Get credentials and login to get token
    elba_id, pin = load_credentials()
    if not elba_id or not pin:
        print("ERROR: Credentials not found")
        sys.exit(1)
    
    if not PROFILE_DIR.exists():
        PROFILE_DIR.mkdir(parents=True)
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        
        page = context.new_page()
        
        try:
            # Login to get session and token
            print("[main] Logging in to get token...")
            page.goto(URL_DOCUMENTS, wait_until="networkidle")
            time.sleep(3)
            
            if "sso.raiffeisen.at" in page.url or "mein-login" in page.url:
                print("[main] Performing login...")
                if not login(page, elba_id, pin):
                    print("[main] Login failed")
                    sys.exit(1)
            
            # Get bearer token
            token = get_bearer_token_from_browser(page)
            if not token:
                print("[main] ERROR: Could not extract bearer token")
                sys.exit(1)
            
            # Get cookies
            cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
            
            print(f"\n[main] Starting download of {len(documents)} documents...")
            print("=" * 60)
            
            success = 0
            failed = 0
            skipped = 0
            
            for i, doc in enumerate(documents, 1):
                print(f"[{i}/{len(documents)}] ", end='', flush=True)
                
                result = download_document(doc, token, cookies, output_dir)
                
                if result is True:
                    # Check if it was skipped or downloaded
                    safe_filename = f"{doc.get('erstellungsDatum', '')[:10]}_{doc.get('dateiName', doc['dokumentenId'])}.pdf"
                    if "skip" in str(result):
                        skipped += 1
                    else:
                        success += 1
                else:
                    failed += 1
                
                # Rate limiting
                if i % 10 == 0:
                    time.sleep(1)
            
            print("\n" + "=" * 60)
            print(f"[main] Download complete!")
            print(f"[main] Success: {success}, Failed: {failed}, Skipped: {skipped}")
            print(f"[main] Files saved to: {output_dir.absolute()}")
            
        finally:
            context.close()

if __name__ == "__main__":
    main()
