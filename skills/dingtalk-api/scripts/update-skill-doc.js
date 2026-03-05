#!/usr/bin/env node
/**
 * 自动更新 SKILL.md 脚本
 * 根据 scripts/ 目录下的代码变更自动同步更新文档
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = process.cwd();
const SCRIPTS_DIR = path.join(PROJECT_ROOT, 'scripts');
const SKILL_MD_PATH = path.join(PROJECT_ROOT, 'SKILL.md');

/**
 * 解析 TypeScript 文件，提取函数信息
 */
function parseScript(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const fileName = path.basename(filePath);

  // 提取 JSDoc 注释和函数信息
  const functionRegex = /\/\*\*\s*([\s\S]*?)\s*\*\/\s*(?:async\s+)?function\s+(\w+)|\/\*\*\s*([\s\S]*?)\s*\*\/\s*static\s+async\s+(\w+)/g;
  const functions = [];
  let match;

  while ((match = functionRegex.exec(content)) !== null) {
    const docComment = match[1] || match[3] || '';
    const funcName = match[2] || match[4] || '';

    // 解析 JSDoc
    const description = docComment.match(/@remarks\s+([\s\S]*?)(?=\s*@|\*\/)/)?.[1]?.trim() ||
                       docComment.match(/\*\s+([^@\n].*)/)?.[1]?.trim() ||
                       '';

    const params = [];
    const paramRegex = /@param\s+(\w+)\s+(.+)/g;
    let paramMatch;
    while ((paramMatch = paramRegex.exec(docComment)) !== null) {
      params.push({
        name: paramMatch[1],
        description: paramMatch[2].trim()
      });
    }

    if (funcName) {
      functions.push({
        name: funcName,
        description,
        params,
        fileName
      });
    }
  }

  // 提取用法注释
  const usageMatch = content.match(/\/\/\s*用法:\s*(.+)/);
  const usage = usageMatch ? usageMatch[1].trim() : '';

  // 提取接口定义（用于输出格式）
  const interfaceMatches = content.match(/interface\s+(\w+)\s*{[^}]+}/g) || [];
  const interfaces = interfaceMatches.map(iface => iface.trim());

  return {
    fileName,
    usage,
    functions,
    interfaces
  };
}

/**
 * 生成 SKILL.md 内容（不包含任何敏感信息）
 */
