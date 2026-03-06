#!/usr/bin/env node

/**
 * Uninstall Command - 卸载命令处理
 * 
 * 处理技能卸载请求，包含二次确认逻辑
 * 
 * @version 1.0.0
 * @author Neo（宇宙神经系统）
 */

const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * 执行卸载（用户确认后）
 */
async function executeUninstall(skillSlug, stateFile) {
  return new Promise((resolve, reject) => {
    exec(`clawhub uninstall ${skillSlug}`, { encoding: 'utf8', timeout: 60000 }, (error, stdout, stderr) => {
      if (error) {
        reject({ error: error.message, stderr });
      } else {
        // 清理状态缓存
        try {
          if (fs.existsSync(stateFile)) {
            const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
            if (state[skillSlug]) {
              delete state[skillSlug];
              fs.writeFileSync(stateFile, JSON.stringify(state, null, 2), 'utf8');
            }
          }
        } catch (e) {
          console.error('清理状态缓存失败:', e.message);
        }
        
        // 拦截 raw 输出，返回简洁的自然语言
        resolve({
          success: true,
          message: `✅ ${skillSlug} 已卸载成功。`
        });
      }
    });
  });
}

/**
 * 生成卸载确认信息
 */
function generateConfirmMessage(skillName) {
  return `⚠️ 确定要卸载 ${skillName} 吗？\n\n卸载后：\n- 技能文件将被删除\n- 配置将丢失\n- 需要重新安装才能使用\n\n这个操作不可逆，确定要继续吗？（回复"确定"或"取消"）`;
}

module.exports = {
  executeUninstall,
  generateConfirmMessage
};
