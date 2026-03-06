#!/usr/bin/env node

/**
 * Image Generation CLI Script
 *
 * Main entry point for image generation with:
 * - Output path safety validation
 * - Retry logic for transient errors
 * - Atomic file writes
 * - Deterministic error codes per cli-contract.md
 *
 * Exit Codes:
 *   0 = SUCCESS
 *   1 = CONFIG_ERROR (missing params, invalid flags, auth issues)
 *   2 = API_ERROR (rate limits, server errors)
 *   3 = FS_ERROR (filesystem issues)
 *
 * @module generate
 */

const fs = require('fs');
const path = require('path');

const openrouter = require('./adapters/openrouter');

// Exit codes matching cli-contract.md
const ExitCodes = {
    SUCCESS: 0,
    CONFIG_ERROR: 1,
    API_ERROR: 2,
    FS_ERROR: 3
};

// Retry configuration
const RETRY_CONFIG = {
    maxAttempts: 3,
    delays: [1000, 2000, 4000] // Exponential backoff: 1s, 2s, 4s
};

// Transient HTTP status codes that should trigger retry
const TRANSIENT_STATUS_CODES = [429, 502, 503];

/**
 * Creates a structured error object following cli-contract.md schema
 *
 * @param {string} code - Error code
 * @param {string} message - Human-readable error message
 * @param {number} statusCode - HTTP-like status code
 * @param {Object} [details={}] - Additional error details
 * @returns {Object} Structured error object
 */
function createError(code, message, statusCode, details = {}) {
    return {
        success: false,
        error: code,
        message: message,
        details: details,
        statusCode: statusCode,
        timestamp: new Date().toISOString()
    };
}

/**
 * Validates that an output path is safe (no directory traversal)
 *
 * Rejects:
 * - Paths containing '..' (directory traversal)
 * - Paths starting with '~' (home directory)
 * - Absolute paths outside current working directory
 * - Paths with null bytes
 *
 * @param {string} outputPath - The path to validate
 * @returns {Object} Validation result { valid: boolean, error?: Object }
 */
function validateOutputPath(outputPath) {
    // Check for null bytes
    if (outputPath.includes('\0')) {
        return {
            valid: false,
            error: createError(
                'CONFIG_ERROR',
                'Output path contains invalid null bytes',
                400,
                { path: outputPath }
            )
        };
    }

    // Reject paths with directory traversal
    if (outputPath.includes('..')) {
        return {
            valid: false,
            error: createError(
                'CONFIG_ERROR',
                'Output path contains directory traversal ("..") which is not allowed',
                400,
                { path: outputPath }
            )
        };
    }

    // Reject paths starting with ~ (home directory)
    if (outputPath.startsWith('~')) {
        return {
            valid: false,
            error: createError(
                'CONFIG_ERROR',
                'Output path cannot start with "~" (home directory)',
                400,
                { path: outputPath }
            )
        };
    }

    // Resolve to absolute path
    const resolvedPath = path.resolve(outputPath);
    const cwd = process.cwd();

    // For absolute paths, ensure they're within cwd
    if (path.isAbsolute(outputPath)) {
        // Check if path is within current working directory
        const relativePath = path.relative(cwd, resolvedPath);
        if (relativePath.startsWith('..') || relativePath === '') {
            return {
                valid: false,
                error: createError(
                    'CONFIG_ERROR',
                    'Absolute output path must be within current working directory',
                    400,
                    { path: outputPath, cwd: cwd }
                )
            };
        }
    }

    return { valid: true, resolvedPath };
}

/**
 * Ensures the parent directory exists, creating it if necessary
 *
 * @param {string} filePath - Path to the file
 * @returns {Object} Result { success: boolean, error?: Object }
 */
