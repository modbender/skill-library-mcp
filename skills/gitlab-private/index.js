const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const http = require('http');
const https = require('https');
const url = require('url');

// ============ 配置 ============
const CONFIG_DIR = path.join(__dirname, 'config');
const USERS_FILE = path.join(CONFIG_DIR, 'users.enc'); // 加密存储的用户 token
const OAUTH_FILE = path.join(CONFIG_DIR, 'oauth.json');

// 加密密钥（必须通过环境变量设置）
const ENCRYPT_KEY = process.env.GITLAB_ENCRYPT_KEY;
if (!ENCRYPT_KEY) {
  console.error('错误：必须设置环境变量 GITLAB_ENCRYPT_KEY 才能使用此工具');
  console.error('设置方法：export GITLAB_ENCRYPT_KEY=你的密钥（至少32个字符）');
  process.exit(1);
}

// ============ 工具函数 ============

// 加密
function encrypt(text) {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', Buffer.from(ENCRYPT_KEY.slice(0, 32)), iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

// 解密
function decrypt(text) {
  try {
    const parts = text.split(':');
    const iv = Buffer.from(parts[0], 'hex');
    const encryptedText = parts[1];
    const decipher = crypto.createDecipheriv('aes-256-cbc', Buffer.from(ENCRYPT_KEY.slice(0, 32)), iv);
    let decrypted = decipher.update(encryptedText, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  } catch (e) {
    return null;
  }
}

// 读取用户配置
function loadUsers() {
  if (!fs.existsSync(USERS_FILE)) {
    return {};
  }
  try {
    const encrypted = fs.readFileSync(USERS_FILE, 'utf8');
    const decrypted = decrypt(encrypted);
    return decrypted ? JSON.parse(decrypted) : {};
  } catch (e) {
    return {};
  }
}

// 保存用户配置（加密）
function saveUsers(users) {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
  const encrypted = encrypt(JSON.stringify(users));
  fs.writeFileSync(USERS_FILE, encrypted);
}

// 读取 OAuth 配置（加密存储）
function loadOauthConfig() {
  if (!fs.existsSync(OAUTH_FILE)) {
    return null;
  }
  try {
    const encrypted = fs.readFileSync(OAUTH_FILE, 'utf8');
    const decrypted = decrypt(encrypted);
    return decrypted ? JSON.parse(decrypted) : null;
  } catch (e) {
    return null;
  }
}

// 保存 OAuth 配置（加密）
function saveOauthConfig(config) {
  if (!fs.existsSync(CONFIG_DIR)) {
    fs.mkdirSync(CONFIG_DIR, { recursive: true });
  }
  const encrypted = encrypt(JSON.stringify(config));
  fs.writeFileSync(OAUTH_FILE, encrypted);
}

// API 请求
function request(token, method, endpoint, data = null) {
  return new Promise((resolve, reject) => {
    const gitlabUrl = process.env.GITLAB_URL || 'http://gitlab.example.com';
    const parsedUrl = new url.parse(gitlabUrl + endpoint);
    const isHttps = gitlabUrl.startsWith('https');
    const lib = isHttps ? https : http;

    const options = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (isHttps ? 443 : 80),
      path: parsedUrl.path,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    };

    const req = lib.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          resolve(body);
        }
      });
    });

    req.on('error', reject);
    if (data) {
      req.write(JSON.stringify(data));
    }
    req.end();
  });
}

// ============ 主逻辑 ============

const command = process.argv[2];
const args = process.argv.slice(3);

