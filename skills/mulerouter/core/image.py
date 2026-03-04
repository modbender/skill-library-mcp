"""Image utilities for handling local file paths and base64 conversion."""

import base64
import mimetypes
from pathlib import Path
from typing import Any

# Parameter names that accept image input (local path, URL, or base64)
IMAGE_PARAM_NAMES = {
    "image",
    "images",
    "first_frame",
    "last_frame",
    "first_frame_url",
    "last_frame_url",
    "ref_images_url",
    "reference_images",
}

# Hint to add to image parameter descriptions
IMAGE_PARAM_HINT = " **Prefer local file path** (e.g., /tmp/img.png) - auto-converted to base64."

# Allowed image/video file extensions for local file reading
ALLOWED_IMAGE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp",
    ".tiff", ".tif", ".svg", ".ico", ".heic", ".heif", ".avif",
}

# Sensitive directory names that should never be read from (relative to home directory)
_SENSITIVE_HOME_DIRS = {
    ".ssh", ".gnupg", ".gpg", ".aws", ".azure", ".gcloud",
    ".config", ".kube", ".docker", ".npm", ".pypirc",
}

# Sensitive system directories that should never be read from.
# These are resolved at runtime to handle platform-specific symlink layouts
# (e.g., /etc -> /private/etc on macOS).
_SENSITIVE_SYSTEM_DIRS = (
    Path("/etc"),
    Path("/proc"),
    Path("/sys"),
    Path("/dev"),
)


def is_image_param(name: str) -> bool:
    """Check if a parameter name is an image parameter."""
    return name in IMAGE_PARAM_NAMES


def enhance_image_param_description(name: str, description: str) -> str:
    """Enhance image parameter description with local file path hint.

    Args:
        name: Parameter name
        description: Original description

    Returns:
        Enhanced description if it's an image param, otherwise original
    """
    if is_image_param(name):
        return description + IMAGE_PARAM_HINT
    return description


def validate_image_path(file_path: str) -> Path:
    """Validate that a file path points to a safe, allowed image file.

    Checks:
    - File extension is in the allowed image extensions list
    - Resolved path does not point to sensitive system directories
    - Resolved path does not point to dotfiles/dotdirs in the user's home directory
    - File is not a .env file

    Args:
        file_path: Path to validate

    Returns:
        Resolved Path object if validation passes

    Raises:
        ValueError: If the path fails any validation check
    """
    path = Path(file_path).resolve()

    # Check file extension
    suffix = path.suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))
        raise ValueError(
            f"File '{file_path}' has extension '{suffix}' which is not an allowed "
            f"image format. Allowed extensions: {allowed}"
        )

    # Block .env files explicitly (even if somehow given an image extension)
    if path.name == ".env" or ".env" in {p.name for p in path.parents}:
        raise ValueError(f"Access denied: '{file_path}' is in or is a .env path")

    # Block sensitive system directories
    for sensitive_dir in _SENSITIVE_SYSTEM_DIRS:
        resolved_sensitive_dir = sensitive_dir.resolve()
        if path == resolved_sensitive_dir or resolved_sensitive_dir in path.parents:
            raise ValueError(
                f"Access denied: '{file_path}' is in a sensitive system directory"
            )

    # Block sensitive home directory dotfiles/dotdirs
    home = Path.home().resolve()
    if path == home or str(path).startswith(str(home)):
        # Check each component after the home directory
        try:
            relative = path.relative_to(home)
            parts = relative.parts
            if parts:
                first_component = parts[0]
                if first_component.startswith(".") and first_component in _SENSITIVE_HOME_DIRS:
                    raise ValueError(
                        f"Access denied: '{file_path}' is in a sensitive home directory"
                    )
        except ValueError as e:
            if "Access denied" in str(e):
                raise
            # relative_to failed, path is not under home — that's fine

    return path


def is_local_image_file(value: str) -> bool:
    """Check if a string value is a local image file path.

    Validates that the path exists, is a file, and has an allowed image extension.
    Also rejects paths to sensitive directories.
    """
    if not isinstance(value, str):
        return False
    if value.startswith(("http://", "https://", "data:")):
        return False
    try:
        path = validate_image_path(value)
        return path.exists() and path.is_file()
    except ValueError:
        return False


def file_to_base64(file_path: str) -> str:
    """Convert a local image file to base64 data URI.

    Args:
        file_path: Path to the local image file

    Returns:
        Base64 data URI string (e.g., "data:image/png;base64,...")

    Raises:
        ValueError: If the file is not an allowed image format
    """
    path = validate_image_path(file_path)
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        mime_type = "image/png"

    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{data}"


def convert_image_value(value: Any) -> Any:
    """Convert image parameter value, handling local file paths.

    Args:
        value: Parameter value (string or list of strings)

    Returns:
        Converted value with local files as base64 data URIs
    """
    if isinstance(value, str):
        if is_local_image_file(value):
            return file_to_base64(value)
        return value
    elif isinstance(value, list):
        return [convert_image_value(v) for v in value]
    return value


def process_image_params(body: dict[str, Any]) -> dict[str, Any]:
    """Process request body, converting local file paths to base64.

    Args:
        body: Request body dictionary

    Returns:
        Processed body with image params converted
    """
    result = body.copy()
    for key in IMAGE_PARAM_NAMES:
        if key in result:
            result[key] = convert_image_value(result[key])
    return result
