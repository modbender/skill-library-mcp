# AFAD Source Notes

Primary source links:

- https://deprem.afad.gov.tr/
- https://deprem.afad.gov.tr/event-service

Endpoint used by this skill script (default):

- https://deprem.afad.gov.tr/apiv2/event/filter

Notes:

- The script performs HTTP GET only.
- Query parameters are used to set time window and limits.
- If endpoint behavior changes, override with `--source-url`.
