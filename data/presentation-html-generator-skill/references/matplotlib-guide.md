# Matplotlib 架构图生成完整指南

## 脚本架构设计

推荐结构：通用工具函数 + 每张图独立函数。

```python
#!/usr/bin/env python3
"""架构图生成脚本"""
import matplotlib
matplotlib.use('Agg')  # 无GUI后端，必须在 import plt 前
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

# ===== 全局配置 =====
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Heiti TC', 'STHeiti', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ===== 颜色方案 =====
C = {
    'input':   ('#E3F2FD', '#1976D2'),
    'encoder': ('#FFF3E0', '#F57C00'),
    'preflow': ('#E8F5E9', '#388E3C'),
    'decoder': ('#E3F2FD', '#1565C0'),
    'vocoder': ('#F3E5F5', '#7B1FA2'),
    'output':  ('#FFEBEE', '#C62828'),
    'bg': '#FAFAFA',
    'accent': '#1976D2',
}

def box(ax, cx, cy, w, h, text, color_key='input', fs=10, bold=True, lw=2, pad_ratio=0.15):
    """圆角矩形 + 居中多行文字"""
    ...

def arrow(ax, x1, y1, x2, y2):
    """箭头连线"""
    ...

def setup_ax(fig, ax, W, H):
    """初始化坐标系"""
    ...

def gen_overview(): ...
def gen_module_detail(): ...

if __name__ == '__main__':
    gen_overview()
    gen_module_detail()
```

## 坐标系统设计

```python
def setup_ax(fig, ax, W, H):
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.invert_yaxis()  # y=0 在顶部
    ax.axis('off')
    fig.patch.set_facecolor('#FAFAFA')
```

关键规则：

| 原则 | 说明 |
|------|------|
| `figsize` 与坐标范围 1:100 | `figsize=(16, 7)` 对应 `(0, 1600) x (0, 700)` |
| **禁用** `set_aspect('equal')` | 导致变形和留白 |
| `invert_yaxis()` | y=0 在顶部，从上到下布局 |
| 方块以 `(cx, cy)` 中心定位 | 比左上角更直观 |

## 通用方块函数

```python
def box(ax, cx, cy, w, h, text, color_key='input', fs=10, bold=True, lw=2, pad_ratio=0.15):
    fc, ec = C[color_key] if isinstance(color_key, str) else color_key
    pad_val = min(w, h) * pad_ratio  # 按短边比例计算 pad
    rect = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle=f"round,pad={pad_val:.1f}",
        facecolor=fc, edgecolor=ec, linewidth=lw, alpha=0.92, zorder=2
    )
    ax.add_patch(rect)

    lines = text.split('\n')
    n_lines = len(lines)
    lh = h * 0.75 / max(n_lines, 1)  # 行高基于方块高度
    for i, line in enumerate(lines):
        offset = (i - (n_lines-1)/2) * lh
        ax.text(cx, cy + offset, line, ha='center', va='center',
                fontsize=fs, fontweight='bold' if (bold and i == 0) else 'normal',
                color='#212121', zorder=3)
```

## 常见组件绘制

### 垂直流程图
```python
nodes = [
    ('输入', 'input', 100),
    ('处理', 'encoder', 200),
    ('输出', 'output', 300),
]
for text, ck, y in nodes:
    box(ax, cx, y, bw, bh, text, ck)
for i in range(len(nodes) - 1):
    arrow(ax, cx, nodes[i][2] + bh/2 + 5, cx, nodes[i+1][2] - bh/2 - 5)
```

### 残差连接（折线法）
```python
res_x = cx - bw/2 - 40
ax.plot([cx - bw/2, res_x], [y_start, y_start], color='red', lw=2, linestyle='--')
ax.plot([res_x, res_x], [y_start, y_end], color='red', lw=2, linestyle='--')
ax.annotate('', xy=(cx - bw/2, y_end), xytext=(res_x, y_end),
            arrowprops=dict(arrowstyle='->', color='red', lw=2))
```

### 右侧维度标注
```python
ax.text(cx + bw/2 + 20, y, '(B, T, 512)', ha='left', va='center',
        fontsize=8.5, color='#888', style='italic')
```

### 半透明高亮区域
```python
highlight = FancyBboxPatch(
    (x, y), w, h,
    boxstyle='round,pad=5', facecolor='#FFF3E0', edgecolor='#F57C00',
    linewidth=1.5, alpha=0.15, linestyle='--', zorder=0
)
ax.add_patch(highlight)
```

## macOS 中文字体

```python
# ✅ 推荐（macOS 预装）
plt.rcParams['font.family'] = ['Arial Unicode MS', 'Heiti TC', 'STHeiti', 'sans-serif']

# ❌ 不可用：'PingFang SC'（matplotlib 不识别）, 'SimHei'（macOS 不预装）
```

验证可用字体：
```python
import matplotlib.font_manager as fm
for f in fm.findSystemFonts():
    if 'Heiti' in f or 'Arial' in f or 'STHeiti' in f:
        print(f)
```

## Emoji 处理

matplotlib 不支持 emoji。用 `[输入层]` 替代 `📥 输入层`。

批量删除：
```bash
sed -i '' "s/📥 //g;s/🔧 //g;s/🎵 //g" generate_diagrams.py
```

## 避坑清单

| 问题 | 根因 | 解决 |
|------|------|------|
| 方块严重膨胀 | `FancyBboxPatch` 的 `pad` 是数据坐标单位 | `min(w,h) * 0.15` |
| 文字挤成一团 | 行高用 `fontsize * 1.6` 估算 | `h * 0.75 / n_lines` |
| 弧线飞出画面 | `arc3,rad=-0.25` 跨度过大 | 三段折线代替弧线 |
| 注释框巨大 | `bbox(pad=6)` 在大坐标系中 | `pad=0.5` |
| 整体变形 | `set_aspect('equal')` | 删掉，用 figsize |
| 中文不显示 | 字体不存在 | `Arial Unicode MS` / `Heiti TC` |
| Emoji 缺失 | matplotlib 不支持 | 用纯文字标签 |

## 调试流程

```bash
# 只生成单张图
python3 -c "from generate_diagrams import gen_convnext; gen_convnext()"

# 检查图片尺寸
python3 -c "from PIL import Image; img=Image.open('output.jpg'); print(img.size)"

# 全部重新生成
python3 generate_diagrams.py
```
