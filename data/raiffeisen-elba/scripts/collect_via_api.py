#!/usr/bin/env python3
"""
Collect documents via API endpoint (much faster and more reliable)
"""
import sys
import time
import json
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from elba import load_credentials, login, URL_DOCUMENTS, PROFILE_DIR, _safe_output_path, WORKSPACE_ROOT

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("ERROR: playwright not installed")
    sys.exit(1)

def extract_bearer_token(page):
    """Extract the Authorization bearer token from the page"""
    print("[token] Extracting bearer token...", flush=True)
    
    # Wait a bit for any background requests to complete
    time.sleep(2)
    
    # Try to get the token from localStorage or sessionStorage
    token = page.evaluate("""() => {
        // Check localStorage
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            const value = localStorage.getItem(key);
            if (value && (value.includes('Bearer') || key.includes('token') || key.includes('auth'))) {
                try {
                    const parsed = JSON.parse(value);
                    if (parsed.access_token) return parsed.access_token;
                    if (parsed.token) return parsed.token;
                    if (typeof parsed === 'string' && parsed.startsWith('Bearer ')) {
                        return parsed.substring(7);
                    }
                } catch {
                    if (typeof value === 'string' && value.match(/^[A-Za-z0-9_-]{20,}$/)) {
                        return value;
                    }
                }
            }
        }
        
        // Check sessionStorage
        for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            const value = sessionStorage.getItem(key);
            if (value && (value.includes('Bearer') || key.includes('token') || key.includes('auth'))) {
                try {
                    const parsed = JSON.parse(value);
                    if (parsed.access_token) return parsed.access_token;
                    if (parsed.token) return parsed.token;
                    if (typeof parsed === 'string' && parsed.startsWith('Bearer ')) {
                        return parsed.substring(7);
                    }
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
    
    print("[token] Token not found in storage, will extract from network requests", flush=True)
    return None

def get_bearer_token_from_context(context, page):
    """Get bearer token from browser context"""
    # First try to extract from page storage
    token = extract_bearer_token(page)
    if token:
        return token
    
    # If not found, navigate to documents page and intercept the API request
    print("[token] Navigating to documents page to capture API token...", flush=True)
    
    captured_token = {'value': None}
    
    def handle_request(route, request):
        auth_header = request.headers.get('authorization', '')
        if auth_header.startswith('Bearer '):
            captured_token['value'] = auth_header[7:]  # Remove 'Bearer ' prefix
            print(f"[token] Captured from request: {captured_token['value'][:20]}...", flush=True)
        route.continue_()
    
    page.route('**/api/**', handle_request)
    
    # Trigger a request by navigating to documents
    page.goto(URL_DOCUMENTS, wait_until="domcontentloaded")
    time.sleep(3)
    
    page.unroute('**/api/**')
    
    return captured_token['value']

def fetch_documents_batch(token, cookies, from_date, to_date, skip, limit=50):
    """Fetch a batch of documents from the API"""
    url = "https://mein.elba.raiffeisen.at/api/bankingquer-dokumentenablage/dokumentenablage-ui/rest/dokumente/filter"
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.3 Safari/605.1.15"
    }
    
    body = {
        "von": f"{from_date}T00:00:00",
        "bis": f"{to_date}T00:00:00",
        "skip": skip,
        "limit": limit
    }
    
    response = requests.post(url, json=body, headers=headers, cookies=cookies)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"[api] Request failed with status {response.status_code}: {response.text}", flush=True)
        return None

def collect_all_documents(token, cookies, from_date="2025-01-01", to_date="2025-12-31"):
    """Collect all documents using pagination"""
    print(f"[api] Collecting documents from {from_date} to {to_date}...", flush=True)
    
    all_docs = []
    skip = 0
    limit = 50
    
    while True:
        print(f"[api] Fetching batch: skip={skip}, limit={limit}", flush=True)
        
        result = fetch_documents_batch(token, cookies, from_date, to_date, skip, limit)
        
        if result is None:
            print("[api] Failed to fetch batch, stopping", flush=True)
            break
        
        # The API might return different structures, check common ones
        docs = []
        if isinstance(result, list):
            docs = result
        elif isinstance(result, dict):
            if 'dokumente' in result:
                docs = result['dokumente']
            elif 'items' in result:
                docs = result['items']
            elif 'data' in result:
                docs = result['data']
            else:
                # Just try to use the whole result
                docs = [result]
        
        if not docs or len(docs) == 0:
            print(f"[api] No more documents (got {len(docs)} documents in this batch)", flush=True)
            break
        
        all_docs.extend(docs)
        print(f"[api] Got {len(docs)} documents, total: {len(all_docs)}", flush=True)
        
        # If we got fewer than limit, we're done
        if len(docs) < limit:
            print(f"[api] Received fewer than {limit} documents, we've reached the end", flush=True)
            break
        
        skip += limit
    
    print(f"[api] Collection complete: {len(all_docs)} documents", flush=True)
    return all_docs

def main():
    elba_id, pin = load_credentials()
    if not elba_id or not pin:
        print("Credentials not found")
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
            # Login
            print("[main] Logging in to get session and token...")
            page.goto(URL_DOCUMENTS, wait_until="networkidle")
            time.sleep(3)
            
            if "sso.raiffeisen.at" in page.url or "mein-login" in page.url:
                print("[main] Not logged in, performing login...")
                if not login(page, elba_id, pin):
                    print("[main] Login failed")
                    sys.exit(1)
                print("[main] Login successful!")
            else:
                print("[main] Already logged in!")
            
            # Get bearer token
            token = get_bearer_token_from_context(context, page)
            
            if not token:
                print("[main] ERROR: Could not extract bearer token")
                sys.exit(1)
            
            print(f"[main] Using bearer token: {token[:20]}...", flush=True)
            
            # Get cookies from context
            cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
            
            # Collect documents via API
            all_docs = collect_all_documents(token, cookies, "2025-01-01", "2025-12-31")
            
            print(f"\n{'='*60}")
            print(f"COLLECTION COMPLETE: {len(all_docs)} documents")
            print(f"{'='*60}")
            
            # Save raw API response (sandboxed to workspace or /tmp)
            output_file = _safe_output_path(str(WORKSPACE_ROOT / "raiffeisen-elba" / "elba_documents_api.json"), WORKSPACE_ROOT)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(all_docs, f, indent=2, ensure_ascii=False)
            print(f"\nAPI response saved to: {output_file}")
            
            # Create a simple list
            text_file = _safe_output_path(str(WORKSPACE_ROOT / "raiffeisen-elba" / "elba_documents_api_list.txt"), WORKSPACE_ROOT)
            with open(text_file, 'w') as f:
                for i, doc in enumerate(all_docs, 1):
                    # Try to extract name from different possible fields
                    name = doc.get('name') or doc.get('dokumentName') or doc.get('titel') or str(doc)
                    date = doc.get('date') or doc.get('datum') or doc.get('erstellt') or ''
                    f.write(f"{i}. {date} | {name}\n")
            print(f"Simple list saved to: {text_file}")
            
            # Show first 30
            print("\nFirst 30 documents:")
            for i, doc in enumerate(all_docs[:30], 1):
                name = doc.get('name') or doc.get('dokumentName') or doc.get('titel') or 'Unknown'
                print(f"  {i}. {name}")
            
            if len(all_docs) > 30:
                print(f"\n  ... and {len(all_docs) - 30} more")
            
        finally:
            context.close()

if __name__ == "__main__":
    main()
