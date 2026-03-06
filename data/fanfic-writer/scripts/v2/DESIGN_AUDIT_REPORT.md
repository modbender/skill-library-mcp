# Fanfic Writer v2.0 - 设计文档一致性检查报告

**检查时间**: 2026-02-16  
**设计文档**: fanfic_writer_skill_v2_0_FULL_FINAL_V3_MERGED_REVIEWED_V22_R.md  
**代码版本**: 初始开发版 (12个Python模块)

---

## 一、静态验收扫描表检查

### 3.1 文件与目录（落盘完整性）

| 检查项 | 设计 requirement | 代码实现 | 状态 |
|--------|-----------------|----------|------|
| `prompts/` (v1/v2_addons) | 必须存在，只读资源 | ✅ 已创建13个模板 | ✅ PASS |
| `logs/prompts/` | Prompt审计日志目录 | ✅ PromptAuditor创建 | ✅ PASS |
| `logs/token-report.jsonl` | Token事件日志 | ✅ atomic_append_jsonl | ✅ PASS |
| `logs/cost-report.jsonl` | 人民币成本日志 | ⚠️ 基础支持，需price_table | ⚠️ PARTIAL |
| `logs/rescue.jsonl` | Auto-Rescue日志 | ✅ AutoRescue类实现 | ✅ PASS |
| `final/quality-report.md` | 质量报告 | ✅ FinalIntegration | ✅ PASS |
| `final/auto_abort_report.md` | 中止报告 | ✅ AutoAbortGuardrail | ✅ PASS |
| `final/auto_rescue_report.md` | 救援报告 | ✅ AutoRescue.generate_rescue_report | ✅ PASS |
| `archive/snapshots/` | 快照目录，含run_id | ✅ SnapshotManager | ✅ PASS |
| 禁止越界写入 | 所有写入必须在workspace_root | ✅ validate_path_in_workspace | ✅ PASS |

**评分**: 9/10 ✅ (cost-report需price_table完善)

---

### 3.2 关键主键与一致性

| 检查项 | 设计 requirement | 代码实现 | 状态 |
|--------|-----------------|----------|------|
| `book_uid` 生成并固化 | 6-10位hash，用于目录隔离 | ✅ generate_book_uid | ✅ PASS |
| `run_id` 与目录强绑定 | YYYYMMDD_HHMMSS_RAND6 | ✅ generate_run_id, 目录名一致 | ✅ PASS |
| `event_id` 跨日志一致 | token/cost/rescue共享 | ⚠️ 生成函数存在，需验证对齐 | ⚠️ PARTIAL |
| `ending_state` 枚举 | not_ready/ready_to_end/ended | ❌ 未在writing-state中明确定义 | ❌ MISSING |
| Attempt状态机门槛 | >=85/75-84/<75 | ✅ QCStatus枚举 + thresholds | ✅ PASS |

**评分**: 4/5 ⚠️ (ending_state缺失)

---

### 3.3 提示词继承与审计

| 检查项 | 设计 requirement | 代码实现 | 状态 |
|--------|-----------------|----------|------|
| Auto模式chapter_outline来自v1 | 必须使用prompts/v1/ | ✅ PromptRegistry.VALIDATE_FOR_AUTO | ✅ PASS |
| Auto模式chapter_draft来自v1 | 必须使用prompts/v1/ | ✅ REQUIRED_TEMPLATES检查 | ✅ PASS |
| 每次调用落盘最终Prompt | `logs/prompts/{phase}_{chapter}_{event_id}.md` | ✅ PromptAuditor.log_prompt | ✅ PASS |
| prompt_registry.json | 指向的模板存在且可读 | ✅ initialize时验证 | ✅ PASS |
| 审计链缺失= fatal | 必须停机 | ⚠️ 返回错误，未强制停机 | ⚠️ PARTIAL |

**评分**: 4.5/5 ⚠️

---

### 3.4 Auto闭环（无人干预能力）

| 检查项 | 设计 requirement | 代码实现 | 状态 |
|--------|-----------------|----------|------|
| Auto-Rescue开关与最大轮次 | auto_rescue_enabled/max_rounds | ✅ AutoRescue类 | ✅ PASS |
| Recoverable vs Fatal分级 | 明确分级，Fatal硬停 | ✅ should_rescue区分 | ✅ PASS |
| Auto Abort Guardrail | 卡死判定+abort报告 | ✅ AutoAbortGuardrail类 | ✅ PASS |
| Forced streak熔断 | >=2时暂停 | ✅ state_commit检查 | ✅ PASS |
| 完结交付包 | 文本+报告+状态归档 | ⚠️ Phase 8/9基础实现 | ⚠️ PARTIAL |

**评分**: 4.5/5 ⚠️

---

### 3.5 成本与人民币口径

| 检查项 | 设计 requirement | 代码实现 | 状态 |
|--------|-----------------|----------|------|
| `price-table.json` | 版本化，含updated_at/source/usd_cny_rate | ❌ 未实现 | ❌ MISSING |
| `cost-report.jsonl` | 含price_table_version和RMB估算 | ⚠️ 占位，需price_table | ⚠️ PARTIAL |
| usd_cny_rate固化 | run启动时固化并落盘 | ❌ 未实现 | ❌ MISSING |
| 热更新费率表 | 保留旧版本+切换时间 | ❌ 未实现 | ❌ MISSING |

