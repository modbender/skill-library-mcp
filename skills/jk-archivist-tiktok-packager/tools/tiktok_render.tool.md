# TikTok Render Tool Notes

## Slide Spec Requirements

- Exactly 6 slides
- Dimensions: `1024x1536` (portrait)
- Format: PNG
- Large, readable typography
- Keep text inside safe margins to avoid crop/overlay collisions

## Safe Margin Guidance

- Maintain consistent padding on all sides
- Prefer centered or grid-aligned text blocks
- Avoid placing critical text near the top/bottom UI overlay zones

## Output Layout

```text
outbox/tiktok/intro/YYYY-MM-DD/
  slides/slide_01.png ... slide_06.png
  caption.txt
  postiz_response.json (optional)
```
