// 获取审批实例详情
// 用法: ts-node scripts/get-approval-instance.ts <instanceId> [--debug]
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const { default: dingtalkWorkflow, GetProcessInstanceHeaders, GetProcessInstanceRequest } = require('@alicloud/dingtalk/workflow_1_0');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');
const { RuntimeOptions } = require('@alicloud/tea-util');

interface Result {
  success: boolean;
  instanceId: string;
  instance: {
    processInstanceId: string;
    title?: string;
    createTimeGMT?: string;
    finishTimeGMT?: string;
    originatorUserId?: string;
    originatorDeptId?: string;
    status?: string;
    processCode?: string;
    formComponentValues?: any[];
    operationRecords?: any[];
    tasks?: any[];
  };
}

interface ErrorResult {
  success: false;
  instanceId: string;
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

async function getApprovalInstance(
  accessToken: string,
  instanceId: string,
  debug: boolean
): Promise<void> {
  const client = new dingtalkWorkflow(createConfig());

  const headers = new GetProcessInstanceHeaders({});
  headers.xAcsDingtalkAccessToken = accessToken;

  const request = new GetProcessInstanceRequest({
    processInstanceId: instanceId,
  });

  try {
    const response = await client.getProcessInstanceWithOptions(
      request,
      headers,
      new RuntimeOptions({})
    );

    if (debug) {
      console.error('\n=== 调试信息 ===');
      console.error('完整响应:', JSON.stringify(response, null, 2));
      console.error('==============\n');
    }

    const result: Result = {
      success: true,
      instanceId: instanceId,
      instance: response.body?.result || {},
    };

    console.log(JSON.stringify(result, null, 2));
  } catch (err: any) {
    const errorResult: ErrorResult = {
      success: false,
      instanceId: instanceId,
      error: {
        code: err.code || 'UNKNOWN_ERROR',
        message: err.message || '未知错误',
      }
    };
    console.error(JSON.stringify(errorResult, null, 2));
    process.exit(1);
  }
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  const debug = args.includes('--debug');
  const filteredArgs = args.filter(arg => arg !== '--debug');

  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'MISSING_CREDENTIALS',
        message: '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET',
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/get-approval-instance.ts <instanceId> [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (filteredArgs.length < 1) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供审批实例 ID（instanceId）',
        usage: 'ts-node scripts/get-approval-instance.ts <instanceId> [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  const instanceId = filteredArgs[0];

  try {
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在查询审批实例详情...');

    await getApprovalInstance(accessToken, instanceId, debug);
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
