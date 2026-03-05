import argparse
import base64
import io
import socket
import time
import urllib.error
import urllib.request
from pathlib import Path

from simple_http_server import PathValue, route, server
from simple_http_server.basic_models import Parameter

from funda import Funda

MULTI_PAGE_REQUEST_DELAY_SECONDS = 0.3
SKILL_ROOT = Path(__file__).resolve().parents[1]


class ValidationError(ValueError):
    def __init__(self, field, message):
        super().__init__(message)
        self.field = field
        self.message = message


def parse_args():
    parser = argparse.ArgumentParser(description="Funda Gateway")
    parser.add_argument(
        "--port", type=int, default=9090, help="Port to run the server on"
    )
    parser.add_argument(
        "--timeout", type=int, default=10, help="Timeout for Funda API calls in seconds"
    )
    return parser.parse_args()


def fetch_public_id(url):
    """Extract the public ID from a Funda listing URL."""
    # Example URL: https://www.funda.nl/detail/koop/amsterdam/appartement-aragohof-11-1/43242669/
    # The public ID is the number after the last hyphen and before the trailing slash.
    try:
        return url.rstrip("/").split("/")[-1]
    except IndexError:
        raise ValueError(f"Invalid Funda listing URL: {url}")


def _ensure_boundries(value, min_value, max_value):
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def _as_list_param(value, lowercase=True):
    if isinstance(value, list):
        items = value
    elif value is None:
        return []
    else:
        items = [value]

    result = []
    for item in items:
        if isinstance(item, str):
            for part in item.split(","):
                text = part.strip()
                if not text:
                    continue
                if lowercase:
                    text = text.lower()
                result.append(text)
        elif item is not None:
            result.append(str(item))
    return result


def _as_optional_int(value, field_name=None):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return int(text)
    except (TypeError, ValueError) as exc:
        if field_name is None:
            raise
        raise ValidationError(field_name, "must be an integer") from exc


def _as_optional_str(value, lowercase=True):
    if value is None:
        return None
    if isinstance(value, list):
        if not value:
            return None
        value = value[0]
    text = str(value).strip()
    if lowercase:
        text = text.lower()
    return text or None


def _as_bool_flag(value):
    text = (_as_optional_str(value, lowercase=True) or "").lower()
    return text in {"1", "true", "yes", "on"}


def _error_response(status_code, code, message, details=None):
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return (status_code, body)


def _build_preview_base64(image_bytes, max_size=320, quality=65):
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is required for preview generation. Install package 'Pillow'."
        ) from exc

    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB")
        img.thumbnail((max_size, max_size))
        output = io.BytesIO()
        img.save(output, format="JPEG", optimize=True, quality=quality)
        preview_bytes = output.getvalue()

    return "image/jpeg", base64.b64encode(preview_bytes).decode("ascii")


def _resolve_output_base_dir(dir_value):
    relative = _as_optional_str(dir_value, lowercase=False) or "previews"
    relative_path = Path(relative)
    if relative_path.is_absolute():
        raise ValueError("dir must be a relative path")

    base_dir = (SKILL_ROOT / relative_path).resolve()
    skill_root_resolved = SKILL_ROOT.resolve()
    if skill_root_resolved not in base_dir.parents and base_dir != skill_root_resolved:
        raise ValueError("dir must stay inside skill root")

    return base_dir


def is_port_listening(port, host="127.0.0.1", timeout=0.5):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, int(port))) == 0


