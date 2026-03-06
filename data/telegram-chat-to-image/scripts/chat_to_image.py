#!/usr/bin/env python3
"""
Telegram Chat to Image Generator
Converts Telegram chat messages into a long screenshot-style image.
"""

import json
import argparse
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from typing import List, Dict, Optional, Tuple


class ChatRenderer:
    """Renders Telegram chat messages as a long image."""
    
    # Colors (RGB)
    BG_COLOR = (255, 255, 255)
    MY_BUBBLE_COLOR = (0, 132, 255)  # iOS blue
    OTHER_BUBBLE_COLOR = (230, 230, 230)  # Light gray
    MY_TEXT_COLOR = (255, 255, 255)
    OTHER_TEXT_COLOR = (0, 0, 0)
    TIME_COLOR = (142, 142, 147)
    NAME_COLOR = (0, 132, 255)
    AVATAR_BG = (200, 200, 200)
    AVATAR_TEXT = (100, 100, 100)
    
    # Layout
    WIDTH = 800
    MARGIN = 20
    BUBBLE_PADDING = 12
    BUBBLE_RADIUS = 16
    AVATAR_SIZE = 40
    LINE_SPACING = 6
    MESSAGE_SPACING = 8
    GROUP_SPACING = 16
    
    def __init__(self, font_path: Optional[str] = None, my_id: Optional[str] = None):
        self.width = self.WIDTH
        self.margin = self.MARGIN
        self.my_id = my_id  # e.g., "user1" or "Me"
        
        # Fonts
        self.font_size = 15
        self.name_font_size = 13
        self.time_font_size = 11
        
        font_candidates = [
            font_path,
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        
        font_path = None
        for c in font_candidates:
            if c and os.path.exists(c):
                font_path = c
                break
        
        try:
            if font_path:
                self.font = ImageFont.truetype(font_path, self.font_size)
                self.name_font = ImageFont.truetype(font_path, self.name_font_size)
                self.time_font = ImageFont.truetype(font_path, self.time_font_size)
            else:
                raise IOError("No font")
        except:
            self.font = ImageFont.load_default()
            self.name_font = self.font
            self.time_font = self.font
    
    def wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text handling newlines and Chinese characters."""
        paragraphs = text.split("\n")
        all_lines = []
        
        for para in paragraphs:
            if not para.strip():
                all_lines.append("")
                continue
            
            lines = []
            current = ""
            
            for char in para:
                test = current + char
                bbox = self.font.getbbox(test)
                w = bbox[2] - bbox[0] if bbox else len(test) * 8
                
                if w <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = char
            
            if current:
                lines.append(current)
            all_lines.extend(lines)
        
        return all_lines if all_lines else [text]
    
    def calc_height(self, text: str, is_first: bool) -> int:
        max_w = self.width - (self.margin * 2) - (self.BUBBLE_PADDING * 2) - self.AVATAR_SIZE - 10
        lines = self.wrap_text(text, max_w)
        lh = self.font_size + self.LINE_SPACING
        h = len(lines) * lh + (self.BUBBLE_PADDING * 2)
        if is_first:
            h += self.name_font_size + 4
        return h
    
    def draw_msg(self, draw: ImageDraw.Draw, y: int, msg: Dict, is_me: bool, is_first: bool) -> int:
        text = msg.get("text", "")
        sender = msg.get("from", "Unknown")
        ts = msg.get("date", "")
        
        time_str = ""
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                time_str = dt.strftime("%H:%M")
            except:
                pass
        
        max_w = self.width - (self.margin * 2) - (self.BUBBLE_PADDING * 2) - self.AVATAR_SIZE - 10
        lines = self.wrap_text(text, max_w)
        lh = self.font_size + self.LINE_SPACING
        txt_h = len(lines) * lh
        
        bubble_h = txt_h + (self.BUBBLE_PADDING * 2)
        if is_first:
            bubble_h += self.name_font_size + 4
        
        if is_me:
            bubble_color = self.MY_BUBBLE_COLOR
            txt_color = self.MY_TEXT_COLOR
            name_color = self.MY_TEXT_COLOR
        else:
            bubble_color = self.OTHER_BUBBLE_COLOR
            txt_color = self.OTHER_TEXT_COLOR
            name_color = self.NAME_COLOR
        
        if is_me:
            bubble_x = self.width - self.margin - max_w - (self.BUBBLE_PADDING * 2) - 10
        else:
            bubble_x = self.margin + self.AVATAR_SIZE + 10
        
        # Avatar for others
        if not is_me and is_first:
            ay = y
            ax = self.margin
            draw.ellipse([ax, ay, ax + self.AVATAR_SIZE, ay + self.AVATAR_SIZE], fill=self.AVATAR_BG)
            init = sender[0].upper() if sender else "?"
            bbox = self.font.getbbox(init)
            tw = bbox[2] - bbox[0] if bbox else 10
            th = bbox[3] - bbox[1] if bbox else 10
            draw.text((ax + self.AVATAR_SIZE//2 - tw//2, ay + self.AVATAR_SIZE//2 - th//2), 
                     init, fill=self.AVATAR_TEXT, font=self.font)
        
        # Bubble
        bubble_w = max_w + (self.BUBBLE_PADDING * 2)
        draw.rounded_rectangle(
            (bubble_x, y, bubble_x + bubble_w, y + bubble_h),
            radius=self.BUBBLE_RADIUS, fill=bubble_color
        )
        
        # Text
        ty = y + self.BUBBLE_PADDING
        if is_first and not is_me:
            draw.text((bubble_x + self.BUBBLE_PADDING, ty), sender, fill=name_color, font=self.name_font)
            ty += self.name_font_size + 4
        elif is_first and is_me:
            ty += self.name_font_size + 4
        
        for line in lines:
            draw.text((bubble_x + self.BUBBLE_PADDING, ty), line, fill=txt_color, font=self.font)
            ty += lh
        
        # Time
        if time_str:
            tb = self.time_font.getbbox(time_str)
            tw = tb[2] - tb[0] if tb else 30
            draw.text((bubble_x + bubble_w - tw - 8, y + bubble_h - 16), time_str, 
                     fill=self.TIME_COLOR, font=self.time_font)
        
        return y + bubble_h + self.MESSAGE_SPACING
    
    def render(self, messages: List[Dict], output: str, my_id: Optional[str] = None):
        if not messages:
            print("No messages")
            return
        
        if my_id:
            self.my_id = my_id
        
        # Auto-detect "me" as first sender if not set
        if not self.my_id and messages:
            self.my_id = messages[0].get("from_id")
        
        total_h = self.margin * 2
        curr = None
        for msg in messages:
            is_first = (msg.get("from") != curr)
            total_h += self.calc_height(msg.get("text", ""), is_first)
            if is_first:
                total_h += self.GROUP_SPACING - self.MESSAGE_SPACING
            curr = msg.get("from")
        total_h += self.margin
        
        img = Image.new("RGB", (self.width, total_h), self.BG_COLOR)
        draw = ImageDraw.Draw(img)
        
        y = self.margin
        curr = None
        for msg in messages:
            is_me = (msg.get("from_id") == self.my_id or msg.get("from") == self.my_id)
            is_first = (msg.get("from") != curr)
            y = self.draw_msg(draw, y, msg, is_me, is_first)
            if is_first:
                y += self.GROUP_SPACING - self.MESSAGE_SPACING
            curr = msg.get("from")
        
        img.save(output, "PNG", quality=95)
        print(f"Saved: {output}")


def load_json(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    msgs = []
    for m in data.get("messages", []):
        if m.get("type") == "message":
            text = m.get("text", "")
            if isinstance(text, list):
                text = "".join(x if isinstance(x, str) else x.get("text", "") for x in text)
            msgs.append({
                "id": m.get("id"),
                "from": m.get("from", "Unknown"),
                "from_id": m.get("from_id", ""),
                "date": m.get("date", ""),
                "text": text,
            })
    return msgs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", required=True)
    p.add_argument("--output", "-o", default="chat.png")
    p.add_argument("--font", "-f")
    p.add_argument("--limit", "-l", type=int)
    p.add_argument("--me", "-m", help="Your from_id or name (e.g., user123 or Me)")
    args = p.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Not found: {args.input}")
        sys.exit(1)
    
    msgs = load_json(args.input)
    if args.limit:
        msgs = msgs[:args.limit]
    print(f"Loaded {len(msgs)} messages")
    
    r = ChatRenderer(font_path=args.font, my_id=args.me)
    r.render(msgs, args.output, my_id=args.me)


if __name__ == "__main__":
    main()
