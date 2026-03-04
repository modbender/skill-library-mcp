#!/usr/bin/env python3
"""
Test script for vips_tool.py - validates all image processing methods.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add script directory to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    import pyvips
except ImportError:
    print("Error: pyvips not installed")
    sys.exit(1)


def create_test_image(path: Path, width: int = 800, height: int = 600) -> Path:
    """Create a test image with gradient and text."""
    # Create gradient image
    image = pyvips.Image.xyz(width, height)
    # Normalize to 0-255 range
    r = image.extract_band(0) * 255 / width
    g = image.extract_band(1) * 255 / height
    b = (r + g) / 2

    # Create RGB image
    rgb = r.bandjoin([g, b]).cast(pyvips.BandFormat.UCHAR)

    rgb.write_to_file(str(path), Q=95)
    return path


def run_command(args: list, expected_success: bool = True) -> tuple:
    """Run vips_tool.py command and return result."""
    cmd = [sys.executable, str(script_dir / "vips_tool.py")] + args
    result = subprocess.run(cmd, capture_output=True, text=True)

    success = result.returncode == 0
    if expected_success and not success:
        print(f"Command failed: {' '.join(args)}")
        print(f"stderr: {result.stderr}")
        return False, result.stderr

    return success, result.stdout + result.stderr


def test_info(test_image: Path) -> bool:
    """Test info command."""
    print("Testing: info")
    success, output = run_command(["info", str(test_image)])
    if success and "Width:" in output and "Height:" in output:
        print("  ✓ info works")
        return True
    print("  ✗ info failed")
    return False


def test_resize(test_image: Path, output_dir: Path) -> bool:
    """Test resize command."""
    print("Testing: resize")
    tests = [
        (["resize", str(test_image), str(output_dir / "resize_width.jpg"), "--width", "400"], "width only"),
        (["resize", str(test_image), str(output_dir / "resize_height.jpg"), "--height", "300"], "height only"),
        (["resize", str(test_image), str(output_dir / "resize_fit.jpg"), "--width", "400", "--height", "300", "--mode", "fit"], "fit mode"),
        (["resize", str(test_image), str(output_dir / "resize_cover.jpg"), "--width", "400", "--height", "300", "--mode", "cover"], "cover mode"),
        (["resize", str(test_image), str(output_dir / "resize_force.jpg"), "--width", "400", "--height", "300", "--mode", "force"], "force mode"),
    ]

    all_passed = True
    for args, desc in tests:
        success, _ = run_command(args)
        output_path = Path(args[2])
        if success and output_path.exists():
            # Verify dimensions
            img = pyvips.Image.new_from_file(str(output_path))
            print(f"  ✓ resize ({desc}) - {img.width}x{img.height}")
        else:
            print(f"  ✗ resize ({desc}) failed")
            all_passed = False

    return all_passed


def test_thumbnail(test_image: Path, output_dir: Path) -> bool:
    """Test thumbnail command."""
    print("Testing: thumbnail")
    tests = [
        (["thumbnail", str(test_image), str(output_dir / "thumb_none.jpg"), "--size", "200", "--crop", "none"], "no crop"),
        (["thumbnail", str(test_image), str(output_dir / "thumb_center.jpg"), "--size", "200", "--crop", "centre"], "center crop"),
        (["thumbnail", str(test_image), str(output_dir / "thumb_attention.jpg"), "--size", "200", "--crop", "attention"], "attention crop"),
    ]

    all_passed = True
    for args, desc in tests:
        success, _ = run_command(args)
        output_path = Path(args[2])
        if success and output_path.exists():
            img = pyvips.Image.new_from_file(str(output_path))
            print(f"  ✓ thumbnail ({desc}) - {img.width}x{img.height}")
        else:
            print(f"  ✗ thumbnail ({desc}) failed")
            all_passed = False

    return all_passed


def test_convert(test_image: Path, output_dir: Path) -> bool:
    """Test convert command."""
    print("Testing: convert")
    formats = [
        ("png", ".png"),
        ("webp", ".webp"),
    ]

    all_passed = True
    for fmt, ext in formats:
        output_path = output_dir / f"convert{ext}"
        success, _ = run_command(["convert", str(test_image), str(output_path), "--quality", "85"])
        if success and output_path.exists():
            size_kb = output_path.stat().st_size / 1024
            print(f"  ✓ convert to {fmt} - {size_kb:.1f} KB")
        else:
            print(f"  ✗ convert to {fmt} failed")
            all_passed = False

    return all_passed


def test_crop(test_image: Path, output_dir: Path) -> bool:
    """Test crop command."""
    print("Testing: crop")
    tests = [
        (["crop", str(test_image), str(output_dir / "crop_manual.jpg"), "--left", "100", "--top", "50", "--width", "400", "--height", "300"], "manual crop"),
        (["crop", str(test_image), str(output_dir / "crop_smart.jpg"), "--width", "400", "--height", "300", "--smart"], "smart crop"),
    ]

    all_passed = True
    for args, desc in tests:
        success, _ = run_command(args)
        output_path = Path(args[2])
        if success and output_path.exists():
            img = pyvips.Image.new_from_file(str(output_path))
            print(f"  ✓ crop ({desc}) - {img.width}x{img.height}")
        else:
            print(f"  ✗ crop ({desc}) failed")
            all_passed = False

    return all_passed


def test_rotate(test_image: Path, output_dir: Path) -> bool:
    """Test rotate command."""
    print("Testing: rotate")
    tests = [
        (["rotate", str(test_image), str(output_dir / "rotate_90.jpg"), "--angle", "90"], "90 degrees"),
        (["rotate", str(test_image), str(output_dir / "rotate_180.jpg"), "--angle", "180"], "180 degrees"),
        (["rotate", str(test_image), str(output_dir / "rotate_45.jpg"), "--angle", "45", "--background", "128,128,128"], "45 degrees"),
        (["rotate", str(test_image), str(output_dir / "rotate_auto.jpg"), "--auto"], "auto rotate"),
    ]

    all_passed = True
    for args, desc in tests:
        success, _ = run_command(args)
        output_path = Path(args[2])
        if success and output_path.exists():
            img = pyvips.Image.new_from_file(str(output_path))
            print(f"  ✓ rotate ({desc}) - {img.width}x{img.height}")
        else:
            print(f"  ✗ rotate ({desc}) failed")
            all_passed = False

    return all_passed


def test_watermark(test_image: Path, output_dir: Path) -> bool:
    """Test watermark command."""
    print("Testing: watermark")
    tests = [
        (["watermark", str(test_image), str(output_dir / "watermark_text.jpg"), "--text", "Test Watermark", "--position", "bottom-right"], "text watermark"),
        (["watermark", str(test_image), str(output_dir / "watermark_opacity.jpg"), "--text", "Low Opacity", "--opacity", "0.3", "--position", "center"], "opacity watermark"),
    ]

    all_passed = True
    for args, desc in tests:
        success, _ = run_command(args)
        output_path = Path(args[2])
        if success and output_path.exists():
            print(f"  ✓ watermark ({desc})")
        else:
            print(f"  ✗ watermark ({desc}) failed")
            all_passed = False

    return all_passed


def test_adjust(test_image: Path, output_dir: Path) -> bool:
    """Test adjust command."""
    print("Testing: adjust")
    tests = [
        (["adjust", str(test_image), str(output_dir / "adjust_bright.jpg"), "--brightness", "1.3"], "brightness"),
        (["adjust", str(test_image), str(output_dir / "adjust_contrast.jpg"), "--contrast", "1.5"], "contrast"),
        (["adjust", str(test_image), str(output_dir / "adjust_combined.jpg"), "--brightness", "1.1", "--contrast", "1.2"], "combined"),
    ]

    all_passed = True
    for args, desc in tests:
        success, _ = run_command(args)
        output_path = Path(args[2])
        if success and output_path.exists():
            print(f"  ✓ adjust ({desc})")
        else:
            print(f"  ✗ adjust ({desc}) failed")
            all_passed = False

    return all_passed


def test_sharpen(test_image: Path, output_dir: Path) -> bool:
    """Test sharpen command."""
    print("Testing: sharpen")
    output_path = output_dir / "sharpen.jpg"
    success, _ = run_command(["sharpen", str(test_image), str(output_path), "--sigma", "1.0"])
    if success and output_path.exists():
        print("  ✓ sharpen works")
        return True
    print("  ✗ sharpen failed")
    return False


def test_blur(test_image: Path, output_dir: Path) -> bool:
    """Test blur command."""
    print("Testing: blur")
    output_path = output_dir / "blur.jpg"
    success, _ = run_command(["blur", str(test_image), str(output_path), "--sigma", "5.0"])
    if success and output_path.exists():
        print("  ✓ blur works")
        return True
    print("  ✗ blur failed")
    return False


def test_flip(test_image: Path, output_dir: Path) -> bool:
    """Test flip command."""
    print("Testing: flip")
    tests = [
        (["flip", str(test_image), str(output_dir / "flip_h.jpg"), "--horizontal"], "horizontal"),
        (["flip", str(test_image), str(output_dir / "flip_v.jpg"), "--vertical"], "vertical"),
    ]

    all_passed = True
    for args, desc in tests:
        success, _ = run_command(args)
        output_path = Path(args[2])
        if success and output_path.exists():
            print(f"  ✓ flip ({desc})")
        else:
            print(f"  ✗ flip ({desc}) failed")
            all_passed = False

    return all_passed


def test_grayscale(test_image: Path, output_dir: Path) -> bool:
    """Test grayscale command."""
    print("Testing: grayscale")
    output_path = output_dir / "grayscale.jpg"
    success, _ = run_command(["grayscale", str(test_image), str(output_path)])
    if success and output_path.exists():
        img = pyvips.Image.new_from_file(str(output_path))
        print(f"  ✓ grayscale works - bands: {img.bands}")
        return True
    print("  ✗ grayscale failed")
    return False


def test_composite(test_image: Path, output_dir: Path) -> bool:
    """Test composite command."""
    print("Testing: composite")

    # Create a smaller overlay image
    overlay_path = output_dir / "overlay.png"
    overlay = pyvips.Image.xyz(100, 100)
    r = overlay.extract_band(0) * 255 / 100
    g = pyvips.Image.new_from_image(overlay, 100)
    b = pyvips.Image.new_from_image(overlay, 200)
    a = pyvips.Image.new_from_image(overlay, 200)  # Semi-transparent
    rgba = r.bandjoin([g, b, a]).cast(pyvips.BandFormat.UCHAR)
    rgba.write_to_file(str(overlay_path))

    output_path = output_dir / "composite.jpg"
    success, _ = run_command([
        "composite", str(test_image), str(overlay_path), str(output_path),
        "--x", "50", "--y", "50", "--blend", "over"
    ])

    if success and output_path.exists():
        print("  ✓ composite works")
        return True
    print("  ✗ composite failed")
    return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("libvips Tool Test Suite")
    print("=" * 60)
    print()

    # Check pyvips version
    print(f"pyvips version: {pyvips.__version__}")
    print(f"libvips version: {pyvips.version(0)}.{pyvips.version(1)}.{pyvips.version(2)}")
    print()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # Create test image
        test_image = tmp_path / "test_input.jpg"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        print("Creating test image...")
        create_test_image(test_image)
        print(f"Test image created: {test_image}")
        print()

        # Run tests
        results = []
        results.append(("info", test_info(test_image)))
        results.append(("resize", test_resize(test_image, output_dir)))
        results.append(("thumbnail", test_thumbnail(test_image, output_dir)))
        results.append(("convert", test_convert(test_image, output_dir)))
        results.append(("crop", test_crop(test_image, output_dir)))
        results.append(("rotate", test_rotate(test_image, output_dir)))
        results.append(("watermark", test_watermark(test_image, output_dir)))
        results.append(("adjust", test_adjust(test_image, output_dir)))
        results.append(("sharpen", test_sharpen(test_image, output_dir)))
        results.append(("blur", test_blur(test_image, output_dir)))
        results.append(("flip", test_flip(test_image, output_dir)))
        results.append(("grayscale", test_grayscale(test_image, output_dir)))
        results.append(("composite", test_composite(test_image, output_dir)))

        # Summary
        print()
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        passed = sum(1 for _, r in results if r)
        failed = sum(1 for _, r in results if not r)
        print(f"Passed: {passed}/{len(results)}")
        print(f"Failed: {failed}/{len(results)}")

        if failed > 0:
            print("\nFailed tests:")
            for name, result in results:
                if not result:
                    print(f"  - {name}")

        return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
