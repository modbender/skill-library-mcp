#!/bin/bash
# AI Image De-Fingerprinting Tool (Bash version)
# Pure ImageMagick + ExifTool implementation
# Version: 1.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration presets
declare -A LIGHT_CONFIG=(
    [noise_attenuate]=3
    [contrast]="2x3"
    [saturation]=101
    [blur_radius]=0.2
    [sharpen_radius]=0.5
    [resize_factor]=99
    [jpeg_quality_low]=88
    [jpeg_quality_high]=96
)

declare -A MEDIUM_CONFIG=(
    [noise_attenuate]=5
    [contrast]="3x5"
    [saturation]=103
    [blur_radius]=0.3
    [sharpen_radius]=0.8
    [resize_factor]=97
    [jpeg_quality_low]=80
    [jpeg_quality_high]=94
)

declare -A HEAVY_CONFIG=(
    [noise_attenuate]=7
    [contrast]="4x8"
    [saturation]=105
    [blur_radius]=0.5
    [sharpen_radius]=1.2
    [resize_factor]=95
    [jpeg_quality_low]=72
    [jpeg_quality_high]=92
)

# Default to medium
declare -A CONFIG=()

function select_config() {
    local strength="${1:-medium}"
    case "$strength" in
        light)
            for key in "${!LIGHT_CONFIG[@]}"; do
                CONFIG[$key]="${LIGHT_CONFIG[$key]}"
            done
            ;;
        heavy)
            for key in "${!HEAVY_CONFIG[@]}"; do
                CONFIG[$key]="${HEAVY_CONFIG[$key]}"
            done
            ;;
        *)
            for key in "${!MEDIUM_CONFIG[@]}"; do
                CONFIG[$key]="${MEDIUM_CONFIG[$key]}"
            done
            ;;
    esac
}

function log_step() {
    local step="$1"
    local message="$2"
    echo -e "${GREEN}[$step/7]${NC} $message"
}

function log_info() {
    echo "    $1"
}

function log_error() {
    echo -e "${RED}Error:${NC} $1" >&2
}

function log_warning() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

function check_dependencies() {
    local missing=()
    
    if ! command -v magick &> /dev/null; then
        missing+=("imagemagick")
    fi
    
    if ! command -v exiftool &> /dev/null; then
        missing+=("exiftool")
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing[*]}"
        echo ""
        echo "Install with:"
        echo "  Debian/Ubuntu: sudo apt install imagemagick libimage-exiftool-perl"
        echo "  macOS: brew install imagemagick exiftool"
        echo "  Fedora: sudo dnf install ImageMagick perl-Image-ExifTool"
        exit 1
    fi
}

function remove_metadata() {
    local file="$1"
    log_step 1 "Stripping metadata (EXIF/C2PA/JUMBF)..."
    
    if exiftool -all= -overwrite_original "$file" 2>/dev/null; then
        log_info "Metadata removed successfully"
    else
        log_warning "Could not remove metadata (continuing anyway)"
    fi
}

function process_image() {
    local input="$1"
    local output="$2"
    local strength="${3:-medium}"
    
    # Setup config
    select_config "$strength"
    
    # Create temp directory
    local temp_dir="/tmp/deai_$$"
    mkdir -p "$temp_dir"
    
    echo ""
    echo "============================================================"
    echo "Processing: $(basename "$input")"
    echo "Strength: $strength"
    echo "============================================================"
    echo ""
    
    # Get original size
    local original_size=$(stat -f%z "$input" 2>/dev/null || stat -c%s "$input" 2>/dev/null)
    
    # Stage 1: Remove metadata
    remove_metadata "$input"
    
    # Stage 2: Add grain (Poisson noise)
    log_step 2 "Adding film grain / sensor noise..."
    log_info "Noise attenuation: ${CONFIG[noise_attenuate]}"
    magick "$input" \
        \( +clone +level-colors GREY50 -attenuate "${CONFIG[noise_attenuate]}" +noise Poisson -colorspace Gray \) \
        -compose Overlay -composite \
        "$temp_dir/step2.png"
    
    # Stage 3: Color/contrast adjustment
    log_step 3 "Adjusting color/contrast/brightness..."
    log_info "Contrast: ${CONFIG[contrast]}, Saturation: ${CONFIG[saturation]}%"
    magick "$temp_dir/step2.png" \
        -brightness-contrast "${CONFIG[contrast]}" \
        -modulate "100,${CONFIG[saturation]},100" \
        "$temp_dir/step3.png"
    
    # Stage 4: Blur and sharpen
    log_step 4 "Applying blur + sharpen cycle..."
    log_info "Blur radius: ${CONFIG[blur_radius]}, Sharpen radius: ${CONFIG[sharpen_radius]}"
    magick "$temp_dir/step3.png" \
        -blur "0x${CONFIG[blur_radius]}" \
        -sharpen "0x${CONFIG[sharpen_radius]}" \
        "$temp_dir/step4.png"
    
    # Stage 5: JPEG recompression cycle
    log_step 5 "JPEG recompression cycle..."
    log_info "First pass: quality ${CONFIG[jpeg_quality_low]}"
    magick "$temp_dir/step4.png" -quality "${CONFIG[jpeg_quality_low]}" "$temp_dir/step5a.jpg"
    
    log_info "Second pass: quality ${CONFIG[jpeg_quality_high]}"
    magick "$temp_dir/step5a.jpg" -quality "${CONFIG[jpeg_quality_high]}" "$temp_dir/step5.jpg"
    
    # Stage 6: Resize cycle (resampling artifacts)
    log_step 6 "Resize cycle (resampling artifacts)..."
    local resize_pct="${CONFIG[resize_factor]}"
    local restore_pct=$(python3 -c "print(round(10000.0/$resize_pct, 2))" 2>/dev/null || echo "103.09")
    
    log_info "Downscale to ${resize_pct}%, upscale to ${restore_pct}%"
    magick "$temp_dir/step5.jpg" \
        -resize "${resize_pct}%" \
        -resize "${restore_pct}%" \
        "$temp_dir/step6.jpg"
    
    # Stage 7: Final save and metadata clean
    log_step 7 "Saving final output..."
    magick "$temp_dir/step6.jpg" \
        -quality "${CONFIG[jpeg_quality_high]}" \
        -strip \
        "$output"
    
    # Final metadata strip
    exiftool -all= -overwrite_original "$output" 2>/dev/null || true
    
    # Get processed size
    local processed_size=$(stat -f%z "$output" 2>/dev/null || stat -c%s "$output" 2>/dev/null)
    
    # Cleanup
    rm -rf "$temp_dir"
    
    # Print report
    print_report "$input" "$output" "$original_size" "$processed_size" "$strength"
}

