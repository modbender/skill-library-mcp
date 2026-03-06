/**
 * Common utilities for Prometheus API client
 */

/**
 * Get environment variable with optional default
 * @param {string} name - Environment variable name
 * @param {string} defaultValue - Default value if not set
 * @returns {string}
 */
export function getEnv(name, defaultValue = '') {
  return process.env[name] || defaultValue;
}

/**
 * Get Prometheus base URL from environment
 * @returns {string}
 */
export function getPrometheusUrl() {
  const url = getEnv('PROMETHEUS_URL');
  if (!url) {
    throw new Error('PROMETHEUS_URL environment variable is required');
  }
  return url.replace(/\/$/, ''); // Remove trailing slash
}

/**
 * Create authentication headers if credentials are provided
 * @returns {Object} Headers object
 */
export function createAuthHeader() {
  const headers = {
    'Accept': 'application/json'
  };
  
  const user = getEnv('PROMETHEUS_USER');
  const password = getEnv('PROMETHEUS_PASSWORD');
  
  if (user && password) {
    const auth = Buffer.from(`${user}:${password}`).toString('base64');
    headers['Authorization'] = `Basic ${auth}`;
  }
  
  return headers;
}

/**
 * Build full URL for API endpoint
 * @param {string} path - API path
 * @returns {string} Full URL
 */
export function buildUrl(path) {
  return `${getPrometheusUrl()}${path}`;
}

/**
 * Handle API response and parse JSON
 * @param {Response} response - Fetch response
 * @returns {Promise<any>} Parsed response data
 */
export async function handleResponse(response) {
  if (!response.ok) {
    const text = await response.text().catch(() => 'Unknown error');
    throw new Error(`HTTP ${response.status}: ${text}`);
  }
  
  const data = await response.json();
  
  if (data.status !== 'success') {
    throw new Error(`Prometheus error: ${data.error || 'Unknown error'}`);
  }
  
  return data.data;
}

/**
 * Format bytes to human readable string
 * @param {number} bytes - Bytes to format
 * @returns {string} Formatted string
 */
export function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format seconds to human readable duration
 * @param {number} seconds - Seconds to format
 * @returns {string} Formatted string
 */
export function formatDuration(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  
  if (days > 0) return `${days}d ${hours}h`;
  if (hours > 0) return `${hours}h ${mins}m`;
  return `${mins}m`;
}