async function main() {
  switch (command) {
    case 'auth-url':
      // 生成授权链接
      const oauthConfig = loadOauthConfig();
      if (!oauthConfig) {
        console.log('错误：请先配置 OAuth 应用: node index.js config <Application ID> <Secret>');
        process.exit(1);
      }
      const redirectUri = 'http://localhost/callback';
      const authUrl = `${oauthConfig.gitlab_url || 'http://gitlab.example.com'}/oauth/authorize?client_id=${oauthConfig.client_id}&redirect_uri=${redirectUri}&response_type=code&scope=api`;
      console.log(authUrl);
      break;

    case 'config':
      // 配置 OAuth 应用
      const clientId = args[0];
      const clientSecret = args[1];
      const gitlabUrl = args[2] || 'http://gitlab.example.com';
      
      if (!clientId || !clientSecret) {
        console.log('用法: node index.js config <Application ID> <Secret> [GitLab URL]');
        process.exit(1);
      }

      const configData = {
        client_id: clientId,
        client_secret: clientSecret,
        gitlab_url: gitlabUrl
      };
      
      saveOauthConfig(configData);
      console.log('✅ OAuth 配置已保存（加密存储）');
      break;

    case 'handle':
      // 处理用户发来的授权链接或 code
      const userId = args[0]; // 用户ID
      const input = args[1]; // 授权链接或 code
      
      if (!input) {
        console.log('用法: node index.js handle <用户ID> <授权链接或code>');
        console.log('');
        console.log('自动识别处理：');
        console.log('- 如果是完整授权链接，自动提取 code 并换取 token');
        console.log('- 如果是纯 code，直接换取 token');
        console.log('- token 加密保存到本地');
        process.exit(1);
      }

      // 提取 code
      let code = input;
      if (input.includes('code=')) {
        const urlMatch = input.match(/[?&]code=([a-f0-9]+)/i);
        if (urlMatch) {
          code = urlMatch[1];
          console.log('从授权链接中提取到 code');
        }
      }

      // 获取 OAuth 配置
      const oauth = loadOauthConfig();
      if (!oauth) {
        console.log('错误：请先配置 OAuth 应用');
        process.exit(1);
      }

      // 换取 token
      console.log('正在换取 token...');
      const tokenData = await new Promise((resolve, reject) => {
        const postData = new url.URLSearchParams({
          client_id: oauth.client_id,
          client_secret: oauth.client_secret,
          code: code,
          grant_type: 'authorization_code',
          redirect_uri: 'http://localhost/callback'
        }).toString();

        const gitlabUrl = oauth.gitlab_url || 'http://gitlab.example.com';
        const parsedUrl = new url.parse(gitlabUrl + '/oauth/token');
        const isHttps = gitlabUrl.startsWith('https');
        const lib = isHttps ? https : http;

        const options = {
          hostname: parsedUrl.hostname,
          port: parsedUrl.port || (isHttps ? 443 : 80),
          path: parsedUrl.path,
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': Buffer.byteLength(postData)
          }
        };

        const req = lib.request(options, (res) => {
          let body = '';
          res.on('data', chunk => body += chunk);
          res.on('end', () => {
            try {
              resolve(JSON.parse(body));
            } catch (e) {
              reject(e);
            }
          });
        });

        req.on('error', reject);
        req.write(postData);
        req.end();
      });

      if (tokenData.access_token) {
        // 获取用户信息
        const userInfo = await request(tokenData.access_token, 'GET', '/api/v4/user');
        
        console.log('✅ 授权成功！');
        console.log(`用户: ${userInfo.name} (${userInfo.username})`);
        
        // 保存用户 token（加密）
        const users = loadUsers();
        users[userId] = {
          token: tokenData.access_token,
          userId: userId,
          gitlabUser: userInfo.username,
          name: userInfo.name,
          updatedAt: new Date().toISOString()
        };
        saveUsers(users);
        
        console.log(`Token 已加密保存到本地，绑定用户: ${userId}`);
      } else {
        console.log('❌ 授权失败:', tokenData.error_description || tokenData.msg);
      }
      break;

    case 'use':
      // 使用指定用户的 token 执行命令
      const useUserId = args[0];
      const targetCommand = args[1];
      const targetArgs = args.slice(2);
      
      const users = loadUsers();
      const userData = users[useUserId];
      
      if (!userData || !userData.token) {
        console.log(`错误：用户 ${useUserId} 未授权，请先运行: node index.js handle ${useUserId} <授权链接>`);
        process.exit(1);
      }

      const token = userData.token;

      switch (targetCommand) {
        case 'list':
          // 列出仓库
          const projects = await request(token, 'GET', '/api/v4/users/current/projects');
          console.log(`用户 ${userData.name} 的仓库:`);
          (Array.isArray(projects) ? projects : []).forEach(p => {
            console.log(`- ${p.name} (ID: ${p.id})`);
          });
          break;

        case 'project':
          const keyword = targetArgs[0];
          const searchResult = await request(token, 'GET', `/api/v4/projects?search=${keyword}`);
          console.log(`搜索 "${keyword}" 结果:`);
          (Array.isArray(searchResult) ? searchResult : []).forEach(p => {
            console.log(`- ${p.name_with_namespace} (ID: ${p.id})`);
          });
          break;

        case 'merge':
          const projectId = targetArgs[0];
          const branch = targetArgs[1] || 'master';
          
          const commits = await request(token, 'GET', `/api/v4/projects/${projectId}/repository/commits?ref_name=${branch}&per_page=10`);
          const mergeCommit = (Array.isArray(commits) ? commits : []).find(c => c.parent_ids && c.parent_ids.length > 1);
          
          if (!mergeCommit) {
            console.log('未找到合并提交');
            break;
          }

          console.log('='.repeat(50));
          console.log('最后一次合并信息');
          console.log('='.repeat(50));
          console.log(`时间: ${mergeCommit.created_at}`);
          console.log(`作者: ${mergeCommit.author_name}`);
          console.log(`提交: ${mergeCommit.title}`);
          
          const diff = await request(token, 'GET', `/api/v4/projects/${projectId}/repository/commits/${mergeCommit.id}/diff`);
          console.log('变更文件:');
          (Array.isArray(diff) ? diff : []).forEach(f => {
            console.log(`  - ${f.new_path || f.old_path}`);
          });
          break;

        default:
          console.log('用法: node index.js use <用户ID> <命令> [参数]');
          console.log('命令: list, project <关键词>, merge <项目ID> [分支]');
      }
      break;

    case 'users':
      // 列出已授权用户
      const allUsers = loadUsers();
      console.log('已授权用户:');
      Object.keys(allUsers).forEach(uid => {
        const u = allUsers[uid];
        console.log(`- ${uid}: ${u.name} (@${u.gitlabUser}), 更新时间: ${u.updatedAt}`);
      });
      break;

    default:
      console.log(`
GitLab Private v0.5.0 - 支持多用户授权

用法:
  node index.js config <Application ID> <Secret> [GitLab URL]    - 配置 OAuth 应用
  node index.js auth-url                                          - 生成授权链接
  node index.js handle <用户ID> <授权链接或code>                  - 处理授权（核心）
  node index.js use <用户ID> <命令> [参数]                        - 使用用户 token 执行命令
  node index.js users                                             - 列出已授权用户

命令示例:
  node index.js use 曾金国 merge 10954 master
  node index.js use 曾金国 project welfare
  node index.js use 曾金国 list
`);
  }
}

main().catch(console.error);
