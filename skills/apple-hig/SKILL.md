---
name: apple-hig
version: 1.0.0
description: Apple Human Interface Guidelines 实战参考。涵盖 macOS/iOS 设计规范、System Colors、排版层级、控件规格、布局间距、Dark Mode 适配、辅助功能和平台差异。适用于开发 macOS 桌面应用（Electron/SwiftUI/AppKit）和 iOS 应用时的 UI 设计决策。
---

# Apple Human Interface Guidelines 实战参考

从 Apple 官方 HIG 和生产级桌面应用实战中提炼的设计规范速查。

## 适用场景

- macOS 桌面应用 UI 设计（Electron / SwiftUI / AppKit）
- iOS 应用 UI 设计
- 需要"原生感"的跨平台应用
- 审计现有 UI 是否符合 Apple 设计语言

## 不适用

- Android / Windows 应用（参考 Material Design / Fluent Design）
- Web 专属设计（不追求 native 感）

---

## 1. 核心设计原则

Apple HIG 的三大支柱：

| 原则 | 含义 | 实践 |
|------|------|------|
| **Clarity（清晰）** | 文字可读、图标清晰、功能一目了然 | 用 SF 字体、标准图标、足够对比度 |
| **Deference（顺从）** | UI 服务内容，不喧宾夺主 | 减少装饰、留白充足、动画克制 |
| **Depth（层次）** | 通过视觉层级传达结构 | 阴影、模糊、动画暗示前后关系 |

### 与其他平台的根本区别

```
Apple: 做减法，每一个像素都要有理由
Material: 做加法，用动效和色彩引导注意力
Fluent: 做透明，用 Acrylic/Mica 融入环境
```

---

## 2. 颜色系统

### Apple System Colors

这些颜色在 Light/Dark 模式下自动适配，**优先使用**：

| 颜色 | Light HEX | Dark HEX | 用途 |
|------|-----------|----------|------|
| Blue | `#007AFF` | `#0A84FF` | 主强调色、链接、可交互元素 |
| Green | `#34C759` | `#30D158` | 成功、确认 |
| Orange | `#FF9500` | `#FF9F0A` | 警告 |
| Red | `#FF3B30` | `#FF453A` | 错误、危险操作、删除 |
| Purple | `#AF52DE` | `#BF5AF2` | 辅助强调 |
| Teal | `#5AC8FA` | `#64D2FF` | 次要信息 |
| Yellow | `#FFCC00` | `#FFD60A` | 注意 |
| Pink | `#FF2D55` | `#FF375F` | 情感、收藏 |
| Indigo | `#5856D6` | `#5E5CE6` | 特殊强调 |

### 语义色

| 用途 | Light | Dark |
|------|-------|------|
| Label（主文字） | `#000000` | `#FFFFFF` |
| Secondary Label | `rgba(0,0,0,0.5)` | `rgba(255,255,255,0.55)` |
| Tertiary Label | `rgba(0,0,0,0.25)` | `rgba(255,255,255,0.25)` |
| Quaternary Label | `rgba(0,0,0,0.1)` | `rgba(255,255,255,0.1)` |
| Separator | `rgba(0,0,0,0.1)` | `rgba(255,255,255,0.1)` |
| Background（窗口） | `#FFFFFF` | `#1E1E1E` |
| Secondary BG | `#F5F5F5` | `#2C2C2E` |
| Tertiary BG | `#FFFFFF` | `#3A3A3C` |

### 使用原则

```
✅ 用 System Colors 做交互元素的强调色
✅ 用语义色做文字、背景、分隔线
❌ 不要硬编码 #007AFF — 在 Dark Mode 下它应该变成 #0A84FF
❌ 不要用 System Colors 做静态数据展示（如参数值 "0.3"、"18s"）
```

**铁律**：主强调色严格保留给**强交互元素**（按钮、Checkbox 选中、Slider 填充段、Focus Ring），不用于静态文字/数值。

---

## 3. 排版

### 字体栈

```css
font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif;
```

macOS 上会自动使用 SF Pro，iOS 上使用 SF。不要手动指定 SF Pro 的 TTF 文件。

### 字号层级（macOS）

