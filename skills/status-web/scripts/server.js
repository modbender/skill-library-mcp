const express = require('express');
const path = require('path');
const fs = require('fs').promises;
const os = require('os');
const { execSync } = require('child_process');

const app = express();
const PORT = 8888;

// 导入任务列表
const { getRecentWorkTasksFixed } = require('./get-work-tasks-fixed');
const { getScheduledTasksSimple } = require('./get-scheduled-tasks-simple');

// 静态文件服务
app.use(express.static(path.join(__dirname, 'public')));

// JSON 解析中间件
app.use(express.json());

// 获取系统运行时间
function getSystemUptime() {
    const uptimeSeconds = os.uptime();
    const days = Math.floor(uptimeSeconds / 86400);
    const hours = Math.floor((uptimeSeconds % 86400) / 3600);
    const minutes = Math.floor((uptimeSeconds % 3600) / 60);
    return `${days} 天 ${hours} 小时 ${minutes} 分钟`;
}

// 获取内存可用空间
function getMemoryAvailable() {
    const freeMem = os.freemem();
    const availableGB = (freeMem / (1024 * 1024 * 1024)).toFixed(2);
    return `${availableGB} GB`;
}

// 获取CPU使用率
function getCpuLoad() {
    const loads = os.loadavg();
    const cores = os.cpus().length;
    const loadPercent = ((loads[0] / cores) * 100);
    return `${Math.min(100, Math.max(0, loadPercent)).toFixed(1)}%`;
}

// 检查OpenClaw状态
async function checkOpenClawStatus() {
    try {
        const stdout = execSync('openclaw status --json', { encoding: 'utf8' });
        const jsonMatch = stdout.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            const status = JSON.parse(jsonMatch[0]);
            return status.gateway && status.gateway.reachable === true;
        }
        return false;
    } catch (error) {
        console.error('Error checking OpenClaw status:', error.message);
        return false;
    }
}

// 获取模型状态
async function getModelStatus() {
    try {
        const stdout = execSync('openclaw status --json', { encoding: 'utf8' });
        const jsonMatch = stdout.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
            const status = JSON.parse(jsonMatch[0]);
            if (status.sessions && status.sessions.recent && status.sessions.recent.length > 0) {
                return status.sessions.recent[0].model || 'unknown';
            }
        }
        return 'unknown';
    } catch (error) {
        console.error('Error getting model status:', error.message);
        return 'unknown';
    }
}

// 获取真实的定时任务（直接读取cron配置文件）- 修复版：只返回最近3个
async function getScheduledTasksFromOpenClaw() {
    try {
        // 导入修复后的任务获取函数
        const { getScheduledTasksSimple } = require('./get-scheduled-tasks-simple');
        return await getScheduledTasksSimple();
    } catch (error) {
        console.error('Error fetching scheduled tasks:', error.message);
        // 返回空数组
        return [];
    }
}

// 获取健康状态
async function getHealthStatusFromOpenClaw() {
    try {
        const openclawConnected = await checkOpenClawStatus();
        const modelStatus = await getModelStatus();
        
        return {
            status: "healthy",
            uptime: getSystemUptime(),
            cpu_load: getCpuLoad(),
            memory_available: getMemoryAvailable(),
            openclaw_connected: openclawConnected,
            model_status: modelStatus,
            last_check: new Date().toISOString()
        };
    } catch (error) {
        console.error('Error fetching health status:', error);
        return {
            status: "error",
            uptime: getSystemUptime(),
            cpu_load: getCpuLoad(),
            memory_available: getMemoryAvailable(),
            openclaw_connected: false,
            model_status: "unknown",
            last_check: new Date().toISOString()
        };
    }
}

// 统一的API端点
app.get('/api/status', async (req, res) => {
    try {
        // 直接获取任务列表
        const tasks = await getRecentWorkTasksFixed();
        const recentWork = tasks.map(task => ({
            id: task.id,
            title: task.title,
            description: `小雨自评完成度：${task.completion}%`,
            timestamp: task.timestamp,
            status: task.completion === 100 ? "completed" : "in_progress",
            type: "development",
            completion: task.completion
        }));
        
        const scheduledTasks = await getScheduledTasksFromOpenClaw();
        const healthStatus = await getHealthStatusFromOpenClaw();
        
        res.json({
            recent_work: recentWork,
            scheduled_tasks: scheduledTasks,
            health_status: healthStatus,
            last_updated: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error fetching data from OpenClaw:', error);
        res.status(500).json({ error: 'Failed to fetch data' });
    }
});

// 聊天 API 端点
app.post('/api/chat', async (req, res) => {
    try {
        const { message, sessionId, unlocked } = req.body;
        
        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }
        
        // 检查口令
        const activationPhrase = "ISME——YT";
        const shouldActivate = message === activationPhrase || unlocked;
        
        let responseMessage;
        let activated = false;
        let newSessionId = sessionId || `web_${Date.now()}`;
        
        if (shouldActivate) {
            activated = true;
            // 使用正确的主会话 ID
            const mainSessionId = "2177ea58-49db-414f-bc44-0c95b5f7eb3f";
            
            // 构建安全的消息（转义特殊字符）
            const safeMessage = message.replace(/"/g, '\\"').replace(/\$/g, '\\$');
            
            // 调用 OpenClaw CLI
            const command = `openclaw agent --session-id ${mainSessionId} --message "${safeMessage}" --json`;
            
            try {
                const result = execSync(command, { timeout: 30000 }); // 30秒超时
                const resultStr = result.toString();
                
                // 提取响应内容
                const jsonMatch = resultStr.match(/\{[\s\S]*\}/);
                if (jsonMatch) {
                    const parsed = JSON.parse(jsonMatch[0]);
                    if (parsed.result?.payloads?.[0]?.text) {
                        responseMessage = parsed.result.payloads[0].text;
                    } else {
                        responseMessage = "收到了你的消息，但处理结果不明确。";
                    }
                } else {
                    responseMessage = "消息已收到并处理。";
                }
            } catch (cliError) {
                console.error('OpenClaw CLI error:', cliError);
                responseMessage = "处理消息时出现错误，请稍后重试。";
            }
        } else {
            responseMessage = "请输入正确的口令来激活隐藏对话功能。";
        }
        
        res.json({
            response: responseMessage,
            activated: activated,
            sessionId: newSessionId
        });
    } catch (error) {
        console.error('Chat API error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// 根路径重定向到 index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// 启动服务器
app.listen(PORT, '0.0.0.0', () => {
    console.log(`小雨 Bot 状态监测页面服务启动成功！`);
    console.log(`访问地址: http://localhost:${PORT}`);
    console.log(`API 端点: http://localhost:${PORT}/api/status`);
});

module.exports = { app };