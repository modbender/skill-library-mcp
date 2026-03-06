import * as fs from 'fs'
import * as path from 'path'

export interface AccountLLM {
  provider?: string
  apiKey?: string
  baseUrl?: string
  model?: string
  temperature?: number
  maxTokens?: number
}

/** 根据 avatarPinId 生成头像 URL */
export const AVATAR_URL_BASE =
  'https://file.metaid.io/metafile-indexer/api/v1/files/accelerate/content'

export function getAvatarUrl(avatarPinId: string): string {
  return `${AVATAR_URL_BASE}/${avatarPinId}`
}

/** Agent 人设选项（与 metabot-chat addGroupToUser 一致，创建 name 节点时写入 account.json） */
export const CHARACTER_OPTIONS = [
  '幽默风趣', '严肃认真', '活泼开朗', '内向沉稳', '热情奔放',
  '理性冷静', '感性细腻', '乐观积极', '谨慎保守', '创新大胆',
  '温和友善', '直率坦诚', '机智聪明', '沉稳可靠', '充满活力',
]
export const PREFERENCE_OPTIONS = [
  '科技与编程', '艺术与创作', '音乐与电影', '运动与健身', '美食与烹饪',
  '旅行与探索', '阅读与写作', '游戏与娱乐', '投资与理财', '学习与成长',
  '社交与交流', '摄影与设计', '创业与商业', '哲学与思考', '环保与公益',
]
export const GOAL_OPTIONS = [
  '成为技术专家', '实现财务自由', '创作优秀作品', '帮助他人成长', '探索未知领域',
  '建立个人品牌', '推动行业发展', '改善生活质量', '学习新技能', '拓展人际关系',
  '实现个人价值', '追求内心平静', '创造社会价值', '体验不同生活', '持续自我提升',
]
export const LANGUAGE_OPTIONS = [
  '中文', 'English', '日本語', '한국어', 'Español',
  'Français', 'Deutsch', 'Italiano', 'Português', 'Русский',
  'العربية', 'हिन्दी', 'ไทย', 'Tiếng Việt', 'Bahasa Indonesia',
]
export const STANCE_OPTIONS = ['乐观进取', '谨慎保守', '中立理性', '激进创新', '温和包容']
export const DEBATE_STYLE_OPTIONS = ['敢于反驳', '善于倾听', '喜欢追问', '温和补充', '直率表达']
export const INTERACTION_STYLE_OPTIONS = ['主动回应他人', '被动参与', '喜欢@人讨论', '倾向独立发言']

export interface AccountProfile {
  character?: string
  preference?: string
  goal?: string
  masteringLanguages?: string[]
  stanceTendency?: string
  debateStyle?: string
  interactionStyle?: string
}

export interface Account {
  mnemonic: string
  mvcAddress: string
  btcAddress: string
  dogeAddress: string
  publicKey: string
  userName: string
  path: string
  globalMetaId?: string // 全局 MetaId，支持多链（MVC/BTC/DOGE）
  metaid?: string
  avatarPinId?: string
  avatar?: string // 格式: https://file.metaid.io/metafile-indexer/api/v1/files/accelerate/content/${avatarPinId}
  chatPublicKey?: string
  chatPublicKeyPinId?: string
  /** llm 为数组，llm[0] 默认来自 .env；未指定时使用 llm[0] */
  llm?: AccountLLM[]
  /** Agent 人设，创建 name 节点时写入；调用 LLM 时作为 config 传入 */
  character?: string
  preference?: string
  goal?: string
  masteringLanguages?: string[]
  stanceTendency?: string
  debateStyle?: string
  interactionStyle?: string
}

/**
 * 获取 account 的 LLM 配置，默认使用 llm[0]
 * @param account 账户
 * @param index 数组下标，默认 0；未指定时使用第一项
 */
export function getAccountLLM(account: Account, index: number = 0): AccountLLM | undefined {
  const llm = account.llm
  if (!llm) return undefined
  const arr = Array.isArray(llm) ? llm : [llm]
  return arr[index]
}

export interface AccountData {
  accountList: Account[]
}

function getRandomItem<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)]
}