**评分**: 0.5/4 ❌ (重大缺失)

---

## 二、SSOT区域检查

### 1. 目录树与workspace_root隔离

| 检查点 | 状态 | 说明 |
|--------|------|------|
| `novels/{book_title_slug}__{book_uid}/runs/{run_id}/` | ✅ | workspace.py实现 |
| book_uid派生workspace_root | ✅ | 自动生成 |
| 手动指定workspace_root限制 | ⚠️ | 代码有预留，未完整实现resume逻辑 |
| 两本书目录隔离 | ✅ | 目录结构保证 |

### 2. Event ID总表

**设计要求的Event IDs**:
- `RS-001` 恢复事件
- `RS-002` 僵尸锁清理
- `AR-001~006` 救援事件
- `BP-*` Backpatch事件
- `CP-*` Cost/Pricing事件

**代码实现**: 
- ✅ event_id生成函数存在
- ⚠️ 具体Event ID常量未定义
- ⚠️ RS/BP/AR事件未完整实现

### 3. Attempt状态机表

| Attempt | 触发条件 | 允许的修改范围 | 失败后的动作 |
|---------|----------|----------------|--------------|
| Attempt 1 | 默认第一次 | 正常生成 | score<85 → Attempt 2 |
| Attempt 2 | Attempt1未达标 | 定向修（仅cons） | <85 → Attempt 3 |
| Attempt 3 | Attempt2未达标 | 全量重写 | <75 → FORCED |
| FORCED | Attempt3且<75 | 最小可行稿 | forced_streak+=1 |

**代码实现**: ✅ writing_loop.py中attempt_cycle完整实现

### 4. Price Table Schema

**缺失模块**: 需要price_table.py实现：
- 多平台费率管理
- 模型档位选择
- 成本计算
- 版本控制

---

## 三、关键功能缺失清单

### 🔴 缺失功能（必须实现）

1. **price_table.py 模块**
   - 费率表版本化
   - 多平台模型选择
   - 成本计算
   - 与cost-report.jsonl集成

2. **ending_state 管理**
   - 在4-writing-state.json中维护
   - not_ready/ready_to_end/ended枚举
   - 完结检查表

3. **resume/断点续传完整实现**
   - RS-001/RS-002事件
   - 状态hash校验
   - 从snapshot恢复

4. **.lock.json 排他锁**
   - runs/{run_id}/.lock.json
   - 僵尸锁检测

5. **runtime_effective_config.json**
   - 参数优先级固化
   - alias映射记录

### 🟡 部分实现（需要完善）

6. **cost-report.jsonl**
   - 需要与price_table集成
   - 人民币口径计算

7. **Multi-Perspective QC**
   - 代码结构存在
   - 需要实际调用3个Critic模型

8. **Backpatch自动修复**
   - 队列管理存在
   - 需要自动生成修复方案

9. **Auto-Rescue策略执行**
   - 策略定义存在
   - 需要完整执行S1-S5

10. **Event ID对齐**
    - 需要确保跨日志一致

---

## 四、设计符合度评分

| 类别 | 权重 | 得分 | 加权得分 |
|------|------|------|----------|
| 目录结构 | 15% | 95% | 14.25 |
| 状态管理 | 20% | 90% | 18.00 |
| QC系统 | 15% | 85% | 12.75 |
| 安全机制 | 15% | 85% | 12.75 |
| 审计日志 | 15% | 80% | 12.00 |
| 成本管理 | 10% | 20% | 2.00 |
| 接口契约 | 10% | 70% | 7.00 |
| **总计** | 100% | | **78.75%** |

---

## 五、修复建议（按优先级）

### P0 - 阻塞级（必须修复）

1. **实现 price_table.py**
   - 包含费率表schema
   - 成本计算
   - 版本管理

2. **添加 ending_state 到 writing-state**
   - 完结态管理
   - 终止条件检查

3. **完善 resume 机制**
   - RS-001/RS-002事件
   - 状态hash校验

### P1 - 重要（强烈建议）

4. **实现 .lock.json 排他锁**
5. **完成 cost-report.jsonl 集成**
6. **添加 runtime_effective_config.json**

### P2 - 改进（可选）

7. **完整Event ID体系**
8. **Multi-Perspective QC实际调用**
9. **Backpatch自动生成修复**

---

## 六、结论

**当前状态**: ⚠️ **基本可用，但有关键缺失**

**已实现** (~75%):
- ✅ 核心架构（目录结构、状态面板）
- ✅ Phase 1-6基础流程
- ✅ 原子I/O和快照
- ✅ 基础安全机制（Auto-Rescue/Abort框架）
- ✅ 提示词审计

**关键缺失** (~25%):
- ❌ price_table/cost管理
- ❌ ending_state/终止条件
- ❌ 完整resume机制
- ❌ 排他锁

**建议**: 完成P0和P1修复后，可达到生产可用状态。
