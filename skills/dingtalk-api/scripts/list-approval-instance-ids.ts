// 获取审批实例 ID 列表
// 用法: ts-node scripts/list-approval-instance-ids.ts <processCode> --startTime <timestamp> --endTime <timestamp> [--size <size>] [--nextToken <token>] [--debug]
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const { default: dingtalkWorkflow, ListProcessInstanceIdsHeaders, ListProcessInstanceIdsRequest } = require('@alicloud/dingtalk/workflow_1_0');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');
const { RuntimeOptions } = require('@alicloud/tea-util');

interface Result {
  success: boolean;
  processCode: string;
  instanceIds: string[];
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

async function listApprovalInstanceIds(
  accessToken: string,
  processCode: string,
  startTime: number,
  endTime: number,
  size: number,
  nextToken: string | undefined,
  debug: boolean
): Promise<void> {
  const client = new dingtalkWorkflow(createConfig());

  const headers = new ListProcessInstanceIdsHeaders({});
  headers.xAcsDingtalkAccessToken = accessToken;

  const request = new ListProcessInstanceIdsRequest({
    processCode: processCode,
    startTime: startTime,
    endTime: endTime,
    size: size,
    nextToken: nextToken,
  });

  try {
    const response = await client.listProcessInstanceIdsWithOptions(
      request,
      headers,
      new RuntimeOptions({})
    );

    if (debug) {
      console.error('\n=== 调试信息 ===');
      console.error('完整响应:', JSON.stringify(response, null, 2));
      console.error('==============\n');
    }

    const instanceIds = response.body?.result?.list || [];
    const result: Result = {
      success: true,
      processCode: processCode,
      instanceIds: instanceIds,
      totalCount: instanceIds.length,
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

function parseArgs(args: string[]): { processCode: string; startTime: number; endTime: number; size: number; nextToken?: string; debug: boolean } {
  let processCode = '';
  let startTime = 0;
  let endTime = 0;
  let size = 20;
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
    } else if (arg === '--size' && i + 1 < args.length) {
      size = parseInt(args[++i], 10);
    } else if (arg === '--nextToken' && i + 1 < args.length) {
      nextToken = args[++i];
    } else if (!arg.startsWith('--') && !processCode) {
      processCode = arg;
    }
  }

  return { processCode, startTime, endTime, size, nextToken, debug };
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const { processCode, startTime, endTime, size, nextToken, debug } = parseArgs(args);

  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'MISSING_CREDENTIALS',
        message: '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET',
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/list-approval-instance-ids.ts <processCode> --startTime <timestamp> --endTime <timestamp> [--size <size>] [--nextToken <token>] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (!processCode) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供审批模板 processCode',
        usage: 'ts-node scripts/list-approval-instance-ids.ts <processCode> --startTime <timestamp> --endTime <timestamp> [--size <size>] [--nextToken <token>] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (!startTime || !endTime) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供 startTime 和 endTime（Unix 时间戳，毫秒）',
        usage: 'ts-node scripts/list-approval-instance-ids.ts <processCode> --startTime <timestamp> --endTime <timestamp> [--size <size>] [--nextToken <token>] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  try {
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在查询审批实例 ID 列表...');

    await listApprovalInstanceIds(accessToken, processCode, startTime, endTime, size, nextToken, debug);
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
