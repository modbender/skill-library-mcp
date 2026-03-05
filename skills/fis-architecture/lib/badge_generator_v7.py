#!/usr/bin/env python3
"""
FIS 3.1 工卡生成器 v7.0 - 优化版

改进内容：
- 动态获取工作区路径，避免硬编码
- 增加高度，预留更多文本空间
- 输出要求分行显示，包含具体任务要求
- 缩减宽度，优化布局
- 右侧添加倾斜像素工牌装饰
- 动态获取 OpenClaw 版本号
- 修复中文显示支持

Author: CyberMao
Version: 3.1.4
"""

from PIL import Image, ImageDraw, ImageFont
import random
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
# qrcode module optional - fallback to placeholder if not available
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

class BadgeGenerator:
    """FIS 3.1 SubAgent Badge Generator - Optimized Layout"""
    
    # 优化后的尺寸
    WIDTH = 900          # 缩减宽度 (原1200)
    HEIGHT = 520         # 原始高度
    
    # 配色方案
    COLORS = {
        'primary': '#ff4d00',      # Orange
        'background': '#f5f5f0',   # Off-white paper
        'border': '#1a1a1a',       # Black
        'text': '#1a1a1a',         # Black text
        'secondary': '#666666',    # Gray
        'muted': '#999999',        # Light gray
        'divider': '#dddddd',      # Divider line
        'paper_line': '#e8e8e3',   # Paper texture
        'active': '#00c853',       # Green active
        'translucent': (26, 26, 26, 128),  # 半透明黑色
    }
    
    def __init__(self, output_dir=None):
        self.width = self.WIDTH
        self.height = self.HEIGHT
        
        # 动态获取输出目录 - 优先使用环境变量或标准路径
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            # 尝试多个可能的路径
            possible_paths = [
                Path(os.environ.get('OPENCLAW_WORKSPACE', '')) / 'output' / 'badges',
                Path.home() / '.openclaw' / 'output' / 'badges',
                Path.home() / '.openclaw' / 'workspace' / 'output' / 'badges',
                Path.cwd() / 'output' / 'badges',
            ]
            
            for path in possible_paths:
                if path.parent.exists():
                    self.output_dir = path
                    break
            else:
                # 回退到当前目录
                self.output_dir = Path.cwd() / 'badges'
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载字体 - 支持中文
        self.fonts = self._load_fonts()
        
        # 获取 OpenClaw 版本
        self.openclaw_version = self._get_openclaw_version()
    
    def _get_openclaw_version(self):
        """动态获取 OpenClaw 版本号 - 格式: vYYYY.MM.DD"""
        try:
            result = subprocess.run(
                ['openclaw', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # 提取版本号 - 处理 "openclaw version 2026.2.17" 或 "2026.2.17" 格式
                import re
                match = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', version_str)
                if match:
                    year, month, day = match.groups()
                    return f"v{year}.{month.zfill(1)}.{day.zfill(1)}"  # 保持原始数字，不添加前导零
                return version_str
        except Exception as e:
            pass
        
        # 回退到默认版本
        return 'v2026.2.17'
    
    def _load_fonts(self):
        """加载支持中文的字体 - 修复 .ttc 文件索引问题"""
        # 中文字体配置: (路径, index) - 对于 .ttc 文件需要正确的索引
        # uming.ttc: index 0 = AR PL UMing (Latin), index 1 = AR PL UMing TW (中文)
        # wqy-zenhei.ttc: index 0 = 文泉驿正黑 (中文), index 1 = 文泉驿等宽正黑
        chinese_font_configs = [
            ("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 0),  # 优先使用文泉驿，index 0 是中文
            ("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc", 0),
            ("/usr/share/fonts/truetype/arphic/uming.ttc", 1),    # index 1 是中文 (TW)
            ("/usr/share/fonts/truetype/arphic/ukai.ttc", 1),     # index 1 是中文 (TW)
            ("/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf", None),
            ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", None),
        ]
        
        # 等宽英文字体
        mono_font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        ]
        
        fonts = {}
        default_font = ImageFont.load_default()
        
        # 尝试加载中文字体
        chinese_font = None
        chinese_font_index = None
        
        for path, index in chinese_font_configs:
            if os.path.exists(path):
                try:
                    # 测试字体是否可用 - ttc文件需要指定index
                    if index is not None:
                        test_font = ImageFont.truetype(path, 12, index=index)
                    else:
                        test_font = ImageFont.truetype(path, 12)
                    
                    # 测试是否能渲染中文
                    test_text = "中文测试"
                    bbox = test_font.getbbox(test_text)
                    if bbox and bbox[2] > bbox[0]:  # 宽度大于0说明能渲染
                        chinese_font = path
                        chinese_font_index = index
                        print(f"  Loaded Chinese font: {path} (index={index})")
                        break
                except Exception as e:
                    print(f"  Failed to load {path} (index={index}): {e}")
                    continue
        
        if not chinese_font:
            print("  Warning: No Chinese font found, using default")
        
        # 尝试加载等宽字体
        mono_font = None
        for path in mono_font_paths:
            if os.path.exists(path):
                try:
                    mono_font = path
                    break
                except:
                    continue
        
        # 创建字体变体
        try:
            if chinese_font:
                # 为 ttc 文件传递 index 参数
                font_kwargs = {'index': chinese_font_index} if chinese_font_index is not None else {}
                fonts['title'] = ImageFont.truetype(chinese_font, 20, **font_kwargs)
                fonts['header'] = ImageFont.truetype(chinese_font, 15, **font_kwargs)
                fonts['text'] = ImageFont.truetype(chinese_font, 13, **font_kwargs)
                fonts['small'] = ImageFont.truetype(chinese_font, 11, **font_kwargs)
            else:
                fonts['title'] = ImageFont.truetype(mono_font, 20) if mono_font else default_font
                fonts['header'] = ImageFont.truetype(mono_font, 15) if mono_font else default_font
                fonts['text'] = ImageFont.truetype(mono_font, 13) if mono_font else default_font
                fonts['small'] = ImageFont.truetype(mono_font, 11) if mono_font else default_font
            
            fonts['pixel'] = ImageFont.truetype(mono_font, 9) if mono_font else default_font
        except Exception as e:
            print(f"  Font loading error: {e}")
            fonts = {k: default_font for k in ['title', 'header', 'text', 'small', 'pixel']}
        
        return fonts
    
    def create_badge(self, agent_data, output_path=None):
        """Create optimized badge layout"""
        # 创建画布
        card = Image.new('RGB', (self.width, self.height), self.COLORS['background'])
        draw = ImageDraw.Draw(card)
        
        # 添加纸质纹理
        self._add_paper_texture(draw)
        
        # 添加边框
        self._add_border(draw)
        
        # 添加头部
        self._add_header(draw, agent_data)
        
        # 添加左侧区域（头像 + 身份信息）
        self._add_left_section(draw, agent_data)
        
        # 添加右侧区域（职责 + 详细任务要求）
        self._add_right_section(draw, agent_data)
        
        # 添加右侧垂直状态条装饰
        self._add_tilted_pixel_badge(draw, agent_data)
        
        # 添加底部（并粘贴QR码）
        self._add_footer(draw, agent_data, card)
        
        # 保存
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            agent_id = agent_data.get('id', 'UNKNOWN').replace('/', '-')
            output_path = self.output_dir / f"badge_v7_{agent_id}_{timestamp}.png"
        
        card.save(output_path)
        return str(output_path)
    
    def _add_paper_texture(self, draw):
        """添加纸质纹理线条"""
        for y in range(0, self.height, 2):
            if y % 4 == 0:
                draw.line([(0, y), (self.width, y)], fill=self.COLORS['paper_line'], width=1)
    
    def _add_border(self, draw):
        """添加黑色边框"""
        draw.rectangle([3, 12, self.width - 3, self.height - 12], 
                      outline=self.COLORS['border'], width=3)
    
    def _add_header(self, draw, agent_data):
        """添加头部区域"""
        header_y = 30
        
        # Logo 和标题
        draw.text((30, header_y), "⚡", fill=self.COLORS['primary'], font=self.fonts['title'])
        draw.text((60, header_y), f"OPENCLAW {self.openclaw_version}", 
                 fill=self.COLORS['border'], font=self.fonts['header'])
        draw.text((60, header_y + 18), "FEDERAL INTELLIGENCE SYSTEM", 
                 fill=self.COLORS['secondary'], font=self.fonts['small'])
        
        # 右侧任务ID
        task_id = agent_data.get('task_id', '#UNKNOWN')
        # 计算文本宽度以便右对齐
        draw.text((self.width - 120, header_y), task_id, 
                 fill=self.COLORS['primary'], font=self.fonts['title'])
        
        # 虚线分隔线
        for x in range(30, self.width - 30, 8):
            draw.line([(x, header_y + 45), (x + 4, header_y + 45)], fill='#333333', width=1)
    
    def _add_left_section(self, draw, agent_data):
        """添加左侧区域"""
        left_x = 40
        avatar_y = 90
        
        # 头像框架（橙色方框）
        draw.rectangle([left_x - 2, avatar_y - 2, left_x + 72, avatar_y + 72],
                      outline=self.COLORS['primary'], width=4)
        
        # 随机小动物像素头像（每次生成随机，不绑定工号）
        self._draw_animal_avatar(draw, left_x, avatar_y)
        
        # 角色标签（固定宽度）
        role = agent_data.get('role', 'AGENT').upper()
        badge_y = avatar_y + 85
        badge_width = 100
        draw.rectangle([left_x, badge_y, left_x + badge_width, badge_y + 22],
                      fill=self.COLORS['border'], outline=self.COLORS['primary'], width=2)
        
        # 居中文字
        bbox = draw.textbbox((0, 0), role, font=self.fonts['pixel'])
        text_width = bbox[2] - bbox[0]
        text_x = left_x + (badge_width - text_width) // 2
        draw.text((text_x, badge_y + 5), role, fill='#ffffff', font=self.fonts['pixel'])
        
        # Agent 元数据
        draw.text((left_x, badge_y + 35), "AGENT NAME", fill=self.COLORS['muted'], font=self.fonts['small'])
        name = agent_data.get('name', 'Unknown Agent')
        draw.text((left_x, badge_y + 50), name[:18], fill=self.COLORS['border'], font=self.fonts['header'])
        
        agent_id = agent_data.get('id', 'UNKNOWN')
        draw.text((left_x, badge_y + 72), f"ID: {agent_id}", fill=self.COLORS['secondary'], font=self.fonts['small'])
        
        # FIS INFO 信息框（移到左侧下方）
        info_y = badge_y + 100
        info_width = 140
        info_height = 145  # 增加高度以容纳字体
        
        # 信息框背景
        draw.rectangle([left_x, info_y, left_x + info_width, info_y + info_height],
                      fill='#f8f8f5', outline=self.COLORS['divider'], width=1)
        
        # 信息框标题
        draw.rectangle([left_x, info_y, left_x + info_width, info_y + 22],
                      fill=self.COLORS['border'])
        draw.text((left_x + 6, info_y + 5), "FIS INFO", fill='#ffffff', font=self.fonts['pixel'])
        
        # 信息内容 - 增加行间距
        draw.text((left_x + 6, info_y + 30), "Version:", fill=self.COLORS['secondary'], font=self.fonts['small'])
        draw.text((left_x + 6, info_y + 48), "3.1 Lite", fill=self.COLORS['border'], font=self.fonts['text'])
        
        draw.text((left_x + 6, info_y + 72), "Security:", fill=self.COLORS['secondary'], font=self.fonts['small'])
        draw.text((left_x + 6, info_y + 90), "Level 1", fill='#00c853', font=self.fonts['text'])
        
        draw.text((left_x + 6, info_y + 114), "Workspace:", fill=self.COLORS['secondary'], font=self.fonts['small'])
        ws_text = agent_data.get('id', 'N/A')[:10]
        draw.text((left_x + 6, info_y + 132), ws_text, fill=self.COLORS['border'], font=self.fonts['small'])
    
    def _draw_animal_avatar(self, draw, left_x, avatar_y):
        """绘制随机小动物像素头像（完全随机，每次不同）"""
        # 完全随机，不绑定工号
        random.seed()
        
        # 随机选择动物类型
        animals = ['cat', 'dog', 'rabbit', 'bear', 'fox', 'panda', 'owl']
        animal = random.choice(animals)
        
        # 颜色配置
        fur_colors = {
            'cat': ['#ff8c42', '#4a4a4a', '#ffffff', '#d4a574', '#1a1a1a', '#ff6b6b', '#ffd700'],
            'dog': ['#d4a574', '#8b4513', '#f5d0b0', '#4a4a4a', '#ffffff', '#e8c4a0'],
            'rabbit': ['#ffffff', '#f5d0b0', '#d4a574', '#ff9999', '#ffb6c1'],
            'bear': ['#8b4513', '#d4a574', '#4a4a4a', '#ffffff', '#a0522d'],
            'fox': ['#ff8c42', '#ff6b00', '#4a4a4a', '#ffffff', '#ffa500'],
            'panda': ['#ffffff'],
            'owl': ['#8b4513', '#4a4a4a', '#d4a574', '#ff8c42', '#654321'],
        }
        
        bg_colors = ['#e8f4f8', '#fff3e0', '#f3e5f5', '#e8f5e9', '#ffebee', '#e0f7fa', '#fff8e1', '#fce4ec']
        
        # 增加像素密度，让头像更精细
        center_x = left_x + 35
        center_y = avatar_y + 35
        pixel_size = 4  # 从6减小到4，增加像素密度
        
        fur_color = random.choice(fur_colors[animal])
        bg_color = random.choice(bg_colors)
        
        # 绘制方形背景
        for y in range(avatar_y + 2, avatar_y + 68, pixel_size):
            for x in range(left_x + 2, left_x + 68, pixel_size):
                draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=bg_color)
        
        # 根据动物类型绘制
        if animal == 'cat':
            self._draw_cat(draw, center_x, center_y, pixel_size, fur_color)
        elif animal == 'dog':
            self._draw_dog(draw, center_x, center_y, pixel_size, fur_color)
        elif animal == 'rabbit':
            self._draw_rabbit(draw, center_x, center_y, pixel_size, fur_color)
        elif animal == 'bear':
            self._draw_bear(draw, center_x, center_y, pixel_size, fur_color)
        elif animal == 'fox':
            self._draw_fox(draw, center_x, center_y, pixel_size, fur_color)
        elif animal == 'panda':
            self._draw_panda(draw, center_x, center_y, pixel_size, fur_color)
        elif animal == 'owl':
            self._draw_owl(draw, center_x, center_y, pixel_size, fur_color)
        
        random.seed()
    
    def _draw_cat(self, draw, cx, cy, ps, color):
        """绘制像素猫（高密度）"""
        # 耳朵（三角形）
        draw.rectangle([cx - 16, cy - 24, cx - 4, cy - 8], fill=color)
        draw.rectangle([cx + 4, cy - 24, cx + 16, cy - 8], fill=color)
        draw.rectangle([cx - 12, cy - 20, cx - 6, cy - 12], fill='#ffb6c1')  # 内耳
        draw.rectangle([cx + 6, cy - 20, cx + 12, cy - 12], fill='#ffb6c1')
        
        # 脸（更圆润）
        for y in range(cy - 14, cy + 16, ps):
            for x in range(cx - 20, cx + 20, ps):
                if abs(x - cx) < 18 and abs(y - cy) < 14:
                    draw.rectangle([x, y, x + ps, y + ps], fill=color)
        
        # 大眼睛（可爱风格）
        eye_color = random.choice(['#228b22', '#4169e1', '#ffd700', '#9370db'])
        draw.rectangle([cx - 14, cy - 6, cx - 4, cy + 6], fill=eye_color)
        draw.rectangle([cx + 4, cy - 6, cx + 14, cy + 6], fill=eye_color)
        draw.rectangle([cx - 12, cy - 4, cx - 6, cy + 2], fill='#000000')  # 瞳孔
        draw.rectangle([cx + 6, cy - 4, cx + 12, cy + 2], fill='#000000')
        draw.rectangle([cx - 10, cy - 2, cx - 8, cy], fill='#ffffff')  # 高光
        draw.rectangle([cx + 8, cy - 2, cx + 10, cy], fill='#ffffff')
        
        # 小鼻子
        draw.rectangle([cx - 3, cy + 6, cx + 3, cy + 10], fill='#ffb6c1')
        
        # 小嘴巴
        draw.rectangle([cx - 6, cy + 10, cx, cy + 12], fill='#333333')
        draw.rectangle([cx, cy + 10, cx + 6, cy + 12], fill='#333333')
    
    def _draw_dog(self, draw, cx, cy, ps, color):
        """绘制像素狗（高密度）"""
        # 耷拉耳朵（更大更可爱）
        draw.rectangle([cx - 22, cy - 14, cx - 6, cy + 10], fill=color)
        draw.rectangle([cx + 6, cy - 14, cx + 22, cy + 10], fill=color)
        draw.rectangle([cx - 18, cy - 8, cx - 10, cy + 4], fill='#d4a574')  # 内耳阴影
        draw.rectangle([cx + 10, cy - 8, cx + 18, cy + 4], fill='#d4a574')
        
        # 脸（更圆润）
        for y in range(cy - 12, cy + 18, ps):
            for x in range(cx - 18, cx + 18, ps):
                if abs(x - cx) < 16 and abs(y - cy) < 12:
                    draw.rectangle([x, y, x + ps, y + ps], fill=color)
        
        # 大眼睛（可爱风格）
        draw.rectangle([cx - 12, cy - 4, cx - 4, cy + 6], fill='#000000')
        draw.rectangle([cx + 4, cy - 4, cx + 12, cy + 6], fill='#000000')
        draw.rectangle([cx - 10, cy - 2, cx - 6, cy + 2], fill='#ffffff')  # 高光
        draw.rectangle([cx + 6, cy - 2, cx + 10, cy + 2], fill='#ffffff')
        
        # 大鼻子
        draw.rectangle([cx - 5, cy + 6, cx + 5, cy + 12], fill='#333333')
        
        # 吐舌头（随机）
        if random.random() > 0.5:
            draw.rectangle([cx - 4, cy + 12, cx + 4, cy + 20], fill='#ff6b6b')
            draw.rectangle([cx - 2, cy + 16, cx + 2, cy + 22], fill='#ff4757')
    
    def _draw_rabbit(self, draw, cx, cy, ps, color):
        """绘制像素兔子（高密度）"""
        # 长耳朵（更可爱）
        draw.rectangle([cx - 16, cy - 36, cx - 4, cy - 10], fill=color)
        draw.rectangle([cx + 4, cy - 36, cx + 16, cy - 10], fill=color)
        draw.rectangle([cx - 12, cy - 32, cx - 6, cy - 16], fill='#ffb6c1')  # 内耳
        draw.rectangle([cx + 6, cy - 32, cx + 12, cy - 16], fill='#ffb6c1')
        
        # 圆脸（更圆润）
        for y in range(cy - 12, cy + 16, ps):
            for x in range(cx - 16, cx + 16, ps):
                if abs(x - cx) < 14 and abs(y - cy) < 12:
                    draw.rectangle([x, y, x + ps, y + ps], fill=color)
        
        # 超大眼睛（可爱风格）
        draw.rectangle([cx - 12, cy - 4, cx - 2, cy + 8], fill='#000000')
        draw.rectangle([cx + 2, cy - 4, cx + 12, cy + 8], fill='#000000')
        draw.rectangle([cx - 10, cy - 2, cx - 4, cy + 4], fill='#ffffff')  # 高光
        draw.rectangle([cx + 4, cy - 2, cx + 10, cy + 4], fill='#ffffff')
        
        # 小鼻子
        draw.rectangle([cx - 3, cy + 8, cx + 3, cy + 12], fill='#ffb6c1')
        
        # 大门牙（更明显）
        draw.rectangle([cx - 4, cy + 12, cx, cy + 18], fill='#ffffff')
        draw.rectangle([cx, cy + 12, cx + 4, cy + 18], fill='#ffffff')
        draw.rectangle([cx - 4, cy + 18, cx + 4, cy + 20], fill='#e0e0e0')  # 牙齿分隔线
    
    def _draw_bear(self, draw, cx, cy, ps, color):
        """绘制像素熊（高密度）"""
        # 圆耳朵（更大）
        draw.rectangle([cx - 18, cy - 16, cx - 6, cy - 6], fill=color)
        draw.rectangle([cx + 6, cy - 16, cx + 18, cy - 6], fill=color)
        draw.rectangle([cx - 14, cy - 14, cx - 8, cy - 8], fill='#d4a574')  # 内耳
        draw.rectangle([cx + 8, cy - 14, cx + 14, cy - 8], fill='#d4a574')
        
        # 大圆脸（更圆润）
        for y in range(cy - 12, cy + 20, ps):
            for x in range(cx - 20, cx + 20, ps):
                if abs(x - cx) < 18 and abs(y - cy) < 14:
                    draw.rectangle([x, y, x + ps, y + ps], fill=color)
        
        # 小眼睛（豆豆眼更可爱）
        draw.rectangle([cx - 10, cy - 4, cx - 4, cy + 2], fill='#000000')
        draw.rectangle([cx + 4, cy - 4, cx + 10, cy + 2], fill='#000000')
        
        # 大鼻子
        draw.rectangle([cx - 6, cy + 4, cx + 6, cy + 12], fill='#333333')
        draw.rectangle([cx - 2, cy + 12, cx + 2, cy + 16], fill='#333333')
        
        # 小嘴巴
        draw.rectangle([cx - 8, cy + 14, cx - 2, cy + 16], fill='#333333')
        draw.rectangle([cx + 2, cy + 14, cx + 8, cy + 16], fill='#333333')
    
    def _draw_fox(self, draw, cx, cy, ps, color):
        """绘制像素狐狸（高密度）"""
        # 尖耳朵（更大）
        draw.rectangle([cx - 18, cy - 24, cx - 6, cy - 8], fill=color)
        draw.rectangle([cx + 6, cy - 24, cx + 18, cy - 8], fill=color)
        draw.rectangle([cx - 16, cy - 22, cx - 10, cy - 14], fill='#ffffff')  # 白耳尖
        draw.rectangle([cx + 10, cy - 22, cx + 16, cy - 14], fill='#ffffff')
        draw.rectangle([cx - 14, cy - 18, cx - 10, cy - 12], fill='#333333')  # 黑耳尖
        draw.rectangle([cx + 10, cy - 18, cx + 14, cy - 12], fill='#333333')
        
        # 尖脸（更精细）
        for y in range(cy - 10, cy + 14, ps):
            for x in range(cx - 16, cx + 16, ps):
                width = 14 - (y - cy + 10) // 3
                if abs(x - cx) < width:
                    draw.rectangle([x, y, x + ps, y + ps], fill=color)
        
        # 眼睛（更大）
        draw.rectangle([cx - 12, cy - 4, cx - 4, cy + 6], fill='#000000')
        draw.rectangle([cx + 4, cy - 4, cx + 12, cy + 6], fill='#000000')
        
        # 尖鼻子
        draw.rectangle([cx - 3, cy + 8, cx + 3, cy + 14], fill='#333333')
    
    def _draw_panda(self, draw, cx, cy, ps, _):
        """绘制像素熊猫（高密度）"""
        # 黑眼圈（耳朵）
        draw.rectangle([cx - 20, cy - 16, cx - 6, cy - 4], fill='#000000')
        draw.rectangle([cx + 6, cy - 16, cx + 20, cy - 4], fill='#000000')
        
        # 白脸（更圆润）
        for y in range(cy - 12, cy + 16, ps):
            for x in range(cx - 18, cx + 18, ps):
                if abs(x - cx) < 16 and abs(y - cy) < 12:
                    draw.rectangle([x, y, x + ps, y + ps], fill='#ffffff')
        
        # 黑眼圈（眼睛周围，更大）
        draw.rectangle([cx - 14, cy - 8, cx - 2, cy + 6], fill='#000000')
        draw.rectangle([cx + 2, cy - 8, cx + 14, cy + 6], fill='#000000')
        
        # 眼睛（更大）
        draw.rectangle([cx - 10, cy - 4, cx - 4, cy + 4], fill='#ffffff')
        draw.rectangle([cx + 4, cy - 4, cx + 10, cy + 4], fill='#ffffff')
        draw.rectangle([cx - 8, cy - 2, cx - 6, cy + 2], fill='#000000')  # 瞳孔
        draw.rectangle([cx + 6, cy - 2, cx + 8, cy + 2], fill='#000000')
        
        # 黑鼻子
        draw.rectangle([cx - 4, cy + 6, cx + 4, cy + 12], fill='#000000')
        
        # 小嘴巴
        draw.rectangle([cx - 2, cy + 12, cx + 2, cy + 16], fill='#000000')
    
    def _draw_owl(self, draw, cx, cy, ps, color):
        """绘制像素猫头鹰（高密度）"""
        # 耳朵羽毛（更大）
        draw.rectangle([cx - 16, cy - 22, cx - 6, cy - 12], fill=color)
        draw.rectangle([cx + 6, cy - 22, cx + 16, cy - 12], fill=color)
        
        # 圆脸（更圆润）
        for y in range(cy - 14, cy + 16, ps):
            for x in range(cx - 18, cx + 18, ps):
                if abs(x - cx) < 16 and abs(y - cy) < 13:
                    draw.rectangle([x, y, x + ps, y + ps], fill=color)
        
        # 超大眼睛（眼圈）
        draw.rectangle([cx - 14, cy - 8, cx, cy + 8], fill='#ffffff')
        draw.rectangle([cx, cy - 8, cx + 14, cy + 8], fill='#ffffff')
        
        # 瞳孔（更大）
        eye_color = random.choice(['#ffd700', '#ffa500', '#ff6b00'])
        draw.rectangle([cx - 10, cy - 4, cx - 2, cy + 6], fill=eye_color)
        draw.rectangle([cx + 2, cy - 4, cx + 10, cy + 6], fill=eye_color)
        draw.rectangle([cx - 8, cy - 2, cx - 4, cy + 4], fill='#000000')
        draw.rectangle([cx + 4, cy - 2, cx + 8, cy + 4], fill='#000000')
        
        # 喙（更大）
        draw.rectangle([cx - 3, cy + 6, cx + 3, cy + 14], fill='#ff8c42')
    
    def _add_right_section(self, draw, agent_data):
        """添加右侧区域 - 包含详细任务要求"""
        right_x = 240  # 向右移动，增加右侧区域宽度
        section_y = 90
        
        # SOUL 标签（橙色）
        soul = agent_data.get('soul', '"Digital familiar navigating the void"')
        draw.rectangle([right_x, section_y, right_x + 70, section_y + 24],
                      fill=self.COLORS['primary'], outline=self.COLORS['border'], width=2)
        draw.text((right_x + 8, section_y + 5), "SOUL", fill='#ffffff', font=self.fonts['pixel'])
        draw.text((right_x + 82, section_y + 3), soul[:45], fill=self.COLORS['primary'], font=self.fonts['text'])
        
        # RESPONSIBILITIES 标签（黑色）
        resp_y = section_y + 42
        draw.rectangle([right_x, resp_y, right_x + 140, resp_y + 24],
                      fill=self.COLORS['border'], outline=self.COLORS['border'], width=2)
        draw.text((right_x + 8, resp_y + 5), "RESPONSIBILITIES", fill='#ffffff', font=self.fonts['pixel'])
        
        # 职责列表
        responsibilities = agent_data.get('responsibilities', [
            "Execute assigned tasks with precision",
            "Maintain communication with parent agent",
            "Report progress and blockers promptly",
        ])
        
        for i, bullet in enumerate(responsibilities[:3]):
            y = resp_y + 30 + (i * 20)
            text = bullet[:58]  # 增加可显示字符数
            draw.text((right_x + 8, y), f"▸ {text}", fill=self.COLORS['border'], font=self.fonts['small'])
        
        # 输出要求 - 格式标签
        out_y = resp_y + 100
        draw.rectangle([right_x, out_y, right_x + 100, out_y + 24],
                      fill='#666666', outline=self.COLORS['border'], width=2)
        draw.text((right_x + 8, out_y + 5), "OUTPUT REQ", fill='#ffffff', font=self.fonts['pixel'])
        
        output_formats = agent_data.get('output_formats', 'MARKDOWN | JSON | TXT')
        draw.text((right_x + 108, out_y + 5), output_formats, 
                 fill=self.COLORS['border'], font=self.fonts['small'])
        
        # 输出要求 - 具体任务要求
        task_req_y = out_y + 32
        task_requirements = agent_data.get('task_requirements', [
            "1. Analyze code structure and dependencies",
            "2. Provide detailed line count statistics",
            "3. Report top 5 largest files",
        ])
        
        draw.text((right_x, task_req_y), "任务要求:", 
                 fill=self.COLORS['primary'], font=self.fonts['small'])
        
        for i, req in enumerate(task_requirements[:3]):
            y = task_req_y + 20 + (i * 18)
            text = req[:55]  # 增加可显示字符数
            draw.text((right_x + 8, y), f"• {text}", fill=self.COLORS['secondary'], font=self.fonts['small'])
        
        # 垂直分隔线（左侧）
        draw.line([(210, 80), (210, self.height - 80)], fill=self.COLORS['divider'], width=2)
    
    def _add_tilted_pixel_badge(self, draw, agent_data):
        """右侧装饰区域 - 已移除"""
        pass
    
    def _generate_qr_code(self, url="https://github.com/MuseLinn/fis-architecture", size=50):
        """生成QR码（如果qrcode模块不可用则绘制类似QR码的图案）"""
        if HAS_QRCODE:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=3,
                border=1,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.convert('RGB')
            qr_img = qr_img.resize((size, size), Image.Resampling.NEAREST)
            return qr_img
        
        # 没有 qrcode 模块时，绘制类似 QR 码的像素图案
        qr_img = Image.new('RGB', (size, size), 'white')
        draw = ImageDraw.Draw(qr_img)
        
        # 绘制三个定位角（类似QR码的结构）
        box_size = size // 7
        
        # 左上角定位图案
        draw.rectangle([0, 0, box_size*3, box_size*3], fill='black', outline='white', width=2)
        draw.rectangle([box_size, box_size, box_size*2, box_size*2], fill='white')
        draw.rectangle([box_size+3, box_size+3, box_size*2-3, box_size*2-3], fill='black')
        
        # 右上角定位图案
        draw.rectangle([size-box_size*3, 0, size, box_size*3], fill='black', outline='white', width=2)
        draw.rectangle([size-box_size*2, box_size, size-box_size, box_size*2], fill='white')
        draw.rectangle([size-box_size*2+3, box_size+3, size-box_size-3, box_size*2-3], fill='black')
        
        # 左下角定位图案
        draw.rectangle([0, size-box_size*3, box_size*3, size], fill='black', outline='white', width=2)
        draw.rectangle([box_size, size-box_size*2, box_size*2, size-box_size], fill='white')
        draw.rectangle([box_size+3, size-box_size*2+3, box_size*2-3, size-box_size-3], fill='black')
        
        # 中间随机填充一些像素
        import random
        random.seed(url)
        for y in range(box_size*3, size-box_size*3, 4):
            for x in range(box_size*3, size, 4):
                if random.random() > 0.5:
                    draw.rectangle([x, y, x+3, y+3], fill='black')
        
        return qr_img
    def _add_footer(self, draw, agent_data, card_img):
        """添加底部区域"""
        footer_y = self.height - 65
        
        # 黑色背景底栏
        draw.rectangle([3, footer_y, self.width - 3, self.height - 12],
                      fill=self.COLORS['border'])
        
        # 条形码
        bar_x = 30
        bar_width = 2
        bar_spacing = 2
        for i in range(35):
            draw.rectangle([bar_x, footer_y + 8, bar_x + bar_width, footer_y + 30], fill='#ffffff')
            bar_x += bar_width + bar_spacing
        
        # 条形码ID
        barcode_id = agent_data.get('barcode_id', f"OC-2025-{agent_data.get('role', 'AGENT')[:4].upper()}-001")
        draw.text((30, footer_y + 35), barcode_id, fill='#666666', font=self.fonts['small'])
        
        # 状态指示器
        status = agent_data.get('status', 'PENDING')
        status_color = self.COLORS['active'] if status == 'ACTIVE' else '#ff4d00'
        status_x = 280
        draw.ellipse([status_x, footer_y + 12, status_x + 12, footer_y + 24], 
                    fill=status_color, outline='#ffffff', width=1)
        draw.text((status_x + 18, footer_y + 12), status, fill='#ffffff', font=self.fonts['pixel'])
        
        # 有效期
        valid_until = agent_data.get('valid_until', 
                                     (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'))
        draw.text((self.width - 200, footer_y + 12), f"VALID UNTIL: {valid_until}", 
                 fill='#666666', font=self.fonts['small'])
        
        # 右下角QR码（GitHub Repo链接）
        qr_x, qr_y = self.width - 60, footer_y + 8
        try:
            qr_img = self._generate_qr_code("https://github.com/MuseLinn/fis-architecture", size=45)
            # 粘贴QR码到底部区域
            card_img.paste(qr_img, (qr_x, qr_y))
        except Exception as e:
            # 备用：绘制简单的像素图案
            for i in range(5):
                for j in range(5):
                    if (i + j) % 2 == 0:
                        draw.rectangle([qr_x + i * 8, qr_y + j * 8, qr_x + i * 8 + 6, qr_y + j * 8 + 6], 
                                      fill='#ffffff')


def generate_badge_with_task(agent_name, role, task_desc, task_requirements, output_dir=None):
    """
    便捷函数：生成带详细任务要求的工卡
    
    Args:
        agent_name: 子代理名称
        role: 角色 (WORKER/RESEARCHER/REVIEWER/FORMATTER)
        task_desc: 任务描述
        task_requirements: 任务输出要求列表
        output_dir: 输出目录
    """
    generator = BadgeGenerator(output_dir)
    
    # 生成唯一ID
    timestamp = datetime.now()
    agent_id = f"CYBERMAO-SA-{timestamp.year}-{timestamp.strftime('%m%d%H%M')}"
    
    agent_data = {
        'name': agent_name,
        'id': agent_id,
        'role': role,
        'task_id': f"#{role[:4].upper()}-{timestamp.strftime('%m%d')}",
        'soul': f'"{task_desc[:30]}..."' if len(task_desc) > 30 else f'"{task_desc}"',
        'responsibilities': [
            "Execute task with precision and quality",
            "Report progress within deadline",
            "Follow FIS 3.1 protocol standards",
        ],
        'output_formats': 'MARKDOWN | JSON | TXT',
        'task_requirements': task_requirements,
        'barcode_id': f"OC-{timestamp.year}-{role[:4].upper()}-{timestamp.strftime('%m%d')}",
        'status': 'PENDING',
    }
    
    return generator.create_badge(agent_data)


def generate_multi_badge(cards_data, output_name=None):
    """
    生成多工牌拼接图 (2x2 网格或垂直排列)
    
    Args:
        cards_data: [{'agent_name': 'Worker-1', 'role': 'worker', 'task_desc': '...', 'task_requirements': [...]}, ...]
        output_name: 输出文件名
    
    Returns:
        拼接后的图片路径
    """
    from PIL import Image
    
    generator = BadgeGenerator()
    
    # 生成单个工牌
    badge_images = []
    for card in cards_data:
        agent_data = {
            'name': card['agent_name'],
            'id': f"CYBERMAO-SA-{datetime.now().year}-{datetime.now().strftime('%m%d%H%M')}",
            'role': card['role'],
            'task_id': f"#{card['role'][:4].upper()}-{datetime.now().strftime('%m%d')}",
            'soul': f'"{card["task_desc"][:30]}..."' if len(card["task_desc"]) > 30 else f'"{card["task_desc"]}"',
            'responsibilities': [
                "Execute task with precision and quality",
                "Report progress within deadline",
                "Follow FIS 3.1 protocol standards",
            ],
            'output_formats': 'MARKDOWN | JSON | TXT',
            'task_requirements': card.get('task_requirements', ['Report.md']),
            'barcode_id': f"OC-{datetime.now().year}-{card['role'][:4].upper()}-{datetime.now().strftime('%m%d')}",
            'status': 'PENDING',
        }
        badge_path = generator.create_badge(agent_data)
        badge_images.append(Image.open(badge_path))
    
    # 拼接图片
    n = len(badge_images)
    if n == 0:
        return None
    
    # 获取单张尺寸
    w, h = badge_images[0].size
    
    # 决定布局: 2x2 网格或垂直排列
    if n <= 2:
        # 垂直排列
        total_h = h * n
        collage = Image.new('RGB', (w, total_h), (245, 245, 240))
        for i, img in enumerate(badge_images):
            collage.paste(img, (0, i * h))
    elif n <= 4:
        # 2x2 网格
        cols = 2
        rows = (n + 1) // 2
        total_w = w * cols
        total_h = h * rows
        collage = Image.new('RGB', (total_w, total_h), (245, 245, 240))
        for i, img in enumerate(badge_images):
            row = i // cols
            col = i % cols
            collage.paste(img, (col * w, row * h))
    else:
        # 超过4张，垂直排列
        total_h = h * n
        collage = Image.new('RGB', (w, total_h), (245, 245, 240))
        for i, img in enumerate(badge_images):
            collage.paste(img, (0, i * h))
    
    # 保存
    output_dir = Path.home() / ".openclaw" / "output" / "badges"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if output_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"badge_multi_{timestamp}.png"
    
    output_path = output_dir / output_name
    collage.save(output_path, 'PNG', quality=95)
    print(f"✅ Multi-badge collage: {output_path}")
    
    return str(output_path)


if __name__ == "__main__":
    # 测试生成工卡
    print("=== FIS 3.1 Badge Generator v7.0 ===")
    
    # 示例：统计代码行数任务
    badge_path = generate_badge_with_task(
        agent_name="CodeStats-001",
        role="RESEARCHER",
        task_desc="统计 workspace 下所有 Python 文件的行数",
        task_requirements=[
            "1. Find all .py files recursively",
            "2. Count lines for each file",
            "3. Report top 5 largest files",
            "4. Calculate total line count",
        ]
    )
    
    print(f"✅ Badge generated: {badge_path}")