function getRandomItems<T>(array: T[], count: number): T[] {
  const shuffled = [...array].sort(() => 0.5 - Math.random())
  return shuffled.slice(0, Math.min(count, array.length))
}

/**
 * 从提示词解析人设，例如「名字叫Sam,性格XXX,爱好XXX，目标XXX，擅长语言XXX，立场xxx，辩论风格XXX，互动风格XXX」
 */
export function extractProfileFromPrompt(prompt: string): Partial<AccountProfile> {
  const out: Partial<AccountProfile> = {}
  const patterns: { key: keyof AccountProfile; reg: RegExp; transform?: (s: string) => any }[] = [
    { key: 'character', reg: /性格[：:]\s*['"]?([^'",，。\n]+)['"]?/i },
    { key: 'character', reg: /性格[为是]\s*['"]?([^'",，。\n]+)['"]?/i },
    { key: 'preference', reg: /爱好[：:]\s*['"]?([^'",，。\n]+)['"]?/i },
    { key: 'preference', reg: /喜好[：:]\s*['"]?([^'",，。\n]+)['"]?/i },
    { key: 'goal', reg: /目标[：:]\s*['"]?([^'",，。\n]+)['"]?/i },
    { key: 'masteringLanguages', reg: /擅长语言[：:]\s*['"]?([^'",，。\n]+)['"]?/i, transform: (s) => s.split(/[,，、\s]+/).map((x) => x.trim()).filter(Boolean) },
    { key: 'stanceTendency', reg: /立场[：:]\s*['"]?([^'",，。\n]+)['"]?/i },
    { key: 'debateStyle', reg: /辩论风格[：:]\s*['"]?([^'",，。\n]+)['"]?/i },
    { key: 'interactionStyle', reg: /互动风格[：:]\s*['"]?([^'",，。\n]+)['"]?/i },
  ]
  for (const { key, reg, transform } of patterns) {
    const m = prompt.match(reg)
    if (m && m[1]) {
      const val = transform ? transform(m[1].trim()) : m[1].trim()
      if (val !== undefined && val !== '') (out as any)[key] = val
    }
  }
  return out
}

/**
 * 为人设字段赋默认值：未提供的用 getRandomItem 分配，并写回 account（修改传入对象）
 */
export function applyProfileToAccount(
  account: Account,
  overrides?: Partial<AccountProfile>
): void {
  account.character = overrides?.character || account.character || getRandomItem(CHARACTER_OPTIONS)
  account.preference = overrides?.preference || account.preference || getRandomItem(PREFERENCE_OPTIONS)
  account.goal = overrides?.goal || account.goal || getRandomItem(GOAL_OPTIONS)
  account.masteringLanguages =
    overrides?.masteringLanguages?.length
      ? overrides.masteringLanguages
      : account.masteringLanguages?.length
        ? account.masteringLanguages
        : getRandomItems(LANGUAGE_OPTIONS, 2)
  account.stanceTendency =
    overrides?.stanceTendency || account.stanceTendency || getRandomItem(STANCE_OPTIONS)
  account.debateStyle = overrides?.debateStyle || account.debateStyle || getRandomItem(DEBATE_STYLE_OPTIONS)
  account.interactionStyle =
    overrides?.interactionStyle || account.interactionStyle || getRandomItem(INTERACTION_STYLE_OPTIONS)
}

// 根目录下的 account.json（与 metabot-chat 共享）
const ROOT_DIR = path.join(__dirname, '..', '..')
const ACCOUNT_FILE = path.join(ROOT_DIR, 'account.json')
const OLD_ACCOUNT_FILE = path.join(__dirname, '..', 'account.json')

/** 将旧格式 llm 对象迁移为 llm 数组 */
function normalizeAccountLLM(acc: any): void {
  if (!acc.llm) return
  if (!Array.isArray(acc.llm)) {
    acc.llm = [acc.llm]
  }
}

