const https = require('https');
const fs = require('fs');
const path = require('path');

const API_URL = 'https://xapiverse.com/api/terabox-pro';

/**
 * TeraBox Link Extractor Engine v1.4.0
 * Standardized for TERABOX_API_KEY environment variables.
 */

function apiRequest(url, key) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify({ url });
        const req = https.request(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'xAPIverse-Key': key,
                'Content-Length': data.length
            },
            timeout: 20000
        }, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(body));
                } catch (e) {
                    resolve({ status: 'error', message: 'Invalid JSON response' });
                }
            });
        });

        req.on('error', reject);
        req.on('timeout', () => {
            req.destroy();
            reject(new Error('Request timed out'));
        });
        req.write(data);
        req.end();
    });
}

function downloadFile(fileUrl, destPath) {
    return new Promise((resolve, reject) => {
        const req = https.get(fileUrl, (res) => {
            if (res.statusCode === 301 || res.statusCode === 302) {
                downloadFile(res.headers.location, destPath).then(resolve).catch(reject);
                return;
            }
            if (res.statusCode !== 200) {
                reject(new Error(`HTTP Status: ${res.statusCode}`));
                return;
            }
            const file = fs.createWriteStream(destPath);
            res.pipe(file);
            file.on('finish', () => {
                file.close(resolve);
            });
        }).on('error', (err) => {
            fs.unlink(destPath, () => { });
            reject(err);
        });
    });
}

async function extractLinks(targetUrl, keys) {
    let successData = null;
    let lastError = null;
    const API_KEYS = Array.isArray(keys) ? keys : (keys || '').split(',').map(k => k.trim()).filter(Boolean);

    for (const key of API_KEYS) {
        try {
            const result = await apiRequest(targetUrl, key);
            if (result.status === 'success' && result.list) {
                successData = result;
                break;
            } else if (result.message && result.message.toLowerCase().includes('subscribe')) {
                continue;
            } else {
                lastError = result.message || 'Unknown API error';
            }
        } catch (e) {
            lastError = e.message;
        }
    }

    if (successData) return { success: true, data: successData };
    return { success: false, error: lastError || 'All API keys exhausted or invalid.' };
}

// --- CLI Execution ---

if (require.main === module) {
    const API_KEYS = (process.env.TERABOX_API_KEY || '').split(',').map(k => k.trim()).filter(Boolean);
    if (API_KEYS.length === 0) {
        if (process.argv.includes('--json')) {
            console.log(JSON.stringify({ status: 'error', message: 'ERROR: No TERABOX_API_KEY found in environment.' }));
        } else {
            console.error('ERROR: No TERABOX_API_KEY found in environment.');
        }
        process.exit(1);
    }

    const args = process.argv.slice(2);
    let targetUrl = null;
    let downloadFlag = false;
    const DOWNLOAD_ROOT = path.resolve(process.cwd(), 'Downloads');
    let outDir = DOWNLOAD_ROOT;

    for (let i = 0; i < args.length; i++) {
        if (args[i] === '--download') {
            downloadFlag = true;
        } else if (args[i] === '--out') {
            if (args[i + 1]) {
                const potentialPath = path.resolve(DOWNLOAD_ROOT, args[i + 1]);
                if (!potentialPath.startsWith(DOWNLOAD_ROOT)) {
                    console.error(`ERROR: Security Violation. Output path must be within ${DOWNLOAD_ROOT}`);
                    process.exit(1);
                }
                outDir = potentialPath;
                i++;
            }
        } else if (!targetUrl && !args[i].startsWith('--')) {
            targetUrl = args[i];
        }
    }

    if (!targetUrl) {
        console.error('Usage: node extract.js <url> [--download] [--out <path>]');
        process.exit(1);
    }

    (async () => {
        const result = await extractLinks(targetUrl, API_KEYS);
        if (result.success) {
            const successData = result.data;
            if (downloadFlag && !fs.existsSync(outDir)) {
                fs.mkdirSync(outDir, { recursive: true });
            }

            for (const file of successData.list) {
                if (downloadFlag) {
                    let dlUrl = file.fast_download_link || file.download_link;
                    const dest = path.join(outDir, file.name);
                    console.log(`STATUS|Starting download for ${file.name}...`);
                    try {
                        await downloadFile(dlUrl, dest);
                        console.log(`DOWNLOAD_COMPLETE|${dest}`);
                        console.log(`SIZE|${file.size_formatted}`);
                    } catch (e) {
                        console.log(`DOWNLOAD_ERROR|${e.message}`);
                    }
                } else {
                    if (process.argv.includes('--json')) {
                        console.log(JSON.stringify(successData));
                        return;
                    }
                    console.log('---FILE_START---');
                    console.log(`NAME|${file.name}`);
                    console.log(`SIZE|${file.size_formatted}`);
                    console.log(`DURATION|${file.duration || 'N/A'}`);
                    console.log(`TYPE|${file.type || 'N/A'}`);
                    console.log(`DL_LINK|${file.download_link}`);
                    console.log(`FAST_DL|${file.fast_download_link || 'N/A'}`);
                    console.log(`STREAM|${file.stream_url}`);
                    console.log(`THUMBNAIL|${file.thumbnail || 'N/A'}`);
                }
            }
            if (!downloadFlag) console.log(`CREDITS|${successData.free_credits_remaining}`);
        } else {
            if (process.argv.includes('--json')) {
                console.log(JSON.stringify({ status: 'error', message: result.error }));
            } else {
                console.log(`ERROR|${result.error}`);
            }
        }
    })();
}

module.exports = { extractLinks, downloadFile };
