const crypto = require('crypto');
const https = require('https');

class OKXClient {
    constructor(config = {}) {
        this.apiKey = config.apiKey || process.env.OKX_API_KEY;
        this.secretKey = config.secretKey || process.env.OKX_SECRET_KEY;
        this.passphrase = config.passphrase || process.env.OKX_PASSPHRASE;
        const isSim = config.isSimulation !== undefined ? config.isSimulation : process.env.OKX_IS_SIMULATION;
        this.isSimulation = isSim === true || isSim === 'true';
    }

    sign(timestamp, method, requestPath, body = '') {
        const signText = timestamp + method + requestPath + body;
        return crypto.createHmac('sha256', this.secretKey).update(signText).digest('base64');
    }

    request(endpoint, method = 'GET', params = '') {
        return new Promise((resolve, reject) => {
            const timestamp = new Date().toISOString();
            let pathStr = endpoint;
            let body = '';

            if (method === 'GET' && typeof params === 'object' && Object.keys(params).length > 0) {
                pathStr += '?' + new URLSearchParams(params).toString();
            } else if (method === 'POST') {
                body = typeof params === 'string' ? params : JSON.stringify(params);
            }

            const options = {
                hostname: 'www.okx.com',
                port: 443,
                path: '/api/v5' + pathStr,
                method: method,
                headers: {
                    'OK-ACCESS-KEY': this.apiKey,
                    'OK-ACCESS-SIGN': this.sign(timestamp, method, '/api/v5' + pathStr, body),
                    'OK-ACCESS-TIMESTAMP': timestamp,
                    'OK-ACCESS-PASSPHRASE': this.passphrase,
                    'x-simulated-trading': this.isSimulation ? '1' : '0',
                    'Content-Type': 'application/json'
                }
            };

            const req = https.request(options, res => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        const json = JSON.parse(data);
                        if (json.code === '0') resolve(json.data);
                        else resolve({ error: json.msg, code: json.code });
                    } catch (e) {
                        resolve({ error: 'JSON Parse Error', raw: data });
                    }
                });
            });

            req.on('error', (e) => reject(e));
            if (body) {
                const bodyStr = typeof body === 'string' ? body : JSON.stringify(body);
                req.write(bodyStr);
            }
            req.end();
        });
    }
}

module.exports = OKXClient;
