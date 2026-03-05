/**
 * Ragflow API Client
 * Universal wrapper for Ragflow REST API
 * 
 * Required env vars: RAGFLOW_URL, RAGFLOW_API_KEY
 */

const fs = require('fs');
const https = require('https');
const http = require('http');
const path = require('path');

const RAGFLOW_URL = process.env.RAGFLOW_URL;
const RAGFLOW_API_KEY = process.env.RAGFLOW_API_KEY;

/**
 * Make HTTP request to Ragflow API
 */
async function request(method, apiPath, body = null) {
  return new Promise((resolve, reject) => {
    if (!RAGFLOW_URL || !RAGFLOW_API_KEY) {
      reject(new Error('RAGFLOW_URL and RAGFLOW_API_KEY must be set'));
      return;
    }
    
    const url = new URL(RAGFLOW_URL);
    const client = url.protocol === 'https:' ? https : http;
    
    const options = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: `/api/v1${apiPath}`,
      method,
      headers: {
        'Authorization': `Bearer ${RAGFLOW_API_KEY}`,
      }
    };
    
    let requestBody = null;
    if (body) {
      requestBody = JSON.stringify(body);
      options.headers['Content-Type'] = 'application/json';
      options.headers['Content-Length'] = Buffer.byteLength(requestBody);
    }
    
    const req = client.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(parsed);
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${data}`));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    if (requestBody) req.write(requestBody);
    req.end();
  });
}

/**
 * List all datasets
 */
async function listDatasets() {
  return request('GET', '/datasets');
}

/**
 * Create a new dataset
 * @param {string} name - Dataset name
 * @param {Object} options - Optional settings (chunk_method, etc.)
 */
async function createDataset(name, options = {}) {
  return request('POST', '/datasets', { name, ...options });
}

/**
 * Delete a dataset
 * @param {string} datasetId
 */
async function deleteDataset(datasetId) {
  return request('DELETE', `/datasets/${datasetId}`);
}

/**
 * List documents in a dataset
 * @param {string} datasetId
 */
async function listDocuments(datasetId) {
  return request('GET', `/datasets/${datasetId}/documents`);
}

/**
 * Upload file to dataset
 * @param {string} datasetId
 * @param {string} filePath - Path to file
 * @param {Object} options - { filename: string }
 */
async function uploadDocument(datasetId, filePath, options = {}) {
  return new Promise((resolve, reject) => {
    if (!RAGFLOW_URL || !RAGFLOW_API_KEY) {
      reject(new Error('RAGFLOW_URL and RAGFLOW_API_KEY must be set'));
      return;
    }
    
    const boundary = '----FormBoundary' + Date.now();
    const fileContent = fs.readFileSync(filePath);
    const filename = options.filename || path.basename(filePath);
    
    const body = [
      `--${boundary}`,
      `Content-Disposition: form-data; name="file"; filename="${filename}"`,
      'Content-Type: application/octet-stream',
      '',
      fileContent.toString(),
      `--${boundary}--`
    ].join('\r\n');
    
    const url = new URL(RAGFLOW_URL);
    const client = url.protocol === 'https:' ? https : http;
    
    const req = client.request({
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: `/api/v1/datasets/${datasetId}/documents`,
      method: 'POST',
      headers: {
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Authorization': `Bearer ${RAGFLOW_API_KEY}`,
        'Content-Length': Buffer.byteLength(body)
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(e);
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });
    
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

/**
 * Trigger document parsing
 * @param {string} datasetId
 * @param {string[]} documentIds
 */
async function triggerParsing(datasetId, documentIds) {
  return request('POST', `/datasets/${datasetId}/chunks`, { document_ids: documentIds });
}

/**
 * Chat query against dataset (RAG)
 * @param {string} datasetId
 * @param {string} question
 * @param {Object} options - { top_k, similarity_threshold }
 */
async function chat(datasetId, question, options = {}) {
  return request('POST', `/datasets/${datasetId}/retrieval`, {
    question,
    top_k: options.top_k || 10,
    similarity_threshold: options.similarity_threshold || 0.1,
  });
}

/**
 * Helper: Upload and parse in one step
 * @param {string} datasetId
 * @param {string} filePath
 * @param {Object} options
 * @returns {Promise<{documentId: string}>}
 */
async function uploadAndParse(datasetId, filePath, options = {}) {
  const result = await uploadDocument(datasetId, filePath, options);
  const documentId = result.data?.[0]?.id;
  if (documentId) {
    await triggerParsing(datasetId, [documentId]);
  }
  return { documentId, ...result };
}

module.exports = {
  listDatasets,
  createDataset,
  deleteDataset,
  listDocuments,
  uploadDocument,
  triggerParsing,
  chat,
  uploadAndParse,
};