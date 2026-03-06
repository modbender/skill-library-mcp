// 机器人发送单聊消息脚本
// 用法: ts-node scripts/send-user-message.ts <userId> <robotCode> <消息内容> [--debug]
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const { default: dingtalkRobot, BatchSendOTOHeaders, BatchSendOTORequest } = require('@alicloud/dingtalk/robot_1_0');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');
const { RuntimeOptions } = require('@alicloud/tea-util');

interface SendMessageResult {
  success: boolean;
  userId: string;
  robotCode: string;
  processQueryKey: string;
  flowControlledStaffIdList: string[];
  invalidStaffIdList: string[];
  message: string;
}

interface ErrorResult {
  success: false;
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
 * 发送单聊消息
 * @param accessToken Access Token
 * @param userId 用户 ID
 * @param robotCode 机器人 Code
 * @param message 消息内容
 * @param debug 是否开启调试模式
 */
async function sendUserMessage(
  accessToken: string,
  userId: string,
  robotCode: string,
  message: string,
  debug: boolean = false
): Promise<void> {
  const client = new dingtalkRobot(createConfig());

  const headers = new BatchSendOTOHeaders({});
  headers.xAcsDingtalkAccessToken = accessToken;

  // 构建消息参数
  const msgParam = JSON.stringify({ content: message });

  const request = new BatchSendOTORequest({
    robotCode: robotCode,
    userIds: [userId],
    msgKey: 'sampleText',  // 文本消息类型
    msgParam: msgParam,
  });

  try {
    const response = await client.batchSendOTOWithOptions(
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
    const processQueryKey = response.body?.processQueryKey;

    if (!processQueryKey) {
      throw new Error('发送消息失败：响应中未包含 processQueryKey');
    }

    const result: SendMessageResult = {
      success: true,
      userId: userId,
      robotCode: robotCode,
      processQueryKey: processQueryKey,
      flowControlledStaffIdList: response.body?.flowControlledStaffIdList || [],
      invalidStaffIdList: response.body?.invalidStaffIdList || [],
      message: message,
    };

    console.log(JSON.stringify(result, null, 2));
    console.error(`✅ 消息发送成功！processQueryKey: ${processQueryKey}`);
  } catch (err: any) {
    const errorResult: ErrorResult = {
      success: false,
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
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/send-user-message.ts "<userId>" "<robotCode>" "<消息内容>" [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (filteredArgs.length < 3) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供 userId、robotCode 和消息内容',
        usage: 'ts-node scripts/send-user-message.ts "<userId>" "<robotCode>" "<消息内容>" [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  const userId = filteredArgs[0];
  const robotCode = filteredArgs[1];
  const message = filteredArgs[2];

  try {
    // 自动获取 access_token
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在发送单聊消息...');

    // 使用获取到的 token 发送消息
    await sendUserMessage(accessToken, userId, robotCode, message, debug);
  } catch (err: any) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'SEND_FAILED',
        message: err.message || '发送失败',
      }
    }, null, 2));
    process.exit(1);
  }
}

main();
