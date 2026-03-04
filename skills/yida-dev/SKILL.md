---
name: yida-dev
description: 钉钉宜搭(yida)低代码平台开发助手。用于：(1) 创建表单和自定义页面 (2) 编写 JS 动作面板代码 (3) 使用 JS-API 操作组件和数据 (4) 配置远程数据源 (5) 设计流程和集成自动化 (6) 解决开发问题
---

## 平台能力

| 能力 | 说明 | 版本要求 |
|------|------|----------|
| 表单搭建 | 拖拽式表单设计，流程审批 | 免费版 |
| 自定义页面 | 拖拽页面 + JS 逻辑 | 专业版+ |
| JS 代码 | 动作面板编写业务逻辑 | 专业版+ |
| JS-API | 前端调用组件/路由/工具 | 专业版+ |
| Open API | 服务端 CRUD 接口 | 专业版+ |

## 核心概念

### 组件别名（推荐）

专业版/专属版支持别名，代替 fieldId：

```js
// 推荐 ✅
this.$('userName').getValue();

// 不推荐 ❌
this.$('textField_xxx').getValue();
```

### 状态与生命周期

```js
this.state.xxx        // 获取状态
this.setState({...}) // 设置状态

didMount()           // 页面加载完成
willUnmount()        // 页面卸载前
```

### 事件

```js
export function onClick() { }
export function onFieldChange() { }
```

## 参考文档

- [JS-API](references/js-api.md) - 前端组件操作
- [JSX 组件](references/jsx.md) - 自定义渲染
- [服务端 API](references/server-api.md) - 后端接口调用
- [公式函数](references/formulas.md) - 表单公式
- [集成自动化](references/integrations.md) - 流程自动化
- [故障排查](references/troubleshooting.md) - 调试指南
- [TodoMVC 教程](scripts/todomvc.md) - 入门示例
