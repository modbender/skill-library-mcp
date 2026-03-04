# Platform Coverage Reference

social-analyzer covers 1000+ platforms. Below are notable categories and examples.

## Social Networks
- Twitter / X, Facebook, Instagram, LinkedIn, TikTok, Pinterest, Snapchat
- Mastodon, Bluesky, Threads

## Developer & Tech
- GitHub, GitLab, Bitbucket, Stack Overflow, HackerNews, Dev.to, Replit

## Video & Streaming
- YouTube, Twitch, Vimeo, Dailymotion, Rumble, Kick

## Gaming
- Steam, Xbox Live, PSN, Battle.net, Epic Games, Riot Games
- Speedrun.com, Roblox, Chess.com

## Music
- SoundCloud, Bandcamp, Last.fm, Spotify (public profiles), Mixcloud

## Creative & Art
- Behance, Dribbble, DeviantArt, ArtStation, Pixiv, Newgrounds

## Writing & Blogging
- Medium, Substack, Tumblr, Blogger, Wordpress.com, Ghost

## Forums & Communities
- Reddit, Quora, Discord (public servers), Telegram (public), 4chan

## Dating & Social (--type adult)
- Covered but disabled by default; use `--type adult` to include

## Professional
- LinkedIn, AngelList, Crunchbase, ProductHunt

## E-commerce & Freelance
- Etsy, Fiverr, Upwork, Patreon, Ko-fi, BuyMeACoffee

## Regional / Country-specific
Use `--countries` flag to prioritize:
- `us` — US-centric platforms
- `ru` — Russian platforms (VK, OK.ru etc)
- `br` — Brazilian platforms
- `jp` — Japanese platforms
- `cn` — Chinese platforms (limited due to access restrictions)

## Filter by Type
`--type` accepts: music, gaming, adult, tech, art, social, dating, shopping, news

## Notes
- Coverage and detection accuracy varies by platform
- Some platforms actively block automated requests (rate limiting)
- Use `--mode slow` for more polite scanning of sensitive platforms
