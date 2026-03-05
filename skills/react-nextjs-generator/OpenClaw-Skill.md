# React Next.js 项目生成器技能

## 描述
根据需求文档和UI设计图生成完整的React + Next.js项目，使用Ant Design、Tailwind CSS和Zustand技术栈。

## 触发条件
当用户请求根据需求文档和UI图生成React项目时激活此技能。

## 执行步骤
1. 检查用户提供的需求文档和UI设计图
2. 如果有图像文件，使用 `image` 工具分析UI元素
3. 使用 `exec` 工具运行项目生成脚本
4. 将需求文档保存到临时文件
5. 调用 `/Users/batype/.openclaw/workspace/skills/react-nextjs-generator/runner.ts` 生成项目
6. 返回生成的项目路径给用户

## 工具使用
- `image`: 分析UI设计图
- `exec`: 运行项目生成脚本
- `write`: 临时保存需求文档
- `read`: 读取生成的项目信息

## 参数
- 需求文档: 文本形式的功能需求、页面结构、组件要求等
- UI设计图 (可选): 图像文件，用于分析视觉设计
- 项目名称 (可选): 指定生成的项目名称
- 输出目录 (可选): 指定项目生成位置