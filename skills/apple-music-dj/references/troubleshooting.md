# Troubleshooting

Step-by-step fixes for common issues. Run `scripts/verify_setup.sh` first — it catches
most problems automatically.

---

## Authentication Issues

### HTTP 401 — Developer Token Invalid or Expired

**Symptoms:** Every API call returns `401 Unauthorized`.

**Cause:** Your JWT developer token is expired or malformed.

**Fix:**

1. Check your token's expiration:

   ```bash
   # Decode the JWT payload (middle segment)
   echo "$APPLE_MUSIC_DEV_TOKEN" | cut -d. -f2 | base64 -d 2>/dev/null | python3 -m json.tool
   ```

   Look at the `exp` field — it's a Unix timestamp.

2. Regenerate if expired:

   ```bash
   python3 scripts/generate_dev_token.py <team_id> <key_id> <path/to/AuthKey.p8>
   export APPLE_MUSIC_DEV_TOKEN="<new_token>"
   ```

3. Verify:

   ```bash
   scripts/apple_music_api.sh verify
   ```

**Common mistakes:**

- Token has a max lifetime of 6 months — Apple rejects longer
- Wrong Key ID or Team ID in generation
- Using the wrong `.p8` file (you may have multiple keys)

---

### HTTP 403 — User Token Expired

**Symptoms:** API calls that access user data (`/v1/me/*`) return `403 Forbidden`.
Catalog endpoints (`/v1/catalog/*`) still work.

**Cause:** The Music User Token expires after ~6 months. There is no refresh flow.

**Fix:**

1. Re-authorize in the browser using the MusicKit JS page from `references/auth-setup.md`
2. Copy the new token from the browser console
3. Update your environment:

   ```bash
   export APPLE_MUSIC_USER_TOKEN="<new_token>"
   ```

4. Verify:

   ```bash
   scripts/apple_music_api.sh verify
   ```

**Note:** Both token types expire around the same time (~6 months). When one expires,
check the other too.

---

### "PyJWT not installed" when generating dev token

**Fix:**

```bash
pip3 install PyJWT cryptography
```

PyJWT is the only pip dependency in the entire project, and it's only needed for
`generate_dev_token.py`. All other scripts use stdlib only.

---

## Taste Profile Issues

### Empty or very sparse taste profile

**Symptoms:** Profile has very few artists/genres, playlists feel generic.

**Causes:**

- New Apple Music account with limited history
- Privacy settings blocking data access
- Replay data not available in your region

**Fix (in order of preference):**

1. **Check Replay data** — even with limited recent history, Replay covers a full year:

   ```bash
   scripts/apple_music_api.sh replay-summary
   ```

2. **Check library size** — you might have songs but not recent plays:

   ```bash
   scripts/apple_music_api.sh library-songs | python3 -c "import sys,json; print(len(json.load(sys.stdin)['data']))"
   ```

3. **Check ratings** — loved songs are the strongest signal:

   ```bash
   scripts/apple_music_api.sh loved-songs
   ```

4. **Manual seeds** — tell the AI 3–5 artists/songs you love. It can use catalog
   search to bootstrap a profile without any listening data.

---

### Stale cache / profile doesn't reflect recent listening

**Symptoms:** Recommendations feel outdated, recently loved artists don't appear.

**Fix:**

```bash
# Force a fresh profile (bypass 7-day cache)
python3 scripts/taste_profiler.py --max-age 0

# Or delete cache entirely
rm -rf ~/.apple-music-dj/
```

---

### "No storefront detected"

**Symptoms:** Error about missing storefront when running catalog commands.

**Cause:** Auto-detection failed (rare API issue) or Apple Music not available
in your region.

**Fix:**

```bash
# Set manually (replace 'us' with your country code)
export APPLE_MUSIC_STOREFRONT=us
```

Valid storefronts: `us`, `gb`, `ca`, `au`, `de`, `fr`, `jp`, `kr`, `br`, `mx`, `in`, etc.
Full list: <https://developer.apple.com/documentation/applemusicapi/storefronts>

---

## API & Network Issues

### HTTP 429 — Rate Limited

**Symptoms:** Commands fail with `429 Too Many Requests`.

**Cause:** Too many API calls in a short window. Apple's rate limits are undocumented
but approximately ~20 requests/second is safe.

**What happens automatically:**
The API wrapper (`apple_music_api.sh`) has built-in exponential backoff:
1s → 2s → 4s, up to 3 retries. Most 429s resolve themselves.

**If it persists:**

- Wait 60 seconds and retry
- Avoid running multiple scripts simultaneously
- The taste profiler makes ~10 API calls — if you're also running other scripts,
  space them out

---

### Network timeout / "Cannot reach api.music.apple.com"

**Fix:**

1. Check internet connectivity: `curl -s https://apple.com > /dev/null && echo "OK"`
2. Check Apple Music API status: <https://developer.apple.com/system-status/>
3. If behind a corporate proxy/VPN, ensure `api.music.apple.com:443` is allowed

---

### HTTP 404 — Resource Not Found

**Symptoms:** Specific songs, albums, or artists return 404.

**Cause:** Content was removed from the Apple Music catalog. This happens regularly
(licensing changes, artist decisions, etc.).

**What happens:** Scripts automatically skip 404s and continue. A warning is logged
but the operation completes.

**If a playlist has 404 tracks:**
Run the Playlist Health Check (or ask the AI to check your playlist).

---

## Playlist Issues

### "Playlist created but it's empty"

**Causes:**

- All candidate tracks were filtered out (disliked artists, duplicates, etc.)
- API returned catalog IDs that don't match the user's storefront
- Assembly rules were too strict for the available candidates

**Fix:**

1. Check your disliked songs — if you've disliked many artists, the filter may be
   too aggressive
2. Try a different strategy or broader mood/genre
3. Run with a different storefront if you suspect region mismatch

---

### Playlist doesn't appear on my device

**Symptoms:** Script says "playlist created" but it's not in Apple Music.

**Fix:**

1. **Wait 30 seconds** — Apple Music sync isn't instant
2. Force sync: close and reopen Apple Music app
3. Check "Recently Added" in your library
4. Verify you're signed into the same Apple ID

---

## Script Issues

### "python3: command not found"

**Fix (macOS):**

```bash
# Install via Homebrew
brew install python3

# Or use Apple's built-in if available
/usr/bin/python3 --version
```

**Fix (Linux):**

```bash
sudo apt install python3   # Debian/Ubuntu
sudo dnf install python3   # Fedora
```

---

### "jq: command not found"

**Fix (macOS):**

```bash
brew install jq
```

**Fix (Linux):**

```bash
sudo apt install jq   # Debian/Ubuntu
sudo dnf install jq   # Fedora
```

---

### "Permission denied" when running a script

**Fix:**

```bash
chmod +x scripts/*.sh
```

Python scripts don't need execute permission if run with `python3 scripts/...`.

---

## Still Stuck?

1. Run `scripts/verify_setup.sh` and share the full output
2. Check [existing issues](https://github.com/and3rn3t/apple-music-dj/issues)
3. Open a [bug report](https://github.com/and3rn3t/apple-music-dj/issues/new?template=bug_report.md) with:
   - Your OS and Python version
   - Full error output
   - What command you ran
   - **Redact all tokens!**
