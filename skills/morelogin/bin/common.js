const http = require('http');

const DEFAULT_BASE_URL = process.env.MORELOGIN_LOCAL_API_URL || 'http://127.0.0.1:40000';
const DEFAULT_TIMEOUT_MS = Number.parseInt(process.env.MORELOGIN_LOCAL_API_TIMEOUT_MS || '10000', 10);

function parseArgs(argv) {
  const options = {};
  const positional = [];

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token.startsWith('--')) {
      const key = token.slice(2);
      const next = argv[i + 1];
      if (!next || next.startsWith('--')) {
        options[key] = true;
      } else {
        options[key] = next;
        i += 1;
      }
    } else {
      positional.push(token);
    }
  }

  return { options, positional };
}

function parseJsonInput(value, fieldName) {
  if (!value) return undefined;
  try {
    return JSON.parse(value);
  } catch (error) {
    throw new Error(`${fieldName} is not valid JSON: ${error.message}`);
  }
}

function toBoolean(value, defaultValue = false) {
  if (value === undefined) return defaultValue;
  if (typeof value === 'boolean') return value;
  const normalized = String(value).trim().toLowerCase();
  return normalized === '1' || normalized === 'true' || normalized === 'yes' || normalized === 'on';
}

function toInt(value, defaultValue) {
  if (value === undefined) return defaultValue;
  const parsed = Number.parseInt(String(value), 10);
  if (Number.isNaN(parsed)) return defaultValue;
  return parsed;
}

function splitCsv(value) {
  if (!value) return [];
  return String(value)
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function requestApi(endpoint, { method = 'POST', body, baseUrl = DEFAULT_BASE_URL, timeoutMs = DEFAULT_TIMEOUT_MS } = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(endpoint, baseUrl);
    const payload = body === undefined ? undefined : JSON.stringify(body);

    const options = {
      hostname: url.hostname,
      port: url.port || 80,
      path: `${url.pathname}${url.search}`,
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: timeoutMs,
    };

    if (payload) {
      options.headers['Content-Length'] = Buffer.byteLength(payload);
    }

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        let parsed;
        try {
          parsed = JSON.parse(data);
        } catch (error) {
          parsed = { raw: data };
        }

        resolve({
          statusCode: res.statusCode,
          ok: res.statusCode >= 200 && res.statusCode < 300,
          body: parsed,
        });
      });
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error(`Request timeout after ${timeoutMs}ms`));
    });

    req.on('error', reject);

    if (payload) {
      req.write(payload);
    }
    req.end();
  });
}

function unwrapApiResult(response) {
  const payload = response.body;
  if (!response.ok) {
    return {
      success: false,
      message: `HTTP ${response.statusCode}`,
      payload,
    };
  }

  if (payload && typeof payload.code === 'number') {
    return {
      success: payload.code === 0,
      message: payload.msg || '',
      payload,
      data: payload.data,
    };
  }

  return {
    success: true,
    payload,
    data: payload.data || payload,
  };
}

function printObject(value) {
  console.log(JSON.stringify(value, null, 2));
}

function isPlainObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function requirePlainObject(value, fieldName) {
  if (!isPlainObject(value)) {
    throw new Error(`${fieldName} must be an object`);
  }
  return value;
}

function requireNonEmptyString(value, fieldName) {
  if (value === undefined || value === null || typeof value === 'boolean' || typeof value === 'object') {
    throw new Error(`${fieldName} is required`);
  }
  const normalized = String(value ?? '').trim();
  if (!normalized) {
    throw new Error(`${fieldName} is required`);
  }
  return normalized;
}

function parseRequiredInt(value, fieldName, { min, max } = {}) {
  const normalized = String(value ?? '').trim();
  if (!normalized) {
    throw new Error(`${fieldName} is required`);
  }
  if (!/^-?\d+$/.test(normalized)) {
    throw new Error(`${fieldName} must be an integer`);
  }
  const intValue = Number.parseInt(normalized, 10);
  if (min !== undefined && intValue < min) {
    throw new Error(`${fieldName} must be >= ${min}`);
  }
  if (max !== undefined && intValue > max) {
    throw new Error(`${fieldName} must be <= ${max}`);
  }
  return intValue;
}

function parseOptionalInt(value, fieldName, { min, max } = {}) {
  if (value === undefined || value === null || String(value).trim() === '') {
    return undefined;
  }
  return parseRequiredInt(value, fieldName, { min, max });
}

function requireNonEmptyArray(value, fieldName) {
  if (!Array.isArray(value) || value.length === 0) {
    throw new Error(`${fieldName} must be a non-empty array`);
  }
  return value;
}

function normalizeStringArray(value, fieldName) {
  const arr = requireNonEmptyArray(value, fieldName);
  const normalized = arr
    .map((item) => String(item ?? '').trim())
    .filter(Boolean);
  if (normalized.length === 0) {
    throw new Error(`${fieldName} must include at least one non-empty item`);
  }
  return normalized;
}

function parsePageOptions(options, { defaultPageNo = 1, defaultPageSize = 20, maxPageSize = 200 } = {}) {
  const pageNo = options.page !== undefined
    ? parseRequiredInt(options.page, '--page', { min: 1 })
    : defaultPageNo;
  const pageSize = options['page-size'] !== undefined
    ? parseRequiredInt(options['page-size'], '--page-size', { min: 1, max: maxPageSize })
    : defaultPageSize;
  return { pageNo, pageSize };
}

module.exports = {
  DEFAULT_BASE_URL,
  isPlainObject,
  parseArgs,
  parseOptionalInt,
  parsePageOptions,
  parseRequiredInt,
  parseJsonInput,
  printObject,
  normalizeStringArray,
  requireNonEmptyArray,
  requireNonEmptyString,
  requirePlainObject,
  requestApi,
  splitCsv,
  toBoolean,
  toInt,
  unwrapApiResult,
};
