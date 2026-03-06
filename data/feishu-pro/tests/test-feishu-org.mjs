import {
  getUser,
  getDepartment,
  listDepartmentUsers,
  getGroup,
  listCalendars,
  createCalendarEvent,
  deleteCalendarEvent,
  listTasks,
  createTask,
  completeTask,
} from '../dist/index.js';
import { applyFeishuDefaults, createStats, logSuiteStart, logSuiteEnd, runCase } from './_utils.mjs';

applyFeishuDefaults();

const stats = createStats();
logSuiteStart('feishu/org (组织/日程/任务)');

const userId = process.env.TEST_USER_ID;
const deptId = process.env.TEST_DEPT_ID;
const groupId = process.env.TEST_GROUP_ID;
const getCalendarId = () => process.env.TEST_CALENDAR_ID;
const getEventId = () => process.env.TEST_EVENT_ID;
const getTaskId = () => process.env.TEST_TASK_ID;

function extractCalendarId(response) {
  return (
    response?.data?.calendar_list?.[0]?.calendar_id ||
    response?.data?.calendars?.[0]?.calendar_id ||
    response?.data?.calendar_list?.[0]?.id
  );
}

function extractEventId(response) {
  return (
    response?.data?.event_id ||
    response?.data?.event?.event_id ||
    response?.event_id
  );
}

function extractTaskId(response) {
  return (
    response?.data?.task_id ||
    response?.data?.task?.task_id ||
    response?.task_id
  );
}

await runCase(stats, {
  name: 'getUser',
  requires: ['TEST_USER_ID'],
  fn: () => getUser(userId),
});

await runCase(stats, {
  name: 'getDepartment',
  requires: ['TEST_DEPT_ID'],
  fn: () => getDepartment(deptId),
});

await runCase(stats, {
  name: 'listDepartmentUsers',
  requires: ['TEST_DEPT_ID'],
  fn: () => listDepartmentUsers(deptId),
});

await runCase(stats, {
  name: 'getGroup',
  requires: ['TEST_GROUP_ID'],
  fn: () => getGroup(groupId),
});

await runCase(stats, {
  name: 'listCalendars',
  fn: async () => {
    const res = await listCalendars();
    const id = extractCalendarId(res);
    if (id && !process.env.TEST_CALENDAR_ID) process.env.TEST_CALENDAR_ID = id;
    return res;
  },
});

await runCase(stats, {
  name: 'createCalendarEvent',
  requires: ['TEST_CALENDAR_ID', 'TEST_EVENT_START', 'TEST_EVENT_END'],
  sideEffect: true,
  fn: async () => {
    const res = await createCalendarEvent(
      getCalendarId(),
      process.env.TEST_EVENT_SUMMARY || 'OpenClaw Test Event',
      process.env.TEST_EVENT_START,
      process.env.TEST_EVENT_END,
      process.env.TEST_EVENT_DESC
    );
    const id = extractEventId(res);
    if (id && !process.env.TEST_EVENT_ID) process.env.TEST_EVENT_ID = id;
    return res;
  },
});

await runCase(stats, {
  name: 'deleteCalendarEvent',
  requires: ['TEST_CALENDAR_ID', 'TEST_EVENT_ID'],
  destructive: true,
  fn: () => deleteCalendarEvent(getCalendarId(), getEventId()),
});

await runCase(stats, {
  name: 'listTasks',
  fn: () => listTasks(),
});

await runCase(stats, {
  name: 'createTask',
  sideEffect: true,
  fn: async () => {
    const res = await createTask(process.env.TEST_TASK_SUMMARY || 'OpenClaw Test Task', process.env.TEST_TASK_DESC);
    const id = extractTaskId(res);
    if (id && !process.env.TEST_TASK_ID) process.env.TEST_TASK_ID = id;
    return res;
  },
});

await runCase(stats, {
  name: 'completeTask',
  requires: ['TEST_TASK_ID'],
  destructive: true,
  fn: () => completeTask(getTaskId()),
});

logSuiteEnd('feishu/org', stats);
