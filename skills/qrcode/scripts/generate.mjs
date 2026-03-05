#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import QRCode from 'qrcode';
import sharp from 'sharp';

// Constants
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const WORKSPACE_ROOT = path.resolve(__dirname, '../../..');

const LIMITS = {
    TEXT: 4096,
    SIZE: 10000,
    SCALE: 10,
    MARGIN: 100,
    QUALITY: { MIN: 1, MAX: 100 },
    SVG_BUFFER: 100 * 1024 * 1024
};

const ALLOWED = {
    EXTENSIONS: ['.svg', '.png', '.jpg', '.jpeg'],
    FORMATS: ['svg', 'png', 'jpg', 'jpeg'],
    DOT_STYLES: ['square', 'circle'],
    EYE_STYLES: ['square', 'circle', 'rounded'],
    EC_LEVELS: ['L', 'M', 'Q', 'H']
};

const SYSTEM_PATHS = ['/etc', '/bin', '/sbin', '/usr/bin', '/usr/sbin', '/System', 'C:\\Windows', 'C:\\Program Files'];

// Utility functions
const exitError = (msg) => { console.error(msg); process.exit(1); };

const usage = () => exitError(
    `Usage: generate.mjs "text" [-o out.svg|out.png|out.jpg] [--format svg|png|jpg] [--size 1024] [--scale 1] [--margin 4] [--dot square|circle] [--eye square|circle|rounded] [--color #000000] [--background #ffffff] [--transparent] [--ec L|M|Q|H] [--quality 80]\n\nNote: Output files are saved to workspace root: ${WORKSPACE_ROOT}`
);

/**
 * Normalize path for cross-platform comparison
 * Handles Windows case-insensitivity and path separators
 * @param {string} p - Path to normalize
 * @returns {string} - Normalized path
 */
const normalizePath = (p) => {
    const normalized = path.resolve(p);
    return process.platform === 'win32' ? normalized.toLowerCase() : normalized;
};

/**
 * Check if path is within allowed directory (cross-platform safe)
 * @param {string} targetPath - Path to check
 * @param {string} allowedDir - Allowed parent directory
 * @returns {boolean} - True if path is within allowed directory
 */
const isPathWithinDirectory = (targetPath, allowedDir) => {
    const normalizedTarget = normalizePath(targetPath);
    const normalizedAllowed = normalizePath(allowedDir);
    return normalizedTarget === normalizedAllowed ||
        normalizedTarget.startsWith(normalizedAllowed + path.sep);
};

// Validation functions
const validate = {
    text: (text) => {
        if (typeof text !== 'string' || !text) exitError('Error: Text must be a non-empty string');
        if (text.length > LIMITS.TEXT) exitError(`Error: Text too long (max ${LIMITS.TEXT} characters)`);
        return text;
    },

    number: (value, min, max, name) => {
        const num = Number(value);
        if (!isFinite(num) || num < min || num > max) {
            exitError(`Error: ${name} must be between ${min} and ${max}`);
        }
        return num;
    },

    enum: (value, allowed, name) => {
        if (typeof value !== 'string' || !allowed.includes(value)) {
            exitError(`Error: ${name} must be one of: ${allowed.join(', ')}`);
        }
        return value;
    },

    color: (color) => {
        if (typeof color !== 'string' || !/^#[0-9A-Fa-f]{6}$/.test(color)) {
            exitError(`Invalid color format: ${color}. Use hex format like #000000`);
        }
        return color;
    }
};

/**
 * Sanitize and validate output file path
 * Prevents path traversal attacks and ensures file is written within workspace root only
 * @param {string} outputPath - User-provided output path
 * @returns {string} - Sanitized absolute path in workspace root
 */
