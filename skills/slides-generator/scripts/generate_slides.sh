#!/bin/bash
# Slides Generator - Create PDF slides from markdown
# Usage: ./generate_slides.sh --input <markdown_file> --output <pdf_file> [--logo <logo_file>] [--edit]

set -e

# Default values
INPUT=""
OUTPUT=""
EDIT_MODE=false
LOGO=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --logo)
            LOGO="$2"
            shift 2
            ;;
        --edit)
            EDIT_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$INPUT" ]]; then
    echo "Error: --input is required"
    echo "Usage: $0 --input <markdown_file> --output <pdf_file>"
    exit 1
fi

if [[ -z "$OUTPUT" ]]; then
    echo "Error: --output is required"
    echo "Usage: $0 --input <markdown_file> --output <pdf_file>"
    exit 1
fi

# Check if input file exists
if [[ ! -f "$INPUT" ]]; then
    echo "Error: Input file not found: $INPUT"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Install with: brew install python3 (macOS) or apt install python3 (Linux)"
    exit 1
fi

# Check/install fpdf2
if ! python3 -c "import fpdf" 2>/dev/null; then
    echo "Installing fpdf2..."
    pip3 install fpdf2 --quiet
fi

# Check for mermaid-cli (mmdc)
MERMAID_AVAILABLE=false
if command -v mmdc &> /dev/null; then
    MERMAID_AVAILABLE=true
    echo "Mermaid CLI detected - diagram rendering enabled"
elif command -v npx &> /dev/null; then
    # Try using npx to run mmdc
    if npx --yes @mermaid-js/mermaid-cli --version &> /dev/null 2>&1; then
        MERMAID_AVAILABLE=true
        echo "Mermaid CLI available via npx - diagram rendering enabled"
    fi
fi

if [[ "$MERMAID_AVAILABLE" == "false" ]]; then
    echo "Note: Mermaid CLI not found. Diagrams will render as code blocks."
    echo "Install with: npm install -g @mermaid-js/mermaid-cli"
fi

# Create output directory if needed
OUTPUT_DIR=$(dirname "$OUTPUT")
if [[ ! -d "$OUTPUT_DIR" ]]; then
    mkdir -p "$OUTPUT_DIR"
fi

# Create temp directory for mermaid diagrams
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Get logo - check --logo option first, then assets folder
if [[ -n "$LOGO" && -f "$LOGO" ]]; then
    LOGO_PATH="$LOGO"
else
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    LOGO_PATH="$SCRIPT_DIR/../assets/hummingbot-logo.png"

    if [[ ! -f "$LOGO_PATH" ]]; then
        LOGO_PATH="$SCRIPT_DIR/assets/hummingbot-logo.png"
    fi
fi

if [[ -f "$LOGO_PATH" ]]; then
    echo "Logo found: $LOGO_PATH"
else
    echo "Warning: Logo not found"
    LOGO_PATH=""
fi

export MERMAID_AVAILABLE
export TEMP_DIR
export LOGO_PATH

# Generate PDF using Python
INPUT="$INPUT" OUTPUT="$OUTPUT" python3 << 'PYTHON_SCRIPT'
import sys
import re
import os
import subprocess
import tempfile
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
from fpdf import FPDF

# Get arguments from environment
input_file = os.environ.get('INPUT')
output_file = os.environ.get('OUTPUT')
mermaid_available = os.environ.get('MERMAID_AVAILABLE', 'false') == 'true'
temp_dir = os.environ.get('TEMP_DIR', tempfile.gettempdir())
logo_path = os.environ.get('LOGO_PATH', '')

# Counter for mermaid diagrams
mermaid_counter = 0

