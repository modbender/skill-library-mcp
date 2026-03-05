#!/usr/bin/env node
/**
 * M5Stack MCP 客户端 - 简单可靠版
 * 基于成功测试的代码
 */

const https = require('https');
const { URL } = require('url');

/**
 * 简单的 MCP 查询函数 - 一键查询 M5Stack 知识库
 * 
 * @param {string} query - 查询内容
 * @param {object} options - 选项 {num, is_chip, filter_type}
 * @returns {Promise<object>} 查询结果
 */
async function mcpSearch(query, options = {}) {
  return new Promise((resolve, reject) => {
    let messageEndpoint = null;
    let sseConnection = null;
    let result = null;
    let initialized = false;
    let toolsListed = false;
    let searchSent = false;
    
    // 1. 连接 SSE
    const sseUrl = new URL('https://mcp.m5stack.com/sse');
    sseConnection = https.get(sseUrl, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk.toString();
        
        // 处理收到的数据
        if (!messageEndpoint && data.includes('event: endpoint')) {
          // 找到 endpoint
          const lines = data.split('\n');
          for (let i = 0; i < lines.length; i++) {
            if (lines[i].startsWith('event: endpoint')) {
              if (i + 1 < lines.length && lines[i+1].startsWith('data:')) {
                messageEndpoint = lines[i+1].replace('data:', '').trim();
                
                // 发送 initialize
                sendJsonRpc(1, 'initialize', {
                  protocolVersion: '2024-11-05',
                  capabilities: {},
                  clientInfo: { name: 'simple-mcp-client', version: '1.0.0' }
                });
              }
            }
          }
        }
        
        // 检查是否有 JSON-RPC 响应
        if (messageEndpoint) {
          // 检查 id=1 (initialize) 响应
          if (!initialized && data.includes('"id":1')) {
            initialized = true;
            // 发送 tools/list
            sendJsonRpc(2, 'tools/list', {});
          }
          
          // 检查 id=2 (tools/list) 响应
          if (!toolsListed && data.includes('"id":2')) {
            toolsListed = true;
            // 发送 knowledge_search
            sendJsonRpc(3, 'tools/call', {
              name: 'knowledge_search',
              arguments: {
                query: query,
                ...options
              }
            });
            searchSent = true;
          }
          
          // 检查 id=3 (knowledge_search) 响应
          if (searchSent && data.includes('"id":3')) {
            // 找到结果！
            try {
              // 提取 id=3 的响应
              const lines = data.split('\n');
              let jsonStr = '';
              let inMessage = false;
              
              for (let i = 0; i < lines.length; i++) {
                if (lines[i].startsWith('event: message')) {
                  inMessage = true;
                } else if (inMessage && lines[i].startsWith('data:')) {
                  jsonStr = lines[i].replace('data:', '').trim();
                  // 检查是不是 id=3 的
                  if (jsonStr.includes('"id":3')) {
                    const json = JSON.parse(jsonStr);
                    result = json.result;
                    // 成功！
                    cleanup();
                    resolve(result);
                    return;
                  } else {
                    inMessage = false;
                  }
                }
              }
            } catch (e) {
              // 解析失败，继续等
            }
          }
        }
      });
      
      res.on('end', () => {
        if (!result) {
          reject(new Error('连接关闭，未收到结果'));
        }
      });
    });
    
    sseConnection.on('error', (e) => {
      reject(e);
    });
    
    // 发送 JSON-RPC 请求
    function sendJsonRpc(id, method, params) {
      const postData = JSON.stringify({
        jsonrpc: '2.0',
        id: id,
        method: method,
        params: params
      });
      
      const url = new URL('https://mcp.m5stack.com' + messageEndpoint);
      const options = {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData)
        }
      };
      
      const req = https.request(url, options, () => {});
      req.on('error', (e) => reject(e));
      req.write(postData);
      req.end();
    }
    
    // 清理
    function cleanup() {
      if (sseConnection) {
        sseConnection.destroy();
      }
    }
    
    // 30秒超时
    const timeout = setTimeout(() => {
      cleanup();
      reject(new Error('查询超时'));
    }, 30000);
  });
}

// 如果直接运行，演示使用方法
if (require.main === module) {
  (async () => {
    console.log('🦾 M5Stack MCP 知识库查询演示');
    console.log('='.repeat(50));
    
    try {
      console.log('\n🔍 查询: M5Stack CoreS3');
      const result = await mcpSearch('M5Stack CoreS3', { num: 1 });
      
      console.log('\n✅ 查询结果:');
      console.log(JSON.stringify(result, null, 2));
      
    } catch (e) {
      console.error('❌ 错误:', e);
    }
  })();
}

module.exports = { mcpSearch };
