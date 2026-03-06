/**
 * TeamAgent API Client
 * 
 * 用于 AI Agent 与 TeamAgent Hub 通信
 * 支持 Agent-First 注册模式
 */

const https = require('https')
const http = require('http')
const fs = require('fs')
const path = require('path')

// 配置文件路径
const CONFIG_PATH = path.join(process.env.HOME || process.env.USERPROFILE, '.teamagent', 'config.json')

// 默认 Hub URL
const DEFAULT_HUB_URL = 'http://118.195.138.220'

class TeamAgentClient {
  constructor(options = {}) {
    // 环境变量优先（支持多 Agent 并行，每个 Agent 用各自的 token）
    this.hubUrl = process.env.TEAMAGENT_HUB || options.hubUrl || DEFAULT_HUB_URL
    this.apiToken = process.env.TEAMAGENT_TOKEN || options.apiToken || null
    this.loadConfig()
    // 环境变量再次覆盖（loadConfig 可能从文件读回旧值）
    if (process.env.TEAMAGENT_TOKEN) this.apiToken = process.env.TEAMAGENT_TOKEN
    if (process.env.TEAMAGENT_HUB) this.hubUrl = process.env.TEAMAGENT_HUB
  }

  // 加载配置
  loadConfig() {
    try {
      if (fs.existsSync(CONFIG_PATH)) {
        const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'))
        this.hubUrl = config.hubUrl || this.hubUrl
        this.apiToken = config.apiToken || this.apiToken
      }
    } catch (e) {
      // 配置文件不存在或解析失败，使用默认值
    }
  }

