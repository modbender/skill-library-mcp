// 钉钉API认证工具
// 提供统一的access_token获取和管理

import { Config } from '@alicloud/openapi-client';
import { GetAccessTokenRequest } from '@alicloud/dingtalk/oauth2_1_0';

/**
 * 创建钉钉客户端配置
 * @returns Config 实例
 */
export function createConfig(): any {
  const config = new Config({});
  config.protocol = "https";
  config.regionId = "central";
  return config;
}

/**
 * 获取 Access Token
 * @param appKey 应用 Key
 * @param appSecret 应用 Secret
 * @returns Access Token
 */
export async function getAccessToken(appKey: string, appSecret: string): Promise<string> {
  const config = createConfig();
  const client = new (require('@alicloud/dingtalk/oauth2_1_0').default)(config);

  const request = new GetAccessTokenRequest({
    appKey: appKey,
    appSecret: appSecret,
  });

  try {
    const response = await client.getAccessToken(request);
    const accessToken = response.body?.accessToken;

    if (!accessToken) {
      throw new Error('获取 access_token 失败：响应中未包含 token');
    }

    return accessToken;
  } catch (err: any) {
    throw new Error(`获取 access_token 失败: ${err.message || err}`);
  }
}

/**
 * 从环境变量获取钉钉应用凭证
 * @returns 包含appKey和appSecret的对象
 */
export function getDingTalkCredentials(): { appKey: string; appSecret: string } {
  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    throw new Error('缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET');
  }

  return { appKey, appSecret };
}