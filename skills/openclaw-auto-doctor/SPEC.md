# OpenClaw Auto-Doctor Skill

## 概述

作为一个智能化的 OpenClaw 日志监控与自动修复系统，本 skill 能够：
1. 实时监控 OpenClaw 运行日志
2. 智能识别错误信息并分析根因
3. 自动搜索 OpenClaw 社区、GitHub Issues 寻找解决方案
4. 对于已知错误自动应用修复
5. 对于未知错误生成修复补丁并自动提交 Pull Request

## 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Auto-Doctor                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  日志监控模块  │───▶│  错误解析模块  │───▶│  解决方案库  │  │
│  │  (Log Watch) │    │(Error Parser)│    │(Solution DB) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   智能决策引擎                         │  │
│  │  (Intelligent Decision Engine)                        │  │
│  └──────────────────────────────────────────────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  自动修复模块  │    │  PR 生成模块  │    │  用户通知模块 │  │
│  │(Auto Fixer)  │    │(PR Creator)  │    │(Notifier)   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 核心模块详细设计

### 1. 日志监控模块 (Log Watcher)

**功能**：实时监控 OpenClaw 日志文件

**实现方式**：
- 使用 `tail -f` 命令实时读取日志
- 支持多个日志文件监控（主日志 + 错误日志）
- 可配置监控的日志级别（error, warning, info）

**配置项**：
```yaml
log_paths:
  - /path/to/openclaw/logs/main.log
  - /path/to/openclaw/logs/error.log

monitoring:
  enabled: true
  debounce_ms: 1000  # 错误信息防抖，避免重复告警
  max_errors_per_hour: 10  # 每小时最大错误数
```

### 2. 错误解析模块 (Error Parser)

**功能**：从日志中提取结构化错误信息

**解析能力**：
- JavaScript/TypeScript 异常堆栈
- Python traceback
- Go panic 信息
- 系统错误码
- HTTP 错误响应

**输出格式**：
```json
{
  "error_type": "TypeError",
  "message": "Cannot read property 'foo' of undefined",
  "stack": "at Function.test (src/index.ts:42:5)...",
  "file": "src/index.ts",
  "line": 42,
  "column": 5,
  "timestamp": "2024-01-15T10:30:00Z",
  "context": "附近10行代码上下文"
}
```

### 3. 解决方案库 (Solution Database)

**功能**：存储已知错误的解决方案

**包含内容**：
- 错误模式（正则匹配）
- 解决方案描述
- 修复脚本或命令
- 来源（社区/GitHub/自研）
- 成功率统计

**示例**：
```yaml
- pattern: "Cannot find module.*node_modules"
  solution: "运行 npm install 重新安装依赖"
  fix_command: "npm install"
  source: "community"

- pattern: "Connection refused.*6379"
  solution: "Redis 服务未启动，启动 Redis"
  fix_command: "brew services start redis"
  source: "github_issue_123"
```

### 4. 智能搜索模块 (Smart Search)

**功能**：多渠道搜索解决方案

**搜索渠道**：
1. **OpenClaw 官方文档** - 搜索内置文档
2. **GitHub Issues** - 使用 GitHub API 搜索相关 issues
3. **GitHub Pull Requests** - 搜索已解决的 PR
4. **OpenClaw 社区论坛** - 搜索社区讨论
5. **Stack Overflow** - 搜索技术问答

**搜索策略**：
- 提取错误关键词
- 模糊匹配 + 精确匹配
- 按相关性排序
- 优先选择已解决的问题

### 5. 自动修复模块 (Auto Fixer)

**功能**：应用修复方案

**修复策略**：
1. **简单修复**：执行预设命令（如 npm install）
2. **代码修复**：生成补丁文件，应用到源代码
3. **配置修复**：修改配置文件
4. **环境修复**：安装缺失依赖、配置环境变量

**安全机制**：
- 修复前创建快照/备份
- 修复后自动验证
- 不确定时请求用户确认

### 6. PR 生成模块 (PR Creator)

**功能**：自动创建 GitHub Pull Request

**PR 内容**：
- 清晰的标题和描述
- 关联的 Issue 链接
- 修复前后的对比
- 测试验证结果

