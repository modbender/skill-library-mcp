/**
 * 中文同义词表
 * 将变体/缩写统一到规范术语，提升标签一致性和检索命中率
 */

const DEFAULT_SYNONYMS = {
    '数据库': ['DB', 'db', 'database', 'Database', 'mysql', 'MySQL', 'postgres', 'PostgreSQL', 'sqlite', 'SQLite'],
    '数仓': ['数据仓库', 'data warehouse', 'DW', 'dw', 'data-warehouse'],
    '大模型': ['LLM', 'llm', 'model', '语言模型', '大语言模型', 'large language model'],
    '飞书': ['feishu', 'Feishu', 'lark', 'Lark'],
    '报表': ['report', 'Report', '数据报表', '日报', '周报', '月报'],
    '自动化': ['automation', 'Automation', 'cron', 'crontab', '定时任务', '自动'],
    'Python': ['python', 'py', 'PY'],
    'API': ['api', 'Api', '接口', '服务接口'],
    '服务器': ['server', 'Server', '机器', '主机', 'host'],
    '容器': ['docker', 'Docker', 'container', 'Container', 'k8s', 'kubernetes'],
    '前端': ['frontend', 'Frontend', 'front-end', 'React', 'react', 'Vue', 'vue'],
    '后端': ['backend', 'Backend', 'back-end', '服务端'],
    '部署': ['deploy', 'Deploy', 'deployment', '发布', '上线'],
    '监控': ['monitor', 'Monitor', 'monitoring', '告警', 'alert'],
    '缓存': ['cache', 'Cache', 'Redis', 'redis', 'Memcached'],
    '消息队列': ['MQ', 'mq', 'Kafka', 'kafka', 'RabbitMQ', 'rabbitmq'],
    '数据治理': ['data governance', '数据质量', '数据标准', 'data quality'],
    'ETL': ['etl', '数据集成', '数据同步', 'data pipeline', '数据管道'],
    '指标': ['metric', 'Metric', 'KPI', 'kpi', '度量'],
    '维度': ['dimension', 'Dimension', '维度表'],
};

let _defaultReverseMap = null;

/**
 * 构建反向映射：变体 → 规范术语
 */
function buildReverseMap(synonyms) {
    const map = new Map();
    for (const [canonical, variants] of Object.entries(synonyms)) {
        map.set(canonical.toLowerCase(), canonical);
        for (const v of variants) {
            map.set(v.toLowerCase(), canonical);
        }
    }
    return map;
}

/**
 * 将文本中的术语统一为规范形式
 * @param {string} term - 待归一化的术语
 * @param {object} [customSynonyms] - 自定义同义词表（覆盖默认）
 * @returns {string} 归一化后的术语
 */
function normalize(term, customSynonyms) {
    if (customSynonyms) {
        const customMap = buildReverseMap(customSynonyms);
        return customMap.get(term.toLowerCase()) || term;
    }
    if (!_defaultReverseMap) {
        _defaultReverseMap = buildReverseMap(DEFAULT_SYNONYMS);
    }
    return _defaultReverseMap.get(term.toLowerCase()) || term;
}

/**
 * 批量归一化标签列表
 * @param {string[]} tags
 * @param {object} [customSynonyms]
 * @returns {string[]} 去重后的归一化标签
 */
function normalizeTags(tags, customSynonyms) {
    const seen = new Set();
    const result = [];
    for (const tag of tags) {
        const normalized = normalize(tag, customSynonyms);
        if (!seen.has(normalized)) {
            seen.add(normalized);
            result.push(normalized);
        }
    }
    return result;
}

/**
 * 加载自定义同义词表（JSON 文件或 "default"）
 */
function loadSynonyms(synonymsConfig) {
    if (!synonymsConfig || synonymsConfig === 'default') {
        return DEFAULT_SYNONYMS;
    }
    try {
        const fs = require('fs');
        const raw = fs.readFileSync(synonymsConfig, 'utf-8');
        return { ...DEFAULT_SYNONYMS, ...JSON.parse(raw) };
    } catch {
        return DEFAULT_SYNONYMS;
    }
}

module.exports = { DEFAULT_SYNONYMS, normalize, normalizeTags, loadSynonyms };
