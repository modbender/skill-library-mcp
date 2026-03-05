#!/usr/bin/env python3
"""
libvips image processing tool.

Usage:
    python vips_tool.py <command> <input> <output> [options]

Commands:
    resize, thumbnail, convert, crop, rotate, watermark,
    composite, adjust, sharpen, blur, flip, grayscale, info
"""

import argparse
import sys
from pathlib import Path

try:
    import pyvips
except ImportError:
    print("Error: pyvips not installed. Run: pip install pyvips")
    print("Also ensure libvips is installed:")
    print("  macOS: brew install vips")
    print("  Ubuntu: sudo apt-get install libvips-dev")
    sys.exit(1)


def resize(args):
    """Resize image to specified dimensions."""
    image = pyvips.Image.new_from_file(args.input, access="sequential")

    orig_width = image.width
    orig_height = image.height

    if args.width and args.height:
        if args.mode == "force":
            # Force exact dimensions (may distort)
            h_scale = args.width / orig_width
            v_scale = args.height / orig_height
            image = image.resize(h_scale, vscale=v_scale)
        elif args.mode == "cover":
            # Cover: scale to fill, then crop
            h_scale = args.width / orig_width
            v_scale = args.height / orig_height
            scale = max(h_scale, v_scale)
            image = image.resize(scale)
            # Crop to exact size
            if image.width > args.width or image.height > args.height:
                left = (image.width - args.width) // 2
                top = (image.height - args.height) // 2
                image = image.crop(left, top, args.width, args.height)
        else:  # fit (default)
            # Fit within bounds
            h_scale = args.width / orig_width
            v_scale = args.height / orig_height
            scale = min(h_scale, v_scale)
            image = image.resize(scale)
    elif args.width:
        scale = args.width / orig_width
        image = image.resize(scale)
    elif args.height:
        scale = args.height / orig_height
        image = image.resize(scale)
    else:
        print("Error: Specify --width and/or --height")
        sys.exit(1)

    save_image(image, args.output, args)
    print(f"Resized: {args.input} -> {args.output} ({image.width}x{image.height})")


def thumbnail(args):
    """Create optimized thumbnail."""
    # Map crop strategy names
    crop_map = {
        "none": pyvips.Interesting.NONE,
        "centre": pyvips.Interesting.CENTRE,
        "center": pyvips.Interesting.CENTRE,
        "entropy": pyvips.Interesting.ENTROPY,
        "attention": pyvips.Interesting.ATTENTION,
    }

    interesting = crop_map.get(args.crop, pyvips.Interesting.NONE)

    image = pyvips.Image.thumbnail(
        args.input,
        args.size,
        height=args.size,
        crop=interesting
    )

    save_image(image, args.output, args)
    print(f"Thumbnail: {args.input} -> {args.output} ({image.width}x{image.height})")


def convert(args):
    """Convert image format."""
    image = pyvips.Image.new_from_file(args.input, access="sequential")
    save_image(image, args.output, args)
    print(f"Converted: {args.input} -> {args.output}")


def crop(args):
    """Crop a region from image."""
    if args.smart and args.width and args.height:
        # Smart crop needs random access
        image = pyvips.Image.new_from_file(args.input)
        image = image.smartcrop(args.width, args.height, interesting=pyvips.Interesting.ATTENTION)
    else:
        image = pyvips.Image.new_from_file(args.input, access="sequential")
        left = args.left or 0
        top = args.top or 0
        width = args.width or (image.width - left)
        height = args.height or (image.height - top)
        image = image.crop(left, top, width, height)

    save_image(image, args.output, args)
    print(f"Cropped: {args.input} -> {args.output} ({image.width}x{image.height})")


def rotate(args):
    """Rotate image."""
    image = pyvips.Image.new_from_file(args.input, access="sequential")

    if args.auto:
        # Auto-rotate based on EXIF orientation
        image = image.autorot()
    elif args.angle:
        # Parse background color
        bg = [255, 255, 255]
        if args.background:
            bg = [int(x) for x in args.background.split(",")]

        # Handle common angles efficiently
        if args.angle == 90:
            image = image.rot90()
        elif args.angle == 180:
            image = image.rot180()
        elif args.angle == 270:
            image = image.rot270()
        else:
            # Arbitrary angle rotation
            image = image.rotate(args.angle, background=bg)

    save_image(image, args.output, args)
    print(f"Rotated: {args.input} -> {args.output}")


