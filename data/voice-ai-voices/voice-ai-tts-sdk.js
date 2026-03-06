/**
 * Voice.ai Text-to-Speech SDK
 * 
 * A comprehensive JavaScript/Node.js SDK for Voice.ai's TTS API.
 * Supports speech generation, streaming, and voice management.
 * 
 * @version 1.1.5
 * @author Nick Gill (https://github.com/gizmoGremlin)
 * @license MIT
 * @see https://voice.ai/docs
 * 
 * @example
 * const VoiceAI = require('./voice-ai-tts-sdk');
 * const client = new VoiceAI('your-api-key');
 * 
 * // List voices
 * const voices = await client.listVoices({ limit: 10 });
 * 
 * // Generate speech
 * const audio = await client.generateSpeech({
 *   text: 'Hello, world!',
 *   voice_id: 'abc123'
 * });
 */

const https = require('https');
const fs = require('fs');
const { URL } = require('url');

// ============================================================================
// Constants
// ============================================================================

// Official Voice.ai production API endpoint (dev.voice.ai is the production domain).
const BASE_URL = 'https://dev.voice.ai';
const API_VERSION = 'v1';

const AUDIO_FORMATS = {
  // Basic formats (32kHz)
  MP3: 'mp3',
  WAV: 'wav',
  PCM: 'pcm',
  
  // Telephony
  ALAW_8000: 'alaw_8000',
  ULAW_8000: 'ulaw_8000',
  
  // MP3 variants
  MP3_22050_32: 'mp3_22050_32',
  MP3_24000_48: 'mp3_24000_48',
  MP3_44100_32: 'mp3_44100_32',
  MP3_44100_64: 'mp3_44100_64',
  MP3_44100_96: 'mp3_44100_96',
  MP3_44100_128: 'mp3_44100_128',
  MP3_44100_192: 'mp3_44100_192',
  
  // Opus variants
  OPUS_48000_32: 'opus_48000_32',
  OPUS_48000_64: 'opus_48000_64',
  OPUS_48000_96: 'opus_48000_96',
  OPUS_48000_128: 'opus_48000_128',
  OPUS_48000_192: 'opus_48000_192',
  
  // PCM variants
  PCM_8000: 'pcm_8000',
  PCM_16000: 'pcm_16000',
  PCM_22050: 'pcm_22050',
  PCM_24000: 'pcm_24000',
  PCM_32000: 'pcm_32000',
  PCM_44100: 'pcm_44100',
  PCM_48000: 'pcm_48000',
  
  // WAV variants
  WAV_16000: 'wav_16000',
  WAV_22050: 'wav_22050',
  WAV_24000: 'wav_24000'
};

const MODELS = {
  TTS_V1_LATEST: 'voiceai-tts-v1-latest',
  TTS_V1_2025_12_19: 'voiceai-tts-v1-2025-12-19',
  MULTILINGUAL_V1_LATEST: 'voiceai-tts-multilingual-v1-latest',
  MULTILINGUAL_V1_2025_01_14: 'voiceai-tts-multilingual-v1-2025-01-14'
};

const LANGUAGES = {
  ENGLISH: 'en',
  SPANISH: 'es',
  FRENCH: 'fr',
  GERMAN: 'de',
  ITALIAN: 'it',
  PORTUGUESE: 'pt',
  POLISH: 'pl',
  RUSSIAN: 'ru',
  DUTCH: 'nl',
  SWEDISH: 'sv',
  CATALAN: 'ca'
};

const VOICE_VISIBILITY = {
  PUBLIC: 'PUBLIC',
  PRIVATE: 'PRIVATE'
};

const VOICE_STATUS = {
  PENDING: 'PENDING',
  PROCESSING: 'PROCESSING',
  AVAILABLE: 'AVAILABLE',
  FAILED: 'FAILED'
};

// ============================================================================
// Error Classes
// ============================================================================

class VoiceAIError extends Error {
  constructor(message, code, details = null) {
    super(message);
    this.name = 'VoiceAIError';
    this.code = code;
    this.details = details;
  }
}

