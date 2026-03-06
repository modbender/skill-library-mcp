#!/usr/bin/env node
/**
 * GitHub Repository Detail Fetcher
 * 获取单个仓库的详细信息
 */

import { execSync } from 'child_process';

const GITHUB_API = 'https://api.github.com/repos';

// 解析参数
function parseArgs() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    return null;
  }
  return args[0]; // repo full name, e.g., "microsoft/autogen"
}

// 调用 GitHub API
async function fetchRepoDetails(repoFullName) {
  const url = `${GITHUB_API}/${repoFullName}`;
  
  const headers = [
    '-H "Accept: application/vnd.github.v3+json"',
    '-H "User-Agent: GitHub-Research-Skill"'
  ];
  
  if (process.env.GITHUB_TOKEN) {
    headers.push(`-H "Authorization: token ${process.env.GITHUB_TOKEN}"`);
  }
  
  const cmd = `curl -s ${headers.join(' ')} "${url}"`;
  
  try {
    const result = execSync(cmd, { encoding: 'utf-8', timeout: 30000 });
    return JSON.parse(result);
  } catch (error) {
    console.error('Error fetching repo details:', error.message);
    return null;
  }
}

// 获取贡献者统计
async function fetchContributors(repoFullName) {
  const url = `${GITHUB_API}/${repoFullName}/contributors?per_page=10`;
  
  const headers = [
    '-H "Accept: application/vnd.github.v3+json"',
    '-H "User-Agent: GitHub-Research-Skill"'
  ];
  
  if (process.env.GITHUB_TOKEN) {
    headers.push(`-H "Authorization: token ${process.env.GITHUB_TOKEN}"`);
  }
  
  const cmd = `curl -s ${headers.join(' ')} "${url}"`;
  
  try {
    const result = execSync(cmd, { encoding: 'utf-8', timeout: 30000 });
    return JSON.parse(result);
  } catch (error) {
    return [];
  }
}

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN');
}

// 格式化数字
function formatNumber(num) {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return num.toString();
}

// 计算活跃度
function getActivityLevel(pushedAt) {
  const days = Math.floor((new Date() - new Date(pushedAt)) / (1000 * 60 * 60 * 24));
  if (days <= 7) return '🟢 非常活跃';
  if (days <= 30) return '🟡 活跃';
  if (days <= 90) return '🟠 一般';
  return '🔴 不活跃';
}

// 生成 Markdown 报告
function generateReport(repo, contributors) {
  let output = `## 📋 项目详情: ${repo.full_name}\n\n`;
  
  // 基本信息
  output += `**名称**: ${repo.name}\n`;
  output += `**描述**: ${repo.description || '无描述'}\n`;
  output += `**🏷️ 标签**: ${repo.topics?.join(', ') || '无标签'}\n\n`;
  
  // 数据统计
  output += `### 📈 数据统计\n`;
  output += `- ⭐ **Stars**: ${formatNumber(repo.stargazers_count)}\n`;
  output += `- 🍴 **Forks**: ${formatNumber(repo.forks_count)}\n`;
  output += `- 👁️ **Watchers**: ${formatNumber(repo.watchers_count)}\n`;
  output += `- 🐛 **Open Issues**: ${repo.open_issues_count}\n`;
  output += `- 🔀 **Open PRs**: ${repo.pull_requests_count || 'N/A'}\n\n`;
  
  // 代码信息
  output += `### 💻 代码信息\n`;
  output += `- **主要语言**: ${repo.language || 'N/A'}\n`;
  output += `- **许可证**: ${repo.license?.name || 'N/A'}\n`;
  output += `- **默认分支**: ${repo.default_branch}\n`;
  output += `- **仓库大小**: ${Math.round(repo.size / 1024)} MB\n\n`;
  
  // 活跃度
  output += `### 📅 活跃度\n`;
  output += `- **最后提交**: ${formatDate(repo.pushed_at)} (${getActivityLevel(repo.pushed_at)})\n`;
  output += `- **创建时间**: ${formatDate(repo.created_at)}\n`;
  output += `- **更新时间**: ${formatDate(repo.updated_at)}\n`;
  
  if (contributors && contributors.length > 0) {
    output += `- **主要贡献者**: ${contributors.slice(0, 5).map(c => c.login).join(', ')}\n`;
  }
  output += '\n';
  
  // 链接
  output += `### 🔗 链接\n`;
  output += `- **仓库**: ${repo.html_url}\n`;
  if (repo.homepage) {
    output += `- **主页**: ${repo.homepage}\n`;
  }
  output += `- **Issues**: ${repo.html_url}/issues\n`;
  output += `- **Pull Requests**: ${repo.html_url}/pulls\n`;
  
  return output;
}

// 主函数
async function main() {
  const repoFullName = parseArgs();
  
  if (!repoFullName) {
    console.log('用法: node repo-detail.mjs <owner/repo>');
    console.log('');
    console.log('示例:');
    console.log('  node repo-detail.mjs microsoft/autogen');
    console.log('  node repo-detail.mjs langchain-ai/langchain');
    process.exit(1);
  }
  
  console.error(`🔍 获取仓库详情: ${repoFullName}\n`);
  
  const [owner, repo] = repoFullName.split('/');
  if (!owner || !repo) {
    console.error('❌ 格式错误，请使用 "owner/repo" 格式');
    process.exit(1);
  }
  
  const repoData = await fetchRepoDetails(repoFullName);
  
  if (!repoData || repoData.message === 'Not Found') {
    console.error('❌ 仓库不存在或无法访问');
    process.exit(1);
  }
  
  console.error('📊 获取贡献者信息...');
  const contributors = await fetchContributors(repoFullName);
  
  console.error('✅ 完成\n');
  
  const report = generateReport(repoData, contributors);
  console.log(report);
}

main().catch(err => {
  console.error('错误:', err);
  process.exit(1);
});
