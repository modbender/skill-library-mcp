# ANSIClaw Reference Files

This folder contains ANSI art provided by the author or user as style references. Use these as a guide for shading, composition, half-block technique, and color palette choices.

> **⛔ Do not modify these files.** They are the operators source material. Open them read-only via the API to analyze, then immediately create a new canvas before drawing anything. You can analyze them with a peekaboo screenshot also.

---

## Reference Library

Nothing here yet, describe some files

---

## How to Use These Files

1. Open the file via the API to load it into Clawbius
2. Read canvas data and analyze color/code distributions by region
3. Use the `image` tool to analyze the matching `.png` file visually — **do NOT use Peekaboo** (captures wrong window) -- if a PNG does not exist with the source .ANS, let the user know and that you can't do the image based analysis
4. **Immediately call `/api/file/new`** before drawing anything — do not draw on a reference canvas