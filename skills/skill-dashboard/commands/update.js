#!/usr/bin/env node

/**
 * Update Command - 更新命令处理
 * 
 * 处理技能更新请求，包含二次确认逻辑
 * 
 * @version 1.0.0
 * @author Neo（宇宙神经系统）
 */

const { exec } = require('child_process');

/**
 * 检查技能更新
 */
async function checkUpdate(skillSlug) {
  return new Promise((resolve, reject) => {
    exec(`clawhub inspect ${skillSlug} --json`, { encoding: 'utf8', timeout: 30000 }, (error, stdout, stderr) => {
      if (error) {
        reject({ error: error.message, stderr });
      } else {
        try {
          const remote = JSON.parse(stdout.trim());
          resolve(remote);
        } catch (e) {
          reject({ error: '解析远程版本失败', stderr });
        }
      }
    });
  });
}

/**
 * 执行更新（用户确认后）
 */
async function executeUpdate(skillSlug) {
  return new Promise((resolve, reject) => {
    exec(`clawhub update ${skillSlug}`, { encoding: 'utf8', timeout: 60000 }, (error, stdout, stderr) => {
      if (error) {
        reject({ error: error.message, stderr });
      } else {
        // 拦截 raw 输出，返回简洁的自然语言
        resolve({
          success: true,
          message: `✅ ${skillSlug} 已更新成功！\n\n新版本已安装，可以立即使用。`
        });
      }
    });
  });
}

/**
 * 生成更新确认信息
 */
function generateConfirmMessage(skillName, currentVersion, newVersion, changelog) {
  return `检测到 ${skillName} 有新版本 v${newVersion}（当前 v${currentVersion}）\n\n更新内容：\n${changelog || '版本更新'}\n\n确定要更新到 v${newVersion} 吗？（回复"确定"或"取消"）`;
}

module.exports = {
  checkUpdate,
  executeUpdate,
  generateConfirmMessage
};
