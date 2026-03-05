// 添加审批评论
// 用法: ts-node scripts/add-approval-comment.ts <instanceId> <userId> <comment> [--debug]
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const { default: dingtalkWorkflow, AddProcessInstanceCommentHeaders, AddProcessInstanceCommentRequest } = require('@alicloud/dingtalk/workflow_1_0');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');
const { RuntimeOptions } = require('@alicloud/tea-util');

interface Result {
  success: boolean;
  instanceId: string;
  userId: string;
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

async function addApprovalComment(
  accessToken: string,
  instanceId: string,
  userId: string,
  comment: string,
  debug: boolean
): Promise<void> {
  const client = new dingtalkWorkflow(createConfig());

  const headers = new AddProcessInstanceCommentHeaders({});
  headers.xAcsDingtalkAccessToken = accessToken;

  const request = new AddProcessInstanceCommentRequest({
    processInstanceId: instanceId,
    commentUserId: userId,
    text: comment,
  });

  try {
    const response = await client.addProcessInstanceCommentWithOptions(
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
      success: response.body?.result?.success || false,
      instanceId: instanceId,
      userId: userId,
      message: '评论已添加',
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

function parseArgs(args: string[]): { instanceId: string; userId: string; comment: string; debug: boolean } {
  let instanceId = '';
  let userId = '';
  let comment = '';
  let debug = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--debug') {
      debug = true;
    } else if (!arg.startsWith('--')) {
      if (!instanceId) {
        instanceId = arg;
      } else if (!userId) {
        userId = arg;
      } else if (!comment) {
        comment = arg;
      }
    }
  }

  return { instanceId, userId, comment, debug };
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const { instanceId, userId, comment, debug } = parseArgs(args);

  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'MISSING_CREDENTIALS',
        message: '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET',
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/add-approval-comment.ts <instanceId> <userId> "<comment>" [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (!instanceId || !userId || !comment) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供审批实例 ID（instanceId）、用户 ID（userId）和评论内容（comment）',
        usage: 'ts-node scripts/add-approval-comment.ts <instanceId> <userId> "<comment>" [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  try {
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在添加审批评论...');

    await addApprovalComment(accessToken, instanceId, userId, comment, debug);
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
