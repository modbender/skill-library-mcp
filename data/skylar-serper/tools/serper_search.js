const https = require('https');

async function serper_search(params) {
  const apiKey = process.env.SERPER_API_KEY;
  
  if (!apiKey) {
    throw new Error('SERPER_API_KEY not found in environment. Add it to your .env or TOOLS.md');
  }
  
  if (!params.q) {
    throw new Error('Parameter "q" (query) is required');
  }
  
  const body = JSON.stringify({
    q: params.q,
    num: params.num || 5,
    ...(params.gl && { gl: params.gl }),
    ...(params.hl && { hl: params.hl })
  });
  
  const options = {
    hostname: 'google.serper.dev',
    path: '/search',
    method: 'POST',
    headers: {
      'X-API-KEY': apiKey,
      'Content-Type': 'application/json'
    }
  };
  
  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          if (res.statusCode !== 200) {
            reject(new Error(`Serper API error: ${res.statusCode} - ${data}`));
            return;
          }
          
          const json = JSON.parse(data);
          
          if (!json.organic || json.organic.length === 0) {
            resolve('No results found.');
            return;
          }
          
          const results = json.organic.map((item, idx) => {
            return `${idx + 1}. **${item.title}**\n   ${item.link}\n   ${item.snippet}`;
          }).join('\n\n');
          
          resolve(results);
        } catch (err) {
          reject(new Error(`Failed to parse response: ${err.message}`));
        }
      });
    });
    
    req.on('error', (err) => {
      reject(new Error(`Request failed: ${err.message}`));
    });
    
    req.write(body);
    req.end();
  });
}

module.exports = { serper_search };
