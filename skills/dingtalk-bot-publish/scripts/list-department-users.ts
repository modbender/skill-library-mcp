// 获取部门用户列表脚本
// 用法: ts-node scripts/list-department-users.ts <deptId> [--debug]
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const https = require('https');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');

interface SimpleUser {
  userId: string;
  name: string;
}

interface SuccessResult {
  success: boolean;
  deptId: number;
  users: SimpleUser[];
}

interface ErrorResult {
  success: false;
  deptId: number;
  error: {
    code: string;
    message: string;
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
 * 通用钉钉新版 API 调用函数
 */
async function dingtalkRequest(accessToken: string, method: string, path: string, body?: any): Promise<any> {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'oapi.dingtalk.com',
      path: `${path}?access_token=${accessToken}`,
      method,
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

/**
 * 获取部门用户列表（简略信息）
 * @param accessToken Access Token
 * @param deptId 部门 ID
 * @param debug 是否开启调试模式
 */
async function listDepartmentUsers(accessToken: string, deptId: number, debug: boolean = false): Promise<void> {
  try {
    // 钉钉 TOP API: POST /topapi/v2/user/list
    // 请求体: { "dept_id": number, "cursor": number, "size": number }
    let allUsers: SimpleUser[] = [];
    let cursor = 0;
    let hasMore = true;

    while (hasMore) {
      const response = await dingtalkRequest(
        accessToken,
        'POST',
        '/topapi/v2/user/list',
        { dept_id: deptId, cursor: cursor, size: 100 }
      );

      // 调试模式：输出完整响应
      if (debug) {
        console.error('\n=== 调试信息 ===');
        console.error('完整响应:', JSON.stringify(response, null, 2));
        console.error('==============\n');
      }

      const users = response.result?.list || [];
      allUsers = allUsers.concat(users.map((u: any) => ({
        userId: u.userid,
        name: u.name,
      })));

      hasMore = response.result?.has_more || false;
      if (hasMore) {
        cursor = response.result?.next_cursor || 0;
      }
    }

    const result: SuccessResult = {
      success: true,
      deptId: deptId,
      users: allUsers,
    };

    console.log(JSON.stringify(result, null, 2));
  } catch (err: any) {
    const errorResult: ErrorResult = {
      success: false,
      deptId: deptId,
      error: {
        code: err.code || 'UNKNOWN_ERROR',
        message: err.message || err.msg || JSON.stringify(err),
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
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/list-department-users.ts <deptId> [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  if (filteredArgs.length < 1) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：需要提供部门 ID（deptId）',
        usage: 'ts-node scripts/list-department-users.ts <deptId> [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  const deptId = parseInt(filteredArgs[0], 10);
  if (isNaN(deptId)) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: '参数错误：deptId 必须是数字',
        usage: 'ts-node scripts/list-department-users.ts <deptId> [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  try {
    // 自动获取 access_token
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在获取部门用户列表...');

    // 使用获取到的 token 获取部门用户列表
    await listDepartmentUsers(accessToken, deptId, debug);
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
