// 查询离职记录列表
// 用法: ts-node scripts/list-resigned-users.ts <startTime> [<endTime>] [--nextToken <token>] [--maxResults <max>] [--debug]
// startTime/endTime 格式: ISO8601 (如 2024-01-15T00:00:00+08:00)
// 需要设置环境变量 DINGTALK_APP_KEY 和 DINGTALK_APP_SECRET
export {};

const https = require('https');
const { default: dingtalkOauth2_1_0, GetAccessTokenRequest } = require('@alicloud/dingtalk/oauth2_1_0');
const { Config } = require('@alicloud/openapi-client');

interface ResignedRecord {
  userId: string;
  name?: string;
  stateCode?: string;
  mobile?: string;
  leaveTime?: string;
  leaveReason?: string;
}

interface SuccessResult {
  success: boolean;
  startTime: string;
  endTime?: string;
  records: ResignedRecord[];
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

async function newApiRequest(accessToken: string, path: string, queryParams?: Record<string, string>): Promise<any> {
  return new Promise((resolve, reject) => {
    const queryString = queryParams ? '?' + new URLSearchParams(queryParams).toString() : '';
    const options = {
      hostname: 'api.dingtalk.com',
      path: `/v1.0${path}${queryString}`,
      method: 'GET',
      headers: {
        'x-acs-dingtalk-access-token': accessToken,
        'Content-Type': 'application/json',
      } as Record<string, string>,
    };
    const req = https.request(options, (res: any) => {
      let data = '';
      res.on('data', (chunk: string) => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode && res.statusCode >= 400) {
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
    req.end();
  });
}

async function listResignedUsers(
  accessToken: string,
  startTime: string,
  endTime: string | null,
  nextToken: string | null,
  maxResults: number,
  debug: boolean = false
): Promise<void> {
  try {
    const queryParams: Record<string, string> = {
      startTime: startTime,
    };

    if (endTime) {
      queryParams.endTime = endTime;
    }
    if (nextToken) {
      queryParams.nextToken = nextToken;
    }
    queryParams.maxResults = maxResults.toString();

    const response = await newApiRequest(
      accessToken,
      '/contact/empLeaveRecords',
      queryParams
    );

    if (debug) {
      console.error('\n=== 调试信息 ===');
      console.error('完整响应:', JSON.stringify(response, null, 2));
      console.error('==============\n');
    }

    const result: SuccessResult = {
      success: true,
      startTime: startTime,
      endTime: endTime || undefined,
      records: response.records || [],
      nextToken: response.nextToken,
    };

    console.log(JSON.stringify(result, null, 2));
  } catch (err: any) {
    const errorResult: ErrorResult = {
      success: false,
      error: {
        code: err.code || err.Code || 'UNKNOWN_ERROR',
        message: err.message || err.Message || JSON.stringify(err),
      }
    };
    console.error(JSON.stringify(errorResult, null, 2));
    process.exit(1);
  }
}

function parseArgs(args: string[]): { startTime: string; endTime: string | null; nextToken: string | null; maxResults: number; debug: boolean } {
  let startTime: string | null = null;
  let endTime: string | null = null;
  let nextToken: string | null = null;
  let maxResults = 100;
  let debug = false;
  let positionalCount = 0;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--debug') {
      debug = true;
    } else if (args[i] === '--nextToken' && i + 1 < args.length) {
      nextToken = args[i + 1];
      i++;
    } else if (args[i] === '--maxResults' && i + 1 < args.length) {
      maxResults = parseInt(args[i + 1], 10);
      if (isNaN(maxResults) || maxResults < 1 || maxResults > 100) {
        throw new Error('--maxResults 必须是 1-100 之间的数字');
      }
      i++;
    } else if (!args[i].startsWith('--')) {
      positionalCount++;
      if (positionalCount === 1) {
        startTime = args[i];
      } else if (positionalCount === 2) {
        endTime = args[i];
      }
    }
  }

  if (!startTime) {
    throw new Error('缺少 startTime 参数');
  }

  return { startTime, endTime, nextToken, maxResults, debug };
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
        usage: 'export DINGTALK_APP_KEY=your-app-key && export DINGTALK_APP_SECRET=your-app-secret && ts-node scripts/list-resigned-users.ts <startTime> [<endTime>] [--nextToken <token>] [--maxResults <max>] [--debug]'
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
        usage: 'ts-node scripts/list-resigned-users.ts <startTime> [<endTime>] [--nextToken <token>] [--maxResults <max>] [--debug]'
      }
    }, null, 2));
    process.exit(1);
  }

  try {
    console.error('正在获取 access_token...');
    const accessToken = await getAccessToken(appKey, appSecret);
    console.error('access_token 获取成功，正在查询离职记录...');

    await listResignedUsers(
      accessToken,
      parsedArgs.startTime,
      parsedArgs.endTime,
      parsedArgs.nextToken,
      parsedArgs.maxResults,
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
