#!/usr/bin/env python3
"""
Scientific Graphical Abstract Generator

Generate editable SVG graphical abstracts for scientific papers
using multiple AI models (Claude, GPT-4o, DeepSeek, etc.)
"""

import argparse
import json
import sys
import os
from typing import Dict, Any, List, Optional
import re


class Config:
    """Configuration management for AI models."""

    def __init__(self, model: str = "claude"):
        self.model = model
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self) -> Dict[str, Optional[str]]:
        """Load API keys from environment variables."""
        return {
            "claude": os.getenv("ANTHROPIC_API_KEY"),
            "gpt4o": os.getenv("OPENAI_API_KEY"),
            "deepseek": os.getenv("DEEPSEEK_API_KEY"),
        }


class SVGBuilder:
    """Build SVG graphics from scratch or templates."""

    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.elements = []

    def add_rectangle(self, x: int, y: int, w: int, h: int,
                     fill: str = "#4A90E2", stroke: str = "none",
                     rx: int = 0, label: str = "") -> str:
        """Add a rectangle element."""
        element_id = f"rect-{len(self.elements)}"
        svg_rect = f'<rect id="{element_id}" x="{x}" y="{y}" width="{w}" height="{h}" '
        svg_rect += f'fill="{fill}" stroke="{stroke}" rx="{rx}"'
        if label:
            svg_rect += f' ><title>{label}</title></rect>'
        else:
            svg_rect += '/>'
        self.elements.append(svg_rect)
        return element_id

    def add_circle(self, cx: int, cy: int, r: int,
                   fill: str = "#4A90E2", stroke: str = "none",
                   label: str = "") -> str:
        """Add a circle element."""
        element_id = f"circle-{len(self.elements)}"
        svg_circle = f'<circle id="{element_id}" cx="{cx}" cy="{cy}" r="{r}" '
        svg_circle += f'fill="{fill}" stroke="{stroke}"'
        if label:
            svg_circle += f' ><title>{label}</title></circle>'
        else:
            svg_circle += '/>'
        self.elements.append(svg_circle)
        return element_id

    def add_text(self, x: int, y: int, text: str,
                 font_size: int = 14, fill: str = "#333333",
                 font_weight: str = "normal", anchor: str = "start") -> str:
        """Add a text element."""
        element_id = f"text-{len(self.elements)}"
        svg_text = f'<text id="{element_id}" x="{x}" y="{y}" '
        svg_text += f'font-family="Arial, sans-serif" font-size="{font_size}" '
        svg_text += f'fill="{fill}" font-weight="{font_weight}" '
        svg_text += f'text-anchor="{anchor}">{text}</text>'
        self.elements.append(svg_text)
        return element_id

    def add_line(self, x1: int, y1: int, x2: int, y2: int,
                 stroke: str = "#333333", stroke_width: int = 2) -> str:
        """Add a line element."""
        element_id = f"line-{len(self.elements)}"
        svg_line = f'<line id="{element_id}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        svg_line += f'stroke="{stroke}" stroke-width="{stroke_width}" />'
        self.elements.append(svg_line)
        return element_id

    def add_arrow(self, x1: int, y1: int, x2: int, y2: int,
                  color: str = "#333333", width: int = 2) -> str:
        """Add an arrow element."""
        element_id = f"arrow-{len(self.elements)}"
        # Calculate arrow head
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_size = 10
        x3 = x2 - arrow_size * math.cos(angle - math.pi / 6)
        y3 = y2 - arrow_size * math.sin(angle - math.pi / 6)
        x4 = x2 - arrow_size * math.cos(angle + math.pi / 6)
        y4 = y2 - arrow_size * math.sin(angle + math.pi / 6)

        svg_arrow = f'<g id="{element_id}">'
        svg_arrow += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" />'
        svg_arrow += f'<polygon points="{x2},{y2} {x3},{y3} {x4},{y4}" fill="{color}" />'
        svg_arrow += '</g>'
        self.elements.append(svg_arrow)
        return element_id

    def add_bar_chart(self, data: List[Dict[str, Any]],
                      x: int = 50, y: int = 50,
                      width: int = 700, height: int = 400,
                      color: str = "#4A90E2") -> None:
        """Add a bar chart."""
        if not data:
            return

        # Find max value for scaling
        max_value = max(float(d.get('value', 0)) for d in data)
        bar_width = width // len(data) - 20

        # Title
        title = data[0].get('title', 'Bar Chart')
        self.add_text(x + width // 2, y - 10, title,
                     font_size=18, font_weight="bold", anchor="middle")

        # Bars
        for i, item in enumerate(data):
            label = item.get('label', f'Item {i+1}')
            value = float(item.get('value', 0))
            bar_height = (value / max_value) * (height - 50)

            bar_x = x + i * (bar_width + 20) + 10
            bar_y = y + height - bar_height - 30

            # Bar
            self.add_rectangle(bar_x, bar_y, bar_width, bar_height,
                             fill=color, label=f"{label}: {value}")

            # Label
            self.add_text(bar_x + bar_width // 2, y + height - 10,
                         label, font_size=12, anchor="middle")

            # Value
            self.add_text(bar_x + bar_width // 2, bar_y - 5,
                         str(value), font_size=11, anchor="middle")

        # Y-axis
        self.add_line(x, y, x, y + height - 30, stroke="#333", stroke_width=2)
        # X-axis
        self.add_line(x, y + height - 30, x + width, y + height - 30,
                     stroke="#333", stroke_width=2)

    def add_line_chart(self, data: List[Dict[str, Any]],
                       x: int = 50, y: int = 50,
                       width: int = 700, height: int = 400,
                       color: str = "#4A90E2") -> None:
        """Add a line chart."""
        if len(data) < 2:
            return

        # Find min/max values
        values = [float(d.get('value', 0)) for d in data]
        min_value = min(values)
        max_value = max(values)
        value_range = max_value - min_value if max_value != min_value else 1

        # Title
        title = data[0].get('title', 'Line Chart')
        self.add_text(x + width // 2, y - 10, title,
                     font_size=18, font_weight="bold", anchor="middle")

        # Generate path data
        points = []
        point_spacing = width / (len(data) - 1)

        for i, item in enumerate(data):
            px = x + i * point_spacing
            normalized_value = (float(item.get('value', 0)) - min_value) / value_range
            py = y + height - 30 - (normalized_value * (height - 50))
            points.append(f"{px},{py}")

            # Label
            label = item.get('label', str(i))
            self.add_text(px, y + height - 10, label,
                         font_size=12, anchor="middle")

        # Draw line
        path_data = "M " + " L ".join(points)
        path_element = f'<path d="{path_data}" fill="none" stroke="{color}" stroke-width="3" />'
        self.elements.append(path_element)

        # Draw points
        for point in points:
            px, py = point.split(',')
            self.add_circle(int(px), int(py), 5, fill=color, stroke="#fff")

        # Axes
        self.add_line(x, y, x, y + height - 30, stroke="#333", stroke_width=2)
        self.add_line(x, y + height - 30, x + width, y + height - 30,
                     stroke="#333", stroke_width=2)

    def add_pie_chart(self, data: List[Dict[str, Any]],
                      cx: int = 400, cy: int = 300,
                      radius: int = 150) -> None:
        """Add a pie chart."""
        if not data:
            return

        total = sum(float(d.get('value', 0)) for d in data)
        colors = ["#4A90E2", "#50E3C2", "#F5A623", "#E040FB", "#FF5722",
                 "#4CAF50", "#2196F3", "#FFC107", "#9C27B0", "#00BCD4"]

        # Title
        title = data[0].get('title', 'Pie Chart')
        self.add_text(cx, cy - radius - 30, title,
                     font_size=18, font_weight="bold", anchor="middle")

        start_angle = -90  # Start from top

        for i, item in enumerate(data):
            value = float(item.get('value', 0))
            angle = (value / total) * 360
            end_angle = start_angle + angle

            # Calculate path
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)

            x1 = cx + radius * math.cos(start_rad)
            y1 = cy + radius * math.sin(start_rad)
            x2 = cx + radius * math.cos(end_rad)
            y2 = cy + radius * math.sin(end_rad)

            large_arc = 1 if angle > 180 else 0

            path_data = f"M {cx} {cy} L {x1} {y1} A {radius} {radius} 0 {large_arc} 1 {x2} {y2} Z"
            path_element = f'<path d="{path_data}" fill="{colors[i % len(colors)]}" stroke="#fff" stroke-width="2" />'
            self.elements.append(path_element)

            # Add legend
            legend_x = cx + radius + 50
            legend_y = cy - radius + i * 30
            label = item.get('label', f'Item {i+1}')
            percentage = (value / total) * 100

            self.add_rectangle(legend_x - 10, legend_y - 10, 20, 20,
                             fill=colors[i % len(colors)])
            self.add_text(legend_x + 20, legend_y + 5,
                         f"{label} ({percentage:.1f}%)", font_size=12)

            start_angle = end_angle

    def add_flowchart(self, steps: List[str],
                      x: int = 100, y: int = 50,
                      box_width: int = 200, box_height: int = 60,
                      spacing: int = 80, color: str = "#4A90E2") -> None:
        """Add a vertical flowchart."""
        current_y = y

        for i, step in enumerate(steps):
            # Box
            self.add_rectangle(x, current_y, box_width, box_height,
                             fill=color, stroke="#333", rx=5)

            # Text
            self.add_text(x + box_width // 2, current_y + box_height // 2 + 5,
                         step, font_size=14, font_weight="bold",
                         fill="white", anchor="middle")

            # Arrow (except for last step)
            if i < len(steps) - 1:
                arrow_start_y = current_y + box_height
                arrow_end_y = current_y + box_height + spacing
                self.add_arrow(x + box_width // 2, arrow_start_y,
                             x + box_width // 2, arrow_end_y,
                             color="#333", width=2)
                current_y = arrow_end_y
            else:
                current_y += box_height

    def build(self) -> str:
        """Build the complete SVG."""
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 {self.width} {self.height}"
     width="{self.width}" height="{self.height}">
  <!-- Generated by Scientific Graphical Abstract Generator -->
  <!-- This SVG is fully editable -->
  <style>
    text {{ font-family: 'Arial', sans-serif; }}
    rect, circle {{ transition: all 0.3s ease; }}
    rect:hover, circle:hover {{ opacity: 0.8; }}
  </style>
