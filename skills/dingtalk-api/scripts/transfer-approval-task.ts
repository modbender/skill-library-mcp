// 转交审批任务
// 用法: ts-node scripts/transfer-approval-task.ts <instanceId> <userId> <transferToUserId> [--taskId <taskId>] [--remark "转交原因"] [--debug]
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const https = require('https');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');

interface Result {
  success: boolean;
  instanceId: string;
  userId: string;
  transferToUserId: string;
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

async function dingtalkRequest(accessToken: string, path: string, body?: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'oapi.dingtalk.com',
      path: `${path}?access_token=${accessToken}`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      } as Record<string, string>,
    };
    const req = https.request(options, (res: any) => {
      let data = '';
      res.on('data', (chunk: string) => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.errcode !== undefined && parsed.errcode !== 0) {
            reject({ code: parsed.errcode, message: parsed.errmsg });
          } else if (res.statusCode && res.statusCode >= 400) {
            reject(parsed);
          } else {
            resolve(parsed);
          }
        } catch {
          reject(new Error(`Invalid JSON response: ${data}`));
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

async function transferApprovalTask(
  accessToken: string,
  instanceId: string,
  taskId: string | undefined,
  userId: string,
  transferToUserId: string,
  remark: string | undefined,
  debug: boolean
): Promise<void> {
  try {
    // 转交审批使用 TOP API
    const response = await dingtalkRequest(
      accessToken,
      '/topapi/process/workrecord/task/transfer',
      {
        process_instance_id: instanceId,
        task_id: taskId,
        userid: userId,
        transfer_to_userid: transferToUserId,
        remark: remark || '转交审批任务',
      }
    );

    if (debug) {
      console.error('\n=== 调试信息 ===');
      console.error('完整响应:', JSON.stringify(response, null, 2));
      console.error('==============\n');
    }

    const result: Result = {
      success: response.errcode === 0,
      instanceId: instanceId,
      userId: userId,
      transferToUserId: transferToUserId,
      message: '审批任务已转交',
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

function parseArgs(args: string[]): { instanceId: string; taskId?: string; userId: string; transferToUserId: string; remark?: string; debug: boolean } {
  let instanceId = '';
  let taskId: string | undefined;
  let userId = '';
  let transferToUserId = '';
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
      } else if (!transferToUserId) {
        transferToUserId = arg;
      }
    }
  }

  return { instanceId, taskId, userId, transferToUserId, remark, debug };
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const { instanceId, taskId, userId, transferToUserId, remark, debug } = parseArgs(args);

  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'MISSING_CREDENTIALS',
        message: '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET',
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/transfer-approval-task.ts <instanceId> <userId> <transferToUserId> [--taskId <taskId>] [--remark "转交原因"] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (!instanceId || !userId || !transferToUserId) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供审批实例 ID（instanceId）、当前处理人用户 ID（userId）和转交目标用户 ID（transferToUserId）',
        usage: 'ts-node scripts/transfer-approval-task.ts <instanceId> <userId> <transferToUserId> [--taskId <taskId>] [--remark "转交原因"] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  try {
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在转交审批任务...');

    await transferApprovalTask(accessToken, instanceId, taskId, userId, transferToUserId, remark, debug);
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
