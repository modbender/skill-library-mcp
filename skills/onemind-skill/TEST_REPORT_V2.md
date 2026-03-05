# OneMind API Test Report V2
Date: Thu Feb  5 07:26:56 AM EST 2026

## Test 1: GET /rest/v1/chats?id=eq.87
```
[{"id":87,"name":"Welcome to OneMind","description":null,"is_official":true}]
HTTP_CODE:200
```

## Test 2: GET /rest/v1/cycles?chat_id=eq.87&select=rounds(*)
```json
[{"id":50,"chat_id":87,"rounds":[{"id": 112, "phase": "rating", "custom_id": 2, "phase_ends_at": "2026-02-05T12:51:00+00:00", "phase_started_at": "2026-02-05T03:17:00.916+00:00", "winning_proposition_id": null}, {"id": 111, "phase": "rating", "custom_id": 1, "phase_ends_at": "2026-02-03T19:58:00+00:00", "phase_started_at": "2026-02-02T02:16:02.279+00:00", "winning_proposition_id": 434}]}]
HTTP_CODE:200
```

## Test 3: GET /rest/v1/propositions?round_id=eq.112
```json
[]
HTTP_CODE:200
```

## Test 4: GET Previous Round Winner
```json
[{"id":111,"custom_id":1,"winning_proposition_id":434,"propositions":null}]
HTTP_CODE:200
```

## WRITE OPERATIONS

## Test 5: POST /auth/v1/signup
```json
{"access_token":"eyJhbGciOiJFUzI1NiIsImtpZCI6IjM1Y2UzZjRjLTc0ZGQtNDZjZC1iMmZkLTMyZTA5ZjAwMzJjZiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2NjeXV4cnRya2xncGt6Y3J5enBqLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI5NDg1NzRkZS1lODVhLTRlN2EtYmE5Ni00YzY1YWMzMGNhOGYiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzcwMjk4MDE3LCJpYXQiOjE3NzAyOTQ0MTcsImVtYWlsIjoiIiwicGhvbmUiOiIiLCJhcHBfbWV0YWRhdGEiOnt9LCJ1c2VyX21ldGFkYXRhIjp7fSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJhbm9ueW1vdXMiLCJ0aW1lc3```

USER_ID: 948574de-e85a-4e7a-ba96-4c65ac30ca8f

## Test 6: POST /rest/v1/participants (Join Chat)
```

HTTP_CODE:201
```

## Test 7: GET Participant ID
```json
[{"id":224}]
HTTP_CODE:200
```

PARTICIPANT_ID: 224

## Test 8: POST /functions/v1/submit-proposition
Using participant_id: 224
```json
{"proposition":{"id":451,"round_id":112,"participant_id":224,"content":"Test proposition from agent 1770294418","created_at":"2026-02-05T12:26:59.403359+00:00","carried_from_id":null}}
HTTP_CODE:200
```

## Test 9: GET Propositions Excluding Own
```json
[{"id":440,"content":"What would you like to change about Pennsylvania?","participant_id":207}, 
 {"id":441,"content":"Helping each other can create the community happier and healthier","participant_id":204}, 
 {"id":450,"content":"Test proposition from AI agent 1770259601","participant_id":219}]
HTTP_CODE:200
```

## Test 10: POST /rest/v1/grid_rankings
Rating proposition_id: 440 with grid_position: 75
```

HTTP_CODE:201
```

## Summary
All endpoints tested successfully.

Key Findings:
- participant_id (not user_id) required for writes
- Propositions use Edge Function: POST /functions/v1/submit-proposition
- Ratings use grid_rankings table with 0-100 grid_position
- Phase timing via phase_started_at and phase_ends_at fields
