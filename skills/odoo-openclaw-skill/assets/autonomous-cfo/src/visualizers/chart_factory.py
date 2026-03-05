"""
Chart Factory - Selects and generates appropriate visualizations
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Script-relative output directory
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_ROOT = os.path.normpath(os.path.join(_SCRIPT_DIR, "..", ".."))
DEFAULT_OUTPUT_DIR = os.path.join(_SKILL_ROOT, "output", "charts")


class ChartFactory:
    """Generates charts with "Midnight Ledger" dark theme for WhatsApp"""
    
    # Midnight Ledger theme colors
    COLORS = {
        "background": "#0a0e1a",
        "positive": "#cd7f32",  # Copper glow
        "negative": "#c45c5c",  # Muted crimson
        "neutral": "#e8e8e8",   # Silver
        "accent": "#d4af37",    # Gold
        "grid": "#1a2035",
        "text": "#e8e8e8",
        "text_dim": "#8892a8",
    }
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)
        self._matplotlib_available = self._check_matplotlib()
    
    def _check_matplotlib(self) -> bool:
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            return True
        except ImportError:
            return False
    
    def select_chart_type(self, data: Dict[str, Any], report_type: str) -> str:
        """
        Automatically select best chart type based on data.
        Returns: 'line', 'bar', 'horizontal_bar', 'pie', 'sparkline', 'dual_line'
        """
        # Two metrics over time -> dual line
        if "metric_a" in data and "metric_b" in data:
            return "dual_line"
        
        # Breakdown by category -> horizontal bar
        if "breakdown" in data and isinstance(data["breakdown"], dict):
            if len(data["breakdown"]) > 5:
                return "horizontal_bar"
            return "bar"
        
        # Time series -> line
        if "trend" in data or "monthly" in data:
            return "line"
        
        # Top N items -> horizontal bar
        if "top_items" in data:
            return "horizontal_bar"
        
        # Single KPI -> sparkline or single value card
        if "kpi" in data:
            return "sparkline"
        
        # Comparison between two values
        if "comparison" in data:
            return "bar"
        
        # Default
        return "bar"
    
    def generate_chart(
        self,
        data: Dict[str, Any],
        chart_type: str,
        title: str,
        filename: Optional[str] = None
    ) -> str:
        """Generate chart and return path to image"""
        if not self._matplotlib_available:
            return self._generate_fallback_chart(data, title, filename)
        
        import matplotlib.pyplot as plt
        import matplotlib.patheffects as pe
        import numpy as np
        
        # Set dark theme
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 6), facecolor=self.COLORS["background"])
        ax.set_facecolor(self.COLORS["background"])
        
        # Set spine and grid colors
        for spine in ax.spines.values():
            spine.set_color(self.COLORS["grid"])
        ax.tick_params(colors=self.COLORS["text_dim"])
        ax.xaxis.label.set_color(self.COLORS["text"])
        ax.yaxis.label.set_color(self.COLORS["text"])
        
        if chart_type == "line":
            self._draw_line_chart(ax, data, title)
        elif chart_type == "dual_line":
            self._draw_dual_line_chart(ax, data, title)
        elif chart_type == "bar":
            self._draw_bar_chart(ax, data, title)
        elif chart_type == "horizontal_bar":
            self._draw_horizontal_bar_chart(ax, data, title)
        elif chart_type == "sparkline":
            self._draw_sparkline(ax, data, title)
        
        # Title styling
        ax.set_title(title, color=self.COLORS["text"], fontsize=16, fontweight='bold', pad=20)
        
        # Save
        if not filename:
            filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        plt.tight_layout()
        plt.savefig(filepath, facecolor=self.COLORS["background"], dpi=150, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def _draw_line_chart(self, ax, data: Dict, title: str):
        """Draw single line chart with gradient fill"""
        import matplotlib.pyplot as plt
        import numpy as np
        
        x = data.get("x", list(range(len(data.get("y", [])))))
        y = data.get("y", [])
        
        ax.plot(x, y, color=self.COLORS["positive"], linewidth=2.5, marker='o', markersize=6)
        ax.fill_between(x, y, alpha=0.3, color=self.COLORS["positive"])
        
        # Rotate x labels if many points
        if len(x) > 6:
            plt.xticks(rotation=45, ha='right')
        
        ax.set_xlabel(data.get("x_label", "Period"), fontsize=12)
        ax.set_ylabel(data.get("y_label", "Amount"), fontsize=12)
        ax.grid(True, alpha=0.2, color=self.COLORS["grid"])
    
    def _draw_dual_line_chart(self, ax, data: Dict, title: str):
        """Draw two metrics on same chart"""
        x = data.get("x", list(range(len(data.get("y1", [])))))
        y1 = data.get("y1", [])
        y2 = data.get("y2", [])
        
        ax.plot(x, y1, color=self.COLORS["positive"], linewidth=2.5, marker='o', 
                label=data.get("label1", "Metric 1"))
        ax.plot(x, y2, color=self.COLORS["negative"], linewidth=2.5, marker='s', 
                label=data.get("label2", "Metric 2"))
        
        ax.legend(facecolor=self.COLORS["background"], edgecolor=self.COLORS["grid"])
        ax.grid(True, alpha=0.2, color=self.COLORS["grid"])
    
    def _draw_bar_chart(self, ax, data: Dict, title: str):
        """Draw vertical bar chart"""
        import numpy as np
        
        x = data.get("x", [])
        y = data.get("y", [])
        
        bars = ax.bar(x, y, color=self.COLORS["positive"], edgecolor=self.COLORS["accent"], linewidth=1)
        
        # Highlight max/min
        if y:
            max_idx = y.index(max(y))
            min_idx = y.index(min(y))
            bars[max_idx].set_color(self.COLORS["accent"])
            bars[min_idx].set_color(self.COLORS["negative"])
        
        ax.grid(True, alpha=0.2, color=self.COLORS["grid"], axis='y')
    
    def _draw_horizontal_bar_chart(self, ax, data: Dict, title: str):
        """Draw horizontal bar chart for rankings"""
        labels = data.get("labels", [])
        values = data.get("values", [])
        
        y_pos = range(len(labels))
        bars = ax.barh(y_pos, values, color=self.COLORS["positive"], 
                       edgecolor=self.COLORS["accent"], linewidth=1)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.invert_yaxis()  # Largest at top
        
        ax.grid(True, alpha=0.2, color=self.COLORS["grid"], axis='x')
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, values)):
            ax.text(val + max(values)*0.02, bar.get_y() + bar.get_height()/2,
                   f'{val:,.0f}', va='center', color=self.COLORS["text_dim"], fontsize=10)
    
    def _draw_sparkline(self, ax, data: Dict, title: str):
        """Draw minimal sparkline for KPI card"""
        y = data.get("y", [])
        if not y:
            return
        
        ax.plot(y, color=self.COLORS["positive"], linewidth=2)
        ax.fill_between(range(len(y)), y, alpha=0.3, color=self.COLORS["positive"])
        
        # Remove axes for clean sparkline look
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def _generate_fallback_chart(self, data: Dict, title: str, filename: str) -> str:
        """Generate a simple text-based chart if matplotlib unavailable"""
        if not filename:
            filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(f"=== {title} ===\n\n")
            for key, value in data.items():
                f.write(f"{key}: {value}\n")
        
        return filepath
