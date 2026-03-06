---
name: fluent-design
version: 1.0.0
description: Microsoft Fluent Design System 实战参考。涵盖 Windows 11 设计语言、Mica/Acrylic 材质、WinUI 3 控件规格、排版层级、布局模式、Dark Mode、辅助功能和 Electron 适配。适用于开发 Windows 桌面应用或需要 Windows 原生感的跨平台应用。
---

# Microsoft Fluent Design System 实战参考

Windows 11 设计语言的实战速查，覆盖材质、控件、布局和跨平台适配。

## 适用场景

- Windows 桌面应用 UI 设计（WinUI / Electron / WPF）
- 需要 Windows 原生感的跨平台应用
- Electron 应用在 Windows 上的视觉适配
- 审计现有 UI 是否符合 Fluent Design

## 不适用

- macOS / iOS 原生应用（参考 apple-hig）
- Android 应用（参考 material-design）

---

## 1. 核心设计原则

Fluent Design 2 的五大支柱：

| 原则 | 含义 | 实践 |
|------|------|------|
| **Light（光照）** | 用光线引导注意力 | Reveal Highlight、悬浮发光效果 |
| **Depth（深度）** | 通过层次感建立空间 | 阴影、z-axis 堆叠 |
| **Motion（动效）** | 有意义的动画 | Connected Animation、页面转场 |
| **Material（材质）** | 半透明材质融入环境 | Mica、Acrylic |
| **Scale（缩放）** | 适应各种设备 | 响应式布局、触控适配 |

### 与 Apple HIG 的核心区别

```
Apple: 内容优先，UI 退后，极简克制
Fluent: 环境融合，材质透明，层次丰富
Apple: 实色背景为主
Fluent: Mica/Acrylic 半透明为主
Apple: 标题栏极简（红黄绿三点）
Fluent: 标题栏可承载导航（NavigationView）
```

---

## 2. 材质系统

### Mica（云母）

```
特点：从桌面壁纸取色，轻微染色效果
用于：窗口背景、标题栏背景
性能：低开销（静态取色，不实时模糊）
```

```css
/* Mica 模拟（Electron/Web） */
.mica-bg {
  background-color: rgba(243, 243, 243, 0.9); /* Light */
  /* Dark: rgba(32, 32, 32, 0.9) */
}
```

### Acrylic（亚克力）

```
特点：高斯模糊 + 噪点 + 排除混合
用于：弹出菜单、Flyout、Command Bar、侧边栏
性能：中等开销（实时 blur）
分类：
  - Background Acrylic：模糊桌面内容（窗口级）
  - In-App Acrylic：模糊应用内内容（组件级）
```

```css
/* Acrylic 模拟 */
.acrylic {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(60px) saturate(125%);
  -webkit-backdrop-filter: blur(60px) saturate(125%);
  /* 可加噪点纹理 */
}

.acrylic-dark {
  background: rgba(32, 32, 32, 0.65);
  backdrop-filter: blur(60px) saturate(125%);
}
```

### Smoke（烟雾）

```
用于：弹窗遮罩层
效果：暗色半透明覆盖
```

```css
.smoke {
  background: rgba(0, 0, 0, 0.3); /* Light */
  /* Dark: rgba(0, 0, 0, 0.5) */
}
```

### 材质选择规则

| 场景 | 材质 | 原因 |
|------|------|------|
| 窗口主背景 | Mica | 低性能开销，与桌面融合 |
| 弹出菜单/Flyout | Acrylic | 暗示临时性和层次 |
| 侧边栏 | Mica Alt | 区分于主内容区 |
| 对话框遮罩 | Smoke | 聚焦于对话框内容 |
| 性能敏感场景 | 实色 fallback | Acrylic 可选降级 |

---

## 3. 颜色系统

### Windows System Colors

| 颜色 | Light HEX | Dark HEX | 用途 |
|------|-----------|----------|------|
| Accent（默认蓝） | `#0078D4` | `#4CC2FF` | 主强调色、链接、选中态 |
| Accent Light 1 | `#429CE3` | `#62CDFF` | Hover 态 |
| Accent Light 2 | `#65B4EE` | `#99EBFF` | 次要强调 |
| Accent Dark 1 | `#005A9E` | `#0093F9` | Pressed 态 |

> Windows 用户可自定义 Accent Color，应用需要适配任意颜色。

### 语义色

