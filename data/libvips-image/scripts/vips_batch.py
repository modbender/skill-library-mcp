#!/usr/bin/env python3
"""
Batch image processing with libvips.

Usage:
    python vips_batch.py <command> <input_dir> <output_dir> [options]
    python vips_batch.py --config batch_config.json

Examples:
    python vips_batch.py resize ./input ./output --width 800
    python vips_batch.py convert ./input ./output --format webp --quality 85
    python vips_batch.py thumbnail ./input ./thumbnails --size 200
"""

import argparse
import json
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

try:
    import pyvips
except ImportError:
    print("Error: pyvips not installed. Run: pip install pyvips")
    sys.exit(1)


def get_files(input_dir: Path, pattern: str, recursive: bool = False) -> List[Path]:
    """Get list of files matching pattern."""
    if recursive:
        return list(input_dir.rglob(pattern))
    return list(input_dir.glob(pattern))


def process_resize(input_path: Path, output_path: Path, width: int = None,
                   height: int = None, mode: str = "fit", quality: int = 85) -> bool:
    """Resize a single image."""
    try:
        image = pyvips.Image.new_from_file(str(input_path), access="sequential")

        orig_width = image.width
        orig_height = image.height

        if width and height:
            if mode == "force":
                h_scale = width / orig_width
                v_scale = height / orig_height
                image = image.resize(h_scale, vscale=v_scale)
            elif mode == "cover":
                h_scale = width / orig_width
                v_scale = height / orig_height
                scale = max(h_scale, v_scale)
                image = image.resize(scale)
                if image.width > width or image.height > height:
                    left = (image.width - width) // 2
                    top = (image.height - height) // 2
                    image = image.crop(left, top, width, height)
            else:  # fit
                h_scale = width / orig_width
                v_scale = height / orig_height
                scale = min(h_scale, v_scale)
                image = image.resize(scale)
        elif width:
            scale = width / orig_width
            image = image.resize(scale)
        elif height:
            scale = height / orig_height
            image = image.resize(scale)

        save_image(image, output_path, quality)
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


def process_thumbnail(input_path: Path, output_path: Path, size: int = 200,
                      crop: str = "none", quality: int = 85) -> bool:
    """Create thumbnail of a single image."""
    try:
        crop_map = {
            "none": pyvips.Interesting.NONE,
            "centre": pyvips.Interesting.CENTRE,
            "center": pyvips.Interesting.CENTRE,
            "entropy": pyvips.Interesting.ENTROPY,
            "attention": pyvips.Interesting.ATTENTION,
        }

        interesting = crop_map.get(crop, pyvips.Interesting.NONE)
        image = pyvips.Image.thumbnail(str(input_path), size, height=size, crop=interesting)

        save_image(image, output_path, quality)
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


def process_convert(input_path: Path, output_path: Path, quality: int = 85) -> bool:
    """Convert a single image."""
    try:
        image = pyvips.Image.new_from_file(str(input_path), access="sequential")
        save_image(image, output_path, quality)
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


