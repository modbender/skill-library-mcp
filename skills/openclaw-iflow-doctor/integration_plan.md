# OpenClaw Self-Healing + iflow-helper 融合方案

## 当前状态

### 1. iflow-helper 技能（服务器上）
- **位置**: `/root/.openclaw/workspace/skills/iflow-helper/`
- **功能**: 调用 iflow CLI 进行安装指导、问题解决、多模态识别
- **触发**: openclaw 主动调用

### 2. OpenClaw Self-Healing（我们做的）
- **位置**: `~/.iflow/memory/openclaw/`（需要移到 `~/.openclaw/skills/`）
- **功能**: 自动诊断、修复、BAT生成、案例库
- **触发**: 自动检测错误或手动调用

## 融合目标

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                         │
│                      (正常运行)                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 错误/崩溃
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              OpenClaw Self-Healing V2                       │
│  1. 自动捕获错误                                             │
│  2. 检索案例库 (cases.json)                                  │
│  3. 尝试自动修复                                             │
└────────┬──────────────────────────────────┬─────────────────┘
         │                                  │
         │ 能自动修复                        │ 无法自动修复
         ▼                                  ▼
┌─────────────────┐              ┌──────────────────────────────┐
│ 生成修复报告      │              │ 生成诊断报告 + BAT工具        │
│ (无需iflow)      │              │                              │
└─────────────────┘              │ 提示: 双击打开iFlow求助       │
                                 │ 或: 自动调用 iflow-helper    │
                                 └──────────────┬───────────────┘
                                                │
                                                ▼
                                 ┌──────────────────────────────┐
                                 │      iflow-helper Skill      │
                                 │  - 分析问题                  │
                                 │  - 调用 iflow CLI            │
                                 │  - 多模态诊断                │
                                 │  - 手动修复指导              │
                                 └──────────────┬───────────────┘
                                                │
                                                ▼
                                 ┌──────────────────────────────┐
                                 │        iflow CLI             │
                                 │  - WebSearch                 │
                                 │  - WebFetch                  │
                                 │  - 图像理解                   │
                                 │  - 执行修复命令               │
                                 └──────────────┬───────────────┘
                                                │
                                                ▼
                                 ┌──────────────────────────────┐
                                 │    修复完成 → 同步到记忆      │
                                 │    (cases.json / records.json)│
                                 └──────────────────────────────┘
```

## 融合后文件结构

```
~/.openclaw/skills/
├── iflow-helper/                    # 原有技能
│   └── SKILL.md
│
└── openclaw-iflow-doctor/        # 新增技能（移动过来）
    ├── skill.md                     # 技能定义
    ├── openclaw_healer.py          # 主修复程序
    ├── cases.json                  # 维修案例库（10个）
    ├── records.json                # 维修记录
    ├── config.json                 # 配置
    ├── config_checker.py           # 配置检查器
    ├── watchdog.py                 # 进程监控
    ├── iflow_bridge.py             # iflow 桥接器
    ├── README.md                   # 说明文档
    └── hooks/
        ├── openclaw_error_hook.py  # 错误捕获钩子
        └── startup_check.py        # 启动检查

~/.iflow/memory/openclaw/            # 可选：iFlow记忆集成
    └── records.json                # 同步的维修记录（如果启用iFlow）
```

## 关键融合点

### 1. 错误处理流程

**Before (只有 iflow-helper)**:
```
openclaw 出错 → 用户手动调用 iflow-helper → 调用 iflow CLI
```

**After (融合后)**:
```
openclaw 出错 → 自动触发 Self-Healing
               ├─ 能修复 → 自动修复 → 记录 → 完成
               └─ 不能修复 → 生成BAT → 提示调用 iflow-helper → iflow CLI修复 → 同步记录
```

### 2. 技能调用关系

```yaml
# openclaw-iflow-doctor/skill.md
triggers:
  on_error:
    # 先尝试自我修复
    - action: "self_heal"
      script: "openclaw_healer.py"
    
    # 如果失败，调用 iflow-helper
    - action: "call_iflow"
      skill: "iflow-helper"
      condition: "self_heal.failed"
```

### 3. 记忆同步

```python
# iflow_bridge.py 中的同步逻辑

class iFlowBridge:
    def sync_repair_record(self, record):
        """将维修记录同步到 iflow 记忆"""
        
        # 1. 保存到本地 records.json
        self.save_local_record(record)
        
        # 2. 如果 iflow 可用，同步到 iflow 记忆
        if self.is_iflow_available():
            self.sync_to_iflow_memory(record)
        
        # 3. 同步到 cases.json（如果解决方案值得复用）
        if record.get('success') and record.get('reuseable'):
            self.add_to_cases(record)
```

### 4. 用户使用流程

**场景 1: OpenClaw 自动修复成功**
```
[系统] OpenClaw 网关崩溃
[系统] Self-Healing 自动修复中...
[系统] ✓ 已自动修复（重置记忆索引）
[系统] 生成报告: openclaw修复报告_20240227.txt
[用户] 查看报告，无需操作
```

**场景 2: 需要 iflow 协助**
```
[系统] OpenClaw 网关崩溃
[系统] Self-Healing 自动修复中...
[系统] ✗ 无法自动修复
[系统] 生成诊断书 + 2个BAT文件
[系统] 提示: 双击"打开iFlow寻求帮助.bat" 或 运行 "openclaw skills run iflow-helper"
[用户] 双击BAT文件 或 调用技能
[系统] 启动 iflow CLI
[用户] 描述问题
[iflow] 分析问题 → 提供解决方案 → 执行修复
[系统] 修复完成，记录同步到记忆库
```

## 融合后的改进

### 1. 自动化程度提升
- **Before**: 用户发现问题 → 手动调用 iflow-helper → 等待修复
- **After**: 系统自动检测 → 自动尝试修复 → 必要时才调用 iflow

### 2. 记忆积累
- **Before**: 每次都要重新描述问题
- **After**: 相同问题自动识别并应用历史方案

### 3. 修复速度
- **Before**: 必须等待 iflow 响应
- **After**: 简单问题秒级自动修复

### 4. 离线可用
- **Before**: 必须联网调用 iflow
- **After**: 本地案例库支持离线修复

## 实施步骤

1. **移动文件**（已完成）
   - 将 `~/.iflow/memory/openclaw/` 移到 `~/.openclaw/skills/openclaw-iflow-doctor/`

2. **修改路径**
   - 更新所有文件中的路径引用

3. **创建钩子**
   - 在 openclaw 中添加错误捕获钩子

4. **测试集成**
   - 测试自动触发
   - 测试 iflow 调用链

5. **发布技能**
   - 打包两个技能
   - 上传到 GitHub 或技能市场

## 使用示例

```bash
# 用户安装两个技能
openclaw skills install iflow-helper
openclaw skills install openclaw-iflow-doctor

# 启用自动修复
openclaw skills enable openclaw-iflow-doctor --auto

# 后续：当 openclaw 出错时自动处理
# 无需用户干预，或最小干预
```
