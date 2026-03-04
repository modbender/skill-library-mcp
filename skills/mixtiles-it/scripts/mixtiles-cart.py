#!/usr/bin/env python3
"""
Upload a local image or URL to a public host, then print a Mixtiles cart URL.

Usage:
  mixtiles-cart.py <local-file-or-url> [--size SIZE]
  mixtiles-cart.py --batch <image1> <image2> ... [--size SIZE]

Mixtiles uses Cloudinary's fetch API to process images. Cloudinary's fetch for
the 'mixtiles' cloud only allows fetching from other Cloudinary URLs. So we
upload images to Cloudinary (demo account, unsigned preset) to get a URL that
Mixtiles can actually display.

Env vars (optional overrides):
  CLOUDINARY_CLOUD    - Cloudinary cloud name (default: demo)
  CLOUDINARY_PRESET   - Cloudinary unsigned upload preset (default: unsigned)
  MIXTILES_UPLOAD_URL  - Custom upload API endpoint (Railway, currently down)
  MIXTILES_UPLOAD_KEY  - Custom upload API key
"""
import argparse, json, mimetypes, os, subprocess, sys
import urllib.parse, urllib.request

DEFAULT_UPLOAD_URL = os.environ.get("MIXTILES_UPLOAD_URL", "")
DEFAULT_UPLOAD_KEY = os.environ.get("MIXTILES_UPLOAD_KEY", "")
MIXTILES_DESIGN_URL = "https://www.mixtiles.com/photos"
CLOUDINARY_UPLOAD_URL = "https://api.cloudinary.com/v1_1/{cloud}/image/upload"


