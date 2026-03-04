import os from 'os';
import path from 'path';
import fs from 'fs';
import readline from 'readline';

export interface ChromeProfile {
  id: string;
  name: string;
  path: string;
}

function getChromeUserDataDir(): string {
  const platform = process.platform;
  
  switch (platform) {
    case 'darwin': // macOS
      return path.join(os.homedir(), 'Library', 'Application Support', 'Google', 'Chrome');
    case 'win32': // Windows
      return path.join(os.homedir(), 'AppData', 'Local', 'Google', 'Chrome', 'User Data');
    case 'linux': // Linux
      return path.join(os.homedir(), '.config', 'google-chrome');
    default:
      throw new Error(`Unsupported platform: ${platform}`);
  }
}

function getProfileName(profilePath: string): string {
  try {
    const prefsPath = path.join(profilePath, 'Preferences');
    if (!fs.existsSync(prefsPath)) {
      return 'Unnamed';
    }
    
    const prefs = JSON.parse(fs.readFileSync(prefsPath, 'utf-8'));
    return prefs?.profile?.name || prefs?.account_info?.[0]?.given_name || 'Unnamed';
  } catch {
    return 'Unnamed';
  }
}

export function listChromeProfiles(): ChromeProfile[] {
  const userDataDir = getChromeUserDataDir();
  
  if (!fs.existsSync(userDataDir)) {
    return [];
  }
  
  const profiles: ChromeProfile[] = [];
  
  // Check for Default profile
  const defaultPath = path.join(userDataDir, 'Default');
  if (fs.existsSync(defaultPath)) {
    profiles.push({
      id: 'Default',
      name: getProfileName(defaultPath),
      path: defaultPath
    });
  }
  
  // Check for Profile 1, 2, 3, etc.
  const entries = fs.readdirSync(userDataDir);
  const profileDirs = entries
    .filter(entry => entry.startsWith('Profile '))
    .sort((a, b) => {
      const numA = parseInt(a.replace('Profile ', ''), 10);
      const numB = parseInt(b.replace('Profile ', ''), 10);
      return numA - numB;
    });
  
  for (const profileDir of profileDirs) {
    const profilePath = path.join(userDataDir, profileDir);
    profiles.push({
      id: profileDir,
      name: getProfileName(profilePath),
      path: profilePath
    });
  }
  
  return profiles;
}

export function getProfileById(profileId: string): ChromeProfile | undefined {
  const profiles = listChromeProfiles();
  return profiles.find(p => p.id === profileId);
}

export async function promptProfileSelection(): Promise<ChromeProfile | null> {
  const profiles = listChromeProfiles();
  
  if (profiles.length === 0) {
    console.log('❌ No Chrome profiles found.');
    return null;
  }
  
  if (profiles.length === 1) {
    console.log(`✅ Using only available profile: ${profiles[0].name} (${profiles[0].id})`);
    return profiles[0];
  }
  
  console.log('\n📋 Found Chrome profiles:\n');
  
  profiles.forEach((profile, index) => {
    const marker = profile.id === 'Default' ? ' (default)' : '';
    console.log(`  ${index + 1}) ${profile.name}${marker} [${profile.id}]`);
  });
  
  console.log(`  n) None - use incognito/test profile`);
  
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  return new Promise((resolve) => {
    rl.question('\nSelect profile (1-' + profiles.length + ', or n): ', (answer: string) => {
      rl.close();
      
      if (answer.toLowerCase() === 'n') {
        console.log('⏭️  Using incognito mode (no profile)');
        resolve(null);
        return;
      }
      
      const selection = parseInt(answer, 10);
      if (isNaN(selection) || selection < 1 || selection > profiles.length) {
        console.log('⚠️  Invalid selection, using incognito mode');
        resolve(null);
        return;
      }
      
      const selected = profiles[selection - 1];
      console.log(`✅ Selected profile: ${selected.name} [${selected.id}]`);
      resolve(selected);
    });
  });
}

export function createChromeProfile(name: string): ChromeProfile & { welcomePage: string } {
  const userDataDir = getChromeUserDataDir();
  
  // Sanitize profile name to prevent directory traversal
  const safeName = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
  const profileId = `Profile-${safeName}`;
  
  // Validate profileId doesn't contain path traversal characters
  const safeProfileId = profileId.replace(/[^a-zA-Z0-9-_]/g, '');
  if (!safeProfileId || safeProfileId !== profileId) {
    throw new Error('Invalid profile name');
  }
  
  const profilePath = path.join(userDataDir, safeProfileId);
  
  if (fs.existsSync(profilePath)) {
    throw new Error(`Profile "${profileId}" already exists`);
  }
  
  // Create profile directory
  fs.mkdirSync(profilePath, { recursive: true });
  
  // Get welcome page path
  const welcomePagePath = path.join(process.cwd(), 'assets', 'welcome.html');
  const welcomePageUrl = `file://${welcomePagePath}`;
  
  // Create Preferences file with welcome page as startup
  const preferences = {
    browser: {
      has_seen_welcome_page: true,
      custom_chrome_frame: true
    },
    profile: {
      name: name,
      using_default_name: false,
      created_by_version: "120.0"
    },
    session: {
      restore_on_startup: 1,
      startup_urls: [welcomePageUrl]
    },
    extensions: {
      settings: {}
    }
  };
  
  fs.writeFileSync(
    path.join(profilePath, 'Preferences'),
    JSON.stringify(preferences, null, 2)
  );
  
  return {
    id: profileId,
    name: name,
    path: profilePath,
    welcomePage: welcomePageUrl
  };
}