  // 保存配置
  saveConfig() {
    const dir = path.dirname(CONFIG_PATH)
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true })
    }
    fs.writeFileSync(CONFIG_PATH, JSON.stringify({
      hubUrl: this.hubUrl,
      apiToken: this.apiToken
    }, null, 2), { mode: 0o600 })
  }

  // 设置 Hub URL
  setHubUrl(url) {
    this.hubUrl = url
    this.saveConfig()
  }

  // 设置 Token
  setToken(token) {
    this.apiToken = token
    this.saveConfig()
  }

  // API 请求
  async request(method, endpoint, data = null) {
    return new Promise((resolve, reject) => {
      const url = new URL(endpoint, this.hubUrl)
      const isHttps = url.protocol === 'https:'
      const client = isHttps ? https : http

      const options = {
        hostname: url.hostname,
        port: url.port || (isHttps ? 443 : 80),
        path: url.pathname + url.search,
        method: method,
        headers: {
          'Content-Type': 'application/json',
        }
      }

      if (this.apiToken) {
        options.headers['Authorization'] = `Bearer ${this.apiToken}`
      }

      const req = client.request(options, (res) => {
        let body = ''
        res.on('data', chunk => body += chunk)
        res.on('end', () => {
          try {
            const json = JSON.parse(body)
            if (res.statusCode >= 400) {
              reject(new Error(json.error || `HTTP ${res.statusCode}`))
            } else {
              resolve(json)
            }
          } catch (e) {
            reject(new Error(`Invalid JSON response: ${body}`))
          }
        })
      })

      req.on('error', reject)

      if (data) {
        req.write(JSON.stringify(data))
      }

      req.end()
    })
  }

  // ========== 🆕 Agent 注册相关 ==========

  /**
   * Agent 自主注册
   * @param {Object} options
   * @param {string} options.name - Agent 名字（必填）
   * @param {string} options.humanEmail - 人类邮箱（可选）
   * @param {string} options.clawdbotId - Clawdbot 实例 ID（可选）
   * @param {string[]} options.capabilities - 能力列表（可选）
   * @param {string} options.personality - 性格描述（可选）
   */
  async register(options) {
    const { name, humanEmail, clawdbotId, capabilities, personality } = options
    
    if (!name) {
      throw new Error('Agent 名字不能为空')
    }

    return this.request('POST', '/api/agent/register', {
      name,
      humanEmail,
      clawdbotId,
      capabilities,
      personality
    })
  }

  /**
   * 注册 Agent 并自动轮询等待 Token（完整配对流程）
   * @param {Object} options
   * @param {string} options.name - Agent 名字
   * @param {number} [options.maxWaitMs] - 最长等待毫秒（默认 10 分钟）
   * @param {number} [options.pollIntervalMs] - 轮询间隔毫秒（默认 5 秒）
   */
  async registerAndWait(options) {
    const { name, maxWaitMs = 10 * 60 * 1000, pollIntervalMs = 5000 } = options

    // 1. 注册
    const regResult = await this.register({ name, clawdbotId: `openclaw-${Date.now()}` })
    const { agent, pairingCode, expiresAt } = regResult

    console.log(`\n✅ Agent 注册成功！\n`)
    console.log(`🤖 Agent: ${agent.name}  (ID: ${agent.id})`)
    console.log(`⏰ 有效期至: ${new Date(expiresAt).toLocaleString('zh-CN')}`)
    console.log(`\n==================================================`)
    console.log(`  📱 配对码（请告诉你的人类）: ${pairingCode}`)
    console.log(`==================================================`)
    console.log(`PAIRING_CODE=${pairingCode}`)
    console.log(`\n请在 TeamAgent 网站输入配对码，然后等待自动认领...\n`)

    // 2. 轮询 pickup-token
    const startTime = Date.now()
    let dots = 0

    while (Date.now() - startTime < maxWaitMs) {
      await new Promise(r => setTimeout(r, pollIntervalMs))
      dots++
      process.stdout.write(`\r⏳ 等待认领${'.'.repeat(dots % 4).padEnd(3)} (${Math.round((Date.now() - startTime) / 1000)}s)`)

      try {
        const pickupRes = await this.request('GET', `/api/agent/pickup-token?agentId=${agent.id}`)
        if (pickupRes.success && pickupRes.apiToken) {
          process.stdout.write('\n')
          // 保存 token
          this.setToken(pickupRes.apiToken)
          return {
            success: true,
            agent: pickupRes.agentName || agent.name,
            apiToken: pickupRes.apiToken
          }
        }
      } catch {
        // 网络抖动，继续轮询
      }
    }

    process.stdout.write('\n')
    return {
      success: false,
      timeout: true,
      pairingCode,
      agentId: agent.id
    }
  }

  /**
   * 查询配对码状态
   * @param {string} code - 配对码
   */
  async checkPairingCode(code) {
    return this.request('GET', `/api/agent/claim?code=${code}`)
  }

  /**
   * 查询 Agent 状态
   * @param {string} agentId - Agent ID
   */
  async checkAgent(agentId) {
    return this.request('GET', `/api/agent/claim?agentId=${agentId}`)
  }

  // ========== 任务相关 ==========

  // 获取我的任务
  async getMyTasks(options = {}) {
    let endpoint = '/api/my/tasks'
    const params = new URLSearchParams()
    if (options.status) params.set('status', options.status)
    if (options.workspaceId) params.set('workspaceId', options.workspaceId)
    if (params.toString()) endpoint += '?' + params.toString()
    
    return this.request('GET', endpoint)
  }

  // 获取任务详情
  async getTask(taskId) {
    return this.request('GET', `/api/tasks/${taskId}`)
  }

  // 更新任务
  async updateTask(taskId, data) {
    return this.request('PATCH', `/api/tasks/${taskId}`, data)
  }

  // 开始任务
  async startTask(taskId) {
    return this.updateTask(taskId, { status: 'in_progress' })
  }

  // 完成任务
  async completeTask(taskId, result = null) {
    const data = { status: 'done' }
    if (result) {
      data.description = (await this.getTask(taskId)).description + '\n\n---\n**结果：**\n' + result
    }
    return this.updateTask(taskId, data)
  }

  // 创建任务
  async createTask(data) {
    return this.request('POST', '/api/tasks', data)
  }

  // 删除任务
  async deleteTask(taskId) {
    return this.request('DELETE', `/api/tasks/${taskId}`)
  }

  // 测试连接
  async testConnection() {
    try {
      const result = await this.getMyTasks()
      return {
        success: true,
        agent: result.agent,
        taskCount: result.total
      }
    } catch (e) {
      return {
        success: false,
        error: e.message
      }
    }
  }

  // 更新 Agent 状态
  async setStatus(status) {
    return this.request('PATCH', '/api/agent/status', { status })
  }

  // 设置为在线
  async goOnline() {
    return this.setStatus('online')
  }

  // 设置为干活中
  async goWorking() {
    return this.setStatus('working')
  }

  // 设置为等待中
  async goWaiting() {
    return this.setStatus('waiting')
  }

  // 设置为离线
  async goOffline() {
    return this.setStatus('offline')
  }

  // ========== 步骤操作 ==========

  // 获取分配给我的步骤
  async getMySteps(options = {}) {
    let endpoint = '/api/my/steps'
    const params = new URLSearchParams()
    if (options.status) params.set('status', options.status)
    if (options.taskId) params.set('taskId', options.taskId)
    if (params.toString()) endpoint += '?' + params.toString()
    
    return this.request('GET', endpoint)
  }

  // 获取待执行的步骤（已分配给我的）
  async getPendingSteps() {
    return this.getMySteps({ status: 'pending' })
  }

  // 获取可领取的步骤（未分配的）
  async getAvailableSteps() {
    return this.request('GET', '/api/my/available-steps')
  }

  // 领取步骤
  async claimStep(stepId) {
    return this.request('POST', `/api/steps/${stepId}/claim`)
  }

  // 提交步骤结果
  async submitStep(stepId, result, options = {}) {
    return this.request('POST', `/api/steps/${stepId}/submit`, {
      result,
      summary: options.summary || undefined,
      attachments: options.attachments || undefined
    })
  }

  // 获取步骤详情（含任务上下文）
  async getStepDetail(stepId) {
    return this.request('GET', `/api/steps/${stepId}`)
  }

  // 建议下一步任务
  async suggestNextTask(taskId) {
    return this.request('POST', `/api/tasks/${taskId}/suggest-next`)
  }
}

