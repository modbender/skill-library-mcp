// 钉钉部门搜索脚本
// 用法: ts-node scripts/search-department.ts <搜索关键词> [--debug]
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const { default: dingtalkContact, SearchDepartmentHeaders, SearchDepartmentRequest } = require('@alicloud/dingtalk/contact_1_0');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');
const { RuntimeOptions } = require('@alicloud/tea-util');

interface SearchResult {
  success: boolean;
  keyword: string;
  totalCount: number;
  hasMore: boolean;
  departmentIds: number[];
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
 * 搜索部门
 * @param accessToken Access Token
 * @param keyword 搜索关键词（部门名称）
 * @param debug 是否开启调试模式
 */
async function searchDepartment(accessToken: string, keyword: string, debug: boolean = false): Promise<void> {
  const client = new dingtalkContact(createConfig());

  const headers = new SearchDepartmentHeaders({});
  headers.xAcsDingtalkAccessToken = accessToken;

  const request = new SearchDepartmentRequest({
    queryWord: keyword,
    offset: 0,
    size: 20,
  });

  try {
    const response = await client.searchDepartmentWithOptions(
      request,
      headers,
      new RuntimeOptions({})
    );

    // 调试模式：输出完整响应
    if (debug) {
      console.error('\n=== 调试信息 ===');
      console.error('完整响应:', JSON.stringify(response, null, 2));
      console.error('响应 body:', JSON.stringify(response.body, null, 2));
      console.error('==============\n');
    }

    // 格式化输出结果
    const departmentIds = response.body?.list || [];
    const result: SearchResult = {
      success: true,
      keyword: keyword,
      totalCount: response.body?.totalCount || 0,
      hasMore: response.body?.hasMore || false,
      departmentIds: departmentIds,
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

  // 检查是否有调试参数
  const debug = args.includes('--debug');
  const filteredArgs = args.filter(arg => arg !== '--debug');

  // 从环境变量读取配置
  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'MISSING_CREDENTIALS',
        message: '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET',
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/search-department.ts "<搜索关键词>" [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (filteredArgs.length < 1) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供搜索关键词（部门名称）',
        usage: 'ts-node scripts/search-department.ts "<搜索关键词>" [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  const keyword = filteredArgs[0];

  try {
    // 自动获取 access_token
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在搜索部门...');

    // 使用获取到的 token 搜索部门
    await searchDepartment(accessToken, keyword, debug);
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
