#!/bin/bash

# Create PNG icons from SVG
# Requires ImageMagick: brew install imagemagick

echo "Creating menu bar icons..."

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "❌ ImageMagick not found. Installing..."
    brew install imagemagick
fi

# Convert SVG to PNG (menu bar size)
convert icons/icon.svg -resize 22x22 icons/icon.png
convert icons/icon.svg -resize 44x44 icons/icon@2x.png

echo "✅ Icons created:"
echo "   icons/icon.png (22x22)"
echo "   icons/icon@2x.png (44x44)"