class AuthenticationError extends VoiceAIError {
  constructor(message = 'Invalid or missing API key') {
    super(message, 401);
    this.name = 'AuthenticationError';
  }
}

class PaymentRequiredError extends VoiceAIError {
  constructor(message = 'Insufficient credits or voice slot limit reached') {
    super(message, 402);
    this.name = 'PaymentRequiredError';
  }
}

class NotFoundError extends VoiceAIError {
  constructor(message = 'Resource not found') {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

class ValidationError extends VoiceAIError {
  constructor(message, details) {
    super(message, 422, details);
    this.name = 'ValidationError';
  }
}

class RateLimitError extends VoiceAIError {
  constructor(message = 'Rate limit exceeded') {
    super(message, 429);
    this.name = 'RateLimitError';
  }
}

// ============================================================================
// Main Client Class
// ============================================================================

class VoiceAI {
  /**
   * Create a Voice.ai API client
   * @param {string} apiKey - Your Voice.ai API key
   * @param {Object} options - Configuration options
   * @param {string} options.baseUrl - API base URL (default: https://dev.voice.ai)
   *   Note: dev.voice.ai is the official production API domain. Only https base URLs are supported.
   * @param {number} options.timeout - Request timeout in ms (default: 60000)
   */
  constructor(apiKey, options = {}) {
    if (!apiKey) {
      throw new AuthenticationError('API key is required');
    }
    
    this.apiKey = apiKey;
    this.baseUrl = options.baseUrl || BASE_URL;
    this.timeout = options.timeout || 60000;
    
    // Expose constants
    this.AUDIO_FORMATS = AUDIO_FORMATS;
    this.MODELS = MODELS;
    this.LANGUAGES = LANGUAGES;
    this.VOICE_VISIBILITY = VOICE_VISIBILITY;
    this.VOICE_STATUS = VOICE_STATUS;
  }

  // --------------------------------------------------------------------------
  // Private Methods
  // --------------------------------------------------------------------------

  /**
   * Make an HTTP request to the API
   * @private
   */
  async _request(method, endpoint, options = {}) {
    const url = new URL(`/api/${API_VERSION}${endpoint}`, this.baseUrl);

    if (url.protocol !== 'https:') {
      throw new ValidationError('Only https baseUrl is supported');
    }
    
    // Add query parameters
    if (options.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.append(key, value);
        }
      });
    }

