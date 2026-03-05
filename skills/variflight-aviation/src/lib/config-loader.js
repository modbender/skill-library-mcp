const fs = require('fs');
const path = require('path');

/**
 * 加载配置
 * 优先级：环境变量 > config.local.json > config.json
 */
function loadConfig() {
    const configDir = path.join(__dirname, '../..');

    // 加载默认配置
    const defaultConfigPath = path.join(configDir, 'config.json');
    let config = {};

    if (fs.existsSync(defaultConfigPath)) {
        config = JSON.parse(fs.readFileSync(defaultConfigPath, 'utf8'));
    }

    // 加载本地配置（覆盖默认配置）
    const localConfigPath = path.join(configDir, 'config.local.json');
    if (fs.existsSync(localConfigPath)) {
        const localConfig = JSON.parse(fs.readFileSync(localConfigPath, 'utf8'));
        config = { ...config, ...localConfig };
    }

    // 环境变量优先级最高
    // 支持两种变量名：X_VARIFLIGHT_KEY (官方) 或 VARIFLIGHT_API_KEY (兼容)
    if (process.env.X_VARIFLIGHT_KEY) {
        config.apiKey = process.env.X_VARIFLIGHT_KEY;
    } else if (process.env.VARIFLIGHT_API_KEY) {
        config.apiKey = process.env.VARIFLIGHT_API_KEY;
    }

    // 其他环境变量覆盖
    if (process.env.VARIFLIGHT_TIMEOUT) {
        config.timeout = parseInt(process.env.VARIFLIGHT_TIMEOUT, 10);
    }

    if (process.env.VARIFLIGHT_LOG_LEVEL) {
        config.logLevel = process.env.VARIFLIGHT_LOG_LEVEL;
    }

    return config;
}

/**
 * 验证配置
 */
function validateConfig(config) {
    if (!config.apiKey) {
        throw new Error(
            'API Key not configured.\n' +
            'Please set environment variable:\n' +
            '  export X_VARIFLIGHT_KEY="your_api_key"\n' +
            'Or:\n' +
            '  export VARIFLIGHT_API_KEY="your_api_key"\n' +
            'Or create config.local.json: {"apiKey": "your_api_key"}'
        );
    }

    return true;
}

module.exports = {
    loadConfig,
    validateConfig
};