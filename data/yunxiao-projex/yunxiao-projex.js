#!/usr/bin/env node
/**
 * 云效项目管理工具
 * 用于查询和管理云效项目中的工作项（需求、Bug、任务）
 * 
 * 使用方法：
 *   node yunxiao.js list-projects
 *   node yunxiao.js search-workitems --spaceId SPACE_ID [--category CATEGORY]
 *   node yunxiao.js get-workitem --workitemId WORKITEM_ID
 *   node yunxiao.js create-workitem --spaceId SPACE_ID --category CATEGORY --subject SUBJECT
 * 
 * 环境变量：
 *   YUNXIAO_ACCESS_TOKEN: 云效访问令牌
 *   YUNXIAO_ORGANIZATION_ID: 云效组织ID
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// 云效 API 基础配置
const API_HOST = 'openapi-rdc.aliyuncs.com';
const USER_AGENT = 'yunxiao-cli/1.0.0';
const USER_CACHE_FILE = path.join(__dirname, '.user-cache.json');

// 用户ID缓存
let userCache = {};

// 加载用户缓存
function loadUserCache() {
  try {
    if (fs.existsSync(USER_CACHE_FILE)) {
      const data = fs.readFileSync(USER_CACHE_FILE, 'utf8');
      userCache = JSON.parse(data);
    }
  } catch (e) {
    userCache = {};
  }
}

// 保存用户缓存
function saveUserCache() {
  try {
    fs.writeFileSync(USER_CACHE_FILE, JSON.stringify(userCache, null, 2));
  } catch (e) {
    // 忽略保存错误
  }
}

// 添加用户到缓存
function addToUserCache(name, id) {
  if (name && id) {
    userCache[name] = id;
    saveUserCache();
  }
}

// 从缓存中查找用户ID
function findUserIdByName(name) {
  return userCache[name] || null;
}

// 初始化时加载缓存
loadUserCache();

// 从环境变量获取配置
function getConfig() {
  const accessToken = process.env.YUNXIAO_ACCESS_TOKEN;
  const organizationId = process.env.YUNXIAO_ORGANIZATION_ID;
  
  if (!accessToken || !organizationId) {
    console.error('错误: 请设置环境变量 YUNXIAO_ACCESS_TOKEN 和 YUNXIAO_ORGANIZATION_ID');
    process.exit(1);
  }
  
  return { accessToken, organizationId };
}

// 发送 HTTPS 请求
function makeRequest(path, method = 'GET', body = null) {
  const { accessToken, organizationId } = getConfig();
  
  return new Promise((resolve, reject) => {
    const now = new Date().toUTCString();
    
    const headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'User-Agent': USER_AGENT,
      'x-yunxiao-token': accessToken,
      'Date': now
    };
    
    const options = {
      hostname: API_HOST,
      path: path,
      method: method,
      headers: headers
    };
    
    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          if (res.statusCode >= 400) {
            reject(new Error(`API Error: ${res.statusCode} - ${JSON.stringify(jsonData)}`));
          } else {
            resolve(jsonData);
          }
        } catch (e) {
          if (res.statusCode >= 400) {
            reject(new Error(`API Error: ${res.statusCode} - ${data}`));
          } else {
            resolve({ raw: data });
          }
        }
      });
    });
    
    req.on('error', (e) => reject(e));
    
    if (body) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

// 获取项目列表
async function listProjects() {
  const { organizationId } = getConfig();
  const path = `/oapi/v1/projex/organizations/${organizationId}/projects:search`;
  const body = {
    page: 1,
    perPage: 50,
    orderBy: 'gmtCreate',
    sort: 'desc'
  };
  return await makeRequest(path, 'POST', body);
}

// 搜索工作项
async function searchWorkitems(spaceId, category = null, status = null, page = 1, perPage = 50) {
  const { organizationId } = getConfig();
  
  const body = {
    category: category,
    spaceId: spaceId,
    orderBy: 'gmtCreate',
    sort: 'desc',
    page: page,
    perPage: perPage
  };
  
  // 构建条件
  const conditions = [];
  if (status) {
    conditions.push({
      fieldIdentifier: 'status',
      operator: 'CONTAINS',
      value: [status]
    });
  }
  if (conditions.length > 0) {
    body.conditions = conditions;
  }
  
  const path = `/oapi/v1/projex/organizations/${organizationId}/workitems:search`;
  const result = await makeRequest(path, 'POST', body);
  
  // 收集用户信息到缓存
  if (Array.isArray(result)) {
    result.forEach(item => {
      // 收集创建者
      if (item.creator && item.creator.name && item.creator.id) {
        addToUserCache(item.creator.name, item.creator.id);
      }
      // 收集修改者
      if (item.modifier && item.modifier.name && item.modifier.id) {
        addToUserCache(item.modifier.name, item.modifier.id);
      }
      // 收集负责人
      if (item.assignedTo && item.assignedTo.name && item.assignedTo.id) {
        addToUserCache(item.assignedTo.name, item.assignedTo.id);
      }
      // 收集参与人
      if (item.participants) {
        item.participants.forEach(p => {
          if (p.name && p.id) {
            addToUserCache(p.name, p.id);
          }
        });
      }
    });
  }
  
  return result;
}

// 获取工作项详情
async function getWorkitem(workitemId) {
  const { organizationId } = getConfig();
  const path = `/oapi/v1/projex/organizations/${organizationId}/workitems/${workitemId}`;
  const result = await makeRequest(path);
  
  // 收集用户信息到缓存
  if (result) {
    // 收集创建者
    if (result.creator && result.creator.name && result.creator.id) {
      addToUserCache(result.creator.name, result.creator.id);
    }
    // 收集修改者
    if (result.modifier && result.modifier.name && result.modifier.id) {
      addToUserCache(result.modifier.name, result.modifier.id);
    }
    // 收集负责人
    if (result.assignedTo && result.assignedTo.name && result.assignedTo.id) {
      addToUserCache(result.assignedTo.name, result.assignedTo.id);
    }
    // 收集参与人
    if (result.participants) {
      result.participants.forEach(p => {
        if (p.name && p.id) {
          addToUserCache(p.name, p.id);
        }
      });
    }
  }
  
  return result;
}

// 创建工作项
async function createWorkitem(spaceId, category, subject, assignedTo = null, description = null) {
  const { organizationId } = getConfig();
  
  // 产品类需求的工作项类型ID（从现有需求中获取）
  const workitemTypeId = '9uy29901re573f561d69jn40';
  
  // 按照API文档的格式
  const body = {
    subject: subject,
    spaceId: spaceId,
    workitemTypeId: workitemTypeId,
    assignedTo: assignedTo || 'YOUR_USER_ID' // 默认指派给自己
  };
  
  if (description) {
    body.description = description;
    body.formatType = 'MARKDOWN'; // 指定为Markdown格式
  }
  
  const path = `/oapi/v1/projex/organizations/${organizationId}/workitems`;
  return await makeRequest(path, 'POST', body);
}

// 获取项目工作项类型
async function getWorkitemTypes(spaceId) {
  const { organizationId } = getConfig();
  const path = `/oapi/v1/projex/organizations/${organizationId}/projects/${spaceId}/workitemTypes`;
  return await makeRequest(path);
}

// 获取当前用户
async function getCurrentUser() {
  const { organizationId } = getConfig();
  const path = `/oapi/v1/organization/organizations/${organizationId}/currentUser`;
  return await makeRequest(path);
}

// 更新工作项
async function updateWorkitem(workitemId, updateData) {
  const { organizationId } = getConfig();
  
  // 注意：更新API不接受formatType字段，只能通过创建时指定
  // 删除formatType字段，避免报错
  if (updateData.formatType) {
    delete updateData.formatType;
  }
  
  // 处理参与人：如果是姓名，转换为ID
  if (updateData.participants && Array.isArray(updateData.participants)) {
    const participantIds = [];
    for (const participant of updateData.participants) {
      // 如果已经是ID格式（包含字母和数字的长字符串），直接使用
      if (/^[a-f0-9]{20,}$/.test(participant)) {
        participantIds.push(participant);
      } else {
        // 否则当作姓名，从缓存中查找
        const id = findUserIdByName(participant);
        if (id) {
          participantIds.push(id);
          console.log(`找到用户: ${participant} -> ${id}`);
        } else {
          console.warn(`警告: 未找到用户 "${participant}" 的ID，请先查询工作项以建立用户缓存`);
        }
      }
    }
    updateData.participants = participantIds;
  }
  
  const path = `/oapi/v1/projex/organizations/${organizationId}/workitems/${workitemId}`;
  return await makeRequest(path, 'PUT', updateData);
}

// 创建工作项关联
async function createWorkitemRelation(workitemId, relatedWorkitemId, relationType = 'ASSOCIATED') {
  const { organizationId } = getConfig();
  
  const body = {
    relationType: relationType, // PARENT, SUB, ASSOCIATED, DEPEND_ON, DEPENDED_BY
    workitemId: relatedWorkitemId
  };
  
  const path = `/oapi/v1/projex/organizations/${organizationId}/workitems/${workitemId}/relationRecords`;
  return await makeRequest(path, 'POST', body);
}

// 主函数
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  try {
    switch (command) {
      case 'list-projects': {
        const result = await listProjects();
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      
      case 'current-user': {
        const result = await getCurrentUser();
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      
      case 'search-workitems': {
        const spaceIdIndex = args.indexOf('--spaceId');
        const categoryIndex = args.indexOf('--category');
        const statusIndex = args.indexOf('--status');
        
        if (spaceIdIndex === -1) {
          console.error('错误: 请指定 --spaceId');
          process.exit(1);
        }
        
        const spaceId = args[spaceIdIndex + 1];
        const category = categoryIndex > -1 ? args[categoryIndex + 1] : null;
        const status = statusIndex > -1 ? args[statusIndex + 1] : null;
        
        const result = await searchWorkitems(spaceId, category, status);
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      
      case 'get-workitem': {
        const workitemIdIndex = args.indexOf('--workitemId');
        
        if (workitemIdIndex === -1) {
          console.error('错误: 请指定 --workitemId');
          process.exit(1);
        }
        
        const workitemId = args[workitemIdIndex + 1];
        const result = await getWorkitem(workitemId);
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      
      case 'create-workitem': {
        const spaceIdIndex = args.indexOf('--spaceId');
        const categoryIndex = args.indexOf('--category');
        const subjectIndex = args.indexOf('--subject');
        const assignedToIndex = args.indexOf('--assignedTo');
        const descIndex = args.indexOf('--description');
        
        if (spaceIdIndex === -1 || categoryIndex === -1 || subjectIndex === -1) {
          console.error('错误: 请指定 --spaceId, --category 和 --subject');
          process.exit(1);
        }
        
        const spaceId = args[spaceIdIndex + 1];
        const category = args[categoryIndex + 1];
        const subject = args[subjectIndex + 1];
        const assignedTo = assignedToIndex > -1 ? args[assignedToIndex + 1] : null;
        const description = descIndex > -1 ? args[descIndex + 1] : null;
        
        const result = await createWorkitem(spaceId, category, subject, assignedTo, description);
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      
      case 'get-workitem-types': {
        const spaceIdIndex = args.indexOf('--spaceId');
        
        if (spaceIdIndex === -1) {
          console.error('错误: 请指定 --spaceId');
          process.exit(1);
        }
        
        const spaceId = args[spaceIdIndex + 1];
        const result = await getWorkitemTypes(spaceId);
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      
      case 'update-workitem': {
        const workitemIdIndex = args.indexOf('--workitemId');
        const subjectIndex = args.indexOf('--subject');
        const descIndex = args.indexOf('--description');
        const assignedToIndex = args.indexOf('--assignedTo');
        const participantsIndex = args.indexOf('--participants');
        
        if (workitemIdIndex === -1) {
          console.error('错误: 请指定 --workitemId');
          process.exit(1);
        }
        
        const workitemId = args[workitemIdIndex + 1];
        const updateData = {};
        
        if (subjectIndex > -1) {
          updateData.subject = args[subjectIndex + 1];
        }
        if (descIndex > -1) {
          updateData.description = args[descIndex + 1];
        }
        if (assignedToIndex > -1) {
          updateData.assignedTo = args[assignedToIndex + 1];
        }
        if (participantsIndex > -1) {
          // 参与人ID用逗号分隔
          updateData.participants = args[participantsIndex + 1].split(',').map(id => id.trim());
        }
        
        if (Object.keys(updateData).length === 0) {
          console.error('错误: 请至少指定一个要更新的字段 (--subject, --description, --assignedTo, --participants)');
          process.exit(1);
        }
        
        const result = await updateWorkitem(workitemId, updateData);
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      
      case 'add-relation': {
        const workitemIdIndex = args.indexOf('--workitemId');
        const relatedIndex = args.indexOf('--relatedWorkitemId');
        const typeIndex = args.indexOf('--relationType');
        
        if (workitemIdIndex === -1 || relatedIndex === -1) {
          console.error('错误: 请指定 --workitemId 和 --relatedWorkitemId');
          process.exit(1);
        }
        
        const workitemId = args[workitemIdIndex + 1];
        const relatedWorkitemId = args[relatedIndex + 1];
        const relationType = typeIndex > -1 ? args[typeIndex + 1] : 'ASSOCIATED';
        
        console.log(`创建关联: ${workitemId} -> ${relatedWorkitemId} (${relationType})`);
        const result = await createWorkitemRelation(workitemId, relatedWorkitemId, relationType);
        console.log(JSON.stringify(result, null, 2));
        break;
      }
      
      default:
        console.log(`
云效项目管理工具

命令:
  list-projects                获取项目列表
  
  current-user                 获取当前用户信息
  
  search-workitems             搜索工作项
    --spaceId SPACE_ID         项目ID（必填）
    --category CATEGORY        类型：Req/Bug/Task（可选）
    --status STATUS            状态（可选）
    
  get-workitem                 获取工作项详情
    --workitemId WORKITEM_ID   工作项ID（必填）
    
  create-workitem              创建工作项
    --spaceId SPACE_ID         项目ID（必填）
    --category CATEGORY        类型：Req/Bug/Task（必填）
    --subject SUBJECT          标题（必填）
    --assignedTo USER_ID       负责人ID（可选）
    --description DESC         描述（可选）
    
  get-workitem-types           获取项目工作项类型
    --spaceId SPACE_ID         项目ID（必填）

环境变量:
  YUNXIAO_ACCESS_TOKEN         云效访问令牌
  YUNXIAO_ORGANIZATION_ID      云效组织ID
        `);
    }
  } catch (error) {
    console.error('执行出错:', error.message);
    process.exit(1);
  }
}

main();
