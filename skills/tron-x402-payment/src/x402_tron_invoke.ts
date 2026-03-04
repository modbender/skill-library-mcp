#!/usr/bin/env node
import {
  TronClientSigner,
  X402Client,
  X402FetchClient,
  ExactTronClientMechanism
} from '@open-aibank/x402-tron';
// @ts-ignore
import TronWeb from 'tronweb';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

async function findPrivateKey(): Promise<string | undefined> {
  // 1. Check environment variable
  if (process.env.TRON_PRIVATE_KEY) {
    return process.env.TRON_PRIVATE_KEY;
  }

  // 2. Check local config files silently
  const configFiles = [
    path.join(process.cwd(), 'x402-config.json'),
    path.join(os.homedir(), '.x402-config.json')
  ];

  for (const file of configFiles) {
    if (fs.existsSync(file)) {
      try {
        const config = JSON.parse(fs.readFileSync(file, 'utf8'));
        const key = config.private_key || config.tron_private_key;
        if (key) return key;
      } catch (e) {
        // ignore malformed config
      }
    }
  }

  // 3. Check mcporter config (AIBank standard)
  const mcporterPath = path.join(os.homedir(), '.mcporter', 'mcporter.json');
  if (fs.existsSync(mcporterPath)) {
    try {
      const config = JSON.parse(fs.readFileSync(mcporterPath, 'utf8'));
      // Try to find the key in any likely server config, prioritizing tron-mcp-server
      const server = config.mcpServers?.['tron-mcp-server'];
      if (server?.env?.TRON_PRIVATE_KEY) {
        return server.env.TRON_PRIVATE_KEY;
      }
      
      // Fallback: check all servers for the env var
      if (config.mcpServers) {
        for (const serverName in config.mcpServers) {
          const s = config.mcpServers[serverName];
          if (s?.env?.TRON_PRIVATE_KEY) {
            return s.env.TRON_PRIVATE_KEY;
          }
        }
      }
    } catch (e) {
      // ignore
    }
  }

  return undefined;
}

async function findApiKey(): Promise<string | undefined> {
  // 1. Check environment variable
  if (process.env.TRON_GRID_API_KEY) {
    return process.env.TRON_GRID_API_KEY;
  }

  // 2. Check local config files silently
  const configFiles = [
    path.join(process.cwd(), 'x402-config.json'),
    path.join(os.homedir(), '.x402-config.json')
  ];

  for (const file of configFiles) {
    if (fs.existsSync(file)) {
      try {
        const config = JSON.parse(fs.readFileSync(file, 'utf8'));
        const key = config.tron_grid_api_key || config.api_key;
        if (key) return key;
      } catch (e) {
        // ignore malformed config
      }
    }
  }

  // 3. Check mcporter config (AIBank standard)
  const mcporterPath = path.join(os.homedir(), '.mcporter', 'mcporter.json');
  if (fs.existsSync(mcporterPath)) {
    try {
      const config = JSON.parse(fs.readFileSync(mcporterPath, 'utf8'));
      // Try to find the key in any likely server config, prioritizing tron-mcp-server
      const server = config.mcpServers?.['tron-mcp-server'];
      if (server?.env?.TRON_GRID_API_KEY) {
        return server.env.TRON_GRID_API_KEY;
      }
      
      // Fallback: check all servers for the env var
      if (config.mcpServers) {
        for (const serverName in config.mcpServers) {
          const s = config.mcpServers[serverName];
          if (s?.env?.TRON_GRID_API_KEY) {
            return s.env.TRON_GRID_API_KEY;
          }
        }
      }
    } catch (e) {
      // ignore
    }
  }

  return undefined;
}

