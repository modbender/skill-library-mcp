# Finding Movies — Detailed Reference

How to discover what's playing, find showtimes, and choose the right film.

Load config: `CONFIG=$(cat ~/.openclaw/skills/date-night/config.json)`

---

## Quick Discovery Methods

### 1. Web Search
```bash
web_search "movies playing near {config.zip} this weekend"
web_search "new movies in theaters {month} {year}"
web_search "best date night movies in theaters now"
web_search "{config.preferred_theater} showtimes tonight"
```

### 2. Fandango (Best Aggregator — All Chains)
```bash
playwright-cli -s=fd open "https://www.fandango.com/movies-in-theaters?location={config.zip}" --headed
playwright-cli -s=fd snapshot
```
Shows all movies across nearby theaters with inline showtimes. Best for discovering options without knowing which chain.

### 3. IMDB Showtimes
```bash
playwright-cli -s=imdb open "https://www.imdb.com/showtimes/?zip={config.zip}&date={YYYY-MM-DD}" --headed
playwright-cli -s=imdb snapshot
```

### 4. Preferred Theater Direct
```bash
# Use config.preferred_theater if set
playwright-cli -s=movies open "https://{preferred_theater_url}" --headed
playwright-cli -s=movies snapshot
```

---

## Choosing a Date Night Movie

### Questions to Consider
1. Genre preference? (comedy, drama, action, thriller, romance)
2. Runtime — long film + dinner = late night
3. Rating? Most couples prefer PG-13; R depends on content
4. Worth a premium format (IMAX, Dolby, PLF) for this film?

### Rating Guide

| Rating | Suitability | Notes |
|--------|-------------|-------|
| G / PG | ✅ Great | Often high quality |
| PG-13 | ✅ Great | Sweet spot for most date nights |
| R | ⚠️ Depends | Violence/language usually fine; check content reason |
| NC-17 | ❌ Skip | |

**Apply dietary config:** No specific filter for movies, but if `dietary` reflects strong values (e.g., lifestyle preferences), consider noting if a film has heavy drug/alcohol themes.

### Review Sources
```bash
web_search "{movie title} {year} Rotten Tomatoes score"
web_search "{movie title} Metacritic score audience"
```

**Quick heuristic:**
- RT > 75% + Audience > 80% = solid bet
- RT < 50% but Audience > 70% = often good entertainment despite critics
- Both < 50% = skip unless specifically requested

---

## Showtime Selection

### Timing for Date Night

| Scenario | Recommended Showtime |
|----------|---------------------|
| Dinner before movie | 7:30–8:30 PM (eat 5:30–6:30) |
| Movie only | 7:00–8:00 PM |
| Dinner after (rare) | 5:00–6:00 PM (eat after at 8:00+) |

**Leave time calculation:**
```
Leave = Showtime - Drive time from {config.location} - 15 min buffer
```

Find drive time: `web_search "drive time from {config.location} to {theater address}"`

### Format Recommendations

| Film Type | Best Format |
|-----------|-------------|
| Action blockbuster, sci-fi | IMAX / PLF (worth the premium) |
| Drama, comedy, romance | Standard |
| Animated | Standard (3D usually not worth it) |

---

## Now Playing vs. Coming Soon

```bash
# Currently in theaters
web_fetch "https://www.fandango.com/movies-in-theaters" --maxChars 5000 2>/dev/null || true

# Upcoming releases
web_search "upcoming movies {month} {year} release dates"
```

**Set a reminder for upcoming films:**
```json
{
  "name": "movie-reminder-{film}",
  "enabled": true,
  "schedule": {"kind": "once", "at": "{release-date}T09:00", "tz": "{user-tz}"},
  "payload": {
    "kind": "agentTurn",
    "message": "Notify the user that '{Film}' is now in theaters. Check {preferred_theater} for showtimes near {config.zip} and suggest a date night. USE THE MESSAGE TOOL to notify via {config.notify_channel}.",
    "deliver": false
  }
}
```

---

## Movie Recommendation Format

Present 2–4 options max:

```
🎬 **Movies Playing — {Date}**
📍 {Theater Name} (your preferred theater)

1. **{Title}** — {Genre}
   ⏱️ {Runtime} | {Rating} | {Format}
   🍅 RT: {%} Critics · {%} Audience
   🎯 Date night fit: {brief reason}
   📅 Showtimes: {time1}, {time2}, {time3}

2. **{Title}** ...
```

Lead with your top recommendation for a date night.
