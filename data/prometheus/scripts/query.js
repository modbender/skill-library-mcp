import { getEnv, createAuthHeader, handleResponse, buildUrl } from './common.js';

/**
 * Execute instant query against Prometheus
 * @param {string} query - PromQL query string
 * @param {string} time - Optional Unix timestamp
 * @returns {Promise<Object>} Query result
 */
export async function instantQuery(query, time = null) {
  const url = buildUrl('/api/v1/query');
  const params = new URLSearchParams({ query });
  if (time) params.append('time', time);
  
  const response = await fetch(`${url}?${params}`, {
    headers: createAuthHeader()
  });
  
  return handleResponse(response);
}

/**
 * Execute range query against Prometheus
 * @param {string} query - PromQL query string
 * @param {string} start - Start time (RFC3339 or Unix timestamp)
 * @param {string} end - End time (RFC3339 or Unix timestamp)
 * @param {number} step - Query resolution step width in seconds
 * @returns {Promise<Object>} Query result
 */
export async function rangeQuery(query, start, end, step = 60) {
  const url = buildUrl('/api/v1/query_range');
  const params = new URLSearchParams({ query, start, end, step: String(step) });
  
  const response = await fetch(`${url}?${params}`, {
    headers: createAuthHeader()
  });
  
  return handleResponse(response);
}

/**
 * Get label names
 * @returns {Promise<string[]>} Array of label names
 */
export async function getLabels() {
  const url = buildUrl('/api/v1/labels');
  
  const response = await fetch(url, {
    headers: createAuthHeader()
  });
  
  return handleResponse(response);
}

/**
 * Get values for a specific label
 * @param {string} label - Label name
 * @returns {Promise<string[]>} Array of label values
 */
export async function getLabelValues(label) {
  const url = buildUrl(`/api/v1/label/${encodeURIComponent(label)}/values`);
  
  const response = await fetch(url, {
    headers: createAuthHeader()
  });
  
  return handleResponse(response);
}

/**
 * Find time series by label matchers
 * @param {string} match - Series selector (e.g., '{__name__="up"}')
 * @param {string} start - Optional start time
 * @param {string} end - Optional end time
 * @returns {Promise<Object[]>} Array of series
 */
export async function getSeries(match, start = null, end = null) {
  const url = buildUrl('/api/v1/series');
  const params = new URLSearchParams();
  params.append('match[]', match);
  if (start) params.append('start', start);
  if (end) params.append('end', end);
  
  const response = await fetch(`${url}?${params}`, {
    headers: createAuthHeader()
  });
  
  return handleResponse(response);
}

/**
 * Get metadata about metrics
 * @param {string} metric - Optional metric name to filter
 * @returns {Promise<Object>} Metrics metadata
 */
export async function getMetadata(metric = '') {
  const url = buildUrl('/api/v1/metadata');
  const params = metric ? `?metric=${encodeURIComponent(metric)}` : '';
  
  const response = await fetch(`${url}${params}`, {
    headers: createAuthHeader()
  });
  
  return handleResponse(response);
}

/**
 * Get current alerts
 * @returns {Promise<Object>} Active alerts
 */
export async function getAlerts() {
  const url = buildUrl('/api/v1/alerts');
  
  const response = await fetch(url, {
    headers: createAuthHeader()
  });
  
  return handleResponse(response);
}

/**
 * Get target discovery status
 * @returns {Promise<Object>} Scrape targets
 */
export async function getTargets() {
  const url = buildUrl('/api/v1/targets');
  
  const response = await fetch(url, {
    headers: createAuthHeader()
  });
  
  return handleResponse(response);
}
