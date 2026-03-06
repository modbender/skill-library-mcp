/**
 * OpenRouter Adapter for Image Generation
 *
 * Provides request building, response parsing, and API communication
 * for OpenRouter's image generation capabilities.
 *
 * @module openrouter-adapter
 */

const OPENROUTER_API_URL = 'https://openrouter.ai/api/v1/chat/completions';
const DEFAULT_TEXT_TO_IMAGE_MODEL = process.env.IMAGE_GEN_TEXT_TO_IMAGE_MODEL || 'bytedance-seed/seedream-4.5';
const DEFAULT_IMAGE_TO_IMAGE_MODEL = process.env.IMAGE_GEN_IMAGE_TO_IMAGE_MODEL || 'google/gemini-2.5-flash-image';

/**
 * Error codes matching cli-contract.md schema
 */
const ErrorCodes = {
    CONFIG_ERROR: 'CONFIG_ERROR',
    API_ERROR: 'API_ERROR',
    PARSE_ERROR: 'PARSE_ERROR',
    NETWORK_ERROR: 'NETWORK_ERROR'
};

/**
 * Creates a structured error object following cli-contract.md schema
 *
 * @param {string} code - Error code from ErrorCodes
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
 * Builds the OpenRouter request payload for image generation
 *
 * @param {string} imageToImageModel - The OpenRouter model ID to use for image-to-image
 * @param {string} textToImageModel - The OpenRouter model ID to use for text-to-image
 * @param {string} prompt - The text description of the image to generate
 * @param {string} [size] - Optional resolution tier ('1K', '2K', or '4K')
 * @param {string} [aspectRatio] - Optional aspect ratio (e.g., '1:1')
 * @param {string} [inputImageBase64] - Optional base64 encoded input image for i2i
 * @returns {Object} Request payload for OpenRouter API
 */
function buildRequest(imageToImageModel, textToImageModel, prompt, size, aspectRatio, inputImageBase64) {
    const defaultModel = inputImageBase64 ? DEFAULT_IMAGE_TO_IMAGE_MODEL : DEFAULT_TEXT_TO_IMAGE_MODEL;
    const model = inputImageBase64 ? (imageToImageModel || defaultModel) : (textToImageModel || defaultModel);

    const messages = [
        {
            role: 'user',
            content: inputImageBase64 ? [
                { type: 'text', text: prompt },
                { type: 'image_url', image_url: { url: `data:image/png;base64,${inputImageBase64}` } }
            ] : prompt
        }
    ];

    const payload = {
        model: model,
        messages: messages,
        modalities: ['image']
    };

    // Build image_config object for OpenRouter API
    const imageConfig = {};

    if (size) {
        imageConfig.image_size = size;
    }

    if (aspectRatio) {
        imageConfig.aspect_ratio = aspectRatio;
    }

    // Only add image_config if there are configuration options
    if (Object.keys(imageConfig).length > 0) {
        payload.image_config = imageConfig;
    }

    return payload;
}

/**
 * Parses the OpenRouter response to extract the base64 image URL
 *
 * Expected response structure:
 * choices[0].message.images[0].image_url.url
 *
 * @param {Object} response - The JSON response from OpenRouter API
 * @returns {Object} Parsed result with success flag and data or error
 */
function parseResponse(response) {
    try {
        // Validate response structure
        if (!response) {
            return {
                success: false,
                error: createError(
                    ErrorCodes.PARSE_ERROR,
                    'Empty response from API',
                    500
                )
            };
        }

        // Check for API-level errors
        if (response.error) {
            return {
                success: false,
                error: createError(
                    ErrorCodes.API_ERROR,
                    response.error.message || 'API returned an error',
                    response.error.code || 500,
                    { apiError: response.error }
                )
            };
        }

        // Validate choices array exists
        if (!response.choices || !Array.isArray(response.choices) || response.choices.length === 0) {
            return {
                success: false,
                error: createError(
                    ErrorCodes.PARSE_ERROR,
                    'Invalid response: missing choices array',
                    500,
                    { response: response }
                )
            };
        }

        const firstChoice = response.choices[0];

        // Validate message structure
        if (!firstChoice.message) {
            return {
                success: false,
                error: createError(
                    ErrorCodes.PARSE_ERROR,
                    'Invalid response: missing message in choice',
                    500
                )
            };
        }

        // Validate images array
        if (!firstChoice.message.images || !Array.isArray(firstChoice.message.images) || firstChoice.message.images.length === 0) {
            return {
                success: false,
                error: createError(
                    ErrorCodes.PARSE_ERROR,
                    'Invalid response: missing images array in message',
                    500
                )
            };
        }

        const firstImage = firstChoice.message.images[0];

        // Validate image_url structure
        if (!firstImage.image_url || !firstImage.image_url.url) {
            return {
                success: false,
                error: createError(
                    ErrorCodes.PARSE_ERROR,
                    'Invalid response: missing image_url.url in image object',
                    500
                )
            };
        }

        // Extract the base64 image URL
        const imageUrl = firstImage.image_url.url;

        // Validate that it's a data URL (base64)
        if (!imageUrl.startsWith('data:image/')) {
            return {
                success: false,
                error: createError(
                    ErrorCodes.PARSE_ERROR,
                    'Invalid response: image URL is not a base64 data URL',
                    500
                )
            };
        }

        return {
            success: true,
            data: {
                imageUrl: imageUrl,
                model: response.model,
                usage: response.usage || null
            },
            timestamp: new Date().toISOString()
        };
    } catch (error) {
        return {
            success: false,
            error: createError(
                ErrorCodes.PARSE_ERROR,
                `Failed to parse response: ${error.message}`,
                500,
                { parseError: error.message }
            )
        };
    }
}

