import { SoundCloudWatcher } from './soundcloud_watcher';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

interface PluginConfig {
  clientId: string;
  clientSecret: string;
  username: string;
  checkIntervalHours: number;
  myTracksLimit: number;
  dormantDays: number;
  includeLinks: boolean;
  sessionKey?: string;
}

function loadConfig(): PluginConfig | null {
  // Try loading from env file first
  const envPath = join(homedir(), '.openclaw', 'secrets', 'soundcloud.env');
  if (existsSync(envPath)) {
    const content = readFileSync(envPath, 'utf-8');
    const env: Record<string, string> = {};
    for (const line of content.split('\n')) {
      const trimmed = line.trim();
      if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
        const [key, ...rest] = trimmed.split('=');
        env[key.trim()] = rest.join('=').trim();
      }
    }
    if (env.SOUNDCLOUD_CLIENT_ID && env.SOUNDCLOUD_CLIENT_SECRET && env.MY_USERNAME) {
      return {
        clientId: env.SOUNDCLOUD_CLIENT_ID,
        clientSecret: env.SOUNDCLOUD_CLIENT_SECRET,
        username: env.MY_USERNAME,
        checkIntervalHours: 6,
        myTracksLimit: 10,
        dormantDays: 90,
        includeLinks: env.INCLUDE_LINKS !== 'false',  // Default: true
        sessionKey: 'agent:main:main',
      };
    }
  }
  return null;
}

export default function register(api: any) {
  const logger = api.getLogger?.() || console;
  let watcher: SoundCloudWatcher | null = null;

  function getWatcher(): SoundCloudWatcher | null {
    if (watcher) return watcher;
    
    const config = loadConfig();
    if (!config) return null;
    
    watcher = new SoundCloudWatcher({
      clientId: config.clientId,
      clientSecret: config.clientSecret,
      username: config.username,
      myTracksLimit: config.myTracksLimit,
      dormantDays: config.dormantDays,
      includeLinks: config.includeLinks,
      logger: (...args: any[]) => logger.debug?.(...args) || console.log(...args),
    });
    return watcher;
  }

  function getSetupMessage(): string {
    const config = loadConfig();
    
    if (config) {
      return `# SoundCloud Watcher Setup

Already configured!

- Username: ${config.username}
- Client ID: ${config.clientId.substring(0, 8)}...${config.clientId.slice(-4)}
- Check interval: ${config.checkIntervalHours} hours

To update credentials, edit:
\`~/.openclaw/secrets/soundcloud.env\`

Then restart: \`openclaw gateway restart\``;
    }
    
    return `# SoundCloud Watcher Setup

Not configured yet.

## Steps:

1. Get credentials from https://soundcloud.com/you/apps

2. Create config file:
\`\`\`bash
nano ~/.openclaw/secrets/soundcloud.env
\`\`\`

3. Add your credentials:
\`\`\`
SOUNDCLOUD_CLIENT_ID=your_client_id
SOUNDCLOUD_CLIENT_SECRET=your_client_secret
MY_USERNAME=your_soundcloud_username
\`\`\`

4. Restart: \`openclaw gateway restart\`

5. Verify: \`/soundcloud-status\``;
  }

  // Register commands
  api.registerCommand({
    name: 'soundcloud-setup',
    description: 'Show SoundCloud watcher setup instructions',
    handler: async () => {
      return { text: getSetupMessage() };
    },
  });

  api.registerCommand({
    name: 'soundcloud-status',
    description: 'Show SoundCloud watcher status',
    handler: async () => {
      const w = getWatcher();
      if (!w) return { text: 'Not configured. Run /soundcloud-setup for instructions.' };
      const result = await w.status();
      return { text: result };
    },
  });

  api.registerCommand({
    name: 'soundcloud-check',
    description: 'Run an immediate SoundCloud check',
    handler: async () => {
      const w = getWatcher();
      if (!w) return { text: 'Not configured. Run /soundcloud-setup for instructions.' };
      const result = await w.check();
      return { text: result };
    },
  });

  api.registerCommand({
    name: 'soundcloud-add',
    description: 'Add artist(s) to track',
    handler: async (ctx: any) => {
      const w = getWatcher();
      if (!w) return { text: 'Not configured. Run /soundcloud-setup for instructions.' };
      
      const args = ctx.args?.trim();
      if (!args) return { text: 'Usage: /soundcloud-add <username> [username2] ...' };
      
      const usernames = args.split(/\s+/).filter(Boolean);
      const result = await w.addArtists(usernames);
      return { text: result };
    },
  });

  api.registerCommand({
    name: 'soundcloud-remove',
    description: 'Remove an artist from tracking',
    handler: async (ctx: any) => {
      const w = getWatcher();
      if (!w) return { text: 'Not configured. Run /soundcloud-setup for instructions.' };
      
      const username = ctx.args?.trim();
      if (!username) return { text: 'Usage: /soundcloud-remove <username>' };
      
      const result = await w.removeArtist(username);
      return { text: result };
    },
  });

  api.registerCommand({
    name: 'soundcloud-list',
    description: 'List all tracked artists',
    handler: async () => {
      const w = getWatcher();
      if (!w) return { text: 'Not configured. Run /soundcloud-setup for instructions.' };
      const result = await w.listArtists();
      return { text: result };
    },
  });

  api.registerCommand({
    name: 'soundcloud-cron',
    description: 'Run check for cron (only outputs if there are updates)',
    handler: async () => {
      const w = getWatcher();
      if (!w) {
        (logger.warn ?? console.warn).call(logger, 'SoundCloud cron: not configured');
        return { text: '' };  // Silent fail for cron
      }
      try {
        const result = await w.runCron();
        if (result) {
          return { text: result };
        }
        // No updates - return empty (silent success)
        (logger.debug ?? console.log).call(logger, 'SoundCloud cron: no updates');
        return { text: '' };
      } catch (e) {
        (logger.error ?? console.error).call(logger, 'SoundCloud cron error:', e);
        return { text: `SoundCloud check failed: ${e}` };
      }
    },
  });

  (logger.info ?? console.log).call(logger, 'SoundCloud Watcher plugin loaded');
}
