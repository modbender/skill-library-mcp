/**
 * Clawlet - Nostr 智能管家
 * OpenClaw Skill for Nostr integration
 */

const { generateSecretKey, getPublicKey, finalizeEvent, verifyEvent } = require('nostr-tools/pure');
const { npubEncode, decode } = require('nostr-tools/nip19');
const { encrypt: nip04Encrypt, decrypt: nip04Decrypt } = require('nostr-tools/nip04');
const WebSocket = require('ws');
const { HttpsProxyAgent } = require('https-proxy-agent');
const fs = require('fs');
const path = require('path');

// 代理配置
const PROXY = process.env.HTTPS_PROXY || process.env.https_proxy || 'http://127.0.0.1:7890';
const proxyAgent = new HttpsProxyAgent(PROXY);

// 配置
const RELAYS = [
    'wss://relay.damus.io',
    'wss://nos.lol',
    'wss://nostr.wine'
];

const DATA_DIR = path.join(__dirname, 'data');
const IDENTITIES_FILE = path.join(DATA_DIR, 'identities.json');

// 确保数据目录存在
function ensureDataDir() {
    if (!fs.existsSync(DATA_DIR)) {
        fs.mkdirSync(DATA_DIR, { recursive: true });
    }
}

// 加载用户身份
function loadIdentities() {
    ensureDataDir();
    if (fs.existsSync(IDENTITIES_FILE)) {
        return JSON.parse(fs.readFileSync(IDENTITIES_FILE, 'utf-8'));
    }
    return {};
}

// 保存用户身份
function saveIdentities(identities) {
    ensureDataDir();
    fs.writeFileSync(IDENTITIES_FILE, JSON.stringify(identities, null, 2));
}

// 获取用户身份（按用户ID）
function getIdentity(userId) {
    const identities = loadIdentities();
    return identities[userId] || null;
}

// 生成新身份
function createIdentity(userId, name = '') {
    const identities = loadIdentities();
    
    // 生成密钥对
    const sk = generateSecretKey();
    const pk = getPublicKey(sk);
    const npub = npubEncode(pk);
    
    // 存储私钥（hex格式）
    const skHex = Buffer.from(sk).toString('hex');
    
    identities[userId] = {
        privateKey: skHex,
        publicKey: pk,
        npub: npub,
        name: name || `user_${userId.slice(0, 8)}`,
        createdAt: new Date().toISOString()
    };
    
    saveIdentities(identities);
    
    return {
        npub: npub,
        name: identities[userId].name,
        createdAt: identities[userId].createdAt
    };
}

// 转换 npub 到 hex
function npubToHex(npub) {
    try {
        const decoded = decode(npub);
        if (decoded.type === 'npub') {
            return decoded.data;
        }
    } catch (e) {
        // 可能是 hex 格式
        if (/^[0-9a-f]{64}$/.test(npub)) {
            return npub;
        }
    }
    return null;
}

// 连接 Relay 并发送消息
async function publishToRelays(signedEvent) {
    return new Promise((resolve, reject) => {
        const results = [];
        let completed = 0;
        
        // 使用 Promise.allSettled 来处理所有 relay
        const promises = RELAYS.map(relayUrl => {
            return new Promise((res) => {
                const ws = new WebSocket(relayUrl, { agent: proxyAgent });
                let settled = false;
                
                ws.on('open', () => {
                    ws.send(JSON.stringify(['EVENT', signedEvent]));
                });
                
                ws.on('message', (data) => {
                    try {
                        const msg = JSON.parse(data.toString());
                        if (msg[0] === 'OK') {
                            settled = true;
                            res({ relay: relayUrl, success: true, eventId: msg[1] });
                            ws.close();
                        } else if (msg[0] === 'NOTICE') {
                            settled = true;
                            res({ relay: relayUrl, success: false, error: msg[1] });
                            ws.close();
                        }
                    } catch (e) {}
                });
                
                ws.on('error', (err) => {
                    if (!settled) {
                        settled = true;
                        res({ relay: relayUrl, success: false, error: '连接失败: ' + err.message });
                    }
                });
                
                ws.on('close', () => {
                    if (!settled) {
                        settled = true;
                        res({ relay: relayUrl, success: false, error: '连接关闭' });
                    }
                });
                
                // 10秒超时
                setTimeout(() => {
                    if (!settled) {
                        settled = true;
                        ws.close();
                        res({ relay: relayUrl, success: false, error: '超时' });
                    }
                }, 10000);
            });
        });
        
        Promise.allSettled(promises).then(results => {
            resolve(results.map(r => r.value || r.reason));
        });
    });
}

