const https = require('https');
const http = require('http');
const { URL } = require('url');

/**
 * Perform an HTTP/HTTPS request.
 * @param {string} method - GET, POST, PUT, DELETE, etc. (default GET)
 * @param {string} endpoint - URL to request.
 * @param {object} headers - Request headers (optional).
 * @param {string|object} body - Request body (string or JSON, optional).
 * @param {number} timeout - Timeout in ms (default 10000).
 * @returns {Promise<object>} - { status, headers, data, error }
 */
function request(method = 'GET', endpoint, headers = {}, body = null, timeout = 10000) {
  return new Promise((resolve) => {
    let parsedUrl;
    try {
      parsedUrl = new URL(endpoint);
    } catch (e) {
      return resolve({ status: 0, headers: {}, data: null, error: `Invalid URL: ${endpoint}` });
    }

    const lib = parsedUrl.protocol === 'https:' ? https : http;
    const options = {
      method: method.toUpperCase(),
      headers: headers || {},
      timeout,
    };

    let bodyData = null;
    if (body) {
      if (typeof body === 'object') {
        bodyData = JSON.stringify(body);
        if (!options.headers['Content-Type']) {
          options.headers['Content-Type'] = 'application/json';
        }
      } else {
        bodyData = String(body);
      }
      options.headers['Content-Length'] = Buffer.byteLength(bodyData);
    }

    const req = lib.request(parsedUrl, options, (res) => {
      let rawData = '';
      res.setEncoding('utf8');
      res.on('data', (chunk) => rawData += chunk);
      res.on('end', () => {
        let parsedData = rawData;
        try {
          // Attempt to parse JSON if content-type suggests it
          const ct = res.headers['content-type'] || '';
          if (ct.includes('application/json')) {
            parsedData = JSON.parse(rawData);
          }
        } catch (e) {
          // Keep as string if parsing fails
        }
        resolve({
          status: res.statusCode,
          headers: res.headers,
          data: parsedData,
          raw: rawData
        });
      });
    });

    req.on('error', (e) => {
      resolve({
        status: 0,
        headers: {},
        data: null,
        error: e.message,
      });
    });

    req.on('timeout', () => {
      req.destroy();
      resolve({
        status: 0,
        headers: {},
        data: null,
        error: 'Request timeout',
      });
    });

    if (bodyData) {
      req.write(bodyData);
    }
    req.end();
  });
}

// Main entry point for CLI or test
async function main() {
  // Simple smoke test: check internet connectivity
  console.log('Running api-tester smoke test...');
  const result = await request('GET', 'https://www.google.com', {}, null, 5000);
  if (result.status >= 200 && result.status < 400) {
    console.log('Smoke test passed: Google reachable.');
    return true;
  } else {
    // Some envs block google, try example.com
    const result2 = await request('GET', 'http://example.com', {}, null, 5000);
    if (result2.status >= 200 && result2.status < 400) {
      console.log('Smoke test passed: example.com reachable.');
      return true;
    }
    console.error('Smoke test failed:', result.error || result.status);
    return false;
  }
}

module.exports = {
  request,
  main
};

if (require.main === module) {
  main();
}
