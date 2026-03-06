const https = require('https');
const { URL } = require('url');

const FEISHU_APP_ID = process.env.FEISHU_APP_ID || 'cli_a9140ac9cab85bd3';
const FEISHU_APP_SECRET = process.env.FEISHU_APP_SECRET || 'qlySTZmzM567o4TnZDrvOdVNXMqIwaD0';

let accessToken = null;
let tokenExpire = 0;

async function getAccessToken() {
  if (accessToken && Date.now() < tokenExpire) {
    return accessToken;
  }

  const postData = JSON.stringify({
    app_id: FEISHU_APP_ID,
    app_secret: FEISHU_APP_SECRET
  });

  const options = {
    hostname: 'open.feishu.cn',
    path: '/open-apis/auth/v3/tenant_access_token/internal',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(postData)
    }
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.code === 0) {
            accessToken = result.tenant_access_token;
            tokenExpire = Date.now() + (result.expire - 300) * 1000;
            resolve(accessToken);
          } else {
            reject(new Error(`Failed to get token: ${result.msg}`));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

async function getBitableRecords(appToken, tableId) {
  const token = await getAccessToken();
  
  const options = {
    hostname: 'open.feishu.cn',
    path: `/open-apis/bitable/v1/apps/${appToken}/tables/${tableId}/records?page_size=100`,
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.code === 0) {
            resolve(result.data.items);
          } else {
            reject(new Error(`Failed to get records: ${result.msg}`));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

async function updateBitableRecord(appToken, tableId, recordId, fields) {
  const token = await getAccessToken();
  const postData = JSON.stringify({ fields });

  const options = {
    hostname: 'open.feishu.cn',
    path: `/open-apis/bitable/v1/apps/${appToken}/tables/${tableId}/records/${recordId}`,
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(postData)
    }
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.code === 0) {
            resolve(result.data);
          } else {
            reject(new Error(`Failed to update record: ${result.msg}`));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

async function sendFeishuMessage(chatId, text) {
  const token = await getAccessToken();
  const content = JSON.stringify({ text });
  const postData = JSON.stringify({
    receive_id: chatId,
    msg_type: 'text',
    content
  });

  const options = {
    hostname: 'open.feishu.cn',
    path: '/open-apis/im/v1/messages?receive_id_type=chat_id',
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Content-Length': Buffer.byteLength(postData)
    }
  };

  return new Promise((resolve, reject) => {
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.code === 0) {
            resolve(result.data);
          } else {
            reject(new Error(`Failed to send message: ${result.msg}`));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

function analyzeCompany(pageText) {
  const text = pageText.toLowerCase();
  
  const factoryKeywords = ['oem', 'production line', 'iso9001', 'request a quote', 'manufacturing', 'factory', 'manufacturer', 'produktion'];
  const distributorKeywords = ['distributor', 'wholesaler', 'warehouse', 'multiple brands', 'reseller', 'vertrieb', 'sales company'];
  const competitorKeywords = ['foundry services', 'iron casting service', 'casting', '代工', ' foundry'];
  
  let factoryScore = 0;
  let distributorScore = 0;
  let competitorScore = 0;
  
  factoryKeywords.forEach(kw => { if (text.includes(kw)) factoryScore++; });
  distributorKeywords.forEach(kw => { if (text.includes(kw)) distributorScore++; });
  competitorKeywords.forEach(kw => { if (text.includes(kw)) competitorScore++; });
  
  if (factoryScore > 0) {
    return { type: '终端工厂', grade: 'A', action: '立即跟进: 开发信 + LinkedIn 加人 + 询盘引导' };
  } else if (competitorScore > 0) {
    return { type: '同行/铸件厂', grade: 'C', action: '过滤: 同行竞争、不跟进' };
  } else if (distributorScore > 0) {
    return { type: '贸易商/经销商', grade: 'B', action: '加入培育: 发资料包 + 问终端项目 + 争取引荐' };
  }
  
  return { type: '未确定', grade: 'C', action: '需要进一步分析' };
}

module.exports = {
  getAccessToken,
  getBitableRecords,
  updateBitableRecord,
  sendFeishuMessage,
  analyzeCompany
};
