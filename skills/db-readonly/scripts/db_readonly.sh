#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <postgres|mysql> \"<SQL>\" [--format table|csv|tsv|json] [--out /path/file]" >&2
  exit 1
fi

ENGINE="$1"
SQL="$2"
shift 2

FORMAT="table"
OUT=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --format)
      FORMAT="${2:-table}"; shift 2 ;;
    --out)
      OUT="${2:-}"; shift 2 ;;
    *)
      echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

LOWER_SQL="$(printf '%s' "$SQL" | tr '[:upper:]' '[:lower:]')"
if printf '%s' "$LOWER_SQL" | grep -Eq '(^|[^a-z])(insert|update|delete|drop|alter|create|truncate|grant|revoke|replace|merge|call|do)([^a-z]|$)'; then
  echo "Blocked: non-read SQL detected." >&2
  exit 2
fi

if ! printf '%s' "$LOWER_SQL" | grep -Eq '^\s*(select|with|explain)\b'; then
  echo "Blocked: only SELECT/WITH/EXPLAIN statements are allowed." >&2
  exit 2
fi

run_postgres() {
  local psql_cmd=(psql -v ON_ERROR_STOP=1 -X)
  case "$FORMAT" in
    table)
      psql_cmd+=( -P pager=off -c "$SQL" ) ;;
    csv)
      psql_cmd+=( -P pager=off -c "\\copy ($SQL) TO STDOUT WITH CSV HEADER" ) ;;
    tsv)
      psql_cmd+=( -P pager=off -F $'\t' -A -c "$SQL" ) ;;
    json)
      psql_cmd+=( -P pager=off -t -A -c "SELECT json_agg(t) FROM ($SQL) t;" ) ;;
    *) echo "Unsupported format: $FORMAT" >&2; exit 1 ;;
  esac

  if [ -n "$OUT" ]; then
    "${psql_cmd[@]}" > "$OUT"
    echo "Saved to $OUT"
  else
    "${psql_cmd[@]}"
  fi
}

run_mysql() {
  local mysql_cmd=(mysql --batch --raw --default-character-set=utf8mb4)
  mysql_cmd+=( -h "${MYSQL_HOST:?MYSQL_HOST is required}" )
  mysql_cmd+=( -P "${MYSQL_PORT:-3306}" )
  mysql_cmd+=( -u "${MYSQL_USER:?MYSQL_USER is required}" )
  mysql_cmd+=( "${MYSQL_DATABASE:?MYSQL_DATABASE is required}" )
  export MYSQL_PWD="${MYSQL_PASSWORD:?MYSQL_PASSWORD is required}"

  case "$FORMAT" in
    table)
      mysql_cmd=(mysql -t -h "${MYSQL_HOST:?}" -P "${MYSQL_PORT:-3306}" -u "${MYSQL_USER:?}" "${MYSQL_DATABASE:?}") ;;
    csv|tsv|json)
      : ;;
    *) echo "Unsupported format: $FORMAT" >&2; exit 1 ;;
  esac

  local query="$SQL"
  if [ "$FORMAT" = "json" ]; then
    query="SELECT JSON_ARRAYAGG(j) FROM (SELECT * FROM ($SQL) s) j;"
  fi

  if [ -n "$OUT" ]; then
    "${mysql_cmd[@]}" -e "$query" > "$OUT"
    echo "Saved to $OUT"
  else
    "${mysql_cmd[@]}" -e "$query"
  fi
}

case "$ENGINE" in
  postgres)
    command -v psql >/dev/null 2>&1 || { echo "psql not found" >&2; exit 127; }
    : "${PGHOST:?PGHOST is required}" "${PGDATABASE:?PGDATABASE is required}" "${PGUSER:?PGUSER is required}" "${PGPASSWORD:?PGPASSWORD is required}"
    export PGHOST PGPORT="${PGPORT:-5432}" PGDATABASE PGUSER PGPASSWORD
    run_postgres
    ;;
  mysql)
    command -v mysql >/dev/null 2>&1 || { echo "mysql client not found" >&2; exit 127; }
    run_mysql
    ;;
  *)
    echo "Unsupported engine: $ENGINE (use postgres|mysql)" >&2
    exit 1
    ;;
esac
