# React Next.js 项目生成器主控制器

当用户提交需求文档和UI设计图时：

1. 如果提供了图像，使用 `image` 工具分析UI设计图，识别组件、布局和交互元素
2. 如果提供了文档，使用文本分析提取功能需求和技术要求
3. 调用 `/Users/batype/.openclaw/workspace/skills/react-nextjs-generator/create-react-app.sh` 创建基础项目结构
4. 根据分析结果定制化生成页面、组件和状态管理逻辑

技术栈：
- React
- Next.js
- Ant Design
- Tailwind CSS
- Zustand

该技能会创建一个完整的项目，包含适当的目录结构、状态管理、样式配置和组件实现。