export class TandoorApiError extends Error {
    statusCode;
    statusText;
    responseBody;
    constructor(statusCode, statusText, responseBody) {
        super(`HTTP ${statusCode} ${statusText}: ${responseBody}`);
        this.statusCode = statusCode;
        this.statusText = statusText;
        this.responseBody = responseBody;
        this.name = 'TandoorApiError';
    }
}
function getConfig() {
    const url = process.env.TANDOOR_URL;
    const token = process.env.TANDOOR_API_TOKEN;
    const additionalHeadersRaw = process.env.TANDOOR_ADDITIONAL_HEADERS;
    if (!url) {
        throw new Error('TANDOOR_URL environment variable is not set');
    }
    if (!token) {
        throw new Error('TANDOOR_API_TOKEN environment variable is not set');
    }
    let additionalHeaders;
    if (additionalHeadersRaw) {
        try {
            additionalHeaders = JSON.parse(additionalHeadersRaw);
        }
        catch {
            throw new Error('TANDOOR_ADDITIONAL_HEADERS must be valid JSON');
        }
    }
    return { url, token, additionalHeaders };
}
/**
 * Make a validated API request to Tandoor
 */
export async function apiRequest(endpoint, schema, options = {}) {
    const { url: TANDOOR_URL, token: TANDOOR_API_TOKEN, additionalHeaders: envHeaders } = getConfig();
    const { method = 'GET', body, headers: optionHeaders } = options;
    const url = new URL(endpoint, TANDOOR_URL);
    const headers = {
        'Authorization': `Bearer ${TANDOOR_API_TOKEN}`,
        'Accept': 'application/json',
        ...envHeaders,
        ...optionHeaders,
    };
    if (body) {
        headers['Content-Type'] = 'application/json';
    }
    const response = await fetch(url.toString(), {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
    });
    if (!response.ok) {
        const text = await response.text();
        throw new TandoorApiError(response.status, response.statusText, text);
    }
    // Handle empty responses (DELETE)
    if (response.status === 204 || response.headers.get('content-length') === '0') {
        return schema.parse(null);
    }
    const data = await response.json();
    return schema.parse(data);
}
/**
 * Make an unvalidated API request (for mutations that don't need response validation)
 */
export async function apiRequestRaw(endpoint, options = {}) {
    const { url: TANDOOR_URL, token: TANDOOR_API_TOKEN, additionalHeaders: envHeaders } = getConfig();
    const { method = 'GET', body, headers: optionHeaders } = options;
    const url = new URL(endpoint, TANDOOR_URL);
    const headers = {
        'Authorization': `Bearer ${TANDOOR_API_TOKEN}`,
        'Accept': 'application/json',
        ...envHeaders,
        ...optionHeaders,
    };
    if (body) {
        headers['Content-Type'] = 'application/json';
    }
    const response = await fetch(url.toString(), {
        method,
        headers,
        body: body ? JSON.stringify(body) : undefined,
    });
    if (!response.ok) {
        const text = await response.text();
        throw new TandoorApiError(response.status, response.statusText, text);
    }
    if (response.status === 204) {
        return null;
    }
    return response.json();
}
//# sourceMappingURL=api.js.map