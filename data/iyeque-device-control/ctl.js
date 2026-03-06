const { exec, execFile } = require('child_process');
const os = require('os');
const fs = require('fs');
const { promisify } = require('util');
const execPromise = promisify(exec);
const execFilePromise = promisify(execFile);

// Parse arguments manually
const args = process.argv.slice(2);
const params = {};
for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith('--')) {
    const key = args[i].substring(2);
    const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
    params[key] = value;
  }
}

const { action, value, app } = params;
let platform = os.platform(); // 'linux', 'darwin', 'win32'
let isWsl = false;
// Default to standard path, but update for WSL
let powershellPath = 'powershell.exe'; 
let cmdPath = 'cmd.exe';
let taskkillPath = 'taskkill.exe'; // Default
let nircmdPath = 'nircmd.exe'; // Default - EXPECT IN PATH

// Detect WSL
if (platform === 'linux') {
    try {
        const release = fs.readFileSync('/proc/version', 'utf8').toLowerCase();
        if (release.includes('microsoft') || release.includes('wsl')) {
            isWsl = true;
            platform = 'wsl'; 
            // Use full paths for WSL system binaries only
            powershellPath = '/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe';
            cmdPath = '/mnt/c/Windows/System32/cmd.exe';
            taskkillPath = '/mnt/c/Windows/System32/taskkill.exe';
            // nircmdPath stays relative/in-path to avoid hardcoded hijackable paths
        }
    } catch (e) {}
}

// SECURITY: Validate and sanitize inputs
function sanitizeNumber(val, min = 0, max = 100) {
  // Strict regex check to prevent trailing junk like "50; rm -rf /"
  if (!/^-?\d+$/.test(String(val))) {
      throw new Error('Value must be a valid integer with no extra characters');
  }
  const num = parseInt(val, 10);
  if (isNaN(num)) throw new Error('Value must be a number');
  if (num < min || num > max) throw new Error(`Value must be between ${min} and ${max}`);
  return num;
}

function sanitizeAppName(name) {
  if (!name || typeof name !== 'string') throw new Error('App name required');
  const sanitized = name.trim();
  
  // SECURITY: Strict Allowlist - Only Alphanumeric, spaces, dashes, underscores, dots
  // Reject everything else.
  if (!/^[a-zA-Z0-9 _\-\.]+$/.test(sanitized)) {
    throw new Error('Invalid app name: only alphanumeric, spaces, dots, dashes, and underscores allowed');
  }
  
  // Limit length to prevent buffer issues
  if (sanitized.length > 256) {
    throw new Error('App name too long (max 256 characters)');
  }
  return sanitized;
}

async function doTool() {
  if (!action) {
    console.error('Error: --action is required');
    process.exit(1);
  }

  console.log('[Device Control] Platform: ' + platform + ' (WSL: ' + isWsl + ')');

  try {
    switch (action) {
      case 'set_volume':
        if (value === undefined) throw new Error('Value required for set_volume');
        await setVolume(value);
        break;
      case 'change_volume':
        if (value === undefined) throw new Error('Value required for change_volume');
        await changeVolume(value);
        break;
      case 'set_brightness':
        if (value === undefined) throw new Error('Value required for set_brightness');
        await setBrightness(value);
        break;
      case 'open_app':
        if (!app) throw new Error('App name/path required for open_app');
        await openApp(app);
        break;
      case 'close_app':
        if (!app) throw new Error('App name required for close_app');
        await closeApp(app);
        break;
      default:
        console.error('Unknown action: ' + action);
        process.exit(1);
    }
    console.log('Action ' + action + ' completed successfully.');
  } catch (error) {
    console.error('Error executing ' + action + ':', error.message);
    process.exit(1);
  }
}