| 层级 | 字号 | 字重 | 颜色 | 用途 |
|------|------|------|------|------|
| Large Title | 26px | Bold | Label | 页面大标题（iOS 常用，macOS 少用） |
| Title 1 | 22px | Regular | Label | 区块标题 |
| Title 2 | 17px | Regular | Label | 次要标题 |
| Title 3 / Headline | 15px | Semibold | Label | 工具栏标题、卡片标题 |
| Body | 13px | Regular | Label | 正文、控件默认 |
| Callout | 12px | Regular | Label | 注释文字 |
| Subheadline | 11px | Regular | Secondary Label | 辅助说明 |
| Footnote | 10px | Regular | Tertiary Label | 脚注、时间戳 |
| Caption 1 | 10px | Regular | Tertiary Label | 图片说明 |
| Caption 2 | 10px | Medium | Tertiary Label | 表格表头 |

### 字号层级（iOS）

| 层级 | 字号 | 字重 |
|------|------|------|
| Large Title | 34px | Bold |
| Title 1 | 28px | Regular |
| Title 2 | 22px | Regular |
| Title 3 | 20px | Regular |
| Headline | 17px | Semibold |
| Body | 17px | Regular |
| Callout | 16px | Regular |
| Subheadline | 15px | Regular |
| Footnote | 13px | Regular |
| Caption 1 | 12px | Regular |
| Caption 2 | 11px | Regular |

### 实战要点

- **macOS 默认正文 13px**，iOS 默认正文 17px — 差异大，不要混用
- Section 标题用 `11px font-medium text-black/40` 降噪（macOS），**禁止** `uppercase tracking-wide font-bold`
- 静态数值（Slider 值、时间）用 `12px font-mono text-black/50`
- 辅助说明 `10-11px font-normal text-black/25~30`

---

## 4. 控件规格

### macOS 标准控件尺寸

| 控件 | 高度 | 内边距 | 圆角 |
|------|------|--------|------|
| Button（Regular） | 22px | 12px 水平 | 5px |
| Button（Large） | 28px | 16px 水平 | 7px |
| TextField | 22px | 4px 内 | 5px |
| Checkbox | 14×14px | — | 3px |
| Radio | 16×16px（circle） | — | 50% |
| Switch（macOS Ventura+） | 20×34px | — | 10px |
| Slider | 4px 轨道高 | — | 2px |
| Segmented Control | 22px | 6px 水平 | 5px |
| Popup Button | 22px | 内含箭头 | 5px |

### iOS 标准控件

| 控件 | 最小高度 | 触控目标 |
|------|----------|---------|
| Button | 44px | 44×44px |
| TextField | 44px | — |
| Navigation Bar | 44px | — |
| Tab Bar | 49px | — |
| Table Row | 44px | 全宽 |

### ⚠️ 触控目标铁律

```
最小触控目标：44×44pt（iOS） / 24×24px（macOS 鼠标）
```

即使视觉上更小，可点击区域也必须达到最小尺寸。

### Segmented Control（macOS 仿真规格）

| 属性 | 值 |
|------|-----|
| 底座色 | `#e8e8ed` |
| 底座内距 | `p-[3px]` |
| 底座圆角 | `rounded-lg` |
| 选中药丸 | `bg-white rounded-[7px]` |
| 药丸阴影 | `0 1px 3px rgba(0,0,0,0.08), 0 0.5px 1px rgba(0,0,0,0.12)` |
| 文字 | `text-[13px] font-medium` |
| 选中文字 | `text-[#1d1d1f]` |
| 未选中文字 | `text-black/50` |
| 布局 | `flex-1` 平分等宽 |

**不要替换为 Tabs 或 RadioGroup** — Segmented Control 是 2-5 个选项的切换专用控件。

---

## 5. 布局与间距

### macOS 间距系统

| 间距 | 值 | 用途 |
|------|-----|------|
| 最小间距 | 4px | 相关元素间 |
| 控件间距 | 8px | 按钮组、表单字段间 |
| 区块间距 | 12-16px | 功能区块间 |
| 大区块间距 | 20-24px | 页面 section 间 |
| 窗口内边距 | 20px | 窗口内容边距 |

