const FormData = require('form-data');
const https = require('https');
const fs = require('fs');

function uploadToIPFS(filePathOrBuffer) {
  const jwt = process.env.PINATA_JWT;
  if (!jwt) {
    throw new Error('PINATA_JWT environment variable not set');
  }

  return new Promise((resolve, reject) => {
    // Read file if path is provided, otherwise use buffer directly
    const buffer = Buffer.isBuffer(filePathOrBuffer) 
      ? filePathOrBuffer 
      : fs.readFileSync(filePathOrBuffer);
    
    const form = new FormData();
    form.append('file', buffer, {
      filename: 'encrypted.bin',
      contentType: 'application/octet-stream',
    });

    const options = {
      hostname: 'api.pinata.cloud',
      path: '/pinning/pinFileToIPFS',
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + jwt,
        ...form.getHeaders(),
      },
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => { body += chunk; });
      res.on('end', () => {
        if (res.statusCode !== 200) {
          reject(new Error('Pinata upload failed: ' + res.statusCode + ' - ' + body));
          return;
        }
        resolve(JSON.parse(body).IpfsHash);
      });
    });

    req.on('error', reject);
    form.pipe(req);
  });
}

module.exports = { uploadToIPFS };
