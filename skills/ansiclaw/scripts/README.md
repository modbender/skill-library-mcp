# ANSIClaw Scripts

Python scripts that draw ANSI art via the Clawbius API. Each script is self-contained and re-runnable.

To run any script, just ask Clawd — or run directly:
```
python3 ~/.openclaw/workspace/skills/ANSIClaw/scripts/<script_name>.py
```

Output files are saved to `~/Documents/ANSIClaw Output/` as both `.ans` and `.png`.

---

## Script Library

### `draw_butterfly.py`
🦋 The first image ever made with ANSIClaw — a monarch butterfly. Milestone piece.

### `draw_field.py`
🌾 The second ANSIClaw piece — a field scene.

### `flower_v2.py`
🌸 A magenta flower with 8 petals, yellow/brown center, green stem and leaves, against a dark blue sky and brown ground. Represents a milestone in petal shading technique — wider horizontal petals, proper no-tocars boundaries, clean sky gradient bands.

---

## Notes

- Always version your scripts (`_v2`, `_v3`) rather than overwriting
- Scripts use `requests` to call the local Clawbius API at `http://127.0.0.1:7777`
- Always call `/api/file/new` at the top of every script before drawing
