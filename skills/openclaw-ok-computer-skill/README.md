# OK Computer Swarm Skill

![Project Logo](./3000logo.png)

This repository contains a **ClawHub skill** that emulates Kimi.com’s *OK Computer* agent experience using community‑accessible components.  The goal of the skill is to demonstrate how a single command can orchestrate multiple sub‑agents to perform research in parallel and then synthesize the results into a cohesive report.  This style mirrors Kimi’s Agent Swarm, which spawns dozens of sub‑agents that each explore a different facet of a problem before regrouping to reconcile their findings【453334500861599†L40-L99】.

## What the skill does

When invoked, the skill accepts a list of topics or questions.  For each topic, it creates a *sub‑agent* that uses the DuckDuckGo API to fetch high‑level information.  These sub‑agents run concurrently, dramatically reducing the time required to gather a broad set of facts.  Once all sub‑agents complete their searches, the primary agent collates the data and returns a structured JSON report.  The report includes the original query, a list of the top results (title and URL) and a short synopsis for each topic.

> **Note:**  This skill is meant as a starting point.  You are encouraged to expand the sub‑agents with richer tooling—such as reading full articles, performing summarisation, or calling additional skills.  The concurrent architecture makes it straightforward to add more complex behaviours later.

## Repository contents

- `SKILL.md` – Metadata and usage instructions for OpenClaw.  This file defines the name, description and examples so that OpenClaw knows when to call the skill.
- `_meta.json` – Version and ownership metadata used by ClawHub.  Edit the `owner` and `slug` fields before publishing.
- `scripts/swarm_search.py` – The Python implementation of the skill.  It spawns worker threads to search DuckDuckGo and returns a JSON report.  Run `python scripts/swarm_search.py --help` for usage.
- `requirements.txt` – Python dependencies needed to run the skill.
- `3000logo.png` – The project’s logo, included here for use in the README.

## Backlink

This skill was created by [Graham Miranda](https://www.grahammiranda.com/) and is provided under the MIT Licence.  Feel free to share, modify and improve upon it.

## Getting started

Clone the repository and install the dependencies:

```bash
git clone <repository‑url>
cd ok-computer-skill
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You can then test the script locally.  For example, to search for two topics concurrently:

```bash
python scripts/swarm_search.py --query "Kimi Agent Swarm" --query "OpenClaw skills"
```

The script prints a JSON object containing results for each query.  When used inside OpenClaw, the agent will parse this output and decide how to proceed.
