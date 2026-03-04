# skill-quick-index

A ClawHub skill for **broad-trigger + precise-call** skill routing.

## Install

- Put under `~/.openclaw/workspace/skills/skill-quick-index/`

## Run

```bash
python3 scripts/skill_lookup.py "你的需求"
```

## Example

```bash
python3 scripts/skill_lookup.py "帮我打开网页并截图"
python3 scripts/skill_lookup.py "识别这张图片文字"
python3 scripts/skill_lookup.py "启动codingteam分配任务"
```

## Notes

- Works best with a maintained `index/skill_index.json`
- You can extend category keywords for your own domain