def upload_to_cloudinary(file_path: str, cloud: str = "demo", preset: str = "unsigned") -> str:
    """Upload a local file to Cloudinary via unsigned upload. Returns a public URL.

    Mixtiles uses Cloudinary fetch (res.cloudinary.com/mixtiles/image/fetch/...)
    to display images. Their Cloudinary account restricts fetch sources to other
    Cloudinary URLs only, so this is the only reliable upload target.
    """
    url = CLOUDINARY_UPLOAD_URL.format(cloud=cloud)
    result = subprocess.run(
        ["curl", "-sf",
         "-F", f"file=@{file_path}",
         "-F", f"upload_preset={preset}",
         url],
        capture_output=True, text=True, timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Cloudinary upload failed: {result.stderr}")
    body = json.loads(result.stdout)
    public_url = body.get("secure_url", "")
    if not public_url:
        err = body.get("error", {}).get("message", "unknown error")
        raise RuntimeError(f"Cloudinary error: {err}")
    return public_url


def _validate_url(url: str) -> None:
    """Block private/internal URLs to prevent SSRF."""
    import ipaddress, socket
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Unsupported scheme: {parsed.scheme}")
    hostname = parsed.hostname or ""
    if not hostname:
        raise ValueError("No hostname in URL")
    # Block obvious internal hostnames
    blocked = ("localhost", "127.0.0.1", "0.0.0.0", "metadata.google.internal", "169.254.169.254")
    if hostname.lower() in blocked or hostname.lower().endswith(".local"):
        raise ValueError(f"Blocked internal hostname: {hostname}")
    # Resolve and check for private IPs
    try:
        for info in socket.getaddrinfo(hostname, None):
            addr = ipaddress.ip_address(info[4][0])
            if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_reserved:
                raise ValueError(f"URL resolves to private/reserved IP: {addr}")
    except socket.gaierror:
        raise ValueError(f"Cannot resolve hostname: {hostname}")


def download_to_temp(source_url: str) -> str:
    """Download a remote image to a temp file. Returns the temp file path."""
    import tempfile
    _validate_url(source_url)
    req = urllib.request.Request(source_url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        ext = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ".jpg"
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(resp.read())
        tmp.close()
        return tmp.name


def upload_via_railway(source_url: str, api_url: str, api_key: str) -> str:
    data = json.dumps({"sourceUrl": source_url}).encode()
    req = urllib.request.Request(
        api_url, data=data,
        headers={"Content-Type": "application/json", "x-api-key": api_key},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read())
    url = body.get("publicUrl", "")
    if not url:
        raise RuntimeError(f"No publicUrl: {body}")
    return url.replace("http:", "https:", 1)


def build_mixtiles_url(image_url: str, size: str = "RECTANGLE_12X16") -> str:
    descriptor = f"{image_url}|{size}|||shallow"
    params = urllib.parse.urlencode({"photos": descriptor})
    return f"{MIXTILES_DESIGN_URL}?{params}"


def build_mixtiles_multi_url(image_urls: list[str], size: str = "RECTANGLE_12X16") -> str:
    """Build a Mixtiles cart URL containing multiple photos.

    Uses repeated `photos` query params — one per image.
    """
    params = "&".join(
        urllib.parse.urlencode({"photos": f"{url}|{size}|||shallow"})
        for url in image_urls
    )
    return f"{MIXTILES_DESIGN_URL}?{params}"


def resolve_and_upload(image: str, cloud: str, preset: str,
                       upload_url: str = "", upload_key: str = "") -> str:
    """Resolve a local file or URL to a Cloudinary public URL."""
    is_local = not image.startswith("http://") and not image.startswith("https://")
    temp_file = None

    if is_local:
        if not os.path.isfile(image):
            raise FileNotFoundError(f"File not found: {image}")
        file_to_upload = image
    else:
        file_to_upload = download_to_temp(image)
        temp_file = file_to_upload
        print(f"[downloaded remote image: {image}]", file=sys.stderr)

    try:
        public_url = upload_to_cloudinary(file_to_upload, cloud, preset)
        print(f"[uploaded via Cloudinary: {os.path.basename(image)}]", file=sys.stderr)
        return public_url
    except Exception as e:
        # Fallback: try Railway API (currently down, but may come back)
        if not is_local and upload_url:
            try:
                public_url = upload_via_railway(image, upload_url, upload_key)
                print(f"[uploaded via Railway API: {image}]", file=sys.stderr)
                return public_url
            except Exception as e2:
                raise RuntimeError(
                    f"All upload methods failed for {image}:\n  Cloudinary: {e}\n  Railway: {e2}"
                )
        raise RuntimeError(f"Upload failed for {image}: {e}")
    finally:
        if temp_file:
            try:
                os.unlink(temp_file)
            except OSError:
                pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image", nargs="?", help="Local file path or public URL (single-photo mode)")
    parser.add_argument("--batch", nargs="+", metavar="IMAGE",
                        help="Multiple image paths/URLs for a multi-photo cart")
    parser.add_argument("--size", default="RECTANGLE_12X16")
    parser.add_argument("--cloud", default=os.environ.get("CLOUDINARY_CLOUD", "demo"))
    parser.add_argument("--preset", default=os.environ.get("CLOUDINARY_PRESET", "unsigned"))
    parser.add_argument("--upload-url", default=os.environ.get("MIXTILES_UPLOAD_URL", DEFAULT_UPLOAD_URL))
    parser.add_argument("--upload-key", default=os.environ.get("MIXTILES_UPLOAD_KEY", DEFAULT_UPLOAD_KEY))
    args = parser.parse_args()

    if not args.image and not args.batch:
        parser.error("Provide either a single image or --batch <image1> <image2> ...")

    images = args.batch if args.batch else [args.image]

    public_urls = []
    for img in images:
        try:
            url = resolve_and_upload(img, args.cloud, args.preset,
                                     args.upload_url, args.upload_key)
            public_urls.append(url)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

    if len(public_urls) == 1:
        cart_url = build_mixtiles_url(public_urls[0], args.size)
    else:
        cart_url = build_mixtiles_multi_url(public_urls, args.size)

    print(cart_url)


if __name__ == "__main__":
    main()
