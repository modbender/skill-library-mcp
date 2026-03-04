# Auto Building Skill

基于 AUTO-BUILDING 源码的信息采集管理系统技能，支持自动化内容采集、审核和发布。

## 功能特性

- 🏗️ **自动化采集**: 支持多种数据源类型
- 📊 **智能分类**: 自动内容分类和标签
- 👁️ **人工审核**: 内容审核工作流
- 🎨 **定制化配置**: 灵活配置栏目和分类
- 🔌 **多数据源**: GitHub、RSS、目录网站等

## 安装使用

### 自动安装
```bash
clawdhub install auto-building
```

### 手动安装
```bash
git clone https://github.com/hasd52636-a11y/Auto_Building_new
cd Auto_Building_new
npm install
npm run dev
```

## 配置示例

### 新闻采集系统
```json
{
  "primaryCategories": ["新闻早报"],
  "secondaryCategories": {
    "新闻早报": ["科技", "财经", "创投"]
  },
  "sources": [
    {
      "name": "36kr",
      "type": "rss",
      "url": "https://36kr.com/feed/",
      "enabled": true
    }
  ]
}
```

### 产品监控系统
```json
{
  "primaryCategories": ["产品监控"],
  "secondaryCategories": {
    "产品监控": ["亚马逊", "淘宝", "京东"]
  },
  "sources": [
    {
      "name": "亚马逊",
      "type": "directory",
      "url": "https://www.amazon.cn",
      "enabled": true
    }
  ]
}
```

## 管理界面

启动后访问：
- 前台首页: http://localhost:3000
- 管理后台: http://localhost:3000/admin

在管理后台可以：
- 配置数据源
- 设置采集规则
- 审核采集内容
- 查看系统状态

## 技术支持

- 项目主页: https://sora.wboke.com/
- 源码仓库: https://github.com/hasd52636-a11y/Auto_Building_new
- 问题反馈: GitHub Issues

## 许可证

MIT License