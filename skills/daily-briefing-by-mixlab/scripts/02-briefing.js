#!/usr/bin/env node

/**
 * Daily Briefing 步骤 2：分类整理 + 推荐语生成 + 提交推荐语 + 上传简报
 * - 读取步骤 1 的 temp JSON，调用 MiniMax-M2.5 做分组与生成（agent loop）
 * - 按 cachedStoryId 提交推荐语：内联 PATCH mixdao API（Bearer MIXDAO_API_KEY）
 * - 保存 MD 后上传简报到 mixdao PATCH /api/briefing
 *
 * 用法: node scripts/02-briefing.js [--debug|-d] <filepath>
 */

import fs from 'fs';
import path from 'path';
import https from 'https';
import Anthropic from '@anthropic-ai/sdk';
import { jsonrepair } from 'jsonrepair';

let DEBUG = false;

function debugLog(...args) {
    if (DEBUG) console.error('[debug]', ...args);
}

const RECOMMENDATION_API_URL = 'https://www.mixdao.world/api/latest/recommendation';
const BRIEFING_API_URL = 'https://www.mixdao.world/api/briefing';
const MODEL = 'MiniMax-M2.5';
const MAX_GROUP_LOOP = 3;
const MAX_GROUPS = 5;
const MIN_ITEMS_PER_GROUP = 3;
const GROUPING_MAX_TOKENS = 8192; // 分组 JSON 较长时避免截断导致缺 id
const RECOMMENDATION_MAX_TOKENS = 16384; // 推荐语/摘要 JSON 较长，提高上限减少截断
const MIN_ITEMS_WHEN_SMALL = 2;   // 条数较少时每组最少条数
const SMALL_LIST_THRESHOLD = 12;   // 低于此条数时使用 MIN_ITEMS_WHEN_SMALL
const ITEM_TEXT_PREVIEW_LEN = 280; // 分组时传入的条目正文长度
const GROUP_NAME_MAX_LEN = 10;     // 组名建议字数

/**
 * 通用 mixdao PATCH 请求（推荐语、简报等复用）
 */
function patchMixdao(urlString, bodyObj) {
    return new Promise((resolve, reject) => {
        const apiKey = process.env.MIXDAO_API_KEY;
        if (!apiKey) {
            reject(new Error('MIXDAO_API_KEY is not set.'));
            return;
        }
        const url = new URL(urlString);
        const body = JSON.stringify(bodyObj);
        const opts = {
            hostname: url.hostname,
            path: url.pathname + url.search,
            method: 'PATCH',
            headers: {
                Authorization: `Bearer ${apiKey}`,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body, 'utf8'),
            },
        };
        const req = https.request(opts, (res) => {
            res.setTimeout(15000, () => {
                req.destroy();
                reject(new Error('API 请求超时'));
            });
            const chunks = [];
            res.on('data', (c) => chunks.push(c));
            res.on('end', () => {
                const responseBody = Buffer.concat(chunks).toString('utf8');
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    resolve(responseBody);
                } else {
                    reject(
                        new Error(
                            `API returned ${res.statusCode}: ${responseBody.slice(0, 300)}`
                        )
                    );
                }
            });
        });
        req.on('error', reject);
        req.write(body, 'utf8');
        req.end();
    });
}

/** 批量提交推荐语到 mixdao（PATCH body: { items: [{ cachedStoryId, recommendationText }, ...] }） */
function batchUpdateRecommendations(items) {
    if (!items.length) return Promise.resolve({ ok: true, results: [] });
    return patchMixdao(RECOMMENDATION_API_URL, { items })
        .then((responseBody) => {
            const data = JSON.parse(responseBody || '{}');
            debugLog('PATCH batch ok', data.results?.length, data.results?.slice(0, 2));
            return data;
        });
}

/** 上传每日简报到 mixdao PATCH /api/briefing */
function updateBriefing(date, title, content) {
    return patchMixdao(BRIEFING_API_URL, { date, title, content })
        .then((responseBody) => {
            debugLog('简报已上传', date, responseBody && responseBody.slice(0, 80));
            return responseBody;
        });
}

function getClient() {
    const baseURL = process.env.ANTHROPIC_BASE_URL;
    const apiKey = process.env.ANTHROPIC_API_KEY;
    if (!apiKey) throw new Error('ANTHROPIC_API_KEY is not set.');
    return new Anthropic({
        baseURL: baseURL || 'https://api.minimaxi.com/anthropic',
        apiKey,
    });
}

