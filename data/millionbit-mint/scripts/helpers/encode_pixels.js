#!/usr/bin/env node
/**
 * encode_pixels.js - Convert an image to Million Bit Homepage v1 pixel encoding + pako compression
 *
 * Replicates the exact encoding pipeline from the frontend:
 *   - utils.js:stringDataForEth (v1 format)
 *   - App.vue:pako.deflate(str, { to: 'string' })
 *
 * Usage: node encode_pixels.js <image_path> <x1> <y1> <url> --output <output_path>
 *
 * Output: Writes compressed binary data to output file.
 *         Prints metadata JSON to stdout.
 */

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const pako = require('pako');

async function main() {
    const args = process.argv.slice(2);

    if (args.length < 4) {
        console.error('Usage: node encode_pixels.js <image_path> <x1> <y1> <url> --output <output_path>');
        process.exit(1);
    }

    const imagePath = args[0];
    const x1 = parseInt(args[1], 10);
    const y1 = parseInt(args[2], 10);
    const url = args[3];

    let outputPath = null;
    const outputIdx = args.indexOf('--output');
    if (outputIdx !== -1 && args[outputIdx + 1]) {
        outputPath = args[outputIdx + 1];
    }

    if (!outputPath) {
        console.error('Error: --output <path> is required');
        process.exit(1);
    }

    // Load image and get raw pixel data
    // Flatten alpha channel to white background (matching utils.js:replaceTransparent)
    const image = sharp(imagePath).flatten({ background: { r: 255, g: 255, b: 255 } });
    const metadata = await image.metadata();

    // Extract raw RGB pixel buffer
    const { data: rawPixels, info } = await image
        .ensureAlpha()
        .raw()
        .toBuffer({ resolveWithObject: true });

    const width = info.width;
    const height = info.height;
    const channels = info.channels; // Should be 4 (RGBA after ensureAlpha)

    // Validate dimensions are multiples of 16
    if (width % 16 !== 0 || height % 16 !== 0) {
        console.error(`Error: Image dimensions ${width}x${height} must be multiples of 16`);
        process.exit(1);
    }

    // Build v1 encoded strings for each 16x16 segment
    // Replicates utils.js:getPixelsData (line 73) and utils.js:stringDataForEth (line 121)
    const segments = [];
    const rows = height / 16;
    const cols = width / 16;

    for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
            const colors = [];

            // Extract 16x16 pixels in row-major order (matching frontend)
            for (let sy = 0; sy < 16; sy++) {
                for (let sx = 0; sx < 16; sx++) {
                    const px = col * 16 + sx;
                    const py = row * 16 + sy;
                    const idx = (py * width + px) * channels;

                    const r = rawPixels[idx];
                    const g = rawPixels[idx + 1];
                    const b = rawPixels[idx + 2];
                    const a = rawPixels[idx + 3];

                    // Replace fully transparent pixels with white
                    // (matching utils.js:replaceTransparent, line 196)
                    let hexColor;
                    if (a === 0) {
                        hexColor = 'ffffff';
                    } else {
                        hexColor = (
                            ('0' + r.toString(16)).slice(-2) +
                            ('0' + g.toString(16)).slice(-2) +
                            ('0' + b.toString(16)).slice(-2)
                        );
                    }
                    colors.push(hexColor);
                }
            }

            // Build segment string (matching utils.js:stringDataForEth)
            const xOffset = (x1 / 16) + col;
            const yOffset = (y1 / 16) + row;
            const encodedUrl = encodeURIComponent(url);
            const bid = '0';

            const segmentStr = `v1|${xOffset},${yOffset}|${colors.join(',')}|${bid}|${encodedUrl}`;
            segments.push(segmentStr);
        }
    }

    // Join all segments with newline
    const pixelDataStr = segments.join('\n');

    // Compress with pako.deflate - exact same call as the frontend
    const compressedStr = pako.deflate(pixelDataStr, { to: 'string' });

    // Write the compressed binary string to file
    // pako's { to: 'string' } produces a binary string where each char is one byte
    // We write it as a Buffer using latin1 encoding to preserve byte values
    const compressedBuffer = Buffer.from(compressedStr, 'latin1');
    fs.writeFileSync(outputPath, compressedBuffer);

    // Output metadata to stdout
    const result = {
        width,
        height,
        segments: segments.length,
        uncompressed_length: pixelDataStr.length,
        compressed_length: compressedBuffer.length,
        compression_ratio: (pixelDataStr.length / compressedBuffer.length).toFixed(2),
        output: outputPath,
    };
    console.log(JSON.stringify(result));
}

main().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
