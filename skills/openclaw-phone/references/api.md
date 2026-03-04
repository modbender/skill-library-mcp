# CallMyCall API Reference (Subset)

Base URL:
```
https://call-my-call-backend.fly.dev
```

If your account is configured for a custom domain, use:
```
https://api.callmycall.com
```

## Authentication
Send your API key in the `Authorization` header.
```
Authorization: Bearer YOUR_API_KEY
```

---

## POST /v1/start-call
Start an outbound AI call.

Auth: **Required**

Request body (JSON):
| Field | Type | Required | Allowed / Notes |
| --- | --- | --- | --- |
| phone_number | string | Yes | E.164 format, e.g. `+46700000000` |
| task | string | Yes | What the AI should do |
| language | string | No | `sv`, `en`, `de`, etc. |
| tts_provider | string | No | `auto`, `openai`, `elevenlabs`, `azure` |
| genderVoice | string | No | Preferred voice gender (for provider voice selection), e.g. `female`, `male`, `neutral` |
| openaiVoice | string | No | OpenAI realtime voice name |
| 11labsVoice | string | No | ElevenLabs voice ID |
| elevenLabsVoice | string | No | Alias for `11labsVoice` |
| elevenLabsModel | string | No | ElevenLabs model ID |
| azureVoice | string | No | Azure Neural voice name |
| style | string | No | Azure style hint |
| role | string | No | Azure role hint |
| azureBackgroundAudio | object | No | `{ src, volume, fadeInMs, fadeOutMs }` |
| additionalPrompt | string | No | Extra instruction for AI |
| record | boolean | No | Record the call |
| max_duration | number | No | Seconds (connected duration) |
| max_queue_time | number | No | Seconds (queue wait limit) |
| persona | object | No | `{ name, phone, personal_security_number, address, role }` |
| transfer_number | string | No | Auto transfer number when human answers |
| from_number | string | No | Override caller ID (must be verified) |
| share_policy | object | No | `{ name_voice, phone_voice, phone_dtmf, pnr_voice, pnr_dtmf }` |
| webhook | string | No | HTTPS URL for events |
| webhook_events | string[] | No | Event types |
| metadata | object | No | Arbitrary metadata |
| enable_calendar | boolean | No | Enable calendar tools |
| calendar_permissions | object | No | `{ read, write }` |
| userOnCall | boolean | No | User on call mode |
| userPhone | string | No | Required if `userOnCall` true |
| monitored | boolean | No | Deprecated alias for `userOnCall` |
| user_phone | string | No | Deprecated alias for `userPhone` |

Response (JSON):
| Field | Type | Notes |
| --- | --- | --- |
| success | boolean | true on success |
| sid | string | Twilio Call SID |
| userOnCall | boolean | Present for user on call |
| sessionId | string | Present for user on call |
| userCallSid | string | Present for user on call |

---

## POST /v1/end-call
End a call.

Auth: **Required**

Request body (JSON):
| Field | Type | Required |
| --- | --- | --- |
| callSid | string | Yes |

Response (JSON):
| Field | Type | Notes |
| --- | --- | --- |
| success | boolean | true if the call was ended |

---

## GET /v1/calls/:callId
Get call status and metadata.

Auth: **Required**

Response (JSON):

The API may return either a flat call object **or** an envelope like:

```json
{ "call": { "status": "busy", "duration": "0", "...": "..." }, "transcripts": [] }
```

Read `status`/`duration` from:
- flat: `status`, `duration`
- envelope: `call.status`, `call.duration`

| Field | Type | Notes |
| --- | --- | --- |
| sid / call.call_id | string | Call SID |
| status / call.status | string | `queued`, `ringing`, `in-progress`, `completed`, `canceled`, `failed`, `busy`, `no-answer` |
| direction / call.direction | string | `outbound-api` or `inbound` |
| from / call.from | string | Caller ID |
| to / call.to | string | Destination number |
| duration / call.duration | number\|string | Duration in seconds (if completed) |
| recordingUrl / call.recording_url | string | Present if recorded |
| transcript / transcripts | object\|array | If available |

---

## GET /v1/calls/:callId/transcripts/stream
Stream transcripts for a call.

Auth: **Required**

Response: text/event-stream (SSE)

---

## GET /v1/calls/:callSid/recording
Get recording info for a call.

Auth: **Required**

Response (JSON):
| Field | Type | Notes |
| --- | --- | --- |
| url | string | Recording URL |
| mime | string | MIME type |
