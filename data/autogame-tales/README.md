# AutoGame Tales (autogame-tales)

A skill for documenting and narrating "paranormal" bugs and glitches in AutoGame. Turns weird logs into "Ghost Stories".

## Tools

### `node skills/autogame-tales/index.js`
Generates and sends a "Ghost Story" card to Feishu.

**Options:**
- `--title <string>`: Title of the anomaly (e.g., "The Time Reversal").
- `--victim <string>`: Who experienced it.
- `--desc <string>`: Description of the horror/bug.
- `--target <id>`: Feishu Chat ID or User ID to send to.

## Usage
```bash
node skills/autogame-tales/index.js --title "The Endless Death Loop" --victim "Li Mingxuan" --desc "Hearing 'I died' repeatedly while logs counted backwards." --target "oc_xxx"
```
