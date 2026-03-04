"""Tests for core.image module."""

import base64
from pathlib import Path
from unittest.mock import patch

import pytest

from core.image import (
    ALLOWED_IMAGE_EXTENSIONS,
    convert_image_value,
    file_to_base64,
    is_local_image_file,
    process_image_params,
    validate_image_path,
)


@pytest.fixture()
def tmp_png(tmp_path: Path) -> Path:
    """Create a temporary PNG file."""
    p = tmp_path / "test.png"
    p.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
    return p


@pytest.fixture()
def tmp_jpg(tmp_path: Path) -> Path:
    """Create a temporary JPEG file."""
    p = tmp_path / "photo.jpg"
    p.write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 100)
    return p


class TestAllowedExtensions:
    """Tests for the ALLOWED_IMAGE_EXTENSIONS constant."""

    def test_common_formats_included(self) -> None:
        for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"):
            assert ext in ALLOWED_IMAGE_EXTENSIONS

    def test_dangerous_formats_excluded(self) -> None:
        for ext in (".txt", ".py", ".sh", ".pem", ".key", ".json", ".env", ".yml"):
            assert ext not in ALLOWED_IMAGE_EXTENSIONS


class TestValidateImagePath:
    """Tests for validate_image_path."""

    def test_valid_png_path(self, tmp_png: Path) -> None:
        result = validate_image_path(str(tmp_png))
        assert result == tmp_png.resolve()

    def test_valid_jpg_path(self, tmp_jpg: Path) -> None:
        result = validate_image_path(str(tmp_jpg))
        assert result == tmp_jpg.resolve()

    def test_all_allowed_extensions(self, tmp_path: Path) -> None:
        for ext in ALLOWED_IMAGE_EXTENSIONS:
            p = tmp_path / f"test{ext}"
            p.write_bytes(b"\x00" * 10)
            result = validate_image_path(str(p))
            assert result == p.resolve()

    def test_rejects_text_file(self, tmp_path: Path) -> None:
        p = tmp_path / "notes.txt"
        p.write_text("secret data")
        with pytest.raises(ValueError, match="not an allowed image format"):
            validate_image_path(str(p))

    def test_rejects_python_file(self, tmp_path: Path) -> None:
        p = tmp_path / "script.py"
        p.write_text("import os")
        with pytest.raises(ValueError, match="not an allowed image format"):
            validate_image_path(str(p))

    def test_rejects_env_file(self, tmp_path: Path) -> None:
        p = tmp_path / ".env"
        p.write_text("API_KEY=secret")
        with pytest.raises(ValueError, match="not an allowed image format"):
            validate_image_path(str(p))

    def test_rejects_pem_file(self, tmp_path: Path) -> None:
        p = tmp_path / "key.pem"
        p.write_text("-----BEGIN RSA PRIVATE KEY-----")
        with pytest.raises(ValueError, match="not an allowed image format"):
            validate_image_path(str(p))

    def test_rejects_no_extension(self, tmp_path: Path) -> None:
        p = tmp_path / "passwd"
        p.write_text("root:x:0:0")
        with pytest.raises(ValueError, match="not an allowed image format"):
            validate_image_path(str(p))

    def test_rejects_etc_passwd(self) -> None:
        with pytest.raises(ValueError):
            validate_image_path("/etc/passwd")

    def test_rejects_etc_shadow(self) -> None:
        with pytest.raises(ValueError):
            validate_image_path("/etc/shadow")

    def test_rejects_etc_with_image_ext(self, tmp_path: Path) -> None:
        """Even if /etc/something.png existed, it should be blocked."""
        with pytest.raises(ValueError, match="sensitive system directory"):
            validate_image_path("/etc/fake.png")

    def test_rejects_ssh_directory(self) -> None:
        home = Path.home()
        with pytest.raises(ValueError):
            validate_image_path(str(home / ".ssh" / "id_rsa"))

    def test_rejects_aws_credentials(self) -> None:
        home = Path.home()
        with pytest.raises(ValueError):
            validate_image_path(str(home / ".aws" / "credentials"))

    def test_rejects_gnupg_directory(self) -> None:
        home = Path.home()
        with pytest.raises(ValueError):
            validate_image_path(str(home / ".gnupg" / "secret.png"))

    def test_path_traversal_resolved(self, tmp_path: Path) -> None:
        """Path traversal attempts are resolved before checking."""
        traversal = str(tmp_path / ".." / ".." / "etc" / "passwd")
        with pytest.raises(ValueError):
            validate_image_path(traversal)

    def test_case_insensitive_extension(self, tmp_path: Path) -> None:
        p = tmp_path / "test.PNG"
        p.write_bytes(b"\x89PNG\r\n\x1a\n")
        result = validate_image_path(str(p))
        assert result == p.resolve()

    def test_case_insensitive_extension_jpg(self, tmp_path: Path) -> None:
        p = tmp_path / "test.JPG"
        p.write_bytes(b"\xff\xd8\xff\xe0")
        result = validate_image_path(str(p))
        assert result == p.resolve()


