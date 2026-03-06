/**
 * Tunnel Manager - Cloudflare Tunnel + Telnyx Call Control App auto-setup
 * 
 * Starts a Cloudflare quick tunnel and automatically creates/updates
 * a Telnyx Call Control Application with the webhook URL.
 */

import 'dotenv/config';
import { spawn, ChildProcess } from 'child_process';
import { createHash } from 'crypto';

// Generate a short consistent hash from a string (for unique but repeatable subdomains)
function shortHash(str: string): string {
  return createHash('sha256').update(str).digest('hex').substring(0, 8);
}

interface TunnelConfig {
  port: number;
  telnyxApiKey: string;
  connectionId: string;
  appName?: string;
  sipSubdomain?: string;
}

interface TunnelResult {
  publicUrl: string;
  webhookUrl: string;
  process: ChildProcess;
  callControlAppId?: string;
  sipAddress?: string;
}

// Store app ID for reuse across restarts
let cachedAppId: string | null = null;

/**
 * Start Cloudflare tunnel and set up Telnyx Call Control App
 */
export async function startTunnel(config: TunnelConfig): Promise<TunnelResult> {
  const { 
    port, 
    telnyxApiKey, 
    appName = 'openclaw-voice',
    sipSubdomain: configSubdomain,
  } = config;
  
  // Generate consistent subdomain: identity name + short hash (same identity = same subdomain)
  // e.g., "assistant" -> "assistant-a1b2c3d4"
  const sipSubdomain = configSubdomain 
    ? `${configSubdomain}-${shortHash(configSubdomain)}`
    : `openclaw-${Date.now().toString(36)}`;

  console.log('🚇 Starting Cloudflare tunnel...');

  const { publicUrl, process: tunnelProcess } = await startCloudflareTunnel(port);
  
  const webhookUrl = `${publicUrl}/voice/webhook`;
  console.log(`✅ Tunnel established: ${publicUrl}`);
  console.log(`📝 Webhook URL: ${webhookUrl}`);

  // Create or update Call Control Application
  console.log(`\n🔗 Setting up Telnyx Call Control Application...`);
  
  let callControlAppId: string | undefined;
  let sipAddress: string | undefined;

  try {
    const result = await setupCallControlApp({
      telnyxApiKey,
      webhookUrl,
      appName,
      sipSubdomain,
      identityPrefix: configSubdomain || 'openclaw',
    });
    callControlAppId = result.appId;
    sipAddress = result.sipAddress;
    console.log(`✅ Call Control App ready`);
    console.log(`   App ID: ${callControlAppId}`);
    console.log(`   SIP: ${sipAddress}`);
  } catch (error) {
    console.error('❌ Failed to set up Call Control App:', error);
    console.log('\n⚠️  You may need to create the app manually in the Telnyx portal');
  }

  return { 
    publicUrl, 
    webhookUrl, 
    process: tunnelProcess,
    callControlAppId,
    sipAddress,
  };
}

/**
 * Create or update a Telnyx Call Control Application
 */
