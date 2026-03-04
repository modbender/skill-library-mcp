---
name: letterboxd-tracker
description: Your personal movie assistant. Track what you watch, check your lists, and get movie info from Letterboxd instantly.
author: Tamizh
version: 1.1.0
---

# Letterboxd Skill

This skill allows the agent to retrieve information about movies or user activity from Letterboxd.

## Setup

```bash
pip install letterboxdpy
```

## Usage

Use this when the user asks about:
- Their Letterboxd profile stats
- Movies they've watched recently
- Their watchlist
- Specific movie details

## Commands

### `lb_user`
- **command**: `python lb_tool.py user "{{username}}"`
- **description**: Gets user profile stats (watched count, reviews, lists, favorites)
- **parameters**: 
  - `username`: The Letterboxd username

### `lb_diary`
- **command**: `python lb_tool.py diary "{{username}}" [limit]`
- **description**: Gets recently watched movies from user's diary
- **parameters**: 
  - `username`: The Letterboxd username
  - `limit`: Optional, default 10

### `lb_watchlist`
- **command**: `python lb_tool.py watchlist "{{username}}" [limit]`
- **description**: Gets movies in user's watchlist
- **parameters**: 
  - `username`: The Letterboxd username
  - `limit`: Optional, default 10

### `lb_movie`
- **command**: `python lb_tool.py movie "{{slug}}"`
- **description**: Gets movie details (title, year, rating, directors, description)
- **parameters**: 
  - `slug`: Movie URL slug (e.g., `vikram-2022`, `the-batman`)

## Examples

User: "How many movies have I watched on Letterboxd?"
Agent: (Calls `lb_user` with username="tamilventhan")

User: "What movies did I watch recently?"
Agent: (Calls `lb_diary` with username="tamilventhan")

User: "Show my watchlist"
Agent: (Calls `lb_watchlist` with username="tamilventhan")

User: "Tell me about the movie Vikram"
Agent: (Calls `lb_movie` with slug="vikram-2022")
