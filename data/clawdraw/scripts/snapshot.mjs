#!/usr/bin/env node
/**
 * Bot-side snapshot capture — fetches rendered tiles from the CDN,
 * composites them, crops to the drawing bounding box, and encodes PNG.
 *
 * Dependencies: @cwasm/webp (WASM WebP decoder), pngjs (pure JS PNG encoder)
 */

// @security-manifest
// env: none
// endpoints: relay.clawdraw.ai (HTTPS, tile CDN)
// files: /tmp/clawdraw-snapshot-*.png (temporary)
// exec: none

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import webp from '@cwasm/webp';
import { PNG } from 'pngjs';
import { onTileUpdate, offTileUpdate } from './connection.mjs';

/** Tile size in canvas units (one z8 tile = one chunk). */
const CHUNK_SIZE = 1024;
/** Tile image resolution in pixels. */
const TILE_PX = 256;
/** Canvas units per pixel at z8. */
const UNITS_PER_PX = CHUNK_SIZE / TILE_PX; // 4

/**
 * Compute axis-aligned bounding box from an array of strokes.
 *
 * @param {Array} strokes - Stroke objects with .points[].{x,y} and .brush.size
 * @returns {{ minX: number, minY: number, maxX: number, maxY: number }}
 */
export function computeBoundingBox(strokes) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

  for (const stroke of strokes) {
    const pad = (stroke.brush?.size || 5) / 2;
    for (const pt of stroke.points || []) {
      minX = Math.min(minX, pt.x - pad);
      minY = Math.min(minY, pt.y - pad);
      maxX = Math.max(maxX, pt.x + pad);
      maxY = Math.max(maxY, pt.y + pad);
    }
  }

  return { minX, minY, maxX, maxY };
}

/**
 * Map a canvas bounding box to z8 tile coordinates.
 *
 * @param {{ minX: number, minY: number, maxX: number, maxY: number }} bbox
 * @returns {{ minTX: number, minTY: number, maxTX: number, maxTY: number, tiles: Array<{x:number,y:number}> }}
 */
export function getTilesForBounds(bbox) {
  const minTX = Math.floor(bbox.minX / CHUNK_SIZE);
  const minTY = Math.floor(bbox.minY / CHUNK_SIZE);
  const maxTX = Math.floor(bbox.maxX / CHUNK_SIZE);
  const maxTY = Math.floor(bbox.maxY / CHUNK_SIZE);

  const tiles = [];
  for (let ty = minTY; ty <= maxTY; ty++) {
    for (let tx = minTX; tx <= maxTX; tx++) {
      tiles.push({ x: tx, y: ty });
    }
  }

  return { minTX, minTY, maxTX, maxTY, tiles };
}

/**
 * Wait for tile.updated WebSocket events covering the given z8 tile coords.
 * Resolves with a map of `"x_y"` → version when all tiles are received,
 * or after timeout (partial results).
 *
 * @param {WebSocket} ws
 * @param {Array<{x:number,y:number}>} tileCoords - z8 tiles to wait for
 * @param {number} [timeoutMs=15000]
 * @returns {Promise<Map<string,number>>} tileKey → version
 */
export function waitForTileUpdates(ws, tileCoords, timeoutMs = 15000) {
  return new Promise((resolve) => {
    const needed = new Set(tileCoords.map(t => `${t.x}_${t.y}`));
    const versions = new Map();

    // If no tiles needed, resolve immediately
    if (needed.size === 0) {
      resolve(versions);
      return;
    }

    const timeout = setTimeout(() => {
      offTileUpdate(ws, handler);
      resolve(versions);
    }, timeoutMs);

    function handler(msg) {
      if (msg.z !== 8) return; // Only interested in z8 tiles
      const key = `${msg.x}_${msg.y}`;
      if (needed.has(key)) {
        versions.set(key, msg.version);
        needed.delete(key);
        if (needed.size === 0) {
          clearTimeout(timeout);
          offTileUpdate(ws, handler);
          resolve(versions);
        }
      }
    }

    onTileUpdate(ws, handler);
  });
}

/**
 * Fetch z8 tile images from the tile CDN.
 *
 * @param {string} cdnUrl - Base tile CDN URL (e.g. "https://tiles.clawdraw.ai/tiles")
 * @param {Array<{x:number,y:number}>} tileCoords
 * @param {Map<string,number>} [versions] - Optional version hints for cache-busting
 * @returns {Promise<Map<string, ArrayBuffer>>} tileKey → raw WebP bytes
 */
export async function fetchTiles(cdnUrl, tileCoords, versions = new Map()) {
  const results = new Map();

  const fetches = tileCoords.map(async ({ x, y }) => {
    const key = `${x}_${y}`;
    const v = versions.get(key);
    const vParam = v ? `?v=${v}` : '';
    const url = `${cdnUrl}/z8/${key}.webp${vParam}`;

    try {
      const res = await fetch(url);
      if (res.ok) {
        results.set(key, await res.arrayBuffer());
      } else {
        // Tile may not exist yet (empty chunk) — use transparent
        results.set(key, null);
      }
    } catch {
      results.set(key, null);
    }
  });

  await Promise.all(fetches);
  return results;
}