function ensureDirectoryExists(filePath) {
    const parentDir = path.dirname(filePath);

    try {
        // Check if directory exists
        const stats = fs.statSync(parentDir);
        if (!stats.isDirectory()) {
            return {
                success: false,
                error: createError(
                    'FS_ERROR',
                    `Parent path exists but is not a directory: ${parentDir}`,
                    500,
                    { path: parentDir }
                )
            };
        }
        return { success: true };
    } catch (error) {
        // Directory doesn't exist, try to create it
        if (error.code === 'ENOENT') {
            try {
                fs.mkdirSync(parentDir, { recursive: true });
                return { success: true };
            } catch (mkdirError) {
                return {
                    success: false,
                    error: createError(
                        'FS_ERROR',
                        `Failed to create output directory: ${mkdirError.message}`,
                        500,
                        { path: parentDir, error: mkdirError.message }
                    )
                };
            }
        }

        return {
            success: false,
            error: createError(
                'FS_ERROR',
                `Failed to access output directory: ${error.message}`,
                500,
                { path: parentDir, error: error.message }
            )
        };
    }
}

/**
 * Writes a file atomically by writing to a temp file and renaming
 *
 * This prevents partial file corruption on crash or failure.
 *
 * @param {string} filePath - Final destination path
 * @param {Buffer} data - File data to write
 * @returns {Object} Result { success: boolean, error?: Object }
 */
function writeFileAtomic(filePath, data) {
    const tempPath = `${filePath}.tmp.${Date.now()}.${process.pid}`;

    try {
        // Write to temp file
        fs.writeFileSync(tempPath, data);

        // Verify temp file was written correctly
        const tempStats = fs.statSync(tempPath);
        if (tempStats.size !== data.length) {
            // Clean up temp file
            try {
                fs.unlinkSync(tempPath);
            } catch {
                // Ignore cleanup errors
            }
            return {
                success: false,
                error: createError(
                    'FS_ERROR',
                    'Temp file size mismatch - partial write detected',
                    500,
                    { expected: data.length, actual: tempStats.size }
                )
            };
        }

        // Atomic rename
        fs.renameSync(tempPath, filePath);

        return { success: true };
    } catch (error) {
        // Clean up temp file on error
        try {
            if (fs.existsSync(tempPath)) {
                fs.unlinkSync(tempPath);
            }
        } catch {
            // Ignore cleanup errors
        }

        return {
            success: false,
            error: createError(
                'FS_ERROR',
                `Failed to write output file: ${error.message}`,
                500,
                { path: filePath, error: error.message }
            )
        };
    }
}

/**
 * Sleeps for the specified number of milliseconds
 *
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise<void>}
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Checks if an error is a transient error that should trigger retry
 *
 * @param {Object} result - The result object from generateImage
 * @returns {boolean} True if the error is transient
 */
function isTransientError(result) {
    if (result.success) {
        return false;
    }

    const statusCode = result.error?.statusCode;
    const errorCode = result.error?.error;

    // Check for transient HTTP status codes
    if (statusCode && TRANSIENT_STATUS_CODES.includes(statusCode)) {
        return true;
    }

    // Check for network errors (typically connection issues)
    if (errorCode === 'NETWORK_ERROR') {
        return true;
    }

    // Check for rate limit or timeout indicators in message
    const message = result.error?.message || '';
    const transientIndicators = [
        'rate limit',
        'rate-limit',
        'too many requests',
        'timeout',
        'temporary',
        'unavailable',
        'overloaded'
    ];

    return transientIndicators.some(indicator =>
        message.toLowerCase().includes(indicator)
    );
}

/**
 * @param {string} apiKey - OpenRouter API key
 * @param {string} imageToImageModel - Image-to-image model ID
 * @param {string} textToImageModel - Text-to-image model ID
 * @param {string} prompt - Generation prompt
 * @param {string} [size] - Image size
 * @param {string} [aspectRatio] - Aspect ratio
 * @param {string} [inputImagePath] - Path to input image for i2i
 * @returns {Promise<Object>} Result with success flag and data or error
 */
