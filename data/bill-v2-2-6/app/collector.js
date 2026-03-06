import fs from 'fs';
import path from 'path';

const USAGE_PATH = '/root/.openclaw/workspace/bill_project/app/dist/usage.json';
const PRICES_PATH = '/root/.openclaw/workspace/bill_project/app/prices.json';
const SESSION_PATH = '/root/.openclaw/agents/main/sessions/sessions.json';
const VAULT_PATH = '/root/.openclaw/workspace/bill_project/app/vault.json';
const WEB_LIVE_PATH = '/var/www/html/bill/usage_live.json';
const WEB_MAIN_PATH = '/var/www/html/bill/usage.json';
const DEBUG_LOG = '/root/.openclaw/workspace/bill_project/app/debug.log';
const CUMULATIVE_PATH = '/root/.openclaw/workspace/bill_project/app/cumulative_usage.json';
const OPENCLAW_CONFIG = '/root/.openclaw/openclaw.json';

const BRANDS = ['openai', 'claude', 'gemini', 'deepseek', 'kimi', 'groq', 'xai', 'minimax', 'mistral', 'qwen', 'glm', 'llama'];

function loadArchived() {
    if (fs.existsSync(CUMULATIVE_PATH)) {
        try {
            return JSON.parse(fs.readFileSync(CUMULATIVE_PATH, 'utf8'));
        } catch (e) {
            console.error('Failed to load archived costs:', e.message);
        }
    }
    const initial = { lastReset: new Date().toISOString() };
    BRANDS.forEach(b => initial[b] = 0);
    return initial;
}

function saveArchived(data) {
    try {
        fs.writeFileSync(CUMULATIVE_PATH, JSON.stringify(data, null, 2));
    } catch (e) {
        console.error('Failed to save archived costs:', e.message);
    }
}

function getRuntimeInfo() {
    try {
        if (!fs.existsSync(OPENCLAW_CONFIG)) return null;
        const config = JSON.parse(fs.readFileSync(OPENCLAW_CONFIG, 'utf8'));
        const defaults = config.models?.defaults || {};
        const provider = defaults.provider || 'minimax-portal';
        const model = defaults.model || 'MiniMax-M2.5';
        return { provider, model, fullModel: `${provider}/${model}` };
    } catch (e) {
        return null;
    }
}

let lastScanSessions = new Map();

async function calculateUsage() {
    try {
        if (!fs.existsSync(SESSION_PATH)) return;

        let sessionsRaw;
        try {
            sessionsRaw = fs.readFileSync(SESSION_PATH, 'utf8');
            if (!sessionsRaw || sessionsRaw.trim() === '') return;
        } catch (e) {
            return;
        }

        const sessions = JSON.parse(sessionsRaw);
        const prices = JSON.parse(fs.readFileSync(PRICES_PATH, 'utf8'));
        const vault = fs.existsSync(VAULT_PATH) ? JSON.parse(fs.readFileSync(VAULT_PATH, 'utf8')) : {};
        const archived = loadArchived();
        
        const currentUsage = {};
        const stats = {};
        BRANDS.forEach(b => {
            currentUsage[b] = 0;
            stats[b] = {};
        });

        const activeSessionKeys = new Set();
        let debugInfo = [];

        Object.entries(sessions).forEach(([sessionKey, s]) => {
            let modelFull = (s.modelOverride || s.providerOverride || s.model || '').toLowerCase();
            const inTokens = s.inputTokens || 0;
            const outTokens = s.outputTokens || 0;
            
            if (inTokens === 0 && outTokens === 0) return;
            
            activeSessionKeys.add(sessionKey);

            let brand = '';
            if (modelFull.includes('claude')) brand = 'claude';
            else if (modelFull.includes('gemini')) brand = 'gemini';
            else if (modelFull.includes('gpt') || modelFull.includes('openai')) brand = 'openai';
            else if (modelFull.includes('kimi')) brand = 'kimi';
            else if (modelFull.includes('deepseek')) brand = 'deepseek';
            else if (modelFull.includes('groq')) brand = 'groq';
            else if (modelFull.includes('grok') || modelFull.includes('xai')) brand = 'xai';
            else if (modelFull.includes('minimax')) brand = 'minimax';
            else if (modelFull.includes('mistral')) brand = 'mistral';
            else if (modelFull.includes('qwen')) brand = 'qwen';
            else if (modelFull.includes('glm')) brand = 'glm';
            else if (modelFull.includes('llama')) brand = 'llama';

            if (brand && prices[brand]) {
                const modelKey = Object.keys(prices[brand]).find(k => modelFull.includes(k.toLowerCase()));
                const priceInfo = modelKey ? prices[brand][modelKey] : prices[brand][Object.keys(prices[brand])[0]];

                if (priceInfo) {
                    const cost = (inTokens * (priceInfo.in / 1000000)) + (outTokens * (priceInfo.out / 1000000));
                    currentUsage[brand] += cost;
                    
                    const verLabel = modelFull.split('/').pop().replace(/-/g, ' ').toUpperCase();
                    stats[brand][verLabel] = (stats[brand][verLabel] || 0) + (inTokens + outTokens);
                    
                    lastScanSessions.set(sessionKey, { brand, cost, time: Date.now() });
                    debugInfo.push(`${sessionKey.split(':').pop()}: ${inTokens}/${outTokens} -> ${modelFull}`);
                }
            }
        });

        let archivedChanged = false;
        for (const [key, data] of lastScanSessions.entries()) {
            if (!activeSessionKeys.has(key)) {
                archived[data.brand] = (archived[data.brand] || 0) + data.cost;
                lastScanSessions.delete(key);
                archivedChanged = true;
                console.log(`[${new Date().toLocaleTimeString()}] Archiving session ${key.split(':').pop()}: $${data.cost.toFixed(4)}`);
            }
        }

        if (archivedChanged) {
            saveArchived(archived);
        }

        const runtimeInfo = getRuntimeInfo();
        const usageData = { 
            timestamp: new Date().toISOString(), 
            runtime: runtimeInfo,
            models: {}
        };

        BRANDS.forEach(k => {
            const totalCost = (archived[k] || 0) + currentUsage[k];
            usageData.models[k] = totalCost.toFixed(4);
            
            const vaultItem = vault[k] || { balance: 0, mode: 'prepaid' };
            const balBase = parseFloat(vaultItem.balance || 0);
            const mode = vaultItem.mode || 'prepaid';

            if (mode === 'postpaid') {
                usageData.models[k + '_bal'] = "POST";
            } else if (mode === 'subscribe') {
                usageData.models[k + '_bal'] = "SUB";
            } else if (mode === 'unused') {
                usageData.models[k + '_bal'] = "OFF";
            } else {
                usageData.models[k + '_bal'] = (balBase - totalCost).toFixed(2);
            }
            
            usageData.models[k + '_stats'] = stats[k];
        });

        const jsonStr = JSON.stringify(usageData, null, 2);
        fs.writeFileSync(USAGE_PATH, jsonStr);
        fs.writeFileSync(WEB_LIVE_PATH, jsonStr);
        fs.writeFileSync(WEB_MAIN_PATH, jsonStr);
        fs.writeFileSync(DEBUG_LOG, debugInfo.join('\n'));
        
        console.log(`[${new Date().toLocaleTimeString()}] Sync OK | Total Brands: ${BRANDS.length}`);
    } catch (e) { 
        console.error(`[${new Date().toLocaleTimeString()}] Engine Error:`, e.message); 
    }
}

calculateUsage();
setInterval(calculateUsage, 27000);
