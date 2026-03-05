# Douyin Cover Builder（抖音封面生成器）

- 这是一个面向中文创作者的 OpenClaw Skill，输入主题与人物气质后，会输出可直接用于生图模型的高质量提示词与创意说明。  
  This OpenClaw skill helps Chinese creators generate high-quality image prompts and art direction notes for Douyin covers.

- 然后将提示词输入给出图模型即可，比如 GPT。  
  Paste the generated prompt into your image model (e.g., GPT image generation).

## 核心风格 Core Style

- 带弧度的大标题（Subtle Arc Headline）
- 关键字突出高亮（Keyword Highlight）
- 右下角人物（Right-bottom Character）
- 左下角主视觉 + 背景按主题创作（Theme-driven Left Visual + Background）

## 使用效果图 Preview

![使用效果图 Preview](./docs/images/preview.png)

## 功能特性 Features

- 主题驱动主视觉（不是固定素材堆砌）
- 关键词高亮（Keyword Highlight）
- 关键词轻弧排版（Subtle Arc Typography）
- 主题自适应配色（Theme-adaptive Color Palette）
- 系列化版式（标题上方 + 人物右下 + 主视觉左下/中下）

## 输入 Input（4项）

1. 主题（Topic）
2. 关键点（Key Points，可选）
3. 右下角人物气质/姿势（Pose & Vibe）
4. 画幅（竖版 or 横版 4:3）

> 推荐上传人物照片，以保持同一人脸一致性。  
> Uploading a portrait is recommended for consistent identity.

## 输出 Output

- 最终提示词 Final Prompt（可直接贴到生图模型）
- 创意说明 Art Direction Brief（解释主视觉、配色与关键词策略）

## 使用建议 Tips

- 如果第一次出图有局部不满意（文字、手势、背景元素等），可在出图后基于当前提示词微调修复。  
  If needed, refine details with a follow-up prompt after first generation.
- 本 skill 的重点是封面结构与风格一致性，你可以在一致框架下持续优化细节。  
  The priority is structural and stylistic consistency across your cover series.

## 快速示例 Quick Example

- 主题：龙虾机器人 5分钟写一个微信
- 关键点：使用龙虾机器人作为核心主视觉，突出“5分钟写完”的效率感与自动化能力
- 人物气质/姿势：右下角我本人，抱头惊讶的表情（震惊但兴奋）
- 画幅：竖版 严格 4:3

## 文件结构 Project Structure

- `SKILL.md`：核心行为与规则（Main behavior contract）
- `templates/final_prompt_template.md`：最终提示词模板（Prompt template）
- `docs/USAGE.md`：使用说明（Usage guide）
- `docs/NOTES.md`：设计与迭代备注（Design notes）

---

欢迎持续迭代：只要保持核心风格一致，就能稳定产出系列化封面。
Keep iterating under the same style system for reliable, scalable cover output.