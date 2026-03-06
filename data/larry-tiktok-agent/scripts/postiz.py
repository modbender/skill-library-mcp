#!/usr/bin/env python3
"""
Larry — Postiz Integration
Uploaded TikTok-Karussells via Postiz API als Draft.
Alex drückt dann nur noch "Publish" in der App.
"""
import json, requests
from pathlib import Path

def _get_auth_headers(base_url: str, config: dict) -> dict:
    """Login + Cookie als Header zurückgeben (Postiz Self-Hosted Auth)."""
    resp = requests.post(
        f"{base_url}/auth/login",
        json={"email": config.get("postiz_email", ""),
              "password": config.get("postiz_password", ""),
              "provider": "LOCAL"},
        timeout=10
    )
    if not resp.ok:
        raise Exception(f"Postiz Login fehlgeschlagen: {resp.status_code}")
    token = resp.cookies.get("auth")
    if not token:
        raise Exception("Kein Auth-Cookie erhalten")
    return {"Cookie": f"auth={token}"}


def upload_to_tiktok(post_data: dict, portal: dict, config: dict) -> dict:
    """
    Uploaded Slideshow als TikTok Draft via Postiz.
    Self-Hosted: Cookie-basierte Auth statt Bearer Token.
    """
    base_url = config.get("postiz_base_url", "https://api.postiz.com/v1")
    account_id = portal.get("tiktok_account_id", "")

    auth = _get_auth_headers(base_url, config)
    headers = {**auth, "Content-Type": "application/json"}

    # Bilder hochladen
    media_ids = []
    for img_path in post_data["images"]:
        media_id = _upload_media(base_url, auth, img_path)
        if media_id:
            media_ids.append(media_id)

    if not media_ids:
        print("❌ Kein Bild hochgeladen")
        return None

    # Caption + Hashtags zusammenbauen
    caption = post_data["caption"]

    # Post erstellen (als Draft)
    payload = {
        "type": "carousel",
        "content": caption,
        "media": [{"id": mid} for mid in media_ids],
        "settings": {
            "account": account_id,
            "status": "draft"  # Draft, nicht sofort live
        }
    }

    try:
        resp = requests.post(
            f"{base_url}/posts",
            headers=headers,
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        result = resp.json()
        print(f"  ✅ Draft erstellt: ID {result.get('id', '?')}")
        return result
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ Postiz API Fehler: {e.response.status_code} — {e.response.text[:200]}")
        return None
    except Exception as e:
        print(f"  ❌ Upload Fehler: {e}")
        return None

def _upload_media(base_url: str, auth: dict, img_path: str) -> str:
    """Uploaded ein Bild zu Postiz und gibt die Media-ID zurück"""
    path = Path(img_path)
    if not path.exists():
        print(f"  ⚠️  Bild nicht gefunden: {img_path}")
        return None

    try:
        with open(img_path, "rb") as f:
            resp = requests.post(
                f"{base_url}/media/upload-simple",
                headers=auth,
                files={"file": (path.name, f, "image/jpeg")},
                timeout=60
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("id")
    except Exception as e:
        print(f"  ⚠️  Media-Upload Fehler: {e}")
        return None

def check_stats(config: dict) -> list:
    """
    Ruft Performance-Daten für alle gespeicherten Posts ab.
    Wird täglich aufgerufen um Hook-Performance zu tracken.
    """
    base_url = config.get("postiz_base_url", "https://api.postiz.com/v1")
    api_key = config["postiz_api_key"]
    headers = {"Authorization": f"Bearer {api_key}"}

    log_file = Path(__file__).parent.parent / "logs" / "performance.json"
    if not log_file.exists():
        return []

    with open(log_file) as f:
        posts = json.load(f)

    updated = []
    for post in posts:
        post_id = post.get("post_id")
        if not post_id:
            updated.append(post)
            continue
        try:
            resp = requests.get(
                f"{base_url}/posts/{post_id}/analytics",
                headers=headers,
                timeout=10
            )
            if resp.ok:
                stats = resp.json()
                post["views"] = stats.get("views", post.get("views", 0))
                post["likes"] = stats.get("likes", post.get("likes", 0))
                post["comments"] = stats.get("comments", post.get("comments", 0))
                post["shares"] = stats.get("shares", post.get("shares", 0))
        except Exception:
            pass
        updated.append(post)

    with open(log_file, "w") as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)

    return updated
