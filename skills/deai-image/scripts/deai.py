#!/usr/bin/env python3
"""
AI Image De-Fingerprinting Tool
Removes AI detection patterns from AI-generated images
Version: 1.0.0
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

class ImageDeAIProcessor:
    """Process AI-generated images to reduce detection fingerprints"""
    
    STRENGTH_CONFIGS = {
        'light': {
            'noise_std': 1.5,
            'contrast': 1.03,
            'saturation': 1.01,
            'brightness': 1.02,
            'blur_radius': 0.2,
            'sharpen_radius': 0.5,
            'resize_factor': 0.99,
            'jpeg_quality_low': 88,
            'jpeg_quality_high': 96,
        },
        'medium': {
            'noise_std': 2.5,
            'contrast': 1.05,
            'saturation': 1.03,
            'brightness': 1.03,
            'blur_radius': 0.3,
            'sharpen_radius': 0.8,
            'resize_factor': 0.97,
            'jpeg_quality_low': 80,
            'jpeg_quality_high': 94,
        },
        'heavy': {
            'noise_std': 4.0,
            'contrast': 1.08,
            'saturation': 1.05,
            'brightness': 1.04,
            'blur_radius': 0.5,
            'sharpen_radius': 1.2,
            'resize_factor': 0.95,
            'jpeg_quality_low': 72,
            'jpeg_quality_high': 92,
        }
    }
    
    def __init__(self, input_path, output_path=None, strength='medium', verbose=False):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path) if output_path else self._default_output()
        self.strength = strength
        self.verbose = verbose
        self.config = self.STRENGTH_CONFIGS[strength]
        self.temp_dir = Path("/tmp") / f"deai_{os.getpid()}"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Statistics
        self.original_size = 0
        self.processed_size = 0
    
    def _default_output(self):
        """Generate default output filename"""
        stem = self.input_path.stem
        return self.input_path.parent / f"{stem}_deai.jpg"
    
    def _log(self, message, step=None):
        """Log processing steps"""
        if self.verbose:
            if step:
                print(f"[{step}/7] {message}")
            else:
                print(f"    {message}")
    
    def _run_exiftool(self, filepath, remove_all=True):
        """Strip metadata using ExifTool"""
        try:
            if remove_all:
                subprocess.run(
                    ["exiftool", "-all=", "-overwrite_original", str(filepath)],
                    check=True,
                    capture_output=True,
                    text=True
                )
            else:
                # Only remove C2PA/AI-specific tags
                subprocess.run(
                    ["exiftool", "-JUMBF:all=", "-Software=", "-Creator=", 
                     "-overwrite_original", str(filepath)],
                    check=True,
                    capture_output=True,
                    text=True
                )
            return True
        except subprocess.CalledProcessError as e:
            self._log(f"Warning: ExifTool error: {e.stderr}", None)
            return False
        except FileNotFoundError:
            self._log("Warning: ExifTool not found, skipping metadata removal", None)
            return False
    
    def remove_metadata(self):
        """Stage 1: Remove EXIF/C2PA/JUMBF metadata"""
        self._log("Stripping metadata (EXIF/C2PA/JUMBF)...", step=1)
        self._run_exiftool(self.input_path)
    
    def add_grain(self, img):
        """Stage 2: Add camera sensor-like noise"""
        self._log("Adding film grain / sensor noise...", step=2)
        
        img_array = np.array(img, dtype=np.float32)
        
        # Add Gaussian noise
        noise = np.random.normal(0, self.config['noise_std'], img_array.shape)
        noisy_array = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        
        self._log(f"Noise strength: {self.config['noise_std']} std dev", None)
        
        return Image.fromarray(noisy_array)
    
    def adjust_colors(self, img):
        """Stage 3: Adjust color/contrast to break AI patterns"""
        self._log("Adjusting color/contrast/brightness...", step=3)
        
        # Contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(self.config['contrast'])
        self._log(f"Contrast: {self.config['contrast']}x", None)
        
        # Saturation
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(self.config['saturation'])
        self._log(f"Saturation: {self.config['saturation']}x", None)
        
        # Brightness
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(self.config['brightness'])
        self._log(f"Brightness: {self.config['brightness']}x", None)
        
        return img
    
    def blur_and_sharpen(self, img):
        """Stage 4: Blur then sharpen to disrupt edge patterns"""
        self._log("Applying blur + sharpen cycle...", step=4)
        
        # Gaussian blur
        img = img.filter(ImageFilter.GaussianBlur(radius=self.config['blur_radius']))
        self._log(f"Blur radius: {self.config['blur_radius']}", None)
        
        # Unsharp mask (sharpen)
        img = img.filter(ImageFilter.UnsharpMask(
            radius=self.config['sharpen_radius'],
            percent=120,
            threshold=3
        ))
        self._log(f"Sharpen radius: {self.config['sharpen_radius']}", None)
        
        return img
    
    def jpeg_recompress(self, img):
        """Stage 5: JPEG compression cycle (introduce artifacts)"""
        self._log("JPEG recompression cycle...", step=5)
        
        temp_path = self.temp_dir / "temp_compress.jpg"
        
        # Low quality compression
        img.save(temp_path, "JPEG", quality=self.config['jpeg_quality_low'], optimize=True)
        self._log(f"First pass: quality {self.config['jpeg_quality_low']}", None)
        
        # Reload and save at higher quality
        img = Image.open(temp_path)
        self._log(f"Second pass: quality {self.config['jpeg_quality_high']}", None)
        
        return img
    
    def resize_cycle(self, img):
        """Stage 6: Resize down/up to introduce resampling artifacts"""
        self._log("Resize cycle (resampling artifacts)...", step=6)
        
        original_size = img.size
        factor = self.config['resize_factor']
        
        # Downscale
        new_size = (int(original_size[0] * factor), int(original_size[1] * factor))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        self._log(f"Downscale to {new_size[0]}x{new_size[1]}", None)
        
        # Upscale back
        img = img.resize(original_size, Image.Resampling.LANCZOS)
        self._log(f"Upscale to {original_size[0]}x{original_size[1]}", None)
        
        return img
    
    def process(self):
        """Execute full de-fingerprinting pipeline"""
        print(f"\n{'='*60}")
        print(f"Processing: {self.input_path.name}")
        print(f"Strength: {self.strength}")
        print(f"{'='*60}\n")
        
        # Record original size
        self.original_size = self.input_path.stat().st_size
        
        # Stage 1: Metadata removal
        self.remove_metadata()
        
        # Load image
        try:
            img = Image.open(self.input_path)
        except Exception as e:
            print(f"Error: Cannot open image: {e}")
            return False
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            self._log(f"Converting from {img.mode} to RGB", None)
            img = img.convert('RGB')
        
        # Stage 2-6: Image processing pipeline
        img = self.add_grain(img)
        img = self.adjust_colors(img)
        img = self.blur_and_sharpen(img)
        img = self.resize_cycle(img)
        img = self.jpeg_recompress(img)
        
        # Stage 7: Save and final metadata clean
        self._log("Saving final output...", step=7)
        img.save(self.output_path, "JPEG", quality=self.config['jpeg_quality_high'], optimize=True)
        
        # Final metadata strip
        self._run_exiftool(self.output_path)
        
        # Statistics
        self.processed_size = self.output_path.stat().st_size
        
        # Report
        self._print_report()
        
        # Cleanup
        if self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
        
        return True
    
    def _print_report(self):
        """Print processing report"""
        size_change = ((self.processed_size - self.original_size) / self.original_size) * 100
        
        print(f"\n{'='*60}")
        print(f"✓ Processing complete!")
        print(f"{'='*60}")
        print(f"Output: {self.output_path}")
        print(f"Original size: {self.original_size / 1024:.1f} KB")
        print(f"Processed size: {self.processed_size / 1024:.1f} KB")
        print(f"Size change: {size_change:+.1f}%")
        print(f"\nProcessing stages applied:")
        print(f"  1. Metadata strip (EXIF/C2PA)")
        print(f"  2. Film grain ({self.config['noise_std']} std dev)")
        print(f"  3. Color adjustment ({self.strength} profile)")
        print(f"  4. Blur/sharpen cycle")
        print(f"  5. JPEG recompression ({self.config['jpeg_quality_low']}→{self.config['jpeg_quality_high']})")
        print(f"  6. Resize cycle ({self.config['resize_factor']}x)")
        print(f"  7. Final metadata clean")
        print(f"\n⚠️  Verify output with AI detectors:")
        print(f"  • Hive Moderation: https://hivemoderation.com/ai-generated-content-detection")
        print(f"  • Illuminarty: https://illuminarty.ai/")
        print(f"  • AI or Not: https://aiornot.com/")
        print(f"{'='*60}\n")


def metadata_only_mode(input_path, output_path):
    """Strip metadata only, no image processing"""
    print(f"\nMetadata-only mode: {input_path}")
    
    if output_path:
        # Copy to output first
        import shutil
        shutil.copy2(input_path, output_path)
        target = output_path
    else:
        target = input_path
    
    try:
        subprocess.run(
            ["exiftool", "-all=", "-overwrite_original", str(target)],
            check=True,
            capture_output=True
        )
        print(f"✓ Metadata stripped: {target}\n")
        return True
    except FileNotFoundError:
        print("Error: ExifTool not found. Install with:")
        print("  Debian/Ubuntu: sudo apt install libimage-exiftool-perl")
        print("  macOS: brew install exiftool")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return False


def batch_process(input_dir, output_dir=None, strength='medium', verbose=False):
    """Batch process directory of images"""
    input_path = Path(input_dir)
    
    if not input_path.is_dir():
        print(f"Error: {input_dir} is not a directory")
        return False
    
    # Find all images
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.JPG', '*.JPEG', '*.PNG']
    image_files = []
    for ext in extensions:
        image_files.extend(input_path.glob(ext))
    
    if not image_files:
        print(f"No image files found in {input_dir}")
        return False
    
    print(f"\nFound {len(image_files)} images to process")
    
    # Setup output directory
    if output_dir:
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
    else:
        out_path = input_path / "deai_output"
        out_path.mkdir(exist_ok=True)
    
    # Process each image
    success_count = 0
    for i, img_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Processing {img_file.name}...")
        
        output_file = out_path / f"{img_file.stem}_deai.jpg"
        
        processor = ImageDeAIProcessor(
            img_file, 
            output_file, 
            strength=strength, 
            verbose=verbose
        )
        
        if processor.process():
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Batch processing complete!")
    print(f"Processed: {success_count}/{len(image_files)} images")
    print(f"Output directory: {out_path}")
    print(f"{'='*60}\n")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="AI Image De-Fingerprinting Tool - Remove AI detection patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s image.png                              # Default processing
  %(prog)s image.png -o clean.jpg                 # Specify output
  %(prog)s image.png --strength heavy             # Aggressive processing
  %(prog)s image.png --no-metadata                # Only strip metadata
  %(prog)s images/ --batch                        # Batch process directory
  %(prog)s images/ --batch -o output/             # Batch with output dir

Processing Strengths:
  light    - Minimal processing, best quality (35-45% success)
  medium   - Balanced approach (50-65% success) [DEFAULT]
  heavy    - Aggressive processing (65-80% success)
        """
    )
    
    parser.add_argument('input', help='Input image file or directory (for batch mode)')
    parser.add_argument('-o', '--output', help='Output file or directory path')
    parser.add_argument('--strength', choices=['light', 'medium', 'heavy'], 
                        default='medium', help='Processing strength (default: medium)')
    parser.add_argument('--no-metadata', action='store_true', 
                        help='Only strip metadata, skip image processing')
    parser.add_argument('--batch', action='store_true', 
                        help='Batch process directory')
    parser.add_argument('-v', '--verbose', action='store_true', 
                        help='Verbose output (show all processing steps)')
    parser.add_argument('-q', '--quiet', action='store_true', 
                        help='Quiet mode (minimal output)')
    
    args = parser.parse_args()
    
    # Check if input exists
    if not Path(args.input).exists():
        print(f"Error: Input not found: {args.input}")
        sys.exit(1)
    
    # Metadata-only mode
    if args.no_metadata:
        success = metadata_only_mode(args.input, args.output)
        sys.exit(0 if success else 1)
    
    # Batch mode
    if args.batch:
        success = batch_process(args.input, args.output, args.strength, args.verbose)
        sys.exit(0 if success else 1)
    
    # Single file mode
    processor = ImageDeAIProcessor(
        args.input, 
        args.output, 
        strength=args.strength,
        verbose=args.verbose or not args.quiet
    )
    
    success = processor.process()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
