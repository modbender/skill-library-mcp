# Cue v1.0.4 vs v1.0.3 详细对比

## 一、架构对比

### v1.0.3 (Bash 脚本)
```
skills/cue/
├── scripts/
│   ├── cue.sh              # 主入口 (31147 字节)
│   ├── research.sh         # 研究执行 (6557 字节)
│   ├── notifier.sh         # 完成通知 (11176 字节)
│   ├── cuecue-client.js    # API 客户端
│   ├── create-monitor.sh   # 监控创建
│   ├── monitor-daemon.sh   # 监控守护
│   ├── monitor-notify.sh   # 监控通知
│   └── executor/
│       ├── monitor-engine.sh
│       ├── search-executor.sh
│       └── browser-executor.sh
└── package.json            # 依赖: @playwright/test
```

**特点**:
- 11 个 shell 脚本文件
- 混合 Bash + Node.js
- 依赖 nohup/tar/grep/sed 等 Unix 工具
- 进程管理通过 PID 文件

### v1.0.4 (Node.js)
```
skills/cue/
├── src/
│   ├── index.js            # 主入口 (模块导出)
│   ├── cli.js              # CLI 入口 (Commander)
│   ├── core/
│   │   ├── logger.js       # 统一日志系统
│   │   ├── userState.js    # 用户状态管理
│   │   ├── taskManager.js  # 任务管理
│   │   └── monitorManager.js # 监控管理
│   ├── api/
│   │   └── cuecueClient.js # API 客户端 (ES Module)
│   └── utils/
│       ├── fileUtils.js    # 文件操作
│       ├── envUtils.js     # 环境变量
│       └── validators.js   # 验证工具
├── package.json            # 10+ npm 依赖
└── node_modules/
```

**特点**:
- 10 个 JS 模块，纯 Node.js
- ES Module 标准
- npm 依赖管理
- 统一进程管理

---

## 二、核心代码对比

### 1. 主入口

**v1.0.3 (Bash)**
```bash
# 31000+ 字节，单文件
# 大量 case/esac 分支
# 字符串处理复杂

case "$cmd" in
    /cue|cue)
        start_research "$topic" "$chat_id" "$mode"
        ;;
    /ct|ct)
        list_tasks "$chat_id"
        ;;
    # ... 更多分支
esac
```

**v1.0.4 (Node.js)**
```javascript
// 模块化设计，职责分离
import { Command } from 'commander';

program
  .command('cue <topic>')
  .option('-m, --mode <mode>', '研究模式')
  .action(async (topic, options) => {
    await handleResearch(topic, options.mode);
  });
```

**对比**:
| 维度 | v1.0.3 | v1.0.4 |
|------|--------|--------|
| 代码行数 | ~900 行 (单文件) | ~200 行 (分散到10模块) |
| 可维护性 | 低 | 高 |
| 类型安全 | 无 | JSDoc 注解 |
| 测试难度 | 难 | 易 (Jest) |

### 2. 日志系统

**v1.0.3**
```bash
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}
# 单一日志文件
```

**v1.0.4**
```javascript
export class Logger {
  async log(level, message) { /* 多级别日志 */ }
  async debug(message) { /* 调试日志 */ }
  async info(message) { /* 信息日志 */ }
  async error(message, error) { /* 错误日志 + 堆栈 */ }
}
// 多文件: cue-YYYY-MM-DD.log, error-YYYYMM.log, info-YYYYMM.log
```

### 3. 任务管理

**v1.0.3**
```bash
# 直接操作 JSON 文件
start_research() {
    # 启动后台进程
    nohup bash -c "..." &
    # 保存 PID
    echo $! > "$PID_FILE"
}
```

**v1.0.4**
```javascript
export class TaskManager {
  async createTask(taskData) { /* 创建任务 */ }
  async updateTask(taskId, updates) { /* 更新状态 */ }
  async getTask(taskId) { /* 获取任务 */ }
  async getTasks(limit) { /* 获取列表 */ }
}
```

---

## 三、依赖对比

### v1.0.3
```json
{
  "dependencies": {
    "@playwright/test": "^1.40.0"
  }
}
```
**系统依赖**: bash, jq, grep, sed, nohup, tar, curl

### v1.0.4
```json
{
  "dependencies": {
    "@playwright/test": "^1.40.0",
    "chalk": "^5.3.0",          // 终端颜色
    "commander": "^11.1.0",     // CLI 框架
    "fs-extra": "^11.2.0",      // 增强文件操作
    "inquirer": "^9.2.12",      // 交互提示
    "node-cron": "^3.0.3",      // 定时任务
    "ora": "^8.0.1"             // 加载动画
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "nodemon": "^3.0.3"
  }
}
```
**系统依赖**: Node.js >= 18.0.0