| 角色 | Light | Dark |
|------|-------|------|
| Text Primary | `#1A1A1A` / `rgba(0,0,0,0.9)` | `#FFFFFF` |
| Text Secondary | `rgba(0,0,0,0.6)` | `rgba(255,255,255,0.79)` |
| Text Tertiary | `rgba(0,0,0,0.45)` | `rgba(255,255,255,0.54)` |
| Text Disabled | `rgba(0,0,0,0.36)` | `rgba(255,255,255,0.36)` |
| Subtle Fill | `rgba(0,0,0,0.04)` | `rgba(255,255,255,0.06)` |
| Secondary Fill | `rgba(0,0,0,0.06)` | `rgba(255,255,255,0.08)` |
| Card Background | `rgba(255,255,255,0.7)` | `rgba(255,255,255,0.05)` |
| Stroke Default | `rgba(0,0,0,0.06)` | `rgba(255,255,255,0.07)` |
| Stroke Divider | `rgba(0,0,0,0.08)` | `rgba(255,255,255,0.08)` |
| Layer Default | `rgba(255,255,255,0.5)` | `rgba(58,58,58,0.3)` |

### 状态色

| 状态 | Light | Dark | 用途 |
|------|-------|------|------|
| Success | `#0F7B0F` | `#6CCB5F` | 成功、完成 |
| Caution | `#9D5D00` | `#FCE100` | 警告 |
| Critical | `#C42B1C` | `#FF99A4` | 错误、危险 |
| Info | `#0078D4` | `#4CC2FF` | 信息（= Accent） |

---

## 4. 排版

### 字体栈

```css
font-family: 'Segoe UI Variable', 'Segoe UI', system-ui, sans-serif;
```

Windows 11 使用 Segoe UI Variable（可变字体）。旧版 Windows 用 Segoe UI。

### 字号层级

| 层级 | 字号 | 字重 | 行高 | 用途 |
|------|------|------|------|------|
| Display | 68px | Semibold | 92px | 超大标题（极少用） |
| Title Large | 40px | Semibold | 52px | 页面标题 |
| Title | 28px | Semibold | 36px | 区块标题 |
| Subtitle | 20px | Semibold | 28px | 次级标题 |
| Body Large | 18px | Regular | 24px | 强调正文 |
| Body | 14px | Regular | 20px | 默认正文 |
| Body Strong | 14px | Semibold | 20px | 加粗正文 |
| Caption | 12px | Regular | 16px | 辅助文字 |
| Caption Strong | 12px | Semibold | 16px | 加粗辅助 |

### 与 Apple 对比

```
Windows Body = 14px → macOS Body = 13px → iOS Body = 17px
Windows 标题偏大偏粗（Semibold），Apple 标题偏克制（Regular/Medium）
```

---

## 5. 控件规格

### 标准控件尺寸

| 控件 | 高度 | 圆角 | 内边距 |
|------|------|------|--------|
| Button | 32px | 4px | 12px 水平 |
| TextBox | 32px | 4px | 8px 水平 |
| ComboBox | 32px | 4px | 12px 水平 |
| Checkbox | 20×20px | 4px | — |
| RadioButton | 20×20px | 50% | — |
| ToggleSwitch | 20×40px | 10px | — |
| Slider | 4px 轨道 | 2px | — |
| ProgressBar | 2px 轨道 | 1px | — |
| InfoBar | 48px | 4px | 12px |

### 圆角规则（Windows 11）

| 元素 | 圆角 |
|------|------|
| 窗口 | 8px |
| 对话框/Flyout | 8px |
| 控件（Button/Input） | 4px |
| Checkbox/Toggle | 4px |
| Tooltip | 4px |
| 嵌套元素 | 内层比外层小 2px |

> **嵌套圆角规则**：外层 8px → 内层 6px → 再内层 4px。避免圆角与直角混搭。

### 底部圆角加粗（Button 特色）

WinUI 3 的 Button 底边比其他三边 **粗 1px**（`border-bottom: 1px solid darker`），模拟微弱的 3D 凸起感：

```css
.fluent-button {
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-bottom: 1px solid rgba(0, 0, 0, 0.16); /* 底部加深 */
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.7);
}
```

---

## 6. 导航模式

### NavigationView（最常用）

```
┌─ 汉堡按钮 ─────────────────────────────┐
│ ☰ App Name                              │
├─────────┬───────────────────────────────┤
│ 🏠 Home  │                               │
│ 📦 Items │          Content Area         │
│ 📊 Stats │                               │
│         │                               │
│─────────│                               │
│ ⚙️ 设置  │                               │
└─────────┴───────────────────────────────┘
```

| 模式 | 触发条件 | 特征 |
|------|---------|------|
| Left Expanded | 窗口宽 ≥ 1008px | Sidebar 常驻展开 |
| Left Compact | 640px ≤ 宽 < 1008px | 只显示图标 |
| Left Minimal | 宽 < 640px | 汉堡菜单，点击展开 |
| Top | — | 水平导航栏 |

### TabView（多标签页）

类似浏览器 Tab，用于多文档/多实例场景。

### Breadcrumb Bar

```
Home > Category > Subcategory > Current
```

用于深层级导航，每级可点击跳转。

---

## 7. 阴影系统

### Elevation（海拔）