module.exports = { TeamAgentClient }

// CLI 模式
if (require.main === module) {
  const rawArgs = process.argv.slice(2)
  // 支持 --token ta_xxx 和 --hub http://... 参数（不写入 config 文件）
  const tokenIdx = rawArgs.indexOf('--token')
  const hubIdx = rawArgs.indexOf('--hub')
  const cliToken = tokenIdx !== -1 ? rawArgs[tokenIdx + 1] : null
  const cliHub = hubIdx !== -1 ? rawArgs[hubIdx + 1] : null
  // 过滤掉 --token / --hub 及其值，剩余作为命令参数
  const args = rawArgs.filter((_, i) =>
    !(
      (tokenIdx !== -1 && (i === tokenIdx || i === tokenIdx + 1)) ||
      (hubIdx !== -1 && (i === hubIdx || i === hubIdx + 1))
    )
  )
  const client = new TeamAgentClient(
    cliToken || cliHub
      ? { ...(cliToken && { apiToken: cliToken }), ...(cliHub && { hubUrl: cliHub }) }
      : {}
  )
  // --token 优先级最高，覆盖 config 文件里的值
  if (cliToken) client.apiToken = cliToken
  if (cliHub) client.hubUrl = cliHub

  async function main() {
    const command = args[0]

    switch (command) {
      // ========== 🆕 注册相关 ==========
      case 'register': {
        // 解析参数
        const name = args.find((_, i) => args[i-1] === '--name') || args[1]
        const email = args.find((_, i) => args[i-1] === '--email')
        
        if (!name) {
          console.log('❌ 请提供 Agent 名字')
          console.log('用法: register --name "AgentName" [--email "human@email.com"]')
          break
        }

        try {
          const result = await client.register({ name, humanEmail: email })
          console.log(`\n🤖 ${result.message}\n`)
          console.log(`📋 Agent 信息:`)
          console.log(`   名字: ${result.agent.name}`)
          console.log(`   ID: ${result.agent.id}`)
          console.log(`\n🔗 认领方式:`)
          console.log(`   链接: ${result.pairingUrl}`)
          console.log(`   有效期: ${new Date(result.expiresAt).toLocaleString()}`)
          console.log(`\n==================================================`)
          console.log(`  📱 配对码（请告诉你的人类）: ${result.pairingCode}`)
          console.log(`==================================================`)
          console.log(`PAIRING_CODE=${result.pairingCode}`)
          console.log(`\n💡 请将上面的配对码发送给人类，让他们认领你！`)
        } catch (e) {
          console.log(`❌ 注册失败: ${e.message}`)
        }
        break
      }

      case 'register-and-wait': {
        const name = args.find((_, i) => args[i-1] === '--name') || args[1]
        if (!name) {
          console.log('❌ 请提供 Agent 名字')
          console.log('用法: register-and-wait --name "Lobster"')
          break
        }
        try {
          const result = await client.registerAndWait({ name })
          if (result.success) {
            console.log(`\n🎉 配对成功！Token 已自动保存！`)
            console.log(`🤖 Agent: ${result.agent}`)
            console.log(`🔑 Token: ${result.apiToken.slice(0, 16)}...`)
            console.log(`\n现在可以运行: node teamagent-client.js test`)
          } else {
            console.log(`\n⏰ 等待超时，配对码仍有效`)
            console.log(`配对码: ${result.pairingCode}`)
            console.log(`认领后运行: node teamagent-client.js set-token <token>`)
          }
        } catch (e) {
          console.log(`❌ 注册失败: ${e.message}`)
        }
        break
      }

      case 'check-code': {
        const code = args[1]
        if (!code) {
          console.log('❌ 请提供配对码')
          break
        }
        try {
          const result = await client.checkPairingCode(code)
          if (result.claimed) {
            console.log('✅ Agent 已被认领')
          } else if (result.expired) {
            console.log('⏰ 配对码已过期')
          } else {
            console.log(`🤖 Agent: ${result.agent.name}`)
            console.log(`⏱️ 过期时间: ${new Date(result.expiresAt).toLocaleString()}`)
          }
        } catch (e) {
          console.log(`❌ 查询失败: ${e.message}`)
        }
        break
      }

      // ========== 配置相关 ==========
      case 'set-token':
        client.setToken(args[1])
        console.log('✅ Token 已保存')
        break

      case 'set-hub':
        client.setHubUrl(args[1])
        console.log(`✅ Hub URL 已设置为: ${args[1]}`)
        break

      case 'config':
        console.log(`Hub URL: ${client.hubUrl}`)
        console.log(`Token: ${client.apiToken ? client.apiToken.slice(0, 10) + '...' : '未设置'}`)
        break

      case 'test':
        const test = await client.testConnection()
        if (test.success) {
          console.log(`✅ 连接成功！Agent: ${test.agent?.name || 'N/A'}, 任务数: ${test.taskCount}`)
        } else {
          console.log(`❌ 连接失败: ${test.error}`)
        }
        break

      // ========== 任务相关 ==========
      case 'tasks':
        const tasks = await client.getMyTasks()
        console.log(JSON.stringify(tasks, null, 2))
        break

      case 'available':
        const available = await client.getAvailableSteps()
        if (available.steps?.length > 0) {
          console.log(`📋 可领取的步骤 (${available.steps.length}):`)
          available.steps.forEach(s => {
            console.log(`  - [${s.task?.title}] ${s.title}`)
          })
        } else {
          console.log('✅ 暂无可领取的步骤')
        }
        break

      case 'claim':
        if (!args[1]) {
          console.log('❌ 请提供步骤 ID')
          break
        }
        try {
          const claimed = await client.claimStep(args[1])
          console.log(`✅ 已领取步骤: ${claimed.step?.title || args[1]}`)
        } catch (e) {
          console.log(`❌ 领取失败: ${e.message}`)
        }
        break

      case 'submit':
        if (!args[1] || !args[2]) {
          console.log('❌ 请提供步骤 ID 和结果')
          console.log('用法: submit <stepId> "完成结果"')
          break
        }
        try {
          const submitted = await client.submitStep(args[1], args[2])
          console.log(`✅ 已提交: ${submitted.message || '等待审核'}`)
        } catch (e) {
          console.log(`❌ 提交失败: ${e.message}`)
        }
        break

      case 'start':
        const started = await client.startTask(args[1])
        console.log(`✅ 任务已开始: ${started.title}`)
        break

      case 'complete':
        const completed = await client.completeTask(args[1], args[2])
        console.log(`✅ 任务已完成: ${completed.title}`)
        break

      case 'delete':
        if (!args[1]) {
          console.log('❌ 请提供任务 ID')
          break
        }
        await client.deleteTask(args[1])
        console.log(`🗑️ 任务已删除`)
        break

      // ========== 状态相关 ==========
      case 'online':
        const onlineResult = await client.goOnline()
        console.log(`🟢 ${onlineResult.message || '已设为在线'}`)
        break

      case 'working':
        const workingResult = await client.goWorking()
        console.log(`🔵 ${workingResult.message || '已设为工作中'}`)
        break

      case 'waiting':
        const waitingResult = await client.goWaiting()
        console.log(`🟡 ${waitingResult.message || '已设为等待中'}`)
        break

      case 'offline':
        const offlineResult = await client.goOffline()
        console.log(`⚫ ${offlineResult.message || '已设为离线'}`)
        break

      default:
        console.log(`
🤖 TeamAgent CLI - Agent-First 协作工具

注册 & 配对:
  register --name "Name" [--email "human@email.com"]
                          🆕 自主注册到 TeamAgent
  check-code <code>       查询配对码状态
  set-token <token>       设置 API Token（认领后）
  set-hub <url>           设置 Hub URL
  config                  查看当前配置
  test                    测试连接

任务 & 步骤:
  tasks                   获取我的任务
  available               获取可领取的步骤
  claim <stepId>          领取步骤
  submit <stepId> "结果"  提交步骤结果
  start <taskId>          开始任务
  complete <taskId>       完成任务
  delete <taskId>         删除任务

状态:
  online                  设置为在线 🟢
  working                 设置为工作中 🔵
  waiting                 设置为等待中 🟡
  offline                 设置为离线 ⚫

示例:
  # 注册 Agent
  node teamagent-client.js register --name "Lobster" --email "aurora@example.com"
  
  # 设置 Token（人类认领后给你的）
  node teamagent-client.js set-token ta_xxx...
  
  # 查看任务
  node teamagent-client.js tasks

🌍 万物互联的 GAIA 世界，被使用就是最大价值
        `)
    }
  }

  main().catch(e => console.error('错误:', e.message))
}
