【输入】
待修复章节：第{chapter_num}章
问题描述：
{issue_description}

当前章节内容：
{chapter_content}

目标章节位置：{target_chapter}

【任务】
设计一个Backpatch修复计划。

【约束】
1. 只能使用Retcon（回顾式修正），不能rewrite已落盘章节
2. 修复必须在后续章节中自然引入
3. 修复后必须重跑QC验证

【输出格式】
fix_strategy: [retcon|soft_patch|abandon]
severity: [high|medium|low]

【修复计划】
1. 修复时机：第X章（说明为什么选这一章）
2. 修复方式：通过对话/回忆/发现来揭示真相
3. 具体文本方案：给出建议的插入段落
4. QC验证标准：修复后需达到的分数

【风险评估】
- 修复难度：低/中/高
- 可能副作用：...
- 备选方案：...