async function main() {
  // Parse arguments
  const args = process.argv.slice(2);
  const options: Record<string, string> = {};
  
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const value = args[i + 1];
      if (value && !value.startsWith('--')) {
        options[key] = value;
        i++;
      } else {
        options[key] = 'true';
      }
    }
  }

  const url = options.url;
  const entrypoint = options.entrypoint;
  const inputRaw = options.input;
  const methodArg = options.method;
  const networkName = options.network || 'nile';
  const checkStatus = options.check === 'true' || options.status === 'true';

  if (checkStatus) {
    const privateKey = await findPrivateKey();
    if (!privateKey) {
      console.error('[ERROR] TRON_PRIVATE_KEY is missing or not configured.');
      process.exit(1);
    }

    const apiKey = await findApiKey();
    if (networkName === 'mainnet' && !apiKey) {
      console.error('[WARNING] TRON_GRID_API_KEY is missing. Mainnet requests may be rate-limited or fail.');
    } else if (apiKey) {
      console.error('[OK] TRON_GRID_API_KEY is configured.');
    }

    try {
      const networks: Record<string, any> = {
        mainnet: { fullHost: 'https://api.trongrid.io' },
        shasta: { fullHost: 'https://api.shasta.trongrid.io' },
        nile: { fullHost: 'https://nile.trongrid.io' }
      };
      const config = networks[networkName] || networks.nile;
      const tronWeb = new TronWeb({
        fullHost: config.fullHost,
        privateKey: privateKey
      });
      const address = tronWeb.address.fromPrivateKey(privateKey);
      console.error(`[OK] Wallet configured (Address: ${address}) on ${networkName}`);
      process.exit(0);
    } catch (e) {
      console.error(`[ERROR] Failed to derive address from key: ${(e as any).message}`);
      process.exit(1);
    }
  }

  if (!url) {
    console.error('Error: --url is required');
    process.exit(1);
  }

  let finalUrl = url;
  let finalMethod = methodArg || 'GET';
  let finalBody: string | undefined = undefined;

  // Logic 1: v2 Agent Invoke (url + entrypoint)
  if (entrypoint) {
    // Remove trailing slash if present
    const baseUrl = url.endsWith('/') ? url.slice(0, -1) : url;
    finalUrl = `${baseUrl}/entrypoints/${entrypoint}/invoke`;
    finalMethod = 'POST';

    // Parse input if provided
    let inputData = {};
    if (inputRaw) {
      try {
        inputData = JSON.parse(inputRaw);
      } catch (e) {
        // Fallback for simple string input or invalid JSON
        inputData = inputRaw;
      }
    }
    finalBody = JSON.stringify({ input: inputData });
  }
  // Logic 2: Direct/Legacy
  else {
    if (methodArg) {
      finalMethod = methodArg.toUpperCase();
    }
    
    if (inputRaw) {
      finalBody = inputRaw;
    }
  }

  const privateKey = await findPrivateKey();
  if (!privateKey) {
    console.error('Error: Payment credentials not found. Missing environment variable: TRON_PRIVATE_KEY.');
    console.error('Please set TRON_PRIVATE_KEY before running this tool.');
    console.error('Alternatively, configure ~/.mcporter/mcporter.json or x402-config.json.');
    console.error('Agent: DO NOT attempt to search for or read private keys from files manually.');
    process.exit(1);
  }

  // Network configuration
  const networks: Record<string, any> = {
    mainnet: {
      fullHost: 'https://api.trongrid.io',
      network: 'mainnet'
    },
    shasta: {
      fullHost: 'https://api.shasta.trongrid.io',
      network: 'shasta'
    },
    nile: {
      fullHost: 'https://nile.trongrid.io',
      network: 'nile'
    }
  };

  const config = networks[networkName] || networks.nile;

  // Check for TRON_GRID_API_KEY to avoid rate limits
  const apiKey = await findApiKey();
  if (apiKey) {
    console.error('[x402] Using TRON_GRID_API_KEY for connection.');
  }

  try {
    // 1. Initialize TronWeb
    // Redirect console.log to console.error to prevent library pollution of STDOUT
    // The library uses console.log for debug info (e.g. signing details, allowance checks)
    // which violates the x402 Agent protocol (STDOUT is exclusive for final JSON).
    const originalConsoleLog = console.log;
    console.log = console.error;

    const tronWebOptions: any = {
      fullHost: config.fullHost,
      privateKey: privateKey
    };

    if (apiKey) {
      tronWebOptions.headers = { 'TRON-PRO-API-KEY': apiKey };
    }

    const tronWeb = new TronWeb(tronWebOptions);

    // 2. Initialize Signer
    // Use config.network to ensure we use a valid/supported network name (e.g. 'nile' instead of 'foo')
    const signer = TronClientSigner.fromTronWeb(tronWeb, config.network);
    console.error(`[x402] Initialized signer for address: ${signer.getAddress()} on network: ${config.network}`);

    // 3. Initialize Mechanism
    const mechanism = new ExactTronClientMechanism(signer);

    // 4. Initialize Core Client
    const client = new X402Client();
    // Register ONLY for the configured network to avoid signing for wrong networks
    client.register(`tron:${config.network}`, mechanism);

    // 5. Initialize Fetch Client
    const fetchClient = new X402FetchClient(client);

    // 6. Execute Request
    console.error(`[x402] Requesting: ${finalMethod} ${finalUrl}`);
    
    const requestInit: RequestInit = {
      method: finalMethod,
      headers: {
        'Content-Type': 'application/json'
      }
    };

    if (finalBody) {
      requestInit.body = finalBody;
    }

    const response = await fetchClient.request(finalUrl, requestInit);

    // 7. Output Result
    console.error(`[x402] Response Status: ${response.status}`);
    
    // Check for payment response headers (settlement info)
    const paymentResponse = response.headers.get('PAYMENT-RESPONSE');
    if (paymentResponse) {
      try {
        const settlement = JSON.parse(Buffer.from(paymentResponse, 'base64').toString());
        console.error(`[x402] Payment Settled: ${settlement.txHash || 'Confirmed'}`);
      } catch (e) {
        // ignore
      }
    }

    const contentType = response.headers.get('content-type') || '';
    let responseBody;
    
    if (contentType.includes('application/json')) {
      responseBody = await response.json();
    } else if (contentType.includes('image/') || contentType.includes('application/octet-stream')) {
      const arrayBuffer = await response.arrayBuffer();
      const buffer = Buffer.from(arrayBuffer);
      
      const tmpDir = os.tmpdir();
      const isImage = contentType.includes('image/');
      const ext = isImage ? (contentType.split('/')[1]?.split(';')[0] || 'bin') : 'bin';
      const prefix = isImage ? 'x402_image' : 'x402_binary';
      const fileName = `${prefix}_${Date.now()}_${Math.random().toString(36).substring(7)}.${ext}`;
      const filePath = path.join(tmpDir, fileName);
      
      fs.writeFileSync(filePath, buffer);
      console.error(`[x402] Binary data saved to temporary file: ${filePath}`);
      console.error(`[x402] Please delete this file after use.`);

      responseBody = {
        file_path: filePath,
        content_type: contentType,
        bytes: buffer.length
      };
    } else {
      responseBody = await response.text();
    }

    // Print final result to STDOUT for the agent to consume
    // Use process.stdout directly to bypass the console.log redirection
    process.stdout.write(JSON.stringify({
      status: response.status,
      headers: Object.fromEntries(response.headers.entries()),
      body: responseBody,
      isBase64: false
    }, null, 2) + '\n');

  } catch (error: any) {
    let message = error.message || 'Unknown error';
    let stack = error.stack || '';

    // Sanitize any potential private key leaks in error messages/stacks
    if (privateKey) {
      const escapedKey = privateKey.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const keyRegex = new RegExp(escapedKey, 'g');
      message = message.replace(keyRegex, '[REDACTED]');
      stack = stack.replace(keyRegex, '[REDACTED]');
    }

    console.error(`[x402] Error: ${message}`);
    process.stdout.write(JSON.stringify({
      error: message,
      stack: stack
    }, null, 2) + '\n');
    process.exit(1);
  }
}

main();
