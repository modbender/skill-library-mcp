# Integration Notes

## ElevenLabs

- `tour-booking` handles API calls to ElevenLabs.
- Required environment variables for live calls:
  - `ELEVENLABS_API_KEY`
  - `ELEVENLABS_AGENT_ID`
- Optional:
  - `ELEVENLABS_OUTBOUND_URL` (override endpoint URL)

## Calendar

- `create_invite_ics.py` creates `.ics` files for each confirmed showing.
- These files can be imported to Google Calendar manually or attached in confirmation emails.

## Audit Log Fields

Track these fields for each listing:
- `job_id`
- `listing_id`
- `address`
- `office_phone`
- `call_status` (`queued`, `completed`, `failed`, `no_answer`)
- `booking_status` (`confirmed`, `pending_callback`, `not_available`)
- `confirmed_start_time` (ISO 8601)
- `notes`