async function setupCallControlApp(config: {
  telnyxApiKey: string;
  webhookUrl: string;
  appName: string;
  sipSubdomain: string;
  identityPrefix: string;
}): Promise<{ appId: string; sipAddress: string }> {
  const { telnyxApiKey, webhookUrl, appName, sipSubdomain, identityPrefix } = config;
  const headers = {
    'Authorization': `Bearer ${telnyxApiKey}`,
    'Content-Type': 'application/json',
  };

  // Try to find existing app by name or use cached ID
  let appId = cachedAppId;
  
  if (!appId) {
    // Search for existing app matching THIS identity
    // Look for apps with SIP subdomain starting with identity prefix (e.g., "assistant-")
    const listResponse = await fetch(
      `https://api.telnyx.com/v2/call_control_applications`,
      { headers }
    );
    
    if (listResponse.ok) {
      const listData = await listResponse.json();
      // Match by SIP subdomain starting with identity prefix (priority)
      // e.g., "assistant-mkzimsgd" matches identity "assistant"
      // Prioritize subdomain match over app name match to preserve existing SIP addresses
      let existingApp = listData.data?.find((app: any) => {
        const subdomain = app.inbound?.sip_subdomain || '';
        return subdomain.startsWith(`${identityPrefix}-`) || subdomain === identityPrefix;
      });
      
      // Fall back to app name match if no subdomain match
      if (!existingApp) {
        existingApp = listData.data?.find((app: any) => 
          app.application_name === appName || 
          app.application_name.startsWith(`${appName}-`)
        );
      }
      if (existingApp) {
        appId = existingApp.id;
        console.log(`   Found existing app for this identity: ${existingApp.application_name}`);
        console.log(`   Reusing SIP subdomain: ${existingApp.inbound?.sip_subdomain}`);
      }
    }
  }

  if (appId) {
    // Update existing app
    const updateResponse = await fetch(
      `https://api.telnyx.com/v2/call_control_applications/${appId}`,
      {
        method: 'PATCH',
        headers,
        body: JSON.stringify({
          webhook_event_url: webhookUrl,
          active: true,
        }),
      }
    );

    if (!updateResponse.ok) {
      const error = await updateResponse.text();
      throw new Error(`Failed to update app: ${error}`);
    }

    const updateData = await updateResponse.json();
    cachedAppId = appId;
    const subdomain = updateData.data.inbound?.sip_subdomain || sipSubdomain;
    return {
      appId,
      sipAddress: `sip:openclaw@${subdomain}.sip.telnyx.com`,
    };
  }

  // Create new app
  console.log(`   Creating new Call Control Application...`);
  const createResponse = await fetch(
    'https://api.telnyx.com/v2/call_control_applications',
    {
      method: 'POST',
      headers,
      body: JSON.stringify({
        application_name: `${appName}-${Date.now()}`,
        webhook_event_url: webhookUrl,
        webhook_api_version: '2',
        active: true,
        first_command_timeout: true,
        first_command_timeout_secs: 30,
        inbound: {
          sip_subdomain: sipSubdomain,
          sip_subdomain_receive_settings: 'from_anyone',
        },
      }),
    }
  );

  if (!createResponse.ok) {
    const error = await createResponse.text();
    // Check if subdomain already taken
    if (error.includes('already in use')) {
      // Try with unique subdomain
      const uniqueSubdomain = `${sipSubdomain}-${Date.now().toString(36)}`;
      return setupCallControlApp({
        ...config,
        sipSubdomain: uniqueSubdomain,
      });
    }
    throw new Error(`Failed to create app: ${error}`);
  }

  const createData = await createResponse.json();
  cachedAppId = createData.data.id;
  const subdomain = createData.data.inbound?.sip_subdomain || sipSubdomain;
  
  return {
    appId: createData.data.id,
    sipAddress: `sip:openclaw@${subdomain}.sip.telnyx.com`,
  };
}

/**
 * Start cloudflared quick tunnel (no account required)
 */
function startCloudflareTunnel(port: number): Promise<{ publicUrl: string; process: ChildProcess }> {
  return new Promise((resolve, reject) => {
    const tunnelProcess = spawn('cloudflared', ['tunnel', '--url', `http://localhost:${port}`], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    let resolved = false;
    const timeout = setTimeout(() => {
      if (!resolved) {
        reject(new Error('Tunnel startup timed out (30s)'));
        tunnelProcess.kill();
      }
    }, 30000);

    tunnelProcess.stderr?.on('data', (data: Buffer) => {
      const output = data.toString();
      const urlMatch = output.match(/https:\/\/[a-z0-9-]+\.trycloudflare\.com/);
      if (urlMatch && !resolved) {
        resolved = true;
        clearTimeout(timeout);
        resolve({ publicUrl: urlMatch[0], process: tunnelProcess });
      }
      if (output.includes('ERR') || output.includes('error')) {
        console.error('[cloudflared]', output.trim());
      }
    });

    tunnelProcess.on('error', (err) => {
      clearTimeout(timeout);
      reject(new Error(`Failed to start cloudflared: ${err.message}`));
    });

    tunnelProcess.on('exit', (code) => {
      if (!resolved) {
        clearTimeout(timeout);
        reject(new Error(`cloudflared exited with code ${code}`));
      }
    });
  });
}

/**
 * Graceful shutdown
 */
export async function stopTunnel(tunnelProcess?: ChildProcess): Promise<void> {
  if (tunnelProcess) {
    console.log('\n🛑 Shutting down tunnel...');
    tunnelProcess.kill();
    console.log('✅ Tunnel closed');
  }
}

// CLI mode
if (import.meta.url === `file://${process.argv[1]}`) {
  const PORT = parseInt(process.env.PORT || '3000', 10);
  const TELNYX_API_KEY = process.env.TELNYX_API_KEY;
  const CONNECTION_ID = process.env.TELNYX_CONNECTION_ID;

  if (!TELNYX_API_KEY) {
    console.error('❌ Missing TELNYX_API_KEY');
    process.exit(1);
  }

  startTunnel({
    port: PORT,
    telnyxApiKey: TELNYX_API_KEY,
    connectionId: CONNECTION_ID || '',
  })
    .then(({ webhookUrl, sipAddress }) => {
      console.log('\n🎉 Ready!');
      console.log(`   Webhook: ${webhookUrl}`);
      if (sipAddress) console.log(`   Dial: ${sipAddress}`);
      console.log('\nPress Ctrl+C to stop.');
    })
    .catch((error) => {
      console.error('Failed:', error);
      process.exit(1);
    });

  process.on('SIGINT', async () => {
    await stopTunnel();
    process.exit(0);
  });
}
