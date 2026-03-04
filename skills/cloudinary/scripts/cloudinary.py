#!/usr/bin/env python3
"""Cloudinary CLI — Cloudinary — manage images/videos, upload, transform, and search assets via REST API

Zero dependencies beyond Python stdlib.
Built by M. Abidi | agxntsix.ai
"""

import argparse, json, os, sys, urllib.request, urllib.error, urllib.parse

API_BASE = "https://api.cloudinary.com/v1_1/{cloud_name}"

def get_env(name):
    val = os.environ.get(name, "")
    if not val:
        env_path = os.path.join(os.environ.get("WORKSPACE", os.path.expanduser("~/.openclaw/workspace")), ".env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(name + "="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    if not val:
        print(f"Error: {name} not set", file=sys.stderr)
        sys.exit(1)
    return val


def get_headers():
    import base64
    key = get_env("CLOUDINARY_API_KEY")
    secret = get_env("CLOUDINARY_API_SECRET") if "CLOUDINARY_API_SECRET" else ""
    creds = base64.b64encode(f"{key}:{secret}".encode()).decode()
    return {"Authorization": f"Basic {creds}", "Content-Type": "application/json", "Accept": "application/json"}



def get_api_base():
    base = API_BASE
    base = base.replace("{cloud_name}", get_env("CLOUDINARY_CLOUD_NAME"))
    return base

def req(method, path, data=None, params=None):
    headers = get_headers()
    if path.startswith("http"):
        url = path
    else:
        url = get_api_base() + path
    if params:
        qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
        if qs:
            url = f"{url}?{qs}" if "?" not in url else f"{url}&{qs}"
    body = json.dumps(data).encode() if data else None
    r = urllib.request.Request(url, data=body, method=method)
    for k, v in headers.items():
        r.add_header(k, v)
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        raw = resp.read().decode()
        return json.loads(raw) if raw.strip() else {"ok": True}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(json.dumps({"error": True, "code": e.code, "message": err_body}), file=sys.stderr)
        sys.exit(1)


def try_json(val):
    if val is None:
        return None
    try:
        return json.loads(val)
    except (json.JSONDecodeError, ValueError):
        return val


def out(data, human=False):
    if human and isinstance(data, dict):
        for k, v in data.items():
            print(f"  {k}: {v}")
    elif human and isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    print(f"  {k}: {v}")
                print()
            else:
                print(item)
    else:
        print(json.dumps(data, indent=2, default=str))


def cmd_resources(args):
    """List resources."""
    path = "/resources/image"
    params = {}
    if getattr(args, "prefix", None): params["prefix"] = args.prefix
    if getattr(args, "max_results", None): params["max_results"] = args.max_results
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_resource_get(args):
    """Get resource."""
    path = f"/resources/image/upload/{args.public_id}"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_upload(args):
    """Upload asset."""
    path = "/image/upload"
    body = {}
    if getattr(args, "file", None): body["file"] = try_json(args.file)
    if getattr(args, "folder", None): body["folder"] = try_json(args.folder)
    if getattr(args, "public_id", None): body["public_id"] = try_json(args.public_id)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_destroy(args):
    """Delete asset."""
    path = "/image/destroy"
    body = {}
    if getattr(args, "public_id", None): body["public_id"] = try_json(args.public_id)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_rename(args):
    """Rename asset."""
    path = "/image/rename"
    body = {}
    if getattr(args, "from_public_id", None): body["from_public_id"] = try_json(args.from_public_id)
    if getattr(args, "to_public_id", None): body["to_public_id"] = try_json(args.to_public_id)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_search(args):
    """Search assets."""
    path = "/resources/search"
    body = {}
    if getattr(args, "expression", None): body["expression"] = try_json(args.expression)
    if getattr(args, "max_results", None): body["max_results"] = try_json(args.max_results)
    data = req("POST", path, data=body)
    out(data, getattr(args, "human", False))

def cmd_tags(args):
    """List tags."""
    path = "/tags/image"
    params = {}
    if getattr(args, "prefix", None): params["prefix"] = args.prefix
    data = req("GET", path, params=params)
    out(data, getattr(args, "human", False))

def cmd_folders(args):
    """List root folders."""
    path = "/folders"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_folder_create(args):
    """Create folder."""
    path = f"/folders/{args.path}"
    data = req("POST", path)
    out(data, getattr(args, "human", False))

def cmd_folder_delete(args):
    """Delete folder."""
    path = f"/folders/{args.path}"
    data = req("DELETE", path)
    out(data, getattr(args, "human", False))

def cmd_transformations(args):
    """List transformations."""
    path = "/transformations"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_usage(args):
    """Get usage stats."""
    path = "/usage"
    data = req("GET", path)
    out(data, getattr(args, "human", False))

def cmd_presets(args):
    """List upload presets."""
    path = "/upload_presets"
    data = req("GET", path)
    out(data, getattr(args, "human", False))



def main():
    parser = argparse.ArgumentParser(description="Cloudinary CLI")
    parser.add_argument("--human", action="store_true", help="Human-readable output")
    sub = parser.add_subparsers(dest="command")

    resources_p = sub.add_parser("resources", help="List resources")
    resources_p.add_argument("--prefix", help="Folder prefix", default=None)
    resources_p.add_argument("--max_results", help="Max results", default=None)
    resources_p.set_defaults(func=cmd_resources)

    resource_get_p = sub.add_parser("resource-get", help="Get resource")
    resource_get_p.add_argument("public_id", help="Public ID")
    resource_get_p.set_defaults(func=cmd_resource_get)

    upload_p = sub.add_parser("upload", help="Upload asset")
    upload_p.add_argument("--file", help="File URL", default=None)
    upload_p.add_argument("--folder", help="Folder", default=None)
    upload_p.add_argument("--public_id", help="Public ID", default=None)
    upload_p.set_defaults(func=cmd_upload)

    destroy_p = sub.add_parser("destroy", help="Delete asset")
    destroy_p.add_argument("--public_id", help="Public ID", default=None)
    destroy_p.set_defaults(func=cmd_destroy)

    rename_p = sub.add_parser("rename", help="Rename asset")
    rename_p.add_argument("--from_public_id", help="From ID", default=None)
    rename_p.add_argument("--to_public_id", help="To ID", default=None)
    rename_p.set_defaults(func=cmd_rename)

    search_p = sub.add_parser("search", help="Search assets")
    search_p.add_argument("--expression", help="Search expression", default=None)
    search_p.add_argument("--max_results", help="Max results", default=None)
    search_p.set_defaults(func=cmd_search)

    tags_p = sub.add_parser("tags", help="List tags")
    tags_p.add_argument("--prefix", help="Tag prefix", default=None)
    tags_p.set_defaults(func=cmd_tags)

    folders_p = sub.add_parser("folders", help="List root folders")
    folders_p.set_defaults(func=cmd_folders)

    folder_create_p = sub.add_parser("folder-create", help="Create folder")
    folder_create_p.add_argument("path", help="Folder path")
    folder_create_p.set_defaults(func=cmd_folder_create)

    folder_delete_p = sub.add_parser("folder-delete", help="Delete folder")
    folder_delete_p.add_argument("path", help="Folder path")
    folder_delete_p.set_defaults(func=cmd_folder_delete)

    transformations_p = sub.add_parser("transformations", help="List transformations")
    transformations_p.set_defaults(func=cmd_transformations)

    usage_p = sub.add_parser("usage", help="Get usage stats")
    usage_p.set_defaults(func=cmd_usage)

    presets_p = sub.add_parser("presets", help="List upload presets")
    presets_p.set_defaults(func=cmd_presets)


    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
