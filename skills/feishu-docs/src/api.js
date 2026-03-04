const axios = require('axios');

// 飞书 block_type 数字到字符串的映射
const BLOCK_TYPE_MAP = {
  1: 'page', 2: 'text',
  3: 'heading1', 4: 'heading2', 5: 'heading3',
  6: 'heading4', 7: 'heading5', 8: 'heading6',
  9: 'heading7', 10: 'heading8', 11: 'heading9',
  12: 'bullet', 13: 'ordered', 14: 'code',
  15: 'quote', 19: 'callout', 22: 'divider',
  27: 'table'
};

// 飞书代码语言编号到名称的映射
const CODE_LANG_MAP = {
  1: '', 12: 'c', 13: 'cpp', 14: 'csharp', 18: 'css',
  22: 'go', 24: 'html', 28: 'java', 29: 'javascript',
  36: 'kotlin', 44: 'php', 46: 'python', 51: 'ruby',
  52: 'rust', 55: 'shell', 58: 'sql', 59: 'swift',
  60: 'typescript', 77: 'json', 78: 'xml', 81: 'yaml'
};

class FeishuDocsAPI {
  constructor(appId, appSecret) {
    this.appId = appId;
    this.appSecret = appSecret;
    this.baseURL = 'https://open.feishu.cn/open-apis';
    this.accessToken = null;
    this.tokenExpireTime = 0;
    this._tokenPromise = null;
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'FeishuDocsAPI/1.0.0'
      }
    });
  }

  /**
   * 获取访问令牌（带并发控制）
   */
  async getAccessToken() {
    const now = Date.now();
    if (this.accessToken && now < this.tokenExpireTime - 60000) {
      return this.accessToken;
    }

    // 防止并发请求同时刷新 token
    if (this._tokenPromise) {
      return this._tokenPromise;
    }

    this._tokenPromise = this._refreshToken();
    try {
      return await this._tokenPromise;
    } finally {
      this._tokenPromise = null;
    }
  }

  /**
   * 刷新访问令牌（内部方法）
   */
  async _refreshToken() {
    try {
      const response = await this.client.post('/auth/v3/tenant_access_token/internal/', {
        app_id: this.appId,
        app_secret: this.appSecret
      });

      if (response.data.code === 0) {
        this.accessToken = response.data.tenant_access_token;
        this.tokenExpireTime = Date.now() + (response.data.expire * 1000);
        return this.accessToken;
      } else {
        throw new Error(`获取访问令牌失败: ${response.data.msg}`);
      }
    } catch (error) {
      this.accessToken = null;
      this.tokenExpireTime = 0;
      throw new Error(`获取访问令牌错误: ${error.message}`);
    }
  }

  /**
   * 发送API请求（带重试和错误恢复）
   */
  async request(method, url, data = null, params = null, _retryCount = 0) {
    const MAX_RETRIES = 2;
    try {
      const token = await this.getAccessToken();
      const config = {
        method,
        url,
        headers: {
          'Authorization': `Bearer ${token}`
        }
      };

      if (data) {
        config.data = data;
      }

      if (params) {
        config.params = params;
      }

      const response = await this.client.request(config);
      
      if (response.data.code === 0) {
        return response.data.data;
      } else if (response.data.code === 99991663 || response.data.code === 99991661) {
        // token 过期或无效，清除缓存后重试
        if (_retryCount < MAX_RETRIES) {
          this.accessToken = null;
          this.tokenExpireTime = 0;
          return this.request(method, url, data, params, _retryCount + 1);
        }
        throw new Error(`API请求失败: ${response.data.msg} (code: ${response.data.code})`);
      } else {
        throw new Error(`API请求失败: ${response.data.msg} (code: ${response.data.code})`);
      }
    } catch (error) {
      if (error.message?.startsWith('API请求失败')) {
        throw error;
      }
      if (error.response) {
        const status = error.response.status;
        const msg = error.response.data?.msg || error.response.statusText || error.message;
        
        // 401 未授权，尝试刷新 token 重试
        if (status === 401 && _retryCount < MAX_RETRIES) {
          this.accessToken = null;
          this.tokenExpireTime = 0;
          return this.request(method, url, data, params, _retryCount + 1);
        }
        
        // 429 限流或 5xx 服务端错误，等待后重试
        if ((status === 429 || status >= 500) && _retryCount < MAX_RETRIES) {
          const delay = Math.pow(2, _retryCount) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
          return this.request(method, url, data, params, _retryCount + 1);
        }
        
        throw new Error(`API请求错误: ${msg} (status: ${status})`);
      } else {
        // 网络错误，重试
        if (_retryCount < MAX_RETRIES) {
          const delay = Math.pow(2, _retryCount) * 1000;
          await new Promise(resolve => setTimeout(resolve, delay));
          return this.request(method, url, data, params, _retryCount + 1);
        }
        throw new Error(`网络请求错误: ${error.message}`);
      }
    }
  }

  /**
   * 创建文档
   * @param {string} folderToken - 文件夹token
   * @param {string} title - 文档标题
   * @param {string} content - 文档内容（Markdown格式）
   * @returns {Promise<Object>} 文档信息
   */
  async createDocument(folderToken, title) {
    const data = {
      folder_token: folderToken,
      title: title
    };

    return await this.request('POST', '/docx/v1/documents', data);
  }

  /**
   * 获取文档信息
   * @param {string} documentId - 文档ID
   * @returns {Promise<Object>} 文档信息
   */
  async getDocument(documentId) {
    return await this.request('GET', `/docx/v1/documents/${documentId}`);
  }

  /**
   * 获取文档原始内容
   * @param {string} documentId - 文档ID
   * @returns {Promise<string>} 文档原始内容
   */
  async getDocumentRawContent(documentId) {
    return await this.request('GET', `/docx/v1/documents/${documentId}/raw_content`);
  }

  /**
   * 获取文档块列表
   * @param {string} documentId - 文档ID
   * @param {number} pageSize - 每页大小
   * @param {string} pageToken - 分页token
   * @returns {Promise<Object>} 块列表
   */
  async getDocumentBlocks(documentId, pageSize = 50, pageToken = null) {
    const params = {
      page_size: pageSize
    };

    if (pageToken) {
      params.page_token = pageToken;
    }

    return await this.request('GET', `/docx/v1/documents/${documentId}/blocks`, null, params);
  }

  /**
   * 获取文档所有块（自动分页）
   * @param {string} documentId - 文档ID
   * @returns {Promise<Object>} 包含所有块的列表
   */
  async getAllDocumentBlocks(documentId) {
    let allItems = [];
    let pageToken = null;
    
    do {
      const result = await this.getDocumentBlocks(documentId, 50, pageToken);
      if (result.items) {
        allItems = allItems.concat(result.items);
      }
      pageToken = result.page_token || null;
    } while (pageToken);
    
    return { items: allItems };
  }

  /**
   * 更新文档块
   * @param {string} documentId - 文档ID
   * @param {string} blockId - 块ID
   * @param {Object} updateRequest - 更新请求
   * @returns {Promise<Object>} 更新结果
   */
  async updateDocumentBlock(documentId, blockId, updateRequest) {
    return await this.request('PATCH', `/docx/v1/documents/${documentId}/blocks/${blockId}`, updateRequest);
  }

  /**
   * 追加内容到文档
   * @param {string} documentId - 文档ID
   * @param {string} content - 要追加的内容（Markdown格式）
   * @returns {Promise<Object>} 更新结果
   */
  async appendToDocument(documentId, content, contentType = 'markdown') {
    // 1. 将内容转换为文档块
    const convertResult = await this.convertContent(contentType, content);
    
    if (!convertResult.blocks || convertResult.blocks.length === 0) {
      throw new Error('内容转换后没有可插入的块');
    }

    // 2. 获取文档块列表，找到 page 块并计算插入位置
    const allBlocks = await this.getAllDocumentBlocks(documentId);
    if (!allBlocks.items || allBlocks.items.length === 0) {
      throw new Error('文档没有可更新的块');
    }
    
    const pageBlockId = allBlocks.items[0].block_id;
    const childCount = allBlocks.items.length - 1; // 减去 page 块本身

    // 3. 过滤不支持直接插入的块类型
    const supportedBlocks = convertResult.blocks.filter(block => {
      const blockType = block.block_type;
      return blockType !== 31 && blockType !== 32;
    });

    if (supportedBlocks.length === 0) {
      throw new Error('转换后没有可插入的块');
    }

    // 4. 在文档末尾插入新块
    return await this.createDocumentBlocks(documentId, pageBlockId, supportedBlocks, childCount);
  }

  /**
   * 删除文档块
   * @param {string} documentId - 文档ID
   * @param {string} blockId - 要删除的块ID
   * @returns {Promise<Object>} 删除结果
   */
  async deleteDocumentBlock(documentId, blockId) {
    return await this.request('DELETE', `/docx/v1/documents/${documentId}/blocks/${blockId}`);
  }

  /**
   * 批量删除文档块（从后往前逐个删除）
   * @param {string} documentId - 文档ID
   * @param {Array<string>} blockIds - 要删除的块ID数组
   */
  async batchDeleteBlocks(documentId, blockIds) {
    for (let i = blockIds.length - 1; i >= 0; i--) {
      await this.deleteDocumentBlock(documentId, blockIds[i]);
    }
  }

  /**
   * 替换文档全部内容
   * @param {string} documentId - 文档ID
   * @param {string} content - 新内容
   * @param {string} contentType - 内容类型：'markdown' 或 'html'
   * @returns {Promise<Object>} 操作结果
   */
  async replaceDocumentContent(documentId, content, contentType = 'markdown') {
    // 1. 获取所有块
    const allBlocks = await this.getAllDocumentBlocks(documentId);
    if (!allBlocks.items || allBlocks.items.length === 0) {
      throw new Error('文档没有可更新的块');
    }

    const pageBlockId = allBlocks.items[0].block_id;
    
    // 2. 删除所有子块（跳过 page 块本身）
    const childBlockIds = allBlocks.items.slice(1).map(b => b.block_id);
    if (childBlockIds.length > 0) {
      await this.batchDeleteBlocks(documentId, childBlockIds);
    }

    // 3. 如果没有新内容，清空即可
    if (!content || content.trim() === '') {
      return { success: true };
    }

    // 4. 转换并插入新内容
    const convertResult = await this.convertContent(contentType, content);
    if (!convertResult.blocks || convertResult.blocks.length === 0) {
      return { success: true };
    }

    const supportedBlocks = convertResult.blocks.filter(block => {
      return block.block_type !== 31 && block.block_type !== 32;
    });

    if (supportedBlocks.length > 0) {
      const batchSize = 50;
      for (let i = 0; i < supportedBlocks.length; i += batchSize) {
        const batch = supportedBlocks.slice(i, i + batchSize);
        await this.createDocumentBlocks(documentId, pageBlockId, batch, i);
      }
    }

    return { success: true };
  }

  /**
   * 删除文档（通过云文档 Drive API）
   * @param {string} documentId - 文档ID
   * @returns {Promise<Object>} 删除结果
   */
  async deleteDocument(documentId) {
    return await this.request('DELETE', `/drive/v1/files/${documentId}`, null, { type: 'docx' });
  }

  /**
   * 获取文件夹下的文件列表
   * @param {string} folderToken - 文件夹token
   * @param {string} type - 文件类型（doc, docx, sheet, bitable, file）
   * @returns {Promise<Array>} 文件列表
   */
  async listFolderFiles(folderToken, type = null) {
    const params = {
      folder_token: folderToken
    };
    if (type) {
      params.type = type;
    }
    return await this.request('GET', '/drive/v1/files', null, params);
  }

  /**
   * 搜索文档
   * @param {string} query - 搜索关键词
   * @param {string} folderToken - 文件夹token（可选）
   * @returns {Promise<Array>} 搜索结果
   */
  async searchDocuments(query, folderToken = null) {
    // 获取指定文件夹（或根目录）下的文件，并按关键词过滤
    const params = {
      page_size: 100
    };
    if (folderToken) {
      params.folder_token = folderToken;
    }

    const allFiles = await this.request('GET', '/drive/v1/files', null, params);
    
    if (!allFiles.files) {
      return { files: [], has_more: false };
    }
    
    // 按关键词过滤
    const filteredFiles = allFiles.files.filter(file => {
      return file.name && file.name.toLowerCase().includes(query.toLowerCase());
    });
    
    return {
      files: filteredFiles,
      has_more: allFiles.has_more || false
    };
  }

  /**
   * 添加文档权限成员
   * @param {string} token - 文档token
   * @param {string} memberId - 成员ID
   * @param {string} memberType - 成员类型（user, department）
   * @param {string} perm - 权限类型（view, edit, comment）
   * @returns {Promise<Object>} 添加结果
   */
  async addPermissionMember(token, memberId, memberType = 'user', perm = 'view') {
    const data = {
      member_type: memberType,
      member_id: memberId,
      perm
    };

    return await this.request('POST', `/drive/v1/permissions/${token}/members`, data, { type: 'docx' });
  }

  /**
   * 获取文档权限成员列表
   * @param {string} token - 文档token
   * @returns {Promise<Array>} 权限成员列表
   */
  async getPermissionMembers(token) {
    return await this.request('GET', `/drive/v1/permissions/${token}/members`, null, { type: 'docx' });
  }

  /**
   * 将Markdown转换为飞书文档块
   * @param {string} markdown - Markdown文本
   * @returns {Array} 飞书文档块数组
   */
  markdownToBlocks(markdown) {
    if (!markdown || markdown.trim() === '') {
      return [];
    }

    const lines = markdown.split('\n');
    const blocks = [];
    let currentList = null;
    let currentListType = null;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // 空行
      if (line === '') {
        if (currentList) {
          blocks.push(currentList);
          currentList = null;
          currentListType = null;
        }
        continue;
      }

      // 标题 (#, ##, ###)
      if (line.startsWith('#')) {
        if (currentList) {
          blocks.push(currentList);
          currentList = null;
          currentListType = null;
        }
        
        const match = line.match(/^(#{1,6})\s+(.+)$/);
        if (match) {
          const level = match[1].length;
          const text = match[2];
          blocks.push({
            block_type: 'heading',
            heading: {
              level,
              title: [{
                elements: [{
                  text_run: {
                    content: text
                  }
                }]
              }]
            }
          });
        }
        continue;
      }

      // 无序列表 (-, *, +)
      if (line.match(/^[-*+]\s+/)) {
        const text = line.replace(/^[-*+]\s+/, '');
        if (!currentList || currentListType !== 'bullet') {
          if (currentList) {
            blocks.push(currentList);
          }
          currentList = {
            block_type: 'bullet',
            bullet: {
              children: []
            }
          };
          currentListType = 'bullet';
        }
        
        currentList.bullet.children.push({
          block_type: 'text',
          text: {
            elements: [{
              text_run: {
                content: text
              }
            }]
          }
        });
        continue;
      }

      // 有序列表 (1., 2., 3.)
      if (line.match(/^\d+\.\s+/)) {
        const text = line.replace(/^\d+\.\s+/, '');
        if (!currentList || currentListType !== 'ordered') {
          if (currentList) {
            blocks.push(currentList);
          }
          currentList = {
            block_type: 'ordered',
            ordered: {
              children: []
            }
          };
          currentListType = 'ordered';
        }
        
        currentList.ordered.children.push({
          block_type: 'text',
          text: {
            elements: [{
              text_run: {
                content: text
              }
            }]
          }
        });
        continue;
      }

      // 代码块 (```)
      if (line.startsWith('```')) {
        if (currentList) {
          blocks.push(currentList);
          currentList = null;
          currentListType = null;
        }
        
        const language = line.replace(/^```/, '') || '';
        let codeContent = '';
        i++;
        
        while (i < lines.length && !lines[i].trim().startsWith('```')) {
          codeContent += lines[i] + '\n';
          i++;
        }
        
        blocks.push({
          block_type: 'code',
          code: {
            language,
            content: codeContent.trim()
          }
        });
        continue;
      }

      // 引用 (>)
      if (line.startsWith('> ') || line === '>') {
        if (currentList) {
          blocks.push(currentList);
          currentList = null;
          currentListType = null;
        }
        
        // 合并连续引用行
        let quoteText = line.replace(/^>\s?/, '');
        while (i + 1 < lines.length) {
          const nextLine = lines[i + 1].trim();
          if (nextLine.startsWith('> ') || nextLine === '>') {
            quoteText += '\n' + nextLine.replace(/^>\s?/, '');
            i++;
          } else {
            break;
          }
        }
        
        blocks.push({
          block_type: 'quote',
          quote: {
            elements: [{
              text_run: {
                content: quoteText
              }
            }]
          }
        });
        continue;
      }

      // 分割线 (---, ***)
      if (line.match(/^-{3,}$/) || line.match(/^\*{3,}$/)) {
        if (currentList) {
          blocks.push(currentList);
          currentList = null;
          currentListType = null;
        }
        
        blocks.push({
          block_type: 'divider',
          divider: {}
        });
        continue;
      }

      // 普通文本
      if (currentList) {
        blocks.push(currentList);
        currentList = null;
        currentListType = null;
      }
      
      blocks.push({
        block_type: 'text',
        text: {
          elements: [{
            text_run: {
              content: line
            }
          }]
        }
      });
    }

    // 处理最后一个列表
    if (currentList) {
      blocks.push(currentList);
    }

    return blocks;
  }

  /**
   * 将飞书文档块转换为Markdown
   * @param {Array} blocks - 飞书文档块数组
   * @returns {string} Markdown文本
   */
  blocksToMarkdown(blocks) {
    if (!blocks || blocks.length === 0) {
      return '';
    }

    let markdown = '';
    let orderedIndex = 1;
    let lastType = null;
    
    for (const block of blocks) {
      // 统一 block_type 为字符串
      let blockType = block.block_type;
      if (typeof blockType === 'number') {
        blockType = BLOCK_TYPE_MAP[blockType] || `unknown_${blockType}`;
      }

      // 从列表切换到非列表时，添加额外空行
      if ((lastType === 'bullet' || lastType === 'ordered') &&
          blockType !== 'bullet' && blockType !== 'ordered') {
        markdown += '\n';
        orderedIndex = 1;
      }

      // 处理标题（heading 或 heading1-heading9）
      if (blockType.startsWith('heading')) {
        let level;
        if (blockType === 'heading') {
          level = block.heading?.level || 1;
        } else {
          level = parseInt(blockType.replace('heading', '')) || 1;
        }
        const title = this._extractBlockText(block, blockType);
        markdown += '#'.repeat(Math.min(level, 6)) + ' ' + title + '\n\n';
        lastType = 'heading';
        orderedIndex = 1;
        continue;
      }

      switch (blockType) {
        case 'page':
          break;
          
        case 'text': {
          const text = this._extractBlockText(block, 'text');
          if (text) {
            markdown += text + '\n\n';
          }
          lastType = 'text';
          orderedIndex = 1;
          break;
        }
          
        case 'bullet': {
          // 飞书 API 格式：每个 bullet 是独立的块
          if (block.bullet?.elements) {
            const text = this.extractTextFromElements(block.bullet.elements);
            markdown += '- ' + text + '\n';
          }
          // 本地格式兼容：bullet 包含 children 数组
          else if (block.bullet?.children) {
            for (const child of block.bullet.children) {
              const childText = this.extractTextFromElements(child.text?.elements || []);
              markdown += '- ' + childText + '\n';
            }
          }
          lastType = 'bullet';
          break;
        }
          
        case 'ordered': {
          if (lastType !== 'ordered') {
            orderedIndex = 1;
          }
          // 飞书 API 格式
          if (block.ordered?.elements) {
            const text = this.extractTextFromElements(block.ordered.elements);
            markdown += orderedIndex + '. ' + text + '\n';
            orderedIndex++;
          }
          // 本地格式兼容
          else if (block.ordered?.children) {
            for (const child of block.ordered.children) {
              const childText = this.extractTextFromElements(child.text?.elements || []);
              markdown += orderedIndex + '. ' + childText + '\n';
              orderedIndex++;
            }
          }
          lastType = 'ordered';
          break;
        }
          
        case 'code': {
          // 语言可能是字符串或数字编号
          let language = block.code?.style?.language ?? block.code?.language ?? '';
          if (typeof language === 'number') {
            language = CODE_LANG_MAP[language] || '';
          }
          // 代码内容可能在 body.elements 或直接在 content 字段
          let codeContent = '';
          if (block.code?.body?.elements) {
            codeContent = this.extractTextFromElements(block.code.body.elements);
          } else {
            codeContent = block.code?.content || '';
          }
          markdown += '```' + language + '\n' + codeContent + '\n```\n\n';
          lastType = 'code';
          orderedIndex = 1;
          break;
        }
          
        case 'quote': {
          const quoteText = this._extractBlockText(block, 'quote');
          const lines = quoteText.split('\n');
          markdown += lines.map(l => '> ' + l).join('\n') + '\n\n';
          lastType = 'quote';
          orderedIndex = 1;
          break;
        }
          
        case 'divider':
          markdown += '---\n\n';
          lastType = 'divider';
          orderedIndex = 1;
          break;
          
        case 'callout': {
          const calloutText = this._extractBlockText(block, 'callout');
          markdown += '> 💡 ' + calloutText + '\n\n';
          lastType = 'callout';
          orderedIndex = 1;
          break;
        }
          
        default:
          lastType = blockType;
          break;
      }
    }

    return markdown.trim();
  }

  /**
   * 从块中提取文本内容（兼容飞书 API 多种块格式）
   */
  _extractBlockText(block, type) {
    // 格式1: block[type].elements（飞书 API 标准格式）
    if (block[type]?.elements) {
      return this.extractTextFromElements(block[type].elements);
    }
    // 格式2: heading 的 title 数组格式（旧格式兼容）
    if (type === 'heading' && block.heading?.title) {
      return this.extractTextFromElements(block.heading.title[0]?.elements || []);
    }
    // 格式3: heading1-heading9 查找
    if (type.startsWith('heading')) {
      for (let i = 1; i <= 9; i++) {
        const key = `heading${i}`;
        if (block[key]?.elements) {
          return this.extractTextFromElements(block[key].elements);
        }
      }
    }
    return '';
  }

  /**
   * 将Markdown/HTML内容转换为文档块
   * @param {string} contentType - 内容类型：'markdown' 或 'html'
   * @param {string} content - 要转换的内容
   * @param {string} userIdType - 用户ID类型：'open_id'、'union_id'、'user_id'（默认：'open_id'）
   * @returns {Promise<Object>} 转换结果，包含块ID和块数据
   */
  async convertContent(contentType, content, userIdType = 'open_id') {
    if (!['markdown', 'html'].includes(contentType)) {
      throw new Error('contentType必须是"markdown"或"html"');
    }

    if (!content || content.trim() === '') {
      throw new Error('content不能为空');
    }

    const data = {
      content_type: contentType,
      content: content
    };

    const params = {};
    if (userIdType) {
      params.user_id_type = userIdType;
    }

    return await this.request('POST', '/docx/v1/documents/blocks/convert', data, params);
  }

  /**
   * 创建嵌套块（将转换后的块插入到文档中）
   * @param {string} documentId - 文档ID
   * @param {string} blockId - 父块ID（通常为文档的根块ID）
   * @param {Array} children - 要插入的子块数组
   * @param {number} index - 插入位置索引（从0开始）
   * @param {string} userIdType - 用户ID类型：'open_id'、'union_id'、'user_id'（默认：'open_id'）
   * @returns {Promise<Object>} 创建结果
   */
  async createDocumentBlocks(documentId, blockId, children, index = 0, userIdType = 'open_id') {
    if (!documentId) {
      throw new Error('documentId不能为空');
    }

    if (!blockId) {
      throw new Error('blockId不能为空');
    }

    if (!children || !Array.isArray(children) || children.length === 0) {
      throw new Error('children必须是非空数组');
    }

    // 处理表格块中的merge_info字段（根据飞书文档，需要去除）
    const processedChildren = children.map(child => {
      // 检查是否是表格块（block_type可能是数字或字符串）
      const isTable = child.block_type === 'table' || child.block_type === 27;
      if (isTable && child.table && child.table.merge_info) {
        // 创建深拷贝并删除merge_info字段
        const processedChild = JSON.parse(JSON.stringify(child));
        delete processedChild.table.merge_info;
        return processedChild;
      }
      return child;
    });

    const data = {
      children: processedChildren,
      index: index
    };

    const params = {};
    if (userIdType) {
      params.user_id_type = userIdType;
    }

    return await this.request('POST', `/docx/v1/documents/${documentId}/blocks/${blockId}/children`, data, params);
  }

  /**
   * 批量创建文档（使用正确的转换和插入流程）
   * @param {string} folderToken - 文件夹token
   * @param {string} title - 文档标题
   * @param {string} content - 文档内容（Markdown格式）
   * @param {string} contentType - 内容类型：'markdown' 或 'html'（默认：'markdown'）
   * @returns {Promise<Object>} 文档信息
   */
  async createDocumentWithContent(folderToken, title, content = '', contentType = 'markdown') {
    // 1. 先创建空文档
    const createData = {
      folder_token: folderToken,
      title: title
    };

    const document = await this.request('POST', '/docx/v1/documents', createData);
    const documentId = document.document.document_id;

    // 如果没有内容，直接返回
    if (!content || content.trim() === '') {
      return document;
    }

    try {
      // 2. 将内容转换为文档块
      const convertResult = await this.convertContent(contentType, content);
      
      if (!convertResult.blocks || convertResult.blocks.length === 0) {
        return document;
      }

      // 3. 过滤掉不支持直接插入的块类型（表格相关）
      const supportedBlocks = convertResult.blocks.filter(block => {
        const blockType = block.block_type;
        return blockType !== 31 && blockType !== 32;
      });
      
      if (supportedBlocks.length === 0) {
        return document;
      }

      // 4. 获取文档的根块ID
      const rootBlockId = documentId;

      // 5. 分批插入块（每批最多50个，飞书API限制）
      const batchSize = 50;
      for (let i = 0; i < supportedBlocks.length; i += batchSize) {
        const batch = supportedBlocks.slice(i, i + batchSize);
        await this.createDocumentBlocks(documentId, rootBlockId, batch, i);
      }

      return document;
    } catch (error) {
      error.message = `文档已创建(ID: ${documentId})，但内容插入失败: ${error.message}`;
      throw error;
    }
  }

  /**
   * 从元素数组中提取文本
   * @param {Array} elements - 元素数组
   * @returns {string} 提取的文本
   */
  extractTextFromElements(elements) {
    if (!elements || elements.length === 0) {
      return '';
    }

    let text = '';
    for (const element of elements) {
      if (element.text_run) {
        text += element.text_run.content || '';
      }
    }
    
    return text;
  }
}

module.exports = FeishuDocsAPI;