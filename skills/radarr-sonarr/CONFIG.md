# Configuration Guide

Complete configuration reference for the Radarr-Sonarr skill.

## Environment Variables

All configuration is done via environment variables. Create a `.env` file in the skill directory:

```bash
cp .env.example .env
```

Then edit the file with your values.

---

## Required Variables

### RADARR_URL

The URL where Radarr is accessible.

```bash
# Local installation
RADARR_URL=http://localhost:7878

# Docker (container name)
RADARR_URL=http://radarr:7878

# Remote server
RADARR_URL=https://radarr.mydomain.com
```

### RADARR_API_KEY

Your Radarr API key. Find it in:
**Radarr → Settings → General → API Key**

```bash
RADARR_API_KEY=your_api_key_here
```

### SONARR_URL

The URL where Sonarr is accessible.

```bash
# Local installation
SONARR_URL=http://localhost:8989

# Docker
SONARR_URL=http://sonarr:8989

# Remote server
SONARR_URL=https://sonarr.mydomain.com
```

### SONARR_API_KEY

Your Sonarr API key. Find it in:
**Sonarr → Settings → General → API Key**

```bash
SONARR_API_KEY=your_api_key_here
```

---

## Optional Variables

### RADARR_ROOT_FOLDER

Default folder where movies are stored.

```bash
RADARR_ROOT_FOLDER=/data/movies
RADARR_ROOT_FOLDER=/mnt/storage/movies
RADARR_ROOT_FOLDER=/home/user/media/Movies
```

**Default:** `/data/movies`

### SONARR_ROOT_FOLDER

Default folder where TV shows are stored.

```bash
SONARR_ROOT_FOLDER=/data/tv
SONARR_ROOT_FOLDER=/mnt/storage/tv
SONARR_ROOT_FOLDER=/home/user/media/TV Shows
```

**Default:** `/data/tv`

### RADARR_QUALITY_PROFILE

Default quality profile for movies.

```bash
RADARR_QUALITY_PROFILE=HD-1080p
RADARR_QUALITY_PROFILE=Any
RADARR_QUALITY_PROFILE=SD
RADARR_QUALITY_PROFILE=Ultra-HD
```

**Default:** `HD-1080p`

### SONARR_QUALITY_PROFILE

Default quality profile for TV shows.

```bash
SONARR_QUALITY_PROFILE=HD-1080p
SONARR_QUALITY_PROFILE=Any
SONARR_QUALITY_PROFILE=SD
SONARR_QUALITY_PROFILE=Ultra-HD
```

**Default:** `HD-1080p`

### RADARR_LANGUAGE_PROFILE

Default language profile for movies.

```bash
RADARR_LANGUAGE_PROFILE=English
RADARR_LANGUAGE_PROFILE=French
RADARR_LANGUAGE_PROFILE=German
```

**Default:** `English`

### SONARR_LANGUAGE_PROFILE

Default language profile for TV shows.

```bash
SONARR_LANGUAGE_PROFILE=English
SONARR_LANGUAGE_PROFILE=French
SONARR_LANGUAGE_PROFILE=German
```

**Default:** `English`

---

## Docker Configuration

If Radarr and Sonarr run in Docker containers:

```bash
RADARR_URL=http://radarr:7878
SONARR_URL=http://sonarr:8989
```

The skill must be able to resolve the container names. This typically works if:
- Running on the same Docker network
- Using Docker Compose with proper networking

---

## Troubleshooting

### Testing Your Configuration

Run the status command to verify connections:

```bash
# Test Radarr
python scripts/cli.py radarr status

# Test Sonarr
python scripts/cli.py sonarr status
```

If you see "connected", your configuration is correct.

### Common Issues

**Connection Refused**
- Check if the URL is correct
- Verify the service is running
- Check firewall rules

**401 Unauthorized**
- API key is incorrect or missing
- Regenerate API key in Radarr/Sonarr settings

**404 Not Found**
- URL path may be incorrect
- Ensure no trailing slashes in URL

---

## Security Notes

- **Never commit `.env` files** to version control
- Use **secrets management** in production
- Consider using **read-only API keys** if supported
- Restrict API access by IP if possible