class TestIsLocalImageFile:
    """Tests for is_local_image_file."""

    def test_existing_png_file(self, tmp_png: Path) -> None:
        assert is_local_image_file(str(tmp_png)) is True

    def test_existing_jpg_file(self, tmp_jpg: Path) -> None:
        assert is_local_image_file(str(tmp_jpg)) is True

    def test_nonexistent_image_file(self, tmp_path: Path) -> None:
        assert is_local_image_file(str(tmp_path / "nonexistent.png")) is False

    def test_http_url(self) -> None:
        assert is_local_image_file("http://example.com/image.png") is False

    def test_https_url(self) -> None:
        assert is_local_image_file("https://example.com/image.png") is False

    def test_data_uri(self) -> None:
        assert is_local_image_file("data:image/png;base64,abc123") is False

    def test_non_string(self) -> None:
        assert is_local_image_file(123) is False  # type: ignore[arg-type]

    def test_non_image_file_rejected(self, tmp_path: Path) -> None:
        p = tmp_path / "secret.txt"
        p.write_text("sensitive data")
        assert is_local_image_file(str(p)) is False

    def test_env_file_rejected(self, tmp_path: Path) -> None:
        p = tmp_path / ".env"
        p.write_text("API_KEY=secret")
        assert is_local_image_file(str(p)) is False

    def test_sensitive_path_rejected(self) -> None:
        assert is_local_image_file("/etc/passwd") is False

    def test_ssh_key_rejected(self) -> None:
        home = Path.home()
        assert is_local_image_file(str(home / ".ssh" / "id_rsa")) is False


class TestFileToBase64:
    """Tests for file_to_base64."""

    def test_converts_png(self, tmp_png: Path) -> None:
        result = file_to_base64(str(tmp_png))
        assert result.startswith("data:image/png;base64,")
        # Verify the base64 content is valid
        b64_data = result.split(",", 1)[1]
        decoded = base64.b64decode(b64_data)
        assert decoded == tmp_png.read_bytes()

    def test_converts_jpg(self, tmp_jpg: Path) -> None:
        result = file_to_base64(str(tmp_jpg))
        assert result.startswith("data:image/jpeg;base64,")

    def test_rejects_non_image(self, tmp_path: Path) -> None:
        p = tmp_path / "secret.txt"
        p.write_text("sensitive data")
        with pytest.raises(ValueError, match="not an allowed image format"):
            file_to_base64(str(p))

    def test_rejects_sensitive_path(self) -> None:
        with pytest.raises(ValueError):
            file_to_base64("/etc/passwd")


class TestConvertImageValue:
    """Tests for convert_image_value."""

    def test_converts_local_image(self, tmp_png: Path) -> None:
        result = convert_image_value(str(tmp_png))
        assert result.startswith("data:image/png;base64,")

    def test_passes_through_url(self) -> None:
        url = "https://example.com/image.png"
        assert convert_image_value(url) == url

    def test_passes_through_data_uri(self) -> None:
        data_uri = "data:image/png;base64,abc123"
        assert convert_image_value(data_uri) == data_uri

    def test_passes_through_non_image_string(self) -> None:
        """Non-image local paths are passed through (not converted)."""
        assert convert_image_value("/nonexistent/path.txt") == "/nonexistent/path.txt"

    def test_handles_list(self, tmp_png: Path, tmp_jpg: Path) -> None:
        result = convert_image_value([str(tmp_png), "https://example.com/img.png"])
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].startswith("data:image/png;base64,")
        assert result[1] == "https://example.com/img.png"

    def test_passes_through_non_string(self) -> None:
        assert convert_image_value(42) == 42
        assert convert_image_value(None) is None


class TestProcessImageParams:
    """Tests for process_image_params end-to-end."""

    def test_converts_image_param(self, tmp_png: Path) -> None:
        body = {"prompt": "test", "image": str(tmp_png)}
        result = process_image_params(body)
        assert result["prompt"] == "test"
        assert result["image"].startswith("data:image/png;base64,")

    def test_leaves_non_image_params(self) -> None:
        body = {"prompt": "test", "width": 512}
        result = process_image_params(body)
        assert result == body

    def test_original_body_unchanged(self, tmp_png: Path) -> None:
        body = {"prompt": "test", "image": str(tmp_png)}
        original_image = body["image"]
        process_image_params(body)
        assert body["image"] == original_image

    def test_handles_url_image(self) -> None:
        body = {"image": "https://example.com/photo.png"}
        result = process_image_params(body)
        assert result["image"] == "https://example.com/photo.png"

    def test_handles_list_images(self, tmp_png: Path) -> None:
        body = {"images": [str(tmp_png), "https://example.com/img.png"]}
        result = process_image_params(body)
        assert len(result["images"]) == 2
        assert result["images"][0].startswith("data:image/png;base64,")
        assert result["images"][1] == "https://example.com/img.png"

    def test_rejects_sensitive_file_via_is_local(self, tmp_path: Path) -> None:
        """Non-image files passed as image params are passed through unchanged."""
        p = tmp_path / "secret.txt"
        p.write_text("sensitive")
        body = {"image": str(p)}
        result = process_image_params(body)
        # Should be unchanged since it's not a valid image file
        assert result["image"] == str(p)
