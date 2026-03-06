"""
WhatsApp Card Generator - Dark theme 1080x1080 PNG cards
Theme: "Midnight Ledger"
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Script-relative output directory
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", ".."))
DEFAULT_OUTPUT_DIR = os.path.join(_SKILL_ROOT, "output", "whatsapp_cards")


class WhatsAppCardGenerator:
    """Generates square cards optimized for WhatsApp display"""
    
    COLORS = {
        "background": "#0a0e1a",
        "card_bg": "#121828",
        "positive": "#cd7f32",
        "negative": "#c45c5c",
        "neutral": "#e8e8e8",
        "accent": "#d4af37",
        "text": "#e8e8e8",
        "text_dim": "#8892a8",
        "border": "#1e2844",
    }
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self._pil_available = self._check_pil()
    
    def _check_pil(self) -> bool:
        try:
            from PIL import Image, ImageDraw, ImageFont
            return True
        except ImportError:
            return False
    
    def generate_kpi_card(
        self,
        title: str,
        value: str,
        change: Optional[Dict[str, Any]] = None,
        subtitle: Optional[str] = None,
        sparkline_data: Optional[List[float]] = None,
        filename: Optional[str] = None
    ) -> str:
        """Generate a single KPI card (1080x1080)"""
        
        if not self._pil_available:
            return self._generate_text_card(title, value, filename)
        
        from PIL import Image, ImageDraw, ImageFont
        
        # Create canvas
        size = 1080
        img = Image.new('RGB', (size, size), self.COLORS["background"])
        draw = ImageDraw.Draw(img)
        
        # Card background with rounded corners effect
        card_margin = 40
        card_box = (card_margin, card_margin, size - card_margin, size - card_margin)
        draw.rounded_rectangle(card_box, radius=30, fill=self.COLORS["card_bg"], 
                               outline=self.COLORS["border"], width=2)
        
        # Load fonts (fallback to default if custom not available)
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            font_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)
            font_change = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
            font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        except:
            font_title = ImageFont.load_default()
            font_value = ImageFont.load_default()
            font_change = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()
        
        # Title
        title_y = 80
        draw.text((size // 2, title_y), title, fill=self.COLORS["text_dim"], 
                  font=font_title, anchor="mt")
        
        # Main value
        value_y = size // 2 - 40
        draw.text((size // 2, value_y), value, fill=self.COLORS["positive"], 
                  font=font_value, anchor="mm")
        
        # Change indicator
        if change:
            change_y = value_y + 100
            direction = change.get("direction", "neutral")
            pct = change.get("percentage", 0)
            
            color = self.COLORS["positive"] if direction == "up" else (
                self.COLORS["negative"] if direction == "down" else self.COLORS["text_dim"]
            )
            arrow = "↑" if direction == "up" else ("↓" if direction == "down" else "→")
            change_text = f"{arrow} {abs(pct):.1f}%"
            
            draw.text((size // 2, change_y), change_text, fill=color, 
                      font=font_change, anchor="mt")
        
        # Subtitle
        if subtitle:
            sub_y = size - 120
            draw.text((size // 2, sub_y), subtitle, fill=self.COLORS["text_dim"], 
                      font=font_subtitle, anchor="mt")
        
        # Sparkline
        if sparkline_data and len(sparkline_data) > 1:
            self._draw_sparkline(draw, sparkline_data, size)
        
        # Footer with timestamp
        footer_y = size - 50
        timestamp = datetime.now().strftime("%d %b %Y")
        draw.text((size // 2, footer_y), f"Generated: {timestamp}", 
                  fill=self.COLORS["text_dim"], font=font_subtitle, anchor="mt")
        
        # Save
        if not filename:
            filename = f"kpi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, "PNG", quality=95)
        
        return filepath
    
    def generate_comparison_card(
        self,
        title: str,
        items: List[Dict[str, Any]],
        filename: Optional[str] = None
    ) -> str:
        """Generate a comparison card with multiple items"""
        
        if not self._pil_available:
            return self._generate_text_card(title, str(items), filename)
        
        from PIL import Image, ImageDraw, ImageFont
        
        size = 1080
        img = Image.new('RGB', (size, size), self.COLORS["background"])
        draw = ImageDraw.Draw(img)
        
        # Card background
        card_margin = 40
        draw.rounded_rectangle(
            (card_margin, card_margin, size - card_margin, size - card_margin),
            radius=30, fill=self.COLORS["card_bg"], outline=self.COLORS["border"], width=2
        )
        
        # Fonts
        try:
            font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
            font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
            font_value = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        except:
            font_title = font_label = font_value = ImageFont.load_default()
        
        # Title
        draw.text((size // 2, 100), title, fill=self.COLORS["text"], 
                  font=font_title, anchor="mt")
        
        # Items
        y_start = 200
        y_spacing = 180
        
        for i, item in enumerate(items[:4]):  # Max 4 items
            y = y_start + (i * y_spacing)
            
            # Label
            draw.text((100, y), item.get("label", ""), fill=self.COLORS["text_dim"], 
                      font=font_label, anchor="lt")
            
            # Value
            value = item.get("value", "N/A")
            color = item.get("color", self.COLORS["positive"])
            draw.text((size - 100, y + 40), value, fill=color, 
                      font=font_value, anchor="rt")
            
            # Separator line
            if i < len(items) - 1:
                draw.line([(100, y + 100), (size - 100, y + 100)], 
                         fill=self.COLORS["border"], width=1)
        
        # Footer
        footer_y = size - 50
        timestamp = datetime.now().strftime("%d %b %Y")
        draw.text((size // 2, footer_y), f"Generated: {timestamp}", 
                  fill=self.COLORS["text_dim"], font=font_label, anchor="mt")
        
        # Save
        if not filename:
            filename = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath, "PNG", quality=95)
        
        return filepath
    
    def _draw_sparkline(self, draw, data: List[float], canvas_size: int):
        """Draw a mini sparkline at the bottom of card"""
        if len(data) < 2:
            return
        
        # Sparkline area
        margin = 100
        width = canvas_size - (2 * margin)
        height = 80
        y_base = canvas_size - 180
        
        # Normalize data
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        # Draw line
        points = []
        for i, val in enumerate(data):
            x = margin + (i / (len(data) - 1)) * width
            y = y_base + height - ((val - min_val) / range_val) * height
            points.append((x, y))
        
        # Draw sparkline
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=self.COLORS["positive"], width=3)
    
    def _generate_text_card(self, title: str, content: str, filename: str) -> str:
        """Fallback text card if PIL unavailable"""
        if not filename:
            filename = f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"=== {title} ===\n\n{content}\n\nGenerated: {datetime.now()}")
        
        return filepath