const sanitizeOutputPath = (outputPath) => {
    if (!outputPath) return null;

    // Check type safety
    if (typeof outputPath !== 'string') exitError('Security Error: Invalid path type');

    // Check for null bytes (directory traversal attack vector)
    if (outputPath.includes('\0')) exitError('Security Error: Null bytes detected in path');

    // Extract only the filename, ignore any directory path provided by user
    const basename = path.basename(outputPath);

    // Verify basename doesn't contain path separators (defensive check)
    if (!basename || basename === '.' || basename === '..' ||
        basename.includes('/') || basename.includes('\\')) {
        exitError('Security Error: Invalid filename');
    }

    // Resolve to absolute path in workspace root directory
    const resolvedPath = path.resolve(WORKSPACE_ROOT, basename);

    // Verify resolved path is within workspace root
    if (!isPathWithinDirectory(resolvedPath, WORKSPACE_ROOT)) {
        exitError(`Security Error: Output path must be within workspace root\nAttempted: ${resolvedPath}\nAllowed: ${WORKSPACE_ROOT}`);
    }

    // Secondary verification: ensure no directory traversal
    const relativePath = path.relative(WORKSPACE_ROOT, resolvedPath);
    if (relativePath.startsWith('..') || path.isAbsolute(relativePath)) {
        exitError('Security Error: Path traversal detected');
    }

    // Validate file extension against whitelist
    const ext = path.extname(resolvedPath).toLowerCase();
    if (!ALLOWED.EXTENSIONS.includes(ext)) {
        exitError(`Security Error: Invalid file extension. Allowed: ${ALLOWED.EXTENSIONS.join(', ')}`);
    }

    // Check for dangerous characters (including shell metacharacters)
    if (/[<>:"|?*\x00-\x1f$`\\;()&]/.test(basename)) {
        exitError('Security Error: Invalid characters in filename');
    }

    // Prevent overwriting system files
    for (const sysPath of SYSTEM_PATHS) {
        if (isPathWithinDirectory(resolvedPath, sysPath)) {
            exitError('Security Error: Cannot write to system directories');
        }
    }

    return resolvedPath;
};

/**
 * Safely write file with symlink protection and atomic operation
 * Prevents TOCTOU attacks and symlink attacks
 * @param {string} filePath - Target file path (must be already sanitized)
 * @param {string|Buffer} content - Content to write
 * @param {string} encoding - File encoding ('utf8' for text, null for binary)
 */
const safeWriteFile = (filePath, content, encoding = 'utf8') => {
    // Check if existing file is a symbolic link
    if (fs.existsSync(filePath)) {
        try {
            const stats = fs.lstatSync(filePath);
            if (stats.isSymbolicLink()) {
                exitError(`Security Error: Refusing to overwrite symbolic link: ${filePath}`);
            }

            // Resolve real path and verify it's within workspace
            const realPath = fs.realpathSync(filePath);
            if (!isPathWithinDirectory(realPath, WORKSPACE_ROOT)) {
                exitError('Security Error: Target file points outside workspace');
            }
        } catch (err) {
            if (err.code !== 'ENOENT') exitError(`Error checking file: ${err.message}`);
        }
    }

    const tempFile = `${filePath}.tmp.${process.pid}`;

    try {
        // Write to temp file with restrictive permissions
        const options = encoding ? { encoding, mode: 0o644 } : { mode: 0o644 };
        fs.writeFileSync(tempFile, content, options);

        // Verify temp file is not a symlink (defense in depth)
        const tempStats = fs.lstatSync(tempFile);
        if (tempStats.isSymbolicLink()) {
            fs.unlinkSync(tempFile);
            exitError('Security Error: Temp file became a symlink');
        }

        // Atomic rename operation
        fs.renameSync(tempFile, filePath);
    } catch (err) {
        // Clean up temp file on error
        try {
            if (fs.existsSync(tempFile)) fs.unlinkSync(tempFile);
        } catch { }
        throw err;
    }
};

/**
 * Generate default filename based on text content and format
 * @param {string} text - QR code text content
 * @param {string} format - Output format
 * @returns {string} - Generated filename
 */
const generateDefaultFilename = (text, format) => {
    const safeText = text.substring(0, 30)
        .replace(/[^a-zA-Z0-9]/g, '_')
        .replace(/_+/g, '_')
        .replace(/^_|_$/g, '') || 'qrcode';
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
    return `qrcode_${safeText}_${timestamp}.${format === 'jpg' ? 'jpg' : format}`;
};

// Parse command line arguments
const argv = process.argv.slice(2);
if (!argv.length || argv[0] === '-h' || argv[0] === '--help') usage();

const config = {
    text: validate.text(argv[0]),
    out: null,
    size: 1024,
    scale: 1,
    margin: 4,
    dot: 'square',
    eye: 'square',
    color: '#000000',
    background: '#ffffff',
    ec: 'M',
    format: 'svg',
    quality: 80,
    transparent: false
};

// Argument handlers with strict validation
const argHandlers = {
    '-o': (v) => { if (typeof v !== 'string') exitError('Error: -o requires string value'); config.out = v; },
    '--out': (v) => { if (typeof v !== 'string') exitError('Error: --out requires string value'); config.out = v; },
    '--size': (v) => config.size = validate.number(v, 1, LIMITS.SIZE, 'size'),
    '--scale': (v) => config.scale = validate.number(v, 0.1, LIMITS.SCALE, 'scale'),
    '--margin': (v) => config.margin = validate.number(v, 0, LIMITS.MARGIN, 'margin'),
    '--quiet': (v) => config.margin = validate.number(v, 0, LIMITS.MARGIN, 'margin'),
    '--dot': (v) => config.dot = validate.enum(v, ALLOWED.DOT_STYLES, 'dot'),
    '--eye': (v) => config.eye = validate.enum(v, ALLOWED.EYE_STYLES, 'eye'),
    '--color': (v) => config.color = validate.color(v),
    '--background': (v) => config.background = validate.color(v),
    '--ec': (v) => config.ec = validate.enum(v.toUpperCase(), ALLOWED.EC_LEVELS, 'ec'),
    '--format': (v) => config.format = validate.enum(v.toLowerCase(), ALLOWED.FORMATS, 'format'),
    '--quality': (v) => config.quality = validate.number(v, LIMITS.QUALITY.MIN, LIMITS.QUALITY.MAX, 'quality'),
    '--transparent': () => config.transparent = true
};

// Parse arguments with security checks
for (let i = 1; i < argv.length; i++) {
    const arg = argv[i];
    if (typeof arg !== 'string') exitError('Error: Invalid argument type');

    const handler = argHandlers[arg];
    if (!handler) exitError(`Unknown argument: ${arg}`);

    if (arg !== '--transparent') {
        if (++i >= argv.length) exitError(`Error: ${arg} requires a value`);
        handler(argv[i]);
    } else {
        handler();
    }
}

// Normalize format and set output path
if (config.format === 'jpeg') config.format = 'jpg';
if (!config.out) {
    config.out = generateDefaultFilename(config.text, config.format);
    console.log(`No output file specified, using: ${config.out}`);
}
config.out = sanitizeOutputPath(config.out);
console.log(`Output will be saved to: ${config.out}`);

// Final verification: ensure output path is in workspace root (not in subdirectory)
const outputDir = path.dirname(config.out);
if (normalizePath(outputDir) !== normalizePath(WORKSPACE_ROOT)) {
    exitError(`Security Error: Output must be in workspace root directory\nOutput dir: ${outputDir}\nWorkspace: ${WORKSPACE_ROOT}`);
}

// Generate QR code matrix
let qr, modules, moduleCount;
try {
    qr = QRCode.create(config.text, { errorCorrectionLevel: config.ec });
    modules = qr.modules;
    moduleCount = modules.size;
    if (!modules || moduleCount <= 0) throw new Error('Invalid QR code generated');
} catch (err) {
    exitError(`Error creating QR code: ${err.message}`);
}

/**
 * Get module value at specific coordinates
 * @param {number} x - X coordinate
 * @param {number} y - Y coordinate
 * @returns {boolean} - True if module is dark
 */
const getModule = (x, y) => {
    if (!modules || x < 0 || x >= moduleCount || y < 0 || y >= moduleCount) return false;
    if (typeof modules.get === 'function') return modules.get(x, y);
    return !!(Array.isArray(modules.data) && modules.data[y] && modules.data[y][x]);
};

// Calculate dimensions with overflow protection
const targetSize = Math.max(1, Math.min(LIMITS.SIZE * LIMITS.SCALE, Math.floor(config.size * config.scale)));
const cellSize = Math.floor(targetSize / (moduleCount + config.margin * 2)) || 1;
const svgSize = cellSize * (moduleCount + config.margin * 2);
const offset = config.margin * cellSize;

// Validate computed sizes to prevent resource exhaustion
if (svgSize > LIMITS.SIZE * LIMITS.SCALE) {
    exitError(`Error: Computed size too large (${svgSize}px). Reduce size, scale, or margin.`);
}

/**
 * Check if coordinates are within finder pattern areas
 * Finder patterns are 7x7 blocks at three corners
 * @param {number} x - X coordinate
 * @param {number} y - Y coordinate
 * @returns {boolean} - True if within finder pattern
 */
const inFinder = (x, y) =>
    (x < 7 && y < 7) ||
    (x >= moduleCount - 7 && y < 7) ||
    (x < 7 && y >= moduleCount - 7);

/**
 * Escape XML special characters to prevent injection
 * @param {string} str - String to escape
 * @returns {string} - Escaped string
 */
const escapeXml = (str) => String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');

// Build SVG with proper escaping
const svg = [
    `<?xml version="1.0" encoding="utf-8"?>`,
    `<svg xmlns="http://www.w3.org/2000/svg" width="${svgSize}" height="${svgSize}" viewBox="0 0 ${svgSize} ${svgSize}">`,
    `<rect width="100%" height="100%" fill="${config.transparent ? 'none' : escapeXml(config.background)}"/>`
];

const safeColor = escapeXml(config.color);
const safeBg = config.transparent ? 'none' : escapeXml(config.background);

// Draw data modules (skip finder pattern areas)
for (let row = 0; row < moduleCount; row++) {
    for (let col = 0; col < moduleCount; col++) {
        if (!getModule(col, row) || inFinder(col, row)) continue;

        const x = offset + col * cellSize;
        const y = offset + row * cellSize;

        svg.push(config.dot === 'circle'
            ? `<circle cx="${x + cellSize / 2}" cy="${y + cellSize / 2}" r="${cellSize * 0.45}" fill="${safeColor}"/>`
            : `<rect x="${x}" y="${y}" width="${cellSize}" height="${cellSize}" fill="${safeColor}"/>`
        );
    }
}

// Draw finder patterns (eyes) at three corners
const eyes = [[0, 0], [moduleCount - 7, 0], [0, moduleCount - 7]];
for (const [fx, fy] of eyes) {
    const x = offset + fx * cellSize;
    const y = offset + fy * cellSize;
    const w = 7 * cellSize;

    if (config.eye === 'circle') {
        const cx = x + 3.5 * cellSize;
        const cy = y + 3.5 * cellSize;
        svg.push(
            `<circle cx="${cx}" cy="${cy}" r="${3.5 * cellSize}" fill="${safeColor}"/>`,
            `<circle cx="${cx}" cy="${cy}" r="${2.5 * cellSize}" fill="${safeBg}"/>`,
            `<circle cx="${cx}" cy="${cy}" r="${1.1 * cellSize}" fill="${safeColor}"/>`
        );
    } else if (config.eye === 'rounded') {
        const rx = cellSize * 1.2;
        svg.push(
            `<rect x="${x}" y="${y}" width="${w}" height="${w}" rx="${rx}" ry="${rx}" fill="${safeColor}"/>`,
            `<rect x="${x + cellSize}" y="${y + cellSize}" width="${5 * cellSize}" height="${5 * cellSize}" rx="${cellSize}" ry="${cellSize}" fill="${safeBg}"/>`,
            `<rect x="${x + 2 * cellSize}" y="${y + 2 * cellSize}" width="${3 * cellSize}" height="${3 * cellSize}" rx="${cellSize * 0.5}" ry="${cellSize * 0.5}" fill="${safeColor}"/>`
        );
    } else {
        svg.push(
            `<rect x="${x}" y="${y}" width="${w}" height="${w}" fill="${safeColor}"/>`,
            `<rect x="${x + cellSize}" y="${y + cellSize}" width="${5 * cellSize}" height="${5 * cellSize}" fill="${safeBg}"/>`,
            `<rect x="${x + 2 * cellSize}" y="${y + 2 * cellSize}" width="${3 * cellSize}" height="${3 * cellSize}" fill="${safeColor}"/>`
        );
    }
}

svg.push('</svg>');
const outSvg = svg.join('\n');

/**
 * Produce final output in requested format
 * Handles SVG, PNG, and JPEG formats with proper error handling
 */
(async () => {
    try {
        if (config.format === 'svg') {
            safeWriteFile(config.out, outSvg, 'utf8');
            console.log(`✓ Successfully wrote ${config.out}`);
            return;
        }

        const svgBuffer = Buffer.from(outSvg, 'utf8');

        // Validate buffer size to prevent memory exhaustion
        if (svgBuffer.length > LIMITS.SVG_BUFFER) exitError('Error: Generated SVG too large');

        let image = sharp(svgBuffer, {
            density: 72,
            limitInputPixels: LIMITS.SIZE * LIMITS.SIZE * LIMITS.SCALE * LIMITS.SCALE
        }).resize(svgSize, svgSize, { fit: 'contain' });

        if (config.format === 'png') {
            image = image.png({
                compressionLevel: 9,
                ...(config.transparent ? {} : { background: { r: 255, g: 255, b: 255 } })
            });
        } else if (config.format === 'jpg') {
            const bg = config.transparent ? '#ffffff' : config.background;
            image = image.flatten({ background: bg }).jpeg({ quality: config.quality });
        }

        const buffer = await image.toBuffer();
        safeWriteFile(config.out, buffer, null);
        console.log(`✓ Successfully wrote ${config.out}`);
    } catch (err) {
        const tempFile = `${config.out}.tmp.${process.pid}`;
        try { if (fs.existsSync(tempFile)) fs.unlinkSync(tempFile); } catch { }
        exitError(`Error producing output: ${err.message || err}`);
    }
})();
