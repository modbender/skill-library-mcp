# Self-Evolve 输出模板

## 进化报告文件规范

在选定进化方案后，需要在 `memory/evolve/` 下创建一份进化报告：
**命名规范**：`YYYYMMDD_self-evolve_[进化方向关键词].md`

### YAML Frontmatter 格式
```yaml
---
type: self-evolve
date: YYYY-MM-DD HH:MM
target: 一句话描述进化目标
cycle_id: evolve-YYYY-WNN-[关键词]
evaluate_by: YYYY-MM-DDTHH:MM:SSZ
result: 成功/失败/进行中
winner: 方案 A/B/C 或 无
---
```

### 实验计划输出结构
在报告内部，记录方案淘汰记录、物理部署说明和完整的测试计划：

```markdown
# 进化报告：[关键词]

> 🧬 **本轮进化目标**：[一句话描述]
> **瓶颈来源**：[来自 self-think / 错误日志 / 用户反馈等]

## 方案淘汰记录
* 方案 A（GitHub）: [一句话说明] - [淘汰/保留原因]
* 方案 B（skills.sh）: [一句话说明] - [淘汰/保留原因]

## 📐 实验计划
* **基线**：[当前状态量化指标，必须可测]
* **指标**：[用什么数据判断优劣，怎么测]
* **遥测钩子 (Telemetry Hook)**：
  * **command**: `[执行获取原始验证数据的 shell 脚本/命令，例如 cat xxx.log | tail -n 20]`
  * **extract**: `[要在输出 JSONL 里的 metrics 字典中提取输出的具体 JSON keys 数组，如 ["error_count", "success_rate"]]`
* **方案 A**：[描述与物理变更指引] — [起止观察时间]
* **方案 B**：[描述与物理变更指引] — [起止观察时间] (如果是A/B Test)
* **切换点**：[方案A切换到B的具体时间]
* **提前终止条件**：[什么负面情况下直接判负回滚]
* **评估截止时间**：[具体如 2026-03-01T12:00:00Z，到期触发评价流]

## 实验日志指针
* 获取到的数据对比指标将追加写入：`memory/evolve/[cycle_id].jsonl`
```
