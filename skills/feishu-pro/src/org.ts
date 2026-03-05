import { createClient } from '@openclaw-feishu/feishu-client';

function getAuth() {
  const appId = process.env.FEISHU_APP_ID;
  const appSecret = process.env.FEISHU_APP_SECRET;
  if (!appId || !appSecret) throw new Error('Missing FEISHU_APP_ID or FEISHU_APP_SECRET');
  return { appId, appSecret };
}

/**
 * 获取用户信息
 */
export async function getUser(userId: string, userIdType: 'user_id' | 'union_id' | 'open_id' = 'open_id') {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().contact.user.get({
    path: { user_id: userId },
    params: { user_id_type: userIdType }
  }));
}

/**
 * 获取部门信息
 */
export async function getDepartment(departmentId: string, userIdType: 'user_id' | 'union_id' | 'open_id' = 'open_id') {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().contact.department.get({
    path: { department_id: departmentId },
    params: { user_id_type: userIdType }
  }));
}

/**
 * 列出部门下的用户
 */
export async function listDepartmentUsers(departmentId: string, pageToken?: string, pageSize?: number) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().contact.user.findByDepartment({
    params: {
      department_id: departmentId,
      page_token: pageToken,
      page_size: pageSize || 20,
    }
  }));
}

/**
 * 获取用户组信息
 */
export async function getGroup(groupId: string, userIdType: 'user_id' | 'union_id' | 'open_id' = 'open_id') {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().contact.group.get({
    path: { group_id: groupId },
    params: { user_id_type: userIdType }
  }));
}

/**
 * 列出日历
 */
export async function listCalendars(pageToken?: string, pageSize?: number) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().calendar.calendar.list({
    params: {
      page_token: pageToken,
      page_size: pageSize || 20,
    }
  }));
}

/**
 * 创建日程
 */
export async function createCalendarEvent(calendarId: string, summary: string, startTime: string, endTime: string, description?: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().calendar.calendarEvent.create({
    path: { calendar_id: calendarId },
    data: {
      summary: summary,
      description: description,
      start_time: { timestamp: startTime },
      end_time: { timestamp: endTime },
    }
  }));
}

/**
 * 删除日程
 */
export async function deleteCalendarEvent(calendarId: string, eventId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().calendar.calendarEvent.delete({
    path: {
      calendar_id: calendarId,
      event_id: eventId,
    }
  }));
}

/**
 * 列出任务
 */
export async function listTasks(pageToken?: string, pageSize?: number) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().task.task.list({
    params: {
      page_token: pageToken,
      page_size: pageSize || 20,
    }
  }));
}

/**
 * 创建任务
 */
export async function createTask(summary: string, description?: string, dueTime?: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().task.task.create({
    data: {
      summary: summary,
      description: description,
      due: dueTime ? { time: dueTime } : undefined,
      origin: {
        platform_i18n_name: JSON.stringify({ zh_cn: "OpenClaw", en_us: "OpenClaw" }),
      }
    }
  }));
}

/**
 * 完成任务
 */
export async function completeTask(taskId: string) {
  const { appId, appSecret } = getAuth();
  const client = createClient({ appId, appSecret });

  return await client.call(() => client.getClient().task.task.complete({
    path: { task_id: taskId }
  }));
}