// Read account.json
export function readAccountFile(): AccountData {
  // 迁移：若旧位置存在且根目录不存在，则复制
  if (fs.existsSync(OLD_ACCOUNT_FILE) && !fs.existsSync(ACCOUNT_FILE)) {
    try {
      fs.copyFileSync(OLD_ACCOUNT_FILE, ACCOUNT_FILE)
      console.log('📦 已迁移: account.json → 根目录')
    } catch {
      /* ignore */
    }
  }

  try {
    if (fs.existsSync(ACCOUNT_FILE)) {
      const content = fs.readFileSync(ACCOUNT_FILE, 'utf-8')
      const data: AccountData = JSON.parse(content)
      data.accountList.forEach(normalizeAccountLLM)
      return data
    }
  } catch (error) {
    console.error('Error reading account.json:', error)
  }
  return { accountList: [] }
}

// Write account.json
export function writeAccountFile(data: AccountData): void {
  try {
    const filtered = data.accountList.filter(
      (account) => account.mnemonic && account.mnemonic.trim() !== ''
    )
    filtered.forEach(normalizeAccountLLM)
    const filteredData: AccountData = { accountList: filtered }
    fs.writeFileSync(ACCOUNT_FILE, JSON.stringify(filteredData, null, 4), 'utf-8')
  } catch (error) {
    console.error('Error writing account.json:', error)
    throw error
  }
}

// Create account.json from template if it doesn't exist
export function ensureAccountFile(): void {
  // 迁移：若旧位置 metabot-basic/account.json 存在且根目录不存在，则复制到根目录
  if (fs.existsSync(OLD_ACCOUNT_FILE) && !fs.existsSync(ACCOUNT_FILE)) {
    try {
      fs.copyFileSync(OLD_ACCOUNT_FILE, ACCOUNT_FILE)
      console.log('📦 已迁移: account.json → 根目录')
    } catch (e) {
      console.warn('⚠️ 迁移 account.json 失败:', (e as Error).message)
    }
  }

  if (!fs.existsSync(ACCOUNT_FILE)) {
    // Create empty account file (don't copy template with empty account)
    writeAccountFile({ accountList: [] })
  } else {
    // Clean up existing file: remove any empty accounts
    const existingData = readAccountFile()
    if (existingData.accountList.some(acc => !acc.mnemonic || acc.mnemonic.trim() === '')) {
      writeAccountFile(existingData) // This will filter out empty accounts
    }
  }
}

// 根目录 userInfo.json（与 metabot-chat 共享）
const USER_INFO_FILE = path.join(ROOT_DIR, 'userInfo.json')

export interface UserInfoItem {
  address: string
  globalmetaid?: string
  metaid?: string
  userName?: string
  groupList?: string[]
  [key: string]: any
}

export interface UserInfoData {
  userList: UserInfoItem[]
}

export function readUserInfoFile(): UserInfoData {
  try {
    if (fs.existsSync(USER_INFO_FILE)) {
      const content = fs.readFileSync(USER_INFO_FILE, 'utf-8')
      return JSON.parse(content)
    }
  } catch (error) {
    console.error('Error reading userInfo.json:', error)
  }
  return { userList: [] }
}

export function writeUserInfoFile(data: UserInfoData): void {
  try {
    fs.writeFileSync(USER_INFO_FILE, JSON.stringify(data, null, 2), 'utf-8')
  } catch (error) {
    console.error('Error writing userInfo.json:', error)
    throw error
  }
}

// Find account by username, address, or metaid
export function findAccountByKeyword(keyword: string, accountData: AccountData): Account | null {
  if (!keyword) return null

  const lowerKeyword = keyword.toLowerCase().trim()
  for (const account of accountData.accountList) {
    if (
      (account.userName && account.userName.toLowerCase().includes(lowerKeyword)) ||
      (account.mvcAddress && account.mvcAddress.toLowerCase().includes(lowerKeyword)) ||
      (account.btcAddress && account.btcAddress.toLowerCase().includes(lowerKeyword)) ||
      (account.dogeAddress && account.dogeAddress.toLowerCase().includes(lowerKeyword)) ||
      (account.metaid && account.metaid.toLowerCase().includes(lowerKeyword))
    ) {
      return account
    }
  }
  return null
}

