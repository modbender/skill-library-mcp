// 发起审批实例
// 用法: ts-node scripts/create-approval-instance.ts <processCode> <originatorUserId> <deptId> <formValuesJson> [--ccList "user1,user2"] [--debug]
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const { default: dingtalkWorkflow, CreateProcessInstanceHeaders, CreateProcessInstanceRequest } = require('@alicloud/dingtalk/workflow_1_0');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');
const { RuntimeOptions } = require('@alicloud/tea-util');

interface Result {
  success: boolean;
  processCode: string;
  originatorUserId: string;
  instanceId: string;
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

async function createApprovalInstance(
  accessToken: string,
  processCode: string,
  originatorUserId: string,
  deptId: string,
  formComponentValues: any[],
  ccList: string | undefined,
  debug: boolean
): Promise<void> {
  const client = new dingtalkWorkflow(createConfig());

  const headers = new CreateProcessInstanceHeaders({});
  headers.xAcsDingtalkAccessToken = accessToken;

  const request = new CreateProcessInstanceRequest({
    processCode: processCode,
    originatorUserId: originatorUserId,
    deptId: deptId,
    formComponentValues: formComponentValues,
    ccList: ccList,
  });

  try {
    const response = await client.createProcessInstanceWithOptions(
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
      processCode: processCode,
      originatorUserId: originatorUserId,
      instanceId: response.body?.result?.processInstanceId || '',
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

function parseArgs(args: string[]): { processCode: string; originatorUserId: string; deptId: string; formValuesJson: string; ccList?: string; debug: boolean } {
  let processCode = '';
  let originatorUserId = '';
  let deptId = '';
  let formValuesJson = '';
  let ccList: string | undefined;
  let debug = false;

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--debug') {
      debug = true;
    } else if (arg === '--ccList' && i + 1 < args.length) {
      ccList = args[++i];
    } else if (!arg.startsWith('--')) {
      if (!processCode) {
        processCode = arg;
      } else if (!originatorUserId) {
        originatorUserId = arg;
      } else if (!deptId) {
        deptId = arg;
      } else if (!formValuesJson) {
        formValuesJson = arg;
      }
    }
  }

  return { processCode, originatorUserId, deptId, formValuesJson, ccList, debug };
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  const { processCode, originatorUserId, deptId, formValuesJson, ccList, debug } = parseArgs(args);

  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'MISSING_CREDENTIALS',
        message: '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET',
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/create-approval-instance.ts <processCode> <originatorUserId> <deptId> \'[{"name":"标题","value":"请假申请"}]\' [--ccList "user1,user2"] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (!processCode || !originatorUserId || !deptId || !formValuesJson) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供 processCode, originatorUserId, deptId 和 formValuesJson',
        usage: 'ts-node scripts/create-approval-instance.ts <processCode> <originatorUserId> <deptId> \'[{"name":"标题","value":"请假申请"}]\' [--ccList "user1,user2"] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  let formComponentValues: any[];
  try {
    formComponentValues = JSON.parse(formValuesJson);
  } catch (e) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_JSON',
        message: 'formValuesJson 参数不是有效的 JSON 字符串',
      }
    }, null, 2));
    process.exit(1);
  }

  try {
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在发起审批实例...');

    await createApprovalInstance(accessToken, processCode, originatorUserId, deptId, formComponentValues, ccList, debug);
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
