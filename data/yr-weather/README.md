# Yr.no Weather CLI (v1.0.0)

Production CLI for MET Norway weather forecasts.

## Install

```bash
pip install .
```

## Usage

```bash
yr-weather -33.9288 18.4174  # Cape Town now + forecast
yr-tomorrow -33.8688 151.2093  # Sydney tomorrow
```

See `SKILL.md` for OpenClaw integration.

## Tests

```bash
pytest
```

Data: MET Norway (free API).
