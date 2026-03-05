# Reveal.js 常见问题修复指南

## Mermaid 图表在隐藏 Slide 中不渲染

### 问题
`startOnLoad: true` 只渲染当前可见 Slide 中的图表。隐藏 Slide 中的 Mermaid 切换过去时显示空白。

### 解决方案一：手动渲染所有图表（推荐）

```javascript
mermaid.initialize({
    startOnLoad: false,
    theme: 'neutral',
    flowchart: { useMaxWidth: true, htmlLabels: true }
});

async function renderAllMermaid() {
    const mermaidDivs = document.querySelectorAll('.mermaid');
    for (let i = 0; i < mermaidDivs.length; i++) {
        const el = mermaidDivs[i];
        if (el.getAttribute('data-processed')) continue;
        const graphDef = el.textContent.trim();
        if (!graphDef) continue;
        try {
            const { svg } = await mermaid.render('mermaid-svg-' + i, graphDef);
            el.innerHTML = svg;
            el.setAttribute('data-processed', 'true');
        } catch(e) {
            console.warn('Mermaid渲染失败:', e);
        }
    }
}

Reveal.on('ready', () => { renderAllMermaid(); });
Reveal.on('slidechanged', () => { renderAllMermaid(); });
```

### 解决方案二：纯 HTML/CSS 替代（最可靠）

关键架构图用纯 HTML + CSS 绘制，避免第三方库问题：

```html
<div style="display: flex; flex-direction: column; align-items: center; gap: 4px;">
    <div style="background: #e3f2fd; border: 2px solid #1976d2;
                border-radius: 8px; padding: 6px 18px; font-weight: 600;">
        输入: (B, T, 512)
    </div>
    <div style="font-size: 1.2em; color: #888;">↓</div>
    <div style="background: #f3e5f5; border: 2px solid #7b1fa2;
                border-radius: 8px; padding: 6px 18px;">
        处理步骤
    </div>
    <div style="font-size: 1.2em; color: #888;">↓</div>
    <div style="background: #e3f2fd; border: 2px solid #1976d2;
                border-radius: 8px; padding: 6px 18px; font-weight: 600;">
        输出: (B, T, 1024)
    </div>
</div>
```

**建议**：关键页面优先使用方案二，辅助性图表用方案一。

---

## 纵向流程图溢出修复

### 问题
纯 HTML/CSS 垂直流程图节点过多（8+）时，总高度超出 Slide 可视区域（960px），底部被截断。

### 解决方案：压缩纵向间距

| 属性 | 修改前 | 修改后 | 说明 |
|------|--------|--------|------|
| `gap` | `4px` | `0` | 消除 flex 间距 |
| `font-size` | `0.88em` | `0.72em` | 整体缩小 |
| `line-height` | 默认 | `1.2` | 压缩行高 |
| `padding` | `6px 18px` | `3px 14px` | 减小内边距 |
| `border-radius` | `8px` | `6px` | 配合缩小圆角 |
| 箭头 `margin` | 无 | `1px 0` | 极小 margin 替代 gap |

额外技巧：
- `<br><small>说明</small>` 改为同行 `<small>说明</small>`，节点从两行变一行
- 节点 10+ 时，拆分为两列或两页
- 标题 `margin-bottom` 缩小到 `5px`

---

## 居中与布局修复

### 问题
不同分辨率下内容偏移（偏右/偏左），部分内容被遮挡。

### 解决方案
使用 Flexbox 让每个 `section` 垂直+水平居中，限制最大宽度：

```css
.reveal .slides { text-align: center; }
.reveal .slides section {
    display: flex; flex-direction: column;
    justify-content: center; align-items: center;
    width: 100%; height: 100%;
    padding: 20px 40px; box-sizing: border-box;
}
.grid-2, .grid-3 { max-width: 1700px; width: 100%; }
.reveal .slides section > * { max-width: 100%; box-sizing: border-box; }
```

关键配置：
- `margin: 0.1`（比默认 0.04 更安全）
- `center: true`
- `max-width: 1700px`（1920px 画布中左右各留 110px）

---

## 内容溢出处理：滚动容器

```css
.scrollable-container {
    overflow-y: auto;
    max-height: 500px;
    padding: 10px;
    border: 1px solid #eee;
}
.mermaid {
    overflow: auto;
    max-height: 400px;
}
```

用法：包裹过长的代码块或整个 grid 列。

---

## 调试方法

浏览器控制台获取当前 Slide 实际尺寸：

```javascript
var slide = document.querySelector('.reveal .slides section.present');
if (slide) {
    var rect = slide.getBoundingClientRect();
    console.log('当前 Slide 实际尺寸:', rect.width, 'x', rect.height);
}
console.log('配置宽度:', Reveal.getConfig().width);
console.log('配置高度:', Reveal.getConfig().height);
console.log('当前缩放比例:', Reveal.getScale());
```

## 宽高比要求

**必须 2:1（宽:高）**：`width: 1920, height: 960`

原因：
- 大多数显示器 16:9 或 16:10，2:1 接近这些比例
- 默认 960×700（≈1.37:1）过于方正，全屏时上下大量黑边
- 2:1 给横向排版提供充足水平空间

配套 CSS：
```css
.reveal .slides section { font-size: 0.72em; padding: 18px 50px; }
.scrollable-container { max-height: 520px; }
```