// 发布文本
async function postText(userId, content) {
    const identity = getIdentity(userId);
    if (!identity) {
        return { success: false, error: '请先生成 Nostr 身份' };
    }
    
    // 创建事件
    const event = {
        kind: 1, // 文本笔记
        created_at: Math.floor(Date.now() / 1000),
        tags: [],
        content: content
    };
    
    // 签名
    const sk = Buffer.from(identity.privateKey, 'hex');
    const signedEvent = finalizeEvent(event, sk);
    
    // 验证
    if (!verifyEvent(signedEvent)) {
        return { success: false, error: '签名验证失败' };
    }
    
    // 发布到 Relays
    const results = await publishToRelays(signedEvent);
    
    const successCount = results.filter(r => r.success).length;
    
    return {
        success: successCount > 0,
        eventId: signedEvent.id,
        content: content,
        relays: results,
        message: `已发布到 ${successCount}/${RELAYS.length} 个 Relay`
    };
}

// 关注用户
async function followUser(userId, targetNpub) {
    const identity = getIdentity(userId);
    if (!identity) {
        return { success: false, error: '请先生成 Nostr 身份' };
    }
    
    const targetPubkey = npubToHex(targetNpub);
    if (!targetPubkey) {
        return { success: false, error: '无效的用户 ID' };
    }
    
    // 创建关注事件 (kind 3)
    const event = {
        kind: 3,
        created_at: Math.floor(Date.now() / 1000),
        tags: [['p', targetPubkey]],
        content: ''
    };
    
    const sk = Buffer.from(identity.privateKey, 'hex');
    const signedEvent = finalizeEvent(event, sk);
    
    if (!verifyEvent(signedEvent)) {
        return { success: false, error: '签名验证失败' };
    }
    
    const results = await publishToRelays(signedEvent);
    const successCount = results.filter(r => r.success).length;
    
    return {
        success: successCount > 0,
        targetNpub: targetNpub,
        message: successCount > 0 ? `已关注 ${targetNpub}` : '关注失败'
    };
}

// 从 Relay 获取数据
async function fetchFromRelays(filters, timeoutMs = 10000) {
    return new Promise((resolve) => {
        const events = [];
        let completed = 0;
        const subId = `clawlet_${Date.now()}`;
        
        RELAYS.forEach(relayUrl => {
            const ws = new WebSocket(relayUrl, { agent: proxyAgent });
            let resolved = false;
            
            ws.on('open', () => {
                ws.send(JSON.stringify(['REQ', subId, ...filters]));
            });
            
            ws.on('message', (data) => {
                try {
                    const msg = JSON.parse(data.toString());
                    if (msg[0] === 'EVENT' && msg[1] === subId) {
                        events.push(msg[2]);
                    } else if (msg[0] === 'EOSE' && msg[1] === subId) {
                        if (!resolved) {
                            resolved = true;
                            completed++;
                            ws.close();
                        }
                    }
                } catch (e) {}
            });
            
            ws.on('error', () => {
                completed++;
            });
            
            ws.on('close', () => {
                if (completed >= RELAYS.length) {
                    resolve(events);
                }
            });
        });
        
        setTimeout(() => {
            resolve(events);
        }, timeoutMs);
    });
}

// 获取时间线
async function getTimeline(userId, limit = 20) {
    const identity = getIdentity(userId);
    if (!identity) {
        return { success: false, error: '请先生成 Nostr 身份' };
    }
    
    // 获取最新事件
    const events = await fetchFromRelays([{ kinds: [1], limit: limit }]);
    
    // 去重并排序
    const uniqueEvents = [];
    const seenIds = new Set();
    
    for (const event of events) {
        if (!seenIds.has(event.id)) {
            seenIds.add(event.id);
            uniqueEvents.push({
                id: event.id,
                pubkey: event.pubkey,
                npub: npubEncode(event.pubkey),
                content: event.content,
                created_at: new Date(event.created_at * 1000).toISOString()
            });
        }
    }
    
    uniqueEvents.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    return {
        success: true,
        events: uniqueEvents.slice(0, limit)
    };
}