function generateSkillMd(scriptsInfo) {
  // 使用占位符的输出示例，不包含真实数据
  const outputExample = `{
  "success": true,
  "keyword": "<搜索关键词>",
  "totalCount": 3,
  "hasMore": false,
  "userIds": [
    "123456789",
    "987654321",
    "456789123"
  ]
}`;

  const errorExample = `{
  "success": false,
  "error": {
    "code": "MISSING_CREDENTIALS",
    "message": "缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET"
  }
}`;

  return `---
name: dingtalk-api
description: 调用钉钉开放平台API，实现用户搜索、部门管理等功能。从系统环境变量读取应用凭证。Use when needing to interact with DingTalk API, search users by name, get user details, or manage organizational contacts.
---

# DingTalk API Skill

用于调用钉钉开放平台API的技能，支持用户搜索、部门查询等功能。

## 前置要求

- 钉钉应用已创建并拥有以下权限：
  - \`Contact.User.Read\` - 读取通讯录成员信息
  - \`openapi\` - 基础接口调用权限
- 已获取应用的 **AppKey** 和 **AppSecret**
- 已设置环境变量 \`DINGTALK_APP_KEY\` 和 \`DINGTALK_APP_SECRET\`

## 环境变量配置

在使用脚本前，需要导出以下环境变量：

\`\`\`bash
export DINGTALK_APP_KEY="<your-app-key>"
export DINGTALK_APP_SECRET="<your-app-secret>"
\`\`\`

或者在一行中执行：

\`\`\`bash
export DINGTALK_APP_KEY="<your-app-key>" && export DINGTALK_APP_SECRET="<your-app-secret>" && npx ts-node scripts/search-user.ts "搜索关键词"
\`\`\`

## 功能列表

### 1. 搜索用户 (searchUser)

根据姓名搜索用户，返回匹配的 UserId 列表。脚本会自动获取 access_token。

**使用方式:**

\`\`\`bash
cd ~/Data/www/dingtalk-api
export DINGTALK_APP_KEY="<your-app-key>"
export DINGTALK_APP_SECRET="<your-app-secret>"
npx ts-node scripts/search-user.ts "<搜索关键词>"
\`\`\`

**示例:**

\`\`\`bash
export DINGTALK_APP_KEY="<your-app-key>"
export DINGTALK_APP_SECRET="<your-app-secret>"
npx ts-node scripts/search-user.ts "张三"
\`\`\`

**输出:**

\`\`\`json
${outputExample}
\`\`\`

> **注意:** 钉钉搜索用户 API 返回的是匹配用户的 **userid 列表**。

**错误输出:**

\`\`\`json
${errorExample}
\`\`\`

## 开发指南

### 自动更新 SKILL.md

修改代码后，运行以下命令自动更新 SKILL.md：

\`\`\`bash
npm run update-skill
\`\`\`

### 安装 Git Hooks（推荐）

安装 post-commit hook，每次 commit 后自动更新 SKILL.md：

\`\`\`bash
npm run setup-hooks
\`\`\`

安装后，每次 \`git commit\` 会自动：
1. 解析 \`scripts/\` 目录下的代码变更
2. 自动更新 SKILL.md
3. 将更新后的 SKILL.md 追加到当前 commit

### 手动更新

如果不想安装 hooks，可以在 commit 前手动运行：

\`\`\`bash
npm run precommit
\`\`\`

## 技术说明

本技能基于钉钉开放平台官方 SDK (\`@alicloud/dingtalk\`) 实现，使用 TypeScript 编写。

### 核心依赖

- \`@alicloud/dingtalk\` - 钉钉官方 SDK
- \`@alicloud/tea-util\` - 阿里云 Tea 工具库
- \`@alicloud/openapi-client\` - OpenAPI 客户端

### 认证流程

1. 从系统环境变量读取 \`DINGTALK_APP_KEY\` 和 \`DINGTALK_APP_SECRET\`
2. 调用 \`oauth2_1_0.getAccessToken\` 接口获取 access_token
3. 使用获取到的 access_token 调用业务接口

### API 文档参考

- [钉钉开放平台 - 获取访问凭证](https://open.dingtalk.com/document/isvapp-server/obtain-the-access_token-of-an-internal-app)
- [钉钉开放平台 - 搜索用户](https://open.dingtalk.com/document/isvapp-server/search-for-users)

---
*本文档由 scripts/update-skill-doc.js 自动维护*
`;
}

/**
 * 主函数
 */
function main() {
  // 检查 scripts 目录是否存在
  if (!fs.existsSync(SCRIPTS_DIR)) {
    console.error('错误: scripts/ 目录不存在');
    process.exit(1);
  }

  // 读取所有 TypeScript 文件
  const scriptFiles = fs.readdirSync(SCRIPTS_DIR)
    .filter(f => f.endsWith('.ts'))
    .map(f => path.join(SCRIPTS_DIR, f));

  if (scriptFiles.length === 0) {
    console.error('错误: scripts/ 目录下没有找到 TypeScript 文件');
    process.exit(1);
  }

  // 解析所有脚本
  const scriptsInfo = scriptFiles.map(parseScript);

  // 生成 SKILL.md
  const skillMdContent = generateSkillMd(scriptsInfo);

  // 写入文件
  fs.writeFileSync(SKILL_MD_PATH, skillMdContent, 'utf-8');

  console.log('✅ SKILL.md 已更新');
  console.log(`   解析了 ${scriptFiles.length} 个脚本文件:`);
  scriptFiles.forEach(f => console.log(`   - ${path.basename(f)}`));
}

main();
