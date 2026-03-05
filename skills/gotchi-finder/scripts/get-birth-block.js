const https = require('https');

const SUBGRAPH_URL = 'https://api.goldsky.com/api/public/project_cm4b9xy95tko101tb1tyxaqw5/subgraphs/aavegotchi-core-base/1.0.0/gn';

async function getBirthBlock(tokenId) {
  const query = `
    query {
      aavegotchi(id: "${tokenId}") {
        id
        createdAt
        createdBlockNumber
        timesTraded
      }
    }
  `;

  return new Promise((resolve, reject) => {
    const data = JSON.stringify({ query });
    const url = new URL(SUBGRAPH_URL);
    
    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          resolve(result);
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

const tokenId = process.argv[2];
if (!tokenId) {
  console.error('Usage: node get-birth-block.js <tokenId>');
  process.exit(1);
}

getBirthBlock(tokenId).then(result => {
  console.log(JSON.stringify(result, null, 2));
}).catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
