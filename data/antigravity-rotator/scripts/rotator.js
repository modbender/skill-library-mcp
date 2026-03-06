const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class Rotator {
    constructor(config) {
        this.config = config;
        this.home = config.paths.home || process.env.HOME;
        
        this.paths = {
            authProfiles: path.resolve(this.home, config.paths.authProfiles),
            statusDb: path.resolve(this.home, config.paths.statusDb),
            rotationLog: path.resolve(this.home, config.paths.rotationLog),
            rotationState: path.resolve(this.home, config.paths.rotationState),
            dashboardConfig: path.resolve(__dirname, '../config.json')
        };

        // API Configuration (configurable via config.json)
        this.QUOTA_API_URL = 'https://daily-cloudcode-pa.sandbox.googleapis.com/v1internal:fetchAvailableModels';
        this.REFRESH_TOKEN_URL = 'https://oauth2.googleapis.com/token';
        
        // OAuth Credentials (from config or hardcoded Antigravity defaults)
        this.CLIENT_ID = config.clientId || '1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com';
        this.CLIENT_SECRET = config.clientSecret || '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';
        this.DEFAULT_PROJECT_ID = config.defaultProjectId || 'bamboo-precept-lgxtn';
        
        this.VIP_KEY = 'google-antigravity:vip_rotation';
        this.threshold = (config.quotas && config.quotas.low) || 21;
        
        // Path handling
        this.openclawBin = config.openclawBin; 
        if (!this.openclawBin) {
            try { this.openclawBin = execSync('which openclaw', { encoding: 'utf8' }).trim(); } catch(e) {}
        }
        
        // Inject PATH for node/openclaw compatibility
        const nodeBinPath = path.dirname(process.execPath);
        process.env.PATH = nodeBinPath + ':' + process.env.PATH;
    }

    readJson(p) { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return {}; } }
    writeJson(p, d) { fs.writeFileSync(p, JSON.stringify(d, null, 2)); }
    appendLog(msg) {
        try { fs.appendFileSync(this.paths.rotationLog, `[${new Date().toISOString()}] ${msg}\n`, 'utf8'); } catch { }
    }
    shortEmail(email) { return email.split('@')[0]; }

    async refreshAccessToken(refreshToken) {
        const postData = new URLSearchParams({
            client_id: this.CLIENT_ID,
            client_secret: this.CLIENT_SECRET,
            refresh_token: refreshToken,
            grant_type: 'refresh_token'
        }).toString();
        const cmd = `curl -s --connect-timeout 10 --retry 1 -X POST "${this.REFRESH_TOKEN_URL}" -d "${postData}"`;
        try {
            const output = execSync(cmd, { encoding: 'utf8', timeout: 35000 });
            const json = JSON.parse(output);
            if (json.access_token) return json.access_token;
            throw new Error(json.error_description || 'Token refresh failed');
        } catch (e) { throw new Error(`Refresh Failed: ${e.message}`); }
    }

    async fetchAccountQuota(accessToken, projectId) {
        const headers = { 'Authorization': `Bearer ${accessToken}`, 'Content-Type': 'application/json', 'User-Agent': 'antigravity/1.15.8 linux/x64' };
        const body = { project: projectId || this.DEFAULT_PROJECT_ID };
        const headerArgs = Object.entries(headers).map(([k, v]) => `-H "${k}: ${v}"`).join(' ');
        const bodyStr = JSON.stringify(body).replace(/"/g, '\\"');
        const cmd = `curl -s --connect-timeout 10 --retry 1 -X POST "${this.QUOTA_API_URL}" ${headerArgs} -d "${bodyStr}"`;
        try {
            const output = execSync(cmd, { encoding: 'utf8', timeout: 35000 });
            if (!output.trim()) throw new Error('Empty response');
            const data = JSON.parse(output);
            if (data.error) {
                if (data.error.code === 403) return { forbidden: true };
                throw new Error(data.error.message || data.error.status);
            }
            const quotas = {};
            for (const [mId, info] of Object.entries(data.models || {})) {
                const fullKey = `google-antigravity/${mId}`;
                const qI = info.quotaInfo;
                const rT = qI && qI.resetTime ? new Date(qI.resetTime).getTime() : 0;
                let pct = 100;
                if (qI) {
                    if (qI.remainingFraction !== undefined) pct = Math.round(qI.remainingFraction * 100);
                    else if (rT > Date.now()) pct = 0;
                }
                quotas[fullKey] = { quota: pct, resetAt: rT, updatedAt: Date.now() };
            }
            return quotas;
        } catch (e) { throw new Error(`Quota Fetch Failed: ${e.message}`); }
    }

    async run() {
        if (!this.openclawBin) { console.error('❌ openclaw binary not found. Please run "node index.js --action=setup".'); return; }
        console.log(`=== Antigravity Rotator Engine [${new Date().toLocaleTimeString()}] ===\n`);
        const authData = this.readJson(this.paths.authProfiles);
        const modelPriority = this.config.modelPriority || [];
        const accounts = this.config.accounts || [];
        if (accounts.length === 0) { console.log('⚠️ No accounts.'); return; }

        console.log(`📋 Accounts: ${accounts.map(a => this.shortEmail(a)).join(', ')}`);
        console.log(`📋 Priority: ${modelPriority.map(m => m.split('/').pop()).join(' > ')}\n`);

        let currentModel = null;
        try {
            const statusOutput = execSync(`${this.openclawBin} gateway call status --params "{}" --json`, { encoding: 'utf8' });
            const status = JSON.parse(statusOutput);
            currentModel = status.sessions?.recent?.find(s => s.key === 'agent:main:main')?.model || status.sessions?.defaults?.model;
            if (currentModel) console.log(`📡 Current Session Model: ${currentModel}`);
        } catch (e) { }

        if (!currentModel) currentModel = modelPriority[0];
        if (!currentModel.includes('/')) {
            const full = `google-antigravity/${currentModel}`;
            if (modelPriority.includes(full)) currentModel = full;
        }

        const currentVip = authData.profiles?.[this.VIP_KEY];
        let currentEmail = accounts[0];
        for (const acc of accounts) {
            if (authData.profiles[`google-antigravity:${acc}`]?.access === currentVip?.access) {
                currentEmail = acc; break;
            }
        }

        if (!currentModel.startsWith('google-antigravity/')) {
            console.log(`ℹ️ Non-Antigravity model (${currentModel}). Skipping.`); return;
        }

        console.log(`Current: ${this.shortEmail(currentEmail)} | ${currentModel}\n`);

        const statusDb = this.readJson(this.paths.statusDb) || {};
        let success = 0;
        let authUpdated = false;

        for (const email of accounts) {
            const profile = authData.profiles?.[`google-antigravity:${email}`];
            if (!profile) continue;
            try {
                let token = profile.access;
                const now = Date.now();
                if (!profile.expires || profile.expires < now + 300000) {
                    console.log(`🔄 ${this.shortEmail(email)}: Refreshing token...`);
                    token = await this.refreshAccessToken(profile.refresh);
                    authData.profiles[`google-antigravity:${email}`].access = token;
                    authData.profiles[`google-antigravity:${email}`].expires = now + 3600000;
                    if (currentVip && currentVip.refresh === profile.refresh) {
                        authData.profiles[this.VIP_KEY].access = token;
                        authData.profiles[this.VIP_KEY].expires = now + 3600000;
                    }
                    authUpdated = true;
                }
                console.log(`📡 ${this.shortEmail(email)}: Fetching quotas...`);
                const quotas = await this.fetchAccountQuota(token, profile.projectId);
                if (quotas.forbidden) continue;
                for (const [m, d] of Object.entries(quotas)) {
                    statusDb[`${email}:${m}`] = d;
                    console.log(`   ${m.split('/').pop()}: ${d.quota}%`);
                }
                success++;
            } catch (e) { console.log(`❌ ${this.shortEmail(email)}: ${e.message}`); }
        }

        if (authUpdated) this.writeJson(this.paths.authProfiles, authData);
        this.writeJson(this.paths.statusDb, statusDb);
        if (success === 0) return;

        let choice = null;
        const now = Date.now();
        for (const model of modelPriority) {
            const startIdx = accounts.indexOf(currentEmail);
            for (let i = 0; i < accounts.length; i++) {
                const acc = accounts[(Math.max(0, startIdx) + i) % accounts.length];
                const info = statusDb[`${acc}:${model}`];
                if (!info) continue;
                if (info.quota >= this.threshold || (info.resetAt && now > info.resetAt)) {
                    if (acc === currentEmail && model === currentModel) choice = { email: acc, model, reason: 'Maintain' };
                    else if (modelPriority.indexOf(model) < modelPriority.indexOf(currentModel)) choice = { email: acc, model, reason: 'Upgrade Model' };
                    else if ((statusDb[`${currentEmail}:${currentModel}`]?.quota || 0) < this.threshold) choice = { email: acc, model, reason: 'Quota Low' };
                    if (choice) break;
                }
            }
            if (choice) break;
        }

        if (!choice) return;
        if (choice.reason === 'Maintain') {
            console.log("\n✅ Status Quo: Maintaining current setup.");
        } else {
            this.performRotation(authData, choice, currentEmail, currentModel);
        }
        await this.warmup(statusDb, authData, modelPriority, accounts);
    }

    performRotation(authData, choice, currentEmail, currentModel) {
        const nextKey = `google-antigravity:${choice.email}`;
        authData.profiles[this.VIP_KEY] = { ...authData.profiles[nextKey], email: 'vip_rotation_active' };
        this.writeJson(this.paths.authProfiles, authData);

        try { execSync(`${this.openclawBin} models set ${choice.model}`); } catch (e) { }
        try {
            const patch = JSON.stringify({ key: 'agent:main:main', model: choice.model });
            execSync(`${this.openclawBin} gateway call sessions.patch --params '${patch}'`);
        } catch (e) { }

        this.writeJson(this.paths.rotationState, {
            lastRotation: Date.now(), previousAccount: currentEmail, newAccount: choice.email,
            previousModel: currentModel, newModel: choice.model, pendingNotification: true, reason: choice.reason
        });

        const zhReason = { 'Maintain': '维持', 'Upgrade Model': '调度更高优先级', 'Quota Low': '余量过低' }[choice.reason] || choice.reason;
        this.appendLog(`✅ 已轮换账号：${this.shortEmail(choice.email)} | 模型：${choice.model.split('/').pop()} | 原因：${zhReason}`);
        console.log(`\n✅ Rotation: ${this.shortEmail(currentEmail)} → ${this.shortEmail(choice.email)} (${zhReason})`);
    }

    async warmup(statusDb, authData, modelPriority, accounts) {
        const TOP = modelPriority.slice(0, 3);
        const toW = [];
        for (const acc of accounts) {
            for (const m of TOP) {
                const info = statusDb[`${acc}:${m}`];
                if (info && info.quota >= 100 && !info.resetAt) toW.push({ acc, m });
            }
        }
        if (toW.length === 0) return;
        console.log(`\n🔥 Warming up ${toW.length} models...`);
        for (const { acc, m } of toW) {
            try {
                const originalVip = authData.profiles[this.VIP_KEY];
                authData.profiles[this.VIP_KEY] = { ...authData.profiles[`google-antigravity:${acc}`], email: 'warmup_temp' };
                this.writeJson(this.paths.authProfiles, authData);
                const sId = `warmup-${Date.now()}`;
                execSync(`${this.openclawBin} gateway call sessions.patch --params '{"key":"agent:main:${sId}","model":"${m}"}'`);
                execSync(`timeout 10 ${this.openclawBin} agent --session-id ${sId} --message "1" --json 2>/dev/null || true`);
                if (originalVip) { authData.profiles[this.VIP_KEY] = originalVip; this.writeJson(this.paths.authProfiles, authData); }
                console.log(`   ✅ ${this.shortEmail(acc)} / ${m.split('/').pop()}`);
            } catch (e) { }
        }
    }
}

module.exports = Rotator;
