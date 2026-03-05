const axios = require('axios');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');
const querystring = require('querystring');

/**
 * Upbit 클라이언트 (upbitClient.js)
 * - 인증 헤더 생성
 * - Rate Limit (429) 자동 재시도
 * - 표준 에러 로깅
 */

const Logger = {
    info: (msg) => console.log(`[${new Date().toLocaleString()}] [UPBIT-CLIENT] ${msg}`),
    warn: (msg) => console.warn(`[${new Date().toLocaleString()}] [UPBIT-WARN] ${msg}`),
    error: (msg) => console.error(`[${new Date().toLocaleString()}] [UPBIT-ERR] ${msg}`),
};

class UpbitClient {
    constructor(accessKey, secretKey) {
        this.accessKey = accessKey;
        this.secretKey = secretKey;
        this.baseUrl = 'https://api.upbit.com/v1';
        // Security: do not allow changing API host (ClawHub safety)
        const allowedHost = 'api.upbit.com';
        const u = new URL(this.baseUrl);
        if (u.protocol !== 'https:' || u.host !== allowedHost) {
            throw new Error(`Blocked baseUrl: ${this.baseUrl} (allowed: https://${allowedHost}/v1)`);
        }

        this.api = axios.create({
            baseURL: this.baseUrl,
            timeout: 10000,
            maxRedirects: 0,
            headers: { 'Content-Type': 'application/json' } // 권장되는 JSON 헤더
        });

        this._setupInterceptors();
    }

    _createAuthHeader(queryParams = {}) {
        const payload = {
            access_key: this.accessKey,
            nonce: uuidv4(),
        };

        const query = querystring.stringify(queryParams);
        if (query) {
            const hash = crypto.createHash('sha512');
            const queryHash = hash.update(query, 'utf-8').digest('hex');
            payload.query_hash = queryHash;
            payload.query_hash_alg = 'SHA512';
        }

        const token = jwt.sign(payload, this.secretKey, { algorithm: 'HS512' });
        return `Bearer ${token}`;
    }

    _setupInterceptors() {
        this.api.interceptors.response.use(
            (response) => response,
            async (error) => {
                const { config, response } = error;
                if (response && response.status === 429) {
                    const remainingSec = parseFloat(response.headers['remaining-second']) || 1;
                    const waitTime = (remainingSec + 0.5) * 1000;
                    Logger.warn(`Rate Limit(429) 도달. ${waitTime}ms 후 재시도...`);
                    await new Promise(resolve => setTimeout(resolve, waitTime));
                    return this.api(config);
                }

                const upbitError = response?.data?.error;
                if (upbitError) {
                    Logger.error(`API Error [${response.status}] (${upbitError.name}): ${upbitError.message}`);
                } else {
                    Logger.error(`Network/HTTP Error: ${error.message}`);
                }
                return Promise.reject(error);
            }
        );
    }

    async request(method, url, data = {}, params = {}) {
        const isAuthRequest = url.startsWith('/orders') || url.startsWith('/accounts') || url.startsWith('/order');
        const headers = {};

        if (isAuthRequest) {
            // POST의 경우 data가 query_hash 대상, GET의 경우 params가 대상
            const authParams = method.toLowerCase() === 'get' ? params : data;
            headers.Authorization = this._createAuthHeader(authParams);
        }

        try {
            const response = await this.api({
                method,
                url,
                data: method.toLowerCase() === 'get' ? undefined : data,
                params,
                headers
            });
            return response.data;
        } catch (err) {
            throw err;
        }
    }
}

module.exports = { UpbitClient, Logger };
