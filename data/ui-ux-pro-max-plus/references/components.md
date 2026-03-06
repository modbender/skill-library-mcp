# 组件设计规范

常用 UI 组件的设计规范，确保一致性。

---

## 🔘 按钮（Button）

### 尺寸规范

| 尺寸 | 高度 | 内边距 | 字体 |
|-----|-----|-------|-----|
| Small | 32px | px-3 py-1.5 | text-sm |
| Default | 40px | px-4 py-2 | text-base |
| Large | 48px | px-6 py-3 | text-lg |

### 样式变体

**主要按钮：**
```html
<button class="bg-blue-600 text-white px-4 py-2 rounded-lg
               hover:bg-blue-700 
               active:bg-blue-800
               disabled:bg-gray-300 disabled:cursor-not-allowed
               transition-colors">
  主要操作
</button>
```

**次要按钮：**
```html
<button class="border border-gray-300 bg-white text-gray-700 
               px-4 py-2 rounded-lg
               hover:bg-gray-50
               active:bg-gray-100">
  次要操作
</button>
```

**危险按钮：**
```html
<button class="bg-red-600 text-white px-4 py-2 rounded-lg
               hover:bg-red-700">
  删除
</button>
```

**文字按钮：**
```html
<button class="text-blue-600 hover:text-blue-700 
               hover:underline px-2 py-1">
  了解更多
</button>
```

**图标按钮：**
```html
<button class="p-2 rounded-lg hover:bg-gray-100 
               text-gray-600 hover:text-gray-900">
  <svg class="w-5 h-5"><!-- 图标 --></svg>
</button>
```

---

## 📥 输入框（Input）

### 基础输入框
```html
<div class="space-y-1">
  <label class="text-sm font-medium text-gray-700">
    邮箱地址
  </label>
  <input type="email" 
         placeholder="you@example.com"
         class="w-full px-3 py-2 border border-gray-300 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-blue-500 
                focus:border-transparent
                placeholder:text-gray-400" />
</div>
```

### 带图标输入框
```html
<div class="relative">
  <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400">
    <!-- 搜索/邮件图标 -->
  </svg>
  <input class="w-full pl-10 pr-3 py-2 border rounded-lg" />
</div>
```

### 错误状态
```html
<div class="space-y-1">
  <label class="text-sm font-medium text-gray-700">邮箱</label>
  <input class="w-full px-3 py-2 border border-red-500 rounded-lg
                focus:ring-2 focus:ring-red-500" />
  <p class="text-sm text-red-600">请输入有效的邮箱地址</p>
</div>
```

---

## ☑️ 复选框与单选框

### 复选框
```html
<label class="flex items-center gap-2 cursor-pointer">
  <input type="checkbox" 
         class="w-4 h-4 rounded border-gray-300 
                text-blue-600 focus:ring-blue-500" />
  <span class="text-gray-700">记住我</span>
</label>
```

### 单选框组
```html
<div class="space-y-2">
  <label class="flex items-center gap-2">
    <input type="radio" name="plan" value="free"
           class="w-4 h-4 text-blue-600 focus:ring-blue-500" />
    <span>免费版</span>
  </label>
  <label class="flex items-center gap-2">
    <input type="radio" name="plan" value="pro"
           class="w-4 h-4 text-blue-600 focus:ring-blue-500" />
    <span>专业版</span>
  </label>
</div>
```

### 开关（Toggle）
```html
<label class="relative inline-flex items-center cursor-pointer">
  <input type="checkbox" class="sr-only peer">
  <div class="w-11 h-6 bg-gray-200 peer-focus:ring-4 
              peer-focus:ring-blue-300 rounded-full peer
              peer-checked:after:translate-x-full 
              peer-checked:after:border-white
              after:content-[''] after:absolute after:top-0.5 
              after:left-[2px] after:bg-white after:border-gray-300 
              after:border after:rounded-full after:h-5 after:w-5 
              after:transition-all peer-checked:bg-blue-600">
  </div>
  <span class="ml-3 text-gray-700">启用通知</span>
</label>
```

---

## 📋 下拉选择（Select）