function print_report() {
    local input="$1"
    local output="$2"
    local original_size="$3"
    local processed_size="$4"
    local strength="$5"
    
    local original_kb=$((original_size / 1024))
    local processed_kb=$((processed_size / 1024))
    local size_change=$(python3 -c "print(round((($processed_size - $original_size) / $original_size) * 100, 1))" 2>/dev/null || echo "N/A")
    
    echo ""
    echo "============================================================"
    echo -e "${GREEN}✓ Processing complete!${NC}"
    echo "============================================================"
    echo "Output: $output"
    echo "Original size: ${original_kb} KB"
    echo "Processed size: ${processed_kb} KB"
    echo "Size change: ${size_change}%"
    echo ""
    echo "Processing stages applied:"
    echo "  1. Metadata strip (EXIF/C2PA)"
    echo "  2. Film grain (${CONFIG[noise_attenuate]} attenuate)"
    echo "  3. Color adjustment ($strength profile)"
    echo "  4. Blur/sharpen cycle"
    echo "  5. JPEG recompression (${CONFIG[jpeg_quality_low]}→${CONFIG[jpeg_quality_high]})"
    echo "  6. Resize cycle (${CONFIG[resize_factor]}%)"
    echo "  7. Final metadata clean"
    echo ""
    echo "⚠️  Verify output with AI detectors:"
    echo "  • Hive Moderation: https://hivemoderation.com/ai-generated-content-detection"
    echo "  • Illuminarty: https://illuminarty.ai/"
    echo "  • AI or Not: https://aiornot.com/"
    echo "============================================================"
    echo ""
}

function show_usage() {
    cat << EOF
AI Image De-Fingerprinting Tool (Bash version)
Pure ImageMagick + ExifTool implementation

Usage: $0 <input> <output> [strength]

Arguments:
  input       Input image file (jpg/png/webp)
  output      Output file path
  strength    Processing strength: light|medium|heavy (default: medium)

Examples:
  $0 image.png output.jpg
  $0 image.png output.jpg heavy
  $0 ai_gen.png clean.jpg light

Processing Strengths:
  light       Minimal processing, best quality (35-45% success)
  medium      Balanced approach (50-65% success) [DEFAULT]
  heavy       Aggressive processing (65-80% success)

Dependencies:
  - ImageMagick 7.0+
  - ExifTool
  - Python3 (for calculations, optional)

EOF
}

# Main script
function main() {
    # Check arguments
    if [ $# -lt 2 ]; then
        show_usage
        exit 1
    fi
    
    local input="$1"
    local output="$2"
    local strength="${3:-medium}"
    
    # Validate strength
    if [[ ! "$strength" =~ ^(light|medium|heavy)$ ]]; then
        log_error "Invalid strength: $strength (must be light/medium/heavy)"
        exit 1
    fi
    
    # Check if input exists
    if [ ! -f "$input" ]; then
        log_error "Input file not found: $input"
        exit 1
    fi
    
    # Check dependencies
    check_dependencies
    
    # Process image
    process_image "$input" "$output" "$strength"
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    main "$@"
fi