    const requestOptions = {
      method,
      hostname: url.hostname,
      path: url.pathname + url.search,
      port: url.port || 443,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'User-Agent': 'VoiceAI-SDK/1.1.5',
        ...options.headers
      },
      timeout: this.timeout
    };

    if (options.body && typeof options.body === 'object' && !options.isFormData) {
      requestOptions.headers['Content-Type'] = 'application/json';
    }

    return new Promise((resolve, reject) => {
      const req = https.request(requestOptions, (res) => {
        const chunks = [];
        
        res.on('data', chunk => chunks.push(chunk));
        
        res.on('end', () => {
          const buffer = Buffer.concat(chunks);
          
          // Handle errors
          if (res.statusCode >= 400) {
            let errorData;
            try {
              errorData = JSON.parse(buffer.toString());
            } catch {
              errorData = { error: buffer.toString() || 'Unknown error' };
            }
            
            switch (res.statusCode) {
              case 401:
                reject(new AuthenticationError(errorData.error));
                break;
              case 402:
                reject(new PaymentRequiredError(errorData.error));
                break;
              case 404:
                reject(new NotFoundError(errorData.error));
                break;
              case 422:
                reject(new ValidationError(errorData.error, errorData.detail));
                break;
              case 429:
                reject(new RateLimitError(errorData.error));
                break;
              default:
                reject(new VoiceAIError(errorData.error, res.statusCode, errorData.detail));
            }
            return;
          }
          
          // Return binary for audio responses
          const contentType = res.headers['content-type'] || '';
          if (contentType.startsWith('audio/') || options.binary) {
            resolve(buffer);
          } else {
            try {
              resolve(JSON.parse(buffer.toString()));
            } catch {
              resolve(buffer.toString());
            }
          }
        });
      });

      req.on('error', reject);
      req.on('timeout', () => {
        req.destroy();
        reject(new VoiceAIError('Request timeout', 'TIMEOUT'));
      });

      // Send body
      if (options.body) {
        if (options.isFormData) {
          req.write(options.body);
        } else if (typeof options.body === 'object') {
          req.write(JSON.stringify(options.body));
        } else {
          req.write(options.body);
        }
      }
      
      req.end();
    });
  }

  /**
   * Make a streaming request
   * @private
   */
  _streamRequest(method, endpoint, options = {}) {
    const url = new URL(`/api/${API_VERSION}${endpoint}`, this.baseUrl);

    if (url.protocol !== 'https:') {
      throw new ValidationError('Only https baseUrl is supported');
    }
    
    const requestOptions = {
      method,
      hostname: url.hostname,
      path: url.pathname,
      port: url.port || 443,
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json',
        'User-Agent': 'VoiceAI-SDK/1.1.5',
        ...options.headers
      }
    };
    
    return new Promise((resolve, reject) => {
      const req = https.request(requestOptions, (res) => {
        if (res.statusCode >= 400) {
          const chunks = [];
          res.on('data', chunk => chunks.push(chunk));
          res.on('end', () => {
            const buffer = Buffer.concat(chunks);
            try {
              const errorData = JSON.parse(buffer.toString());
              reject(new VoiceAIError(errorData.error, res.statusCode));
            } catch {
              reject(new VoiceAIError('Request failed', res.statusCode));
            }
          });
          return;
        }
        resolve(res);
      });

      req.on('error', reject);

      if (options.body) {
        req.write(JSON.stringify(options.body));
      }
      
      req.end();
    });
  }

  // --------------------------------------------------------------------------
  // Voice Management
  // --------------------------------------------------------------------------

  /**
   * List available voices
   * @param {Object} options - Query options
   * @param {number} options.limit - Max voices to return (default: 10)
   * @param {number} options.offset - Pagination offset
   * @param {string} options.visibility - Filter by PUBLIC or PRIVATE
   * @returns {Promise<Object>} Voice list response
   */
  async listVoices(options = {}) {
    const { limit = 10, offset = 0, visibility } = options;
    
    return this._request('GET', '/tts/voices', {
      params: { limit, offset, visibility }
    });
  }

  /**
   * Get voice details
   * @param {string} voiceId - The voice ID
   * @returns {Promise<Object>} Voice details
   */
  async getVoice(voiceId) {
    if (!voiceId) {
      throw new ValidationError('Voice ID is required');
    }
    
    return this._request('GET', `/tts/voice/${voiceId}`);
  }

  /**
   * Update voice metadata
   * @param {string} voiceId - The voice ID
   * @param {Object} updates - Fields to update
   * @param {string} updates.name - New voice name
   * @param {string} updates.voice_visibility - New visibility (PUBLIC/PRIVATE)
   * @returns {Promise<Object>} Updated voice
   */
  async updateVoice(voiceId, updates) {
    if (!voiceId) {
      throw new ValidationError('Voice ID is required');
    }
    
    return this._request('PATCH', `/tts/voice/${voiceId}`, {
      body: updates
    });
  }

  /**
   * Delete a voice
   * @param {string} voiceId - The voice ID to delete
   * @returns {Promise<Object>} Deletion confirmation
   */
  async deleteVoice(voiceId) {
    if (!voiceId) {
      throw new ValidationError('Voice ID is required');
    }
    
    return this._request('DELETE', `/tts/voice/${voiceId}`);
  }

  // --------------------------------------------------------------------------
  // Speech Generation
  // --------------------------------------------------------------------------

  /**
   * Generate speech from text
   * @param {Object} options - Generation options
   * @param {string} options.text - Text to convert to speech (required)
   * @param {string} options.voice_id - Voice ID to use
   * @param {string} options.audio_format - Output format (default: 'mp3')
   * @param {number} options.temperature - Sampling temperature 0-2 (default: 1)
   * @param {number} options.top_p - Nucleus sampling 0-1 (default: 0.8)
   * @param {string} options.model - TTS model to use
   * @param {string} options.language - Language code (default: 'en')
   * @returns {Promise<Buffer>} Audio data buffer
   */
  async generateSpeech(options) {
    const {
      text,
      voice_id,
      audio_format = 'mp3',
      temperature = 1.0,
      top_p = 0.8,
      model,
      language = 'en'
    } = options;

    if (!text) {
      throw new ValidationError('Text is required');
    }

    return this._request('POST', '/tts/speech', {
      body: {
        text,
        voice_id,
        audio_format,
        temperature,
        top_p,
        model,
        language
      },
      binary: true
    });
  }

  /**
   * Generate speech and save to file
   * @param {Object} options - Generation options (same as generateSpeech)
   * @param {string} outputPath - Path to save the audio file
   * @returns {Promise<string>} Path to saved file
   */
  async generateSpeechToFile(options, outputPath) {
    const audio = await this.generateSpeech(options);
    fs.writeFileSync(outputPath, audio);
    return outputPath;
  }

  /**
   * Generate speech with streaming
   * @param {Object} options - Generation options
   * @returns {Promise<ReadableStream>} Streaming audio response
   */
  async streamSpeech(options) {
    const {
      text,
      voice_id,
      audio_format = 'mp3',
      temperature = 1.0,
      top_p = 0.8,
      model,
      language = 'en'
    } = options;

    if (!text) {
      throw new ValidationError('Text is required');
    }

    return this._streamRequest('POST', '/tts/speech/stream', {
      body: {
        text,
        voice_id,
        audio_format,
        temperature,
        top_p,
        model,
        language
      }
    });
  }

  /**
   * Stream speech to file
   * @param {Object} options - Generation options
   * @param {string} outputPath - Path to save the audio file
   * @returns {Promise<string>} Path to saved file
   */
  async streamSpeechToFile(options, outputPath) {
    const stream = await this.streamSpeech(options);
    
    return new Promise((resolve, reject) => {
      const writeStream = fs.createWriteStream(outputPath);
      
      stream.pipe(writeStream);
      
      writeStream.on('finish', () => resolve(outputPath));
      writeStream.on('error', reject);
      stream.on('error', reject);
    });
  }

  // --------------------------------------------------------------------------
  // Utility Methods
  // --------------------------------------------------------------------------

  /**
   * Check if API key is valid
   * @returns {Promise<boolean>} True if valid
   */
  async validateApiKey() {
    try {
      await this.listVoices({ limit: 1 });
      return true;
    } catch (error) {
      if (error instanceof AuthenticationError) {
        return false;
      }
      throw error;
    }
  }

  /**
   * Get first N voices (convenience method)
   * @param {number} count - Number of voices to retrieve
   * @returns {Promise<Array>} Array of voice objects
   */
  async getFirstVoices(count = 10) {
    const response = await this.listVoices({ limit: count });
    return response.voices || [];
  }
}

// ============================================================================
// Exports
// ============================================================================

module.exports = VoiceAI;
module.exports.VoiceAI = VoiceAI;
module.exports.VoiceAIError = VoiceAIError;
module.exports.AuthenticationError = AuthenticationError;
module.exports.PaymentRequiredError = PaymentRequiredError;
module.exports.NotFoundError = NotFoundError;
module.exports.ValidationError = ValidationError;
module.exports.RateLimitError = RateLimitError;
module.exports.AUDIO_FORMATS = AUDIO_FORMATS;
module.exports.MODELS = MODELS;
module.exports.LANGUAGES = LANGUAGES;
module.exports.VOICE_VISIBILITY = VOICE_VISIBILITY;
module.exports.VOICE_STATUS = VOICE_STATUS;
