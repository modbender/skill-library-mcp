---
name: bento-grid
description: Generate beautiful bento grid layouts for social media posts. Create Instagram/Twitter cards with statistics, calendars, music visualization, and custom layouts.
metadata:
  openclaw:
    requires:
      bins: [python3]
      pip: [Pillow]
---

# Bento Grid Generator

Generate beautiful bento-style grid layouts for social media (Twitter/X, Instagram, LinkedIn).

## When to Use

- User wants to create "bento" style social media posts
- User wants to visualize statistics, calendars, or data as cards
- User wants to create music listening cards (Spotify-style)
- User wants to create aesthetic grid layouts

## Commands

### create-bento-grid

Generate a bento grid with customizable cells.

```bash
python3 -c "
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random

def create_bento():
    w, h = 1200, 1200
    bg = (15, 15, 20)
    img = Image.new('RGB', (w, h), bg)
    draw = ImageDraw.Draw(img)
    
    cells = [
        {'r':0,'c':0,'rs':2,'cs':2,'clr':(255,99,71),'txt':'2024'},
        {'r':0,'c':2,'rs':1,'cs':1,'clr':(100,149,237),'txt':'Q1'},
        {'r':1,'c':2,'rs':1,'cs':1,'clr':(144,238,144),'txt':'Q2'},
        {'r':0,'c':3,'rs':2,'cs':1,'clr':(255,218,185),'txt':'Goals'},
        {'r':2,'c':0,'rs':1,'cs':2,'clr':(221,160,221),'txt':'Q3'},
        {'r':2,'c':2,'rs':1,'cs':2,'clr':(175,238,238),'txt':'Q4'},
    ]
    
    gap, cr = 10, 20
    cw = (w - gap*5) / 4
    ch = (h - gap*5) / 3
    
    for c in cells:
        x = c['c']*(cw+gap) + gap
        y = c['r']*(ch+gap) + gap
        wdt = c['cs']*cw + (c['cs']-1)*gap
        hgt = c['rs']*ch + (c['rs']-1)*gap
        draw.rounded_rectangle([x, y, x+wdt, y+hgt], radius=cr, fill=c['clr'])
        
        try: font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 36)
        except: font = ImageFont.load_default()
        bbox = draw.textbbox((0,0), c['txt'], font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text((x+(wdt-tw)/2, y+(hgt-th)/2), c['txt'], fill=(255,255,255), font=font)
    
    img.save('/tmp/bento_grid.png')
    print('Created: /tmp/bento_grid.png')

create_bento()
"
```

### create-stats-card

Create a statistics card with customizable metrics.

```bash
python3 -c "
from PIL import Image, ImageDraw, ImageFont

def stats_card():
    w, h = 800, 400
    img = Image.new('RGB', (w, h), (30, 30, 40))
    draw = ImageDraw.Draw(img)
    
    try:
        tf = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 28)
        vf = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 36)
        lf = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 16)
    except:
        tf = vf = lf = ImageFont.load_default()
    
    draw.text((30, 30), 'My Stats', fill=(255,255,255), font=tf)
    
    metrics = [('Followers','12.5K'),('Posts','248'),('Likes','45.2K')]
    for i,(lbl,val) in enumerate(metrics):
        x = 30 + i * 250
        draw.rounded_rectangle([x,80,x+220,h-30], radius=15, fill=(50,50,65))
        draw.text((x+20, 100), val, fill=(255,255,255), font=vf)
        draw.text((x+20, 160), lbl, fill=(180,180,180), font=lf)
    
    img.save('/tmp/stats_card.png')
    print('Created: /tmp/stats_card.png')

stats_card()
"
```

### create-music-card

Create a Spotify-style music listening card.

```bash
python3 -c "
from PIL import Image, ImageDraw, ImageFont

def music_card():
    w, h = 600, 200
    img = Image.new('RGB', (w, h), (30, 30, 35))
    draw = ImageDraw.Draw(img)
    
    for i in range(h):
        draw.line([(0,i),(w,i)], fill=(30+i//5,30+i//2,35+i//3))
    
    draw.rounded_rectangle([20,20,160,180], radius=10, fill=(80,80,100))
    draw.text((60,80), '♪', fill=(200,200,200))
    
    try:
        tf = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 24)
        af = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
    except: tf = af = ImageFont.load_default()
    
    draw.text((190, 50), 'Song Title', fill=(255,255,255), font=tf)
    draw.text((190, 90), 'Artist Name', fill=(180,180,180), font=af)
    draw.rounded_rectangle([190,150,500,155], radius=2, fill=(80,80,90))
    draw.rounded_rectangle([190,150,350,155], radius=2, fill=(0,200,100))
    
    img.save('/tmp/music_card.png')
    print('Created: /tmp/music_card.png')

music_card()
"
```

## Output

All images saved to /tmp/: bento_grid.png, stats_card.png, music_card.png

## Notes

- Optimized for Twitter/X (1200x1200 works best)
- Use gradients and rounded corners for modern aesthetic
