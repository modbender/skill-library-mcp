const https = require('https');

// Try different possible endpoints
const endpoints = [
  '/v1/jobs/6b2a1efe-07bd-4e2b-b817-77f938209215/submit',
  '/v1/jobs/6b2a1efe-07bd-4e2b-b817-77f938209215/deliverable',
  '/v1/jobs/6b2a1efe-07bd-4e2b-b817-77f938209215/deliverables',
  '/api/jobs/6b2a1efe-07bd-4e2b-b817-77f938209215/deliverables',
];

async function testEndpoint(path, method = 'GET', body = null) {
  return new Promise((resolve) => {
    const options = {
      hostname: 'market.near.ai',
      port: 443,
      path: path,
      method: method,
      headers: {
        'Authorization': 'Bearer sk_live_iOQS6NKYgLCf8sAcIsjeNpIvsN9ml7fK6CVrfIyPIVs'
      }
    };

    if (body) {
      options.headers['Content-Type'] = 'application/json';
      options.headers['Content-Length'] = Buffer.byteLength(body);
    }

    const req = https.request(options, (res) => {
      let responseData = '';
      res.on('data', (chunk) => {
        responseData += chunk;
      });
      res.on('end', () => {
        resolve({ path, status: res.statusCode, response: responseData });
      });
    });

    req.on('error', (error) => {
      resolve({ path, error: error.message });
    });

    if (body) {
      req.write(body);
    }
    req.end();
  });
}

async function main() {
  console.log('Testing endpoints...\n');

  // First, try GET on deliverables endpoints
  for (const endpoint of endpoints) {
    const result = await testEndpoint(endpoint, 'GET');
    console.log(`GET ${endpoint}`);
    console.log(`  Status: ${result.status}`);
    if (result.response && result.response.length < 500) {
      console.log(`  Response: ${result.response}`);
    }
    console.log('');
  }

  // Try POST on the most likely endpoint
  const data = JSON.stringify({
    deliverable_url: "https://clawhub.com/skills/near-multi-account-manager",
    notes: "Test"
  });

  const postResult = await testEndpoint('/v1/jobs/6b2a1efe-07bd-4e2b-b817-77f938209215/deliverable', 'POST', data);
  console.log(`POST /v1/jobs/6b2a1efe-07bd-4e2b-b817-77f938209215/deliverable`);
  console.log(`  Status: ${postResult.status}`);
  console.log(`  Response: ${postResult.response}`);
}

main();
