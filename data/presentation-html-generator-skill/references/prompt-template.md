# C.R.I.S.P 原则 Prompt 模板

以下是经验证的高质量 Prompt 模板，用于生成技术演示文稿。

## 需求三维度

1. **技术框架与渲染限制**：单文件 HTML，Reveal.js + MathJax/KaTeX
2. **交互与演示功能**：Space/→ 翻页，F 全屏，S 演讲者模式
3. **内容核心逻辑**：C.R.I.S.P 原则 — Conceptual Clarity, Relevant Detail, Interaction, Storytelling, Professionalism

## 推荐 Prompt

> **Role:**
> 你是一位顶级的 AI 算法工程师，精通相关技术领域。你现在需要向技术同行（架构师、高级工程师）做一个高深度的技术分享。
>
> **Task:**
> 编写单文件 HTML 演示文稿，使用 Reveal.js 框架。
> 主题："[在此处填入主题]"
> 目标页数：15-20 页。
>
> **Technical Requirements:**
> - **框架**: Reveal.js (CDN 引入)
> - **公式**: MathJax/KaTeX 插件
> - **交互**: Space/→ 下一页，F 全屏，S 演讲者模式
> - **Speaker Notes**: 每页必须包含 `<aside class="notes">`，内容为"同行间对话旁白"风格，解释 Why 不是 What
>
 **Content Framework (C.R.I.S.P):**
> - **Shape**: Input/Output 张量维度（如 `(B, T, 80) → (B, 192)`）
> - **Structure**: 模型骨干结构
> - **Flow**: Training vs Inference 差异（**若为 AI 模型算法，必须分离展示，见下方规则**）
> - **Integration**: 模块间交互方式
> - **Evaluation**: 优缺点对比
>
> **AI 模型算法：训练与推理流程分离展示（必须遵守）:**
> 若主题涉及 AI 模型/算法，**训练流程和推理流程必须作为独立章节分开展示**，不可混在同一页：
>
> - **🏋️ 训练流程专区**（独立 2-4 页）:
>   - 训练数据准备与预处理 Pipeline
>   - 训练架构图（含 Loss 计算、梯度回传路径）
>   - Loss 函数设计与公式推导
>   - 训练超参数表（lr, batch_size, optimizer, scheduler 等）
>   - 训练独有模块（如 Dropout、Data Augmentation、Teacher Forcing）
>   - 训练 Shape 流：从原始数据到 Loss 输出的完整维度变化
>
> - **🚀 推理流程专区**（独立 2-4 页）:
>   - 推理 Pipeline 总览（从输入到最终输出）
>   - 推理架构图（与训练的差异用颜色/标注区分）
>   - 推理独有模块（如 Beam Search、KV-Cache、Post-processing）
>   - 推理优化策略（量化、蒸馏、批处理等）
>   - 推理 Shape 流：从用户输入到模型输出的完整维度变化
>
> - **⚡ 训练 vs 推理对比页**（1 页）:
>   - 并排对比表：数据流、模块差异、计算图差异、资源消耗
>   - 用 Mermaid 或 HTML 流程图可视化两条路径的分叉与合并
>
> **Visual Style:**
> - 浅色苹果风
> - San Francisco/Roboto 字体
> - Mermaid.js 架构图/流程图
> - 训练流程用 🟦蓝色系 标识，推理流程用 🟩绿色系 标识，便于视觉区分
>
> **Output:**
> 直接输出完整可运行 HTML 代码。