// 获取用户资料
async function getProfile(targetNpub) {
    const targetPubkey = npubToHex(targetNpub);
    if (!targetPubkey) {
        return { success: false, error: '无效的用户 ID' };
    }
    
    // 获取 kind 0 (用户资料)
    const events = await fetchFromRelays([{ kinds: [0], authors: [targetPubkey], limit: 1 }]);
    
    if (events.length === 0) {
        return {
            success: true,
            npub: targetNpub,
            pubkey: targetPubkey,
            profile: null,
            message: '未找到用户资料'
        };
    }
    
    try {
        const profile = JSON.parse(events[0].content);
        return {
            success: true,
            npub: targetNpub,
            pubkey: targetPubkey,
            profile: {
                name: profile.name || '',
                display_name: profile.display_name || '',
                about: profile.about || '',
                picture: profile.picture || '',
                website: profile.website || ''
            }
        };
    } catch (e) {
        return {
            success: true,
            npub: targetNpub,
            pubkey: targetPubkey,
            profile: null,
            message: '资料解析失败'
        };
    }
}

// 合规过滤 - 敏感词列表
const SENSITIVE_WORDS = [
    // 这里可以添加需要过滤的敏感词
    // 默认为空，用户可以根据需要添加
];

// 检查内容是否合规
function isContentSafe(content) {
    const lowerContent = content.toLowerCase();
    for (const word of SENSITIVE_WORDS) {
        if (lowerContent.includes(word.toLowerCase())) {
            return false;
        }
    }
    return true;
}

// AI 筛选 - 简单的关键词匹配和评分
function scoreEvent(event, interests = []) {
    let score = 0;
    const content = event.content.toLowerCase();
    
    // 基于兴趣关键词加分
    for (const interest of interests) {
        if (content.includes(interest.toLowerCase())) {
            score += 10;
        }
    }
    
    // 基于互动指标（如果有）
    const replyCount = event.tags?.filter(t => t[0] === 'e')?.length || 0;
    score += replyCount * 2;
    
    // 基于内容长度（太短的可能没价值）
    if (content.length > 50) score += 5;
    if (content.length > 200) score += 5;
    
    // 过滤垃圾内容
    if (content.includes('关注我') || content.includes('加微信')) {
        score -= 20;
    }
    
    return Math.max(0, score);
}

// 获取用户兴趣
function getUserInterests(userId) {
    const identities = loadIdentities();
    const identity = identities[userId];
    return identity?.interests || [];
}

// 设置用户兴趣
function setUserInterests(userId, interests) {
    const identities = loadIdentities();
    if (identities[userId]) {
        identities[userId].interests = interests;
        saveIdentities(identities);
        return true;
    }
    return false;
}

// 获取用户昵称映射
function getNicknames(userId) {
    const identities = loadIdentities();
    const identity = identities[userId];
    return identity?.nicknames || {};
}

// 设置昵称
function setNickname(userId, nickname, npub) {
    const identities = loadIdentities();
    if (!identities[userId]) return false;
    
    if (!identities[userId].nicknames) {
        identities[userId].nicknames = {};
    }
    
    // 转换 npub 到 hex 存储完整信息
    const pubkey = npubToHex(npub);
    if (!pubkey) return false;
    
    identities[userId].nicknames[nickname.toLowerCase()] = {
        npub: npub,
        pubkey: pubkey,
        createdAt: new Date().toISOString()
    };
    
    saveIdentities(identities);
    return true;
}

// 删除昵称
function removeNickname(userId, nickname) {
    const identities = loadIdentities();
    if (!identities[userId] || !identities[userId].nicknames) return false;
    
    delete identities[userId].nicknames[nickname.toLowerCase()];
    saveIdentities(identities);
    return true;
}

