/**
 * LLM 对话知识提取
 * 从 session-memory dump 中提取结构化知识条目
 * 产出为草稿文件，必须人工审阅后 import
 */
const fs = require('fs');
const path = require('path');

const DEFAULT_PROMPT = `你是一个知识提取助手。从以下对话中提取值得长期记住的知识。

只提取以下类型：
1. 业务规则/数据口径（用户说的算数标准、业务定义）
2. 人物角色（谁负责什么、组织关系）
3. 决策记录（选了什么方案、为什么选、放弃了什么）
4. 术语定义（专有名词解释）
5. 经验教训（踩过的坑、最佳实践）

每条知识用以下格式输出：
### [BOSS:领域] 标题
一句话核心要点。可补充关键细节，但不超过 3 行。
#tag1 #tag2

规则：
- 不要提取闲聊、寒暄、操作指令、调试日志
- 每条知识必须有明确的信息增量，不要提取显而易见的事实
- 标签用中文，2-4 个
- 没有值得提取的知识时只输出"无"
- 领域用简短中文词（如：数据、人事、架构、工具）

对话内容：
`;

/**
 * 构建 LLM API 请求
 */
function buildRequest(content, llmConfig) {
    const prompt = llmConfig.extractPrompt === 'default'
        ? DEFAULT_PROMPT
        : llmConfig.extractPrompt;

    return {
        model: llmConfig.model,
        messages: [
            { role: 'system', content: '你是知识提取专家，精通中文信息抽取。只输出符合格式要求的知识条目，不输出任何解释。' },
            { role: 'user', content: prompt + content },
        ],
        temperature: 0.3,
        max_tokens: 4096,
    };
}

/**
 * 调用 LLM 提取知识
 * @param {string} content - 对话文本内容
 * @param {object} llmConfig - config.ai.llm
 * @returns {Promise<string>} 提取结果文本
 */
async function callLLM(content, llmConfig) {
    const { endpoint, apiKey } = llmConfig;
    if (!apiKey) throw new Error('LLM API key 未配置');
    if (!endpoint) throw new Error('LLM endpoint 未配置');

    const body = buildRequest(content, llmConfig);

    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`,
        },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const errText = await response.text();
        throw new Error(`LLM API 错误 (${response.status}): ${errText}`);
    }

    const result = await response.json();
    return result.choices[0].message.content;
}

/**
 * 从文件或目录提取知识
 * @param {string} inputPath - session dump 文件或目录
 * @param {object} config
 * @param {object} options - { days?: number }
 * @returns {Promise<{draftPath: string, entryCount: number, files: string[]}>}
 */
async function extract(inputPath, config, options = {}) {
    const files = [];

    if (fs.statSync(inputPath).isDirectory()) {
        const cutoff = options.days
            ? new Date(Date.now() - options.days * 86400000).toISOString().slice(0, 10)
            : null;

        for (const f of fs.readdirSync(inputPath).sort()) {
            if (!f.endsWith('.md')) continue;
            if (cutoff) {
                const dateMatch = f.match(/(\d{4}-\d{2}-\d{2})/);
                if (dateMatch && dateMatch[1] < cutoff) continue;
            }
            files.push(path.join(inputPath, f));
        }
    } else {
        files.push(inputPath);
    }

    if (files.length === 0) {
        console.log('没有找到待提取的文件');
        return { draftPath: null, entryCount: 0, files: [] };
    }

    const outputDir = config._outputDirAbs;
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const dateStr = new Date().toISOString().slice(5, 10).replace('-', '');
    const draftPath = path.join(outputDir, `kb-draft-${dateStr}.md`);
    const draftLines = [`# 知识提取草稿 (${new Date().toISOString().slice(0, 10)})`, ''];
    let totalEntries = 0;

    for (const file of files) {
        console.log(`提取: ${path.basename(file)}`);
        const content = fs.readFileSync(file, 'utf-8');

        if (content.trim().length < 100) {
            console.log(`  跳过（内容过短）`);
            continue;
        }

        try {
            const extracted = await callLLM(content, config.ai.llm);
            if (extracted.trim() === '无') {
                console.log('  无可提取知识');
                continue;
            }

            draftLines.push(`<!-- 来源: ${path.basename(file)} -->`);
            draftLines.push(extracted);
            draftLines.push('');

            const entryCount = (extracted.match(/^### \[/gm) || []).length;
            totalEntries += entryCount;
            console.log(`  提取 ${entryCount} 条知识`);
        } catch (err) {
            console.error(`  提取失败: ${err.message}`);
        }
    }

    fs.writeFileSync(draftPath, draftLines.join('\n'), 'utf-8');
    console.log(`\n草稿已保存: ${draftPath}`);
    console.log(`共 ${totalEntries} 条待审阅条目`);
    console.log('审阅后运行: km import ' + draftPath);

    return { draftPath, entryCount: totalEntries, files };
}

module.exports = { extract, callLLM, DEFAULT_PROMPT };