def spin_up_server(server_port, funda_timeout):
    if is_port_listening(server_port):
        raise RuntimeError(f"Gateway already running on 127.0.0.1:{server_port}")

    f = Funda(timeout=funda_timeout)

    @route("/get_listing/{id}", method=["GET"])
    def get_listing(id=PathValue()):
        try:
            return f.get_listing(id).to_dict()
        except LookupError:
            return _error_response(404, "listing_not_found", f"Listing '{id}' was not found")
        except ValueError as exc:
            return _error_response(400, "invalid_listing_id", str(exc))
        except Exception as exc:
            return _error_response(502, "upstream_error", str(exc))

    @route("/get_price_history/{id}", method=["GET"])
    def get_price_history(id=PathValue()):
        try:
            listing = f.get_listing(id)
            return {item["date"]: item for item in f.get_price_history(listing)}
        except LookupError:
            return _error_response(404, "listing_not_found", f"Listing '{id}' was not found")
        except ValueError as exc:
            return _error_response(400, "invalid_listing_id", str(exc))
        except Exception as exc:
            return _error_response(502, "upstream_error", str(exc))

    @route("/get_previews/{id}", method=["GET"])
    def get_previews(
        id=PathValue(),
        limit=Parameter("limit", default="5"),  # Maximum number of previews to return
        preview_size=Parameter("preview_size", default="320"),  # Max preview side in px
        preview_quality=Parameter("preview_quality", default="65"),  # JPEG quality
        save=Parameter("save", default="0"),  # Save resized previews to disk
        dir=Parameter("dir", default=""),  # Relative output directory inside skill root
        filename_pattern=Parameter("filename_pattern", default=""),  # e.g. {id}_{index}
        ids=Parameter("ids", default=""),
    ):  # Comma-separated photo IDs (like 224/802/529). If omitted, take first N photos.

        def extract_id(url):
            # example URL: https://images.funda.nl/hdp/224/802/529/jpeg/224_802_529.jpeg
            # returns: "224/802/529"
            return "/".join(url.split("/")[-3:]).split(".")[0]

        try:
            listing = f.get_listing(id)
        except LookupError:
            return _error_response(404, "listing_not_found", f"Listing '{id}' was not found")
        except ValueError as exc:
            return _error_response(400, "invalid_listing_id", str(exc))
        except Exception as exc:
            return _error_response(502, "upstream_error", str(exc))

        photo_urls = sorted(listing.get("photo_urls") or [])
        if not photo_urls:
            return {"id": id, "count": 0, "previews": []}

        photo_ids_to_urls = {extract_id(url): url for url in photo_urls}

        ids = _as_list_param(ids)

        try:
            max_items = _as_optional_int(limit, "limit") or 5
            max_items = _ensure_boundries(max_items, 1, 50)

            max_size = _as_optional_int(preview_size, "preview_size") or 320
            max_size = _ensure_boundries(max_size, 64, 1024)

            quality = _as_optional_int(preview_quality, "preview_quality") or 65
            quality = _ensure_boundries(quality, 30, 90)
        except ValidationError as exc:
            return _error_response(
                400,
                "invalid_parameter",
                "Invalid numeric query parameter",
                {"field": exc.field, "reason": exc.message},
            )

        should_save = _as_bool_flag(save)
        pattern = _as_optional_str(filename_pattern, lowercase=False)

        output_base_dir = None
        if should_save:
            try:
                output_base_dir = _resolve_output_base_dir(dir)
            except ValueError as exc:
                return _error_response(
                    400,
                    "invalid_parameter",
                    "Invalid directory parameter",
                    {"field": "dir", "reason": str(exc)},
                )

        if ids:
            urls_to_download = [
                photo_ids_to_urls[photo_id]
                for photo_id in ids
                if photo_id in photo_ids_to_urls
            ]
        else:
            urls_to_download = photo_urls

        urls_to_download = urls_to_download[:max_items]
        previews = []

        for index, url in enumerate(urls_to_download, start=1):
            photo_id = extract_id(url)
            try:
                request = urllib.request.Request(
                    url, headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(request, timeout=funda_timeout) as response:
                    content = response.read()
                content_type, encoded = _build_preview_base64(
                    content, max_size=max_size, quality=quality
                )
                previews.append(
                    {
                        "id": photo_id,
                        "url": url,
                        "content_type": content_type,
                    }
                )

                if not should_save:
                    previews[-1]["base64"] = encoded

                if should_save and output_base_dir is not None:
                    safe_photo_id = photo_id.replace("/", "-")
                    if pattern:
                        try:
                            filename = pattern.format(
                                id=id, index=index, photo_id=safe_photo_id
                            )
                        except KeyError as exc:
                            return _error_response(
                                400,
                                "invalid_parameter",
                                "Invalid filename pattern",
                                {
                                    "field": "filename_pattern",
                                    "reason": f"unknown placeholder '{exc.args[0]}'",
                                },
                            )
                        filename = Path(filename).name
                    else:
                        filename = f"{safe_photo_id}.jpg"
                    if not filename.lower().endswith(".jpg"):
                        filename = f"{filename}.jpg"

                    if pattern:
                        target_dir = output_base_dir
                    else:
                        target_dir = output_base_dir / str(id)
                    target_dir.mkdir(parents=True, exist_ok=True)

                    output_path = target_dir / filename
                    output_path.write_bytes(base64.b64decode(encoded))
                    previews[-1]["saved_path"] = str(output_path.resolve())
                    previews[-1]["relative_path"] = str(
                        output_path.resolve().relative_to(SKILL_ROOT.resolve())
                    )
            except urllib.error.URLError as exc:
                previews.append(
                    {
                        "id": photo_id,
                        "url": url,
                        "error": str(exc),
                    }
                )

        return {"id": id, "count": len(previews), "previews": previews}

    @route("/search_listings", method=["GET", "POST"])
    def search_listings(
        location=Parameter("location", default="Amsterdam"),  # City or area name
        offering_type=Parameter("offering_type", default=""),  # "buy" or "rent"
        availability=Parameter(
            "availability", default=""
        ),  # available/negotiations/sold
        radius_km=Parameter("radius_km", default=""),  # Search radius in kilometers
        price_min=Parameter("price_min", default=""),  # Minimum price
        price_max=Parameter("price_max", default=""),  # Maximum price
        area_min=Parameter("area_min", default=""),  # Minimum living area (m²)
        area_max=Parameter("area_max", default=""),  # Maximum living area (m²)
        plot_min=Parameter("plot_min", default=""),  # Minimum plot area (m²)
        plot_max=Parameter("plot_max", default=""),  # Maximum plot area (m²)
        object_type=Parameter("object_type", default=""),  # Property types
        energy_label=Parameter("energy_label", default=""),  # Energy labels
        sort=Parameter("sort", default="newest"),  # Sort order
        page=Parameter("page", default=""),  # Backward-compatible single page alias
        pages=Parameter("pages", default="0"),  # Page numbers (15 results per page)
    ):
        location = _as_optional_str(location) or "amsterdam"
        object_type = _as_list_param(object_type) or None
        energy_label = _as_list_param(energy_label, lowercase=False)
        energy_label = [item.upper() for item in energy_label] or None
        availability = _as_list_param(availability) or None
        pages = _as_list_param(pages)
        if not pages:
            single_page = _as_optional_int(page)
            pages = [str(single_page)] if single_page is not None else ["0"]
        try:
            pages = [_as_optional_int(p, "pages") for p in pages]
            pages = [p for p in pages if p is not None]
        except ValidationError as exc:
            return _error_response(
                400,
                "invalid_parameter",
                "Invalid numeric query parameter",
                {"field": exc.field, "reason": exc.message},
            )
        if not pages:
            pages = [0]
        offering_type = _as_optional_str(offering_type) or "buy"
        sort = _as_optional_str(sort)

        response = {}

        for index, page in enumerate(pages):
            try:
                search_kwargs = {
                    "location": location,
                    "offering_type": offering_type,
                    "availability": availability,
                    "radius_km": _as_optional_int(radius_km, "radius_km"),
                    "price_min": _as_optional_int(price_min, "price_min"),
                    "price_max": _as_optional_int(price_max, "price_max"),
                    "area_min": _as_optional_int(area_min, "area_min"),
                    "area_max": _as_optional_int(area_max, "area_max"),
                    "plot_min": _as_optional_int(plot_min, "plot_min"),
                    "plot_max": _as_optional_int(plot_max, "plot_max"),
                    "object_type": object_type,
                    "energy_label": energy_label,
                    "sort": sort,
                    "page": page,
                }
            except ValidationError as exc:
                return _error_response(
                    400,
                    "invalid_parameter",
                    "Invalid numeric query parameter",
                    {"field": exc.field, "reason": exc.message},
                )
            print(f"[funda_gateway] search_listing kwargs: {search_kwargs}")
            try:
                results = f.search_listing(**search_kwargs)
            except Exception as exc:
                return _error_response(502, "upstream_error", str(exc))
            response.update(
                {
                    fetch_public_id(item["detail_url"]): item.to_dict()
                    for item in results
                }
            )
            if index < len(pages) - 1:
                time.sleep(MULTI_PAGE_REQUEST_DELAY_SECONDS)

        items = []
        for public_id, listing in response.items():
            item = dict(listing)
            item.setdefault("public_id", public_id)
            items.append(item)
        return {"count": len(items), "items": items}

    server.start(host="127.0.0.1", port=server_port)


if __name__ == "__main__":
    args = parse_args()
    spin_up_server(args.port, args.timeout)