def process_watermark(input_path: Path, output_path: Path, text: str = None,
                      watermark_image: str = None, position: str = "bottom-right",
                      opacity: float = 0.5, font: str = "sans 24", quality: int = 85) -> bool:
    """Add watermark to a single image."""
    try:
        image = pyvips.Image.new_from_file(str(input_path), access="sequential")

        if text:
            overlay = pyvips.Image.text(text, font=font, rgba=True)
            if opacity < 1.0 and overlay.bands == 4:
                rgb = overlay.extract_band(0, n=3)
                alpha = overlay.extract_band(3) * opacity
                overlay = rgb.bandjoin(alpha)
        elif watermark_image:
            overlay = pyvips.Image.new_from_file(watermark_image, access="sequential")
            if opacity < 1.0:
                if overlay.bands == 4:
                    rgb = overlay.extract_band(0, n=3)
                    alpha = overlay.extract_band(3) * opacity
                    overlay = rgb.bandjoin(alpha)
                else:
                    alpha = pyvips.Image.new_from_image(overlay, opacity * 255)
                    overlay = overlay.bandjoin(alpha)
        else:
            return False

        # Calculate position
        margin = 20
        positions = {
            "top-left": (margin, margin),
            "top-right": (image.width - overlay.width - margin, margin),
            "bottom-left": (margin, image.height - overlay.height - margin),
            "bottom-right": (image.width - overlay.width - margin, image.height - overlay.height - margin),
            "center": ((image.width - overlay.width) // 2, (image.height - overlay.height) // 2),
        }

        x, y = positions.get(position, positions["bottom-right"])
        x = max(0, x)
        y = max(0, y)

        if image.bands == 3:
            image = image.bandjoin(255)

        result = image.composite2(overlay, pyvips.BlendMode.OVER, x=int(x), y=int(y))

        # Remove alpha if JPEG
        if str(output_path).lower().endswith(('.jpg', '.jpeg')):
            result = result.flatten(background=[255, 255, 255])

        save_image(result, output_path, quality)
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


def process_pipeline(input_path: Path, output_path: Path, operations: list,
                     quality: int = 85) -> bool:
    """Process image through a pipeline of operations."""
    try:
        image = pyvips.Image.new_from_file(str(input_path), access="sequential")

        for op in operations:
            op_type = op.get("type")

            if op_type == "resize":
                width = op.get("width")
                height = op.get("height")
                mode = op.get("mode", "fit")

                orig_width = image.width
                orig_height = image.height

                if width and height:
                    if mode == "force":
                        h_scale = width / orig_width
                        v_scale = height / orig_height
                        image = image.resize(h_scale, vscale=v_scale)
                    elif mode == "cover":
                        h_scale = width / orig_width
                        v_scale = height / orig_height
                        scale = max(h_scale, v_scale)
                        image = image.resize(scale)
                        if image.width > width or image.height > height:
                            left = (image.width - width) // 2
                            top = (image.height - height) // 2
                            image = image.crop(left, top, width, height)
                    else:
                        h_scale = width / orig_width
                        v_scale = height / orig_height
                        scale = min(h_scale, v_scale)
                        image = image.resize(scale)
                elif width:
                    scale = width / orig_width
                    image = image.resize(scale)
                elif height:
                    scale = height / orig_height
                    image = image.resize(scale)

            elif op_type == "sharpen":
                sigma = op.get("sigma", 0.5)
                image = image.sharpen(sigma=sigma)

            elif op_type == "blur":
                sigma = op.get("sigma", 3.0)
                image = image.gaussblur(sigma)

            elif op_type == "grayscale":
                image = image.colourspace(pyvips.Interpretation.B_W)

            elif op_type == "rotate":
                angle = op.get("angle", 0)
                if angle == 90:
                    image = image.rot90()
                elif angle == 180:
                    image = image.rot180()
                elif angle == 270:
                    image = image.rot270()
                elif angle:
                    bg = op.get("background", [255, 255, 255])
                    image = image.rotate(angle, background=bg)

            elif op_type == "flip":
                if op.get("horizontal"):
                    image = image.fliphor()
                if op.get("vertical"):
                    image = image.flipver()

            elif op_type == "adjust":
                brightness = op.get("brightness", 1.0)
                contrast = op.get("contrast", 1.0)

                if brightness != 1.0:
                    image = image * brightness
                if contrast != 1.0:
                    image = (image - 128) * contrast + 128

                image = image.cast(pyvips.BandFormat.UCHAR)

        save_image(image, output_path, quality)
        return True
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


def save_image(image, output_path: Path, quality: int = 85):
    """Save image with appropriate options."""
    output_str = str(output_path).lower()
    kwargs = {}

    if output_str.endswith(('.jpg', '.jpeg')):
        kwargs['Q'] = quality
        kwargs['optimize_coding'] = True
    elif output_str.endswith('.png'):
        kwargs['compression'] = 6
    elif output_str.endswith('.webp'):
        kwargs['Q'] = quality
    elif output_str.endswith('.avif'):
        kwargs['Q'] = quality

    image.write_to_file(str(output_path), **kwargs)


def batch_process(args, process_func, **kwargs):
    """Generic batch processing function."""
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Get files to process
    files = get_files(input_dir, args.pattern, args.recursive)

    if not files:
        print(f"No files found matching pattern: {args.pattern}")
        return

    print(f"Found {len(files)} files to process")

    # Determine output format
    output_format = getattr(args, 'format', None)

    success_count = 0
    error_count = 0

    def process_file(input_path: Path):
        # Determine output path
        if args.recursive:
            rel_path = input_path.relative_to(input_dir)
            output_subdir = output_dir / rel_path.parent
            output_subdir.mkdir(parents=True, exist_ok=True)
        else:
            output_subdir = output_dir

        if output_format:
            output_name = input_path.stem + f".{output_format}"
        else:
            output_name = input_path.name

        output_path = output_subdir / output_name

        return process_func(input_path, output_path, **kwargs)

    # Process files in parallel
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_file, f): f for f in files}

        for future in as_completed(futures):
            input_file = futures[future]
            try:
                if future.result():
                    success_count += 1
                    print(f"Processed: {input_file.name}")
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error: {input_file.name}: {e}")

    print(f"\nCompleted: {success_count} succeeded, {error_count} failed")


