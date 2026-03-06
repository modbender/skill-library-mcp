const https = require('https');

const data = JSON.stringify({
  deliverable_url: "https://clawhub.com/skills/near-multi-account-manager",
  notes: "Complete NEAR Multi-Account Manager skill with secure credential storage, account switching, balance checking, transfers, transaction tracking, and account summaries."
});

const options = {
  hostname: 'market.near.ai',
  port: 443,
  path: '/v1/jobs/6b2a1efe-07bd-4e2b-b817-77f938209215/submit',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer sk_live_iOQS6NKYgLCf8sAcIsjeNpIvsN9ml7fK6CVrfIyPIVs',
    'Content-Length': data.length
  }
};

const req = https.request(options, (res) => {
  console.log(`Status: ${res.statusCode}`);
  console.log(`Headers: ${JSON.stringify(res.headers)}`);

  res.setEncoding('utf8');
  let responseData = '';
  res.on('data', (chunk) => {
    responseData += chunk;
  });
  res.on('end', () => {
    console.log('Response:', responseData);
  });
});

req.on('error', (error) => {
  console.error('Error:', error);
});

req.write(data);
req.end();
