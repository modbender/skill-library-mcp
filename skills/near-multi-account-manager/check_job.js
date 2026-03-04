const https = require('https');

const options = {
  hostname: 'market.near.ai',
  port: 443,
  path: '/v1/jobs/6b2a1efe-07bd-4e2b-b817-77f938209215',
  method: 'GET',
  headers: {
    'Authorization': 'Bearer sk_live_iOQS6NKYgLCf8sAcIsjeNpIvsN9ml7fK6CVrfIyPIVs'
  }
};

const req = https.request(options, (res) => {
  console.log(`Status: ${res.statusCode}`);

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

req.end();
