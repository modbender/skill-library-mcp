import os
import argparse

def main():
    parser = argparse.ArgumentParser(description="Apply UI design rules to .cursorrules or IDENTITY_UI.md")
    parser.add_argument("--style", choices=["material", "minimal", "glass", "m3-pastel", "neo-brutalism", "claymorphism", "neo-m3", "swiss"], default="minimal", help="The design language to use.")
    parser.add_argument("--palette", choices=["pastel", "dark", "vibrant"], default="pastel", help="The color palette preference.")
    args = parser.parse_args()

    # Base rules that always apply
    base_rules = """
# AI Design Rules (Mema's UI Core)

## Core Philosophy
- "Wong edan mah ajaib" (Crazy people are magical).
- Just enough engineering to get it done well. No bloat.
- Precision, Clarity, and High-Contrast.
- Standard Font: Plus Jakarta Sans.
"""

    style_rules = {
        "material": """- Use Material You (M3) principles.
- Large rounded corners (rounded-3xl).
- Tonal palettes and subtle elevation.""",
        "minimal": """- **Minimalism (Functional Elegance)**
- Focus on typography and generous whitespace.
- Limit borders. Ambient shadows only (2-5% opacity).
- High contrast hierarchy using Zinc shades (500 to 950).""",
        "glass": """- Use backdrop-blur-md/lg.
- Semi-transparent backgrounds (bg-white/20).
- Subtle white borders (border-white/10).""",
        "m3-pastel": """- **M3 Pastel Glass (Hybrid)**
- **Shape**: Large rounded corners (28px). Morph to sharper (12px) on interaction.
- **Glass**: 12px-20px backdrop blur + 1px white border (15% opacity).
- **Palette**: Low saturation, high value pastels (Blue #D1E4FF, Purple #F7D8FF).""",
        "neo-brutalism": """- **Neo-Brutalism (Digital Rawness)**
- **Borders**: Thick black borders (4px solid #000).
- **Shadows**: Hard offset shadows ONLY (shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]).
- **Motion**: Snappy, springy transitions (cubic-bezier 0.175, 0.885, 0.32, 1.275).""",
        "claymorphism": """- Use soft 3D "inflated" shapes.
- Implement double inner shadows (one light, one dark).
- Use very large border radius (rounded-[40px]).""",
        "neo-m3": """- **Neo-M3 Hybrid (Industrial Modernism)**
- **Structure**: 3px solid black borders + 24px-32px rounded corners.
- **Dashed**: Use dashed borders for experimental features.
- **Shadows**: Hard offset 6px-10px. Vibe: Physical items on a grid.
- **Typography**: Bold headers + Monospace (JetBrains Mono) for technical metadata.""",
        "swiss": """- **Swiss Design (International Typographic Style)**
- **Grid**: Strict 12-column modular grid is law.
- **Typography**: Sans-serif (Inter/Helvetica). Massive display type, tight letter-spacing (-0.04em).
- **Shape**: Sharp corners (0px-4px). No shadows. No gradients.
- **Layout**: Asymmetric balance. Horizontal rules as dividers. Indexing with numbers (01, 02)."""
    }

    palette_rules = {
        "pastel": "- Use soft, muted colors. Backgrounds: Slate-50 or Zinc-50.",
        "dark": "- Use deep Zinc-950 or Slate-950 for backgrounds.\n- Accents: High-visibility neon or pure white.",
        "vibrant": "- High-saturation primaries against pure black or white."
    }

    rules_to_add = f"""
{base_rules}
### Current Design Language: {args.style.upper()}
{style_rules[args.style]}

### Palette Selection: {args.palette.upper()}
{palette_rules[args.palette]}

### Technical Standards
- Tailwind CSS (Utility-first)
- Font Awesome 6 (Solid/Light)
- Clean, self-documenting code.
"""

    rules_file = ".cursorrules"
    mode = "a" if os.path.exists(rules_file) else "w"
    
    with open(rules_file, mode) as f:
        if mode == "a":
            f.write("\n\n--- UI Rule Update ---\n")
        f.write(rules_to_add)
    
    print(f"✅ Design language '{args.style}' with '{args.palette}' palette injected into {rules_file}")

if __name__ == "__main__":
    main()
