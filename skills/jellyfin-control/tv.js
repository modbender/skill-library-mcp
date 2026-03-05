/**
 * TV Control Module — Multi-backend, multi-platform support
 * 
 * Backends:
 *   "homeassistant" — Uses HA REST API (supports WebOS + Android TV entities)
 *   "webos"         — Direct WebOS SSAP protocol via WebSocket (LG TVs, no HA)
 *   "androidtv"     — Direct ADB connection (Android TV / Fire TV / Chromecast, no HA)
 * 
 * Wake-on-LAN works with all backends (Node dgram, zero dependencies).
 */

const http = require('http');
const https = require('https');
const dgram = require('dgram');
const { URL } = require('url');
const { execSync } = require('child_process');

// ── Configuration ──────────────────────────────────────────────────────────
const TV_CONFIG = {
    backend: (process.env.TV_BACKEND || 'auto').toLowerCase(),
    platform: (process.env.TV_PLATFORM || 'auto').toLowerCase(), // webos | androidtv | auto
    // Home Assistant
    haUrl: process.env.HA_URL || '',
    haToken: process.env.HA_TOKEN || '',
    haEntity: process.env.HA_TV_ENTITY || '',
    // Direct WebOS
    tvIp: process.env.TV_IP || '',
    // Direct ADB (Android TV)
    adbDevice: process.env.ADB_DEVICE || '', // e.g. "192.168.1.100:5555"
    // Universal
    tvMac: process.env.TV_MAC || '',
    jellyfinApp: process.env.TV_JELLYFIN_APP || '',  // auto-detected per platform
    // Timing
    bootDelay: parseInt(process.env.TV_BOOT_DELAY || '10', 10),
    appDelay: parseInt(process.env.TV_APP_DELAY || '8', 10),
};

// Default Jellyfin app IDs per platform
const JELLYFIN_APPS = {
    webos: 'org.jellyfin.webos',
    androidtv: 'org.jellyfin.androidtv',
};

function getPlatform() {
    if (TV_CONFIG.platform !== 'auto') return TV_CONFIG.platform;
    if (TV_CONFIG.adbDevice) return 'androidtv';
    if (TV_CONFIG.haEntity.includes('fire_tv') || TV_CONFIG.haEntity.includes('android')) return 'androidtv';
    if (TV_CONFIG.haEntity.includes('webos') || TV_CONFIG.haEntity.includes('lg')) return 'webos';
    if (TV_CONFIG.tvIp && !TV_CONFIG.adbDevice) return 'webos';
    return 'androidtv'; // safer default for generic smart TVs
}

function getJellyfinApp() {
    if (TV_CONFIG.jellyfinApp) return TV_CONFIG.jellyfinApp;
    const platform = getPlatform();
    return JELLYFIN_APPS[platform] || JELLYFIN_APPS.androidtv;
}

function getBackend() {
    if (TV_CONFIG.backend !== 'auto') return TV_CONFIG.backend;
    if (TV_CONFIG.haUrl && TV_CONFIG.haToken && TV_CONFIG.haEntity) return 'homeassistant';
    if (TV_CONFIG.adbDevice) return 'androidtv';
    if (TV_CONFIG.tvIp) return 'webos';
    return 'none';
}

// ── Wake-on-LAN (universal, zero deps) ─────────────────────────────────────
function wakeOnLan(mac) {
    return new Promise((resolve, reject) => {
        if (!mac) return reject(new Error('TV_MAC not configured. Set it to your TV\'s MAC address (e.g. AA:BB:CC:DD:EE:FF).'));
        
        const cleanMac = mac.replace(/[:\-]/g, '');
        if (cleanMac.length !== 12) return reject(new Error(`Invalid MAC address: ${mac}`));
        
        const macBytes = Buffer.from(cleanMac, 'hex');
        const magic = Buffer.alloc(102);
        magic.fill(0xFF, 0, 6);
        for (let i = 0; i < 16; i++) {
            macBytes.copy(magic, 6 + i * 6);
        }

        const socket = dgram.createSocket('udp4');
        socket.once('error', (err) => { socket.close(); reject(err); });
        
        socket.bind(() => {
            socket.setBroadcast(true);
            socket.send(magic, 0, magic.length, 9, '255.255.255.255', (err) => {
                socket.close();
                if (err) reject(err);
                else resolve(true);
            });
        });
    });
}