### 窗口

| 属性 | macOS | iOS |
|------|-------|-----|
| 最小宽度 | 400px | — |
| 标题栏高度 | 22px（标准）/ 52px（工具栏） | — |
| Sidebar 宽度 | 200-260px（标准） | — |
| Safe Area | 无 | 顶部/底部刘海 |

### 容器层级

```
✅ 平铺式布局 — 内容直接放在白底上，用间距和微弱分隔线区分
❌ 框套框 — Card 里面套 Card，增加视觉噪音
```

**实战规则**：
- 配置参数直接平铺，不要用 border + padding 整体包裹
- 列表 Header 可用极弱底纹（`bg-[#f5f5f7]/50`）产生软分隔
- 去掉灰色嵌套面板（`bg-s-bg-subtle` Card 套 Card）

---

## 6. 图标

### SF Symbols

Apple 提供 5000+ 个 SF Symbols 图标，与 SF 字体匹配。

```
使用场景：macOS / iOS 原生应用
替代方案：Lucide Icons（Web/Electron，风格接近 SF Symbols）
```

### 图标规格

| 场景 | 尺寸 | 线宽 |
|------|------|------|
| 工具栏 | 16×16px | 1.5px |
| 导航项 | 20×20px | 1.5px |
| Tab Bar（iOS） | 25×25px | — |
| 空状态 | 48-64px | 1px |

### 颜色规则

```
✅ 可交互图标：System Blue（或当前 accent color）
✅ 信息图标：Secondary Label 色
✅ 状态图标：对应 System Color（Green=成功, Red=错误）
❌ 禁止给信息图标上彩色 — 只有可交互/状态图标用色
```

---

## 7. 动画与过渡

### 标准时长

| 类型 | 时长 | 缓动 |
|------|------|------|
| 微交互（hover, press） | 100-200ms | ease-out |
| 状态切换 | 200-300ms | ease-in-out |
| 页面转场 | 300-500ms | ease-in-out |
| 弹窗出现 | 200ms | ease-out |
| 弹窗消失 | 150ms | ease-in |

### Apple 标准缓动

```css
/* macOS 标准 */
--apple-ease: cubic-bezier(0.25, 0.1, 0.25, 1);

/* Spring-like（弹性） */
--apple-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
```

### 动画原则

```
✅ 动画要有目的 — 引导注意力、暗示关系
✅ 支持 prefers-reduced-motion — 简化或禁用动画
❌ 不要为了炫技加动画 — Apple 的动画是"感觉到但说不出"的
❌ 不要用 linear 缓动 — 感觉机械
```

---

## 8. Dark Mode

### 设计原则

```
Dark Mode ≠ 反转颜色
Dark Mode = 重新设计的配色方案
```

| 原则 | 实践 |
|------|------|
| 用语义色 | 不硬编码 `#FFFFFF` / `#000000` |
| 降低饱和度 | Dark 模式中高饱和度色块刺眼 |
| 提高对比度 | 文字/图标的对比度要求更严格 |
| 阴影不可见 | Dark 模式中阴影效果弱，改用微弱边框或高光 |

### macOS Dark Mode 特殊处理

```css
/* Light: 阴影分层 */
box-shadow: 0 1px 3px rgba(0,0,0,0.08);

/* Dark: 阴影无效，改用微弱边框 */
border: 1px solid rgba(255,255,255,0.06);
```

### 适配检查

```
✅ 所有文字在 Dark 背景上对比度 ≥ 4.5:1
✅ 分隔线/边框在两种模式下都可见
✅ 图标在两种模式下都清晰
✅ 品牌色在 Dark 模式下略微提亮
```

---

## 9. 辅助功能（Accessibility）

### WCAG 对比度

| 级别 | 正文 | 大字体（≥18px bold / ≥24px） |
|------|------|---------------------------|
| AA | ≥ 4.5:1 | ≥ 3:1 |
| AAA | ≥ 7:1 | ≥ 4.5:1 |

### Apple 特有要求