**对比**:
| 维度 | v1.0.3 | v1.0.4 |
|------|--------|--------|
| 运行时 | Bash + Node | 纯 Node |
| 依赖管理 | 系统包 + npm | 纯 npm |
| 可移植性 | 依赖 Unix 环境 | 跨平台 (Windows/Mac/Linux) |
| 包大小 | 较小 | 较大 (含 node_modules) |

---

## 四、功能实现对比

### 1. 自动角色匹配

**v1.0.3**
```bash
auto_detect_mode() {
    local topic="$1"
    if echo "$topic" | grep -qiE "龙虎榜|涨停"; then
        echo "trader"
    elif echo "$topic" | grep -qiE "财报|估值"; then
        echo "fund-manager"
    fi
}
```

**v1.0.4**
```javascript
export function autoDetectMode(topic) {
  const topicLower = topic.toLowerCase();
  
  if (/龙虎榜|涨停|游资/.test(topicLower)) {
    return 'trader';
  } else if (/财报|估值|业绩/.test(topicLower)) {
    return 'fund-manager';
  }
  return 'researcher';
}
```
**优势**: JS 正则更易读，可单元测试

### 2. API Key 配置

**v1.0.3**
```bash
# 直接操作 .env 文件
sed -i "s/^${var_name}=.*/${var_name}=${api_key}/" "$env_file"
```

**v1.0.4**
```javascript
export async function setApiKey(keyName, value) {
  process.env[keyName] = value;
  const env = await loadEnvFile();
  env.set(keyName, value);
  await saveEnvFile(env);
}
```
**优势**: 内存 + 文件同步更新，容错更好

### 3. 错误处理

**v1.0.3**
```bash
if [ $? -ne 0 ]; then
    echo "❌ 错误"
    exit 1
fi
```

**v1.0.4**
```javascript
try {
  await operation();
} catch (error) {
  await logger.error('Operation failed', error);
  // 自动记录堆栈
}
```
**优势**: 异常捕获 + 日志记录 + 堆栈跟踪

---

## 五、测试对比

### v1.0.3
```bash
# Bash 测试
bash -n scripts/cue.sh  # 仅语法检查
# 功能测试需手动执行
```

### v1.0.4
```javascript
// Jest 测试
import { autoDetectMode } from './api/cuecueClient.js';

test('自动角色匹配 - 龙虎榜', () => {
  expect(autoDetectMode('今日龙虎榜')).toBe('trader');
});

// 10个自动化测试
```

**对比**:
| 维度 | v1.0.3 | v1.0.4 |
|------|--------|--------|
| 测试框架 | 无 | Jest |
| 自动化 | 低 | 高 |
| 覆盖率 | 难统计 | 可统计 |

---

## 六、性能对比

| 维度 | v1.0.3 | v1.0.4 |
|------|--------|--------|
| 启动速度 | 快 (Bash 启动快) | 稍慢 (Node.js 启动) |
| 运行时性能 | 中等 | 高 (V8 优化) |
| 内存占用 | 低 | 中等 |
| 扩展性 | 低 | 高 |

---

## 七、可维护性对比

| 维度 | v1.0.3 | v1.0.4 |
|------|--------|--------|
| 代码可读性 | 中 | 高 |
| 调试难度 | 高 (shell 调试难) | 低 (可用 debugger) |
| IDE 支持 | 弱 | 强 (VSCode 等) |
| 重构难度 | 高 | 低 |
| 新手上手 | 难 (需懂 Bash) | 易 (JS 开发者多) |

---

## 八、发布包对比

### v1.0.3
- 大小: ~40KB
- 文件: 22个 (主要是 .sh 脚本)
- 依赖: 系统工具 + @playwright/test

### v1.0.4
- 大小: ~25KB (不含 node_modules)
- 文件: 22个 (10个 JS 模块)
- 依赖: 10+ npm 包

**注意**: v1.0.4 运行时实际占用更大 (含 node_modules ~100MB)

---

## 九、优缺点总结

### v1.0.3 (Bash)
**优点**:
- 启动快
- 依赖少 (系统自带)
- 包体积小

**缺点**:
- 代码难以维护
- 跨平台性差
- 错误处理弱
- 测试困难

### v1.0.4 (Node.js)
**优点**:
- 模块化，易维护
- 类型安全 (JSDoc)
- 跨平台
- 错误处理完善
- 可单元测试
- 社区生态丰富

**缺点**:
- 启动稍慢
- 依赖体积大
- 需 Node.js 环境

---

## 十、迁移价值评估

**建议 v1.0.4 场景**:
- 长期维护
- 团队协作
- 功能扩展
- 跨平台支持

**建议 v1.0.3 场景**:
- 资源受限环境
- 快速原型
- 简单功能

**结论**: v1.0.4 更适合生产环境长期发展
