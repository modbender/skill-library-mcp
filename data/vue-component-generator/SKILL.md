---
name: vue-component-generator
description: 生成 Vue 3 组件模板，支持 Composition API、Options API、TypeScript、SFC 单文件组件，一键生成完整 Vue 组件代码。
metadata: {"clawdbot":{"emoji":"💚","requires":{},"primaryEnv":""}}
---

# Vue Component Generator

快速生成专业的 Vue 3 组件代码。

## 功能

- ⚡ 一键生成组件
- 📝 支持 TypeScript
- 🎯 Composition API / Options API
- 🎨 SCSS 样式支持
- 📖 Props/Emits 定义

## 支持的 API

| API | 说明 |
|-----|------|
| composition | Composition API (推荐) |
| options | Options API |
| script-setup | `<script setup>` 语法 |

## 组件类型

- 普通组件
- 路由组件
- 布局组件
- 表单组件

## 使用方法

### 基本用法

```bash
# 生成 Composition API 组件
vue-component-generator MyButton --api composition

# 生成 Options API 组件
vue-component-generator MyModal --api options

# 生成 TypeScript 组件
vue-component-generator MyForm --typescript
```

### 选项

| 选项 | 说明 |
|------|------|
| `--api, -a` | API 类型 (composition/options) |
| `--typescript, -t` | 启用 TypeScript |
| `--scss, -s` | 启用 SCSS |
| `--output, -o` | 输出目录 |

## 输出示例

```vue
<template>
  <div class="my-button">
    <button @click="handleClick">
      {{ label }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  label: {
    type: String,
    default: 'Click me'
  }
})

const emit = defineEmits(['click'])

const handleClick = () => {
  emit('click')
}
</script>

<style scoped>
.my-button {
  padding: 10px 20px;
}
</style>
```

## 安装

```bash
# 无需额外依赖
```

## 变现思路

1. **组件库模板** - 销售专业组件库模板
2. **企业服务** - 定制 Vue 组件
3. **培训** - Vue 开发培训

## 更多示例

### 表单组件

```bash
vue-component-generator InputField --api composition --typescript
```

### 模态框

```bash
vue-component-generator Modal --api composition --scss
```
