# Firefly AI API Reference

## Endpoint
- GraphQL: `https://api.fireflies.ai/graphql`
- Auth: `Authorization: Bearer <API_KEY>`

## Key Queries

### transcripts (list)
Arguments: `keyword`, `scope` (title|sentences|all), `fromDate`, `toDate`, `limit` (max 50), `skip`, `host_email`, `mine`, `organizers`, `participants`, `channel_id`

### transcript (single)
Arguments: `id` (required)

## Transcript Fields
- `id`, `title`, `date` (epoch ms), `duration` (minutes), `participants`, `host_email`, `organizer_email`
- `transcript_url`, `audio_url`, `video_url`, `meeting_link`
- `sentences[]`: `index`, `speaker_name`, `speaker_id`, `text`, `raw_text`, `start_time`, `end_time`
- `speakers[]`: `id`, `name`
- `summary`: `keywords`, `action_items`, `outline`, `shorthand_bullet`, `overview`, `bullet_gist`, `gist`, `short_summary`, `short_overview`, `meeting_type`, `topics_discussed`, `transcript_chapters`
- `analytics.sentiments`: `negative_pct`, `neutral_pct`, `positive_pct`
- `analytics.speakers[]`: `name`, `duration`, `word_count`, `longest_monologue`, `questions`, `words_per_minute`
- `meeting_attendees[]`: `displayName`, `email`, `phoneNumber`
- `meeting_attendance[]`: `name`, `join_time`, `leave_time`
