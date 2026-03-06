/**
 * PREFIX → kb/ 目录映射分类器
 * 纯确定性，零 LLM 成本
 */
const path = require('path');

function sanitizeName(name) {
    return name
        .toLowerCase()
        .replace(/\s+/g, '-')
        .replace(/[^\w\u4e00-\u9fff-]/g, '');
}

/**
 * 根据 PREFIX 和 name 确定目标 kb/ 文件路径
 * @param {{prefix:string, name:string}} entry
 * @param {object} config - 包含 prefixMap 和 _kbDirAbs
 * @returns {string} 目标文件的绝对路径
 */
function classify(entry, config) {
    const { prefixMap, _kbDirAbs } = config;
    const template = prefixMap[entry.prefix];

    if (!template) {
        return path.join(_kbDirAbs, 'uncategorized.md');
    }

    const safeName = sanitizeName(entry.name);
    const relativePath = template.replace(/\{name\}/g, safeName);
    return path.join(_kbDirAbs, relativePath);
}

/**
 * 获取所有已配置的 PREFIX 列表
 * @param {object} config
 * @returns {string[]}
 */
function getKnownPrefixes(config) {
    return Object.keys(config.prefixMap);
}

module.exports = { classify, sanitizeName, getKnownPrefixes };
