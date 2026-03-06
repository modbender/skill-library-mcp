/**
 * Content Hash 去重
 * 使用 MD5(title | date | body[:200]) 生成 16 位指纹
 */
const crypto = require('crypto');
const fs = require('fs');

function computeHash(entry) {
    const input = `${entry.title}|${entry.date}|${(entry.body || '').slice(0, 200)}`;
    return crypto.createHash('md5').update(input, 'utf-8').digest('hex').slice(0, 16);
}

/**
 * 加载同步状态（hash → 文件路径映射）
 * @param {string} statePath - sync-state.json 路径
 * @returns {object} { hashes: {hash: filePath}, lastSync: string }
 */
function loadState(statePath) {
    try {
        const raw = fs.readFileSync(statePath, 'utf-8');
        return JSON.parse(raw);
    } catch {
        return { hashes: {}, lastSync: null };
    }
}

/**
 * 保存同步状态
 */
function saveState(statePath, state) {
    state.lastSync = new Date().toISOString();
    fs.writeFileSync(statePath, JSON.stringify(state, null, 2), 'utf-8');
}

/**
 * 检查条目是否已同步
 * @param {object} entry - 解析后的日志条目
 * @param {object} state - 同步状态
 * @returns {{ isDuplicate: boolean, hash: string }}
 */
function checkDuplicate(entry, state) {
    const hash = computeHash(entry);
    return {
        isDuplicate: hash in state.hashes,
        hash,
    };
}

/**
 * 清理状态中引用了已不存在文件的条目
 * @param {object} state
 * @returns {{ removed: number, state: object }}
 */
function cleanupState(state) {
    let removed = 0;
    const cleaned = { ...state, hashes: {} };

    for (const [hash, filePath] of Object.entries(state.hashes)) {
        if (fs.existsSync(filePath)) {
            cleaned.hashes[hash] = filePath;
        } else {
            removed++;
        }
    }

    return { removed, state: cleaned };
}

module.exports = { computeHash, loadState, saveState, checkDuplicate, cleanupState };