def watermark(args):
    """Add text or image watermark."""
    image = pyvips.Image.new_from_file(args.input, access="sequential")

    if args.text:
        # Create text image
        text = pyvips.Image.text(
            args.text,
            font=args.font or "sans 24",
            rgba=True
        )

        # Apply opacity
        if args.opacity < 1.0:
            # Split into RGB and alpha, modify alpha
            if text.bands == 4:
                rgb = text.extract_band(0, n=3)
                alpha = text.extract_band(3) * args.opacity
                text = rgb.bandjoin(alpha)

        overlay = text
    elif args.image:
        overlay = pyvips.Image.new_from_file(args.image, access="sequential")

        # Apply opacity
        if args.opacity < 1.0:
            if overlay.bands == 4:
                rgb = overlay.extract_band(0, n=3)
                alpha = overlay.extract_band(3) * args.opacity
                overlay = rgb.bandjoin(alpha)
            else:
                # Add alpha channel
                alpha = pyvips.Image.new_from_image(overlay, args.opacity * 255)
                overlay = overlay.bandjoin(alpha)
    else:
        print("Error: Specify --text or --image for watermark")
        sys.exit(1)

    # Calculate position
    margin = 20
    positions = {
        "top-left": (margin, margin),
        "top-right": (image.width - overlay.width - margin, margin),
        "bottom-left": (margin, image.height - overlay.height - margin),
        "bottom-right": (image.width - overlay.width - margin, image.height - overlay.height - margin),
        "center": ((image.width - overlay.width) // 2, (image.height - overlay.height) // 2),
    }

    x, y = positions.get(args.position, positions["bottom-right"])
    x = max(0, x)
    y = max(0, y)

    # Ensure image has alpha channel for compositing
    if image.bands == 3:
        image = image.bandjoin(255)

    # Composite
    result = image.composite2(overlay, pyvips.BlendMode.OVER, x=int(x), y=int(y))

    # Remove alpha if saving to JPEG
    if args.output.lower().endswith(('.jpg', '.jpeg')):
        result = result.flatten(background=[255, 255, 255])

    save_image(result, args.output, args)
    print(f"Watermarked: {args.input} -> {args.output}")


def composite(args):
    """Composite two images."""
    background = pyvips.Image.new_from_file(args.input, access="sequential")
    overlay = pyvips.Image.new_from_file(args.overlay, access="sequential")

    # Map blend mode names
    blend_map = {
        "over": pyvips.BlendMode.OVER,
        "multiply": pyvips.BlendMode.MULTIPLY,
        "screen": pyvips.BlendMode.SCREEN,
        "overlay": pyvips.BlendMode.OVERLAY,
        "darken": pyvips.BlendMode.DARKEN,
        "lighten": pyvips.BlendMode.LIGHTEN,
    }

    mode = blend_map.get(args.blend, pyvips.BlendMode.OVER)

    # Ensure images have alpha for compositing
    if background.bands == 3:
        background = background.bandjoin(255)
    if overlay.bands == 3:
        overlay = overlay.bandjoin(255)

    result = background.composite2(overlay, mode, x=args.x, y=args.y)

    # Remove alpha if saving to JPEG
    if args.output.lower().endswith(('.jpg', '.jpeg')):
        result = result.flatten(background=[255, 255, 255])

    save_image(result, args.output, args)
    print(f"Composited: {args.input} + {args.overlay} -> {args.output}")


def adjust(args):
    """Adjust brightness, contrast, saturation."""
    image = pyvips.Image.new_from_file(args.input, access="sequential")

    # Brightness adjustment
    if args.brightness != 1.0:
        image = image * args.brightness

    # Contrast adjustment
    if args.contrast != 1.0:
        # Adjust around midpoint (128)
        image = (image - 128) * args.contrast + 128

    # Saturation adjustment
    if args.saturation != 1.0:
        # Convert to LCh color space for saturation control
        if image.bands >= 3:
            lch = image.colourspace(pyvips.Interpretation.LCH)
            # Scale chroma (saturation)
            l = lch.extract_band(0)
            c = lch.extract_band(1) * args.saturation
            h = lch.extract_band(2)
            lch = l.bandjoin([c, h])
            image = lch.colourspace(pyvips.Interpretation.SRGB)

    # Clamp values
    image = image.cast(pyvips.BandFormat.UCHAR)

    save_image(image, args.output, args)
    print(f"Adjusted: {args.input} -> {args.output}")


def sharpen(args):
    """Apply sharpening filter."""
    image = pyvips.Image.new_from_file(args.input, access="sequential")

    image = image.sharpen(
        sigma=args.sigma,
        x1=args.x1,
        y2=args.y2,
        y3=args.y3,
        m1=args.m1,
        m2=args.m2
    )

    save_image(image, args.output, args)
    print(f"Sharpened: {args.input} -> {args.output}")


def blur(args):
    """Apply Gaussian blur."""
    image = pyvips.Image.new_from_file(args.input, access="sequential")

    image = image.gaussblur(args.sigma)

    save_image(image, args.output, args)
    print(f"Blurred: {args.input} -> {args.output}")


def flip(args):
    """Flip image horizontally or vertically."""
    image = pyvips.Image.new_from_file(args.input, access="sequential")

    if args.horizontal:
        image = image.fliphor()
    if args.vertical:
        image = image.flipver()

    save_image(image, args.output, args)
    print(f"Flipped: {args.input} -> {args.output}")


def grayscale(args):
    """Convert to grayscale."""
    image = pyvips.Image.new_from_file(args.input, access="sequential")

    image = image.colourspace(pyvips.Interpretation.B_W)

    save_image(image, args.output, args)
    print(f"Grayscale: {args.input} -> {args.output}")


def info(args):
    """Display image information."""
    image = pyvips.Image.new_from_file(args.input)

    # Get file size
    file_path = Path(args.input)
    file_size = file_path.stat().st_size
    if file_size > 1024 * 1024:
        size_str = f"{file_size / (1024 * 1024):.1f} MB"
    elif file_size > 1024:
        size_str = f"{file_size / 1024:.1f} KB"
    else:
        size_str = f"{file_size} bytes"

    # Get format
    loader = image.get("vips-loader") if image.get_typeof("vips-loader") else "unknown"

    print(f"File: {args.input}")
    print(f"Format: {loader}")
    print(f"Width: {image.width}")
    print(f"Height: {image.height}")
    print(f"Bands: {image.bands}")
    print(f"Interpretation: {image.interpretation}")
    print(f"Size: {size_str}")

    # Print EXIF if available
    if args.exif:
        for field in image.get_fields():
            if field.startswith("exif-"):
                print(f"{field}: {image.get(field)}")


def save_image(image, output, args):
    """Save image with appropriate options based on format."""
    output_lower = output.lower()

    kwargs = {}

    if output_lower.endswith(('.jpg', '.jpeg')):
        kwargs['Q'] = args.quality
        kwargs['optimize_coding'] = True
        if hasattr(args, 'strip') and args.strip:
            kwargs['strip'] = True
    elif output_lower.endswith('.png'):
        kwargs['compression'] = args.compression
    elif output_lower.endswith('.webp'):
        kwargs['Q'] = args.quality
        if hasattr(args, 'lossless') and args.lossless:
            kwargs['lossless'] = True
    elif output_lower.endswith('.avif'):
        kwargs['Q'] = args.quality
    elif output_lower.endswith('.heic'):
        kwargs['Q'] = args.quality
    elif output_lower.endswith('.tiff'):
        kwargs['compression'] = 'lzw'

    image.write_to_file(output, **kwargs)


def main():
    parser = argparse.ArgumentParser(
        description="libvips image processing tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Common arguments
    def add_common_args(p):
        p.add_argument("input", help="Input image file")
        p.add_argument("output", nargs="?", help="Output image file")
        p.add_argument("--quality", "-q", type=int, default=85, help="JPEG/WebP quality (1-100)")
        p.add_argument("--compression", "-c", type=int, default=6, help="PNG compression (0-9)")
        p.add_argument("--strip", action="store_true", help="Strip metadata")
        p.add_argument("--lossless", action="store_true", help="Lossless WebP")

    # Resize
    p_resize = subparsers.add_parser("resize", help="Resize image")
    add_common_args(p_resize)
    p_resize.add_argument("--width", "-w", type=int, help="Target width")
    p_resize.add_argument("--height", type=int, help="Target height")
    p_resize.add_argument("--mode", "-m", choices=["fit", "cover", "force"], default="fit", help="Resize mode")

    # Thumbnail
    p_thumb = subparsers.add_parser("thumbnail", help="Create thumbnail")
    add_common_args(p_thumb)
    p_thumb.add_argument("--size", "-s", type=int, default=200, help="Thumbnail size")
    p_thumb.add_argument("--crop", choices=["none", "centre", "center", "entropy", "attention"], default="none", help="Crop strategy")

    # Convert
    p_convert = subparsers.add_parser("convert", help="Convert format")
    add_common_args(p_convert)

    # Crop
    p_crop = subparsers.add_parser("crop", help="Crop image")
    add_common_args(p_crop)
    p_crop.add_argument("--left", "-l", type=int, help="Left offset")
    p_crop.add_argument("--top", "-t", type=int, help="Top offset")
    p_crop.add_argument("--width", "-w", type=int, help="Crop width")
    p_crop.add_argument("--height", type=int, help="Crop height")
    p_crop.add_argument("--smart", action="store_true", help="Smart crop using attention")

    # Rotate
    p_rotate = subparsers.add_parser("rotate", help="Rotate image")
    add_common_args(p_rotate)
    p_rotate.add_argument("--angle", "-a", type=float, help="Rotation angle in degrees")
    p_rotate.add_argument("--auto", action="store_true", help="Auto-rotate based on EXIF")
    p_rotate.add_argument("--background", "-b", help="Background color (R,G,B)")

    # Watermark
    p_watermark = subparsers.add_parser("watermark", help="Add watermark")
    add_common_args(p_watermark)
    p_watermark.add_argument("--text", help="Watermark text")
    p_watermark.add_argument("--image", help="Watermark image")
    p_watermark.add_argument("--font", help="Font for text watermark")
    p_watermark.add_argument("--position", "-p", choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"], default="bottom-right", help="Watermark position")
    p_watermark.add_argument("--opacity", "-o", type=float, default=0.5, help="Watermark opacity (0-1)")

    # Composite (custom args order: input overlay output)
    p_composite = subparsers.add_parser("composite", help="Composite images")
    p_composite.add_argument("input", help="Background image file")
    p_composite.add_argument("overlay", help="Overlay image")
    p_composite.add_argument("output", help="Output image file")
    p_composite.add_argument("--quality", "-q", type=int, default=85, help="JPEG/WebP quality (1-100)")
    p_composite.add_argument("--compression", "-c", type=int, default=6, help="PNG compression (0-9)")
    p_composite.add_argument("--x", type=int, default=0, help="X offset")
    p_composite.add_argument("--y", type=int, default=0, help="Y offset")
    p_composite.add_argument("--blend", choices=["over", "multiply", "screen", "overlay", "darken", "lighten"], default="over", help="Blend mode")

    # Adjust
    p_adjust = subparsers.add_parser("adjust", help="Adjust brightness/contrast/saturation")
    add_common_args(p_adjust)
    p_adjust.add_argument("--brightness", type=float, default=1.0, help="Brightness multiplier")
    p_adjust.add_argument("--contrast", type=float, default=1.0, help="Contrast multiplier")
    p_adjust.add_argument("--saturation", type=float, default=1.0, help="Saturation multiplier")

    # Sharpen
    p_sharpen = subparsers.add_parser("sharpen", help="Sharpen image")
    add_common_args(p_sharpen)
    p_sharpen.add_argument("--sigma", type=float, default=0.5, help="Sigma for blur")
    p_sharpen.add_argument("--x1", type=float, default=2.0, help="Flat/jaggy threshold")
    p_sharpen.add_argument("--y2", type=float, default=10.0, help="Maximum darkening")
    p_sharpen.add_argument("--y3", type=float, default=20.0, help="Maximum brightening")
    p_sharpen.add_argument("--m1", type=float, default=0.0, help="Slope for flat areas")
    p_sharpen.add_argument("--m2", type=float, default=3.0, help="Slope for jaggy areas")

    # Blur
    p_blur = subparsers.add_parser("blur", help="Blur image")
    add_common_args(p_blur)
    p_blur.add_argument("--sigma", type=float, default=3.0, help="Blur sigma")

    # Flip
    p_flip = subparsers.add_parser("flip", help="Flip image")
    add_common_args(p_flip)
    p_flip.add_argument("--horizontal", "-H", action="store_true", help="Flip horizontally")
    p_flip.add_argument("--vertical", "-V", action="store_true", help="Flip vertically")

    # Grayscale
    p_gray = subparsers.add_parser("grayscale", help="Convert to grayscale")
    add_common_args(p_gray)

    # Info
    p_info = subparsers.add_parser("info", help="Show image info")
    p_info.add_argument("input", help="Input image file")
    p_info.add_argument("--exif", action="store_true", help="Show EXIF data")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Validate input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Execute command
    commands = {
        "resize": resize,
        "thumbnail": thumbnail,
        "convert": convert,
        "crop": crop,
        "rotate": rotate,
        "watermark": watermark,
        "composite": composite,
        "adjust": adjust,
        "sharpen": sharpen,
        "blur": blur,
        "flip": flip,
        "grayscale": grayscale,
        "info": info,
    }

    try:
        commands[args.command](args)
    except pyvips.Error as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