### 原生选择器
```html
<div class="space-y-1">
  <label class="text-sm font-medium">国家/地区</label>
  <select class="w-full px-3 py-2 border border-gray-300 rounded-lg
                 focus:ring-2 focus:ring-blue-500 focus:border-transparent
                 bg-white">
    <option value="">请选择</option>
    <option value="cn">中国</option>
    <option value="us">美国</option>
  </select>
</div>
```

### 自定义下拉（按钮式）
```html
<div class="relative">
  <button class="w-full px-3 py-2 border rounded-lg text-left 
                 flex justify-between items-center">
    <span>选择选项</span>
    <svg class="w-4 h-4"><!-- 箭头 --></svg>
  </button>
  <!-- 下拉菜单 -->
  <div class="absolute top-full mt-1 w-full bg-white border 
              rounded-lg shadow-lg z-10">
    <div class="py-1">
      <button class="w-full px-4 py-2 text-left hover:bg-gray-50">
        选项 1
      </button>
    </div>
  </div>
</div>
```

---

## 🃏 卡片（Card）

### 基础卡片
```html
<div class="bg-white rounded-lg shadow p-6">
  <h3 class="text-lg font-semibold mb-2">卡片标题</h3>
  <p class="text-gray-600">卡片内容描述...</p>
</div>
```

### 带图片卡片
```html
<div class="bg-white rounded-lg shadow overflow-hidden">
  <img src="..." class="w-full h-48 object-cover" />
  <div class="p-6">
    <h3 class="text-lg font-semibold mb-2">标题</h3>
    <p class="text-gray-600 mb-4">描述...</p>
    <button class="text-blue-600 hover:underline">了解更多</button>
  </div>
</div>
```

### 统计卡片
```html
<div class="bg-white rounded-lg shadow p-6">
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-gray-500 text-sm font-medium">总收入</h3>
    <span class="text-green-500 text-sm">↑ 12%</span>
  </div>
  <p class="text-3xl font-bold">¥48,290</p>
</div>
```

---

## 🔔 警告提示（Alert）

### 信息提示
```html
<div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
  <div class="flex items-start gap-3">
    <svg class="w-5 h-5 text-blue-600 mt-0.5"><!-- 图标 --></svg>
    <div>
      <h4 class="font-medium text-blue-900">提示</h4>
      <p class="text-blue-700 text-sm mt-1">这是一条信息提示。</p>
    </div>
  </div>
</div>
```

### 成功提示
```html
<div class="bg-green-50 border border-green-200 rounded-lg p-4">
  <div class="flex items-center gap-3">
    <svg class="w-5 h-5 text-green-600"><!-- 勾选图标 --></svg>
    <p class="text-green-800 font-medium">操作成功！</p>
  </div>
</div>
```

### 警告提示
```html
<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
  <div class="flex items-start gap-3">
    <svg class="w-5 h-5 text-yellow-600 mt-0.5"><!-- 警告图标 --></svg>
    <div>
      <h4 class="font-medium text-yellow-900">注意</h4>
      <p class="text-yellow-700 text-sm mt-1">请检查您的输入。</p>
    </div>
  </div>
</div>
```

### 错误提示
```html
<div class="bg-red-50 border border-red-200 rounded-lg p-4">
  <div class="flex items-start gap-3">
    <svg class="w-5 h-5 text-red-600 mt-0.5"><!-- 错误图标 --></svg>
    <div>
      <h4 class="font-medium text-red-900">出错了</h4>
      <p class="text-red-700 text-sm mt-1">无法连接到服务器。</p>
    </div>
  </div>
</div>
```

---

## 🎴 徽章（Badge）

```html
<!-- 默认 -->
<span class="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs">
  标签
</span>

<!-- 状态徽章 -->
<span class="px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
  ● 活跃
</span>

<span class="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs">
  ● 待处理
</span>

<span class="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs">
  ● 已停止
</span>

<!-- 数字徽章 -->
<span class="px-2 py-0.5 bg-blue-600 text-white rounded-full text-xs font-medium">
  12
</span>
```

---

## 📊 进度条

### 线性进度条
```html
<div class="w-full bg-gray-200 rounded-full h-2">
  <div class="bg-blue-600 h-2 rounded-full" style="width: 60%"></div>
</div>
```

