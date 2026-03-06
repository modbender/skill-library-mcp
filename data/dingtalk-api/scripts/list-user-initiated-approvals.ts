// 获取用户发起的审批列表
// 用法: ts-node scripts/list-user-initiated-approvals.ts <userId> [--startTime <timestamp>] [--endTime <timestamp>] [--maxResults <max>] [--nextToken <token>] [--debug]
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const { default: dingtalkWorkflow, ListUserStartedProcessInstancesHeaders, ListUserStartedProcessInstancesRequest } = require('@alicloud/dingtalk/workflow_1_0');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');
const { RuntimeOptions } = require('@alicloud/tea-util');

interface Result {
  success: boolean;
  userId: string;
  instances: any[];
  totalCount: number;
  hasMore: boolean;
  nextToken?: string;
}

interface ErrorResult {
  success: false;
  error: {
    code: string;
    message: string;
  };
}

function createConfig(): any {
  const config = new Config({});
  config.protocol = "https";
  config.regionId = "central";
  return config;
}

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

async function listUserInitiatedApprovals(
  accessToken: string,
  userId: string,
  startTime: number | undefined,
  endTime: number | undefined,
  maxResults: number,
  nextToken: string | undefined,
  debug: boolean
): Promise<void> {
  const client = new dingtalkWorkflow(createConfig());

  const headers = new ListUserStartedProcessInstancesHeaders({});
  headers.xAcsDingtalkAccessToken = accessToken;

  const request = new ListUserStartedProcessInstancesRequest({
    userId: userId,
    startTime: startTime,
    endTime: endTime,
    maxResults: maxResults,
    nextToken: nextToken,
  });

  try {
    const response = await client.listUserStartedProcessInstancesWithOptions(
      request,
      headers,
      new RuntimeOptions({})
    );

    if (debug) {
      console.error('\n=== 调试信息 ===');
      console.error('完整响应:', JSON.stringify(response, null, 2));
      console.error('==============\n');
    }

    const instances = response.body?.result?.data || [];
    const result: Result = {
      success: true,
      userId: userId,
      instances: instances,
      totalCount: instances.length,
      hasMore: !!response.body?.result?.nextToken,
      nextToken: response.body?.result?.nextToken,
    };

    console.log(JSON.stringify(result, null, 2));
  } catch (err: any) {
    const errorResult: ErrorResult = {
      success: false,
      error: {
        code: err.code || 'UNKNOWN_ERROR',
        message: err.message || '未知错误',
      }
    };
    console.error(JSON.stringify(errorResult, null, 2));
    process.exit(1);
  }
}

function parseArgs(args: string[]): { userId: string; startTime?: number; endTime?: number; maxResults: number; nextToken?: string; debug: boolean } {
  let userId = '';
  let startTime: number | undefined;
  let endTime: number | undefined;
  let maxResults = 20;
  let nextToken: string | undefined;
  let debug = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--debug') {
      debug = true;
    } else if (arg === '--startTime' && i + 1 < args.length) {
      startTime = parseInt(args[++i], 10);
    } else if (arg === '--endTime' && i + 1 < args.length) {
      endTime = parseInt(args[++i], 10);
    } else if (arg === '--maxResults' && i + 1 < args.length) {
      maxResults = parseInt(args[++i], 10);
    } else if (arg === '--nextToken' && i + 1 < args.length) {
      nextToken = args[++i];
    } else if (!arg.startsWith('--') && !userId) {
      userId = arg;
    }
  }

  return { userId, startTime, endTime, maxResults, nextToken, debug };
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const { userId, startTime, endTime, maxResults, nextToken, debug } = parseArgs(args);

  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'MISSING_CREDENTIALS',
        message: '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET',
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/list-user-initiated-approvals.ts <userId> [--startTime <timestamp>] [--endTime <timestamp>] [--maxResults <max>] [--nextToken <token>] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (!userId) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供用户 ID（userId）',
        usage: 'ts-node scripts/list-user-initiated-approvals.ts <userId> [--startTime <timestamp>] [--endTime <timestamp>] [--maxResults <max>] [--nextToken <token>] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  try {
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在查询用户发起的审批列表...');

    await listUserInitiatedApprovals(accessToken, userId, startTime, endTime, maxResults, nextToken, debug);
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