// 通过昵称或 npub 查找用户
function resolveRecipient(userId, nameOrNpub) {
    // 先检查是否是昵称
    const nicknames = getNicknames(userId);
    const lowerName = nameOrNpub.toLowerCase();
    
    if (nicknames[lowerName]) {
        return {
            npub: nicknames[lowerName].npub,
            pubkey: nicknames[lowerName].pubkey,
            isNickname: true
        };
    }
    
    // 不是昵称，检查是否是有效的 npub
    const pubkey = npubToHex(nameOrNpub);
    if (pubkey) {
        return {
            npub: nameOrNpub,
            pubkey: pubkey,
            isNickname: false
        };
    }
    
    return null;
}

// 导出函数
module.exports = {
    // 生成身份
    clawlet_identity_create: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const name = params?.name || '';
        
        const existing = getIdentity(userId);
        if (existing) {
            return {
                success: true,
                npub: existing.npub,
                name: existing.name,
                message: '你已有 Nostr 身份'
            };
        }
        
        const identity = createIdentity(userId, name);
        return {
            success: true,
            ...identity,
            message: `Nostr 身份已创建：${identity.npub}`
        };
    },
    
    // 获取身份信息
    clawlet_identity_get: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const identity = getIdentity(userId);
        
        if (!identity) {
            return {
                success: false,
                message: '你还没有 Nostr 身份，说"生成 Nostr 身份"来创建一个'
            };
        }
        
        return {
            success: true,
            npub: identity.npub,
            name: identity.name,
            createdAt: identity.createdAt
        };
    },
    
    // 导出私钥（供用户备份）
    clawlet_identity_export: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const identity = getIdentity(userId);
        
        if (!identity) {
            return {
                success: false,
                message: '你还没有 Nostr 身份'
            };
        }
        
        return {
            success: true,
            privateKey: identity.privateKey,
            npub: identity.npub,
            warning: '请妥善保管私钥，不要泄露给他人'
        };
    },
    
    // 发布文本
    clawlet_post: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const content = params?.content || params?.text;
        
        if (!content) {
            return { success: false, message: '请提供要发布的内容' };
        }
        
        // 合规检查
        if (!isContentSafe(content)) {
            return { success: false, message: '内容包含敏感词，无法发布' };
        }
        
        return await postText(userId, content);
    },
    
    // 关注用户
    clawlet_follow: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const targetNpub = params?.npub || params?.user_id;
        
        if (!targetNpub) {
            return { success: false, message: '请提供要关注的用户 ID (npub)' };
        }
        
        return await followUser(userId, targetNpub);
    },
    
    // 获取时间线
    clawlet_timeline: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const limit = params?.limit || 20;
        
        return await getTimeline(userId, limit);
    },
    
    // 获取用户资料
    clawlet_profile: async (params, context) => {
        const targetNpub = params?.npub || params?.user_id;
        
        if (!targetNpub) {
            return { success: false, message: '请提供用户 ID (npub)' };
        }
        
        return await getProfile(targetNpub);
    },
    
    // 设置用户兴趣
    clawlet_interests_set: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const interests = params?.interests || [];
        
        if (!interests.length) {
            return { success: false, message: '请提供兴趣列表' };
        }
        
        const success = setUserInterests(userId, interests);
        return {
            success,
            interests,
            message: success ? `已设置 ${interests.length} 个兴趣标签` : '设置失败，请先生成身份'
        };
    },
    
    // 获取用户兴趣
    clawlet_interests_get: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const interests = getUserInterests(userId);
        
        return {
            success: true,
            interests,
            message: interests.length > 0 ? `你有 ${interests.length} 个兴趣标签` : '还没设置兴趣标签'
        };
    },
    
    // AI 筛选时间线
    clawlet_timeline_filtered: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const limit = params?.limit || 20;
        const minScore = params?.min_score || 5;
        
        const interests = getUserInterests(userId);
        const timeline = await getTimeline(userId, limit * 3); // 获取更多，然后筛选
        
        if (!timeline.success) {
            return timeline;
        }
        
        // 筛选和评分
        const filtered = timeline.events
            .map(event => ({
                ...event,
                score: scoreEvent(event, interests)
            }))
            .filter(event => event.score >= minScore && isContentSafe(event.content))
            .sort((a, b) => b.score - a.score)
            .slice(0, limit);
        
        return {
            success: true,
            events: filtered,
            message: `从 ${timeline.events.length} 条消息中筛选出 ${filtered.length} 条`
        };
    },
    
    // 发现推荐用户（基于兴趣）
    clawlet_discover: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const interests = getUserInterests(userId);
        
        if (interests.length === 0) {
            return {
                success: false,
                message: '请先设置兴趣标签，例如："设置我的兴趣为中医、AI、编程"'
            };
        }
        
        // 搜索包含兴趣关键词的帖子
        const events = await fetchFromRelays([
            { kinds: [1], limit: 100 }
        ]);
        
        // 找到相关作者
        const authorScores = {};
        for (const event of events) {
            const score = scoreEvent(event, interests);
            if (score > 0) {
                if (!authorScores[event.pubkey]) {
                    authorScores[event.pubkey] = { pubkey: event.pubkey, score: 0, postCount: 0 };
                }
                authorScores[event.pubkey].score += score;
                authorScores[event.pubkey].postCount += 1;
            }
        }
        
        // 排序并获取 top 用户
        const topAuthors = Object.values(authorScores)
            .sort((a, b) => b.score - a.score)
            .slice(0, 10)
            .map(a => ({
                npub: npubEncode(a.pubkey),
                pubkey: a.pubkey,
                score: a.score,
                postCount: a.postCount
            }));
        
        return {
            success: true,
            recommendations: topAuthors,
            basedOn: interests,
            message: topAuthors.length > 0 
                ? `基于你的兴趣【${interests.join('、')}】，推荐 ${topAuthors.length} 个用户`
                : '未找到相关用户'
        };
    },
    
    // 发送私信（NIP-04 加密）
    clawlet_dm_send: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const identity = getIdentity(userId);
        
        if (!identity) {
            return { success: false, message: '请先生成 Nostr 身份' };
        }
        
        const recipientName = params?.npub || params?.recipient || params?.user_id || params?.nickname;
        const content = params?.content || params?.message || params?.text;
        
        if (!recipientName) {
            return { success: false, message: '请提供收件人 ID 或昵称' };
        }
        
        if (!content) {
            return { success: false, message: '请提供私信内容' };
        }
        
        // 解析收件人（支持昵称或 npub）
        const recipient = resolveRecipient(userId, recipientName);
        if (!recipient) {
            return { success: false, message: `找不到收件人：${recipientName}。如果是昵称，请先用"添加昵称"功能设置。` };
        }
        
        // 使用 NIP-04 加密
        const sk = Buffer.from(identity.privateKey, 'hex');
        const encryptedContent = nip04Encrypt(sk, recipient.pubkey, content);
        
        // 创建私信事件（kind 4）
        const event = {
            kind: 4,  // NIP-04 加密私信
            created_at: Math.floor(Date.now() / 1000),
            tags: [['p', recipient.pubkey]],
            content: encryptedContent
        };
        
        // 签名
        const signedEvent = finalizeEvent(event, sk);
        
        if (!verifyEvent(signedEvent)) {
            return { success: false, message: '签名验证失败' };
        }
        
        // 发布到 Relays
        const results = await publishToRelays(signedEvent);
        const successCount = results.filter(r => r.success).length;
        
        const displayName = recipient.isNickname ? `${recipientName}(${recipient.npub.slice(0,12)}...)` : recipient.npub.slice(0, 20);
        
        return {
            success: successCount > 0,
            eventId: signedEvent.id,
            recipient: recipient.npub,
            displayName: displayName,
            isNickname: recipient.isNickname,
            message: successCount > 0 
                ? `私信已发送给 ${displayName}` 
                : '发送失败'
        };
    },
    
    // 接收私信
    clawlet_dm_receive: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const identity = getIdentity(userId);
        
        if (!identity) {
            return { success: false, message: '请先生成 Nostr 身份' };
        }
        
        const limit = params?.limit || 20;
        const myPubkey = identity.publicKey;
        
        // 从 Relays 获取发给我的私信（kind 4）
        // 查询条件：#p 标签包含我的 pubkey（发给我的私信）
        const events = await fetchFromRelays([
            { kinds: [4], "#p": [myPubkey], limit: limit }
        ]);
        
        // 解密私信
        const dms = [];
        const sk = Buffer.from(identity.privateKey, 'hex');
        
        for (const event of events) {
            try {
                // 获取发件人公钥
                const senderPubkey = event.pubkey;
                
                // 解密内容
                const decryptedContent = nip04Decrypt(sk, senderPubkey, event.content);
                
                dms.push({
                    id: event.id,
                    from: senderPubkey,
                    fromNpub: npubEncode(senderPubkey),
                    content: decryptedContent,
                    created_at: new Date(event.created_at * 1000).toISOString()
                });
            } catch (e) {
                // 解密失败，跳过
                console.log('解密失败:', e.message);
            }
        }
        
        // 按时间排序
        dms.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        
        return {
            success: true,
            dms: dms,
            message: `收到 ${dms.length} 条私信`
        };
    },
    
    // 发送私信并等待回复（模拟对话）
    clawlet_dm_converse: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const identity = getIdentity(userId);
        
        if (!identity) {
            return { success: false, message: '请先生成 Nostr 身份' };
        }
        
        const recipientName = params?.npub || params?.recipient || params?.nickname;
        const message = params?.message || params?.content || params?.text;
        
        if (!recipientName || !message) {
            return { success: false, message: '请提供收件人和私信内容' };
        }
        
        // 先发送私信
        const sendResult = await module.exports.clawlet_dm_send({
            npub: recipientName,
            content: message
        }, context);
        
        if (!sendResult.success) {
            return sendResult;
        }
        
        return {
            success: true,
            message: `已发送私信给 ${sendResult.displayName}，等待对方回复...`,
            note: '可以使用 clawlet_dm_receive 查看回复'
        };
    },
    
    // 添加昵称
    clawlet_nickname_add: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const identity = getIdentity(userId);
        
        if (!identity) {
            return { success: false, message: '请先生成 Nostr 身份' };
        }
        
        const nickname = params?.nickname || params?.name;
        const npub = params?.npub || params?.user_id;
        
        if (!nickname) {
            return { success: false, message: '请提供昵称' };
        }
        
        if (!npub) {
            return { success: false, message: '请提供 Nostr ID (npub)' };
        }
        
        const success = setNickname(userId, nickname, npub);
        
        return {
            success,
            nickname,
            npub,
            message: success 
                ? `已添加昵称：${nickname} → ${npub.slice(0, 20)}...` 
                : '添加失败，请检查 npub 是否正确'
        };
    },
    
    // 删除昵称
    clawlet_nickname_remove: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const nickname = params?.nickname || params?.name;
        
        if (!nickname) {
            return { success: false, message: '请提供要删除的昵称' };
        }
        
        const success = removeNickname(userId, nickname);
        
        return {
            success,
            message: success 
                ? `已删除昵称：${nickname}` 
                : `昵称 "${nickname}" 不存在`
        };
    },
    
    // 列出所有昵称
    clawlet_nickname_list: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const nicknames = getNicknames(userId);
        
        const list = Object.entries(nicknames).map(([name, data]) => ({
            nickname: name,
            npub: data.npub,
            createdAt: data.createdAt
        }));
        
        return {
            success: true,
            nicknames: list,
            message: list.length > 0 
                ? `你有 ${list.length} 个昵称` 
                : '还没有设置昵称，说"给某人添加昵称 xxx"来设置'
        };
    },
    
    // 查找昵称
    clawlet_nickname_get: async (params, context) => {
        const userId = context?.user?.id || 'default';
        const nickname = params?.nickname || params?.name;
        
        if (!nickname) {
            return { success: false, message: '请提供昵称' };
        }
        
        const nicknames = getNicknames(userId);
        const data = nicknames[nickname.toLowerCase()];
        
        if (!data) {
            return {
                success: false,
                message: `昵称 "${nickname}" 不存在`
            };
        }
        
        return {
            success: true,
            nickname: nickname,
            npub: data.npub,
            createdAt: data.createdAt
        };
    }
};