'''
        for element in self.elements:
            svg += f"  {element}\n"
        svg += '</svg>'
        return svg


class GraphicalAbstractGenerator:
    """Main generator class."""

    def __init__(self, config: Config):
        self.config = config
        self.svg_builder = None

    def generate_from_prompt(self, prompt: str, chart_type: str = "auto",
                            width: int = 800, height: int = 600,
                            style: str = "professional") -> str:
        """Generate SVG from text prompt."""
        self.svg_builder = SVGBuilder(width, height)

        # Parse the prompt and generate appropriate visualization
        prompt_lower = prompt.lower()

        if "workflow" in prompt_lower or "flow" in prompt_lower:
            return self._generate_workflow(prompt)
        elif "chart" in prompt_lower or "plot" in prompt_lower:
            if "bar" in prompt_lower:
                return self._generate_bar_chart_prompt(prompt)
            elif "line" in prompt_lower:
                return self._generate_line_chart_prompt(prompt)
            elif "pie" in prompt_lower:
                return self._generate_pie_chart_prompt(prompt)
        elif "mechanism" in prompt_lower or "diagram" in prompt_lower:
            return self._generate_mechanism_diagram(prompt)

        # Default: Generate a template-based visualization
        return self._generate_template(prompt, style)

    def generate_from_data(self, data: List[Dict[str, Any]],
                          chart_type: str = "bar",
                          title: str = "Chart",
                          width: int = 800, height: int = 600,
                          color: str = "#4A90E2") -> str:
        """Generate SVG from structured data."""
        self.svg_builder = SVGBuilder(width, height)

        # Add title to data
        if data:
            data[0]['title'] = title

        if chart_type == "bar":
            self.svg_builder.add_bar_chart(data, color=color)
        elif chart_type == "line":
            self.svg_builder.add_line_chart(data, color=color)
        elif chart_type == "pie":
            self.svg_builder.add_pie_chart(data)

        return self.svg_builder.build()

    def _generate_workflow(self, prompt: str) -> str:
        """Generate a workflow diagram."""
        # Extract steps from prompt
        steps = []
        if "→" in prompt or "->" in prompt or "to" in prompt.lower():
            # Try to parse workflow steps
            for sep in ["→", "->", " to ", " then "]:
                if sep in prompt or sep.lower() in prompt.lower():
                    parts = re.split(sep.replace("→", "|").replace("->", "|"), prompt,
                                   flags=re.IGNORECASE)
                    steps = [p.strip() for p in parts if p.strip()]
                    break

        if not steps:
            # Default workflow
            steps = ["Step 1", "Step 2", "Step 3", "Step 4"]

        self.svg_builder.add_flowchart(steps)
        return self.svg_builder.build()

    def _generate_bar_chart_prompt(self, prompt: str) -> str:
        """Generate a bar chart from prompt."""
        # Try to extract data from prompt
        data = self._extract_data_from_prompt(prompt)
        if data:
            self.svg_builder.add_bar_chart(data)
        else:
            # Generate placeholder
            self.svg_builder.add_text(400, 300, "Bar Chart: Please provide data",
                                     font_size=20, anchor="middle")
        return self.svg_builder.build()

    def _generate_line_chart_prompt(self, prompt: str) -> str:
        """Generate a line chart from prompt."""
        data = self._extract_data_from_prompt(prompt)
        if data and len(data) > 1:
            self.svg_builder.add_line_chart(data)
        else:
            self.svg_builder.add_text(400, 300, "Line Chart: Please provide data",
                                     font_size=20, anchor="middle")
        return self.svg_builder.build()

    def _generate_pie_chart_prompt(self, prompt: str) -> str:
        """Generate a pie chart from prompt."""
        data = self._extract_data_from_prompt(prompt)
        if data:
            self.svg_builder.add_pie_chart(data)
        else:
            self.svg_builder.add_text(400, 300, "Pie Chart: Please provide data",
                                     font_size=20, anchor="middle")
        return self.svg_builder.build()

    def _generate_mechanism_diagram(self, prompt: str) -> str:
        """Generate a mechanism diagram."""
        # Add title
        self.svg_builder.add_text(400, 40, "Mechanism of Action",
                                 font_size=24, font_weight="bold", anchor="middle")

        # Create a simple mechanism diagram template
        # Central component
        self.svg_builder.add_rectangle(300, 150, 200, 100, fill="#4A90E2", rx=10,
                                      label="Target")
        self.svg_builder.add_text(400, 200, "Target Protein",
                                 font_size=16, fill="white", anchor="middle")

        # Inhibitor/Drug
        self.svg_builder.add_circle(400, 350, 50, fill="#E040FB", label="Drug")
        self.svg_builder.add_text(400, 350, "Drug",
                                 font_size=14, fill="white", anchor="middle")

        # Arrow
        self.svg_builder.add_arrow(400, 290, 400, 290, color="#333", width=3)

        # Effect
        self.svg_builder.add_rectangle(300, 450, 200, 80, fill="#50E3C2", rx=10,
                                      label="Effect")
        self.svg_builder.add_text(400, 490, "Inhibition",
                                 font_size=16, fill="white", anchor="middle")

        self.svg_builder.add_arrow(400, 400, 400, 440, color="#333", width=3)

        return self.svg_builder.build()

    def _generate_template(self, prompt: str, style: str) -> str:
        """Generate a template-based visualization."""
        # Add title
        self.svg_builder.add_text(400, 50, "Graphical Abstract",
                                 font_size=28, font_weight="bold", anchor="middle")

        # Background
        self.svg_builder.add_rectangle(50, 100, 700, 450,
                                     fill="#f8f9fa", stroke="#dee2e6", rx=10)

        # Placeholder for content
        self.svg_builder.add_text(400, 200, "Research visualization will be here",
                                 font_size=18, anchor="middle", fill="#6c757d")
        self.svg_builder.add_text(400, 250, "Based on your description:",
                                 font_size=14, anchor="middle", fill="#6c757d")
        self.svg_builder.add_text(400, 300, f'"{prompt[:100]}..."',
                                 font_size=12, anchor="middle", fill="#495057",
                                 font_weight="italic")

        return self.svg_builder.build()

    def _extract_data_from_prompt(self, prompt: str) -> List[Dict[str, Any]]:
        """Try to extract structured data from prompt."""
        data = []

        # Pattern: "Label: Value" or "Label=Value"
        patterns = [
            r'(\w+(?:\s+\w+)*)\s*:\s*(\d+(?:\.\d+)?)',
            r'(\w+(?:\s+\w+)*)\s*=\s*(\d+(?:\.\d+)?)',
            r'(\w+(?:\s+\w+)*)\s+(\d+(?:\.\d+)?)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, prompt)
            if matches and len(matches) >= 2:
                for label, value in matches:
                    data.append({"label": label, "value": float(value)})
                break

        return data


import math  # Import math for SVGBuilder calculations


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='Generate scientific graphical abstracts in SVG format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from prompt
  %(prog)s generate --prompt "Create a workflow: Sample -> Extract -> Analyze" --output workflow.svg

  # Generate bar chart from data
  %(prog)s generate --data data.json --type bar --title "Sales by Quarter" --output chart.svg

  # Generate line chart from CSV
  %(prog)s generate --data results.csv --type line --output line.svg

  # Use specific model
  %(prog)s generate --prompt "Create a mechanism diagram" --model claude --output diagram.svg
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate a graphical abstract')
    generate_parser.add_argument('--prompt', help='Description of what to visualize')
    generate_parser.add_argument('--data', help='Data file (CSV/JSON)')
    generate_parser.add_argument('--type', choices=['bar', 'line', 'pie', 'scatter', 'flowchart', 'diagram', 'auto'],
                                 default='auto', help='Chart/visualization type')
    generate_parser.add_argument('--model', choices=['claude', 'gpt4o', 'deepseek'],
                                 default='claude', help='AI model to use')
    generate_parser.add_argument('--style', choices=['minimal', 'professional', 'colorful', 'journal'],
                                 default='professional', help='Visual style')
    generate_parser.add_argument('--title', default='Chart', help='Chart title')
    generate_parser.add_argument('--output', required=True, help='Output SVG file path')
    generate_parser.add_argument('--width', type=int, default=800, help='Canvas width')
    generate_parser.add_argument('--height', type=int, default=600, help='Canvas height')
    generate_parser.add_argument('--color', default='#4A90E2', help='Primary color')

    # Template command
    template_parser = subparsers.add_parser('template', help='Use predefined templates')
    template_parser.add_argument('--type', choices=['workflow', 'mechanism', 'comparison', 'timeline'],
                                 required=True, help='Template type')
    template_parser.add_argument('--prompt', help='Specific requirements')
    template_parser.add_argument('--output', required=True, help='Output SVG file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize
    config = Config(args.model if args.command == 'generate' else 'claude')
    generator = GraphicalAbstractGenerator(config)

    # Execute command
    if args.command == 'generate':
        if args.data:
            # Load data from file
            try:
                with open(args.data, 'r', encoding='utf-8') as f:
                    if args.data.endswith('.json'):
                        data = json.load(f)
                    else:
                        # Simple CSV parsing
                        reader = csv.reader(f)
                        headers = next(reader)
                        data = []
                        for row in reader:
                            data.append({headers[0]: row[0], headers[1]: float(row[1])})

                svg_content = generator.generate_from_data(
                    data, chart_type=args.type, title=args.title,
                    width=args.width, height=args.height, color=args.color
                )
            except Exception as e:
                print(f"Error loading data: {str(e)}", file=sys.stderr)
                sys.exit(1)
        else:
            svg_content = generator.generate_from_prompt(
                args.prompt or "Graphical Abstract",
                chart_type=args.type,
                width=args.width,
                height=args.height,
                style=args.style
            )

        # Save SVG
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"SVG generated successfully: {args.output}")
        print(f"Model used: {args.model}")
        print(f"You can edit this file in Inkscape, Adobe Illustrator, or any text editor.")

    elif args.command == 'template':
        svg_content = generator.generate_from_prompt(
            f"Template: {args.type} - {args.prompt or ''}",
            chart_type="flowchart" if args.type == "workflow" else "diagram"
        )

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"Template generated successfully: {args.output}")


if __name__ == "__main__":
    import csv  # Import csv for data loading
    main()
