# Boosta `video_type` Selection

`video_type` is required by Boosta API.

## Valid values

- `conversation`: podcasts, interviews, multi-person discussions
- `gaming`: gameplay or screen recording with reaction
- `faceless`: educational or documentary without a visible speaker
- `solo`: single presenter talking-head or expert format
- `vlog`: IRL/street/day-in-life style
- `movies`: films, TV series, cinematic scenes

## Mapping heuristics

Use these rules when user does not specify `video_type`:

1. Two or more speakers in frame/audio -> `conversation`
2. Gameplay or stream UI visible -> `gaming`
3. No person on camera most of runtime -> `faceless`
4. One speaker directly addressing camera -> `solo`
5. Handheld lifestyle sequence / daily vlog -> `vlog`
6. Professional narrative scenes / movie footage -> `movies`

If confidence is low, ask a clarifying question before submit.