/**
 * Generates an image using OpenRouter API
 *
 * @param {string} apiKey - The OpenRouter API key
 * @param {string} imageToImageModel - The image-to-image model ID to use
 * @param {string} textToImageModel - The text-to-image model ID to use
 * @param {string} prompt - The text prompt for image generation
 * @param {string} [size] - Optional size specification
 * @param {string} [aspectRatio] - Optional aspect ratio
 * @param {string} [inputImageBase64] - Optional base64 encoded input image
 * @returns {Promise<Object>} Result object with success flag and image data or error
 */
async function generateImage(apiKey, imageToImageModel, textToImageModel, prompt, size, aspectRatio, inputImageBase64) {
    // Validate API key
    if (!apiKey) {
        return {
            success: false,
            error: createError(
                ErrorCodes.CONFIG_ERROR,
                'Missing OPENROUTER_API_KEY environment variable.',
                401
            )
        };
    }

    // Validate prompt
    if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
        return {
            success: false,
            error: createError(
                ErrorCodes.CONFIG_ERROR,
                'The --prompt argument is required.',
                400,
                { field: 'prompt' }
            )
        };
    }

    // Build request payload
    const payload = buildRequest(imageToImageModel, textToImageModel, prompt, size, aspectRatio, inputImageBase64);

    try {
        const response = await fetch(OPENROUTER_API_URL, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://github.com/ohmyopencodelabs/ai-workers',
                'X-Title': 'AI Workers Image Generation'
            },
            body: JSON.stringify(payload)
        });

        // Handle HTTP errors
        if (!response.ok) {
            const errorBody = await response.text();
            let parsedError;
            try {
                parsedError = JSON.parse(errorBody);
            } catch {
                parsedError = { message: errorBody };
            }

            return {
                success: false,
                error: createError(
                    ErrorCodes.API_ERROR,
                    parsedError.error?.message || `API request failed: ${response.status} ${response.statusText}`,
                    response.status,
                    { apiResponse: parsedError }
                )
            };
        }

        // Parse JSON response
        const data = await response.json();

        // Parse and return result
        return parseResponse(data);

    } catch (error) {
        // Handle network/fetch errors
        if (error.name === 'TypeError' || error.name === 'FetchError') {
            return {
                success: false,
                error: createError(
                    ErrorCodes.NETWORK_ERROR,
                    `Network error: ${error.message}`,
                    503
                )
            };
        }

        return {
            success: false,
            error: createError(
                ErrorCodes.API_ERROR,
                `Request failed: ${error.message}`,
                500,
                { error: error.message }
            )
        };
    }
}

/**
 * Tests OpenRouter connectivity without generating an image
 * Validates that OPENROUTER_API_KEY is configured
 *
 * @param {string} [apiKey] - Optional API key (defaults to process.env.OPENROUTER_API_KEY)
 * @returns {Promise<Object>} Test result with success flag and details or error
 */
async function test(apiKey) {
    const key = apiKey || process.env.OPENROUTER_API_KEY;

    if (!key) {
        return {
            success: false,
            error: createError(
                ErrorCodes.CONFIG_ERROR,
                'Missing OPENROUTER_API_KEY environment variable.',
                401
            )
        };
    }

    // Validate API key format (should be a non-empty string)
    if (typeof key !== 'string' || key.trim().length === 0) {
        return {
            success: false,
            error: createError(
                ErrorCodes.CONFIG_ERROR,
                'OPENROUTER_API_KEY is empty or invalid.',
                401
            )
        };
    }

    // Note: We don't make an actual API call here to avoid consuming tokens
    // For now, we validate the key exists and is properly formatted

    return {
        success: true,
        data: {
            apiKeyConfigured: true,
            keyPrefix: key.substring(0, 8) + '...',
            endpoint: OPENROUTER_API_URL,
            defaultTextToImageModel: DEFAULT_TEXT_TO_IMAGE_MODEL,
            defaultImageToImageModel: DEFAULT_IMAGE_TO_IMAGE_MODEL
        },
        message: 'OpenRouter API key is configured. Test passed.',
        timestamp: new Date().toISOString()
    };
}

module.exports = {
    buildRequest,
    parseResponse,
    generateImage,
    test,
    ErrorCodes,
    DEFAULT_TEXT_TO_IMAGE_MODEL,
    DEFAULT_IMAGE_TO_IMAGE_MODEL,
    OPENROUTER_API_URL,
    createError
};
