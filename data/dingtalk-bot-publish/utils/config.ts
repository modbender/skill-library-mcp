/**
 * 钉钉API配置工具
 * 提供环境变量验证和配置管理
 */

export interface DingTalkConfig {
  appKey: string;
  appSecret: string;
}

/**
 * 获取钉钉应用配置
 * @returns 配置对象
 * @throws Error 如果缺少必要的环境变量
 */
export function getDingTalkConfig(): DingTalkConfig {
  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    throw new Error(
      '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET'
    );
  }

  return {
    appKey,
    appSecret
  };
}

/**
 * 验证必需的参数
 * @param args 参数数组
 * @param minCount 最小参数数量
 * @param usage 使用说明
 * @throws Error 如果参数不足
 */
export function validateRequiredArgs(
  args: string[],
  minCount: number,
  usage: string
): void {
  if (args.length < minCount) {
    throw new Error(`参数错误：需要至少 ${minCount} 个参数\n用法: ${usage}`);
  }
}