### 7. 用户通知模块 (Notifier)

**功能**：及时告知用户系统状态

**通知内容**：
- 检测到新错误
- 搜索结果摘要
- 修复状态（成功/失败/需确认）
- PR 创建结果

## 工作流程

```
日志输入
   │
   ▼
┌─────────────────────────────────────────┐
│  1. 日志监控捕获错误                      │
└─────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────┐
│  2. 错误解析提取关键信息                   │
│     - 错误类型、消息、堆栈、位置           │
└─────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────┐
│  3. 检查解决方案库                        │
│     - 已知错误？→ 直接应用修复            │
│     - 未知错误？→ 进入搜索流程            │
└─────────────────────────────────────────┘
   │
   ├── 已知错误 ──▶ 应用修复 ──▶ 验证 ──▶ 完成
   │
   ▼
┌─────────────────────────────────────────┐
│  4. 多渠道智能搜索                        │
│     - GitHub Issues                     │
│     - 社区论坛                          │
│     - 官方文档                          │
└─────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────┐
│  5. 评估搜索结果                          │
│     - 有高置信度方案？→ 应用修复          │
│     - 无确定方案？→ 生成修复建议          │
└─────────────────────────────────────────┘
   │
   ├── 有方案 ──▶ 申请修复 ──▶ 验证 ──▶ 创建 PR
   │
   ▼
┌─────────────────────────────────────────┐
│  6. 自主分析尝试修复                      │
│     - 分析错误根因                        │
│     - 生成修复代码                        │
│     - 本地测试验证                        │
└─────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────┐
│  7. 创建 Pull Request                    │
│     - 提交代码更改                        │
│     - 描述问题和解决方案                  │
│     - 关联相关 Issue                      │
└─────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────┐
│  8. 通知用户结果                          │
└─────────────────────────────────────────┘
```

## 关键设计决策

### 1. 实时性与性能平衡
- 使用防抖机制避免重复处理相同错误
- 错误限流，每小时最多处理一定数量
- 后台异步处理，不阻塞主进程

### 2. 安全第一
- 所有修复操作前创建备份
- 未知修复需要用户确认
- 详细的操作日志便于回滚

### 3. 学习能力
- 记录每次修复的成功率
- 用户确认的方案加入解决方案库
- 持续优化搜索和匹配算法

### 4. 透明可追溯
- 所有操作记录详细日志
- 用户可以查看修复历史
- PR 清晰描述问题来源

## 配置示例

```yaml
# openclaw-auto-doctor.yaml

openclaw:
  log_paths:
    - ~/openclaw/logs/claude-code.log
    - ~/openclaw/logs/error.log

github:
  repository: openclaw/openclaw
  token: ${GITHUB_TOKEN}  # 从环境变量读取

auto_fix:
  enabled: true
  require_confirmation: false  # 全自动模式
  backup_before_fix: true
  max_auto_fixes_per_day: 20

notifications:
  enabled: true
  channels:
    - type: console
    - type: desktop  # macOS 通知
```

## 使用方式

### 启动监控
```bash
# 启动 OpenClaw Auto-Doctor
/openclaw-doctor start

# 指定配置文件
/openclaw-doctor start --config ~/openclaw-doctor.yaml
```

### 手动触发分析
```bash
# 分析最近一天的日志
/openclaw-doctor analyze

# 分析特定错误
/openclaw-doctor analyze "TypeError: Cannot read property"
```

### 查看状态
```bash
# 查看监控状态
/openclaw-doctor status

# 查看修复历史
/openclaw-doctor history
```

### 管理配置
```bash
# 添加新的解决方案
/openclaw-doctor add-solution --pattern "..." --fix "..."

# 导出解决方案库
/export-solutions
```

## 验收标准

1. ✅ 能够实时监控指定日志文件
2. ✅ 准确识别常见的错误类型
3. ✅ 能够搜索 GitHub Issues 找到相关解决方案
4. ✅ 对于已知错误能够自动应用修复
5. ✅ 能够生成修复代码并创建 PR
6. ✅ 修复失败时能够清晰告知用户
7. ✅ 所有操作有详细日志可追溯
8. ✅ 配置灵活可自定义