```
✅ 支持 Dynamic Type（iOS）— 用户可全局调整字体大小
✅ 支持 VoiceOver — 所有可交互元素有 aria-label
✅ 支持 Reduce Motion — 简化动画
✅ 支持 Increase Contrast — 提高边框/文字对比度
✅ 支持键盘导航（macOS）— Tab 遍历所有控件
```

### Focus Ring

```css
/* macOS 标准 Focus Ring */
outline: none;
box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.3);

/* 或用 Tailwind */
ring-[var(--color-primary)]/30  /* 不带 ring-offset */
```

所有可聚焦控件统一此规则。

---

## 10. macOS vs iOS 差异速查

| 差异点 | macOS | iOS |
|--------|-------|-----|
| 正文字号 | 13px | 17px |
| 最小交互目标 | 24px | 44px |
| 导航模式 | Sidebar + Tab | Tab Bar + Navigation Stack |
| 窗口管理 | 多窗口 | 单窗口全屏 |
| 输入方式 | 鼠标 + 键盘 | 手指触控 |
| Hover 状态 | 必须有 | 没有（无鼠标） |
| Right-click | 上下文菜单 | 长按菜单 |
| 滚动条 | 自动隐藏 / 始终显示 | 始终自动隐藏 |
| 标题栏 | 红黄绿三按钮（左上角） | 无 |
| 通知 | 右上角通知中心 | 顶部横幅 |

### 跨平台设计策略

```
如果是 Electron 桌面应用：
  → macOS: 追求 native 感，使用 Segmented Control、Sidebar
  → Windows: 可以偏 Fluent，也可以保持统一（大多数 Electron 应用选后者）

如果是 React Native / Flutter：
  → 每个平台用对应的组件库（iOS: Cupertino / Android: Material）
  → 或用自定义设计语言统一（如 Notion、Figma 的做法）
```

---

## 11. HIG 审计 Checklist

### 设计审计五维度

**D1 — 容器层级与分组**
- [ ] 无框套框（Card 套 Card）
- [ ] 配置参数平铺，不过度包裹
- [ ] 列表 Header 用弱底纹分隔，非强边框

**D2 — 排版降噪**
- [ ] Section 标题用 `11px font-medium text-black/40`（macOS）
- [ ] 禁止 `uppercase tracking-wider font-bold`
- [ ] Card header 高度适当（macOS: ~40px）

**D3 — 控件选择**
- [ ] 2-5 选项切换用 Segmented Control
- [ ] 数值显示用纯文字 `font-mono text-black/50`
- [ ] 主按钮用 accent color，不用品牌色

**D4 — 交互反馈**
- [ ] 所有可交互元素有 hover 状态（macOS）
- [ ] Focus Ring 统一使用 accent color /30
- [ ] 动画时长 100-300ms，缓动用 ease-out

**D5 — 状态表达**
- [ ] 日志/状态用纯文字颜色区分（Apple System Colors）
- [ ] 时间戳 `text-black/20 text-[10px]`
- [ ] 空状态克制：浅灰图标 + 简短文字
- [ ] Loading 用 skeleton / spinner，不留空白

### 通用审计

- [ ] 所有文字对比度 ≥ 4.5:1
- [ ] 触控目标 ≥ 44pt（iOS）/ 24px（macOS）
- [ ] 支持 prefers-reduced-motion
- [ ] 支持 prefers-color-scheme（Dark Mode）
- [ ] 键盘可导航所有控件（macOS）

---

## 12. 快速参考卡片

### 色彩

```
主强调: #007AFF (Light) / #0A84FF (Dark)
成功:   #34C759 / #30D158
警告:   #FF9500 / #FF9F0A
错误:   #FF3B30 / #FF453A
```

### 字体

```
macOS 正文: 13px Regular
iOS 正文:   17px Regular
字体栈:     -apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui
```

### 间距

```
最小: 4px | 控件间: 8px | 区块间: 16px | 窗口边距: 20px
```

### 动画

```
微交互: 150ms ease-out
状态切换: 250ms ease-in-out
标准缓动: cubic-bezier(0.25, 0.1, 0.25, 1)
```

---

## 来源

Apple Human Interface Guidelines (developer.apple.com/design/human-interface-guidelines) + 生产级 macOS Electron 应用实战中的像素级校准经验。
