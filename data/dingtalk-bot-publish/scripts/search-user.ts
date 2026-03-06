// 钉钉用户搜索脚本
// 用法: ts-node scripts/search-user.ts <搜索关键词>
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const { default: dingtalkContact, SearchUserHeaders, SearchUserRequest } = require('@alicloud/dingtalk/contact_1_0');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');
const { RuntimeOptions } = require('@alicloud/tea-util');

interface SearchResult {
  success: boolean;
  keyword: string;
  totalCount: number;
  hasMore: boolean;
  userIds: string[];
}

interface ErrorResult {
  success: false;
  keyword: string;
  error: {
    code: string;
    message: string;
    description: string | null;
    requestId: string | null;
  };
}

/**
 * 创建钉钉客户端配置
 * @returns Config 实例
 */
function createConfig(): any {
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
async function getAccessToken(appKey: string, appSecret: string): Promise<string> {
  const config = createConfig();
  const client = new dingtalkOauth2_1_0(config);

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
 * 搜索用户
 * @param accessToken Access Token
 * @param keyword 搜索关键词（姓名）
 */
async function searchUser(accessToken: string, keyword: string): Promise<void> {
  const client = new dingtalkContact(createConfig());

  const headers = new SearchUserHeaders({});
  headers.xAcsDingtalkAccessToken = accessToken;

  const request = new SearchUserRequest({
    queryWord: keyword,
    offset: 0,
    size: 20,
  });

  try {
    const response = await client.searchUserWithOptions(
      request,
      headers,
      new RuntimeOptions({})
    );

    // 格式化输出结果
    const userIds = response.body?.list || [];
    const result: SearchResult = {
      success: true,
      keyword: keyword,
      totalCount: response.body?.totalCount || 0,
      hasMore: response.body?.hasMore || false,
      userIds: userIds,
    };

    console.log(JSON.stringify(result, null, 2));
  } catch (err: any) {
    const errorResult: ErrorResult = {
      success: false,
      keyword: keyword,
      error: {
        code: err.code || 'UNKNOWN_ERROR',
        message: err.message || '未知错误',
        description: err.description || null,
        requestId: err.requestId || null,
      }
    };
    console.error(JSON.stringify(errorResult, null, 2));
    process.exit(1);
  }
}

// 主函数
async function main(): Promise<void> {
  const args = process.argv.slice(2);

  // 从环境变量读取配置
  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'MISSING_CREDENTIALS',
        message: '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET',
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/search-user.ts "<搜索关键词>"'
      }
    }, null, 2));
    process.exit(1);
  }

  if (args.length < 1) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供搜索关键词',
        usage: 'ts-node scripts/search-user.ts "<搜索关键词>"'
      }
    }, null, 2));
    process.exit(1);
  }

  const keyword = args[0];

  try {
    // 自动获取 access_token
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在搜索用户...');
    
    // 使用获取到的 token 搜索用户
    await searchUser(accessToken, keyword);
  } catch (err: any) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'AUTH_FAILED',
        message: err.message || '认证失败',
      }
    }, null, 2));
    process.exit(1);
  }
}

main();