/** 从模型返回的 content 中取出完整文本（忽略 thinking 块） */
function getTextFromContent(content) {
    if (!Array.isArray(content)) return '';
    let text = '';
    for (const block of content) {
        if (block.type === 'text' && block.text) text += block.text;
    }
    return text.trim();
}

/** 从字符串中解析 JSON，允许被 ```json ... ``` 包裹；截断或损坏时用 jsonrepair 兜底 */
function parseJSON(text) {
    const stripped = text.replace(/^[\s\S]*?```(?:json)?\s*([\s\S]*?)```[\s\S]*$/i, '$1').trim() || text.trim();
    try {
        return JSON.parse(stripped);
    } catch (e) {
        try {
            const repaired = jsonrepair(stripped);
            const out = JSON.parse(repaired);
            debugLog('parseJSON 使用 jsonrepair 修复后解析成功');
            return out;
        } catch (e2) {
            throw e;
        }
    }
}

/**
 * 根据总条数计算分组约束（条数少时放宽每组最少条数、并限制最大组数使约束可满足）
 */
function computeGroupConstraints(total) {
    const minPer = total < SMALL_LIST_THRESHOLD ? MIN_ITEMS_WHEN_SMALL : MIN_ITEMS_PER_GROUP;
    const maxGroups = Math.min(MAX_GROUPS, Math.max(1, Math.floor(total / minPer)));
    return { maxGroups, minItemsPerGroup: minPer };
}

/**
 * 校验分组结果：非空、无重复、组数/每组条数满足约束。允许部分 id 未出现在任何组（只处理已分组的条目）。
 * @param {Array} groups - 分组数组
 * @param {{ expectedIds: Set<string>, maxGroups: number, minItemsPerGroup: number }} opts
 * @returns {{ ok: boolean, msg: string, duplicateId?: string }}
 */
function validateGroups(groups, opts = {}) {
    if (!Array.isArray(groups) || groups.length === 0) return { ok: false, msg: '分组结果必须是非空数组' };
    const expectedIds = opts.expectedIds;
    const maxGroups = opts.maxGroups != null ? opts.maxGroups : MAX_GROUPS;
    const minItemsPerGroup = opts.minItemsPerGroup != null ? opts.minItemsPerGroup : MIN_ITEMS_PER_GROUP;
    if (expectedIds && expectedIds.size > 0) {
        const seen = new Set();
        for (const g of groups) {
            const itemIds = (g.items || g.itemIds || []).map((it) => (typeof it === 'string' ? it : it.id));
            if (itemIds.length < minItemsPerGroup) return { ok: false, msg: `组「${g.name || '(未命名)'}」仅 ${itemIds.length} 条，至少需要 ${minItemsPerGroup} 条` };
            for (const id of itemIds) {
                if (!expectedIds.has(id)) return { ok: false, msg: `未知条目 id: ${id}` };
                if (seen.has(id)) return { ok: false, msg: `条目 id 重复: ${id}`, duplicateId: id };
                seen.add(id);
            }
        }
        // 允许 id 缺失：未分组的条目后续不生成推荐语、不写入 Markdown
    }
    if (groups.length > maxGroups) return { ok: false, msg: `共 ${groups.length} 组，超过上限 ${maxGroups} 组` };
    return { ok: true };
}

async function callMiniMax(client, system, userText, options = {}) {
    const { max_tokens = 4096, enableThinking = false } = typeof options === 'number' ? { max_tokens: options } : options;
    const params = {
        model: MODEL,
        max_tokens,
        system,
        messages: [{ role: 'user', content: userText }],
    };
    if (enableThinking) {
        params.thinking = { type: 'enabled', budget_tokens: 2048 };
    }
    debugLog('callMiniMax', { max_tokens: params.max_tokens, enableThinking: !!params.thinking, promptLen: userText.length });
    const message = await client.messages.create(params);
    const text = getTextFromContent(message.content);
    debugLog('callMiniMax response', { textLen: text.length, preview: text.slice(0, 120) });
    return text;
}