async function generateImageWithRetry(apiKey, imageToImageModel, textToImageModel, prompt, size, aspectRatio, inputImagePath) {
    let lastResult = null;
    let inputImageBase64 = null;

    if (inputImagePath) {
        try {
            const imageBuffer = fs.readFileSync(inputImagePath);
            inputImageBase64 = imageBuffer.toString('base64');
        } catch (error) {
            return {
                success: false,
                error: createError(
                    'FS_ERROR',
                    `Failed to read input image: ${error.message}`,
                    400,
                    { path: inputImagePath }
                )
            };
        }
    }

    for (let attempt = 1; attempt <= RETRY_CONFIG.maxAttempts; attempt++) {
        const result = await openrouter.generateImage(
            apiKey,
            imageToImageModel,
            textToImageModel,
            prompt,
            size,
            aspectRatio,
            inputImageBase64
        );

        if (result.success) {
            return result;
        }

        lastResult = result;

        // Check if this is a transient error that should be retried
        if (isTransientError(result) && attempt < RETRY_CONFIG.maxAttempts) {
            const delay = RETRY_CONFIG.delays[attempt - 1] || 4000;
            console.error(JSON.stringify({
                warning: 'Transient error, retrying',
                attempt: attempt,
                maxAttempts: RETRY_CONFIG.maxAttempts,
                delayMs: delay,
                error: result.error?.message,
                timestamp: new Date().toISOString()
            }));
            await sleep(delay);
            continue;
        }

        // Non-transient error or max attempts reached
        break;
    }

    // Add retry information to final error
    if (lastResult && !lastResult.success) {
        lastResult.error.details = {
            ...lastResult.error.details,
            retryAttempts: RETRY_CONFIG.maxAttempts
        };
    }

    return lastResult;
}

/**
 * Maps error codes to exit codes per cli-contract.md
 *
 * @param {Object} errorResult - The error result from generateImage
 * @returns {number} Exit code
 */
function mapErrorToExitCode(errorResult) {
    const errorCode = errorResult.error?.error;

    switch (errorCode) {
        case 'CONFIG_ERROR':
            return ExitCodes.CONFIG_ERROR;
        case 'API_ERROR':
        case 'NETWORK_ERROR':
            return ExitCodes.API_ERROR;
        case 'FS_ERROR':
        case 'PARSE_ERROR':
            return ExitCodes.FS_ERROR;
        default:
            // Default to API_ERROR for unknown errors
            return ExitCodes.API_ERROR;
    }
}

/**
 * Parses CLI arguments into a map
 *
 * @param {string[]} args - Process arguments
 * @returns {Object} Parsed arguments map
 */
function parseArgs(args) {
    const argMap = {};
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg.startsWith('--')) {
            const key = arg.replace(/^--/, '');
            const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
            argMap[key] = value;
            if (value !== true) i++;
        }
    }
    return argMap;
}

/**
 * Main execution function
 *
 * @returns {Promise<number>} Exit code
 */
