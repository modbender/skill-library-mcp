"""
FIS 3.1 Lite - Badge Image Generator
工卡图片生成器 (支持批量生成)
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Paths
SKILL_DIR = Path(__file__).parent.parent
TEMPLATE_PATH = SKILL_DIR / "lib" / "badge_template.html"
OUTPUT_DIR = Path.home() / ".openclaw" / "output" / "badges"

def load_template() -> str:
    """Load HTML template"""
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        return f.read()

def render_badge_html(card: dict) -> str:
    """Render single badge HTML from card data"""
    template = load_template()
    
    # Role styling
    role_class = f"role-{card['role']}"
    role_display = card['role'].upper()
    
    # Status styling
    status_class = f"status-{card['status']}"
    status_dot_class = f"status-{card['status']}"
    status_display = card['status'].upper()
    
    # Emoji by role
    emoji_map = {
        'worker': '🔧',
        'reviewer': '👁️',
        'researcher': '🔬',
        'formatter': '🎨'
    }
    emoji = emoji_map.get(card['role'], '🤖')
    
    # Parse deadline
    deadline = card['task']['deadline'][:16].replace('T', ' ')
    
    # Permissions
    perms = card['permissions']
    perm_icons = {
        'read': '✓' if perms.get('can_read_shared_hub') else '✗',
        'write': '✓' if perms.get('can_write_shared_hub') else '✗',
        'call': '✓' if perms.get('can_call_other_agents') else '✗',
        'ticket': '✓' if perms.get('can_modify_tickets') else '✗'
    }
    
    # Replace template variables
    html = template
    html = re.sub(r'CYBERMAO-SA-2026-0001', card['employee_id'], html)
    html = re.sub(r'小毛-Worker-001', card['name'], html)
    html = re.sub(r'role-worker', role_class, html)
    html = re.sub(r'Worker</span>', f'{role_display}</span>', html)
    html = re.sub(r'status-active', status_class, html)
    html = re.sub(r'status-dot status-active', f'status-dot {status_dot_class}', html)
    html = re.sub(r'ACTIVE', status_display, html)
    html = re.sub(r'🤖', emoji, html)
    html = re.sub(r'cybermao', card['parent'], html)
    html = re.sub(r'2026-02-17 22:48', deadline, html)
    
    # Permissions
    html = re.sub(r'>✓</span>\s*<span>Read Shared Hub', f">{perm_icons['read']}</span><span>Read Shared Hub", html)
    html = re.sub(r'>✗</span>\s*<span>Write \(via Parent\)', f">{perm_icons['write']}</span><span>Write (via Parent)", html)
    html = re.sub(r'>✗</span>\s*<span>Call Other Agents', f">{perm_icons['call']}</span><span>Call Other Agents", html)
    html = re.sub(r'>✗</span>\s*<span>Modify Tickets', f">{perm_icons['ticket']}</span><span>Modify Tickets", html)
    
    return html

def generate_multi_badge_html(cards: list) -> str:
    """Render multiple badges in one HTML (grid layout)"""
    # Load template and extract CSS
    template = load_template()
    css_match = re.search(r'<style>(.*?)</style>', template, re.DOTALL)
    css = css_match.group(1) if css_match else ""
    
    # Generate each badge HTML
    badge_divs = []
    for card in cards:
        single_html = render_badge_html(card)
        # Extract just the badge div
        badge_match = re.search(r'(<div class="badge".*?</div>)', single_html, re.DOTALL)
        if badge_match:
            badge_divs.append(badge_match.group(1))
    
    # Combine in grid layout
    multi_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
{css}
.badge-container {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    padding: 20px;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    min-height: 100vh;
}}
.badge {{
    margin: 0;
}}
@media (max-width: 900px) {{
    .badge-container {{
        grid-template-columns: 1fr;
    }}
}}
</style>
</head>
<body>
<div class="badge-container">
    {''.join(badge_divs)}
</div>
</body>
</html>"""
    
    return multi_html

def save_badge_html(cards: list, output_name: str = None) -> Path:
    """Save badge HTML to file"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    if output_name is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"badges_{timestamp}.html"
    
    output_path = OUTPUT_DIR / output_name
    
    if isinstance(cards, dict):
        cards = [cards]
    
    if len(cards) == 1:
        html = render_badge_html(cards[0])
    else:
        html = generate_multi_badge_html(cards)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path

# Canvas integration for OpenClaw
def generate_badge_image(cards: list, output_name: str = None) -> str:
    """
    Generate badge image using OpenClaw canvas
    
    Usage:
        # Single card
        image_path = generate_badge_image(card, "worker_badge.png")
        
        # Multiple cards (grid layout)
        image_path = generate_badge_image([card1, card2, card3], "team_badges.png")
    
    Returns:
        Path to generated image (relative for messaging)
    """
    # Save HTML first
    html_path = save_badge_html(cards, output_name.replace('.png', '.html') if output_name else None)
    
    # Return HTML path - will be rendered by canvas
    return str(html_path)

# CLI interface
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from subagent_lifecycle import SubAgentLifecycleManager
    
    print("🎫 FIS 3.1 Badge Image Generator")
    print("=" * 50)
    
    # Load existing subagents
    from fis_config import get_shared_hub_path
    registry_file = get_shared_hub_path() / ".fis3.1" / "subagent_registry.json"
    
    if registry_file.exists():
        with open(registry_file) as f:
            registry = json.load(f)
        
        subagents = registry.get("subagents", [])
        
        if subagents:
            print(f"\nFound {len(subagents)} subagent(s)")
            
            # Generate multi-badge HTML
            html_path = save_badge_html(subagents, "all_badges.html")
            print(f"\n✅ Multi-badge HTML saved: {html_path}")
            
            # Also generate individual badges
            for card in subagents[:2]:  # Limit to first 2 for demo
                single_path = save_badge_html(card, f"badge_{card['employee_id']}.html")
                print(f"✅ Single badge: {single_path.name}")
            
            print("\n💡 To generate image, use OpenClaw canvas:")
            print(f"   canvas snapshot --url file://{html_path}")
        else:
            print("\n⚠️  No subagents found. Create one first:")
            print("   python3 -m subagent_lifecycle")
    else:
        print("\n⚠️  Registry not found. Initialize FIS 3.1 first.")
