/**
 * 钉钉推送工具 - 可被其他 Skill 导入使用
 * 
 * 用法:
 *   import { dingtalkPush } from './skills/dingtalk-push/tool.js';
 *   
 *   await dingtalkPush({ message: "任务完成", type: "success" });
 */

import { sendDingTalkMessage } from './send.js';

/**
 * 发送钉钉消息的便捷函数
 * @param {Object} options - 消息选项
 * @param {string} options.message - 消息内容
 * @param {string} [options.title] - 标题
 * @param {string} [options.type='info'] - 类型: info/success/warning/error
 * @param {string[]} [options.atMobiles] - @手机号列表
 * @param {boolean} [options.isAtAll=false] - @所有人
 * @returns {Promise<Object>}
 */
export async function dingtalkPush(options) {
  return sendDingTalkMessage(options);
}

/**
 * 发送成功消息
 */
export async function dingtalkSuccess(message, title = '成功') {
  return sendDingTalkMessage({ message, title, type: 'success' });
}

/**
 * 发送警告消息
 */
export async function dingtalkWarning(message, title = '警告') {
  return sendDingTalkMessage({ message, title, type: 'warning' });
}

/**
 * 发送错误消息
 */
export async function dingtalkError(message, title = '错误') {
  return sendDingTalkMessage({ message, title, type: 'error' });
}

/**
 * 发送普通通知
 */
export async function dingtalkNotify(message, title = '通知') {
  return sendDingTalkMessage({ message, title, type: 'info' });
}

export default {
  dingtalkPush,
  dingtalkSuccess,
  dingtalkWarning,
  dingtalkError,
  dingtalkNotify
};
