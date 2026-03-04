const fetch = require('node-fetch'); // Retain for specialized calls if needed, or refactor to use fetchWithAuth
const { getTenantAccessToken } = require('./auth');
const { fetchWithAuth, fetchWithRetry: fetchCommon } = require('../../feishu-common/index.js'); // Import new common

// Re-implement executeWithAuthRetry using common if possible, or adapt.
// Ideally, we replace manual token handling with fetchWithAuth where appropriate.
// But `fetchWithAuth` in feishu-common handles token refresh internally.
// So we can simplify `getAllUsers` and others to use `fetchWithAuth`.

async function getAllUsers() {
    let users = [];
    let pageToken = '';
    
    do {
      const url = `https://open.feishu.cn/open-apis/contact/v3/users?department_id_type=open_department_id&department_id=0&page_size=50${pageToken ? '&page_token=' + pageToken : ''}`;
      // feishu-common's fetchWithAuth handles the Authorization header
      const response = await fetchWithAuth(url);
      const data = await response.json();
      
      if (data.code !== 0) {
        console.warn('Failed to fetch users:', data.msg);
        break;
      }
      if (data.data && data.data.items) {
        users = users.concat(data.data.items);
      }
      pageToken = data.data && data.data.page_token;
    } while (pageToken);

    return users;
}

async function getAttendance(userIds, dateInt, idType = 'employee_id') {
    const url = `https://open.feishu.cn/open-apis/attendance/v1/user_tasks/query?employee_type=${idType}`;
    
    const chunks = [];
    for (let i = 0; i < userIds.length; i += 50) {
      chunks.push(userIds.slice(i, i + 50));
    }

    let allTasks = [];

    for (const chunk of chunks) {
      const response = await fetchWithAuth(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_ids: chunk,
          check_date_from: dateInt,
          check_date_to: dateInt
        })
      });
      const data = await response.json();
      if (data.code === 0 && data.data && data.data.user_task_results) {
        allTasks = allTasks.concat(data.data.user_task_results);
      } else {
        console.error(`Attendance query failed for chunk (${idType}):`, JSON.stringify(data));
      }
    }

    return allTasks;
}

async function sendMessage(receiveId, content) {
    let type = 'user_id';
    if (receiveId.startsWith('ou_')) type = 'open_id';
    else if (receiveId.startsWith('oc_')) type = 'chat_id';
    
    let msgType = 'text';
    let bodyContent = '';

    if (typeof content === 'object') {
        msgType = 'interactive';
        bodyContent = JSON.stringify(content);
    } else {
        msgType = 'text';
        bodyContent = JSON.stringify({ text: content });
    }

    const response = await fetchWithAuth(`https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=${type}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        receive_id: receiveId,
        msg_type: msgType,
        content: bodyContent
      })
    });
    
    return await response.json();
}

module.exports = {
  getAllUsers,
  getAttendance,
  sendMessage
};
