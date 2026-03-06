# 🧠 AI协作操作系统 - 完整使用说明书

**版本：1.0.0 | 更新日期：2026年2月25日**

---

## 目录

1. [系统概述](#1-系统概述)
2. [安装部署](#2-安装部署)
3. [快速开始](#3-快速开始)
4. [统一记忆系统](#4-统一记忆系统)
5. [信息信号识别系统](#5-信息信号识别系统)
6. [工作流资产沉淀系统](#6-工作流资产沉淀系统)
7. [个人目标追踪系统](#7-个人目标追踪系统)
8. [时间衰减机制](#8-时间衰减机制)
9. [值班机制应用](#9-值班机制应用)
10. [API完整参考](#10-api完整参考)
11. [配置说明](#11-配置说明)
12. [使用示例](#12-使用示例)
13. [最佳实践](#13-最佳实践)
14. [常见问题](#14-常见问题)
15. [故障排除](#15-故障排除)

---

## 1. 系统概述

### 1.1 什么是AI协作操作系统

AI协作操作系统是一套完整的个人成长和知识管理工具，包含四个核心系统：

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI协作操作系统架构                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │              AICollaborationSystem (主类)               │  │
│   │                                                         │  │
│   │   const ai = new AICollaborationSystem('my_system');    │  │
│   │                                                         │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              ▼                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │              UnifiedMemorySystem (统一记忆)              │  │
│   │                                                         │  │
│   │   L0闪存 → L1工作 → L2经验 → L3知识 → L4智慧            │  │
│   │                                                         │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                  │
│           ┌──────────────────┼──────────────────┐              │
│           │                  │                  │              │
│           ▼                  ▼                  ▼              │
│   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│   │SignalRecognition│ │WorkflowAsset    │ │PersonalGoal     │  │
│   │System           │ │System           │ │System           │  │
│   │                 │ │                 │ │                 │  │
│   │ 信息信号识别    │ │ 工作流资产沉淀  │ │ 个人目标追踪    │  │
│   │                 │ │                 │ │                 │  │
│   │ • 信号分层      │ │ • 隐性知识显性化│ │ • 动机解析      │  │
│   │ • 模式发现      │ │ • 能力基因识别  │ │ • AI镜像        │  │
│   │ • 时间衰减      │ │ • 方法论构建    │ │ • 未来预测      │  │
│   └─────────────────┘ └─────────────────┘ └─────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 四大核心系统

| 系统 | 核心功能 | 应用场景 |
|------|----------|----------|
| **统一记忆系统** | 五层记忆架构管理 | 数据存储、知识沉淀、智慧积累 |
| **信息信号识别** | 信息价值评估、过滤噪音 | 热点监测、趋势发现、决策支持 |
| **工作流资产沉淀** | 隐性知识显性化 | 能力沉淀、方法论构建、经验传承 |
| **个人目标追踪** | 目标管理、AI镜像 | 自我认知、精力管理、成长追踪 |

### 1.3 核心特性

- ✅ **一站式集成**：四个系统自动关联，共享记忆
- ✅ **五层记忆架构**：从临时变量到人生智慧
- ✅ **自动流转**：记忆自动归档、升级
- ✅ **时间衰减机制**：不错过最新信息，过期自动降级
- ✅ **AI镜像洞察**：发现认知盲点，预测未来
- ✅ **开箱即用**：解压安装即可使用

---

## 2. 安装部署

### 2.1 系统要求

| 项目 | 要求 |
|------|------|
| Node.js | >= 16.0.0 |
| npm | >= 7.0.0 |
| 操作系统 | Windows / macOS / Linux |
| 磁盘空间 | >= 100MB |

### 2.2 安装步骤

#### 方式一：一键安装（推荐）

```bash
# 1. 解压部署包
unzip ai-collaboration-complete.zip

# 2. 进入目录
cd ai-collaboration-complete

# 3. 执行一键安装脚本
./install.sh
```

安装脚本会自动完成：
- 检查Node.js环境
- 安装依赖
- 编译TypeScript
- 创建记忆目录
- 运行测试验证

#### 方式二：手动安装

```bash
# 1. 解压
unzip ai-collaboration-complete.zip
cd ai-collaboration-complete

# 2. 安装依赖
npm install

# 3. 编译TypeScript
npm run build

# 4. 验证安装
node dist/example.js
```

### 2.3 验证安装

运行演示程序验证安装是否成功：

```bash
# 运行完整功能演示
node demo.js

# 运行值班机制演示
node duty-demo.js

# 运行时间衰减演示
node time-decay-demo.js
```

看到 `✅ 演示完成！` 表示安装成功。

### 2.4 目录结构

```
ai-collaboration-complete/
├── install.sh              # 一键安装脚本
├── README.md               # 快速开始
├── package.json            # 项目配置
├── tsconfig.json           # TypeScript配置
├── LICENSE                 # MIT许可证
│
├── scripts/                # TypeScript源代码
│   ├── index.ts            # 主入口
│   ├── example.ts          # 基础示例
│   ├── core/
│   │   └── memory.ts       # 统一记忆系统核心
│   └── systems/
│       ├── signal.ts       # 信息信号识别系统
│       ├── workflow.ts     # 工作流资产沉淀系统
│       └── goal.ts         # 个人目标追踪系统
│
├── dist/                   # 编译输出（可直接使用）
│   ├── index.js            # 主入口
│   ├── example.js          # 基础示例
│   ├── core/
│   │   └── memory.js       # 记忆系统
│   └── systems/
│       ├── signal.js       # 信号系统
│       ├── workflow.js     # 工作流系统
│       └── goal.js         # 目标系统
│
├── demo.js                 # 完整功能演示
├── duty-demo.js            # 值班机制演示
├── time-decay-demo.js      # 时间衰减演示
│
├── docs/                   # 文档
│   ├── 完整使用手册.md
│   └── 集中部署指南.md
│
└── memory/                 # 记忆存储目录
    └── my_system/          # 按技能名分类
        ├── L0_flash/       # 闪存
        ├── L1_working/     # 工作记忆
        ├── L2_experience/  # 经验记忆
        ├── L3_knowledge/   # 知识记忆
        ├── L4_wisdom/      # 智慧记忆
        ├── shared/         # 跨系统共享
        └── logs/           # 日志
```

---

## 3. 快速开始

### 3.1 第一个程序

创建文件 `my-first-app.js`：

```javascript
// 导入系统
const { AICollaborationSystem } = require('./dist/index');

// 创建实例（一行代码完成所有初始化）
const ai = new AICollaborationSystem('my_first_app');

// 获取系统摘要
console.log(ai.getSummary());

// 存储一条记忆
ai.memory.addToL1('今日任务', '学习AI协作系统', 'task', 3);

// 查询记忆
const results = ai.memory.queryAll('任务');
console.log('查询结果:', results);

// 生成AI镜像洞察
const insight = ai.generateInsight();
console.log('AI洞察:', insight);
```

运行：

```bash
node my-first-app.js
```

### 3.2 基础使用流程

```javascript
const { AICollaborationSystem } = require('./dist/index');

// 1. 初始化系统
const ai = new AICollaborationSystem('my_app', 'memory');

// 2. 使用统一记忆系统
ai.memory.setVariable('user', '张三');           // L0闪存
ai.memory.addToL1('任务', '完成报告', 'task', 3); // L1工作记忆
ai.memory.addToL2('经验', '经验内容', 'insight', 4, ['tag']); // L2经验记忆

// 3. 使用信息信号识别
const signals = [
  { title: '热点1', source: '来源', timeSensitivity: 'immediate', 
    impactDepth: 'worldview', actionability: 8, compoundValue: 9 }
];
const report = ai.dailyScan(signals);
console.log(report);

// 4. 使用工作流沉淀
const tasks = ['完成任务A'];
const responses = [{ operation: '步骤', experience: '经验' }];
const workflow = ai.dailyWorkflow(tasks, responses);
console.log(workflow);

// 5. 使用目标追踪
const goals = [{ name: '目标1', priority: 8, progress: 30 }];
const timeLog = { career: 40, family: 20, health: 10 };
const energy = ai.dailyGoalTracking(goals, timeLog, { career: 35, family: 25, health: 15 });
console.log(energy);

// 6. 健康检查
const health = ai.healthCheck();
console.log(health);
```

---

## 4. 统一记忆系统

### 4.1 五层记忆架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     五层记忆架构                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   【L0 闪存】临时变量、对话上下文                               │
│   ├── 容量：10条                                                │
│   ├── 生命周期：当前会话                                        │
│   ├── 访问速度：实时                                            │
│   └── 用途：临时数据存储                                        │
│                                                                 │
│   【L1 工作记忆】当前任务、核心规则                             │
│   ├── 容量：50行                                                │
│   ├── 生命周期：当前任务周期                                    │
│   ├── 访问速度：实时                                            │
│   └── 用途：当前工作内容                                        │
│                                                                 │
│   【L2 经验记忆】经验教训、能力基因                             │
│   ├── 容量：200条                                               │
│   ├── 生命周期：长期                                            │
│   ├── 访问速度：快速检索                                        │
│   └── 用途：经验沉淀                                            │
│                                                                 │
│   【L3 知识记忆】方法论、世界观、能力模型                       │
│   ├── 容量：1000条                                              │
│   ├── 生命周期：永久                                            │
│   ├── 访问速度：结构化查询                                      │
│   └── 用途：知识体系                                            │
│                                                                 │
│   【L4 智慧记忆】人生洞察、核心价值观                           │
│   ├── 容量：无限制                                              │
│   ├── 生命周期：永久                                            │
│   ├── 访问速度：按需查询                                        │
│   └── 用途：人生智慧                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 L0 闪存使用

L0闪存用于存储临时变量和对话上下文。

```javascript
// 设置变量
ai.memory.setVariable('current_user', '张三');
ai.memory.setVariable('session_id', 'session_001');
ai.memory.setVariable('task_count', 5);

// 获取变量
const user = ai.memory.getVariable('current_user');
console.log('当前用户:', user);

// 获取所有变量
const allVars = ai.memory.getAllVariables();
console.log('所有变量:', allVars);

// 设置上下文
ai.memory.setContext('正在处理用户登录请求');
const context = ai.memory.getContext();
console.log('当前上下文:', context);
```

**使用场景**：
- 存储当前会话状态
- 临时计算结果
- 用户偏好设置
- 对话上下文

### 4.3 L1 工作记忆使用

L1工作记忆用于存储当前任务和核心规则。

```javascript
// 添加任务
ai.memory.addToL1('今日目标', '完成AI系统演示', 'task', 4);

// 添加规则
ai.memory.addToL1('核心规则', '所有输出必须有结构化格式', 'rule', 5);

// 添加洞察
ai.memory.addToL1('关键发现', '用户更倾向于简洁的输出', 'insight', 4);

// 查询工作记忆
const results = ai.memory.queryL1('目标');
console.log('查询结果:', results);

// 获取全部内容
const content = ai.memory.getL1Content();
console.log('工作记忆内容:', content);
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| key | string | 记忆标题 |
| value | string | 记忆内容 |
| category | string | 类别：task/rule/insight/pattern |
| importance | number | 重要程度：1-5 |

### 4.4 L2 经验记忆使用

L2经验记忆用于存储经验教训和能力基因。

```javascript
// 添加成功经验
ai.memory.addToL2(
  '成功经验_项目演示',
  {
    task: '完成系统演示',
    result: '成功',
    key: '清晰的输出格式让用户更容易理解',
    lessons: ['提前准备示例', '结构化输出']
  },
  'insight',
  4,
  ['success', 'demo', 'presentation'],
  'shared'
);

// 添加踩坑记录
ai.memory.addToL2(
  '踩坑记录_数据存储',
  {
    issue: '忘记创建目录导致存储失败',
    solution: '添加自动创建目录逻辑',
    prevention: '存储前检查目录是否存在'
  },
  'insight',
  3,
  ['error', 'fix', 'storage'],
  'shared'
);

// 查询经验
const experiences = ai.memory.queryL2('经验', 'success', 3);
console.log('成功经验:', experiences);

// 按标签查询
const taggedResults = ai.memory.queryL2('', 'demo', 0);
console.log('演示相关:', taggedResults);
```

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| key | string | 记忆标题 |
| value | string/object | 记忆内容 |
| category | string | 类别：task/insight/pattern/methodology |
| importance | number | 重要程度：1-5 |
| tags | string[] | 标签数组 |
| system | string | 来源系统：signal/workflow/goal/shared |

### 4.5 L3 知识记忆使用

L3知识记忆用于存储方法论、世界观和能力模型。

```javascript
// 添加方法论
ai.memory.addToL3({
  id: '',
  level: 'L3',
  category: 'methodology',
  key: 'AI协作方法论',
  value: {
    name: 'AI协作五步法',
    steps: [
      '1.明确目标',
      '2.收集信息',
      '3.分析决策',
      '4.执行沉淀',
      '5.复盘优化'
    ],
    principles: ['简洁优先', '结构化输出', '持续迭代']
  },
  tags: ['methodology', 'ai-collaboration'],
  importance: 5,
  system: 'shared',
  createdAt: new Date().toISOString(),
  accessedAt: new Date().toISOString(),
  accessCount: 0
});

// 添加世界观
ai.memory.addToL3({
  id: '',
  level: 'L3',
  category: 'worldview',
  key: 'AI发展趋势',
  value: {
    observation: 'AI正在从工具变为伙伴',
    evidence: ['GPT能力提升', 'Agent应用增多'],
    implication: '需要学习与AI协作的能力'
  },
  tags: ['worldview', 'ai-trend'],
  importance: 5,
  system: 'signal',
  createdAt: new Date().toISOString(),
  accessedAt: new Date().toISOString(),
  accessCount: 0
});

// 查询方法论
const methodologies = ai.memory.queryL3('methodology');
console.log('方法论:', methodologies);

// 查询世界观
const worldviews = ai.memory.queryL3('worldview');
console.log('世界观:', worldviews);

// 查询所有L3
const allL3 = ai.memory.queryL3();
console.log('所有知识:', allL3);
```

**类别说明**：

| 类别 | 说明 | 示例 |
|------|------|------|
| methodology | 方法论 | 工作方法、决策框架 |
| worldview | 世界观 | 行业趋势、认知模型 |
| pattern | 能力模型 | 能力基因、行为模式 |
| goal | 目标体系 | 人生目标、价值观 |

### 4.6 L4 智慧记忆使用

L4智慧记忆用于存储人生洞察和核心价值观。

```javascript
// 添加人生洞察
ai.memory.addToL4({
  id: '',
  level: 'L4',
  category: 'insight',
  key: '关于成长的洞察',
  value: {
    observation: '持续学习比天赋更重要',
    evidence: '观察身边成功人士的共同特点',
    implication: '每天进步1%，一年后提升37倍',
    action: '建立每日学习习惯'
  },
  tags: ['insight', 'growth'],
  importance: 5,
  system: 'goal',
  createdAt: new Date().toISOString(),
  accessedAt: new Date().toISOString(),
  accessCount: 0
});

// 添加核心价值观
ai.memory.addToL4({
  id: '',
  level: 'L4',
  category: 'value',
  key: '核心价值观',
  value: {
    values: ['诚信', '成长', '贡献'],
    description: '诚信是基础，成长是路径，贡献是目标'
  },
  tags: ['value', 'core'],
  importance: 5,
  system: 'goal',
  createdAt: new Date().toISOString(),
  accessedAt: new Date().toISOString(),
  accessCount: 0
});

// 查询洞察
const insights = ai.memory.queryL4('insight');
console.log('人生洞察:', insights);

// 查询价值观
const values = ai.memory.queryL4('value');
console.log('核心价值观:', values);
```

### 4.7 统一查询

```javascript
// 跨层级统一查询
const results = ai.memory.queryAll('关键词');

console.log('L0结果:', results.L0);
console.log('L1结果:', results.L1);
console.log('L2结果:', results.L2);
console.log('L3结果:', results.L3);
console.log('L4结果:', results.L4);
```

### 4.8 跨系统同步

```javascript
// 同步数据到其他系统
const entries = ai.memory.queryL2('重要');
ai.memory.syncToSystem('signal', entries);
ai.memory.syncToSystem('workflow', entries);
ai.memory.syncToSystem('goal', entries);

// 从其他系统获取同步数据
const signalData = ai.memory.syncFromSystem('signal');
const workflowData = ai.memory.syncFromSystem('workflow');
const goalData = ai.memory.syncFromSystem('goal');
```

### 4.9 记忆自动流转

系统会自动进行记忆流转：

```
L0闪存(满10条) → 自动转存到L1
L1工作记忆(满50行) → 自动归档到L2
L2经验记忆(满200条) → 高价值条目自动升级到L3
L3知识记忆 → 核心洞察可手动升级到L4
```

---

## 5. 信息信号识别系统

### 5.1 系统概述

信息信号识别系统用于从海量信息中识别有价值的信号，过滤噪音。

```
┌─────────────────────────────────────────────────────────────────┐
│                   信息信号识别流程                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   【输入】原始信息列表                                          │
│      ↓                                                          │
│   【评估】计算综合价值                                          │
│      ├── 时间敏感度 (0-10)                                      │
│      ├── 影响深度 (0-10)                                        │
│      ├── 可行动性 (0-10)                                        │
│      └── 复利价值 (0-10)                                        │
│      ↓                                                          │
│   【分层】信号等级划分                                          │
│      ├── 元信号(meta): 综合价值≥8，改变世界观                   │
│      ├── 核心信号(core): 综合价值≥6，影响决策                   │
│      ├── 普通信号(signal): 综合价值≥3，值得关注                 │
│      └── 噪音(noise): 综合价值<3，可忽略                        │
│      ↓                                                          │
│   【时间衰减】应用时间衰减机制                                  │
│      ├── 0-1天: 100%，不衰减                                    │
│      ├── 1-3天: 90%，轻微衰减                                   │
│      ├── 3-7天: 70%，中度衰减                                   │
│      ├── 7-14天: 40%，重度衰减，默认不显示                      │
│      └── 14天以上: 10%，极低，仅存档                            │
│      ↓                                                          │
│   【输出】处理后的信号列表                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 信号评估维度

| 维度 | 说明 | 评分范围 |
|------|------|----------|
| timeSensitivity | 时间敏感度 | immediate(2)/continuous(6)/delayed(8)/cyclical(4)/meta(10) |
| impactDepth | 影响深度 | tool(2)/method(4)/strategy(6)/cognition(8)/worldview(10) |
| actionability | 可行动性 | 0-10 |
| compoundValue | 复利价值 | 0-10 |

### 5.3 基础使用

```javascript
// 定义原始信号
const rawSignals = [
  {
    title: 'OpenAI发布GPT-5',
    source: 'OpenAI官方',
    timeSensitivity: 'immediate',
    impactDepth: 'worldview',
    actionability: 9,
    compoundValue: 10,
    publishDate: new Date()  // 发布时间（用于时间衰减）
  },
  {
    title: '某明星八卦',
    source: '娱乐新闻',
    timeSensitivity: 'immediate',
    impactDepth: 'tool',
    actionability: 1,
    compoundValue: 1,
    publishDate: new Date()
  }
];

// 生成每日扫描报告
const report = ai.signal.generateDailyScanReport(
  '2026-02-25',
  rawSignals
);

// 查看结果
console.log('信号列表:', report.signals);
console.log('发现模式:', report.patterns);
console.log('行动建议:', report.actions);
```

### 5.4 信号等级说明

```javascript
// 信号等级判断标准
const signalLevels = {
  meta: {
    threshold: 8,
    description: '元信号，改变世界观',
    action: '立即关注，可能需要调整战略',
    storage: 'L2经验记忆 + L3世界观'
  },
  core: {
    threshold: 6,
    description: '核心信号，影响决策',
    action: '重点关注，纳入决策考量',
    storage: 'L2经验记忆'
  },
  signal: {
    threshold: 3,
    description: '普通信号，值得关注',
    action: '记录备案，持续观察',
    storage: 'L1工作记忆'
  },
  noise: {
    threshold: 0,
    description: '噪音，可忽略',
    action: '不存储',
    storage: '不存储'
  }
};
```

### 5.5 时间衰减机制

```javascript
// 时间衰减配置
const TIME_DECAY_CONFIG = {
  DEFAULT_MAX_AGE_DAYS: 7,  // 默认显示最近7天
  
  DECAY_RATES: {
    '0-1天': 1.0,      // 当天/昨天：不衰减
    '1-3天': 0.9,      // 1-3天：轻微衰减
    '3-7天': 0.7,      // 3-7天：中度衰减
    '7-14天': 0.4,     // 7-14天：重度衰减
    '14天以上': 0.1    // 14天以上：极低
  },
  
  LEVEL_ADJUSTMENT: {
    '7天以上': { maxLevel: 'B级', defaultVisible: false },
    '14天以上': { maxLevel: 'C级', defaultVisible: false }
  }
};

// 应用时间衰减
function applyTimeDecay(signal) {
  const age = calculateAgeInDays(signal.publishDate);
  const decay = getDecayRate(age);
  
  // 应用衰减系数
  signal.adjustedScore = signal.rawScore * decay;
  
  // 应用等级限制
  if (age > 7) signal.maxLevel = 'B级';
  if (age > 14) signal.maxLevel = 'C级';
  
  // 设置默认可见性
  signal.defaultVisible = age <= 7;
  
  return signal;
}
```

### 5.6 查询历史信号

```javascript
// 查询信号
const signals = ai.signal.querySignals('AI');
console.log('AI相关信号:', signals);

// 查询特定等级的信号
const coreSignals = ai.signal.querySignals('')
  .filter(s => s.level === 'core');
console.log('核心信号:', coreSignals);
```

### 5.7 同步到其他系统

```javascript
// 同步世界观到其他系统
ai.signal.syncToOtherSystems();
```

---

## 6. 工作流资产沉淀系统

### 6.1 系统概述

工作流资产沉淀系统用于将隐性知识显性化，构建个人方法论。

```
┌─────────────────────────────────────────────────────────────────┐
│                   知识显性化五层模型                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   【第1层】操作步骤层 (Operation)                               │
│   ├── 内容：具体做了什么                                        │
│   ├── 发现方式：直接记录                                        │
│   └── 输出形式：流程文档                                        │
│                                                                 │
│   【第2层】经验技巧层 (Experience)                              │
│   ├── 内容：为什么这样做更好                                    │
│   ├── 发现方式：提问引导                                        │
│   └── 输出形式：技巧清单                                        │
│                                                                 │
│   【第3层】决策逻辑层 (Decision)                                │
│   ├── 内容：如果...会怎样                                       │
│   ├── 发现方式：情境假设                                        │
│   └── 输出形式：决策树                                          │
│                                                                 │
│   【第4层】思维模式层 (Thinking)                                │
│   ├── 内容：你是怎么想的                                        │
│   ├── 发现方式：深度对话                                        │
│   └── 输出形式：思维模型                                        │
│                                                                 │
│   【第5层】价值观层 (Value)                                     │
│   ├── 内容：这对你意味着什么                                    │
│   ├── 发现方式：深度对话                                        │
│   └── 输出形式：价值宣言                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 基础使用

```javascript
// 定义任务和响应
const tasks = ['完成产品需求文档', '主持团队周会'];
const responses = [
  {
    operation: '1.用户调研 2.需求分析 3.文档撰写 4.评审修改',
    experience: '调研阶段多花时间，后期返工少',
    decision: '如果时间紧，先写核心功能，次要功能后续迭代',
    thinking: '从用户价值出发，而非功能堆砌',
    value: '用户价值第一，团队效率第二'
  },
  {
    operation: '1.同步进度 2.讨论问题 3.分配任务',
    experience: '周会时间控制在1小时内效果最好',
    decision: '如果有争议，先记录后续单独讨论',
    thinking: '周会是同步信息，不是解决问题',
    value: '高效沟通比长时间讨论更重要'
  }
];

// 生成工作流报告
const report = ai.workflow.generateDailyWorkflowReport(
  '2026-02-25',
  tasks,
  responses
);

// 查看结果
console.log('隐性知识:', report.tacitKnowledge);
console.log('能力基因:', report.capabilityGenes);
console.log('方法论:', report.methodologies);
```

### 6.3 隐性知识结构

```javascript
// 隐性知识对象结构
const tacitKnowledge = {
  level: 'operation',  // 层级
  content: '具体内容',
  discoveryMethod: '发现方式',
  outputForm: '输出形式'
};
```

### 6.4 能力基因识别

系统会自动识别能力基因：

```javascript
// 能力基因结构
const capabilityGene = {
  name: '判断能力',           // 基因名称
  category: 'decision',       // 类别
  description: '决策逻辑描述', // 描述
  manifestation: '在XX任务中体现', // 表现场景
  transferableScenarios: ['类似决策场景'], // 可迁移场景
  strength: 'medium'          // 强度：high/medium/low
};
```

### 6.5 方法论构建

```javascript
// 方法论结构
const methodology = {
  name: '工作方法论',
  levels: {
    philosophy: '用户价值第一',  // 哲学层
    principles: ['从用户价值出发'], // 原则层
    methods: ['如果时间紧，先核心'], // 方法层
    processes: ['调研→分析→撰写'], // 流程层
    tools: ['文档模板']          // 工具层
  },
  validation: '待验证'
};
```

### 6.6 查询方法论

```javascript
// 查询已沉淀的方法论
const methodologies = ai.workflow.queryMethodologies();
console.log('方法论列表:', methodologies);
```

---

## 7. 个人目标追踪系统

### 7.1 系统概述

个人目标追踪系统用于管理目标、追踪进度、发现盲点。

```
┌─────────────────────────────────────────────────────────────────┐
│                   个人目标追踪流程                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   【输入】                                                      │
│   ├── 目标列表                                                  │
│   ├── 时间日志                                                  │
│   ├── 理想分配                                                  │
│   └── 声称优先级                                                │
│                                                                 │
│   【处理】                                                      │
│   ├── 动机解析 → 识别深层动机                                   │
│   ├── 目标网络 → 发现目标关系                                   │
│   ├── 精力分配 → 分析实际投入                                   │
│   └── 盲点发现 → 识别言行不一                                   │
│                                                                 │
│   【输出】                                                      │
│   ├── AI镜像信 → 个性化反馈                                     │
│   ├── 未来预测 → 发展趋势预测                                   │
│   └── 下周建议 → 行动建议                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 基础使用

```javascript
// 定义目标
const goals = [
  {
    name: '学习AI技术',
    description: '掌握AI相关技术',
    priority: 8,
    progress: 35,
    deadline: new Date('2026-12-31'),
    motivations: []
  },
  {
    name: '保持健康',
    description: '每周运动3次',
    priority: 9,
    progress: 50,
    deadline: new Date('2026-12-31'),
    motivations: []
  }
];

// 定义时间日志
const timeLog = {
  career: 45,    // 工作45小时
  family: 15,    // 家庭15小时
  health: 3,     // 健康3小时
  learning: 8,   // 学习8小时
  social: 5,     // 社交5小时
  leisure: 8     // 休闲8小时
};

// 定义理想分配
const idealAllocation = {
  career: 35,
  family: 25,
  health: 15,
  learning: 15,
  social: 5,
  leisure: 5
};

// 定义声称优先级
const statedPriorities = {
  career: 8,
  family: 9,
  health: 9,
  learning: 8,
  social: 5,
  leisure: 4
};

// 生成每周报告
const report = ai.goal.generateWeeklySelfAwarenessReport(
  '本周',
  goals,
  timeLog,
  idealAllocation,
  statedPriorities
);

// 查看结果
console.log('精力分配:', report.energyAllocation);
console.log('认知盲点:', report.blindSpots);
console.log('AI镜像:', report.mirrorFeedback);
```

### 7.3 动机解析

```javascript
// 解析目标动机
const motivations = ai.goal.analyzeMotivation(goals[0], {
  safety: '需要AI技能保住工作',
  social: '希望被认可为技术专家',
  esteem: '获得成就感',
  'self-actualization': '实现自我价值',
  meaning: '帮助更多人使用AI'
});

console.log('动机层次:', motivations);
```

### 7.4 目标网络构建

```javascript
// 构建目标网络
const network = ai.goal.buildGoalNetwork(goals);

console.log('目标关系:', network.relations);
// 输出示例：
// [
//   { goalA: '学习AI技术', goalB: '升职加薪', relation: 'synergistic', reason: '相互促进' },
//   { goalA: '学习AI技术', goalB: '保持健康', relation: 'competitive', reason: '争夺时间资源' }
// ]
```

### 7.5 精力分配分析

```javascript
// 分析精力分配
const allocation = ai.goal.analyzeEnergyAllocation(timeLog, idealAllocation);

// 输出示例：
// [
//   { dimension: 'career', actualPercentage: 54, idealPercentage: 35, gap: 19, status: '过度' },
//   { dimension: 'health', actualPercentage: 4, idealPercentage: 15, gap: -11, status: '不足' }
// ]
```

### 7.6 AI镜像洞察

```javascript
// 生成AI镜像信
const mirrorLetter = ai.goal.generateAIMirrorLetter(
  '本周我观察到你在多个领域都有投入',
  ['目标"保持健康"有进展'],
  [{ observation: '声称健康优先级为9，但实际投入4%', concern: '言行不一', suggestion: '重新评估' }],
  ['你是否思考过这些目标对你的真正意义？'],
  ['基于你的能力，我看到了更多可能性'],
  ['建议下周重点关注精力分配的平衡']
);

console.log('AI镜像信:', mirrorLetter);
```

### 7.7 未来预测

```javascript
// 预测未来自我
const predictions = ai.goal.predictFutureSelf(
  goals,
  allocation,
  ['每天学习1小时', '每周运动2次']
);

console.log('未来预测:', predictions);
// 输出示例：
// [
//   { timeframe: '3个月后', capabilityState: '能力稳步提升', ... },
//   { timeframe: '6个月后', capabilityState: '显著提升', ... },
//   { timeframe: '1年后', capabilityState: '成为专家', ... }
// ]
```

---

## 8. 时间衰减机制

### 8.1 机制概述

时间衰减机制确保系统始终关注最新信息，过期信息自动降级。

### 8.2 衰减规则

```
┌─────────────────────────────────────────────────────────────────┐
│                     时间衰减规则                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   信息年龄      衰减系数    等级限制      默认显示              │
│   ────────────────────────────────────────────────────────────  │
│   0-1天         100%       可评S级       ✅ 显示                │
│   1-3天         90%        可评S级       ✅ 显示                │
│   3-7天         70%        最高A级       ✅ 显示                │
│   7-14天        40%        最高B级       ❌ 不显示              │
│   14天以上      10%        C级           ❌ 不显示              │
│                                                                 │
│   核心原则：                                                    │
│   • 不错过最新信息                                              │
│   • 当天信息优先级最高                                          │
│   • 一周以上自动降级                                            │
│   • 历史信息可手动查询                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 使用示例

```javascript
// 带发布时间的信号
const signals = [
  {
    title: '刚刚发生的重大事件',
    source: '官方',
    publishDate: new Date(),  // 今天
    timeSensitivity: 'immediate',
    impactDepth: 'worldview',
    actionability: 9,
    compoundValue: 10
  },
  {
    title: '一周前的新闻',
    source: '媒体',
    publishDate: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000),  // 8天前
    timeSensitivity: 'immediate',
    impactDepth: 'strategy',
    actionability: 7,
    compoundValue: 6
  }
];

// 系统会自动应用时间衰减
const report = ai.signal.generateDailyScanReport('2026-02-25', signals);

// 结果：只有今天的新闻会默认显示，一周前的新闻被过滤
```

### 8.4 手动查询历史

```javascript
// 如需查看历史信息，可手动查询
// 查询最近30天的信息
const history = ai.memory.queryL2('')
  .filter(e => {
    const age = (Date.now() - new Date(e.createdAt)) / (24 * 60 * 60 * 1000);
    return age <= 30;
  });

console.log('最近30天的信息:', history);
```

---

## 9. 值班机制应用

### 9.1 应用场景

春节值班机制是信息信号识别系统的典型应用场景：

- 每天监测产业科技热点
- 自动评估关注等级
- 生成每日热点日报
- 触发深度分析机制

### 9.2 完整实现

```javascript
const { AICollaborationSystem } = require('./dist/index');

// 初始化系统
const ai = new AICollaborationSystem('duty_system');

// ===== 第一步：定义值班机制 =====
ai.memory.addToL3({
  id: '',
  level: 'L3',
  category: 'methodology',
  key: '春节值班机制',
  value: {
    name: '春节产业热点监测值班机制',
    schedule: { time: '每天2位同学值班' },
    tasks: [
      { time: '09:00', task: '开始监测热点' },
      { time: '18:00', task: '发布当日总结' }
    ]
  },
  tags: ['duty', 'mechanism'],
  importance: 5,
  system: 'workflow',
  createdAt: new Date().toISOString(),
  accessedAt: new Date().toISOString(),
  accessCount: 0
});

// ===== 第二步：监测热点 =====
const todayHotspots = [
  {
    title: 'OpenAI发布GPT-5',
    source: '官方公告',
    publishDate: new Date(),
    timeSensitivity: 'immediate',
    impactDepth: 'worldview',
    actionability: 9,
    compoundValue: 10,
    // 舆论维度
    publicAttention: 95,
    discussionVolume: 50000,
    emotionIntensity: 90
  },
  // ... 更多热点
];

// ===== 第三步：评估关注等级 =====
function evaluateHotspot(hotspot) {
  // 基础价值评估
  const baseValue = ai.signal.evaluateSignal(hotspot);
  
  // 舆论热度评分
  const attentionScore = (
    hotspot.publicAttention * 0.4 +
    (hotspot.discussionVolume / 1000) * 0.3 +
    hotspot.emotionIntensity * 0.3
  );
  
  // 时间衰减
  const age = (Date.now() - new Date(hotspot.publishDate)) / (24 * 60 * 60 * 1000);
  let decayRate = 1.0;
  if (age > 7) decayRate = 0.4;
  if (age > 14) decayRate = 0.1;
  
  // 最终评分
  const finalScore = attentionScore * decayRate;
  
  // 确定等级
  let level = 'C级';
  let needAnalysis = false;
  
  if (finalScore >= 75 && age <= 7) {
    level = 'S级';
    needAnalysis = true;
  } else if (finalScore >= 60) {
    level = 'A级';
  } else if (finalScore >= 40) {
    level = 'B级';
  }
  
  // 7天以上强制降级
  if (age > 7) level = 'B级';
  if (age > 14) level = 'C级';
  
  return { ...hotspot, level, finalScore, needAnalysis };
}

// ===== 第四步：生成日报 =====
function generateDailyReport(hotspots, dutyPersons) {
  const evaluated = hotspots.map(evaluateHotspot);
  const visible = evaluated.filter(h => h.level !== 'C级');
  
  return {
    date: new Date().toLocaleDateString('zh-CN'),
    dutyPersons,
    hotspots: visible,
    alertCount: evaluated.filter(h => h.needAnalysis).length,
    summary: `共监测${hotspots.length}条热点，S级${evaluated.filter(h=>h.level==='S级').length}条`
  };
}

// ===== 第五步：执行 =====
const report = generateDailyReport(todayHotspots, ['张三', '李四']);
console.log('日报:', report);
```

### 9.3 触发深度分析的条件

满足**任一条件**即触发深度分析：

| 条件 | 阈值 |
|------|------|
| 舆论关注度 | ≥ 80 |
| 讨论量 | ≥ 30000 |
| 情绪强度 | ≥ 85 |
| 综合评分 | ≥ 75 |
| 影响深度 | = worldview |

### 9.4 输出模板

**每日热点日报模板**：

```
【X月X日 产业热点日报】

值班人员：XXX、XXX

【S级热点】（需要深度分析）
• 标题：XXX
  评分：XX | 来源：XXX
  简要：XXX

【A级热点】（高度关注）
• 标题：XXX
  评分：XX | 来源：XXX
  简要：XXX

【B级热点】（持续跟踪）
• 标题：XXX
  评分：XX

【今日统计】
共监测X条热点，S级X条，A级X条，B级X条

【待处理事项】
• 需要输出分析材料：X条
```

---

## 10. API完整参考

### 10.1 AICollaborationSystem 主类

```typescript
class AICollaborationSystem {
  // 属性
  memory: UnifiedMemorySystem;
  signal: SignalRecognitionSystem;
  workflow: WorkflowAssetSystem;
  goal: PersonalGoalSystem;
  
  // 构造函数
  constructor(skillName?: string, baseDir?: string, config?: Partial<MemoryConfig>);
  
  // 便捷方法
  getSummary(): string;
  healthCheck(): object;
  generateInsight(): AIMirrorInsight;
  syncAllSystems(): void;
  queryAll(query: string): object;
  
  // 每日工作流
  dailyScan(rawSignals: any[]): object;
  dailyWorkflow(tasks: string[], responses: any[]): object;
  dailyGoalTracking(goals: any[], timeLog: object, ideal: object): object[];
  
  // 每周工作流
  weeklyReview(goals: any[], timeLog: any, ideal: any, priorities: any): object;
}
```

### 10.2 UnifiedMemorySystem

```typescript
class UnifiedMemorySystem {
  // L0 闪存
  setContext(context: string): void;
  getContext(): string;
  setVariable(key: string, value: any): void;
  getVariable(key: string): any;
  getAllVariables(): Record<string, any>;
  
  // L1 工作记忆
  addToL1(key: string, value: string, category: MemoryCategory, importance?: number): void;
  queryL1(pattern: string): MemoryEntry[];
  getL1Content(): string;
  
  // L2 经验记忆
  addToL2(key: string, value: string | object, category: MemoryCategory, 
          importance: number, tags?: string[], system?: SystemType): void;
  queryL2(query: string, tagFilter?: string, importanceMin?: number): MemoryEntry[];
  getL2Entries(): MemoryEntry[];
  
  // L3 知识记忆
  addToL3(entry: MemoryEntry): void;
  queryL3(category?: MemoryCategory): MemoryEntry[];
  getL3Data(): object;
  
  // L4 智慧记忆
  addToL4(entry: MemoryEntry): void;
  queryL4(category?: MemoryCategory): MemoryEntry[];
  getL4Data(): object;
  
  // 统一查询
  queryAll(query: string): Record<MemoryLevel, MemoryEntry[]>;
  
  // 跨系统共享
  syncToSystem(targetSystem: SystemType, entries: MemoryEntry[]): void;
  syncFromSystem(sourceSystem: SystemType): MemoryEntry[];
  
  // AI镜像
  generateMirrorInsight(): AIMirrorInsight;
  
  // 健康检查
  healthCheck(): object;
  
  // 摘要
  getSummary(): string;
  
  // 配置
  getConfig(): MemoryConfig;
  updateConfig(newConfig: Partial<MemoryConfig>): void;
}
```

### 10.3 SignalRecognitionSystem

```typescript
class SignalRecognitionSystem {
  // 评估信号
  evaluateSignal(signal: Omit<Signal, 'level' | 'reason'>): { level: SignalLevel; reason: string };
  
  // 添加信号
  addSignal(signal: Omit<Signal, 'level' | 'reason'>): void;
  
  // 生成日报
  generateDailyScanReport(date: string, rawSignals: Omit<Signal, 'level' | 'reason'>[]): {
    date: string;
    signals: Signal[];
    patterns: Pattern[];
    actions: string[];
  };
  
  // 查询信号
  querySignals(query: string): Signal[];
  
  // 同步
  syncToOtherSystems(): void;
}
```

### 10.4 WorkflowAssetSystem

```typescript
class WorkflowAssetSystem {
  // 隐性知识显性化
  explicitizeTacitKnowledge(task: string, userResponses: Record<KnowledgeLevel, string>): TacitKnowledge[];
  
  // 识别能力基因
  identifyCapabilityGenes(task: string, result: string, tacitKnowledge: TacitKnowledge[]): CapabilityGene[];
  
  // 构建方法论
  buildMethodology(tacitKnowledge: TacitKnowledge[], capabilityGenes: CapabilityGene[]): Methodology;
  
  // 生成日报
  generateDailyWorkflowReport(date: string, tasks: string[], userResponses: Record<KnowledgeLevel, string>[]): {
    date: string;
    tasks: string[];
    tacitKnowledge: TacitKnowledge[];
    capabilityGenes: CapabilityGene[];
    methodologies: Methodology[];
  };
  
  // 查询方法论
  queryMethodologies(): Methodology[];
  
  // 同步
  syncToOtherSystems(): void;
}
```

### 10.5 PersonalGoalSystem

```typescript
class PersonalGoalSystem {
  // 动机解析
  analyzeMotivation(goal: Goal, userResponses: Record<MotivationLevel, string>): Motivation[];
  
  // 构建目标网络
  buildGoalNetwork(goals: Goal[]): { goals: Goal[]; relations: object[] };
  
  // 分析精力分配
  analyzeEnergyAllocation(timeLog: Record<string, number>, idealAllocation: Record<string, number>): EnergyAllocation[];
  
  // 发现盲点
  discoverBlindSpots(goals: Goal[], energyAllocation: EnergyAllocation[], statedPriorities: Record<string, number>): object[];
  
  // 生成AI镜像信
  generateAIMirrorLetter(observations: string, progress: string[], concerns: object[], 
                         challenges: string[], possibilities: string[], recommendations: string[]): AIMirrorLetter;
  
  // 预测未来
  predictFutureSelf(goals: Goal[], energyAllocation: EnergyAllocation[], behaviorPatterns: string[]): object[];
  
  // 生成周报
  generateWeeklySelfAwarenessReport(period: string, goals: Goal[], timeLog: Record<string, number>,
                                    idealAllocation: Record<string, number>, statedPriorities: Record<string, number>): object;
  
  // 同步
  syncToOtherSystems(): void;
}
```

### 10.6 类型定义

```typescript
// 记忆层级
type MemoryLevel = 'L0' | 'L1' | 'L2' | 'L3' | 'L4';

// 记忆类别
type MemoryCategory = 'task' | 'rule' | 'insight' | 'pattern' | 'methodology' | 'worldview' | 'goal' | 'value' | 'wisdom';

// 系统类型
type SystemType = 'signal' | 'workflow' | 'goal' | 'shared';

// 记忆条目
interface MemoryEntry {
  id: string;
  level: MemoryLevel;
  category: MemoryCategory;
  key: string;
  value: string | object;
  tags: string[];
  importance: number;
  system: SystemType;
  createdAt: string;
  accessedAt: string;
  accessCount: number;
  metadata?: Record<string, any>;
}

// 信号等级
type SignalLevel = 'noise' | 'signal' | 'core' | 'meta';

// 时间敏感度
type TimeSensitivity = 'immediate' | 'continuous' | 'delayed' | 'cyclical' | 'meta';

// 影响深度
type ImpactDepth = 'tool' | 'method' | 'strategy' | 'cognition' | 'worldview';

// AI镜像洞察
interface AIMirrorInsight {
  observation: string;
  pattern: string;
  blindSpot: string;
  suggestion: string;
  prediction: string;
}
```

---

## 11. 配置说明

### 11.1 默认配置

```javascript
const DEFAULT_CONFIG = {
  // L0闪存最大条目数
  L0_MAX_ITEMS: 10,
  
  // L1工作记忆最大行数
  L1_MAX_LINES: 50,
  
  // L2经验记忆最大条目数
  L2_MAX_ENTRIES: 200,
  
  // L3知识记忆最大条目数
  L3_MAX_ENTRIES: 1000,
  
  // 自动归档阈值（百分比）
  AUTO_ARCHIVE_THRESHOLD: 0.8
};
```

### 11.2 自定义配置

```javascript
// 创建系统时自定义配置
const ai = new AICollaborationSystem('my_system', 'memory', {
  L0_MAX_ITEMS: 20,           // 增大L0容量
  L1_MAX_LINES: 100,          // 增大L1容量
  L2_MAX_ENTRIES: 500,        // 增大L2容量
  AUTO_ARCHIVE_THRESHOLD: 0.9 // 提高归档阈值
});

// 运行时更新配置
ai.memory.updateConfig({
  L1_MAX_LINES: 200
});

// 获取当前配置
const config = ai.memory.getConfig();
console.log('当前配置:', config);
```

### 11.3 时间衰减配置

```javascript
const TIME_DECAY_CONFIG = {
  // 默认显示最近N天的信息
  DEFAULT_MAX_AGE_DAYS: 7,
  
  // 时间衰减系数
  DECAY_RATES: {
    '0-1天': 1.0,
    '1-3天': 0.9,
    '3-7天': 0.7,
    '7-14天': 0.4,
    '14天以上': 0.1
  },
  
  // 等级调整规则
  LEVEL_ADJUSTMENT: {
    '7天以上': { maxLevel: 'B级', defaultVisible: false },
    '14天以上': { maxLevel: 'C级', defaultVisible: false }
  }
};
```

---

## 12. 使用示例

### 12.1 完整工作流示例

```javascript
const { AICollaborationSystem } = require('./dist/index');

async function main() {
  // ===== 1. 初始化系统 =====
  const ai = new AICollaborationSystem('daily_work', 'memory');
  console.log('系统初始化完成');
  console.log(ai.getSummary());
  
  // ===== 2. 早晨：信息扫描 =====
  console.log('\n===== 早晨：信息扫描 =====');
  
  const morningSignals = [
    {
      title: 'GPT-5发布预告',
      source: 'OpenAI官方',
      publishDate: new Date(),
      timeSensitivity: 'immediate',
      impactDepth: 'worldview',
      actionability: 9,
      compoundValue: 10,
      publicAttention: 95,
      discussionVolume: 50000,
      emotionIntensity: 90
    },
    {
      title: '某科技公司财报',
      source: '财经新闻',
      publishDate: new Date(),
      timeSensitivity: 'delayed',
      impactDepth: 'strategy',
      actionability: 6,
      compoundValue: 5,
      publicAttention: 60,
      discussionVolume: 10000,
      emotionIntensity: 40
    }
  ];
  
  const scanReport = ai.dailyScan(morningSignals);
  console.log('核心信号:', scanReport.signals.filter(s => s.level === 'core' || s.level === 'meta'));
  console.log('行动建议:', scanReport.actions);
  
  // ===== 3. 工作中：任务沉淀 =====
  console.log('\n===== 工作中：任务沉淀 =====');
  
  const tasks = ['完成产品需求文档', '参加团队周会'];
  const responses = [
    {
      operation: '1.调研 2.分析 3.撰写',
      experience: '调研要充分',
      decision: '先核心后细节',
      thinking: '用户价值优先',
      value: '质量第一'
    },
    {
      operation: '1.同步 2.讨论',
      experience: '控制在1小时',
      decision: '争议单独讨论',
      thinking: '同步为主',
      value: '高效沟通'
    }
  ];
  
  const workflowReport = ai.dailyWorkflow(tasks, responses);
  console.log('沉淀的方法论:', workflowReport.methodologies);
  
  // ===== 4. 晚上：目标追踪 =====
  console.log('\n===== 晚上：目标追踪 =====');
  
  const goals = [
    { name: '学习AI', priority: 8, progress: 35, deadline: new Date('2026-12-31'), motivations: [] },
    { name: '保持健康', priority: 9, progress: 50, deadline: new Date('2026-12-31'), motivations: [] }
  ];
  
  const timeLog = { career: 45, family: 15, health: 3, learning: 8, social: 5, leisure: 8 };
  const ideal = { career: 35, family: 25, health: 15, learning: 15, social: 5, leisure: 5 };
  const priorities = { career: 8, family: 9, health: 9, learning: 8, social: 5, leisure: 4 };
  
  const weeklyReport = ai.weeklyReview(goals, timeLog, ideal, priorities);
  console.log('精力分配:', weeklyReport.energyAllocation);
  console.log('认知盲点:', weeklyReport.blindSpots);
  
  // ===== 5. 睡前：AI镜像 =====
  console.log('\n===== 睡前：AI镜像 =====');
  
  const insight = ai.generateInsight();
  console.log('观察:', insight.observation);
  console.log('模式:', insight.pattern);
  console.log('盲点:', insight.blindSpot);
  console.log('建议:', insight.suggestion);
  console.log('预测:', insight.prediction);
  
  // ===== 6. 健康检查 =====
  console.log('\n===== 系统健康检查 =====');
  
  const health = ai.healthCheck();
  console.log('各层状态:', health.levels);
  console.log('建议:', health.recommendations);
  
  // ===== 7. 同步所有系统 =====
  ai.syncAllSystems();
  console.log('\n✅ 一天工作流完成！');
}

main().catch(console.error);
```

### 12.2 值班机制完整示例

```javascript
const { AICollaborationSystem } = require('./dist/index');

// 初始化值班系统
const ai = new AICollaborationSystem('duty_system');

// 模拟当天监测到的热点
const todayHotspots = [
  {
    title: 'OpenAI发布GPT-5',
    source: '官方公告',
    publishDate: new Date(),
    timeSensitivity: 'immediate',
    impactDepth: 'worldview',
    actionability: 9,
    compoundValue: 10,
    publicAttention: 95,
    discussionVolume: 50000,
    emotionIntensity: 90
  },
  {
    title: '某科技公司裁员传闻',
    source: '社交媒体',
    publishDate: new Date(),
    timeSensitivity: 'immediate',
    impactDepth: 'strategy',
    actionability: 6,
    compoundValue: 5,
    publicAttention: 75,
    discussionVolume: 20000,
    emotionIntensity: 85
  },
  {
    title: '新能源汽车销量数据',
    source: '行业报告',
    publishDate: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3天前
    timeSensitivity: 'delayed',
    impactDepth: 'strategy',
    actionability: 7,
    compoundValue: 6,
    publicAttention: 45,
    discussionVolume: 5000,
    emotionIntensity: 30
  }
];

// 评估每个热点
function evaluateHotspot(hotspot) {
  const baseValue = ai.signal.evaluateSignal(hotspot);
  
  // 计算舆论热度
  const attentionScore = (
    hotspot.publicAttention * 0.4 +
    (hotspot.discussionVolume / 1000) * 0.3 +
    hotspot.emotionIntensity * 0.3
  );
  
  // 计算时间衰减
  const age = (Date.now() - new Date(hotspot.publishDate)) / (24 * 60 * 60 * 1000);
  let decayRate = 1.0;
  if (age <= 1) decayRate = 1.0;
  else if (age <= 3) decayRate = 0.9;
  else if (age <= 7) decayRate = 0.7;
  else if (age <= 14) decayRate = 0.4;
  else decayRate = 0.1;
  
  // 最终评分
  const finalScore = attentionScore * decayRate;
  
  // 确定等级
  let level = 'C级';
  let needAnalysis = false;
  
  if (finalScore >= 75 && age <= 7) {
    level = 'S级';
    needAnalysis = true;
  } else if (finalScore >= 60 && age <= 7) {
    level = 'A级';
  } else if (finalScore >= 40) {
    level = 'B级';
  }
  
  // 时间限制
  if (age > 7) level = 'B级';
  if (age > 14) level = 'C级';
  
  return {
    ...hotspot,
    baseLevel: baseValue.level,
    attentionScore: Math.round(attentionScore),
    finalScore: Math.round(finalScore),
    level,
    needAnalysis,
    age: Math.round(age)
  };
}

// 生成日报
function generateDailyReport(hotspots, dutyPersons) {
  const evaluated = hotspots.map(evaluateHotspot);
  const visible = evaluated.filter(h => h.level !== 'C级');
  
  // 按时间排序（最新优先）
  visible.sort((a, b) => a.age - b.age);
  
  // 生成报告
  let report = `【${new Date().toLocaleDateString('zh-CN')} 产业热点日报】\n\n`;
  report += `值班人员：${dutyPersons.join('、')}\n\n`;
  
  // S级热点
  const sLevel = visible.filter(h => h.level === 'S级');
  if (sLevel.length > 0) {
    report += `【S级热点】（需要深度分析）\n`;
    sLevel.forEach(h => {
      report += `🔴 ${h.title}\n`;
      report += `   评分：${h.finalScore} | 来源：${h.source}\n`;
      report += `   ⚠️ 需要输出深度分析材料\n\n`;
    });
  }
  
  // A级热点
  const aLevel = visible.filter(h => h.level === 'A级');
  if (aLevel.length > 0) {
    report += `【A级热点】（高度关注）\n`;
    aLevel.forEach(h => {
      report += `🟠 ${h.title}\n`;
      report += `   评分：${h.finalScore} | 来源：${h.source}\n\n`;
    });
  }
  
  // B级热点
  const bLevel = visible.filter(h => h.level === 'B级');
  if (bLevel.length > 0) {
    report += `【B级热点】（持续跟踪）\n`;
    bLevel.forEach(h => {
      report += `🟡 ${h.title}\n`;
      report += `   评分：${h.finalScore}\n\n`;
    });
  }
  
  // 统计
  report += `【今日统计】\n`;
  report += `共监测${hotspots.length}条热点，`;
  report += `S级${sLevel.length}条，A级${aLevel.length}条，B级${bLevel.length}条\n\n`;
  
  // 待处理
  const needAnalysis = evaluated.filter(h => h.needAnalysis);
  if (needAnalysis.length > 0) {
    report += `【待处理事项】\n`;
    report += `• 需要输出分析材料：${needAnalysis.length}条\n`;
    needAnalysis.forEach(h => {
      report += `  - ${h.title}（截止时间：次日12:00）\n`;
    });
  }
  
  return { report, evaluated, visible };
}

// 执行
const result = generateDailyReport(todayHotspots, ['张三', '李四']);
console.log(result.report);
```

---

## 13. 最佳实践

### 13.1 每日工作流

| 时间 | 活动 | 系统 | 输出 |
|------|------|------|------|
| 早晨 | 信息扫描 | 信息信号识别 | 核心信号列表 |
| 工作中 | 任务沉淀 | 工作流资产沉淀 | 隐性知识、方法论 |
| 晚上 | 目标追踪 | 个人目标追踪 | 精力分析、盲点发现 |
| 睡前 | AI镜像 | 统一记忆系统 | 洞察、建议 |

### 13.2 每周工作流

| 时间 | 活动 | 输出 |
|------|------|------|
| 周一 | 设定本周目标 | 目标列表 |
| 周二-周五 | 执行+沉淀 | 日常输出 |
| 周六 | 周复盘 | 周报、AI镜像 |
| 周日 | 规划下周 | 下周计划 |

### 13.3 记忆管理最佳实践

1. **定期清理L1**：每周清理一次L1工作记忆
2. **主动提升L2**：将重要经验标记为高importance
3. **珍惜L4**：只有真正有价值的洞察才存入L4
4. **定期同步**：每周执行一次跨系统同步

### 13.4 避免的陷阱

| 陷阱 | 表现 | 解决方案 |
|------|------|----------|
| 信息囤积 | 收集大量信息但不处理 | 只存储核心信号 |
| 知识不沉淀 | 学习但不记录 | 每次学习后强制沉淀 |
| 目标不追踪 | 设定目标但不跟进 | 每周强制复盘 |
| 记忆不流转 | 记忆堆积在L1/L2 | 定期执行健康检查 |

---

## 14. 常见问题

### Q1：四个系统必须全部使用吗？

**A**：不是必须的。可以根据需求选择：
- 只想管理信息 → 使用信息信号识别系统
- 只想沉淀能力 → 使用工作流资产沉淀系统
- 只想追踪目标 → 使用个人目标追踪系统
- 想要完整体验 → 使用全部四个系统

### Q2：记忆会丢失吗？

**A**：不会。记忆系统有以下保护机制：
- 自动保存到文件
- 自动流转到更高层
- L4智慧记忆永久保存

### Q3：如何备份记忆？

**A**：
```bash
# 备份整个记忆目录
cp -r memory/ backup/memory_$(date +%Y%m%d)

# 或使用压缩
tar -czf backup/memory_$(date +%Y%m%d).tar.gz memory/
```

### Q4：如何迁移到新机器？

**A**：
1. 备份记忆目录
2. 在新机器上安装系统
3. 恢复记忆目录
4. 运行健康检查验证

### Q5：时间衰减可以调整吗？

**A**：可以。修改配置中的时间衰减参数：
```javascript
const TIME_DECAY_CONFIG = {
  DEFAULT_MAX_AGE_DAYS: 14,  // 改为14天
  DECAY_RATES: {
    '0-1天': 1.0,
    '1-3天': 0.95,
    // ... 自定义
  }
};
```

### Q6：如何查看历史信息？

**A**：默认只显示最近7天的信息。如需查看历史：
```javascript
// 查询所有L2记忆
const all = ai.memory.getL2Entries();

// 过滤特定时间范围
const history = all.filter(e => {
  const age = (Date.now() - new Date(e.createdAt)) / (24 * 60 * 60 * 1000);
  return age <= 30; // 最近30天
});
```

### Q7：如何重置系统？

**A**：
```bash
# 删除记忆目录
rm -rf memory/my_system/

# 重新创建系统
const ai = new AICollaborationSystem('my_system');
```

---

## 15. 故障排除

### 15.1 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| Cannot find module | 未安装依赖 | 运行 `npm install` |
| Cannot write to memory | 目录权限问题 | 检查目录权限 |
| TypeScript compile error | 编译问题 | 运行 `npm run build` |

### 15.2 调试方法

```javascript
// 1. 检查系统状态
console.log(ai.healthCheck());

// 2. 检查记忆内容
console.log(ai.memory.getL1Content());
console.log(ai.memory.getL2Entries());

// 3. 检查配置
console.log(ai.memory.getConfig());
```

### 15.3 日志查看

```bash
# 查看记忆文件
cat memory/my_system/L1_working/WORKING_MEMORY.md
cat memory/my_system/L2_experience/EXPERIENCE_MEMORY.json
cat memory/my_system/L3_knowledge/KNOWLEDGE_MEMORY.json
cat memory/my_system/L4_wisdom/WISDOM_MEMORY.json
```

---

## 附录

### A. 文件路径

| 文件 | 路径 |
|------|------|
| 部署包 | `/home/z/my-project/download/ai-collaboration-complete.zip` |
| 使用说明 | `/home/z/my-project/download/AI协作操作系统_完整使用说明书.md` |

### B. 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 1.0.0 | 2026-02-25 | 初始版本发布 |

### C. 技术支持

如有问题，请查看：
- `README.md` - 快速开始
- `demo.js` - 完整示例
- `duty-demo.js` - 值班机制示例
- `time-decay-demo.js` - 时间衰减示例

---

**文档版本**: 1.0.0  
**最后更新**: 2026年2月25日

**一行代码，开启AI协作之旅！**