def run_config(config_path: str):
    """Run batch processing from config file."""
    with open(config_path) as f:
        config = json.load(f)

    input_dir = Path(config["input_dir"])
    output_dir = Path(config["output_dir"])
    operations = config.get("operations", [])
    pattern = config.get("pattern", "*.*")
    recursive = config.get("recursive", False)
    workers = config.get("workers", 4)
    quality = config.get("quality", 85)

    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    files = get_files(input_dir, pattern, recursive)

    if not files:
        print(f"No files found matching pattern: {pattern}")
        return

    print(f"Found {len(files)} files to process")

    # Get output format from last convert operation if exists
    output_format = None
    for op in operations:
        if op.get("type") == "convert":
            output_format = op.get("format")

    success_count = 0
    error_count = 0

    def process_file(input_path: Path):
        if recursive:
            rel_path = input_path.relative_to(input_dir)
            output_subdir = output_dir / rel_path.parent
            output_subdir.mkdir(parents=True, exist_ok=True)
        else:
            output_subdir = output_dir

        if output_format:
            output_name = input_path.stem + f".{output_format}"
        else:
            output_name = input_path.name

        output_path = output_subdir / output_name

        return process_pipeline(input_path, output_path, operations, quality)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_file, f): f for f in files}

        for future in as_completed(futures):
            input_file = futures[future]
            try:
                if future.result():
                    success_count += 1
                    print(f"Processed: {input_file.name}")
                else:
                    error_count += 1
            except Exception as e:
                error_count += 1
                print(f"Error: {input_file.name}: {e}")

    print(f"\nCompleted: {success_count} succeeded, {error_count} failed")


def main():
    parser = argparse.ArgumentParser(
        description="Batch image processing with libvips",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--config", help="Config file for batch processing")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Common arguments
    def add_common_args(p):
        p.add_argument("input_dir", help="Input directory")
        p.add_argument("output_dir", help="Output directory")
        p.add_argument("--pattern", "-p", default="*.{jpg,jpeg,png,webp,gif,tiff}",
                       help="File pattern to match")
        p.add_argument("--recursive", "-r", action="store_true", help="Process subdirectories")
        p.add_argument("--workers", "-w", type=int, default=4, help="Number of worker threads")
        p.add_argument("--quality", "-q", type=int, default=85, help="Output quality (1-100)")
        p.add_argument("--format", "-f", help="Output format (jpg, png, webp, avif)")

    # Resize
    p_resize = subparsers.add_parser("resize", help="Batch resize images")
    add_common_args(p_resize)
    p_resize.add_argument("--width", type=int, help="Target width")
    p_resize.add_argument("--height", type=int, help="Target height")
    p_resize.add_argument("--mode", "-m", choices=["fit", "cover", "force"], default="fit")

    # Thumbnail
    p_thumb = subparsers.add_parser("thumbnail", help="Batch create thumbnails")
    add_common_args(p_thumb)
    p_thumb.add_argument("--size", "-s", type=int, default=200, help="Thumbnail size")
    p_thumb.add_argument("--crop", choices=["none", "centre", "center", "entropy", "attention"],
                         default="none")

    # Convert
    p_convert = subparsers.add_parser("convert", help="Batch convert format")
    add_common_args(p_convert)

    # Watermark
    p_watermark = subparsers.add_parser("watermark", help="Batch add watermark")
    add_common_args(p_watermark)
    p_watermark.add_argument("--text", help="Watermark text")
    p_watermark.add_argument("--image", help="Watermark image")
    p_watermark.add_argument("--position", choices=["top-left", "top-right", "bottom-left",
                                                     "bottom-right", "center"],
                             default="bottom-right")
    p_watermark.add_argument("--opacity", "-o", type=float, default=0.5)
    p_watermark.add_argument("--font", default="sans 24")

    args = parser.parse_args()

    if args.config:
        run_config(args.config)
        return

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == "resize":
        batch_process(args, process_resize,
                      width=args.width, height=args.height,
                      mode=args.mode, quality=args.quality)
    elif args.command == "thumbnail":
        batch_process(args, process_thumbnail,
                      size=args.size, crop=args.crop, quality=args.quality)
    elif args.command == "convert":
        batch_process(args, process_convert, quality=args.quality)
    elif args.command == "watermark":
        batch_process(args, process_watermark,
                      text=args.text, watermark_image=args.image,
                      position=args.position, opacity=args.opacity,
                      font=args.font, quality=args.quality)


if __name__ == "__main__":
    main()