/**
 * Decode WebP tiles, composite into a grid, crop to bounding box, encode PNG.
 *
 * @param {Map<string, ArrayBuffer|null>} tileBuffers - tileKey → WebP bytes (null = empty)
 * @param {{ minTX: number, minTY: number, maxTX: number, maxTY: number }} grid
 * @param {{ minX: number, minY: number, maxX: number, maxY: number }} bbox - Canvas-unit bbox
 * @returns {Buffer} PNG-encoded image
 */
export function compositeAndCrop(tileBuffers, grid, bbox) {
  const gridW = grid.maxTX - grid.minTX + 1;
  const gridH = grid.maxTY - grid.minTY + 1;
  const compositeW = gridW * TILE_PX;
  const compositeH = gridH * TILE_PX;

  // Create composite RGBA buffer (initialized to transparent black)
  const composite = Buffer.alloc(compositeW * compositeH * 4);

  // Place each tile into the composite
  for (let ty = grid.minTY; ty <= grid.maxTY; ty++) {
    for (let tx = grid.minTX; tx <= grid.maxTX; tx++) {
      const key = `${tx}_${ty}`;
      const webpBytes = tileBuffers.get(key);
      if (!webpBytes) continue; // Empty tile — leave transparent

      let decoded;
      try {
        decoded = webp.decode(new Uint8Array(webpBytes));
      } catch {
        continue; // Decode failure — skip tile
      }

      // Copy tile pixels into composite at the correct grid position
      const offsetX = (tx - grid.minTX) * TILE_PX;
      const offsetY = (ty - grid.minTY) * TILE_PX;

      for (let row = 0; row < decoded.height && row < TILE_PX; row++) {
        const srcStart = row * decoded.width * 4;
        const srcEnd = srcStart + Math.min(decoded.width, TILE_PX) * 4;
        const dstStart = ((offsetY + row) * compositeW + offsetX) * 4;
        composite.set(decoded.data.subarray(srcStart, srcEnd), dstStart);
      }
    }
  }

  // Convert canvas-unit bbox to pixel coords within the composite
  const cropX1 = Math.max(0, Math.floor((bbox.minX - grid.minTX * CHUNK_SIZE) / UNITS_PER_PX));
  const cropY1 = Math.max(0, Math.floor((bbox.minY - grid.minTY * CHUNK_SIZE) / UNITS_PER_PX));
  const cropX2 = Math.min(compositeW, Math.ceil((bbox.maxX - grid.minTX * CHUNK_SIZE) / UNITS_PER_PX));
  const cropY2 = Math.min(compositeH, Math.ceil((bbox.maxY - grid.minTY * CHUNK_SIZE) / UNITS_PER_PX));

  const cropW = Math.max(1, cropX2 - cropX1);
  const cropH = Math.max(1, cropY2 - cropY1);

  // Create cropped PNG
  const png = new PNG({ width: cropW, height: cropH });
  for (let y = 0; y < cropH; y++) {
    const srcRow = (cropY1 + y) * compositeW * 4 + cropX1 * 4;
    const dstRow = y * cropW * 4;
    composite.copy(png.data, dstRow, srcRow, srcRow + cropW * 4);
  }

  return PNG.sync.write(png);
}

/**
 * Full snapshot pipeline: compute bounds → wait for tiles → fetch → crop → save PNG.
 *
 * @param {WebSocket} ws - Connected WebSocket (for tile.updated events)
 * @param {Array} strokes - Strokes that were drawn
 * @param {string} tileCdnUrl - Tile CDN base URL
 * @param {object} [opts]
 * @param {number} [opts.timeoutMs=15000] - Max wait for tile.updated events
 * @param {string} [opts.outDir] - Output directory (default: os.tmpdir())
 * @returns {Promise<{ imagePath: string, center: {x:number,y:number}, boundingBox: object, width: number, height: number } | null>}
 */
export async function captureSnapshot(ws, strokes, tileCdnUrl, opts = {}) {
  if (!strokes || strokes.length === 0) return null;

  const timeoutMs = opts.timeoutMs ?? 15000;
  const outDir = opts.outDir || os.tmpdir();

  // 1. Compute bounding box
  const bbox = computeBoundingBox(strokes);
  if (!isFinite(bbox.minX)) return null; // No valid points

  // 2. Map to tile coordinates
  const grid = getTilesForBounds(bbox);

  // 3. Wait for tile.updated events
  const versions = await waitForTileUpdates(ws, grid.tiles, timeoutMs);

  // 4. Fetch tile images from CDN
  const tileBuffers = await fetchTiles(tileCdnUrl, grid.tiles, versions);

  // 5. Composite and crop
  const pngBuf = compositeAndCrop(tileBuffers, grid, bbox);

  // 6. Save to file
  const timestamp = Date.now();
  const imagePath = path.join(outDir, `clawdraw-snapshot-${timestamp}.png`);
  fs.writeFileSync(imagePath, pngBuf);

  // Compute dimensions for reporting
  const cropW = Math.max(1, Math.ceil((bbox.maxX - bbox.minX) / UNITS_PER_PX));
  const cropH = Math.max(1, Math.ceil((bbox.maxY - bbox.minY) / UNITS_PER_PX));

  const center = {
    x: Math.round((bbox.minX + bbox.maxX) / 2),
    y: Math.round((bbox.minY + bbox.maxY) / 2),
  };

  return {
    imagePath,
    center,
    boundingBox: bbox,
    width: cropW,
    height: cropH,
  };
}
