#!/usr/bin/env node

import SwaggerAPISkill from './index.js';
import readline from 'readline';

const skill = new SwaggerAPISkill();
let swaggerUrl = null;
let token = null;
let cookies = null;

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function prompt(question) {
  return new Promise(resolve => {
    rl.question(question, resolve);
  });
}

async function main() {
  console.log('\n╔════════════════════════════════════════╗');
  console.log('║     Swagger API Skill CLI 工具         ║');
  console.log('╚════════════════════════════════════════╝\n');

  // 获取 Swagger URL
  swaggerUrl = await prompt('请输入 Swagger API 文档 URL (如: http://localhost:8090/v2/api-docs): ');
  if (!swaggerUrl.trim()) {
    console.error('❌ URL 不能为空');
    rl.close();
    return;
  }

  // 获取 Token（可选）
  const tokenInput = await prompt('请输入认证 Token (可选，按 Enter 跳过): ');
  if (tokenInput.trim()) {
    token = tokenInput.trim();
    console.log('✓ Token 已设置\n');
  } else {
    console.log('✓ 未设置 Token\n');
  }

  // 获取 Cookie（可选，JSON 格式）
  const cookieInput = await prompt('请输入认证 Cookie (JSON 格式，可选，按 Enter 跳过): ');
  if (cookieInput.trim()) {
    try {
      const parsed = JSON.parse(cookieInput);
      const cookieResult = skill.setAuthCookies(parsed);
      if (!cookieResult.success) {
        console.error(`❌ Cookie 设置失败: ${cookieResult.message}`);
        rl.close();
        return;
      }
      cookies = parsed;
      console.log('✓ Cookie 已设置\n');
    } catch (e) {
      console.error('❌ Cookie JSON 格式错误');
      rl.close();
      return;
    }
  } else if (!token) {
    console.log('✓ 无需认证\n');
  }

  // 加载 Swagger 规范
  console.log('正在加载 Swagger 规范...');
  const fetchOptions = {};
  if (token) {
    fetchOptions.token = token;
    fetchOptions.tokenOptions = {
      tokenType: 'Bearer',
      headerName: 'Authorization'
    };
  }
  if (cookies) {
    fetchOptions.cookies = cookies;
  }
  const specResult = await skill.fetchSwaggerSpec(swaggerUrl, fetchOptions);

  if (!specResult.success) {
    console.error('❌ 加载失败:', specResult.error);
    rl.close();
    return;
  }

  console.log(`✓ 加载成功，共找到 ${specResult.apiCount} 个接口\n`);

  // 交互菜单
  await showMenu();

  rl.close();
}

async function showMenu() {
  while (true) {
    console.log('\n═══════════════════════════════════════');
    console.log('请选择操作:');
    console.log('1. 获取所有接口列表');
    console.log('2. 搜索接口');
    console.log('3. 获取接口详情');
    console.log('4. 调用接口');
    console.log('5. 刷新会话');
    console.log('6. 退出');
    console.log('═══════════════════════════════════════');

    const choice = await prompt('\n请输入选项 (1-6): ');

    switch (choice.trim()) {
      case '1':
        await listAllAPIs();
        break;
      case '2':
        await searchAPIs();
        break;
      case '3':
        await getAPIDetail();
        break;
      case '4':
        await callAPI();
        break;
      case '5':
        await refreshSession();
        break;
      case '6':
        console.log('\n👋 再见！');
        return;
      default:
        console.log('❌ 无效的选项');
    }
  }
}

async function listAllAPIs() {
  console.log('\n📋 所有接口列表:\n');
  const allAPIs = skill.getAllAPIs();
  allAPIs.apis.forEach((api, index) => {
    console.log(`${index + 1}. [${api.method.toUpperCase()}] ${api.path}`);
    if (api.summary) console.log(`   📝 ${api.summary}`);
  });
  console.log(`\n共 ${allAPIs.total} 个接口`);
}

async function searchAPIs() {
  const query = await prompt('\n请输入搜索关键词: ');
  if (!query.trim()) {
    console.log('❌ 关键词不能为空');
    return;
  }

  const results = skill.searchAPI(query);
  if (results.matchCount === 0) {
    console.log(`\n❌ 未找到匹配 "${query}" 的接口`);
    return;
  }

  console.log(`\n🔍 搜索结果 (共 ${results.matchCount} 个):\n`);
  results.results.forEach((result, index) => {
    console.log(`${index + 1}. [${result.method.toUpperCase()}] ${result.path}`);
    console.log(`   📝 ${result.summary || result.description || '无描述'}`);
    console.log(`   匹配度: ${(result.score * 100).toFixed(2)}%\n`);
  });
}

async function getAPIDetail() {
  const path = await prompt('\n请输入接口路径 (如: /users/{id}): ');
  const method = await prompt('请输入 HTTP 方法 (GET/POST/PUT/DELETE 等): ');

  if (!path.trim() || !method.trim()) {
    console.log('❌ 路径和方法不能为空');
    return;
  }

  const detail = skill.getAPIDetail(path.trim(), method.trim().toUpperCase());
  if (!detail.success) {
    console.log(`❌ ${detail.error}`);
    return;
  }

  console.log('\n📄 接口详情:\n');
  console.log(JSON.stringify(detail.detail, null, 2));
}

async function callAPI() {
  const path = await prompt('\n请输入接口路径: ');
  const method = await prompt('请输入 HTTP 方法: ');

  if (!path.trim() || !method.trim()) {
    console.log('❌ 路径和方法不能为空');
    return;
  }

  const queryStr = await prompt('请输入查询参数 (JSON 格式，可选): ');
  const bodyStr = await prompt('请输入请求体 (JSON 格式，可选): ');

  const params = {};
  if (queryStr.trim()) {
    try {
      params.query = JSON.parse(queryStr);
    } catch (e) {
      console.log('❌ 查询参数 JSON 格式错误');
      return;
    }
  }
  if (bodyStr.trim()) {
    try {
      params.body = JSON.parse(bodyStr);
    } catch (e) {
      console.log('❌ 请求体 JSON 格式错误');
      return;
    }
  }

  console.log('\n正在调用接口...');
  const result = await skill.callAPI(path.trim(), method.trim().toUpperCase(), params);

  if (result.success) {
    console.log('\n✓ 调用成功\n');
    console.log('响应数据:');
    console.log(JSON.stringify(result.data, null, 2));
  } else {
    console.log(`\n❌ 调用失败: ${result.error}`);
  }
}

async function refreshSession() {
  const result = skill.refreshSession();
  console.log(`\n✓ ${result.message}`);
  console.log(`新会话ID: ${skill.getSessionId()}`);

  // 重新加载 Swagger 规范
  console.log('\n正在重新加载 Swagger 规范...');
  const fetchOptions = {};
  if (token) {
    fetchOptions.token = token;
    fetchOptions.tokenOptions = {
      tokenType: 'Bearer',
      headerName: 'Authorization'
    };
  }
  if (cookies) {
    fetchOptions.cookies = cookies;
  }
  const specResult = await skill.fetchSwaggerSpec(swaggerUrl, fetchOptions);

  if (specResult.success) {
    console.log(`✓ 重新加载成功，共 ${specResult.apiCount} 个接口`);
  } else {
    console.log(`❌ 重新加载失败: ${specResult.error}`);
  }
}

main().catch(console.error);
