# Ulanzi TC001 local HTTP endpoints

## Base
- `http://<TC001_HOST>/`

## Pages / Endpoints
- `GET /` → General Setting HTML
- `POST /` → Save General Setting (`page=sys_setting` + fields)
- `GET /app_switch` → Common Setting HTML
- `POST /app_switch` → Save Common Setting (`page=app_switch` + fields)
- `GET /info` → Device info (firmware, model)

## Notes
- Forms are standard `application/x-www-form-urlencoded`.
- Most fields are `<select>` values (0..n) or checkboxes (present = on).
