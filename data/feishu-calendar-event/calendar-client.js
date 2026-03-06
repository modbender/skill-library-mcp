/**
 * Feishu Calendar API Client
 * 飞书日历 API 客户端
 */

// 从环境变量读取配置，或使用传入的配置
const FEISHU_CONFIG = {
  appId: process.env.FEISHU_APP_ID || 'cli_xxxxxxxxxxxx',
  appSecret: process.env.FEISHU_APP_SECRET || 'xxxxxxxxxxxxx',
  baseUrl: 'https://open.feishu.cn/open-apis'
};

/**
 * 获取 tenant_access_token
 */
async function getAccessToken() {
  const response = await fetch(`${FEISHU_CONFIG.baseUrl}/auth/v3/tenant_access_token/internal`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      app_id: FEISHU_CONFIG.appId,
      app_secret: FEISHU_CONFIG.appSecret
    })
  });
  
  const data = await response.json();
  if (data.code !== 0) {
    throw new Error(`获取 Token 失败: ${data.msg}`);
  }
  
  return data.tenant_access_token;
}

/**
 * 获取日历列表
 */
async function getCalendars(accessToken) {
  const response = await fetch(`${FEISHU_CONFIG.baseUrl}/calendar/v4/calendars?page_size=100`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  const data = await response.json();
  if (data.code !== 0) {
    throw new Error(`获取日历失败: ${data.msg}`);
  }
  
  return data.data.calendar_list;
}

/**
 * 获取日历事件
 */
async function getEvents(accessToken, calendarId, startTime, endTime) {
  // 飞书 API 需要 Unix 时间戳（秒）
  const startTimestamp = Math.floor(new Date(startTime).getTime() / 1000);
  const endTimestamp = Math.floor(new Date(endTime).getTime() / 1000);
  
  const url = `${FEISHU_CONFIG.baseUrl}/calendar/v4/calendars/${calendarId}/events?` +
    `start_time=${startTimestamp}&` +
    `end_time=${endTimestamp}`;
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  });
  
  const data = await response.json();
  
  if (data.code !== 0) {
    throw new Error(`获取事件失败: ${data.msg}`);
  }
  
  return data.data.items || [];
}

/**
 * 获取今天的所有日程
 */
async function getTodayEvents() {
  try {
    // 1. 获取 access token
    const token = await getAccessToken();
    console.log('✅ 获取 Access Token 成功');
    
    // 2. 获取日历列表
    const calendars = await getCalendars(token);
    console.log(`📅 找到 ${calendars.length} 个日历`);
    
    // 3. 获取今天的时间范围
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const startTime = `${year}-${month}-${day}T00:00:00+08:00`;
    const endTime = `${year}-${month}-${day}T23:59:59+08:00`;
    
    // 4. 获取主日历的事件
    const primaryCalendar = calendars.find(c => c.is_primary) || calendars[0];
    console.log(`📆 使用日历: ${primaryCalendar.summary}`);
    
    const events = await getEvents(token, primaryCalendar.calendar_id, startTime, endTime);
    
    return {
      calendar: primaryCalendar,
      events: events,
      date: `${year}-${month}-${day}`
    };
    
  } catch (error) {
    console.error('❌ 错误:', error.message);
    throw error;
  }
}

// 导出函数
module.exports = {
  getAccessToken,
  getCalendars,
  getEvents,
  getTodayEvents
};

// 如果直接运行脚本
if (require.main === module) {
  getTodayEvents().then(result => {
    console.log('\n📋 今日日程:');
    console.log('================');
    if (result.events.length === 0) {
      console.log('今天没有安排日程');
    } else {
      result.events.forEach(event => {
        const start = new Date(parseInt(event.start_time.timestamp) * 1000);
        const end = new Date(parseInt(event.end_time.timestamp) * 1000);
        console.log(`\n📝 ${event.summary}`);
        console.log(`   时间: ${start.toLocaleTimeString()} - ${end.toLocaleTimeString()}`);
        if (event.description) console.log(`   描述: ${event.description}`);
        if (event.location?.name) console.log(`   地点: ${event.location.name}`);
      });
    }
  }).catch(console.error);
}
