# Artisan Traps

- `migrate:fresh` drops ALL tables — use `migrate:refresh` to keep other tables
- `config:cache` bakes env — `env()` returns null except in config files
- `route:cache` requires controllers — closure routes break with cryptic error
- Schedule in `Kernel` — cron must run `schedule:run` every minute or skips
- `queue:work` caches code — restart workers after deploy or stale code runs
- Tinker `$model->save()` — actually saves to DB, not sandboxed
- `--force` in production — some commands refuse without it, CI needs flag
