# ClawHub技能探索和导航工具

## 项目概述

ClawHub技能探索和导航工具是一个专门为ClawHub平台设计的技能发现工具。它允许用户通过关键词搜索和分类浏览快速找到所需的技能，提高了技能发现的效率。

## 主要功能

### 🔍 **技能搜索**
- 支持关键词搜索技能
- 搜索结果支持按相关性排序
- 搜索历史记录

### 📂 **技能分类**
- 按技能类别分类显示
- 支持技能标签筛选
- 推荐相关技能

### 🏷️ **标签系统**
- 支持多种技能标签
- 标签云可视化
- 标签搜索功能

### 📊 **技能详情**
- 查看技能详细信息
- 技能安装和使用指南
- 技能版本历史

### 🌟 **收藏功能**
- 支持收藏感兴趣的技能
- 管理个人技能收藏
- 分享收藏的技能

## 安装和使用

### 安装技能

```bash
clawhub install clawhub-skill-explorer
```

### 常用命令

#### 搜索技能

```bash
clawhub-skill-explorer search --query "problem solving"
```

#### 浏览分类

```bash
clawhub-skill-explorer browse --category "productivity"
```

#### 查看技能详情

```bash
clawhub-skill-explorer view --slug "clawhub-search-verify"
```

#### 收藏技能

```bash
clawhub-skill-explorer favorite --slug "clawhub-search-verify"
```

## 开发指南

### 项目结构

```
clawhub-skill-explorer/
├── src/
│   ├── components/          # 前端组件
│   ├── services/            # API服务
│   ├── utils/              # 工具函数
│   └── constants.js        # 常量定义
├── public/                 # 静态资源
├── tests/                 # 测试文件
├── package.json           # 项目依赖
└── README.md             # 项目说明
```

### 开发流程

1. 克隆项目到本地
2. 安装依赖：`npm install`
3. 启动开发服务器：`npm start`
4. 运行测试：`npm test`
5. 构建生产版本：`npm run build`

## 技术架构

### 前端技术栈

- **React.js**：用户界面框架
- **Tailwind CSS**：样式框架
- **React Router**：路由管理
- **Axios**：HTTP客户端
- **React Query**：数据管理

### 后端技术栈

- **Node.js**：服务器端运行环境
- **Express**：Web应用框架
- **MongoDB**：数据库
- **Mongoose**：ODM工具

### API集成

- **ClawHub API**：获取技能数据
- **GitHub API**：获取项目信息
- **Google Analytics**：用户行为分析

## 测试

### 单元测试

```bash
npm test
```

### 集成测试

```bash
npm run test:e2e
```

### 代码覆盖

```bash
npm run coverage
```

## 部署

### 开发部署

```bash
npm run dev
```

### 生产部署

```bash
npm run build
npm run start:prod
```

### 容器化部署

```bash
docker build -t clawhub-skill-explorer .
docker run -p 3000:3000 clawhub-skill-explorer
```

## 版本控制

- **主要版本**：重大功能更新
- **次要版本**：新功能或改进
- **补丁版本**：bug修复

## 许可证

MIT License - 详见LICENSE文件

## 联系方式

如有问题或建议，请通过以下方式联系：

- **项目仓库**：[GitHub Repository](https://github.com/clawhub/clawhub-skill-explorer)
- **问题反馈**：[Issue Tracker](https://github.com/clawhub/clawhub-skill-explorer/issues)
- **文档**：[项目文档](https://clawhub.ai/skills/clawhub-skill-explorer)

---

**ClawHub技能探索和导航工具** - 让技能发现更简单，让工作更高效！
