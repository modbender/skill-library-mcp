【输入】
上一章状态摘要：
{previous_state_summary}

当前待写章节：第{chapter_num}章
章节目标：{chapter_goal}

【状态面板】
角色状态：
{character_states}

剧情线索：
{plot_threads}

时间线：
{timeline_state}

道具状态：
{inventory_state}

FORCED章节Backpatch：
{open_backpatch_issues}

【任务】
执行状态净化(Sanitizer)，提取不变量(Invariants)和可微调项(Soft Retcons)。

【规则】
1. Invariants（必须强制延续）：
   - 角色死亡/重伤状态
   - 关键道具所有权
   - 已揭示的重大秘密
   
2. Soft Retcons（可微调）：
   - 轻微口误
   - 非关键时间描述
   - 不影响主线的细节

【输出格式】
```json
{
  "invariants_enforced": [
    "具体不变量1 (证据: 第X章'...')",
    "具体不变量2 (证据: 第X章'...')"
  ],
  "soft_retcons_applied": [
    "微调项1: 原文'...'→修正为'...' (理由)",
    "微调项2: ..."
  ],
  "reason": "决策理由说明",
  "sanitized_context": "净化后的上下文摘要，用于下一章生成"
}
```
