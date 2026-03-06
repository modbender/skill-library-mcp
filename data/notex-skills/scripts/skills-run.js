#!/usr/bin/env node
/**
 * NoteX Skills 通用测试脚本
 * 
 * 支持所有 7 种技能：slide / mindmap / report / flashcards / quiz / infographic / audio
 * 
 * 使用方式：
 *   node skills-run.js --skill <技能> --key <CWork Key> --title "标题" --content "内容"
 * 
 * 示例：
 *   node skills-run.js --skill mindmap --key YOUR_KEY --title "口腔AI趋势" --content "主要数据..."
 *   node skills-run.js --skill slide   --key YOUR_KEY --title "年度汇报"   --content "销售数据..."
 *   node skills-run.js --skill quiz    --key YOUR_KEY --title "护理测验"   --content "护理规范..."
 */

const https = require('https');
const http = require('http');

// ===================== 配置 =====================
const CONFIG = {
    cworkBaseUrl: 'https://cwork-web.mediportal.com.cn',
    cworkAppCode: 'cms_gpt',
    notexBaseUrl: 'https://notex.aishuo.co/noteX',
    authorizationKey: 'BP',              // 固定值，已验证可用
    pollIntervalMs: 60000,   // 每 60 秒轮询一次
    pollMaxTimes: 20,        // 最多 20 次（20 分钟上限）
};

// 各技能的预计生成时间（仅用于输出提示）
const SKILL_INFO = {
    slide: { name: '演示文稿（PPT）', estimatedTime: '3~5 分钟' },
    mindmap: { name: '思维导图', estimatedTime: '1~2 分钟' },
    report: { name: '分析报告', estimatedTime: '1~3 分钟' },
    flashcards: { name: '记忆卡片', estimatedTime: '1~2 分钟' },
    quiz: { name: '测验题目', estimatedTime: '1~2 分钟' },
    infographic: { name: '信息图', estimatedTime: '2~4 分钟' },
    audio: { name: '音频播客', estimatedTime: '3~6 分钟' },
};

const ALLOWED_SKILLS = Object.keys(SKILL_INFO);
// ================================================

function parseArgs() {
    const args = process.argv.slice(2);
    const result = {};
    for (let i = 0; i < args.length; i += 2) {
        result[args[i].replace(/^--/, '')] = args[i + 1];
    }
    return result;
}

function request(url, options = {}) {
    return new Promise((resolve, reject) => {
        const lib = url.startsWith('https') ? https : http;
        const req = lib.request(url, options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve({ status: res.statusCode, json: () => JSON.parse(data) });
                } catch (e) {
                    reject(new Error(`JSON 解析失败: ${data.substring(0, 200)}`));
                }
            });
        });
        req.on('error', reject);
        if (options.body) req.write(options.body);
        req.end();
    });
}

// Step 1: 用 CWork Key 换取 xgToken
async function getXgToken(cwKey) {
    console.log('\n[Step 1] 用 CWork Key 换取 xgToken...');
    const url = `${CONFIG.cworkBaseUrl}/user/login/appkey?appCode=${CONFIG.cworkAppCode}&appKey=${cwKey}`;
    const res = await request(url, { method: 'GET', headers: { 'Content-Type': 'application/json' } });
    const data = res.json();

    if (data.resultCode !== 1 || !data.data?.xgToken) {
        throw new Error(`获取 xgToken 失败: ${data.resultMsg || JSON.stringify(data)}`);
    }

    console.log(`✅ xgToken 获取成功`);
    console.log(`   userId:   ${data.data.userId}`);
    console.log(`   personId: ${data.data.personId}`);
    return data.data; // { xgToken, userId, personId }
}

// Step 2: 提交技能生成任务
async function createTask(userData, skill, title, content, require_text) {
    const info = SKILL_INFO[skill];
    console.log(`\n[Step 2] 提交「${info.name}」生成任务...`);

    const bizId = `skills_${skill}_${Date.now()}`;
    const body = JSON.stringify({
        title,
        bizId,
        bizType: 'TRILATERA_SKILLS',
        skills: [skill],
        require: require_text || `请根据提供的内容生成${info.name}，主题为：${title}`,
        sources: [{ id: 'src_001', title: `${title} - 素材`, content_text: content }]
    });

    const url = `${CONFIG.notexBaseUrl}/api/trilateral/autoTask`;
    const res = await request(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'authorization': CONFIG.authorizationKey,
            'personId': String(userData.personId),
            'x-user-id': userData.userId,
            'access-token': userData.xgToken,
        },
        body
    });
    const data = res.json();

    if (data.resultCode !== 1) {
        throw new Error(`创建任务失败: ${data.resultMsg}`);
    }

    const taskId = data.data.taskId?.[0];
    console.log(`✅ 任务创建成功`);
    console.log(`   taskId:     ${taskId}`);
    console.log(`   notebookId: ${data.data.noteBook_id}`);
    return taskId;
}

// Step 3: 轮询任务状态
async function pollTaskStatus(taskId, xgToken, skillName) {
    const interval = CONFIG.pollIntervalMs;
    const maxTimes = CONFIG.pollMaxTimes;
    console.log(`\n[Step 3] 轮询任务状态（每 ${interval / 1000}s，最多 ${maxTimes} 次 = ${maxTimes} 分钟上限）...`);

    const url = `${CONFIG.notexBaseUrl}/api/trilateral/taskStatus/${taskId}`;

    for (let i = 1; i <= maxTimes; i++) {
        // 第一次等 3 秒，后续等完整间隔
        await new Promise(r => setTimeout(r, i === 1 ? 3000 : interval));

        const res = await request(url, { method: 'GET' });
        const data = res.json();
        const { task_status, url: taskUrl } = data.data || {};

        console.log(`   第 ${i} 次轮询 → task_status: ${task_status}`);

        if (task_status === 'COMPLETED' && taskUrl) {
            const finalUrl = `${taskUrl}&token=${xgToken}`;
            console.log(`\n🎉 ${skillName}生成完成！`);
            console.log(`   查看链接：${finalUrl}`);
            return finalUrl;
        }

        if (task_status === 'FAILED') {
            throw new Error(`${skillName}生成失败，请检查输入内容后重试`);
        }
    }

    throw new Error(`轮询超时（超过 ${maxTimes} 分钟），请稍后通过 taskId 查询状态`);
}

// 主流程
async function main() {
    const args = parseArgs();

    // 参数校验
    if (!args.skill || !ALLOWED_SKILLS.includes(args.skill)) {
        console.error(`❌ 请指定有效的技能 --skill <技能>`);
        console.error(`   支持：${ALLOWED_SKILLS.join(' | ')}`);
        process.exit(1);
    }
    if (!args.key) {
        console.error('❌ 请提供 CWork Key：--key <your-key>');
        process.exit(1);
    }
    if (!args.title) {
        console.error('❌ 请提供标题：--title "标题"');
        process.exit(1);
    }
    if (!args.content) {
        console.error('❌ 请提供素材内容：--content "内容"');
        process.exit(1);
    }

    const info = SKILL_INFO[args.skill];
    console.log(`\n🚀 NoteX Skills — ${info.name}`);
    console.log(`   预计生成时间：${info.estimatedTime}`);
    console.log(`   标题：${args.title}`);

    try {
        const userData = await getXgToken(args.key);
        const taskId = await createTask(userData, args.skill, args.title, args.content, args.require);
        await pollTaskStatus(taskId, userData.xgToken, info.name);
    } catch (err) {
        console.error(`\n❌ 错误：${err.message}`);
        process.exit(1);
    }
}

main();
