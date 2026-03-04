#!/usr/bin/env node
/**
 * abi_encode.js - ABI-encode the mint() calldata for Million Bit Homepage
 *
 * Uses ethers.js to produce the exact same ABI encoding as the frontend.
 *
 * Usage: node abi_encode.js <x1> <y1> <x2> <y2> --pixel-file <compressed_data_file>
 *
 * Output: Hex-encoded calldata to stdout (with 0x prefix)
 */

const fs = require('fs');
const { Interface } = require('ethers');

// Minimal ABI for the mint function
const MINT_ABI = [
    'function mint(uint16 x1, uint16 y1, uint16 x2, uint16 y2, string pixelStr) payable',
];

function main() {
    const args = process.argv.slice(2);

    if (args.length < 4) {
        console.error('Usage: node abi_encode.js <x1> <y1> <x2> <y2> --pixel-file <path>');
        process.exit(1);
    }

    const x1 = parseInt(args[0], 10);
    const y1 = parseInt(args[1], 10);
    const x2 = parseInt(args[2], 10);
    const y2 = parseInt(args[3], 10);

    let pixelFile = null;
    const fileIdx = args.indexOf('--pixel-file');
    if (fileIdx !== -1 && args[fileIdx + 1]) {
        pixelFile = args[fileIdx + 1];
    }

    if (!pixelFile) {
        console.error('Error: --pixel-file <path> is required');
        process.exit(1);
    }

    // Read the compressed pixel data
    const compressedBuffer = fs.readFileSync(pixelFile);

    // Convert to binary string (same as pako's { to: 'string' } output)
    // Each byte becomes a character with that code point
    const pixelStr = compressedBuffer.toString('latin1');

    // ABI-encode the mint function call using ethers.js
    // This matches exactly how the frontend calls contract.mint(...)
    const iface = new Interface(MINT_ABI);
    const calldata = iface.encodeFunctionData('mint', [x1, y1, x2, y2, pixelStr]);

    // Output the hex calldata
    console.log(calldata);
}

main();
