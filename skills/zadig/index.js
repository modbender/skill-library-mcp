/**
 * Zadig DevOps Platform API Client 
 * 
 * 基于 Zadig OpenAPI 规范实现
 * 文档：Zadig OpenAPI 规范
 * 
 * @requires ZADIG_API_URL - Zadig base URL (e.g., https://your-zadig.example.com)
 * @requires ZADIG_API_KEY - Zadig API JWT Token
 * 
 * 多环境支持：
 
 
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

// Multi-environment configuration

// Environment configurations
const ENV_CONFIG = {
  uat: {
    baseUrl: process.env.ZADIG_API_URL || '',
    apiKey: process.env.ZADIG_API_KEY || ''
  },
  };

// Current active configuration
let BASE_URL = process.env.ZADIG_API_URL || "";
let API_KEY = process.env.ZADIG_API_KEY || "";
const DEFAULT_PROJECT = process.env.ZADIG_DEFAULT_PROJECT || '';
const DEFAULT_ENV = process.env.ZADIG_DEFAULT_ENV || '';

// Ensure BASE_URL doesn't end with /api
let API_BASE = BASE_URL.replace(/\/api$/, '').replace(/\/$/, '');

/**
 * Make HTTP request to Zadig API
 * @private
 */
function request(method, path, data = null, queryParams = {}) {
  return new Promise((resolve, reject) => {
    if (!API_BASE) {
      reject(new Error('ZADIG_API_URL environment variable is not set'));
      return;
    }

    if (!API_KEY) {
      reject(new Error('ZADIG_API_KEY environment variable is not set'));
      return;
    }

    // Build query string
    const queryParts = [];
    for (const [key, value] of Object.entries(queryParams)) {
      if (value !== undefined && value !== null) {
        queryParts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`);
      }
    }
    const queryString = queryParts.length > 0 ? `?${queryParts.join('&')}` : '';

    const url = new URL(path + queryString, API_BASE);
    const isHttps = url.protocol === 'https:';
    const lib = isHttps ? https : http;

    const options = {
      hostname: url.hostname,
      port: url.port || (isHttps ? 443 : 80),
      path: url.pathname + url.search,
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + API_KEY
      }
    };

    const req = lib.request(options, (res) => {
      let responseData = '';

      res.on('data', (chunk) => {
        responseData += chunk;
      });

      res.on('end', () => {
        try {
          const response = JSON.parse(responseData);
          
          if (res.statusCode >= 400) {
            const error = new Error(response.message || response.description || `HTTP ${res.statusCode}`);
            error.statusCode = res.statusCode;
            error.response = response;
            reject(error);
          } else {
            resolve(response);
          }
        } catch (e) {
          if (res.statusCode >= 400) {
            const error = new Error(responseData || `HTTP ${res.statusCode}`);
            error.statusCode = res.statusCode;
            error.response = responseData;
            reject(error);
          } else {
            resolve(responseData ? JSON.parse(responseData) : {});
          }
        }
      });
    });

    req.on('error', (e) => {
      reject(new Error(`Request failed: ${e.message}`));
    });

    req.setTimeout(30000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });

    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      req.write(JSON.stringify(data));
    }

    req.end();
  });
}

// ============================================================================
// 项目 API (Project)
// 文档：/openapi/projects/project
// ============================================================================

/**
 * 获取项目列表
 * @param {Object} params
 * @param {number} [params.pageSize=20] - 每页数量
 * @param {number} [params.pageNum=1] - 页码
 * @returns {Promise<Object>} { projects: [], total: number }
 */
async function listProjects(params = {}) {
  const { pageSize = 20, pageNum = 1 } = params;
  return await request('GET', '/openapi/projects/project', null, { pageSize, pageNum });
}

/**
 * 获取项目详情
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @returns {Promise<Object>} 项目详情
 */
async function getProject(params) {
  const { projectKey } = params;
  return await request('GET', '/openapi/projects/project/detail', null, { projectKey });
}

/**
 * 创建空项目
 * @param {Object} params
 * @param {string} params.projectName - 项目名称
 * @param {string} params.projectKey - 项目标识（小写字母、数字、中划线）
 * @param {boolean} params.isPublic - 是否公开
 * @param {string} params.projectType - 项目类型：helm/yaml/loaded
 * @param {string} [params.description] - 项目描述
 * @returns {Promise<Object>} { message: "success" }
 */
async function createProject(params) {
  const { projectName, projectKey, isPublic, projectType, description = '' } = params;
  return await request('POST', '/openapi/projects/project', {
    project_name: projectName,
    project_key: projectKey,
    is_public: isPublic,
    project_type: projectType,
    description
  });
}

/**
 * 删除项目
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {boolean} params.isDelete - 是否同时删除 K8s 命名空间和服务
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteProject(params) {
  const { projectKey, isDelete } = params;
  return await request('DELETE', '/openapi/projects/project', null, { projectKey, isDelete });
}

// ============================================================================
// 工作流 API (Workflow) - Zadig
// 文档：/openapi/workflows
// ============================================================================

/**
 * 获取工作流列表
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} [params.viewName] - 工作流视图名称（可选）
 * @returns {Promise<Object>} { workflows: [] }
 */
async function listWorkflows(params) {
  const { projectKey, viewName } = params;
  return await request('GET', '/openapi/workflows', null, { projectKey, viewName });
}

/**
 * 获取工作流详情
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.workflowKey - 工作流标识
 * @returns {Promise<Object>} 工作流详情
 */
async function getWorkflow(params) {
  const { projectKey, workflowKey } = params;
  return await request('GET', `/openapi/workflows/custom/${workflowKey}/detail`, null, { projectKey });
}

/**
 * 执行工作流
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.workflowKey - 工作流标识
 * @param {Array} [params.parameters] - 全局变量
 * @param {Array} params.inputs - 执行工作流的具体参数（必填）
 * @param {Array} [params.notifyInputs] - 通知参数
 * @returns {Promise<Object>} { project_name, workflow_name, task_id }
 */
async function triggerWorkflow(params) {
  const { projectKey, workflowKey, parameters = [], inputs, notifyInputs } = params;
  return await request('POST', '/openapi/workflows/custom/task', {
    project_key: projectKey,
    workflow_key: workflowKey,
    parameters,
    inputs,
    notify_inputs: notifyInputs
  });
}

/**
 * 获取工作流任务列表
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.workflowKey - 工作流标识
 * @param {number} [params.pageNum=1] - 页码
 * @param {number} [params.pageSize=50] - 每页数量
 * @returns {Promise<Object>} { total: number, workflow_tasks: [] }
 */
async function listWorkflowTasks(params) {
  const { projectKey, workflowKey, pageNum = 1, pageSize = 50 } = params;
  return await request('GET', `/openapi/workflows/custom/${workflowKey}/tasks`, null, { projectKey, pageNum, pageSize });
}

/**
 * 获取工作流任务详情
 * @param {Object} params
 * @param {string} params.workflowKey - 工作流标识
 * @param {number} params.taskId - 工作流任务 ID
 * @returns {Promise<Object>} 任务详情
 */
async function getWorkflowTask(params) {
  const { workflowKey, taskId } = params;
  return await request('GET', '/openapi/workflows/custom/task', null, { taskId, workflowKey });
}

/**
 * 取消工作流任务
 * @param {Object} params
 * @param {string} params.workflowKey - 工作流标识
 * @param {number} params.taskId - 工作流任务 ID
 * @returns {Promise<Object>} { message: "success" }
 */
async function cancelWorkflowTask(params) {
  const { workflowKey, taskId } = params;
  return await request('DELETE', '/openapi/workflows/custom/task', null, { taskId, workflowKey });
}

/**
 * 重试工作流任务
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.workflowKey - 工作流标识
 * @param {number} params.taskId - 工作流任务 ID
 * @returns {Promise<Object>} { message: "success" }
 */
async function retryWorkflowTask(params) {
  const { projectKey, workflowKey, taskId } = params;
  return await request('POST', `/openapi/workflows/custom/${workflowKey}/task/${taskId}`, null, { projectKey });
}

/**
 * 审批工作流
 * @param {Object} params
 * @param {number} params.taskId - 工作流任务 ID
 * @param {string} params.workflowKey - 工作流标识
 * @param {string} params.stageName - 待审批阶段名称
 * @param {boolean} [params.approve=true] - 是否审批通过
 * @param {string} [params.comment] - 审批意见
 * @returns {Promise<Object>} { message: "success" }
 */
async function approveWorkflow(params) {
  const { taskId, workflowKey, stageName, approve = true, comment = '' } = params;
  return await request('POST', '/openapi/workflows/custom/task/approve', {
    task_id: taskId,
    workflow_key: workflowKey,
    stage_name: stageName,
    approve,
    comment
  });
}

/**
 * 删除工作流
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.workflowKey - 工作流标识
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteWorkflow(params) {
  const { projectKey, workflowKey } = params;
  return await request('DELETE', '/openapi/workflows/custom', null, { projectKey, workflowKey });
}

// ============================================================================
// 工作流视图 API (Workflow View)
// 文档：/openapi/workflows/view
// ============================================================================

/**
 * 获取工作流视图列表
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @returns {Promise<Array>} 视图列表
 */
async function listWorkflowViews(params) {
  const { projectKey } = params;
  return await request('GET', '/openapi/workflows/view', null, { projectKey });
}

/**
 * 创建工作流视图
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.name - 视图名称
 * @param {Array} params.workflowList - 工作流列表 [{ workflow_key, workflow_type: "custom" }]
 * @returns {Promise<Object>} { message: "success" }
 */
async function createWorkflowView(params) {
  const { projectKey, name, workflowList } = params;
  return await request('POST', '/openapi/workflows/view', {
    project_key: projectKey,
    name,
    workflow_list: workflowList
  });
}

/**
 * 编辑工作流视图
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.viewName - 视图名称
 * @param {Array} params.workflowList - 工作流列表 [{ workflow_key, workflow_type, enabled }]
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateWorkflowView(params) {
  const { projectKey, viewName, workflowList } = params;
  return await request('PUT', `/openapi/workflows/view/${viewName}`, {
    workflow_list: workflowList
  }, { projectKey });
}

/**
 * 删除工作流视图
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.viewName - 视图名称
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteWorkflowView(params) {
  const { projectKey, viewName } = params;
  return await request('DELETE', `/openapi/workflows/view/${viewName}`, null, { projectKey });
}

// ============================================================================
// 环境 API (Environment)
// 文档：/openapi/environments
// ============================================================================

/**
 * 获取测试环境列表
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @returns {Promise<Array>} 环境列表
 */
async function listEnvironments(params) {
  const { projectKey } = params;
  return await request('GET', '/openapi/environments', null, { projectKey });
}

/**
 * 获取生产环境列表
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @returns {Promise<Array>} 环境列表
 */
async function listProductionEnvironments(params) {
  const { projectKey } = params;
  return await request('GET', '/openapi/environments/production', null, { projectKey });
}

/**
 * 获取测试环境详情
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @returns {Promise<Object>} 环境详情
 */
async function getEnvironment(params) {
  const { projectKey, envName } = params;
  return await request('GET', `/openapi/environments/${envName}`, null, { projectKey });
}

/**
 * 获取生产环境详情
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @returns {Promise<Object>} 环境详情
 */
async function getProductionEnvironment(params) {
  const { projectKey, envName } = params;
  return await request('GET', `/openapi/environments/production/${envName}`, null, { projectKey });
}

/**
 * 获取环境服务详情
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {string} params.serviceName - 服务名称
 * @returns {Promise<Object>} 服务详情
 */
async function getEnvironmentService(params) {
  const { projectKey, envName, serviceName } = params;
  return await request('GET', `/openapi/environments/${envName}/services/${serviceName}`, null, { projectKey });
}

/**
 * 新建测试环境（K8s YAML 项目）
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envKey - 环境标识
 * @param {string} params.clusterName - 集群名称
 * @param {string} params.namespace - 命名空间
 * @returns {Promise<Object>} { message: "success" }
 */
async function createEnvironment(params) {
  const { projectKey, envKey, clusterName, namespace } = params;
  return await request('POST', '/openapi/environments', {
    project_key: projectKey,
    env_key: envKey,
    cluster_name: clusterName,
    namespace
  });
}

/**
 * 编辑测试环境
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {Object} params.envData - 环境数据
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateEnvironment(params) {
  const { projectKey, envName, envData } = params;
  return await request('PUT', `/openapi/environments/${envName}`, envData, { projectKey });
}

/**
 * 删除测试环境
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteEnvironment(params) {
  const { projectKey, envName } = params;
  return await request('DELETE', `/openapi/environments/${envName}`, null, { projectKey });
}

/**
 * 添加服务到环境（K8s YAML 项目）
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {Array} params.services - 服务列表
 * @returns {Promise<Object>} { message: "success" }
 */
async function addServiceToEnvironment(params) {
  const { projectKey, envName, services } = params;
  return await request('POST', '/openapi/environments/service/yaml', {
    project_key: projectKey,
    env_name: envName,
    services
  });
}

/**
 * 更新环境服务
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {Array} params.services - 服务列表
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateEnvironmentService(params) {
  const { projectKey, envName, services } = params;
  return await request('PUT', '/openapi/environments/service/yaml', {
    project_key: projectKey,
    env_name: envName,
    services
  });
}

/**
 * 删除环境服务
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {string} params.serviceName - 服务名称
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteEnvironmentService(params) {
  const { projectKey, envName, serviceName } = params;
  return await request('DELETE', '/openapi/environments/service/yaml', null, {
    projectKey,
    env_name: envName,
    service_name: serviceName
  });
}

/**
 * 更新 Deployment 镜像
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {string} params.workloadName - Workload 名称
 * @param {string} params.containerName - 容器名称
 * @param {string} params.imageName - 新镜像名称
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateDeploymentImage(params) {
  const { projectKey, envName, workloadName, containerName, imageName } = params;
  return await request('POST', `/openapi/environments/image/deployment/${envName}`, {
    project_key: projectKey,
    workload_name: workloadName,
    container_name: containerName,
    image_name: imageName
  });
}

/**
 * 更新 StatefulSet 镜像
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {string} params.workloadName - Workload 名称
 * @param {string} params.containerName - 容器名称
 * @param {string} params.imageName - 新镜像名称
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateStatefulSetImage(params) {
  const { projectKey, envName, workloadName, containerName, imageName } = params;
  return await request('POST', `/openapi/environments/image/statefulset/${envName}`, {
    project_key: projectKey,
    workload_name: workloadName,
    container_name: containerName,
    image_name: imageName
  });
}

/**
 * 更新 CronJob 镜像
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {string} params.workloadName - Workload 名称
 * @param {string} params.containerName - 容器名称
 * @param {string} params.imageName - 新镜像名称
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateCronJobImage(params) {
  const { projectKey, envName, workloadName, containerName, imageName } = params;
  return await request('POST', `/openapi/environments/image/cronjob/${envName}`, {
    project_key: projectKey,
    workload_name: workloadName,
    container_name: containerName,
    image_name: imageName
  });
}

/**
 * 调整服务实例副本数
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {string} params.workloadName - Workload 名称
 * @param {string} params.workloadType - Workload 类型：Deployment/StatefulSet
 * @param {number} params.replicas - 副本数
 * @returns {Promise<Object>} { message: "success" }
 */
async function scaleService(params) {
  const { projectKey, envName, workloadName, workloadType, replicas } = params;
  return await request('POST', '/openapi/environments/scale', {
    project_key: projectKey,
    env_name: envName,
    workload_name: workloadName,
    workload_type: workloadType,
    replicas
  });
}

/**
 * 重启服务实例
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {string} params.serviceName - 服务名称
 * @returns {Promise<Object>} { message: "success" }
 */
async function restartService(params) {
  const { projectKey, envName, serviceName } = params;
  return await request('POST', `/openapi/environments/${envName}/service/${serviceName}/restart`, null, { projectKey });
}

/**
 * 获取全局变量
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @returns {Promise<Array>} 全局变量列表
 */
async function getGlobalVariables(params) {
  const { projectKey, envName } = params;
  return await request('GET', `/openapi/environments/${envName}/variable`, null, { projectKey });
}

/**
 * 更新全局变量
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {Array} params.variables - 变量列表 [{ key, value, type }]
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateGlobalVariables(params) {
  const { projectKey, envName, variables } = params;
  return await request('PUT', `/openapi/environments/${envName}/variable`, {
    project_key: projectKey,
    variables
  });
}

// ============================================================================
// 服务 API (Service)
// 文档：/openapi/service
// ============================================================================

/**
 * 获取服务列表（测试）
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @returns {Promise<Array>} 服务列表
 */
async function listServices(params) {
  const { projectKey } = params;
  return await request('GET', '/openapi/service/yaml/services', null, { projectKey });
}

/**
 * 获取服务列表（生产）
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @returns {Promise<Array>} 服务列表
 */
async function listProductionServices(params) {
  const { projectKey } = params;
  return await request('GET', '/openapi/service/yaml/production/services', null, { projectKey });
}

/**
 * 获取服务详情（测试）
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.serviceName - 服务名称
 * @returns {Promise<Object>} 服务详情
 */
async function getService(params) {
  const { projectKey, serviceName } = params;
  return await request('GET', `/openapi/service/yaml/${serviceName}`, null, { projectKey });
}

/**
 * 获取服务详情（生产）
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.serviceName - 服务名称
 * @returns {Promise<Object>} 服务详情（包含 scales、pods、containers 等详细信息）
 */
async function getProductionService(params) {
  const { projectKey, serviceName } = params;
  return await request('GET', `/openapi/service/yaml/production/${serviceName}`, null, { projectKey });
}

/**
 * 获取生产环境服务详情（新版 API）
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.envName - 环境名称
 * @param {string} params.serviceName - 服务名称
 * @returns {Promise<Object>} 服务详情（包含 scales、pods、containers、ingress 等）
 */
async function getProductionEnvironmentService(params) {
  const { projectKey, envName, serviceName } = params;
  return await request('GET', `/openapi/environments/production/${envName}/services/${serviceName}`, null, { projectKey });
}

// ============================================================================
// 构建 API (Build)
// 文档：/openapi/build
// ============================================================================

/**
 * 获取构建列表
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @returns {Promise<Array>} 构建列表
 */
async function listBuilds(params) {
  const { projectKey } = params;
  return await request('GET', '/openapi/build', null, { projectKey });
}

/**
 * 获取构建详情
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.buildName - 构建名称
 * @returns {Promise<Object>} 构建详情
 */
async function getBuild(params) {
  const { projectKey, buildName } = params;
  return await request('GET', `/openapi/build/${buildName}/detail`, null, { projectKey });
}

/**
 * 新建构建
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {Object} params.buildData - 构建配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function createBuild(params) {
  const { projectKey, buildData } = params;
  return await request('POST', '/openapi/build', buildData, { projectKey });
}

/**
 * 更新构建
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {Object} params.buildData - 构建配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateBuild(params) {
  const { projectKey, buildData } = params;
  return await request('PUT', '/openapi/build', buildData, { projectKey });
}

/**
 * 删除构建
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.buildName - 构建名称
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteBuild(params) {
  const { projectKey, buildName } = params;
  return await request('DELETE', '/openapi/build', null, { projectKey, buildName });
}

// ============================================================================
// 测试 API (Test)
// 文档：/openapi/quality/testing
// ============================================================================

/**
 * 执行测试任务
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.testName - 测试名称
 * @param {Object} [params.inputs] - 测试参数
 * @returns {Promise<Object>} { task_id }
 */
async function triggerTest(params) {
  const { projectKey, testName, inputs = {} } = params;
  return await request('POST', '/openapi/quality/testing/task', {
    project_key: projectKey,
    test_name: testName,
    ...inputs
  });
}

/**
 * 获取测试任务详情
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.testName - 测试名称
 * @param {number} params.taskId - 任务 ID
 * @returns {Promise<Object>} 测试任务详情
 */
async function getTestTask(params) {
  const { projectKey, testName, taskId } = params;
  return await request('GET', `/openapi/quality/testing/${testName}/task/${taskId}`, null, { projectKey });
}

// ============================================================================
// 代码扫描 API (Code Scan)
// 文档：/openapi/quality/codescan
// ============================================================================

/**
 * 创建代码扫描
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {Object} params.scanData - 扫描配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function createScan(params) {
  const { projectKey, scanData } = params;
  return await request('POST', '/openapi/quality/codescan', scanData, { projectKey });
}

/**
 * 执行代码扫描任务
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.scanName - 扫描名称
 * @returns {Promise<Object>} { task_id }
 */
async function triggerScan(params) {
  const { projectKey, scanName } = params;
  return await request('POST', `/openapi/quality/codescan/${scanName}/task`, null, { projectKey });
}

/**
 * 获取代码扫描任务详情
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.scanName - 扫描名称
 * @param {number} params.taskId - 任务 ID
 * @returns {Promise<Object>} 扫描任务详情
 */
async function getScanTask(params) {
  const { projectKey, scanName, taskId } = params;
  return await request('GET', `/openapi/quality/codescan/${scanName}/task/${taskId}`, null, { projectKey });
}

// ============================================================================
// 版本发布 API (Delivery/Release)
// 文档：/openapi/delivery/releases
// ============================================================================

/**
 * 列出版本
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @returns {Promise<Array>} 版本列表
 */
async function listReleases(params) {
  const { projectKey } = params;
  return await request('GET', '/openapi/delivery/releases', null, { projectKey });
}

/**
 * 获取版本详情
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {number} params.id - 版本 ID
 * @returns {Promise<Object>} 版本详情
 */
async function getRelease(params) {
  const { projectKey, id } = params;
  return await request('GET', `/openapi/delivery/releases/${id}`, null, { projectKey });
}

/**
 * 删除版本
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {number} params.id - 版本 ID
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteRelease(params) {
  const { projectKey, id } = params;
  return await request('DELETE', `/openapi/delivery/releases/${id}`, null, { projectKey });
}

/**
 * 创建版本（K8s YAML 项目）
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {Object} params.releaseData - 版本配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function createRelease(params) {
  const { projectKey, releaseData } = params;
  return await request('POST', '/openapi/delivery/releases/k8s', releaseData, { projectKey });
}

// ============================================================================
// 发布计划 API (Release Plan)
// 文档：/openapi/release_plan/v1
// ============================================================================

/**
 * 创建发布计划
 * @param {Object} params
 * @param {Object} params.planData - 发布计划配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function createReleasePlan(params) {
  const { planData } = params;
  return await request('POST', '/openapi/release_plan/v1', planData);
}

/**
 * 获取发布计划列表
 * @param {Object} params
 * @param {string} [params.projectKey] - 项目标识（可选）
 * @returns {Promise<Array>} 发布计划列表
 */
async function listReleasePlans(params = {}) {
  const { projectKey } = params;
  return await request('GET', '/openapi/release_plan/v1', null, projectKey ? { projectKey } : {});
}

/**
 * 获取发布计划详情
 * @param {Object} params
 * @param {number} params.id - 发布计划 ID
 * @returns {Promise<Object>} 发布计划详情
 */
async function getReleasePlan(params) {
  const { id } = params;
  return await request('GET', `/openapi/release_plan/v1/${id}`);
}

/**
 * 更新发布计划
 * @param {Object} params
 * @param {number} params.id - 发布计划 ID
 * @param {Object} params.planData - 发布计划配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateReleasePlan(params) {
  const { id, planData } = params;
  return await request('PATCH', `/openapi/release_plan/v1/${id}`, planData);
}

// ============================================================================
// 集群 API (Cluster)
// 文档：/openapi/system/cluster
// ============================================================================

/**
 * 列出集群信息
 * @returns {Promise<Array>} 集群列表
 */
async function listClusters() {
  return await request('GET', '/openapi/system/cluster');
}

/**
 * 创建集群
 * @param {Object} params
 * @param {Object} params.clusterData - 集群配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function createCluster(params) {
  const { clusterData } = params;
  return await request('POST', '/openapi/system/cluster', clusterData);
}

/**
 * 更新集群
 * @param {Object} params
 * @param {string} params.clusterId - 集群 ID
 * @param {Object} params.clusterData - 集群配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateCluster(params) {
  const { clusterId, clusterData } = params;
  return await request('PUT', `/openapi/system/cluster/${clusterId}`, clusterData);
}

/**
 * 删除集群
 * @param {Object} params
 * @param {string} params.clusterId - 集群 ID
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteCluster(params) {
  const { clusterId } = params;
  return await request('DELETE', `/openapi/system/cluster/${clusterId}`);
}

// ============================================================================
// 镜像仓库 API (Registry)
// 文档：/openapi/system/registry
// ============================================================================

/**
 * 列出镜像仓库信息
 * @returns {Promise<Array>} 镜像仓库列表
 */
async function listRegistries() {
  return await request('GET', '/openapi/system/registry');
}

/**
 * 集成镜像仓库
 * @param {Object} params
 * @param {Object} params.registryData - 仓库配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function createRegistry(params) {
  const { registryData } = params;
  return await request('POST', '/openapi/system/registry', registryData);
}

/**
 * 获取指定镜像仓库信息
 * @param {Object} params
 * @param {string} params.id - 仓库 ID
 * @returns {Promise<Object>} 仓库详情
 */
async function getRegistry(params) {
  const { id } = params;
  return await request('GET', `/openapi/system/registry/${id}`);
}

/**
 * 更新镜像仓库信息
 * @param {Object} params
 * @param {string} params.id - 仓库 ID
 * @param {Object} params.registryData - 仓库配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateRegistry(params) {
  const { id, registryData } = params;
  return await request('PUT', `/openapi/system/registry/${id}`, registryData);
}

// ============================================================================
// 用户及权限 API (User & Policy)
// 文档：/openapi/users, /openapi/policy
// ============================================================================

/**
 * 列出用户信息
 * @returns {Promise<Array>} 用户列表
 */
async function listUsers() {
  return await request('GET', '/openapi/users');
}

/**
 * 删除用户
 * @param {Object} params
 * @param {string} params.uid - 用户 ID
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteUser(params) {
  const { uid } = params;
  return await request('DELETE', `/openapi/users/${uid}`);
}

/**
 * 列出用户组信息
 * @returns {Promise<Array>} 用户组列表
 */
async function listUserGroups() {
  return await request('GET', '/openapi/user-groups');
}

/**
 * 列出项目角色信息
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @returns {Promise<Array>} 角色列表
 */
async function listRoles(params) {
  const { projectKey } = params;
  return await request('GET', '/openapi/policy/roles', null, { projectKey });
}

/**
 * 获取项目角色详情
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.roleName - 角色名称
 * @returns {Promise<Object>} 角色详情
 */
async function getRole(params) {
  const { projectKey, roleName } = params;
  return await request('GET', `/openapi/policy/roles/${roleName}`, null, { projectKey });
}

/**
 * 创建项目角色
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {Object} params.roleData - 角色配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function createRole(params) {
  const { projectKey, roleData } = params;
  return await request('POST', '/openapi/policy/roles', roleData, { projectKey });
}

/**
 * 编辑项目角色
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.roleName - 角色名称
 * @param {Object} params.roleData - 角色配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateRole(params) {
  const { projectKey, roleName, roleData } = params;
  return await request('PUT', `/openapi/policy/roles/${roleName}`, roleData, { projectKey });
}

/**
 * 删除项目角色
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.roleName - 角色名称
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteRole(params) {
  const { projectKey, roleName } = params;
  return await request('DELETE', `/openapi/policy/roles/${roleName}`, null, { projectKey });
}

/**
 * 列出项目成员
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @returns {Promise<Array>} 成员列表
 */
async function listRoleBindings(params) {
  const { projectKey } = params;
  return await request('GET', '/openapi/policy/role-bindings', null, { projectKey });
}

/**
 * 增加项目成员
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {Object} params.bindingData - 成员配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function createRoleBinding(params) {
  const { projectKey, bindingData } = params;
  return await request('POST', '/openapi/policy/role-bindings', bindingData, { projectKey });
}

/**
 * 更新项目成员权限
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.uid - 用户 ID
 * @param {Object} params.bindingData - 成员配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function updateRoleBinding(params) {
  const { projectKey, uid, bindingData } = params;
  return await request('POST', `/openapi/policy/role-bindings/user/${uid}`, bindingData, { projectKey });
}

/**
 * 删除项目成员
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.uid - 用户 ID
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteRoleBinding(params) {
  const { projectKey, uid } = params;
  return await request('DELETE', `/openapi/policy/role-bindings/user/${uid}`, null, { projectKey });
}

// ============================================================================
// 效能洞察 API (Insight/Statistics)
// 文档：/openapi/statistics
// ============================================================================

/**
 * 数据概览
 * @param {Object} params
 * @param {string} [params.projectKey] - 项目标识
 * @returns {Promise<Object>} 统计数据
 */
async function getStatisticsOverview(params = {}) {
  const { projectKey } = params;
  return await request('GET', '/openapi/statistics/overview', null, projectKey ? { projectKey } : {});
}

/**
 * 构建数据统计
 * @param {Object} params
 * @param {string} [params.projectKey] - 项目标识
 * @returns {Promise<Object>} 构建统计数据
 */
async function getBuildStatistics(params = {}) {
  const { projectKey } = params;
  return await request('GET', '/openapi/statistics/build', null, projectKey ? { projectKey } : {});
}

/**
 * 部署数据统计
 * @param {Object} params
 * @param {string} [params.projectKey] - 项目标识
 * @returns {Promise<Object>} 部署统计数据
 */
async function getDeployStatistics(params = {}) {
  const { projectKey } = params;
  return await request('GET', '/openapi/statistics/deploy', null, projectKey ? { projectKey } : {});
}

/**
 * 测试数据统计
 * @param {Object} params
 * @param {string} [params.projectKey] - 项目标识
 * @returns {Promise<Object>} 测试统计数据
 */
async function getTestStatistics(params = {}) {
  const { projectKey } = params;
  return await request('GET', '/openapi/statistics/test', null, projectKey ? { projectKey } : {});
}

/**
 * 生产环境发布数据统计
 * @param {Object} params
 * @param {string} [params.projectKey] - 项目标识
 * @returns {Promise<Object>} 发布统计数据
 */
async function getReleaseStatistics(params = {}) {
  const { projectKey } = params;
  return await request('GET', '/openapi/statistics/v2/release', null, projectKey ? { projectKey } : {});
}

// ============================================================================
// 系统 API (System)
// 文档：/openapi/system/operation
// ============================================================================

/**
 * 列出系统操作日志
 * @param {Object} params
 * @param {number} [params.pageNum=1] - 页码
 * @param {number} [params.pageSize=20] - 每页数量
 * @returns {Promise<Object>} 操作日志列表
 */
async function listSystemOperations(params = {}) {
  const { pageNum = 1, pageSize = 20 } = params;
  return await request('GET', '/openapi/system/operation', null, { pageNum, pageSize });
}

/**
 * 列出环境操作日志
 * @param {Object} params
 * @param {string} [params.projectKey] - 项目标识
 * @param {number} [params.pageNum=1] - 页码
 * @param {number} [params.pageSize=20] - 每页数量
 * @returns {Promise<Object>} 环境操作日志列表
 */
async function listEnvOperations(params = {}) {
  const { projectKey, pageNum = 1, pageSize = 20 } = params;
  return await request('GET', '/openapi/system/operation/env', null, { projectKey, pageNum, pageSize });
}

// ============================================================================
// 协作模式 API (Collaboration)
// 文档：/openapi/collaborations
// ============================================================================

/**
 * 新建协作模式
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {Object} params.collabData - 协作配置
 * @returns {Promise<Object>} { message: "success" }
 */
async function createCollaboration(params) {
  const { projectKey, collabData } = params;
  return await request('POST', '/openapi/collaborations', collabData, { projectKey });
}

/**
 * 删除协作模式
 * @param {Object} params
 * @param {string} params.projectKey - 项目标识
 * @param {string} params.name - 协作模式名称
 * @returns {Promise<Object>} { message: "success" }
 */
async function deleteCollaboration(params) {
  const { projectKey, name } = params;
  return await request('DELETE', `/openapi/collaborations/${name}`, null, { projectKey });
}

// ============================================================================
// 日志 API (Logs)
// 文档：/openapi/logs
// ============================================================================

/**
 * 查看容器实时日志（SSE 流）
 * @param {Object} params
 * @param {string} params.podName - Pod 名称
 * @param {string} params.containerName - 容器名称
 * @returns {Promise<Stream>} SSE 日志流
 */
async function getContainerLogs(params) {
  const { podName, containerName } = params;
  // 注意：这是 SSE 流，需要特殊处理
  return await request('GET', `/openapi/logs/sse/pods/${podName}/containers/${containerName}`);
}

/**
 * 查看工作流任务实时日志（SSE 流）
 * @param {Object} params
 * @param {string} params.workflowKey - 工作流标识
 * @param {number} params.taskId - 任务 ID
 * @param {string} params.jobTaskName - JobTask 名称
 * @param {number} [params.tails=100] - 返回行数
 * @returns {Promise<Stream>} SSE 日志流
 */
async function getWorkflowTaskLogs(params) {
  const { workflowKey, taskId, jobTaskName, tails = 100 } = params;
  return await request('GET', `/openapi/logs/sse/v4/workflow/${workflowKey}/${taskId}/${jobTaskName}/${tails}`);
}

/**
 * 查看工作流任务完整日志
 * @param {Object} params
 * @param {string} params.workflowKey - 工作流标识
 * @param {number} params.taskId - 任务 ID
 * @param {string} params.jobTaskName - JobTask 名称
 * @returns {Promise<string>} 完整日志文本
 */
async function getWorkflowTaskFullLogs(params) {
  const { workflowKey, taskId, jobTaskName } = params;
  return await request('GET', `/openapi/logs/log/v4/workflow/${workflowKey}/${taskId}/${jobTaskName}`);
}

// ============================================================================
// 环境管理
// ============================================================================

/**
 * 获取当前激活的环境配置
 * @returns {Object} { env: string, baseUrl: string, hasApiKey: boolean }
 */
module.exports = {
  // 环境管理
  
  // 项目
  listProjects,
  getProject,
  createProject,
  deleteProject,
  
  // 工作流
  listWorkflows,
  getWorkflow,
  triggerWorkflow,
  listWorkflowTasks,
  getWorkflowTask,
  cancelWorkflowTask,
  retryWorkflowTask,
  approveWorkflow,
  deleteWorkflow,
  
  // 工作流视图
  listWorkflowViews,
  createWorkflowView,
  updateWorkflowView,
  deleteWorkflowView,
  
  // 环境
  listEnvironments,
  listProductionEnvironments,
  getEnvironment,
  getProductionEnvironment,
  getEnvironmentService,
  createEnvironment,
  updateEnvironment,
  deleteEnvironment,
  addServiceToEnvironment,
  updateEnvironmentService,
  deleteEnvironmentService,
  updateDeploymentImage,
  updateStatefulSetImage,
  updateCronJobImage,
  scaleService,
  restartService,
  getGlobalVariables,
  updateGlobalVariables,
  
  // 服务
  listServices,
  listProductionServices,
  getService,
  getProductionService,
  getProductionEnvironmentService,
  
  // 构建
  listBuilds,
  getBuild,
  createBuild,
  updateBuild,
  deleteBuild,
  
  // 测试
  triggerTest,
  getTestTask,
  
  // 代码扫描
  createScan,
  triggerScan,
  getScanTask,
  
  // 版本发布
  listReleases,
  getRelease,
  deleteRelease,
  createRelease,
  
  // 发布计划
  createReleasePlan,
  listReleasePlans,
  getReleasePlan,
  updateReleasePlan,
  
  // 集群
  listClusters,
  createCluster,
  updateCluster,
  deleteCluster,
  
  // 镜像仓库
  listRegistries,
  createRegistry,
  getRegistry,
  updateRegistry,
  
  // 用户及权限
  listUsers,
  deleteUser,
  listUserGroups,
  listRoles,
  getRole,
  createRole,
  updateRole,
  deleteRole,
  listRoleBindings,
  createRoleBinding,
  updateRoleBinding,
  deleteRoleBinding,
  
  // 效能洞察
  getStatisticsOverview,
  getBuildStatistics,
  getDeployStatistics,
  getTestStatistics,
  getReleaseStatistics,
  
  // 系统
  listSystemOperations,
  listEnvOperations,
  
  // 协作模式
  createCollaboration,
  deleteCollaboration,
  
  // 日志
  getContainerLogs,
  getWorkflowTaskLogs,
  getWorkflowTaskFullLogs,
  
  // 配置
  config: {
    API_URL: API_BASE,
    API_KEY,
    DEFAULT_PROJECT,
    DEFAULT_ENV
  }
};