async function main() {
    const args = process.argv.slice(2);
    const argMap = parseArgs(args);

    // Handle help flag
    if (argMap.help || argMap.h) {
        console.log('Image Generation CLI');
        console.log('');
        console.log('Usage: node generate.js [options]');
        console.log('');
        console.log('Options:');
        console.log('  --prompt <text>     Image generation prompt (required)');
        console.log('  --model <id>        Text-to-Image Model ID (env: IMAGE_GEN_TEXT_TO_IMAGE_MODEL, default: bytedance-seed/seedream-4.5)');
        console.log('  --i2i-model <id>    Image-to-Image Model ID (env: IMAGE_GEN_IMAGE_TO_IMAGE_MODEL, default: google/gemini-2.5-flash-image)');
        console.log('  --input-image <path> Input image file for image-to-image');
        console.log('  --size <1K|2K|4K>  Image resolution tier (default: model default)');
        console.log('  --aspect <ratio>    Aspect ratio (e.g., 1:1)');
        console.log('  --output <path>     Output file path (default: .sisyphus/generated/image_<timestamp>.png)');
        console.log('  --help              Show this help');
        console.log('');
        console.log('Exit Codes:');
        console.log('  0  SUCCESS');
        console.log('  1  CONFIG_ERROR (missing params, invalid flags, auth)');
        console.log('  2  API_ERROR (rate limits, server errors)');
        console.log('  3  FS_ERROR (filesystem issues)');
        console.log('');
        console.log('Environment Variables:');
        console.log('  OPENROUTER_API_KEY  Required API key for OpenRouter');
        console.log('');
        console.log('Examples:');
        console.log('  node generate.js --prompt "a sunset over mountains"');
        console.log('  node generate.js --prompt "a cat" --output ./images/cat.png');
        console.log('  node generate.js --prompt "a city" --size 2K --aspect 16:9');
        return ExitCodes.SUCCESS;
    }

    // Validate required parameters
    if (!argMap.prompt) {
        const error = createError(
            'CONFIG_ERROR',
            'The --prompt argument is required. Use --help for usage information.',
            400,
            { field: 'prompt' }
        );
        console.error(JSON.stringify(error, null, 2));
        return ExitCodes.CONFIG_ERROR;
    }

    const apiKey = process.env.OPENROUTER_API_KEY;
    if (!apiKey) {
        const error = createError(
            'CONFIG_ERROR',
            'Missing OPENROUTER_API_KEY environment variable.',
            401
        );
        console.error(JSON.stringify(error, null, 2));
        return ExitCodes.CONFIG_ERROR;
    }

    // Determine output path
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const defaultOutput = path.join('.sisyphus', 'generated', `image_${timestamp}.png`);
    const outputPath = argMap.output || defaultOutput;

    // Validate output path safety
    const pathValidation = validateOutputPath(outputPath);
    if (!pathValidation.valid) {
        console.error(JSON.stringify(pathValidation.error, null, 2));
        return ExitCodes.CONFIG_ERROR;
    }

    const resolvedOutputPath = pathValidation.resolvedPath;

    // Ensure parent directory exists
    const dirResult = ensureDirectoryExists(resolvedOutputPath);
    if (!dirResult.success) {
        console.error(JSON.stringify(dirResult.error, null, 2));
        return ExitCodes.FS_ERROR;
    }

    // Generate image with retry logic
    const result = await generateImageWithRetry(
        apiKey,
        argMap['i2i-model'],
        argMap.model,
        argMap.prompt,
        argMap.size,
        argMap.aspect,
        argMap['input-image']
    );

    if (!result.success) {
        const exitCode = mapErrorToExitCode(result);
        console.error(JSON.stringify(result.error, null, 2));
        return exitCode;
    }

    // Extract and decode base64 image
    let imageData;
    try {
        const base64Data = result.data.imageUrl.replace(/^data:image\/\w+;base64,/, '');
        imageData = Buffer.from(base64Data, 'base64');
    } catch (error) {
        const fsError = createError(
            'FS_ERROR',
            `Failed to decode image data: ${error.message}`,
            500,
            { error: error.message }
        );
        console.error(JSON.stringify(fsError, null, 2));
        return ExitCodes.FS_ERROR;
    }

    // Write image file atomically
    const writeResult = writeFileAtomic(resolvedOutputPath, imageData);
    if (!writeResult.success) {
        console.error(JSON.stringify(writeResult.error, null, 2));
        return ExitCodes.FS_ERROR;
    }

    // Success output
    const successOutput = {
        success: true,
        data: {
            outputPath: resolvedOutputPath,
            model: result.data.model,
            usage: result.data.usage
        },
        message: 'Image generated successfully',
        timestamp: new Date().toISOString()
    };

    console.log(JSON.stringify(successOutput, null, 2));
    return ExitCodes.SUCCESS;
}

// Execute main function
main().then(exitCode => {
    process.exit(exitCode);
}).catch(error => {
    const unexpectedError = createError(
        'API_ERROR',
        `Unexpected error: ${error.message}`,
        500,
        { stack: error.stack }
    );
    console.error(JSON.stringify(unexpectedError, null, 2));
    process.exit(ExitCodes.API_ERROR);
});