async function runGroupingLoop(client, items) {
    const expectedIds = new Set(items.map((it) => it.id));
    const { maxGroups, minItemsPerGroup } = computeGroupConstraints(items.length);
    const itemList = items.map((it) => ({
        id: it.id,
        title: (it.translatedTitle || it.title || '').slice(0, 80),
        text: (it.text || '').slice(0, ITEM_TEXT_PREVIEW_LEN),
    }));
    const system = `你是一个内容分类助手，面向创业者场景。请将用户提供的条目按「创业者会关心的主题/需求」分组（如：冷启动获客、技术选型、融资与节奏、团队与招人、行业与趋势等）。组名需简短可读、概括该需求，${GROUP_NAME_MAX_LEN} 字以内。严格满足：至多 ${maxGroups} 组，每组至少 ${minItemsPerGroup} 条。尽量将更多条目分入组；若难以全部覆盖可只分部分条目，每条最多出现在一个组中，不能重复。只输出一个 JSON，不要其他解释。`;
    let userPrompt = `请对以下条目按创业者关心的主题/需求分组，输出唯一一个 JSON，格式：{"groups":[{"name":"组名（${GROUP_NAME_MAX_LEN}字内）","items":[{"id":"条目id"}]}]}。共 ${items.length} 条，请尽量全部分组；若输出长度受限可只分部分，每条最多出现一次。\n\n条目列表：\n${JSON.stringify(itemList, null, 2)}`;

    for (let attempt = 0; attempt < MAX_GROUP_LOOP; attempt++) {
        debugLog('分组 attempt', attempt + 1, '/', MAX_GROUP_LOOP, 'maxGroups=', maxGroups, 'minPer=', minItemsPerGroup, 'promptLen=', userPrompt.length);
        const raw = await callMiniMax(client, system, userPrompt, { max_tokens: GROUPING_MAX_TOKENS, enableThinking: attempt === 0 });
        let data;
        try {
            data = parseJSON(raw);
        } catch (e) {
            debugLog('分组 parseJSON 失败', e.message, 'rawPreview=', raw.slice(0, 200));
            if (attempt < MAX_GROUP_LOOP - 1) {
                userPrompt += '\n\n你上次的回复不是合法 JSON，请重新只输出一个 JSON。';
                continue;
            }
            throw new Error('分组结果解析失败: ' + e.message);
        }
        const groups = data.groups || data;
        const validation = validateGroups(groups, { expectedIds, maxGroups, minItemsPerGroup });
        debugLog('分组 校验', validation.ok ? '通过' : validation.msg, 'groups.length=', groups && groups.length);
        if (validation.ok) {
            const seenIds = new Set();
            for (const g of groups) {
                for (const it of g.items || g.itemIds || []) {
                    const id = typeof it === 'string' ? it : it.id;
                    if (id) seenIds.add(id);
                }
            }
            const missingCount = expectedIds.size - seenIds.size;
            if (missingCount > 0) debugLog('未分组条数', missingCount, '（仅对已分组条目生成推荐语）');
            debugLog('分组 结果', groups.map((g) => ({ name: g.name || g.groupName, count: (g.items || g.itemIds || []).length })));
            return groups;
        }
        if (attempt < MAX_GROUP_LOOP - 1) {
            if (validation.duplicateId) {
                userPrompt += `\n\n约束未满足：${validation.msg}。请确保 id 「${validation.duplicateId}」只出现在一个组中，重新输出完整 JSON。`;
            } else {
                userPrompt += `\n\n约束未满足：${validation.msg}。请重新分组并只输出一个 JSON。`;
            }
        } else {
            throw new Error('分组约束在最大重试次数内未满足: ' + validation.msg);
        }
    }
    throw new Error('分组 loop 异常结束');
}

/** 将分组结构转为 id -> item 的 Map，便于按 id 取回条目信息 */
function buildIdMap(items) {
    const map = new Map();
    for (const it of items) map.set(it.id, it);
    return map;
}

/** 根据分组结果（每组只有 id 列表）填充完整 item，返回 groups: [ { name, groupSummary?, items: [ item ] } ] */
function fillGroupsWithItems(groups, idMap) {
    return groups.map((g) => {
        const itemIds = (g.items || g.itemIds || []).map((it) => (typeof it === 'string' ? it : it.id));
        const items = itemIds.map((id) => idMap.get(id)).filter(Boolean);
        return {
            name: g.name || g.groupName || '',
            items,
        };
    });
}

