# Youmind Skill Usage Patterns

## Always Use `run.py`

```bash
python scripts/run.py [script].py [args...]
```

## Pattern 1: Initial Setup

```bash
python scripts/run.py auth_manager.py status
python scripts/run.py auth_manager.py setup
python scripts/run.py board_manager.py add \
  --url "https://youmind.com/boards/..." \
  --name "Board name" \
  --description "What this board contains" \
  --topics "topic1,topic2"
```

## Pattern 1.5: Smart Add

```bash
# One-command Smart Add
python scripts/run.py board_manager.py smart-add \
  --url "https://youmind.com/boards/..."

# If needed, fallback to two-step manual discovery + add
python scripts/run.py ask_question.py \
  --question "请概括这个board的内容和主要主题" \
  --board-url "https://youmind.com/boards/..."
python scripts/run.py board_manager.py add \
  --url "https://youmind.com/boards/..." \
  --name "Meaningful board name" \
  --description "Discovered board description" \
  --topics "topic1,topic2"
```

## Pattern 2: Daily Query

```bash
python scripts/run.py board_manager.py list
python scripts/run.py ask_question.py --question "What changed this week?"
```

## Pattern 3: Explicit Board Selection

```bash
python scripts/run.py ask_question.py --question "Summarize decisions" --board-id product-roadmap
```

## Pattern 4: Follow-Up Loop

1. Ask base question.
2. Check whether answer fully covers user intent.
3. Ask targeted follow-up(s) with explicit context.
4. Synthesize all answers into final response.

## Pattern 5: Multi-Board Comparison

```bash
python scripts/run.py board_manager.py activate --id board-a
python scripts/run.py ask_question.py --question "Answer X"

python scripts/run.py board_manager.py activate --id board-b
python scripts/run.py ask_question.py --question "Answer X"
```

Then compare outputs.

## Pattern 6: Recovery

```bash
python scripts/run.py cleanup_manager.py --confirm --preserve-library
python scripts/run.py auth_manager.py reauth
```

## Pattern 7: Direct URL Query (No Library)

```bash
python scripts/run.py ask_question.py --question "Give me highlights" --board-url "https://youmind.com/boards/..."
```

This is useful for temporary one-off boards.
