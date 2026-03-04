#!/usr/bin/env node

/**
 * Toggle Command - 启用/禁用命令处理
 * 
 * 处理技能启用/禁用请求
 * 
 * @version 1.0.0
 * @author Neo（宇宙神经系统）
 */

const fs = require('fs');
const path = require('path');

/**
 * 切换技能状态
 */
async function toggleSkill(skillSlug, enable, stateFile) {
  try {
    let state = {};
    
    // 加载状态
    if (fs.existsSync(stateFile)) {
      state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
    }
    
    // 初始化技能状态
    if (!state[skillSlug]) {
      state[skillSlug] = {};
    }
    
    // 更新状态
    state[skillSlug].enabled = enable;
    state[skillSlug].lastUsed = new Date().toISOString();
    state[skillSlug].lastModified = new Date().toISOString();
    
    // 保存状态
    fs.writeFileSync(stateFile, JSON.stringify(state, null, 2), 'utf8');
    
    const action = enable ? '启用' : '禁用';
    return {
      success: true,
      message: `✅ ${skillSlug} 已${action}。`
    };
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 获取技能状态
 */
function getSkillState(skillSlug, stateFile) {
  try {
    if (fs.existsSync(stateFile)) {
      const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
      return state[skillSlug] || { enabled: true };
    }
    return { enabled: true };
  } catch (error) {
    return { enabled: true, error: error.message };
  }
}

module.exports = {
  toggleSkill,
  getSkillState
};