async function generateSummariesAndRecommendations(client, filledGroups) {
    const system = `你是面向创业者的内容点评助手。

分组摘要（groupSummary）：100字内。用一两句话概括本组内容共同对应的创业者需求或关注点（如：早期获客、技术选型、融资节奏）。只输出一个 JSON，不要其他解释。

推荐语（recommendationText）：每条 140 字以内，站在创业者角度；具体、可操作，禁止「提升效率」「值得关注」等空泛表述。根据内容类型选择侧重，不必每类都写满四段：
- 论文/研究：提炼最核心的 1～2 条结论或关键数据，点明对创业者/决策的启示，不写方法细节。
- 产品：写清目标用户与典型场景、解决的具体问题、可感知的价值（效率/成本/体验），不堆砌功能。
- 技术：突出技术如何更优、解决了什么具体问题、与常见方案的差异或适用边界。示例（技术/AI）：如「Claude计算机使用能力16个月提升5倍」——从介绍文章中提炼「时间+能力/指标提升」，信息密度高、可量化，对创业者判断技术成熟度很有价值。
- 融资/投资：提炼金额、轮次、估值或条款亮点及投资人逻辑，点明对同类创业者的参考（节奏、叙事）。
- 公司/案例：概括关键决策与结果，提炼可复用的打法或可避的坑，让读者能对标自身阶段。
- 政策/监管：写清新规要点、谁受影响、关键时间节点，以及合规要点或潜在机会。
- 市场/行业报告：提炼 1～2 个关键数据或结论、重要细分与驱动因素，点明对选赛道、定战略的启示。
- 工具/方法论：说明能做什么、适用场景、与常见方案的取舍，可简要提上手成本或适用阶段。
- 人物/观点：提炼核心论点与 1～2 条可执行建议，点明最适合哪类角色（如早期创始人、增长负责人）。
- 竞品/对比：概括差异点与优劣势，点明在什么情境下选哪种方案更合适。
- 招聘/团队：提炼岗位需求信号、薪酬或级别参考，以及招人、留人或组织上的可借鉴点。
- 失败/复盘：概括失败主因与可避免的坑，提炼可迁移到其他项目或阶段的教训。
- 活动/会议：说明主题与核心信息、适合谁参加、能获得什么（洞察/资源/人脉）。
- 设计：提炼设计原则或视觉/交互要点、适用场景（如品牌、产品、运营），点明可借鉴的决策或可直接复用的思路，适合做产品/品牌/UX 的创始人或设计负责人。
- 其他或跨类型：按「谁会用 + 具体收获/避坑」写，不强行凑齐多段；若与创业关联弱，只写场景与价值。`;

    const payload = filledGroups.map((g) => ({
        name: g.name,
        items: g.items.map((it) => ({
            id: it.id,
            title: it.translatedTitle || it.title,
            text: (it.text || '').slice(0, 300),
        })),
    }));
    const userPrompt = `请为以下分组生成 groupSummary（100字内）和每条条目的 recommendationText（140字内）。推荐语请根据每条内容类型（论文/产品/技术/融资/案例/政策/市场/工具/观点/竞品/招聘/失败复盘/活动/设计/其他）选择对应侧重，避免空话，确保每条都有 id 和 recommendationText（纯文本、无换行）。\n只输出一个 JSON，格式：{"groups":[{"groupSummary":"...","items":[{"id":"...","recommendationText":"..."}]}]}\n\n分组与条目：\n${JSON.stringify(payload, null, 2)}`;

    debugLog('生成摘要/推荐语 promptLen=', userPrompt.length);
    const raw = await callMiniMax(client, system, userPrompt, { max_tokens: RECOMMENDATION_MAX_TOKENS, enableThinking: false });
    let data;
    try {
        data = parseJSON(raw);
    } catch (e) {
        debugLog('推荐语 parseJSON 失败', e.message, 'rawPreview=', raw.slice(0, 300));
        throw new Error('推荐语/摘要结果解析失败: ' + e.message);
    }
    const groups = data.groups || data;
    const flat = [];
    const groupsWithSummaries = groups.map((g, i) => {
        const items = (g.items || []).map((it) => ({
            id: it.id,
            recommendationText: (it.recommendationText || it.recommendation || '').trim(),
        })).filter((it) => it.id && it.recommendationText);
        for (const it of items) flat.push({
            id: it.id,
            title: filledGroups[i]?.items?.find((x) => x.id === it.id)?.translatedTitle || filledGroups[i]?.items?.find((x) => x.id === it.id)?.title,
            recommendationText: it.recommendationText,
        });
        return {
            name: filledGroups[i]?.name ?? g.name ?? '',
            groupSummary: (g.groupSummary || '').trim(),
            items,
        };
    });
    debugLog('推荐语 条数', flat.length, 'sample', flat[0]);
    return { toSubmit: flat, groupsWithSummaries };
}

