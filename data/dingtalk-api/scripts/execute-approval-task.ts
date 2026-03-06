// 执行审批任务（同意/拒绝）
// 用法: ts-node scripts/execute-approval-task.ts <instanceId> <userId> <result> [--taskId <taskId>] [--remark "审批意见"] [--debug]
// result: agree 或 refuse
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const { default: dingtalkWorkflow, ExecuteTaskHeaders, ExecuteTaskRequest } = require('@alicloud/dingtalk/workflow_1_0');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');
const { RuntimeOptions } = require('@alicloud/tea-util');

interface Result {
  success: boolean;
  instanceId: string;
  userId: string;
  action: string;
  message: string;
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

async function executeApprovalTask(
  accessToken: string,
  instanceId: string,
  taskId: string | undefined,
  userId: string,
  result: string,
  remark: string | undefined,
  debug: boolean
): Promise<void> {
  const client = new dingtalkWorkflow(createConfig());

  const headers = new ExecuteTaskHeaders({});
  headers.xAcsDingtalkAccessToken = accessToken;

  const request = new ExecuteTaskRequest({
    processInstanceId: instanceId,
    taskId: taskId,
    actionerUserId: userId,
    result: result,
    remark: remark || '',
  });

  try {
    const response = await client.executeTaskWithOptions(
      request,
      headers,
      new RuntimeOptions({})
    );

    if (debug) {
      console.error('\n=== 调试信息 ===');
      console.error('完整响应:', JSON.stringify(response, null, 2));
      console.error('==============\n');
    }

    const res: Result = {
      success: response.body?.result?.success || false,
      instanceId: instanceId,
      userId: userId,
      action: result,
      message: result === 'agree' ? '已同意审批' : '已拒绝审批',
    };

    console.log(JSON.stringify(res, null, 2));
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

function parseArgs(args: string[]): { instanceId: string; taskId?: string; userId: string; result: string; remark?: string; debug: boolean } {
  let instanceId = '';
  let taskId: string | undefined;
  let userId = '';
  let result = '';
  let remark: string | undefined;
  let debug = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--debug') {
      debug = true;
    } else if (arg === '--taskId' && i + 1 < args.length) {
      taskId = args[++i];
    } else if (arg === '--remark' && i + 1 < args.length) {
      remark = args[++i];
    } else if (!arg.startsWith('--')) {
      if (!instanceId) {
        instanceId = arg;
      } else if (!userId) {
        userId = arg;
      } else if (!result) {
        result = arg;
      }
    }
  }

  return { instanceId, taskId, userId, result, remark, debug };
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const { instanceId, taskId, userId, result, remark, debug } = parseArgs(args);

  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'MISSING_CREDENTIALS',
        message: '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET',
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/execute-approval-task.ts <instanceId> <userId> <agree|refuse> [--taskId <taskId>] [--remark "审批意见"] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (!instanceId || !userId || !result) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供审批实例 ID（instanceId）、用户 ID（userId）和审批结果（agree/refuse）',
        usage: 'ts-node scripts/execute-approval-task.ts <instanceId> <userId> <agree|refuse> [--taskId <taskId>] [--remark "审批意见"] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (result !== 'agree' && result !== 'refuse') {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_RESULT',
        message: '审批结果必须是 agree（同意）或 refuse（拒绝）',
      }
    }, null, 2));
    process.exit(1);
  }

  try {
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在执行审批任务...');

    await executeApprovalTask(accessToken, instanceId, taskId, userId, result, remark, debug);
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