| 层级 | 阴影 | 用途 |
|------|------|------|
| 0 | 无 | 内容区域 |
| 2 | `0 2px 4px rgba(0,0,0,0.04)` | Card、Expander |
| 4 | `0 2px 4px rgba(0,0,0,0.04), 0 0 2px rgba(0,0,0,0.06)` | CommandBar |
| 8 | `0 4px 8px rgba(0,0,0,0.08), 0 0 2px rgba(0,0,0,0.06)` | Flyout、Menu |
| 16 | `0 8px 16px rgba(0,0,0,0.12), 0 0 2px rgba(0,0,0,0.06)` | Dialog |
| 32 | `0 16px 32px rgba(0,0,0,0.16), 0 0 2px rgba(0,0,0,0.06)` | 拖拽浮层 |
| 64 | `0 32px 64px rgba(0,0,0,0.24), 0 0 2px rgba(0,0,0,0.06)` | 全屏弹窗 |

> Dark 模式下阴影透明度加倍，但实际效果更弱。Fluent 2 更依赖 stroke（border）区分层次。

---

## 8. 动画

### 标准时长

| 类型 | 时长 | 缓动 |
|------|------|------|
| Fast（控件响应） | 83ms | ease-out |
| Normal（状态切换） | 167ms | ease-out |
| Slow（页面转场） | 250ms | ease-in-out |
| Emphasis（强调） | 333ms | ease-in-out |

### Fluent 标准缓动

```css
/* Decelerate (ease-out) — 进入 */
--fluent-decelerate: cubic-bezier(0, 0, 0, 1);

/* Accelerate (ease-in) — 退出 */
--fluent-accelerate: cubic-bezier(1, 0, 1, 1);

/* Standard (ease-in-out) — 通用 */
--fluent-standard: cubic-bezier(0.8, 0, 0.2, 1);

/* Point to Point — 不离开屏幕的移动 */
--fluent-point: cubic-bezier(0.55, 0.55, 0, 1);
```

### 动画原则

```
✅ 进入用 Decelerate — 从快到慢（感觉有惯性）
✅ 退出用 Accelerate — 从慢到快（快速消失）
✅ 不离开屏幕的移动用 Point to Point
❌ 不用 linear — Fluent 所有动画都有缓动
```

---

## 9. Electron 适配 Windows

### 窗口设置

```typescript
// 无框窗口 + 自定义标题栏
const win = new BrowserWindow({
  frame: false,
  titleBarStyle: 'hidden',
  titleBarOverlay: {
    color: 'transparent',
    symbolColor: '#1A1A1A',
    height: 48, // Fluent 标题栏高度
  },
});
```

### 圆角窗口

Windows 11 自动给窗口加 8px 圆角，**不需要 CSS 处理**。但应用内容需要配合：

```css
/* 避免内容溢出窗口圆角 */
html, body {
  border-radius: 8px;
  overflow: hidden;
}
```

### 字体渲染

```css
/* Windows 上启用亚像素渲染 */
body {
  -webkit-font-smoothing: auto; /* 不要用 antialiased */
  text-rendering: optimizeLegibility;
}
```

> macOS 用 `antialiased`（灰度抗锯齿），Windows 用 `auto`（ClearType 亚像素）。跨平台 Electron 应用需分平台设置。

---

## 10. 与 macOS 差异速查

| 差异点 | Windows (Fluent) | macOS (HIG) |
|--------|-----------------|-------------|
| 窗口按钮 | 右上角（最小化/最大化/关闭） | 左上角（红黄绿） |
| 默认正文 | 14px Segoe UI | 13px SF Pro |
| 控件高度 | 32px | 22px |
| 控件圆角 | 4px | 5px |
| 背景材质 | Mica / Acrylic | vibrancy（仅原生） |
| 主强调色 | `#0078D4`（用户可改） | `#007AFF` |
| 滚动条 | 默认可见 2px | 默认隐藏 |
| 上下文菜单 | 右键 | 右键 / Ctrl+Click |
| 设置入口 | NavigationView 最下方 | 菜单栏 → 偏好设置 |

---

## 11. Checklist

### 设计审计
- [ ] 窗口圆角 8px（Windows 11）
- [ ] 控件圆角 4px
- [ ] 使用 Mica 或 Acrylic 背景
- [ ] 按钮底边加深 1px
- [ ] 导航使用 NavigationView 模式
- [ ] 文字使用 Segoe UI Variable
- [ ] 阴影使用标准 elevation 级别
- [ ] 动画使用 Fluent 标准缓动

### Electron 适配
- [ ] titleBarOverlay 配置正确
- [ ] 窗口圆角不裁剪内容
- [ ] 字体渲染用 `auto`（非 antialiased）
- [ ] accent color 支持系统设置

---

## 来源

Microsoft Fluent Design System 2 (fluent2.microsoft.design) + WinUI 3 Gallery 控件参考。
