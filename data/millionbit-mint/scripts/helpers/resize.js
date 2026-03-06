#!/usr/bin/env node
/**
 * resize.js - Resize an image to exact plot dimensions using sharp
 *
 * Replaces transparent pixels with white and force-resizes to exact dimensions.
 *
 * Usage: node resize.js <input_image> <width> <height> <output_image>
 *
 * Output: JSON to stdout with output path and dimensions
 */

const sharp = require('sharp');

async function main() {
    const args = process.argv.slice(2);

    if (args.length < 4) {
        console.error('Usage: node resize.js <input_image> <width> <height> <output_image>');
        process.exit(1);
    }

    const inputPath = args[0];
    const targetWidth = parseInt(args[1], 10);
    const targetHeight = parseInt(args[2], 10);
    const outputPath = args[3];

    // Validate dimensions
    if (targetWidth % 16 !== 0 || targetHeight % 16 !== 0) {
        console.error(`Error: Dimensions ${targetWidth}x${targetHeight} must be multiples of 16`);
        process.exit(1);
    }

    if (targetWidth < 16 || targetHeight < 16) {
        console.error('Error: Minimum dimension is 16x16');
        process.exit(1);
    }

    if (targetWidth > 1024 || targetHeight > 1024) {
        console.error('Error: Maximum dimension is 1024x1024');
        process.exit(1);
    }

    // Resize with white background for transparency, force exact dimensions
    await sharp(inputPath)
        .flatten({ background: { r: 255, g: 255, b: 255 } })
        .resize(targetWidth, targetHeight, {
            fit: 'fill',  // Force exact dimensions (ignore aspect ratio)
        })
        .png()
        .toFile(outputPath);

    const result = {
        output: outputPath,
        width: targetWidth,
        height: targetHeight,
    };
    console.log(JSON.stringify(result));
}

main().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
