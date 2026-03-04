#!/usr/bin/env node
/**
 * find_plots.js - Scan the Million Bit Homepage grid for available plot positions
 *
 * Uses batch JSON-RPC calls to efficiently check checkOverlap across the grid.
 *
 * Usage: node find_plots.js <width> <height> [--limit N] [--rpc-url URL]
 *
 * Output: JSON array of available positions to stdout
 */

const https = require('https');
const http = require('http');
const { AbiCoder, keccak256, toUtf8Bytes } = require('ethers');

const CONTRACT = '0x25b9afe64bb3593ec7e9dc7ef386a9b04c53f96e';
const DEFAULT_RPC = 'https://mainnet.base.org';
const CANVAS_SIZE = 1024;
const GRID_UNIT = 16;

// Function selector for checkOverlap(uint16,uint16,uint16,uint16)
const SEL_CHECK_OVERLAP = '84bd3031';

function encodeCheckOverlap(x1, y1, x2, y2) {
    const coder = AbiCoder.defaultAbiCoder();
    const params = coder.encode(['uint16', 'uint16', 'uint16', 'uint16'], [x1, y1, x2, y2]);
    return '0x' + SEL_CHECK_OVERLAP + params.slice(2);
}

function makeRpcRequest(url, body) {
    return new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const transport = urlObj.protocol === 'https:' ? https : http;
        const options = {
            hostname: urlObj.hostname,
            port: urlObj.port,
            path: urlObj.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const req = transport.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    reject(new Error(`Failed to parse response: ${data.slice(0, 200)}`));
                }
            });
        });

        req.on('error', reject);
        req.write(JSON.stringify(body));
        req.end();
    });
}

async function batchCheckOverlap(positions, rpcUrl) {
    const BATCH_SIZE = 10; // Public Base RPC limits to 10 calls per batch
    const results = [];

    for (let i = 0; i < positions.length; i += BATCH_SIZE) {
        const batch = positions.slice(i, i + BATCH_SIZE);
        const rpcBatch = batch.map((pos, idx) => ({
            jsonrpc: '2.0',
            id: i + idx,
            method: 'eth_call',
            params: [
                {
                    to: CONTRACT,
                    data: encodeCheckOverlap(pos.x1, pos.y1, pos.x2, pos.y2),
                },
                'latest',
            ],
        }));

        const responses = await makeRpcRequest(rpcUrl, rpcBatch);

        // Handle batch-level errors (e.g., RPC rejects the batch entirely)
        if (!Array.isArray(responses)) {
            const errMsg = responses.error ? responses.error.message : 'Batch request failed';
            process.stderr.write(`  Batch error: ${errMsg}\n`);
            for (const pos of batch) {
                results.push({ ...pos, available: false, error: errMsg });
            }
            continue;
        }

        const sortedResponses = responses.sort((a, b) => a.id - b.id);

        for (let j = 0; j < sortedResponses.length; j++) {
            const resp = sortedResponses[j];
            if (resp.result) {
                // checkOverlap returns bool: 0x...01 = occupied, 0x...00 = available
                const isOccupied = parseInt(resp.result, 16) !== 0;
                results.push({
                    ...batch[j],
                    available: !isOccupied,
                });
            } else {
                // RPC error, mark as unknown
                results.push({
                    ...batch[j],
                    available: false,
                    error: resp.error ? resp.error.message : 'Unknown error',
                });
            }
        }

        // Small delay between batches to avoid rate limiting
        if (i + BATCH_SIZE < positions.length) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }

    return results;
}

async function main() {
    const args = process.argv.slice(2);

    if (args.length < 2) {
        console.error('Usage: node find_plots.js <width> <height> [--limit N] [--rpc-url URL]');
        process.exit(1);
    }

    const width = parseInt(args[0], 10);
    const height = parseInt(args[1], 10);

    let limit = 10;
    const limitIdx = args.indexOf('--limit');
    if (limitIdx !== -1 && args[limitIdx + 1]) {
        limit = parseInt(args[limitIdx + 1], 10);
    }

    let rpcUrl = DEFAULT_RPC;
    const rpcIdx = args.indexOf('--rpc-url');
    if (rpcIdx !== -1 && args[rpcIdx + 1]) {
        rpcUrl = args[rpcIdx + 1];
    }

    // Validate
    if (width % GRID_UNIT !== 0 || height % GRID_UNIT !== 0) {
        console.error(`Error: Dimensions ${width}x${height} must be multiples of ${GRID_UNIT}`);
        process.exit(1);
    }

    // Generate all candidate positions
    const candidates = [];
    for (let y = 0; y + height <= CANVAS_SIZE; y += GRID_UNIT) {
        for (let x = 0; x + width <= CANVAS_SIZE; x += GRID_UNIT) {
            candidates.push({ x1: x, y1: y, x2: x + width, y2: y + height });
        }
    }

    // Process stderr for progress info
    process.stderr.write(`Scanning ${candidates.length} positions for ${width}x${height} plots...\n`);

    // Check in batches, stop early when we have enough
    const BATCH_SIZE = 10; // Public Base RPC limits to 10 calls per batch
    const available = [];

    for (let i = 0; i < candidates.length && available.length < limit; i += BATCH_SIZE) {
        const batch = candidates.slice(i, i + BATCH_SIZE);
        const results = await batchCheckOverlap(batch, rpcUrl);

        for (const r of results) {
            if (r.available) {
                available.push({ x1: r.x1, y1: r.y1, x2: r.x2, y2: r.y2 });
                if (available.length >= limit) break;
            }
        }

        process.stderr.write(`  Checked ${Math.min(i + BATCH_SIZE, candidates.length)}/${candidates.length}, found ${available.length}/${limit}\n`);
    }

    const output = {
        available_plots: available,
        count: available.length,
        plot_size: `${width}x${height}`,
        total_candidates: candidates.length,
    };

    console.log(JSON.stringify(output, null, 2));
}

main().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
