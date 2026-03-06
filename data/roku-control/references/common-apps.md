# Common Roku Apps & Channels

This reference lists popular Roku channel/app IDs for quick launching.

## Streaming Services

| App Name | App ID | Notes |
|----------|--------|-------|
| Netflix | 12 | Most common streaming service |
| Hulu | 2285 | Subscription streaming |
| Disney+ | 291097 | Disney, Pixar, Marvel, Star Wars |
| Amazon Prime Video | 13 | Prime Video streaming |
| HBO Max | 61322 | HBO and Warner Bros content |
| YouTube | 837 | Free video platform |
| YouTube TV | 41468 | Live TV streaming |
| Apple TV+ | 551012 | Apple's streaming service |
| Peacock | 593099 | NBCUniversal streaming |
| Paramount+ | 31440 | CBS, MTV, Nickelodeon content |
| ESPN | 34376 | Sports streaming |
| ESPN+ | 116014 | ESPN premium streaming |

## Live TV & News

| App Name | App ID | Notes |
|----------|--------|-------|
| The Roku Channel | 151908 | Free live TV and movies |
| Pluto TV | 74519 | Free live TV channels |
| Tubi | 41468 | Free movies and TV |
| Sling TV | 46041 | Live TV subscription |
| FuboTV | 147977 | Live sports and TV |
| Plex | 13535 | Media server and free content |

## Music

| App Name | App ID | Notes |
|----------|--------|-------|
| Spotify | 22297 | Music streaming |
| Pandora | 28 | Internet radio |
| Apple Music | 626209 | Apple's music service |
| Amazon Music | 41387 | Amazon music streaming |
| iHeartRadio | 31533 | Radio and podcasts |

## Gaming

| App Name | App ID | Notes |
|----------|--------|-------|
| Twitch | 46510 | Game streaming |

## Note

App IDs may vary by region and device. To get the exact IDs for your Roku:

```bash
python3 scripts/roku_control.py --ip <your-roku-ip> apps
```

This will list all installed apps with their IDs.
