# Letterboxd Tracker Skill for OpenCLAW

**Author:** Tamizh  
**Version:** 1.1.0

## Description
Your personal movie assistant. Track what you watch, check your lists, and get movie info from Letterboxd instantly.

This skill allows your OpenCLAW agent to retrieve information from Letterboxd.com, including user profiles, diaries, watchlists, and movie details. It uses the `letterboxdpy` library to scrape public data.

## Features
- **User Stats:** Get a user's watched count, reviews, lists, and favorite movies.
- **Diary:** Fetch recently watched movies from a user's diary.
- **Watchlist:** Retrieve movies from a user's watchlist.
- **Movie Details:** Get information about a specific movie (directors, year, rating).

## Installation

1. Ensure you have Python installed.
2. Install the required dependency:
   ```bash
   pip install letterboxdpy
   ```
3. Place these files in your OpenCLAW skill directory.

## Usage
The skill exposes the following commands to the agent:
- `lb_user`: Get profile stats.
- `lb_diary`: Get recent diary entries.
- `lb_watchlist`: Get watchlist items.
- `lb_movie`: Get movie details.

## License
MIT License - Copyright (c) 2026 Tamizh