// Log error to log/error.md
export function logError(error: Error, context: string, method?: string): void {
  const logFile = path.join(__dirname, '..', 'log', 'error.md')
  const timestamp = new Date().toISOString()
  const errorLog = `
## Error at ${timestamp}

**Context**: ${context}
${method ? `**Method**: ${method}` : ''}
**Error**: ${error.message}
**Stack**: 
\`\`\`
${error.stack}
\`\`\`

---

`
  
  try {
    fs.appendFileSync(logFile, errorLog, 'utf-8')
  } catch (err) {
    console.error('Failed to write error log:', err)
  }
}

// Parse user prompt for username
export function extractUsername(prompt: string): string | null {
  // Patterns: "名字叫'xxx'", "名字叫xxx", "name is xxx", "username: xxx"
  const patterns = [
    /名字叫['"]([^'"]+)['"]/i,
    /名字叫\s*([^\s,，。]+)/i,
    /name\s+is\s+['"]?([^'",，。\s]+)['"]?/i,
    /username[:\s]+['"]?([^'",，。\s]+)['"]?/i,
    /用户名[:\s]+['"]?([^'",，。\s]+)['"]?/i,
  ]
  
  for (const pattern of patterns) {
    const match = prompt.match(pattern)
    if (match && match[1]) {
      return match[1].trim()
    }
  }
  
  return null
}

// Parse user prompt for buzz content
export function extractBuzzContent(prompt: string): string | null {
  // Patterns: "内容为'xxx'", "内容为xxx", "content is xxx", "发条信息，内容为xxx"
  const patterns = [
    /内容为['"]([^'"]+)['"]/i,
    /内容为\s+['"]?([^'",，。]+)['"]?/i,
    /content\s+is\s+['"]?([^'",，。]+)['"]?/i,
    /(?:发条|发送|发布)(?:信息|消息|buzz)[，,]?\s*(?:内容为|内容)?\s*['"]?([^'",，。]+)['"]?/i,
    /buzz\s+content[:\s]+['"]?([^'",，。]+)['"]?/i,
  ]
  
  for (const pattern of patterns) {
    const match = prompt.match(pattern)
    if (match && match[1]) {
      return match[1].trim()
    }
  }
  
  return null
}

export interface WalletPathConfig {
  /** 完整 BIP44 path，如 m/44'/10001'/0'/0/1 */
  path?: string
  /** 仅索引号，如 “路径1” 中的 1 */
  index?: number
}

/**
 * 从用户提示词中解析钱包路径：
 * - “钱包路径使用1” / “路径1”        -> { index: 1 }
 * - “钱包路径使用m/44'/10001'/0'/0/1” -> { path: "m/44'/10001'/0'/0/1" }
 */
export function extractWalletPathFromPrompt(prompt: string): WalletPathConfig | null {
  if (!prompt) return null

  // 1. 优先解析完整 BIP44 path（允许前后有其他文字）
  const pathMatch = prompt.match(/m\/44'\/10001'\/0'\/0\/\d+/)
  if (pathMatch) {
    return { path: pathMatch[0] }
  }

  // 2. 解析纯索引写法：“钱包路径使用1”、“路径1”、“路径为 2”
  const indexMatch =
    prompt.match(/钱包路径(?:为|是|使用|用)?\s*([0-9]+)/i) ||
    prompt.match(/路径(?:为|是|使用|用)?\s*([0-9]+)/i)

  if (indexMatch && indexMatch[1]) {
    const idx = parseInt(indexMatch[1], 10)
    if (!Number.isNaN(idx)) {
      return { index: idx }
    }
  }

  return null
}

// Check if prompt indicates wallet creation
export function shouldCreateWallet(prompt: string): boolean {
  const createKeywords = [
    '创建一个',
    '创建',
    '新建',
    '生成',
    'create',
    'new',
    'generate'
  ]
  
  const agentKeywords = [
    'metaid agent',
    'metaid代理',
    'metaid机器人',
    '代理',
    '机器人',
    'agent',
    'robot',
    'proxy'
  ]
  
  const lowerPrompt = prompt.toLowerCase()
  const hasCreateKeyword = createKeywords.some(kw => lowerPrompt.includes(kw))
  const hasAgentKeyword = agentKeywords.some(kw => lowerPrompt.includes(kw))
  
  return hasCreateKeyword && hasAgentKeyword
}