// ── Home Assistant Backend ─────────────────────────────────────────────────
function haRequest(service, domain, data) {
    return new Promise((resolve, reject) => {
        const url = new URL(`/api/services/${domain}/${service}`, TV_CONFIG.haUrl);
        const isHttps = url.protocol === 'https:';
        const lib = isHttps ? https : http;

        const body = JSON.stringify(data);
        const options = {
            method: 'POST',
            hostname: url.hostname,
            port: url.port || (isHttps ? 443 : 80),
            path: url.pathname,
            headers: {
                'Authorization': `Bearer ${TV_CONFIG.haToken}`,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body)
            }
        };

        const req = lib.request(options, (res) => {
            let chunks = [];
            res.on('data', c => chunks.push(c));
            res.on('end', () => {
                const text = Buffer.concat(chunks).toString();
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try { resolve(JSON.parse(text)); } catch { resolve(text); }
                } else {
                    reject(new Error(`HA API ${res.statusCode}: ${text}`));
                }
            });
        });
        req.on('error', reject);
        req.write(body);
        req.end();
    });
}

const ha = {
    async turnOn() {
        if (TV_CONFIG.tvMac) {
            await wakeOnLan(TV_CONFIG.tvMac);
            console.log('📡 Wake-on-LAN packet sent');
        }
        await haRequest('turn_on', 'media_player', { entity_id: TV_CONFIG.haEntity });
        console.log('✅ TV turn_on sent via Home Assistant');
    },

    async turnOff() {
        await haRequest('turn_off', 'media_player', { entity_id: TV_CONFIG.haEntity });
        console.log('✅ TV turned off via Home Assistant');
    },

    async launchApp(appId) {
        const platform = getPlatform();
        
        if (platform === 'webos') {
            // WebOS via HA: webostv.command
            await haRequest('command', 'webostv', {
                entity_id: TV_CONFIG.haEntity,
                command: 'system.launcher/launch',
                payload: { id: appId }
            });
        } else {
            // Android TV via HA: androidtv.adb_command
            const launchCmd = `monkey -p ${appId} -c android.intent.category.LAUNCHER 1`;
            try {
                await haRequest('adb_command', 'androidtv', {
                    entity_id: TV_CONFIG.haEntity,
                    command: launchCmd
                });
            } catch (e) {
                // Fallback: media_player.select_source
                console.log('⚠️  androidtv.adb_command failed, trying select_source...');
                await haRequest('select_source', 'media_player', {
                    entity_id: TV_CONFIG.haEntity,
                    source: 'Jellyfin'
                });
            }
        }
        console.log(`✅ Launched app: ${appId}`);
    },

    async listApps() {
        const platform = getPlatform();
        
        if (platform === 'webos') {
            await haRequest('command', 'webostv', {
                entity_id: TV_CONFIG.haEntity,
                command: 'com.webos.applicationManager/listLaunchPoints',
                payload: {}
            });
            console.log('✅ App list requested — check Home Assistant logs/events for the response.');
        } else {
            try {
                await haRequest('adb_command', 'androidtv', {
                    entity_id: TV_CONFIG.haEntity,
                    command: 'pm list packages -3'
                });
                console.log('✅ Package list requested — check HA entity attributes or logcat.');
            } catch (e) {
                console.log('⚠️  Could not list apps. Check HA → Developer Tools → States → your entity.');
            }
        }
    }
};

// ── Android TV Direct Backend (ADB) ────────────────────────────────────────
// Uses `adb` CLI via child_process. No npm packages needed.
// Requires: adb installed on the system.

function adbExec(command, throwOnError = true) {
    const device = TV_CONFIG.adbDevice;
    const prefix = device ? `adb -s ${device}` : 'adb';
    const fullCmd = `${prefix} ${command}`;
    
    try {
        return execSync(fullCmd, { 
            encoding: 'utf8', 
            timeout: 10000,
            stdio: ['pipe', 'pipe', 'pipe']
        }).trim();
    } catch (e) {
        if (throwOnError) {
            throw new Error(`ADB failed: ${fullCmd}\n${e.stderr || e.message}`);
        }
        return '';
    }
}