async function setVolume(val) {
  const v = sanitizeNumber(val, 0, 100);
  
  if (platform === 'linux') {
    try {
      // SECURITY: Use execFile where possible to avoid shell interpolation
      await execFilePromise('pactl', ['set-sink-volume', '@DEFAULT_SINK@', `${v}%`]);
    } catch (e) {
      await execFilePromise('amixer', ['sset', 'Master', `${v}%`]);
    }
  } else if (platform === 'darwin') {
    // osascript requires shell, but v is strictly validated number
    await execPromise(`osascript -e "set volume output volume ${v}"`);
  } else if (platform === 'win32' || platform === 'wsl') {
    // 65535 is 100% volume
    const nircmdVal = Math.floor(65535 * (v / 100));
    // Verify nircmd exists in path or current dir, don't use absolute hardcoded path
    if (isWsl) {
        // For WSL, we have to run windows binary.
        // We use execFile on the windows binary if possible, but crossing WSL boundary usually needs shell wrapper
        // Since nircmdVal is strictly validated integer, injection risk is low here.
        await execPromise(`${nircmdPath} setsysvolume ${nircmdVal}`);
    } else {
        await execPromise(`${nircmdPath} setsysvolume ${nircmdVal}`);
    }
  }
}

async function changeVolume(delta) {
  const d = sanitizeNumber(delta, -100, 100);
  let currentVolume = 50; // default fallback
  
  if (platform === 'linux') {
    try {
      const result = await execPromise('pactl get-sink-volume @DEFAULT_SINK@');
      // Parse output safely
      const match = result.stdout.match(/(\d+)%/);
      if (match) currentVolume = parseInt(match[1], 10);
    } catch (e) {
      try {
        const result = await execPromise('amixer get Master');
        const match = result.stdout.match(/(\d+)%/);
        if (match) currentVolume = parseInt(match[1], 10);
      } catch (e2) {}
    }
  } else if (platform === 'darwin') {
    const result = await execPromise('osascript -e "output volume of (get volume settings)"');
    currentVolume = parseInt(result.stdout.trim(), 10) || 50;
  }
  
  const newVolume = Math.max(0, Math.min(100, currentVolume + d));
  await setVolume(newVolume);
  console.log(`Volume changed from ${currentVolume}% to ${newVolume}%`);
}

async function setBrightness(val) {
  const v = sanitizeNumber(val, 0, 100);
  
  if (platform === 'linux' && !isWsl) {
    try {
      await execFilePromise('brightnessctl', ['set', `${v}%`]);
    } catch (e) {
        // Fallback or error
        throw new Error('Cannot control brightness: install brightnessctl');
    }
  } else if (platform === 'darwin') {
    throw new Error("macOS brightness requires 'brightness' CLI tool.");
  } else if (platform === 'win32' || platform === 'wsl') {
    // WmiMonitorBrightnessMethods via PowerShell
    // 1 is the timeout in seconds
    // Since v is strict number, injection is mitigated
    const psCmd = `(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, ${v})`;
    if (isWsl) {
        await execFilePromise(powershellPath, ['-Command', psCmd]);
    } else {
        await execPromise(`powershell -Command "${psCmd}"`);
    }
  }
}

async function openApp(appName) {
  const sanitizedApp = sanitizeAppName(appName);
  
  if (platform === 'linux') {
    // SECURITY: Use exec with shell: false is ideal, but for opening apps we often need detached
    // We use the sanitized name directly.
    const subprocess = exec(`"${sanitizedApp}"`, { detached: true, stdio: 'ignore' });
    subprocess.unref();
  } else if (platform === 'darwin') {
    // Escape double quotes just in case, though allowlist blocks them
    const safeName = sanitizedApp.replace(/"/g, '\\"');
    await execPromise(`open -a "${safeName}"`);
  } else if (platform === 'win32') {
    await execPromise(`start "" "${sanitizedApp}"`, { shell: 'cmd.exe' });
  } else if (platform === 'wsl') {
      // Use cmd.exe /c start to launch Windows apps from WSL
      await execFilePromise(cmdPath, ['/c', 'start', '', sanitizedApp]);
  }
}

async function closeApp(appName) {
  const sanitizedApp = sanitizeAppName(appName);
  
  if (platform === 'linux' || platform === 'darwin') {
    // pkill -f pattern
    await execFilePromise('/usr/bin/pkill', ['-f', sanitizedApp]);
  } else if (platform === 'win32') {
    await execPromise(`taskkill /IM "${sanitizedApp}.exe" /F`);
  } else if (platform === 'wsl') {
      await execFilePromise(taskkillPath, ['/F', '/IM', `${sanitizedApp}.exe`]); 
  }
}

doTool();
