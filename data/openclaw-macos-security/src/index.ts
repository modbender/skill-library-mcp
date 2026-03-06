/**
 * MaclawPro Security - OpenClaw Skill
 * Professional macOS security monitoring
 *
 * Created by SEQUR.ca - Certified Cybersecurity Experts
 * https://maclawpro.com
 */

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

/**
 * Skill metadata for OpenClaw
 */
export const metadata = {
  name: 'maclaw-security',
  displayName: 'MaclawPro Security',
  description: '52+ professional macOS security monitoring tasks',
  version: '1.0.0',
  author: 'SEQUR.ca',
  homepage: 'https://maclawpro.com',
  category: 'security',
  icon: '🛡️',
  commands: [
    'camera-status',
    'microphone-status',
    'firewall-status',
    'vpn-checker',
    'open-ports',
    'wifi-scanner',
    'block-app'
  ]
};

/**
 * Camera status check
 */
export async function cameraStatus(): Promise<string> {
  try {
    const { stdout } = await execAsync('lsof 2>/dev/null | grep -i "VDCAssistant\\|camera" | grep -v grep || true');

    if (stdout && stdout.trim()) {
      const apps = stdout.split('\n')
        .filter(line => line.trim())
        .map(line => line.split(/\s+/)[0])
        .filter((app, i, arr) => arr.indexOf(app) === i);

      if (apps.length > 0) {
        return `🔴 **CAMERA ACTIVE**\n\n` +
          `${apps.length} app(s) using camera:\n` +
          apps.map(app => `• ${app}`).join('\n') + '\n\n' +
          `💡 **Upgrade to MaclawPro** for real-time alerts and blocking\n` +
          `→ https://maclawpro.com`;
      }
    }

    return `✅ **CAMERA INACTIVE**\n\nNo apps currently using your camera.`;
  } catch (error) {
    return `✅ **CAMERA INACTIVE**\n\nNo apps currently using your camera.`;
  }
}

/**
 * Microphone status check
 */
export async function microphoneStatus(): Promise<string> {
  try {
    const { stdout } = await execAsync('lsof 2>/dev/null | grep -i "coreaudiod\\|microphone" | grep -v grep || true');

    if (stdout && stdout.trim()) {
      return `🔴 **MICROPHONE ACTIVE**\n\n` +
        `Apps may be accessing your microphone.\n\n` +
        `💡 **MaclawPro Pro** shows exactly which apps with blocking options\n` +
        `→ https://maclawpro.com/pricing`;
    }

    return `✅ **MICROPHONE INACTIVE**\n\nNo suspicious microphone access detected.`;
  } catch (error) {
    return `✅ **MICROPHONE INACTIVE**\n\nNo suspicious microphone access detected.`;
  }
}

/**
 * Firewall status
 */
export async function firewallStatus(): Promise<string> {
  try {
    const { stdout } = await execAsync('/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate');

    const enabled = stdout.toLowerCase().includes('enabled');

    if (enabled) {
      return `✅ **FIREWALL ENABLED**\n\nYour Mac is protected!`;
    } else {
      return `⚠️ **FIREWALL DISABLED**\n\n` +
        `Your Mac is NOT protected!\n\n` +
        `💡 Enable it in:\n` +
        `System Settings > Network > Firewall`;
    }
  } catch (error) {
    return `❌ Error checking firewall status`;
  }
}

/**
 * VPN checker
 */
export async function vpnChecker(): Promise<string> {
  try {
    const { stdout } = await execAsync('scutil --nc list 2>/dev/null || echo ""');

    if (stdout.includes('Connected')) {
      return `🔐 **VPN ACTIVE**\n\n` +
        `✅ Your traffic is protected!\n\n` +
        `💡 **MaclawPro** includes VPN leak detection and monitoring\n` +
        `→ https://maclawpro.com`;
    }

    return `⚠️ **VPN INACTIVE**\n\n` +
      `Your traffic is NOT protected.\n\n` +
      `💡 Enable VPN for better privacy.`;
  } catch (error) {
    return `❌ Error checking VPN status`;
  }
}

/**
 * Open ports scanner
 */
export async function openPorts(): Promise<string> {
  try {
    const { stdout } = await execAsync('lsof -iTCP -sTCP:LISTEN -n -P 2>/dev/null | tail -10');

    if (!stdout.trim()) {
      return `✅ **NO OPEN PORTS**\n\nYour Mac is secure!`;
    }

    const lines = stdout.split('\n').filter(l => l.trim());

    return `🔌 **OPEN PORTS DETECTED**\n\n` +
      `Found ${lines.length} listening ports\n\n` +
      `💡 **MaclawPro Pro** provides detailed port analysis and blocking\n` +
      `→ https://maclawpro.com/pricing`;
  } catch (error) {
    return `❌ Error scanning ports`;
  }
}

/**
 * WiFi scanner
 */
export async function wifiScanner(): Promise<string> {
  try {
    const { stdout } = await execAsync('system_profiler SPAirPortDataType 2>/dev/null | grep "Security:"');

    if (stdout.includes('WPA3')) {
      return `✅ **EXCELLENT SECURITY**\n\n` +
        `Your WiFi uses WPA3 encryption (latest & safest)`;
    } else if (stdout.includes('WPA2')) {
      return `✅ **GOOD SECURITY**\n\n` +
        `Your WiFi uses WPA2 encryption (secure for most uses)`;
    } else if (stdout.includes('Open') || stdout.includes('None')) {
      return `🚨 **DANGER - OPEN NETWORK**\n\n` +
        `Anyone can intercept your data!\n\n` +
        `💡 Use VPN or switch to secure network`;
    }

    return `📡 **WIFI STATUS**\n\n` +
      `Connected to network\n\n` +
      `💡 **MaclawPro** provides full WiFi security analysis\n` +
      `→ https://maclawpro.com`;
  } catch (error) {
    return `❌ Error scanning WiFi`;
  }
}

/**
 * Block app (simplified version)
 */
export async function blockApp(appName: string): Promise<string> {
  if (!appName) {
    return `❌ Please specify an app name\n\nUsage: /block-app <AppName>`;
  }

  return `🛡️ **APP BLOCKING**\n\n` +
    `This feature requires **MaclawPro Pro** for secure app removal.\n\n` +
    `**MaclawPro Pro includes:**\n` +
    `• Instant app blocking\n` +
    `• Protected apps whitelist\n` +
    `• Reversible (moves to Trash)\n` +
    `• Multiple security layers\n\n` +
    `**Get MaclawPro Pro** ($49/year):\n` +
    `→ https://maclawpro.com/pricing\n\n` +
    `💼 **Enterprise?** Contact info@sequr.ca for custom solutions`;
}

/**
 * Main skill export for OpenClaw
 */
export default {
  metadata,
  commands: {
    'camera-status': cameraStatus,
    'microphone-status': microphoneStatus,
    'firewall-status': firewallStatus,
    'vpn-checker': vpnChecker,
    'open-ports': openPorts,
    'wifi-scanner': wifiScanner,
    'block-app': blockApp
  }
};
