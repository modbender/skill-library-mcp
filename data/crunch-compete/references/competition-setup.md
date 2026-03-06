# Competition Setup Examples

## Generic Setup Pattern

Every competition follows this pattern.

Prerequisite: We use the UV packaging system, if that is not present switch to pip and venv


```bash
# 1. Create workspace and venv
mkdir -p ~/.crunch/workspace/competitions/<competition>
cd ~/.crunch/workspace/competitions/<competition>
python -m venv .venv
source .venv/bin/activate

# 2. Install crunch CLI and Jupyter
pip install crunch-cli jupyter ipykernel --upgrade --quiet --progress-bar=off

# 3. Register Jupyter kernel
python -m ipykernel install --user --name <competition> --display-name "CrunchDAO - <competition>"

# 4. Get token from: https://hub.crunchdao.com/competitions/<competition>/submit
crunch setup <competition> <project-name> --token <TOKEN>

# 5. Enter project directory
cd <competition>-<project-name>
```

## Competition-Specific Packages

Some competitions have their own SDK. Install in step 2:

| Competition | Additional Package |
|-------------|-------------------|
| Synth | `crunch-synth` |
| Falcon | `birdgame` |

Check the competition's repo README.md for required packages.

## Example: Synth Setup

```bash
mkdir -p ~/.crunch/workspace/competitions/synth
cd ~/.crunch/workspace/competitions/synth
python -m venv .venv
source .venv/bin/activate
pip install crunch-cli crunch-synth jupyter ipykernel --upgrade --quiet --progress-bar=off
python -m ipykernel install --user --name synth --display-name "CrunchDAO - Synth"
# Get token from: https://hub.crunchdao.com/competitions/synth/submit
crunch setup synth my-project --token <TOKEN>
cd synth-my-project
```


## Dedicated Competition Repos

Some competitions have SDK repos (e.g. `crunch-synth` for Synth) providing base classes, quickstarters, and utilities. Check the competition's repo for an installable package and ask the user if they want to install it:

```bash
pip install crunch-synth --upgrade
```

## Reference Material

After setup, check competition repo for:
- `SKILL.md` or `README.md` — rules, interface, scoring
- `LITERATURE.md` — academic papers and approaches
- `PACKAGES.md` — useful Python packages
- `scoring/` — scoring functions
