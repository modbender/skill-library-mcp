// 获取未登录钉钉的员工列表
// 用法: ts-node scripts/list-inactive-users.ts <queryDate> [--deptIds <id1,id2,...>] [--offset <offset>] [--size <size>] [--debug]
// queryDate 格式: yyyyMMdd
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const https = require('https');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');

interface SuccessResult {
  success: boolean;
  queryDate: string;
  userIds: string[];
  hasMore: boolean;
  nextOffset?: number;
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

async function listInactiveUsers(
  accessToken: string,
  queryDate: string,
  deptIds: number[],
  offset: number,
  size: number,
  debug: boolean = false
): Promise<void> {
  try {
    const body: any = {
      is_active: false,
      query_date: queryDate,
      offset: offset,
      size: size,
    };

    if (deptIds.length > 0) {
      body.dept_ids = deptIds;
    }

    const response = await dingtalkRequest(
      accessToken,
      'POST',
      '/topapi/inactive/user/v2/get',
      body
    );

    if (debug) {
      console.error('\n=== 调试信息 ===');
      console.error('完整响应:', JSON.stringify(response, null, 2));
      console.error('==============\n');
    }

    const result: SuccessResult = {
      success: true,
      queryDate: queryDate,
      userIds: response.result?.list || [],
      hasMore: response.result?.has_more || false,
      nextOffset: response.result?.has_more ? (offset + size) : undefined,
    };

    console.log(JSON.stringify(result, null, 2));
  } catch (err: any) {
    const errorResult: ErrorResult = {
      success: false,
      error: {
        code: err.code || 'UNKNOWN_ERROR',
        message: err.message || err.msg || JSON.stringify(err),
      }
    };
    console.error(JSON.stringify(errorResult, null, 2));
    process.exit(1);
  }
}

function parseArgs(args: string[]): { queryDate: string; deptIds: number[]; offset: number; size: number; debug: boolean } {
  let queryDate: string | null = null;
  let deptIds: number[] = [];
  let offset = 0;
  let size = 100;
  let debug = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--debug') {
      debug = true;
    } else if (args[i] === '--deptIds' && i + 1 < args.length) {
      deptIds = args[i + 1].split(',').map(id => parseInt(id.trim(), 10)).filter(id => !isNaN(id));
      i++;
    } else if (args[i] === '--offset' && i + 1 < args.length) {
      offset = parseInt(args[i + 1], 10);
      if (isNaN(offset)) {
        throw new Error('--offset 必须是数字');
      }
      i++;
    } else if (args[i] === '--size' && i + 1 < args.length) {
      size = parseInt(args[i + 1], 10);
      if (isNaN(size) || size < 1 || size > 100) {
        throw new Error('--size 必须是 1-100 之间的数字');
      }
      i++;
    } else if (!queryDate && !args[i].startsWith('--')) {
      queryDate = args[i];
      if (!/^\d{8}$/.test(queryDate)) {
        throw new Error('queryDate 必须是 yyyyMMdd 格式（如 20240115）');
      }
    }
  }

  if (!queryDate) {
    throw new Error('缺少 queryDate 参数');
  }

  return { queryDate, deptIds, offset, size, debug };
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);

  const appKey = process.env.DINGTALK_APP_KEY;
  const appSecret = process.env.DINGTALK_APP_SECRET;

  if (!appKey || !appSecret) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'MISSING_CREDENTIALS',
        message: '缺少钉钉应用凭证，请设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET',
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/list-inactive-users.ts <queryDate> [--deptIds <id1,id2,...>] [--offset <offset>] [--size <size>] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  let parsedArgs;
  try {
    parsedArgs = parseArgs(args);
  } catch (err: any) {
    console.error(JSON.stringify({
      success: false,
      error: {
        code: 'INVALID_ARGUMENTS',
        message: err.message,
        usage: 'ts-node scripts/list-inactive-users.ts <queryDate> [--deptIds <id1,id2,...>] [--offset <offset>] [--size <size>] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  try {
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在获取未登录用户列表...');

    await listInactiveUsers(
      accessToken,
      parsedArgs.queryDate,
      parsedArgs.deptIds,
      parsedArgs.offset,
      parsedArgs.size,
      parsedArgs.debug
    );
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
