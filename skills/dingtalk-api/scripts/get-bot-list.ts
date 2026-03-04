// 获取群内机器人列表脚本
// 用法: ts-node scripts/get-bot-list.ts <openConversationId>
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const { default: dingtalkRobot, GetBotListInGroupHeaders, GetBotListInGroupRequest } = require('@alicloud/dingtalk/robot_1_0');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');
const { RuntimeOptions } = require('@alicloud/tea-util');

interface BotInfo {
  robotCode: string;
  robotName: string;
  robotAvatar: string;
  openRobotType?: number;
}

interface GetBotListResult {
  success: boolean;
  openConversationId: string;
  botList: BotInfo[];
}

interface ErrorResult {
  success: false;
  openConversationId: string;
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
 * 获取群内机器人列表
 * @param accessToken Access Token
 * @param openConversationId 开放会话 ID
 * @param debug 是否开启调试模式
 */
async function getBotList(accessToken: string, openConversationId: string, debug: boolean = false): Promise<void> {
  const client = new dingtalkRobot(createConfig());

  const headers = new GetBotListInGroupHeaders({});
  headers.xAcsDingtalkAccessToken = accessToken;

  const request = new GetBotListInGroupRequest({
    openConversationId: openConversationId,
  });

  try {
    const response = await client.getBotListInGroupWithOptions(
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
    // API 返回的是 chatbotInstanceVOList，不是 botList
    const botList = response.body?.chatbotInstanceVOList || [];
    const result: GetBotListResult = {
      success: true,
      openConversationId: openConversationId,
      botList: botList.map((bot: any) => ({
        robotCode: bot.robotCode,
        robotName: bot.name,
        robotAvatar: bot.downloadIconURL,
        openRobotType: bot.openRobotType,
      })),
    };

    console.log(JSON.stringify(result, null, 2));

    // 如果列表为空，给出提示
    if (botList.length === 0) {
      console.error('\n⚠️  返回的机器人列表为空，可能的原因：');
      console.error('   1. 应用没有 "Robot.Read" 或 "机器人信息读取" 权限');
      console.error('   2. openConversationId 不正确（请确认是当前应用可访问的群）');
      console.error('   3. 群内机器人不是通过当前企业内部应用创建的');
      console.error('   4. 群内机器人是 webhook 类型的自定义机器人（此类机器人不通过此 API 返回）');
      console.error('\n   排查建议：');
      console.error('   • 在钉钉开放平台检查应用权限（权限管理 -> 机器人相关权限）');
      console.error('   • 使用 --debug 参数查看完整响应');
      console.error('   • 确认 openConversationId 是通过当前应用的接口获取的');
    }
  } catch (err: any) {
    const errorResult: ErrorResult = {
      success: false,
      openConversationId: openConversationId,
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
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/get-bot-list.ts "<openConversationId>" [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (filteredArgs.length < 1) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供 openConversationId（开放会话 ID）',
        usage: 'ts-node scripts/get-bot-list.ts "<openConversationId>" [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  const openConversationId = filteredArgs[0];

  try {
    // 自动获取 access_token
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在获取群内机器人列表...');
    
    // 使用获取到的 token 获取机器人列表
    await getBotList(accessToken, openConversationId, debug);
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