async function main() {
    const args = process.argv.slice(2);
    const hasDebug = args.includes('--debug') || args.includes('-d');
    const filepath = args.filter((a) => a !== '--debug' && a !== '-d')[0];
    if (!filepath) {
        console.error('用法: node scripts/02-briefing.js [--debug|-d] <filepath>');
        console.error('示例: node scripts/02-briefing.js ./temp/briefing-2026-02-14.json');
        process.exit(1);
    }
    DEBUG = !!hasDebug;
    if (DEBUG) debugLog('debug 已开启', 'filepath=', filepath);
    if (!fs.existsSync(filepath)) {
        console.error('错误: 找不到文件', filepath);
        process.exit(1);
    }

    let data;
    try {
        data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
    } catch (e) {
        console.error('错误: 无法读取或解析 JSON', e.message);
        process.exit(1);
    }
    const date = data?.date;
    const items = data?.items;
    if (typeof date !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(date)) {
        console.error('错误: 文件内容应为 { date, items }，且 date 为 YYYY-MM-DD（01-fetch 输出格式）');
        process.exit(1);
    }
    if (!Array.isArray(items) || !items.length) {
        console.error('错误: 文件内容应为 { date, items }，且 items 为非空数组（01-fetch 输出格式）');
        process.exit(1);
    }
    debugLog('加载文件', 'date=', date, 'items=', items.length);

    const client = getClient();
    debugLog(`步骤 1/3: 分组（至多 ${MAX_GROUPS} 组，每组至少 ${MIN_ITEMS_PER_GROUP} 条）…`);
    const groups = await runGroupingLoop(client, items);
    const idMap = buildIdMap(items);
    const filledGroups = fillGroupsWithItems(groups, idMap);
    debugLog('filledGroups', filledGroups.map((g) => ({ name: g.name, items: g.items.length })));
    debugLog(`步骤 2/3: 生成${filledGroups.length}组摘要与每条推荐语…`);
    const { toSubmit, groupsWithSummaries } = await generateSummariesAndRecommendations(client, filledGroups);
    debugLog(`步骤 3/3: 提交推荐语（共 ${toSubmit.length} 条）…`);

    const mdPath = path.join(path.dirname(filepath), path.basename(filepath, '.json') + '.md');
    const mdLines = [`# Daily Briefing - ${date}`, ''];
    for (const g of groupsWithSummaries) {
        mdLines.push(`## ${g.name}`, '');
        if (g.groupSummary) mdLines.push(g.groupSummary, '');
        for (const it of g.items) {
            const item = idMap.get(it.id);
            const title = item ? (item.translatedTitle || item.title || '') : '';
            const url = item?.url || '';
            mdLines.push(url ? `### [${title}](${url})` : `### ${title}`);
            mdLines.push(`- **推荐语:** ${it.recommendationText}`, '');
        }
    }
    const mdContent = mdLines.join('\n');
    fs.writeFileSync(mdPath, mdContent, 'utf8');

    try {
        await updateBriefing(date, '每日简报', mdContent);
    } catch (e) {
        console.error('上传简报失败:', e.message);
        process.exit(1);
    }

    const batchBody = toSubmit.map(({ id, recommendationText }) => ({
        cachedStoryId: id,
        recommendationText,
    }));
    let ok = 0;
    let fail = 0;
    let results = [];
    try {
        const res = await batchUpdateRecommendations(batchBody);
        results = res.results || [];
    } catch (e) {
        console.error('批量提交推荐语失败:', e.message);
        process.exit(1);
    }
    const resultByCachedId = new Map(
        results.map((r) => [r.cachedStoryId, r])
    );
    for (const { id, recommendationText } of toSubmit) {
        const r = resultByCachedId.get(id);
        if (r?.ok) {
            ok++;
            debugLog('提交 ok', id);
        } else {
            fail++;
            console.error('提交失败 id=%s: %s', id, r?.error || 'unknown');
        }
        const item = idMap.get(id);
        const title = item ? (item.translatedTitle || item.title || '') : '';
        const url = item ?.url || '';
        console.log(
            [
                '',
                url ? `### [${title}](${url})` : `### ${title}`,
                `- **ID:** ${id}`,
                `- **推荐语:** ${recommendationText}`,
                '',
            ].join('\n')
        );
    }
    debugLog('完成。成功 %d，失败 %d', ok, fail);
    if (fail > 0) process.exit(1);
    console.log('Markdown 已写入:', path.resolve(mdPath));
}

main().catch((err) => {
    console.error(err.message);
    process.exit(1);
});