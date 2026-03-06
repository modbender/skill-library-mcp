# Crunch CLI Reference

## Installation

```bash
pip install crunch-cli
```

## Setup Commands

| Command | Description |
|---------|-------------|
| `crunch setup <competition> <project> --token <TOKEN>` | Set up workspace with quickstarter |
| `crunch setup <competition> <project> --token <TOKEN> --notebook` | Set up notebook workspace |
| `crunch setup <competition> <project> --token <TOKEN> --quickstarter-name "Name"` | Pre-select quickstarter |
| `crunch setup <competition> <project> --token <TOKEN> --no-data` | Skip data download |

## Data Commands

| Command | Description |
|---------|-------------|
| `crunch download` | Download competition data |
| `crunch download --force` | Re-download data |
| `crunch download --size-variant small` | Download smaller dataset |

## Quickstarter Commands

| Command | Description |
|---------|-------------|
| `crunch quickstarter` | Interactive quickstarter selection |
| `crunch quickstarter --name "Name"` | Deploy specific quickstarter |
| `crunch quickstarter --show-notebook` | Include notebook quickstarters |
| `crunch quickstarter --overwrite` | Overwrite existing files |

## Testing Commands

| Command | Description |
|---------|-------------|
| `crunch test` | Test solution locally |
| `crunch test --main-file main.py` | Specify entrypoint |
| `crunch test --model-directory resources` | Specify model directory |
| `crunch test --gpu` | Enable GPU flag |
| `crunch test --no-checks` | Skip prediction validation |
| `crunch test --no-determinism-check` | Skip determinism check |

## Submission Commands

| Command | Description |
|---------|-------------|
| `crunch push -m "message"` | Submit solution |
| `crunch push --dry` | Dry run (no actual submission) |
| `crunch push --main-file main.py` | Specify entrypoint |
| `crunch push --model-directory resources` | Specify model directory |

## Utility Commands

| Command | Description |
|---------|-------------|
| `crunch convert notebook.ipynb main.py` | Convert notebook to Python |
| `crunch convert notebook.ipynb main.py --requirements` | Also export requirements.txt |
| `crunch list` | List all available competitions |
| `crunch update-token` | Update project clone token |
| `crunch ping` | Check if server is online |

## Environment Detection

```python
import crunch

if crunch.is_inside_runner:
    print("running inside the runner")
else:
    print("running locally")
```

## Notebook Usage

```python
import crunch
crunch = crunch.load_notebook()

X_train, y_train, X_test = crunch.load_data()
# ... build model ...
crunch.test()
```
