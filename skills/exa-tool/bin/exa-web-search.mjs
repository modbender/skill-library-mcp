#!/usr/bin/env node
/**
 * Exa Web Search - Simple wrapper for web_search_exa
 *
 * Usage: exa-web-search '{"query":"...", "count":10, "freshness":"pw"}'
 */

import https from 'https';

async function main() {
  const argsString = process.argv[2];

  if (!argsString) {
    console.error('Usage: exa-web-search \'{"query":"...", "count":10, "freshness":"pw"}\'');
    process.exit(1);
  }

  let args;
  try {
    args = JSON.parse(argsString);
  } catch (e) {
    console.error('ERROR: Invalid JSON:', e.message);
    process.exit(1);
  }

  const token = process.env.EXA_API_KEY;
  if (!token) {
    console.error('ERROR: EXA_API_KEY environment variable not set');
    process.exit(1);
  }

  const payload = {
    jsonrpc: '2.0',
    method: 'tools/call',
    params: {
      name: 'web_search_exa',
      arguments: args
    },
    id: Date.now()
  };

  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/json, text/event-stream'
    }
  };

  const results = [];

  const req = https.request('https://mcp.exa.ai/mcp', options, (res) => {
    let buffer = '';
    res.on('data', (chunk) => {
      buffer += chunk.toString();
      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (line.startsWith('data:')) {
          const data = line.slice(5).trim();
          if (data === '[DONE]') continue;
          try {
            const parsed = JSON.parse(data);
            results.push(parsed);
          } catch (e) {}
        }
      }
    });

    res.on('end', () => {
      let finalResult = null;
      for (let i = results.length - 1; i >= 0; i--) {
        if (results[i].result) {
          finalResult = results[i];
          break;
        }
        if (results[i].error) {
          console.error(JSON.stringify(results[i].error, null, 2));
          process.exit(1);
        }
      }

      if (finalResult && finalResult.result) {
        console.log(JSON.stringify(finalResult.result, null, 2));
        process.exit(0);
      } else {
        console.error('ERROR: No result in response');
        process.exit(1);
      }
    });
  });

  req.on('error', (e) => {
    console.error('ERROR:', e.message);
    process.exit(1);
  });

  req.write(JSON.stringify(payload));
  req.end();
}

main();