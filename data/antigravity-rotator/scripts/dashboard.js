const fs = require('fs');
const http = require('http');
const path = require('path');
const { exec, execSync } = require('child_process');

class Dashboard {
    constructor(config) {
        this.config = config;
        this.configPath = path.resolve(__dirname, '../config.json');
        this.home = config.paths.home || process.env.HOME;
        
        this.paths = {
            authProfiles: path.resolve(this.home, config.paths.authProfiles),
            statusDb: path.resolve(this.home, config.paths.statusDb),
            rotationLog: path.resolve(this.home, config.paths.rotationLog),
            rotationState: path.resolve(this.home, config.paths.rotationState)
        };

        // Path handling
        this.openclawBin = config.openclawBin;
        if (!this.openclawBin) {
            try { this.openclawBin = execSync('which openclaw', { encoding: 'utf8' }).trim(); } catch(e) {}
        }

        // Inject PATH for node/openclaw compatibility
        const nodeBinPath = path.dirname(process.execPath);
        process.env.PATH = nodeBinPath + ':' + process.env.PATH;

        this.getCoreModels = () => {
            const priority = this.config.modelPriority || [];
            return priority.slice(0, 3);
        };
    }

    readJson(p) { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return {}; } }
    writeJson(p, d) { fs.writeFileSync(p, JSON.stringify(d, null, 2)); }

    getActiveAccount() {
        try {
            const authData = this.readJson(this.paths.authProfiles);
            const vip = authData.profiles?.['google-antigravity:vip_rotation'];
            if (!vip?.access) return null;
            for (const acc of this.config.accounts) {
                const realKey = `google-antigravity:${acc}`;
                if (authData.profiles?.[realKey]?.access === vip.access) return acc;
            }
        } catch (e) { }
        return null;
    }

    getRotationLogs() {
        try {
            const content = fs.readFileSync(this.paths.rotationLog, 'utf8');
            const lines = content.trim().split('\n').slice(-100).reverse();
            return lines.map(line => {
                const match = line.match(/\[(.*?)\] (.*)/);
                if (match) {
                    let time = match[1];
                    let msg = match[2];
                    try { if (time.includes('T') || time.includes('-')) time = new Date(time).toLocaleTimeString('zh-CN'); } catch(e) {}
                    return { time, message: msg };
                }
                return { time: '', message: line };
            });
        } catch (e) { return []; }
    }

    async getDetailedLog() {
        try {
            const cronLog = path.join(this.home, '.openclaw/workspace/memory/cron-rotate.log');
            if (fs.existsSync(cronLog)) {
                const content = fs.readFileSync(cronLog, 'utf8');
                const lastPart = content.slice(-20000);
                const sections = lastPart.split(/=== (余量查询 & 自动轮换|Antigravity Rotator Engine)/);
                if (sections.length > 1) return '=== ' + sections.pop();
                return lastPart;
            }
        } catch (e) {}
        return '暂无详细日志数据。';
    }

    formatTimeLeft(resetAt) {
        const now = Date.now();
        const diff = resetAt - now;
        if (diff <= 0) return '已满';
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        return hours > 0 ? `${hours}时 ${mins}分` : `${mins}分钟`;
    }

    generateHTML() {
        const statusDb = this.readJson(this.paths.statusDb);
        const logs = this.getRotationLogs();
        const now = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });

        let activeAccount = null;
        let activeModel = null;
        if (this.openclawBin) {
            try {
                const statusJson = execSync(`${this.openclawBin} gateway call status --params "{}" --json`, { encoding: 'utf8' });
                const realStatus = JSON.parse(statusJson);
                const mainSession = realStatus.sessions?.recent?.find(s => s.key === 'agent:main:main');
                activeModel = mainSession?.model;
            } catch (e) {}
        }

        activeAccount = this.getActiveAccount();
        const coreModelKeys = this.getCoreModels();
        const allModelKeys = this.config.modelPriority || [];

        let accountCards = '';
        for (const acc of this.config.accounts) {
            if (!acc || typeof acc !== 'string' || !acc.includes('@')) continue;
            const isActive = acc === activeAccount;
            const shortName = acc.split('@')[0];
            let modelsHtml = '';
            let lastUpdated = 0;

            for (const modelKey of coreModelKeys) {
                const key = `${acc}:${modelKey}`;
                const info = statusDb[key];
                if (!info) continue;
                const quota = info.quota || 0;
                const resetText = info.resetAt ? this.formatTimeLeft(info.resetAt) : '-';
                if (info.updatedAt > lastUpdated) lastUpdated = info.updatedAt;
                let barClass = quota < 20 ? 'bar-critical' : (quota < 50 ? 'bar-warning' : 'bar-high');
                const displayName = modelKey.replace('google-antigravity/', '');
                const isModelCurrentlyActive = isActive && (activeModel === modelKey || activeModel === modelKey.split('/').pop());

                modelsHtml += `
                <div class="model-row ${isModelCurrentlyActive ? 'active-model-row' : ''}">
                    <div class="model-info">
                        <span class="model-name">${displayName} ${isModelCurrentlyActive ? '🔥' : ''}</span>
                        <span class="model-quota">${quota}%</span>
                    </div>
                    <div class="progress-bg"><div class="progress-bar ${barClass}" style="width: ${quota}%"></div></div>
                    <div class="model-meta">重置: ${resetText}</div>
                </div>`;
            }

            const updateTimeStr = lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : '无数据';
            accountCards += `
            <div class="card ${isActive ? 'active-card' : ''}">
                <div class="card-header">
                    <div class="account-name">${isActive ? '🟢' : '⚫'} ${shortName}</div>
                    ${isActive ? '<span class="badge">正在使用</span>' : ''}
                    <button class="delete-btn" onclick="confirmRemoveAccount('${acc}')" title="移除监控">×</button>
                </div>
                <div class="card-body">${modelsHtml || '<div style="color: #666; font-size: 0.8rem;">暂无配额数据</div>'}</div>
                <div class="card-footer">更新: ${updateTimeStr}</div>
            </div>`;
        }

        let priorityHtml = allModelKeys.map((m, i) => {
            const displayName = m.replace('google-antigravity/', '');
            return `
            <div class="priority-item" data-model="${m}" data-index="${i}">
                <span class="priority-label">${i + 1}. ${displayName}</span>
                <div class="priority-controls">
                    <button onclick="moveUp(this)" ${i === 0 ? 'disabled' : ''}>↑</button>
                    <button onclick="moveDown(this)" ${i === allModelKeys.length - 1 ? 'disabled' : ''}>↓</button>
                </div>
            </div>`;
        }).join('');

        let logsHtml = logs.map(l => `
            <div class="log-entry" onclick="viewLogDetail()">
                <span class="log-time">${l.time || ''}</span>
                <span class="log-msg">${l.message}</span>
                <span class="log-arrow">›</span>
            </div>
        `).join('');

        return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Antigravity 矩阵看板</title>
    <style>
        :root { --bg: #05050a; --card-bg: rgba(20, 20, 35, 0.6); --active-border: #00ff9d; --text: #e0e0e0; --text-dim: #808080; --bar-bg: #151525; --high: #00ff9d; --warn: #ffcc00; --crit: #ff0055; --accent: #00f260; --cyber-blue: #00d2ff; }
        * { box-sizing: border-box; }
        body { background-color: var(--bg); background-image: radial-gradient(circle at 50% 50%, #101025 0%, #05050a 100%); color: var(--text); font-family: 'JetBrains Mono', 'Inter', "Microsoft YaHei", monospace; margin: 0; padding: 20px; overflow-x: hidden; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--accent); box-shadow: 0 0 10px var(--accent); }
        .cyber-scroll { scrollbar-width: thin; scrollbar-color: #333 transparent; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 15px; }
        .title-group { display: flex; align-items: baseline; gap: 20px; }
        .title { font-size: 1.6rem; font-weight: 800; letter-spacing: 1px; background: linear-gradient(90deg, #00f260, #00d2ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .status-pill { font-size: 0.7rem; padding: 2px 10px; border-radius: 20px; background: rgba(0, 255, 157, 0.05); color: var(--accent); border: 1px solid rgba(0, 255, 157, 0.2); font-weight: 700; }
        .top-actions { display: flex; gap: 10px; align-items: center; }
        .btn-add-small { background: rgba(255,255,255,0.05); color: #fff; border: 1px solid #444; padding: 6px 15px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; cursor: pointer; transition: all 0.2s; }
        .btn-add-small:hover { background: var(--accent); color: #000; border-color: var(--accent); box-shadow: 0 0 15px rgba(0,242,96,0.3); }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }
        .card { background: var(--card-bg); backdrop-filter: blur(10px); border-radius: 12px; padding: 18px; border: 1px solid #222; transition: all 0.3s ease; position: relative; }
        .card:hover { transform: translateY(-3px); border-color: #444; box-shadow: 0 10px 30px rgba(0,0,0,0.6); }
        .active-card { border: 1px solid rgba(0, 255, 157, 0.4); background: rgba(0, 255, 157, 0.02); }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .account-name { font-size: 1rem; font-weight: 700; color: #fff; }
        .badge { background: rgba(0, 255, 157, 0.1); color: var(--active-border); padding: 2px 8px; border-radius: 4px; font-size: 0.6rem; font-weight: 800; }
        .model-row { margin-bottom: 12px; padding: 4px; }
        .model-info { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.8rem; font-weight: 600; }
        .progress-bg { background: var(--bar-bg); height: 4px; border-radius: 2px; overflow: hidden; }
        .progress-bar { height: 100%; border-radius: 2px; transition: width 1s ease; }
        .bar-high { background: var(--high); }
        .bar-warning { background: var(--warn); }
        .bar-critical { background: var(--crit); }
        .model-meta { font-size: 0.65rem; color: var(--text-dim); text-align: right; margin-top: 3px; }
        .card-footer { margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.03); font-size: 0.65rem; color: var(--text-dim); }
        .dashboard-main { display: grid; grid-template-columns: 350px 1fr; gap: 20px; }
        .side-box { background: var(--card-bg); border-radius: 12px; border: 1px solid #222; padding: 20px; display: flex; flex-direction: column; }
        .section-title { font-size: 0.9rem; font-weight: 800; margin-bottom: 15px; color: #888; text-transform: uppercase; letter-spacing: 1px; display: flex; align-items: center; }
        .section-title::before { content: ''; width: 3px; height: 14px; background: var(--accent); margin-right: 8px; }
        .priority-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; background: rgba(0,0,0,0.2); margin-bottom: 8px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.02); }
        .priority-label { font-size: 0.8rem; }
        .priority-controls button { background: #1a1a25; color: #aaa; border: 1px solid #333; padding: 2px 8px; border-radius: 4px; cursor: pointer; margin-left: 3px; font-size: 0.7rem; }
        .priority-controls button:hover:not(:disabled) { color: var(--accent); border-color: var(--accent); }
        .log-container { flex-grow: 1; overflow-y: auto; max-height: 500px; padding-right: 10px; }
        .log-entry { font-size: 0.75rem; padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,0.03); display: flex; align-items: center; cursor: pointer; border-radius: 4px; margin-bottom: 2px; }
        .log-entry:hover { background: rgba(255,255,255,0.03); }
        .log-time { color: var(--text-dim); width: 80px; flex-shrink: 0; }
        .log-msg { color: #bbb; flex-grow: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .delete-btn { background: none; border: none; color: #555; font-size: 1.2rem; cursor: pointer; transition: color 0.2s; }
        .delete-btn:hover { color: var(--crit); }
        #modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); backdrop-filter: blur(5px); z-index: 1000; display: none; align-items: center; justify-content: center; opacity: 0; transition: opacity 0.2s; }
        #modal-box { background: #0f0f1a; border: 1px solid #333; border-radius: 12px; width: 90%; max-width: 600px; max-height: 85vh; display: flex; flex-direction: column; transform: translateY(10px); transition: transform 0.2s; }
        .modal-header { padding: 15px 20px; border-bottom: 1px solid #222; display: flex; justify-content: space-between; align-items: center; }
        .modal-title { font-size: 1rem; font-weight: 800; color: var(--accent); }
        .modal-body { padding: 20px; overflow-y: auto; color: #ccc; font-size: 0.9rem; line-height: 1.6; }
        .modal-footer { padding: 12px 20px; border-top: 1px solid #222; display: flex; justify-content: flex-end; gap: 10px; }
        .modal-btn { padding: 8px 16px; border-radius: 6px; border: none; font-weight: 700; cursor: pointer; font-size: 0.8rem; }
        .modal-btn-primary { background: var(--accent); color: #000; }
        .modal-btn-secondary { background: #222; color: #eee; }
        .visible { display: flex !important; opacity: 1 !important; }
        .visible #modal-box { transform: translateY(0) !important; }
        .code-block { background: #000; padding: 15px; border-radius: 8px; color: #0f0; position: relative; border: 1px solid #222; margin: 10px 0; font-size: 0.8rem; word-break: break-all; }
        .copy-tag { position: absolute; top: 8px; right: 8px; background: rgba(0,255,157,0.1); color: var(--accent); font-size: 0.6rem; padding: 2px 6px; border-radius: 4px; border: 1px solid var(--accent); cursor: pointer; }
        .btn-rotate-fixed { position: fixed; bottom: 25px; right: 25px; width: 50px; height: 50px; background: var(--accent); color: #000; border: none; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 0 20px rgba(0,255,157,0.3); transition: all 0.3s; z-index: 99; }
        .btn-rotate-fixed:hover { transform: rotate(180deg) scale(1.1); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title-group">
                <div class="title">Antigravity 矩阵看板</div>
                <div class="status-pill">● 在线</div>
            </div>
            <div class="top-actions">
                <span style="font-size: 0.7rem; color: #555; margin-right: 15px;" id="live-clock">${now}</span>
                <button class="btn-add-small" onclick="syncAccounts()">同步凭证</button>
                <button class="btn-add-small" onclick="startOAuth()" style="background: var(--accent); color: #000; border-color: var(--accent);">+ 添加账号</button>
            </div>
        </div>
        
        <div class="grid">${accountCards}</div>

        <div class="dashboard-main">
            <div class="side-box">
                <div class="section-title">优先级序列</div>
                <div id="priority-list" style="flex-grow: 1;">${priorityHtml}</div>
                <button onclick="savePriority()" style="width: 100%; margin-top: 15px; background: #222; color: var(--accent); border: 1px solid var(--accent); padding: 10px; border-radius: 8px; cursor: pointer; font-weight: 800; font-size: 0.75rem;">保存配置</button>
                <div id="priority-status" style="font-size: 0.6rem; margin-top: 8px; text-align: center;"></div>
            </div>
            
            <div class="side-box">
                <div class="section-title">轮换日志记录</div>
                <div class="log-container cyber-scroll" id="log-list">${logsHtml}</div>
            </div>
        </div>
    </div>

    <button class="btn-rotate-fixed" onclick="triggerRotate()" title="强制执行轮换">🚀</button>

    <div id="modal-overlay"><div id="modal-box"><div class="modal-header"><div class="modal-title" id="modal-title"></div><button onclick="closeModal()" style="background:none;border:none;color:#555;font-size:1.5rem;cursor:pointer;">×</button></div><div class="modal-body" id="modal-body"></div><div class="modal-footer" id="modal-footer"></div></div></div>

    <script>
        let priorityChanged = false;
        function showModal(title, content, options = {}) {
            document.getElementById('modal-title').textContent = title;
            document.getElementById('modal-body').innerHTML = content;
            const footer = document.getElementById('modal-footer'); footer.innerHTML = '';
            if (options.buttons) {
                options.buttons.forEach(btn => {
                    const b = document.createElement('button'); b.className = 'modal-btn ' + (btn.primary ? 'modal-btn-primary' : 'modal-btn-secondary'); b.textContent = btn.text;
                    b.onclick = () => { if (btn.onclick) btn.onclick(); if (!btn.keepOpen) closeModal(); }; footer.appendChild(b);
                });
            } else { footer.innerHTML = '<button class="modal-btn modal-btn-secondary" onclick="closeModal()">好的</button>'; }
            document.getElementById('modal-overlay').classList.add('visible');
        }
        function closeModal() { document.getElementById('modal-overlay').classList.remove('visible'); }
        function moveUp(btn) { const item = btn.closest('.priority-item'); const prev = item.previousElementSibling; if (prev) { item.parentNode.insertBefore(item, prev); updatePriorityLabels(); markChanged(); } }
        function moveDown(btn) { const item = btn.closest('.priority-item'); const next = item.nextElementSibling; if (next) { item.parentNode.insertBefore(next, item); updatePriorityLabels(); markChanged(); } }
        function updatePriorityLabels() {
            const items = document.querySelectorAll('#priority-list .priority-item');
            items.forEach((item, i) => {
                const label = item.querySelector('.priority-label');
                const text = label.textContent.replace(/^[0-9]+\\.\\s*/, '');
                label.textContent = (i + 1) + '. ' + text;
                const buttons = item.querySelectorAll('button'); buttons[0].disabled = (i === 0); buttons[1].disabled = (i === items.length - 1);
            });
        }
        function markChanged() { priorityChanged = true; document.getElementById('priority-status').textContent = '⚠️ 有未保存的更改'; document.getElementById('priority-status').style.color = 'var(--warn)'; }
        async function savePriority() {
            if (!priorityChanged) return;
            const items = document.querySelectorAll('#priority-list .priority-item');
            const newOrder = Array.from(items).map(item => item.dataset.model);
            try {
                await apiCall('setPriority', { order: newOrder });
                priorityChanged = false; document.getElementById('priority-status').textContent = '✅ 已保存'; document.getElementById('priority-status').style.color = 'var(--high)';
            } catch (e) { showModal('错误', e.message); }
        }
        async function apiCall(action, data) {
            const res = await fetch('/api', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action, ...data }) });
            const result = await res.json(); if (result.success) return result; throw new Error(result.message || '操作失败');
        }
        function confirmRemoveAccount(email) {
            showModal('确认移除', '<p>确定要从监控列表中移除账号 <strong>' + email + '</strong> 吗？</p>', {
                buttons: [{ text: '取消' }, { text: '确定移除', primary: true, onclick: () => apiCall('removeAccount', { email }).then(() => location.reload()) }]
            });
        }
        function triggerRotate() { apiCall('triggerRotate', {}).then(() => showModal('成功', '轮换指令已发出。')); }
        function startOAuth() {
            const content = '<p>请在终端运行以下命令完成授权：</p><div class="code-block">openclaw models auth login --provider google-antigravity<span class="copy-tag" onclick="copyText(\\'openclaw models auth login --provider google-antigravity\\')">复制命令</span></div><p style="font-size:0.8rem;color:#888;">完成后点击下方按钮同步账号信息。</p>';
            showModal('添加账号', content, { buttons: [{ text: '取消' }, { text: '我已完成登录 - 立即同步', primary: true, onclick: () => syncAccounts() }] });
        }
        function copyText(text) { navigator.clipboard.writeText(text).then(() => alert('已复制到剪贴板！')); }
        function syncAccounts() {
            apiCall('syncAccounts', {}).then(result => {
                if (result.added > 0) { showModal('同步完成', '<p>成功发现并添加了 ' + result.added + ' 个新账号凭证。</p>', { buttons: [{ text: '刷新', primary: true, onclick: () => location.reload() }] }); }
                else { showModal('同步完成', '未发现新凭证。'); }
            }).catch(err => showModal('同步失败', err.message));
        }
        async function viewLogDetail() {
            try { const result = await apiCall('getDetailedLog', {}); showModal('轮换日志详情 - 完整输出', '<pre style="background:#000;padding:15px;border-radius:10px;font-size:0.7rem;overflow-x:auto;border:1px solid #222;color:#8f8;line-height:1.4;">' + result.log + '</pre>'); }
            catch (e) { showModal('错误', '无法获取日志。'); }
        }
        setInterval(() => { document.getElementById('live-clock').textContent = new Date().toLocaleString('zh-CN'); }, 1000);
        setTimeout(() => location.reload(), 60000);
    </script>
</body>
</html>`;
    }

    start() {
        const port = this.config.dashboardPort || 18090;
        const server = http.createServer(async (req, res) => {
            if (req.url === '/' && req.method === 'GET') {
                res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
                res.end(this.generateHTML());
            } else if (req.url === '/api' && req.method === 'POST') {
                let body = '';
                req.on('data', chunk => body += chunk);
                req.on('end', async () => {
                    try {
                        const data = JSON.parse(body);
                        const result = await this.handleApi(data);
                        res.writeHead(200, { 'Content-Type': 'application/json' });
                        res.end(JSON.stringify(result));
                    } catch (e) {
                        res.writeHead(400);
                        res.end(JSON.stringify({ success: false, message: e.message }));
                    }
                });
            } else {
                res.writeHead(404);
                res.end('Not Found');
            }
        });
        server.listen(port, '0.0.0.0', () => { console.log(`\n🔮 Antigravity Dashboard started on http://0.0.0.0:${port}`); });
    }

    async handleApi(data) {
        const { action } = data;
        let changed = false;
        const currentConfig = this.readJson(this.configPath);

        if (action === 'addAccount') {
            if (!currentConfig.accounts.includes(data.email)) { currentConfig.accounts.push(data.email); changed = true; }
        } else if (action === 'removeAccount') {
            currentConfig.accounts = currentConfig.accounts.filter(a => a !== data.email); changed = true;
        } else if (action === 'syncAccounts') {
            const authData = this.readJson(this.paths.authProfiles);
            const antigravityAccounts = Object.keys(authData.profiles || {}).filter(k => k.startsWith('google-antigravity:')).map(k => k.replace('google-antigravity:', ''));
            let added = 0;
            for (const email of antigravityAccounts) { if (!currentConfig.accounts.includes(email)) { currentConfig.accounts.push(email); added++; changed = true; } }
            if (added > 0) { this.writeJson(this.configPath, currentConfig); this.config = currentConfig; }
            return { success: true, added, accounts: antigravityAccounts };
        } else if (action === 'movePriority') {
            const { index, direction } = data;
            const newIndex = index + direction;
            if (newIndex >= 0 && newIndex < currentConfig.modelPriority.length) {
                const item = currentConfig.modelPriority.splice(index, 1)[0];
                currentConfig.modelPriority.splice(newIndex, 0, item); changed = true;
            }
        } else if (action === 'setPriority') {
            if (Array.isArray(data.order) && data.order.length > 0) { currentConfig.modelPriority = data.order; changed = true; }
        } else if (action === 'triggerRotate') {
            const indexPath = path.resolve(__dirname, '../index.js');
            exec(`node ${indexPath} --action=rotate`, (err, stdout) => { console.log('Manual rotation output:', stdout); });
            return { success: true, message: 'Rotation triggered' };
        } else if (action === 'getDetailedLog') {
            const log = await this.getDetailedLog();
            return { success: true, log };
        }

        if (changed) { this.writeJson(this.configPath, currentConfig); this.config = currentConfig; return { success: true }; }
        return { success: false, message: 'No action taken' };
    }
}

module.exports = Dashboard;