### 带标签进度条
```html
<div class="space-y-2">
  <div class="flex justify-between text-sm">
    <span class="text-gray-600">进度</span>
    <span class="text-gray-900 font-medium">60%</span>
  </div>
  <div class="w-full bg-gray-200 rounded-full h-2">
    <div class="bg-blue-600 h-2 rounded-full transition-all" 
         style="width: 60%"></div>
  </div>
</div>
```

### 步骤进度条
```html
<div class="flex items-center">
  <div class="flex items-center">
    <div class="w-8 h-8 rounded-full bg-blue-600 text-white 
                flex items-center justify-center text-sm font-medium">1</div>
    <div class="w-16 h-1 bg-blue-600"></div>
  </div>
  <div class="flex items-center">
    <div class="w-8 h-8 rounded-full bg-blue-600 text-white 
                flex items-center justify-center text-sm font-medium">2</div>
    <div class="w-16 h-1 bg-gray-300"></div>
  </div>
  <div class="w-8 h-8 rounded-full bg-gray-300 text-gray-600 
              flex items-center justify-center text-sm font-medium">3</div>
</div>
```

---

## 🗂️ 标签页（Tabs）

### 水平标签
```html
<div class="border-b">
  <nav class="flex gap-6">
    <button class="pb-2 border-b-2 border-blue-600 text-blue-600 font-medium">
      全部
    </button>
    <button class="pb-2 border-b-2 border-transparent text-gray-500 
                   hover:text-gray-700">
      活跃
    </button>
    <button class="pb-2 border-b-2 border-transparent text-gray-500 
                   hover:text-gray-700">
      归档
    </button>
  </nav>
</div>
```

### 胶囊标签
```html
<div class="flex gap-2 p-1 bg-gray-100 rounded-lg">
  <button class="px-4 py-1.5 bg-white rounded-md shadow text-sm font-medium">
    日
  </button>
  <button class="px-4 py-1.5 text-gray-600 hover:text-gray-900 text-sm">
    周
  </button>
  <button class="px-4 py-1.5 text-gray-600 hover:text-gray-900 text-sm">
    月
  </button>
</div>
```

---

## 🧭 导航

### 面包屑
```html
<nav class="flex items-center gap-2 text-sm">
  <a href="/" class="text-gray-500 hover:text-gray-700">首页</a>
  <span class="text-gray-400">/</span>
  <a href="/products" class="text-gray-500 hover:text-gray-700">产品</a>
  <span class="text-gray-400">/</span>
  <span class="text-gray-900">详情</span>
</nav>
```

### 分页
```html
<div class="flex items-center gap-2">
  <button class="px-3 py-1 border rounded hover:bg-gray-50">上一页</button>
  <button class="px-3 py-1 bg-blue-600 text-white rounded">1</button>
  <button class="px-3 py-1 border rounded hover:bg-gray-50">2</button>
  <button class="px-3 py-1 border rounded hover:bg-gray-50">3</button>
  <span class="text-gray-400">...</span>
  <button class="px-3 py-1 border rounded hover:bg-gray-50">10</button>
  <button class="px-3 py-1 border rounded hover:bg-gray-50">下一页</button>
</div>
```

---

## 📝 设计令牌（Design Tokens）

### 圆角
```
rounded-none:  0px
rounded-sm:    2px
rounded:       4px
rounded-md:    6px
rounded-lg:    8px
rounded-xl:    12px
rounded-2xl:   16px
rounded-3xl:   24px
rounded-full:  9999px
```

### 阴影
```
shadow-sm:   0 1px 2px 0 rgb(0 0 0 / 0.05)
shadow:      0 1px 3px 0 rgb(0 0 0 / 0.1)
shadow-md:   0 4px 6px -1px rgb(0 0 0 / 0.1)
shadow-lg:   0 10px 15px -3px rgb(0 0 0 / 0.1)
shadow-xl:   0 20px 25px -5px rgb(0 0 0 / 0.1)
```

### 间距
```
基础单位: 4px (0.25rem)

space-1:  4px
space-2:  8px
space-3:  12px
space-4:  16px
space-5:  20px
space-6:  24px
space-8:  32px
space-10: 40px
space-12: 48px
space-16: 64px
```

---

**记住：** 组件的一致性 = 品牌的专业性。
