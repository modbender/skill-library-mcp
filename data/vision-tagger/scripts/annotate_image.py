#!/usr/bin/env python3
"""
annotate_image.py - Draw detection results on images
Uses image_tagger output to annotate photos with boxes and labels
"""

import json
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = Path(__file__).parent
TAGGER_BIN = SCRIPT_DIR / "image_tagger"

# Colors for different detection types (R, G, B)
COLORS = {
    'face': (0, 255, 0),       # Green
    'body': (255, 165, 0),     # Orange
    'hand': (255, 0, 255),     # Magenta
    'text': (0, 255, 255),     # Cyan
    'object': (255, 255, 0),   # Yellow
    'barcode': (255, 0, 0),    # Red
    'label': (255, 255, 255),  # White
    'saliency': (128, 128, 255), # Light blue
}

def get_font(size=20):
    """Try to get a nice font, fall back to default"""
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for fp in font_paths:
        try:
            return ImageFont.truetype(fp, size)
        except:
            pass
    return ImageFont.load_default()

def denormalize_bbox(bbox, width, height):
    """Convert normalized (0-1) bbox to pixel coordinates"""
    # Vision uses bottom-left origin, PIL uses top-left
    x = int(bbox['x'] * width)
    y = int((1 - bbox['y'] - bbox['height']) * height)  # Flip Y
    w = int(bbox['width'] * width)
    h = int(bbox['height'] * height)
    return (x, y, x + w, y + h)

def draw_box(draw, bbox, width, height, color, label, font):
    """Draw a bounding box with label"""
    coords = denormalize_bbox(bbox, width, height)
    
    # Draw box
    draw.rectangle(coords, outline=color, width=3)
    
    # Draw label background
    text_bbox = draw.textbbox((0, 0), label, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    label_x = coords[0]
    label_y = coords[1] - text_h - 4
    if label_y < 0:
        label_y = coords[3] + 2
    
    draw.rectangle([label_x, label_y, label_x + text_w + 6, label_y + text_h + 4], fill=color)
    draw.text((label_x + 3, label_y + 2), label, fill=(0, 0, 0), font=font)

def draw_joints(draw, joints, width, height, color):
    """Draw body/hand pose joints"""
    points = []
    for name, joint in joints.items():
        if joint['confidence'] > 0.3:
            x = int(joint['x'] * width)
            y = int((1 - joint['y']) * height)  # Flip Y
            points.append((x, y, name))
            # Draw joint point
            draw.ellipse([x-4, y-4, x+4, y+4], fill=color, outline=(0,0,0))
    return points

def annotate_image(image_path, output_path=None):
    """Run tagger and annotate the image"""
    image_path = Path(image_path)
    
    if output_path is None:
        output_path = image_path.parent / f"{image_path.stem}_annotated{image_path.suffix}"
    else:
        output_path = Path(output_path)
    
    # Run tagger
    result = subprocess.run(
        [str(TAGGER_BIN), str(image_path)],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        print(f"Tagger failed: {result.stderr}", file=sys.stderr)
        return None
    
    # Parse JSON (skip any debug output before the JSON)
    output = result.stdout
    json_start = output.find('{')
    if json_start == -1:
        print("No JSON in tagger output", file=sys.stderr)
        return None
    
    tags = json.loads(output[json_start:])
    
    # Load image
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    font = get_font(18)
    font_small = get_font(14)
    
    # Draw saliency regions (background, subtle)
    if tags.get('saliency'):
        for bbox in tags['saliency'].get('attentionBased', []):
            coords = denormalize_bbox(bbox, width, height)
            draw.rectangle(coords, outline=COLORS['saliency'], width=2)
    
    # Draw rectangles/objects
    for obj in tags.get('objects', []):
        draw_box(draw, obj['bbox'], width, height, COLORS['object'], 
                 f"{obj['label']} ({obj['confidence']:.0%})", font_small)
    
    # Draw faces
    for i, face in enumerate(tags.get('faces', [])):
        label = f"face {i+1}"
        if face.get('roll') is not None:
            label += f" (roll:{face['roll']:.0f}°)"
        draw_box(draw, face['bbox'], width, height, COLORS['face'], label, font)
    
    # Draw bodies
    for i, body in enumerate(tags.get('bodies', [])):
        if body.get('joints'):
            draw_joints(draw, body['joints'], width, height, COLORS['body'])
    
    # Draw hands
    for hand in tags.get('hands', []):
        if hand.get('joints'):
            color = (255, 100, 100) if hand['chirality'] == 'left' else (100, 255, 100)
            draw_joints(draw, hand['joints'], width, height, color)
    
    # Draw text regions
    for text in tags.get('text', []):
        label = text['text'][:30] + ('...' if len(text['text']) > 30 else '')
        draw_box(draw, text['bbox'], width, height, COLORS['text'], label, font_small)
    
    # Draw barcodes
    for barcode in tags.get('barcodes', []):
        label = f"{barcode['symbology']}: {barcode['payload'][:20]}"
        draw_box(draw, barcode['bbox'], width, height, COLORS['barcode'], label, font_small)
    
    # Draw labels in corner
    labels = tags.get('labels', [])
    if labels:
        label_text = "Scene: " + ", ".join([f"{l['label']} ({l['confidence']:.0%})" for l in labels[:5]])
        text_bbox = draw.textbbox((0, 0), label_text, font=font_small)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        
        # Background
        draw.rectangle([10, height - text_h - 20, text_w + 20, height - 10], fill=(0, 0, 0, 180))
        draw.text((15, height - text_h - 15), label_text, fill=COLORS['label'], font=font_small)
    
    # Save
    img.save(output_path, quality=95)
    print(f"Saved: {output_path}")
    
    # Return summary
    summary = {
        'output': str(output_path),
        'faces': len(tags.get('faces', [])),
        'bodies': len(tags.get('bodies', [])),
        'hands': len(tags.get('hands', [])),
        'text_regions': len(tags.get('text', [])),
        'objects': len(tags.get('objects', [])),
        'labels': [l['label'] for l in labels[:5]],
    }
    return summary

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: annotate_image.py <image_path> [output_path]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = annotate_image(image_path, output_path)
    if result:
        print(json.dumps(result, indent=2))