def render_mermaid_to_png(mermaid_code):
    """Render mermaid code to PNG using mmdc CLI."""
    global mermaid_counter
    mermaid_counter += 1

    mmd_file = os.path.join(temp_dir, f'diagram_{mermaid_counter}.mmd')
    png_file = os.path.join(temp_dir, f'diagram_{mermaid_counter}.png')

    # Write mermaid code to temp file
    with open(mmd_file, 'w') as f:
        f.write(mermaid_code)

    try:
        # Try direct mmdc first
        result = subprocess.run(
            ['mmdc', '-i', mmd_file, '-o', png_file, '-b', 'transparent', '-w', '800'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0 and os.path.exists(png_file):
            return png_file
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    try:
        # Fallback to npx
        result = subprocess.run(
            ['npx', '--yes', '@mermaid-js/mermaid-cli', '-i', mmd_file, '-o', png_file, '-b', 'transparent', '-w', '800'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0 and os.path.exists(png_file):
            return png_file
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return None

# Hummingbot theme
THEME = {
    'bg_color': (255, 255, 255),
    'title_color': (33, 33, 33),
    'text_color': (66, 66, 66),
    'accent_color': (0, 208, 132),  # Hummingbot green #00D084
    'box_fill': (245, 245, 245),
    'box_border': (0, 208, 132),
    'arrow_color': (100, 100, 100),
}

class SlidesPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='L', unit='mm', format='A4')
        self.set_auto_page_break(auto=False)

    def add_slide_background(self):
        bg = THEME['bg_color']
        self.set_fill_color(*bg)
        self.rect(0, 0, 297, 210, 'F')

    def add_logo(self):
        """Add Hummingbot logo to lower right corner."""
        if logo_path and os.path.exists(logo_path):
            try:
                # Logo size: 15mm width, positioned in lower right
                logo_width = 15
                x_pos = 297 - logo_width - 8  # 8mm from right edge
                y_pos = 210 - logo_width - 5  # 5mm from bottom
                self.image(logo_path, x=x_pos, y=y_pos, w=logo_width)
            except Exception:
                pass  # Skip logo if any error

    def add_title_slide(self, title):
        self.add_page()
        self.add_slide_background()

        # Title
        self.set_font('Helvetica', 'B', 48)
        self.set_text_color(*THEME['title_color'])
        self.set_y(80)
        self.multi_cell(0, 20, title, align='C')

        # Accent line
        accent = THEME['accent_color']
        self.set_draw_color(*accent)
        self.set_line_width(2)
        self.line(98, 120, 199, 120)

        # Add logo
        self.add_logo()

    def add_content_slide(self, title, content):
        self.add_page()
        self.add_slide_background()

        # Slide title
        self.set_font('Helvetica', 'B', 32)
        self.set_text_color(*THEME['title_color'])
        self.set_xy(20, 15)
        self.cell(0, 15, title, ln=True)

        # Accent line under title
        accent = THEME['accent_color']
        self.set_draw_color(*accent)
        self.set_line_width(1)
        self.line(20, 35, 100, 35)

        # Check if this is a two-column slide (has both text and mermaid)
        has_mermaid = '```mermaid' in content or '```diagram' in content
        has_text_content = False
        for line in content.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('```') and not stripped.startswith('mermaid:'):
                if stripped.startswith('- ') or stripped.startswith('* ') or re.match(r'^\d+\.', stripped) or not stripped.startswith('```'):
                    has_text_content = True
                    break

        use_two_column = has_mermaid and has_text_content

        if use_two_column:
            self._render_two_column_slide(content)
        else:
            self._render_single_column_slide(content)

        # Add logo
        self.add_logo()

    def _render_two_column_slide(self, content):
        """Render slide with text on left, diagram on right."""
        # Split content into text and diagram parts
        text_lines = []
        mermaid_lines = []
        in_code_block = False
        block_type = 'code'

        for line in content.split('\n'):
            if line.strip().startswith('```'):
                if in_code_block:
                    in_code_block = False
                    block_type = 'code'
                else:
                    in_code_block = True
                    block_marker = line.strip().lower()
                    if 'mermaid' in block_marker:
                        block_type = 'mermaid'
                    elif 'diagram' in block_marker:
                        block_type = 'diagram'
                continue

            if in_code_block:
                if block_type in ['mermaid', 'diagram']:
                    mermaid_lines.append(line)
            else:
                text_lines.append(line)

        # Left column - text (x: 20-140)
        y_pos = 45
        self.set_font('Helvetica', '', 16)
        self.set_text_color(*THEME['text_color'])

        for line in text_lines:
            if y_pos > 185:
                break

            stripped = line.strip()
            if not stripped:
                y_pos += 4
                continue

            if stripped.startswith('- ') or stripped.startswith('* '):
                self.set_font('Helvetica', '', 14)
                self.set_xy(25, y_pos)
                bullet_text = stripped[2:]
                bullet_text = re.sub(r'\*\*(.*?)\*\*', r'\1', bullet_text)
                bullet_text = re.sub(r'\*(.*?)\*', r'\1', bullet_text)
                self.cell(5, 7, '-')
                self.set_x(32)
                self.multi_cell(100, 7, bullet_text)
                y_pos += 9
            elif re.match(r'^\d+\.', stripped):
                self.set_font('Helvetica', '', 14)
                self.set_xy(25, y_pos)
                stripped = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
                self.multi_cell(110, 7, stripped)
                y_pos += 9
            else:
                self.set_font('Helvetica', '', 14)
                self.set_xy(25, y_pos)
                stripped = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
                stripped = re.sub(r'\*(.*?)\*', r'\1', stripped)
                self.multi_cell(110, 7, stripped)
                y_pos += 9

        # Right column - diagram (x: 145-280)
        if mermaid_lines:
            self._render_mermaid_in_column(mermaid_lines, x_start=145, y_start=45, max_width=130)

    def _render_mermaid_in_column(self, mermaid_lines, x_start, y_start, max_width):
        """Render mermaid diagram in a specific column area."""
        mermaid_code = '\n'.join(mermaid_lines)

        if mermaid_available:
            png_path = render_mermaid_to_png(mermaid_code)
            if png_path and os.path.exists(png_path):
                try:
                    from PIL import Image
                    with Image.open(png_path) as img:
                        img_w, img_h = img.size

                    max_height = 140
                    scale_w = max_width / (img_w / 3.78)
                    scale_h = max_height / (img_h / 3.78)
                    scale = min(scale_w, scale_h, 1.0)

                    final_w = (img_w / 3.78) * scale
                    final_h = (img_h / 3.78) * scale

                    x_pos = x_start + (max_width - final_w) / 2

                    self.image(png_path, x=x_pos, y=y_start, w=final_w, h=final_h)
                    return
                except ImportError:
                    self.image(png_path, x=x_start, y=y_start, w=max_width)
                    return
                except Exception:
                    pass

        # Fallback: render as code
        self.set_font('Courier', '', 8)
        self.set_text_color(50, 50, 50)
        y = y_start
        for line in mermaid_lines[:15]:
            self.set_xy(x_start, y)
            self.cell(max_width, 5, line[:40])
            y += 5

    def _render_single_column_slide(self, content):
        """Render slide with single column layout."""
        # Content
        self.set_font('Helvetica', '', 18)
        self.set_text_color(*THEME['text_color'])
        self.set_xy(20, 45)

        # Process content - handle code blocks first
        lines = content.split('\n')
        y_pos = 45
        in_code_block = False
        block_type = 'code'  # 'code', 'diagram', or 'mermaid'
        code_lines = []

        i = 0
        while i < len(lines):
            if y_pos > 185:  # Avoid overflow
                break

            line = lines[i]

            # Check for code block start/end
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of block - render it
                    in_code_block = False
                    if code_lines:
                        if block_type == 'mermaid':
                            y_pos = self.render_mermaid(code_lines, y_pos)
                        elif block_type == 'diagram':
                            y_pos = self.render_diagram(code_lines, y_pos)
                        else:
                            y_pos = self.render_code_block(code_lines, y_pos)
                    code_lines = []
                    block_type = 'code'
                else:
                    # Start of block - check type
                    in_code_block = True
                    block_marker = line.strip().lower()
                    if 'mermaid' in block_marker:
                        block_type = 'mermaid'
                    elif 'diagram' in block_marker:
                        block_type = 'diagram'
                    else:
                        block_type = 'code'
                i += 1
                continue

            if in_code_block:
                code_lines.append(line)
                i += 1
                continue

            # Regular content processing
            stripped = line.strip()
            if not stripped:
                y_pos += 4
                i += 1
                continue

            # Handle bullet points
            if stripped.startswith('- ') or stripped.startswith('* '):
                self.set_font('Helvetica', '', 16)
                self.set_xy(25, y_pos)
                bullet_text = stripped[2:]
                bullet_text = re.sub(r'\*\*(.*?)\*\*', r'\1', bullet_text)
                bullet_text = re.sub(r'\*(.*?)\*', r'\1', bullet_text)
                self.cell(5, 8, '-')
                self.set_x(32)
                self.multi_cell(245, 8, bullet_text)
                y_pos += 10
            # Handle numbered lists
            elif re.match(r'^\d+\.', stripped):
                self.set_font('Helvetica', '', 16)
                self.set_xy(25, y_pos)
                stripped = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
                stripped = re.sub(r'\*(.*?)\*', r'\1', stripped)
                self.multi_cell(250, 8, stripped)
                y_pos += 10
            # Handle table rows
            elif stripped.startswith('|'):
                self.set_font('Helvetica', '', 12)
                self.set_xy(25, y_pos)
                cells = [c.strip() for c in stripped.split('|')[1:-1]]
                if cells and not all(c.replace('-', '') == '' for c in cells):
                    row_text = '   '.join(cells)
                    self.multi_cell(250, 7, row_text)
                    y_pos += 8
            # Regular text
            else:
                self.set_font('Helvetica', '', 16)
                self.set_xy(25, y_pos)
                stripped = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)
                stripped = re.sub(r'\*(.*?)\*', r'\1', stripped)
                stripped = re.sub(r'`(.*?)`', r'\1', stripped)
                self.multi_cell(250, 8, stripped)
                y_pos += 10

            i += 1

    def render_code_block(self, code_lines, y_pos):
        """Render a code block with monospace font and background."""
        if not code_lines:
            return y_pos

        # Calculate block height
        line_height = 5
        block_height = len(code_lines) * line_height + 6
        max_height = 185 - y_pos

        if block_height > max_height:
            block_height = max_height
            max_lines = int((max_height - 6) / line_height)
            code_lines = code_lines[:max_lines]

        # Draw background
        self.set_fill_color(245, 245, 245)
        self.rect(25, y_pos, 250, block_height, 'F')

        # Draw border
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        self.rect(25, y_pos, 250, block_height, 'D')

        # Render code with monospace font
        self.set_font('Courier', '', 10)
        self.set_text_color(50, 50, 50)

        code_y = y_pos + 3
        for line in code_lines:
            if code_y > 182:
                break
            self.set_xy(28, code_y)
            # Preserve spacing - don't strip
            self.cell(244, line_height, line[:80])  # Limit line length
            code_y += line_height

        # Reset colors
        self.set_text_color(*THEME['text_color'])

        return y_pos + block_height + 3

    def render_mermaid(self, mermaid_lines, y_pos):
        """Render a mermaid diagram as an image."""
        if not mermaid_lines:
            return y_pos

        mermaid_code = '\n'.join(mermaid_lines)

        if mermaid_available:
            png_path = render_mermaid_to_png(mermaid_code)
            if png_path and os.path.exists(png_path):
                # Calculate available space
                max_height = 185 - y_pos
                max_width = 250

                # Add the image centered
                try:
                    # Get image dimensions
                    from PIL import Image
                    with Image.open(png_path) as img:
                        img_w, img_h = img.size

                    # Scale to fit
                    scale_w = max_width / (img_w / 3.78)  # Convert px to mm (96 dpi)
                    scale_h = max_height / (img_h / 3.78)
                    scale = min(scale_w, scale_h, 1.0)

                    final_w = (img_w / 3.78) * scale
                    final_h = (img_h / 3.78) * scale

                    x_pos = (297 - final_w) / 2  # Center on slide

                    self.image(png_path, x=x_pos, y=y_pos, w=final_w, h=final_h)
                    return y_pos + final_h + 5
                except ImportError:
                    # PIL not available, use fixed size
                    self.image(png_path, x=25, y=y_pos, w=max_width)
                    return y_pos + 80  # Estimate height
                except Exception:
                    pass

        # Fallback: render as code block
        return self.render_code_block(mermaid_lines, y_pos)

    def render_diagram(self, diagram_lines, y_pos):
        """Render a diagram with proper boxes and arrows."""
        if not diagram_lines:
            return y_pos

        # Parse diagram commands
        elements = []
        current_y = y_pos
        x_center = 148  # Center of slide

        for line in diagram_lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Parse: box "Label"
            box_match = re.match(r'^box\s+"([^"]+)"(?:\s+(\w+))?', line)
            if box_match:
                label = box_match.group(1)
                style = box_match.group(2) or 'default'
                elements.append(('box', label, style, current_y))
                current_y += 25
                continue

            # Parse: arrow down/up/right/left
            arrow_match = re.match(r'^arrow\s+(\w+)(?:\s+(\d+))?', line)
            if arrow_match:
                direction = arrow_match.group(1)
                length = int(arrow_match.group(2) or 15)
                elements.append(('arrow', direction, length, current_y))
                current_y += length
                continue

            # Parse: group "Label" { ... }
            group_match = re.match(r'^group\s+"([^"]+)"', line)
            if group_match:
                label = group_match.group(1)
                elements.append(('group_start', label, current_y))
                continue

            if line == '}':
                elements.append(('group_end', current_y))
                current_y += 5
                continue

            # Parse: row { box "A", box "B" }
            row_match = re.match(r'^row\s*\{(.+)\}', line)
            if row_match:
                row_content = row_match.group(1)
                boxes = re.findall(r'box\s+"([^"]+)"', row_content)
                if boxes:
                    elements.append(('row', boxes, current_y))
                    current_y += 25
                continue

        # Render elements
        group_stack = []
        for elem in elements:
            if elem[0] == 'box':
                _, label, style, ey = elem
                self._draw_box(x_center - 50, ey, 100, 18, label, style)

            elif elem[0] == 'arrow':
                _, direction, length, ey = elem
                self._draw_arrow(x_center, ey, direction, length)

            elif elem[0] == 'row':
                _, boxes, ey = elem
                num_boxes = len(boxes)
                total_width = num_boxes * 80 + (num_boxes - 1) * 20
                start_x = x_center - total_width / 2
                for i, label in enumerate(boxes):
                    bx = start_x + i * 100
                    self._draw_box(bx, ey, 75, 18, label, 'default')

            elif elem[0] == 'group_start':
                _, label, ey = elem
                group_stack.append((label, ey))

            elif elem[0] == 'group_end':
                if group_stack:
                    label, start_y = group_stack.pop()
                    _, end_y = elem
                    self._draw_group(x_center - 70, start_y - 5, 140, end_y - start_y + 10, label)

        return current_y + 5

    def _draw_box(self, x, y, w, h, label, style='default'):
        """Draw a rounded box with label."""
        # Box fill
        if style == 'highlight':
            self.set_fill_color(*THEME['accent_color'])
            text_color = (255, 255, 255)
        else:
            self.set_fill_color(*THEME['box_fill'])
            text_color = THEME['title_color']

        # Draw rounded rectangle
        self.set_draw_color(*THEME['box_border'])
        self.set_line_width(0.8)

        # Simple rectangle (fpdf2 doesn't have built-in rounded rect)
        self.rect(x, y, w, h, 'FD')

        # Label
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(*text_color)
        self.set_xy(x, y + (h - 5) / 2)
        self.cell(w, 5, label, align='C')

        # Reset
        self.set_text_color(*THEME['text_color'])

    def _draw_arrow(self, x, y, direction, length):
        """Draw an arrow."""
        self.set_draw_color(*THEME['arrow_color'])
        self.set_line_width(0.8)

        if direction == 'down':
            self.line(x, y, x, y + length - 3)
            # Arrow head
            self.line(x, y + length, x - 3, y + length - 5)
            self.line(x, y + length, x + 3, y + length - 5)
        elif direction == 'up':
            self.line(x, y + length, x, y + 3)
            self.line(x, y, x - 3, y + 5)
            self.line(x, y, x + 3, y + 5)

    def _draw_group(self, x, y, w, h, label):
        """Draw a group container."""
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.5)
        self.rect(x, y, w, h, 'D')

        # Group label
        self.set_font('Helvetica', '', 9)
        self.set_text_color(120, 120, 120)
        self.set_xy(x + 3, y + 2)
        self.cell(0, 4, label)
        self.set_text_color(*THEME['text_color'])

def parse_markdown(content):
    """Parse markdown into slides."""
    slides = []
    presentation_title = None

    # Split by ## headers (slide markers)
    sections = re.split(r'\n(?=## )', content)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Check for presentation title (# Title)
        title_match = re.match(r'^# (.+?)(?:\n|$)', section)
        if title_match and presentation_title is None:
            presentation_title = title_match.group(1).strip()
            # Remove title from section
            section = re.sub(r'^# .+?\n', '', section).strip()
            if not section:
                continue

        # Parse slide header (## N. Title or ## Title)
        slide_match = re.match(r'^## (?:\d+\.\s*)?(.+?)(?:\n|$)', section)
        if slide_match:
            slide_title = slide_match.group(1).strip()
            # Get content after the header
            slide_content = re.sub(r'^## .+?\n', '', section).strip()
            slides.append({
                'title': slide_title,
                'content': slide_content
            })

    return presentation_title, slides

# Read input file
with open(input_file, 'r', encoding='utf-8') as f:
    markdown_content = f.read()

# Parse markdown
presentation_title, slides = parse_markdown(markdown_content)

if not slides:
    print("Error: No slides found. Make sure your markdown has ## headers for each slide.")
    sys.exit(1)

# Create PDF
pdf = SlidesPDF()

# Add title slide if we have a presentation title
if presentation_title:
    pdf.add_title_slide(presentation_title)

# Add content slides
for slide in slides:
    pdf.add_content_slide(slide['title'], slide['content'])

# Save PDF
pdf.output(output_file)

print(f"Generated {len(slides)} slides")
print(f"Output: {output_file}")
PYTHON_SCRIPT

echo ""
echo "PDF generation complete!"
echo "Output: $OUTPUT"
