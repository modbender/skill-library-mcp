/**
 * Variflight Aviation Skill - Main Entry
 * OpenClaw Skill for flight information query
 */

const { VariflightClient } = require('./lib/variflight-client');
const { loadConfig } = require('./lib/config-loader');

// 导出核心类供外部使用
module.exports = {
    VariflightClient,
    loadConfig,

    // 便捷方法：创建客户端实例
    createClient: (apiKey) => new VariflightClient(apiKey),

    // Skill 元数据
    metadata: {
        name: 'variflight-aviation',
        version: '1.0.0',
        description: '飞常准航班信息查询'
    }
};