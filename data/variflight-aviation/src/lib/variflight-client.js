const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');
const { loadConfig, validateConfig } = require('./config-loader');

class VariflightClient {
  constructor(apiKey) {
    const config = loadConfig();
    validateConfig(config);

    this.apiKey = apiKey || config.apiKey;
    this.timeout = config.timeout || 30000;
    this.client = null;
    this.transport = null;
    this.isConnected = false;
  }

  /**
   * 建立连接
   */
  async connect() {
    if (this.isConnected) return;

    // 创建传输层 - 使用正确的环境变量名 X_VARIFLIGHT_KEY
    this.transport = new StdioClientTransport({
      command: '/Users/lixiao/.nvm/versions/node/v22.14.0/bin/npx',
      args: ['-y', '@variflight-ai/variflight-mcp'],
      env: {
        X_VARIFLIGHT_KEY: this.apiKey,
        PATH: '/Users/lixiao/.nvm/versions/node/v22.14.0/bin:/usr/local/bin:/usr/bin:/bin'
      }
    });

    this.client = new Client({
      name: 'variflight-openclaw-skill',
      version: '1.0.0'
    });

    await this.client.connect(this.transport);
    this.isConnected = true;
  }

  /**
   * 断开连接
   */
  async disconnect() {
    if (this.client) {
      try {
        await this.client.close();
      } catch (e) { }
      this.client = null;
    }
    if (this.transport) {
      try {
        await this.transport.close();
      } catch (e) { }
      this.transport = null;
    }
    this.isConnected = false;
  }

  /**
   * 解析工具调用结果
   * 处理 Variflight 的各种返回格式
   */
  parseResult(result) {
    if (!result) return null;

    // 如果已经是对象/数组，直接返回
    if (typeof result !== 'string') {
      return result;
    }

    // 尝试解析 JSON
    try {
      return JSON.parse(result);
    } catch (e) {
      // 不是 JSON，返回原始字符串
      return result;
    }
  }

  /**
   * 调用工具
   */
  async callTool(name, args) {
    await this.connect();

    try {
      const result = await this.client.callTool({
        name: name,
        arguments: args
      });

      // 解析 content
      if (result && result.content && Array.isArray(result.content)) {
        const textContent = result.content.find(c => c.type === 'text');
        if (textContent && textContent.text) {
          return this.parseResult(textContent.text);
        }
      }

      return result;
    } catch (error) {
      throw error;
    }
  }

  // ===== 业务方法 =====

  async searchFlightsByDepArr(dep, arr, date) {
    return this.callTool('searchFlightsByDepArr', { dep, arr, date });
  }

  async searchFlightsByNumber(fnum, date) {
    return this.callTool('searchFlightsByNumber', { fnum, date });
  }

  async getTransferInfo(depcity, arrcity, date) {
    return this.callTool('getFlightTransferInfo', { depcity, arrcity, depdate: date });
  }

  async getFlightHappinessIndex(fnum, date) {
    return this.callTool('flightHappinessIndex', { fnum, date });
  }

  async trackAircraft(anum) {
    return this.callTool('getRealtimeLocationByAnum', { anum });
  }

  async getAirportWeather(airport) {
    return this.callTool('getFutureWeatherByAirport', { airport });
  }

  async searchItineraries(dep, arr, date) {
    return this.callTool('searchFlightItineraries', {
      depCityCode: dep,
      arrCityCode: arr,
      depDate: date
    });
  }

  /**
   * 列出可用工具（调试用）
   */
  async listTools() {
    await this.connect();
    try {
      const tools = await this.client.listTools();
      return tools;
    } catch (e) {
      console.error('Failed to list tools:', e.message);
      return [];
    }
  }
}

module.exports = { VariflightClient };