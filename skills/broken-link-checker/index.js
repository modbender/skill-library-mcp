const https = require('https');
const http = require('http');

async function checkUrl(url) {
  return new Promise((resolve) => {
    const protocol = url.startsWith('https') ? https : http;
    const req = protocol.request(url, { method: 'HEAD', timeout: 5000 }, (res) => {
      resolve({
        url,
        valid: res.statusCode >= 200 && res.statusCode < 400,
        status: res.statusCode
      });
    });

    req.on('error', (err) => {
      resolve({
        url,
        valid: false,
        error: err.message
      });
    });

    req.on('timeout', () => {
      req.destroy();
      resolve({
        url,
        valid: false,
        error: 'timeout'
      });
    });

    req.end();
  });
}

async function main() {
  const args = process.argv.slice(2);
  const urls = args.filter(arg => arg.startsWith('http'));

  if (urls.length === 0) {
    console.error('Usage: node skills/broken-link-checker/index.js <url1> [url2...]');
    // Don't exit 1 if just imported, but if run directly without args, show usage.
    if (require.main === module) process.exit(1);
    return;
  }

  const results = await Promise.all(urls.map(checkUrl));
  console.log(JSON.stringify(results, null, 2));

  if (results.some(r => !r.valid)) {
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { main, checkUrl };