function adbCheckInstalled() {
    try {
        execSync('adb version', { encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
    } catch (e) {
        throw new Error(
            'adb is not installed or not in PATH.\n' +
            'Install it:\n' +
            '  • Debian/Ubuntu: sudo apt install adb\n' +
            '  • macOS:         brew install android-platform-tools\n' +
            '  • Or use TV_BACKEND=homeassistant instead'
        );
    }
}

function adbConnect() {
    const device = TV_CONFIG.adbDevice;
    if (!device) {
        throw new Error('ADB_DEVICE not configured. Set it to "TV_IP:5555" (e.g. "192.168.1.100:5555").');
    }
    
    const devices = adbExec('devices', false);
    if (devices.includes(device) && !devices.includes('offline')) return;

    const result = adbExec(`connect ${device}`);
    if (result.includes('connected') || result.includes('already')) {
        console.log(`🔌 ADB connected to ${device}`);
    } else {
        throw new Error(
            `Cannot connect to ${device}.\n` +
            'Make sure:\n' +
            '  1. TV is on and on the same network\n' +
            '  2. Developer Options enabled (Settings → About → tap Build Number 7x)\n' +
            '  3. Network debugging / USB debugging enabled\n' +
            '  4. You accepted the "Allow debugging?" prompt on the TV'
        );
    }
}

const androidtv = {
    async turnOn() {
        if (TV_CONFIG.tvMac) {
            await wakeOnLan(TV_CONFIG.tvMac);
            console.log('📡 Wake-on-LAN packet sent');
        } else {
            // ADB wakeup works if TV is in standby (not fully off)
            adbCheckInstalled();
            try {
                adbConnect();
                adbExec('shell input keyevent KEYCODE_WAKEUP');
                console.log('✅ ADB WAKEUP sent');
                return;
            } catch (e) {
                throw new Error(
                    'Cannot wake TV. Set TV_MAC for Wake-on-LAN, or keep TV in standby mode.'
                );
            }
        }
    },

    async turnOff() {
        adbCheckInstalled();
        adbConnect();
        adbExec('shell input keyevent KEYCODE_SLEEP');
        console.log('✅ TV sent to sleep via ADB');
    },

    async launchApp(appId) {
        adbCheckInstalled();
        adbConnect();
        
        // monkey is the most reliable universal launcher
        const result = adbExec(`shell monkey -p ${appId} -c android.intent.category.LAUNCHER 1`, false);
        
        if (result.includes('No activities found')) {
            // Fallback: leanback launcher intent (Android TV specific)
            adbExec(
                `shell am start -a android.intent.action.MAIN -c android.intent.category.LEANBACK_LAUNCHER ${appId}`,
                false
            );
        }
        
        console.log(`✅ Launched app: ${appId}`);
    },

    async listApps() {
        adbCheckInstalled();
        adbConnect();
        
        const raw = adbExec('shell pm list packages -3');
        const packages = raw.split('\n')
            .map(line => line.replace('package:', '').trim())
            .filter(Boolean)
            .sort();
        
        console.log('\n📱 Installed Apps (third-party):\n');
        packages.forEach(pkg => console.log(`  ${pkg}`));
        console.log(`\n  Total: ${packages.length} apps`);
        
        const jfApp = getJellyfinApp();
        if (packages.includes(jfApp)) {
            console.log(`  ✅ Jellyfin found: ${jfApp}`);
        } else {
            const found = packages.filter(p => p.includes('jellyfin'));
            if (found.length) {
                console.log(`  ⚠️  Expected ${jfApp}, found: ${found.join(', ')}`);
                console.log(`     Set TV_JELLYFIN_APP to the correct package.`);
            } else {
                console.log(`  ❌ Jellyfin not found! Install from Play Store / Amazon Appstore.`);
            }
        }
        
        return packages;
    }
};

// ── WebOS Direct Backend (SSAP over WebSocket) ─────────────────────────────

function webosConnect(tvIp, timeoutMs = 8000) {
    return new Promise((resolve, reject) => {
        let WebSocket;
        try {
            WebSocket = require('ws');
        } catch (e) {
            reject(new Error(
                'WebOS direct backend requires "ws" package.\n' +
                'Install: npm install ws\n' +
                'Or use TV_BACKEND=homeassistant or TV_BACKEND=androidtv'
            ));
            return;
        }

        const ws = new WebSocket(`ws://${tvIp}:3000`);
        const timer = setTimeout(() => {
            ws.close();
            reject(new Error(`Timeout connecting to TV at ${tvIp}:3000. Is the TV on?`));
        }, timeoutMs);

        ws.on('open', () => { clearTimeout(timer); resolve(ws); });
        ws.on('error', (err) => { clearTimeout(timer); reject(new Error(`TV at ${tvIp}:3000 — ${err.message}`)); });
    });
}

function webosSend(ws, uri, payload = {}) {
    return new Promise((resolve, reject) => {
        const id = `req_${Date.now()}`;
        const timer = setTimeout(() => reject(new Error(`Timeout: ${uri}`)), 5000);

        const handler = (raw) => {
            try {
                const data = JSON.parse(raw);
                if (data.id === id) {
                    clearTimeout(timer);
                    ws.removeListener('message', handler);
                    if (data.type === 'error') reject(new Error(data.error || 'WebOS error'));
                    else resolve(data.payload || data);
                }
            } catch (e) { /* ignore */ }
        };
        ws.on('message', handler);
        ws.send(JSON.stringify({ id, type: 'request', uri: `ssap://${uri}`, payload }));
    });
}

function webosRegister(ws) {
    return new Promise((resolve, reject) => {
        const id = 'register_0';
        let prompted = false;
        const timer = setTimeout(() => {
            ws.removeListener('message', handler);
            reject(new Error('Timeout waiting for TV pairing. Accept the prompt on your TV.'));
        }, 30000);

        const handler = (raw) => {
            try {
                const data = JSON.parse(raw);
                if (data.id !== id) return;
                if (data.type === 'registered') {
                    clearTimeout(timer);
                    ws.removeListener('message', handler);
                    const key = data.payload && data.payload['client-key'];
                    if (key && !process.env.TV_CLIENT_KEY) {
                        console.log(`\n🔑 SAVE THIS! Add to env: "TV_CLIENT_KEY": "${key}"\n`);
                    }
                    resolve(key);
                } else if (data.type === 'response' && !prompted) {
                    prompted = true;
                    console.log('📺 Accept the pairing prompt on your TV!');
                }
            } catch (e) { /* ignore */ }
        };
        ws.on('message', handler);
        ws.send(JSON.stringify({
            id, type: 'register',
            payload: { pairingType: 'PROMPT', 'client-key': process.env.TV_CLIENT_KEY || undefined }
        }));
    });
}

const webos = {
    async turnOn() {
        if (!TV_CONFIG.tvMac) {
            throw new Error('TV_MAC is required to turn on the TV (Wake-on-LAN).');
        }
        await wakeOnLan(TV_CONFIG.tvMac);
        console.log('📡 Wake-on-LAN packet sent');
    },

    async turnOff() {
        const ws = await webosConnect(TV_CONFIG.tvIp);
        await webosRegister(ws);
        await webosSend(ws, 'system/turnOff');
        ws.close();
        console.log('✅ TV turned off');
    },

    async launchApp(appId) {
        const ws = await webosConnect(TV_CONFIG.tvIp);
        await webosRegister(ws);
        await webosSend(ws, 'system.launcher/launch', { id: appId });
        ws.close();
        console.log(`✅ Launched app: ${appId}`);
    },

    async listApps() {
        const ws = await webosConnect(TV_CONFIG.tvIp);
        await webosRegister(ws);
        const result = await webosSend(ws, 'com.webos.applicationManager/listLaunchPoints');
        ws.close();

        if (result.launchPoints) {
            console.log('\n📱 Installed Apps:\n');
            result.launchPoints
                .sort((a, b) => a.title.localeCompare(b.title))
                .forEach(app => console.log(`  ${app.title.padEnd(30)} → ${app.id}`));
            console.log(`\n  Total: ${result.launchPoints.length} apps`);
        }
        return result.launchPoints || [];
    }
};

// ── Public API ──────────────────────────────────────────────────────────────
function getDriver() {
    const backend = getBackend();
    switch (backend) {
        case 'homeassistant': return ha;
        case 'webos': return webos;
        case 'androidtv': return androidtv;
        case 'none':
            throw new Error(
                'No TV backend configured. Set one of:\n' +
                '  • Home Assistant:  HA_URL + HA_TOKEN + HA_TV_ENTITY (any TV brand)\n' +
                '  • Direct WebOS:    TV_IP (LG TVs only)\n' +
                '  • Direct ADB:      ADB_DEVICE (Android TV / Fire TV / Chromecast w/ Google TV)\n' +
                'See SKILL.md for details.'
            );
        default:
            throw new Error(`Unknown TV_BACKEND: "${backend}". Use "homeassistant", "webos", "androidtv", or "auto".`);
    }
}

function sleep(seconds) {
    return new Promise(r => setTimeout(r, seconds * 1000));
}

module.exports = {
    TV_CONFIG,
    getBackend,
    getPlatform,
    getJellyfinApp,

    async turnOn() { await getDriver().turnOn(); },
    async turnOff() { await getDriver().turnOff(); },
    async launchApp(appId) { await getDriver().launchApp(appId || getJellyfinApp()); },
    async listApps() { return getDriver().listApps(); },

    /** Full automation: ON → wait → Launch Jellyfin → wait */
    async wakeAndLaunch() {
        const driver = getDriver();
        const jellyfinApp = getJellyfinApp();

        console.log(`📺 Step 1/3: Turning on TV... [${getBackend()}/${getPlatform()}]`);
        await driver.turnOn();

        console.log(`⏳ Step 2/3: Waiting ${TV_CONFIG.bootDelay}s for boot...`);
        await sleep(TV_CONFIG.bootDelay);

        console.log(`🚀 Step 3/3: Launching Jellyfin (${jellyfinApp})...`);
        await driver.launchApp(jellyfinApp);

        console.log(`⏳ Waiting ${TV_CONFIG.appDelay}s for session...`);
        await sleep(TV_CONFIG.appDelay);

        console.log('✅ TV ready for playback!');
    },

    wakeOnLan,
    sleep
};
