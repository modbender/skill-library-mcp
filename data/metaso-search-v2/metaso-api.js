// Metaso 搜索 API 模块 - 直接 HTTP API 访问

// 支持的模型和搜索范围
const SUPPORTED_MODELS = ['fast', 'fast_thinking', 'ds-r1'];
const SUPPORTED_SCOPES = ['webpage', 'document', 'paper', 'image', 'video', 'podcast'];

// Metaso API 基础类
class MetasoAPI {
  constructor() {
    // 必须从环境变量获取 API 密钥
    this.apiKey = process.env.METASO_API_KEY;
    
    if (!this.apiKey) {
      throw new Error('METASO_API_KEY 环境变量未设置，请在使用前配置');
    }
    
    this.searchUrl = 'https://metaso.cn/api/v1/search';
    this.readerUrl = 'https://metaso.cn/api/v1/reader';
    this.chatUrl = 'https://metaso.cn/api/v1/chat/completions';
  }

  // 通用请求方法
  async _request(url, options = {}) {
    const defaultOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      ...options
    };

    try {
      const response = await fetch(url, defaultOptions);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP Error ${response.status}: ${response.statusText} - ${errorText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`请求失败 [${url}]:`, error.message);
      throw error;
    }
  }

  // 网页搜索 - 使用正确的搜索 URL
  async search(q, size, scope, includeSummary, includeRawContent, conciseSnippet) {
    // 验证参数
    if (!q || typeof q !== 'string') {
      throw new Error('搜索关键词 (q) 必须是有效的字符串');
    }
    if (typeof size !== 'number' || size < 1 || size > 100) {
      throw new Error('搜索结果数量 (size) 必须是 1-100 之间的整数');
    }
    if (!SUPPORTED_SCOPES.includes(scope)) {
      throw new Error(`不支持的搜索范围 (scope): ${scope}。支持的范围: ${SUPPORTED_SCOPES.join(', ')}`);
    }
    if (typeof includeSummary !== 'boolean') {
      throw new Error('是否包含精简的原文匹配信息 (includeSummary) 必须是布尔值');
    }
    if (typeof includeRawContent !== 'boolean') {
      throw new Error('是否通过网页的摘要信息进行召回增强 (includeRawContent) 必须是布尔值');
    }
    if (typeof conciseSnippet !== 'boolean') {
      throw new Error('是否抓取所有来源网页原文 (conciseSnippet) 必须是布尔值');
    }

    const body = {
      q: q,
      size: size,
      scope: scope,
      includeSummary: includeSummary,
      includeRawContent: includeRawContent,
      conciseSnippet: conciseSnippet
    };

    return this._request(this.searchUrl, {
      body: JSON.stringify(body)
    });
  }

  // 网页内容读取 - 使用正确的阅读器 URL
  async readWebPage(url, format) {
    // 验证参数
    if (!url || typeof url !== 'string') {
      throw new Error('URL 地址 (url) 必须是有效的字符串');
    }
    if (!['json', 'markdown'].includes(format)) {
      throw new Error(`不支持的输出格式 (format): ${format}。支持的格式: json, markdown`);
    }

    const headers = {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json'
    };

    // 根据格式设置 Accept 头部
    if (format === 'json') {
      headers['Accept'] = 'application/json';
    } else if (format === 'markdown') {
      headers['Accept'] = 'text/plain';
    }

    const body = {
      url: url
    };

    try {
      const response = await fetch(this.readerUrl, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(body)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP Error ${response.status}: ${response.statusText} - ${errorText}`);
      }

      // 根据格式解析响应
      if (format === 'json') {
        return await response.json();
      } else {
        return {
          title: url,
          url: url,
          content: await response.text()
        };
      }
    } catch (error) {
      console.error(`网页读取失败 [${url}]:`, error.message);
      throw error;
    }
  }

  // 智能问答 - 使用正确的聊天 URL
  async chat(messages, model, scope, format, stream, conciseSnippet) {
    // 验证参数
    if (!SUPPORTED_MODELS.includes(model)) {
      throw new Error(`不支持的模型 (model): ${model}。支持的模型: ${SUPPORTED_MODELS.join(', ')}`);
    }
    if (!SUPPORTED_SCOPES.includes(scope)) {
      throw new Error(`不支持的搜索范围 (scope): ${scope}。支持的范围: ${SUPPORTED_SCOPES.join(', ')}`);
    }
    if (!['chat_completions', 'simple'].includes(format)) {
      throw new Error(`不支持的输出格式 (format): ${format}。支持的格式: chat_completions, simple`);
    }
    if (typeof stream !== 'boolean') {
      throw new Error('是否开启流式输出 (stream) 必须是布尔值');
    }
    if (format === 'simple' && stream) {
      throw new Error('流式输出仅在 format = chat_completions 时支持');
    }
    if (!Array.isArray(messages)) {
      throw new Error('消息内容 (messages) 必须是数组类型');
    }

    const body = {
      model: model,
      messages: messages,
      scope: scope,
      format: format,
      stream: stream,
      conciseSnippet: conciseSnippet
    };

    return this._request(this.chatUrl, {
      body: JSON.stringify(body)
    });
  }
}

// 创建单例实例
let metasoAPI = null;

export function getMetasoAPI() {
  if (!metasoAPI) {
    metasoAPI = new MetasoAPI();
  }
  return metasoAPI;
}

// 导出常用方法
export async function metasoSearch(query, size, scope, includeSummary, includeRawContent, conciseSnippet) {
  const api = getMetasoAPI();
  return api.search(query, size, scope, includeSummary, includeRawContent, conciseSnippet);
}

export async function metasoReadPage(url, format) {
  const api = getMetasoAPI();
  return api.readWebPage(url, format);
}

export async function metasoChat(messages, model, scope, format, stream, conciseSnippet) {
  const api = getMetasoAPI();
  return api.chat(messages, model, scope, format, stream, conciseSnippet);
}

// 提供与旧 API 兼容的方法
export async function metasoPing() {
  return { status: 'ok' }; // 模拟 Ping 响应
}

export async function metasoListTools() {
  return {
    tools: [
      {
        name: 'metaso_web_search',
        description: '根据关键词搜索网页、文档、论文、图片、视频、播客等内容',
        inputSchema: {
          type: 'object',
          properties: {
            q: { type: 'string', description: '搜索查询关键词' },
            size: { type: 'integer', description: '返回结果数量，默认10' },
            scope: { 
              type: 'string', 
              description: `搜索范围：${SUPPORTED_SCOPES.join(', ')}, 默认 webpage`,
              enum: SUPPORTED_SCOPES
            },
            includeSummary: { type: 'boolean', description: '是否包含精简的原文匹配信息，默认 true' },
            includeRawContent: { type: 'boolean', description: '是否通过网页的摘要信息进行召回增强，默认 false' },
            conciseSnippet: { type: 'boolean', description: '是否抓取所有来源网页原文，默认 false' }
          },
          required: ['q', 'size', 'scope', 'includeSummary', 'includeRawContent', 'conciseSnippet']
        }
      },
      {
        name: 'metaso_web_reader',
        description: '读取指定 URL 的网页内容',
        inputSchema: {
          type: 'object',
          properties: {
            url: { type: 'string', description: '要读取的 URL 地址' },
            format: { type: 'string', description: '输出格式：json, markdown' }
          },
          required: ['url', 'format']
        }
      },
      {
        name: 'metaso_chat',
        description: '基于 RAG 的智能问答服务',
        inputSchema: {
          type: 'object',
          properties: {
            messages: { type: 'array', description: '用户消息数组' },
            model: { 
              type: 'string', 
              description: `使用的模型：${SUPPORTED_MODELS.join(', ')}, 默认 fast`,
              enum: SUPPORTED_MODELS
            },
            scope: { 
              type: 'string', 
              description: `搜索范围：${SUPPORTED_SCOPES.join(', ')}, 默认 webpage`,
              enum: SUPPORTED_SCOPES
            },
            format: { 
              type: 'string', 
              description: '输出格式：chat_completions, simple',
              enum: ['chat_completions', 'simple']
            },
            stream: { type: 'boolean', description: '是否开启流式输出，默认 false' },
            conciseSnippet: { type: 'boolean', description: '是否返回精简的原文匹配信息，默认 false' }
          },
          required: ['messages', 'model', 'scope', 'format', 'stream', 'conciseSnippet']
        }
      }
    ]
  };
}

// 默认导出
export default MetasoAPI;
