/**
 * TeamAgent Decompose Handler
 * 主 Agent 自动处理 decompose 类型步骤
 * 
 * 流程：
 *   1. 收到 step:ready + stepType=decompose 通知
 *   2. 认领步骤
 *   3. 获取任务描述 + 团队成员能力
 *   4. 调用 LLM 生成步骤拆解 JSON
 *   5. 提交结果 → 服务器自动展开子步骤
 */

const { TeamAgentClient } = require('./teamagent-client.js')

const client = new TeamAgentClient()

// ====== LLM 调用（使用 OpenClaw 内置 Claude） ======
async function callLLM(prompt) {
  // 通过 OpenClaw 的本地 claude-code 接口
  // 实际运行时 agent-worker 在 OpenClaw 环境里，可以用 process 调用
  // 这里用千问 API 作为 fallback（Skill 环境通用）
  const QWEN_API_KEY = process.env.QWEN_API_KEY
  if (!QWEN_API_KEY) {
    throw new Error('QWEN_API_KEY 环境变量未设置，无法调用 LLM')
  }
  const https = require('https')
  
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: 'qwen-max',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.3,
      response_format: { type: 'json_object' }
    })
    
    const opts = {
      hostname: 'dashscope.aliyuncs.com',
      port: 443,
      path: '/compatible-mode/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${QWEN_API_KEY}`,
        'Content-Length': Buffer.byteLength(body)
      }
    }
    
    const req = https.request(opts, res => {
      let d = ''
      res.on('data', c => d += c)
      res.on('end', () => {
        try {
          const json = JSON.parse(d)
          resolve(json.choices?.[0]?.message?.content || '{}')
        } catch { reject(new Error('LLM 解析失败: ' + d)) }
      })
    })
    req.on('error', reject)
    req.write(body)
    req.end()
  })
}

// ====== 生成拆解步骤 ======
async function generateDecomposeSteps(taskDescription, teamMembers) {
  const teamInfo = teamMembers.map(m => 
    `- ${m.agentName || m.name}（${m.capabilities?.join('、') || '通用'}）`
  ).join('\n')

  const prompt = `你是 TeamAgent 主协调 Agent。请将以下任务拆解为具体步骤，并分配给最合适的团队成员。

## 任务描述
${taskDescription}

## 可用团队成员及能力
${teamInfo}

## 输出格式（JSON 数组）
[
  {
    "title": "步骤标题",
    "description": "详细说明",
    "assignee": "团队成员名字（必须是上面列出的成员之一）",
    "requiresApproval": true,
    "parallelGroup": null,
    "inputs": ["输入依赖"],
    "outputs": ["产出物，有文件写文件名如 报告.md"],
    "skills": ["需要的技能"],
    "stepType": "task"
  }
]

## 拆解规则
- requiresApproval: 关键决策、最终产出设 true；常规执行设 false
- parallelGroup: 可同时执行的步骤设相同字符串（如"调研"），顺序执行设 null
- assignee: 必须是团队成员列表中的名字，选最合适的
- 最少 2 步，逻辑清晰，每步独立可执行

## ⚠️ Agent 军团注册任务（必须遵守）
当任务涉及"组建 Agent 军团"、"注册 Agent 成员"、"创建子 Agent"时，**必须**拆成以下两步，缺一不可：

**步骤 A — TeamAgent API 注册**
- description: 调用 POST /api/agents/register 为每位成员注册账号，获取各自 token
- outputs: ["成员注册清单.md"]（含每人的 agentId / 邮箱 / token 前缀）
- requiresApproval: false

**步骤 B — OpenClaw 真实 Agent 创建（关键！）**
- description: 为每位成员执行：(1) 创建 ~/.openclaw/workspace-<agentId> 和 agents/<agentId>/agent 目录；(2) 用 gateway config.patch 将成员加入 agents.list 并更新 main.subagents.allowAgents；(3) openclaw agents list 验证出现在列表中
- outputs: ["OpenClaw配置确认.md"]（含每人 openclaw agents list 截图或输出）
- requiresApproval: true（人类需确认两步都完成）

**原因**：仅 API 注册是"纸面军团"——OpenClaw 中不存在的 Agent 无法被 sessions_spawn 调度执行任何真实任务。

只输出 JSON 数组，不要其他内容。`

  const raw = await callLLM(prompt)
  try {
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : (parsed.steps || [])
  } catch (e) {
    throw new Error('LLM 返回格式错误: ' + raw.substring(0, 200))
  }
}

// ====== 主流程：执行一个 decompose 步骤 ======
async function executeDecomposeStep(step) {
  console.log(`\n🔀 处理拆解步骤: ${step.title}`)
  console.log(`   任务: ${step.task?.title}`)
  console.log(`   任务描述: ${step.task?.description?.substring(0, 100)}...`)

  // 1. 认领步骤
  console.log('\n📥 认领步骤...')
  await client.goWorking()
  const claimed = await client.claimStep(step.id)
  console.log('✅ 已认领')

  try {
    // 2. 获取团队成员能力
    console.log('\n👥 获取团队成员信息...')
    let teamMembers = []
    try {
      const teamRes = await client.request('GET', '/api/agents/team')
      teamMembers = teamRes.members || teamRes || []
      console.log(`   发现 ${teamMembers.length} 位成员:`, teamMembers.map(m => m.agentName || m.name).join(', '))
    } catch (e) {
      console.log('   ⚠️ 获取团队信息失败，使用任务上下文继续')
    }

    const taskDescription = claimed?.context?.taskDescription || step.task?.description || step.description || ''
    if (!taskDescription) {
      console.warn('   ⚠️ 任务描述为空，拆解结果可能不准确')
    }

    // 3. 调用 LLM 生成步骤
    console.log('\n🤖 分析任务，生成拆解方案...')
    const steps = await generateDecomposeSteps(taskDescription, teamMembers)
    console.log(`✅ 生成了 ${steps.length} 个步骤:`)
    steps.forEach((s, i) => {
      const parallel = s.parallelGroup ? ` [并行:${s.parallelGroup}]` : ''
      const approval = s.requiresApproval ? ' [需审批]' : ' [自动通过]'
      console.log(`   ${i+1}. [${s.assignee}]${parallel}${approval} ${s.title}`)
    })

    // 4. 提交结果
    console.log('\n📤 提交拆解结果...')
    const summary = `已拆解为 ${steps.length} 个步骤，` +
      `分配给 ${[...new Set(steps.map(s => s.assignee).filter(Boolean))].join('、')}`
    
    await client.submitStep(step.id, JSON.stringify(steps), { summary })
    await client.goOnline()
    console.log('✅ 提交成功！子步骤已自动创建，相关 Agent 已收到通知')

    return steps
  } catch (error) {
    // 出错时归还步骤（取消认领），不要卡住
    console.error('\n❌ 拆解失败:', error.message)
    await client.goOnline()
    throw error
  }
}

// ====== 检查并处理所有 pending 的 decompose 步骤 ======
async function checkAndHandleDecompose() {
  const result = await client.getPendingSteps()
  const decomposeSteps = (result.steps || []).filter(s => s.stepType === 'decompose')
  
  if (decomposeSteps.length === 0) {
    return 0
  }

  console.log(`\n📋 发现 ${decomposeSteps.length} 个待拆解任务`)
  
  for (const step of decomposeSteps) {
    try {
      await executeDecomposeStep(step)
    } catch (e) {
      console.error(`处理步骤 ${step.id} 失败:`, e.message)
    }
  }

  return decomposeSteps.length
}

module.exports = { executeDecomposeStep, checkAndHandleDecompose, generateDecomposeSteps }
