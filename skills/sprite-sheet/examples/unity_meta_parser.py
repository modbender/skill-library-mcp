#!/usr/bin/env python3
"""
Unity .meta File Sprite Sheet Parser
Extracts sprite coordinate information from Unity TextureImporter .meta files
"""

import yaml
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional


def parse_meta_file(meta_path: str) -> Optional[Dict]:
    """Parse Unity .meta file and extract sprite information"""
    try:
        with open(meta_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if 'TextureImporter' not in data:
            print(f"Warning: No TextureImporter section found in {meta_path}", file=sys.stderr)
            return None
        
        texture_importer = data['TextureImporter']
        sprite_mode = texture_importer.get('spriteMode', 1)
        
        # spriteMode: 1=Single, 2=Multiple, 3=Polygon
        if sprite_mode != 2:
            print(f"Warning: spriteMode is {sprite_mode} (not Multiple/2), no sprite sheet", file=sys.stderr)
            return None
        
        sprite_sheet = texture_importer.get('spriteSheet', {})
        sprites = sprite_sheet.get('sprites', [])
        
        if not sprites:
            print(f"Warning: No sprites found in spriteSheet section", file=sys.stderr)
            return None
        
        result = {
            'meta_file': str(meta_path),
            'sprite_count': len(sprites),
            'pixels_per_unit': texture_importer.get('spritePixelsToUnits', 100),
            'sprites': []
        }
        
        for sprite in sprites:
            rect = sprite.get('rect', {})
            pivot = sprite.get('pivot', {})
            border = sprite.get('border', {})
            
            sprite_info = {
                'name': sprite.get('name', 'unnamed'),
                'x': rect.get('x', 0),
                'y': rect.get('y', 0),
                'width': rect.get('width', 0),
                'height': rect.get('height', 0),
                'pivot': {
                    'x': pivot.get('x', 0.5),
                    'y': pivot.get('y', 0.5)
                },
                'alignment': sprite.get('alignment', 0),
                'internal_id': sprite.get('internalID', 0)
            }
            
            # Include border if non-zero (for 9-slice sprites)
            border_values = [border.get(k, 0) for k in ['x', 'y', 'z', 'w']]
            if any(border_values):
                sprite_info['border'] = {
                    'left': border.get('x', 0),
                    'bottom': border.get('y', 0),
                    'right': border.get('z', 0),
                    'top': border.get('w', 0)
                }
            
            result['sprites'].append(sprite_info)
        
        # Check for grid slicing metadata
        custom_meta = sprite_sheet.get('spriteCustomMetadata', {})
        entries = custom_meta.get('entries', [])
        for entry in entries:
            if entry.get('key') == 'SpriteEditor.SliceSettings':
                try:
                    slice_settings = json.loads(entry.get('value', '{}'))
                    result['slice_settings'] = {
                        'grid_cell_count': slice_settings.get('gridCellCount', {}),
                        'grid_sprite_size': slice_settings.get('gridSpriteSize', {}),
                        'grid_sprite_offset': slice_settings.get('gridSpriteOffset', {}),
                        'grid_sprite_padding': slice_settings.get('gridSpritePadding', {}),
                        'slicing_type': slice_settings.get('slicingType', 1)
                    }
                except json.JSONDecodeError:
                    pass
        
        return result
        
    except Exception as e:
        print(f"Error parsing {meta_path}: {e}", file=sys.stderr)
        return None


def format_rust_struct(sprite_data: Dict) -> str:
    """Format sprite data as Rust struct initialization code"""
    sprites = sprite_data['sprites']
    
    rust_code = f"// Auto-generated from: {sprite_data['meta_file']}\n"
    rust_code += f"// Total sprites: {sprite_data['sprite_count']}\n"
    rust_code += f"// Pixels per unit: {sprite_data['pixels_per_unit']}\n\n"
    
    rust_code += "pub const SPRITE_FRAMES: &[SpriteFrame] = &[\n"
    
    for sprite in sprites:
        rust_code += f"    SpriteFrame {{\n"
        rust_code += f"        name: \"{sprite['name']}\",\n"
        rust_code += f"        x: {sprite['x']},\n"
        rust_code += f"        y: {sprite['y']},\n"
        rust_code += f"        width: {sprite['width']},\n"
        rust_code += f"        height: {sprite['height']},\n"
        rust_code += f"        pivot_x: {sprite['pivot']['x']},\n"
        rust_code += f"        pivot_y: {sprite['pivot']['y']},\n"
        rust_code += f"    }},\n"
    
    rust_code += "];\n\n"
    
    rust_code += """// Example struct definition:
// #[derive(Debug, Clone)]
// pub struct SpriteFrame {
//     pub name: &'static str,
//     pub x: i32,
//     pub y: i32,
//     pub width: i32,
//     pub height: i32,
//     pub pivot_x: f32,
//     pub pivot_y: f32,
// }
"""
    
    return rust_code


def main():
    if len(sys.argv) < 2:
        print("Usage: unity_meta_parser.py <meta_file.meta> [--json|--rust]", file=sys.stderr)
        print("\nOptions:", file=sys.stderr)
        print("  --json    Output as JSON (default)", file=sys.stderr)
        print("  --rust    Output as Rust code", file=sys.stderr)
        sys.exit(1)
    
    meta_file = sys.argv[1]
    output_format = 'json'
    
    if len(sys.argv) > 2:
        if sys.argv[2] == '--rust':
            output_format = 'rust'
        elif sys.argv[2] == '--json':
            output_format = 'json'
    
    if not Path(meta_file).exists():
        print(f"Error: File not found: {meta_file}", file=sys.stderr)
        sys.exit(1)
    
    result = parse_meta_file(meta_file)
    
    if result is None:
        sys.exit(1)
    
    if output_format == 'rust':
        print(format_rust_struct(result))
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
