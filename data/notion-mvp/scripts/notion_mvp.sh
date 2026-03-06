#!/usr/bin/env bash
set -euo pipefail

: "${NOTION_TOKEN:?Missing NOTION_TOKEN}"

api="https://api.notion.com/v1"
version="2022-06-28"

cmd="${1:-}"
shift || true

today_utc() { date -u +%F; }

request() {
  local method="$1"; shift
  local url="$1"; shift
  local data="${1:-}"

  if [[ -n "$data" ]]; then
    curl -sS -X "$method" "$url" \
      -H "Authorization: Bearer $NOTION_TOKEN" \
      -H "Notion-Version: $version" \
      -H "Content-Type: application/json" \
      --data "$data"
  else
    curl -sS -X "$method" "$url" \
      -H "Authorization: Bearer $NOTION_TOKEN" \
      -H "Notion-Version: $version" \
      -H "Content-Type: application/json"
  fi
}

resolve_db_id() {
  local alias="$1"
  node -e '
const alias = process.argv[1] || "";
const mapRaw = process.env.NOTION_DATABASE_MAP || "";
const fallback = process.env.NOTION_DATABASE_ID || "";
let map = {};
if (mapRaw) {
  try { map = JSON.parse(mapRaw); } catch (e) { process.stderr.write("Invalid NOTION_DATABASE_MAP JSON\n"); process.exit(2); }
}
if (alias) {
  const db = map[alias];
  if (!db) { process.stderr.write(`Unknown alias: ${alias}\n`); process.exit(3); }
  process.stdout.write(db); process.exit(0);
}
if (fallback) { process.stdout.write(fallback); process.exit(0); }
process.stderr.write("Missing database alias and NOTION_DATABASE_ID fallback\n");
process.exit(4);
' "$alias"
}

list_aliases() {
  node -e '
const raw = process.env.NOTION_DATABASE_MAP || "{}";
let map = {};
try { map = JSON.parse(raw); } catch { console.log("invalid NOTION_DATABASE_MAP JSON"); process.exit(1); }
const keys = Object.keys(map);
if (!keys.length) { console.log("(no aliases configured)"); process.exit(0); }
for (const k of keys) console.log(`${k} -> ${map[k]}`);
'
}

get_props_json() {
  local db_id="$1"
  local raw
  raw="$(request GET "$api/databases/$db_id")"
  node -e '
const j = JSON.parse(process.argv[1]);
if (j.object === "error") { console.log(JSON.stringify(j)); process.exit(0); }
const p = j.properties || {};
const entries = Object.entries(p).map(([name,val])=>({name,type:val.type}));
const findByNamesAndType = (names, types) => entries.find(e => names.includes(e.name) && types.includes(e.type));
const findByType = (types) => entries.find(e => types.includes(e.type));
const title = findByType(["title"]);
const date = findByNamesAndType(["Data","Date"],["date"]) || findByType(["date"]);
const time = findByNamesAndType(["Hora","Time"],["rich_text","title"]) || findByNamesAndType(["Hora","Time"],["select"]);
const location = findByNamesAndType(["Local","Location"],["rich_text","title"]) || findByNamesAndType(["Local","Location"],["select"]);
const weekday = findByNamesAndType(["Dia da semana","Dia","Weekday"],["rich_text","select"]);
console.log(JSON.stringify({
  title: title?.name || null,
  date: date?.name || null,
  time: time?.name || null,
  location: location?.name || null,
  weekday: weekday?.name || null,
  weekdayType: weekday?.type || null
}));
' "$raw"
}

case "$cmd" in
  aliases)
    list_aliases
    ;;

  add)
    alias="${1:-}"
    bloco="${2:-}"
    data_value="${3:-$(today_utc)}"
    hora_value="${4:-09:00}"
    local_value="${5:-}"

    if [[ -z "$alias" || -z "$bloco" ]]; then
      echo 'Usage: notion_mvp.sh add <alias> "<bloco>" [YYYY-MM-DD] [HH:MM] ["<local>"]' >&2
      exit 1
    fi

    db_id="$(resolve_db_id "$alias")"
    props_json="$(get_props_json "$db_id")"

    payload="$(node -e '
const [bloco,data,hora,localTxt,db,propsRaw] = process.argv.slice(1);
const props = JSON.parse(propsRaw);
if (!props.title || !props.date) {
  process.stderr.write("Database precisa de coluna title + date (ex.: Bloco e Data).\n");
  process.exit(2);
}
const p = {
  parent: { database_id: db },
  properties: {
    [props.title]: { title: [{ text: { content: bloco } }] },
    [props.date]: { date: { start: data } }
  }
};
if (props.time) p.properties[props.time] = { rich_text: hora ? [{ text: { content: hora } }] : [] };
if (props.location) p.properties[props.location] = { rich_text: localTxt ? [{ text: { content: localTxt } }] : [] };
if (props.weekday) {
  const d = new Date(data + "T12:00:00Z");
  const names=["domingo","segunda","terça","quarta","quinta","sexta","sábado"];
  const dia = names[d.getUTCDay()];
  if (props.weekdayType === "select") p.properties[props.weekday] = { select: { name: dia } };
  else p.properties[props.weekday] = { rich_text: [{ text: { content: dia } }] };
}
process.stdout.write(JSON.stringify(p));
' "$bloco" "$data_value" "$hora_value" "$local_value" "$db_id" "$props_json")"

    request POST "$api/pages" "$payload"
    ;;

  today)
    alias="${1:-}"
    if [[ -z "$alias" ]]; then
      echo 'Usage: notion_mvp.sh today <alias>' >&2
      exit 1
    fi
    db_id="$(resolve_db_id "$alias")"
    props_json="$(get_props_json "$db_id")"
    d="$(today_utc)"

    payload="$(node -e '
const [d,propsRaw] = process.argv.slice(1);
const props = JSON.parse(propsRaw);
if (!props.date) { process.stderr.write("Database sem coluna de data.\n"); process.exit(2); }
const p = { filter: { property: props.date, date: { equals: d } }, page_size: 50 };
process.stdout.write(JSON.stringify(p));
' "$d" "$props_json")"

    request POST "$api/databases/$db_id/query" "$payload"
    ;;

  query)
    alias="${1:-}"
    q="${2:-}"
    if [[ -z "$alias" || -z "$q" ]]; then
      echo 'Usage: notion_mvp.sh query <alias> "<text>"' >&2
      exit 1
    fi
    db_id="$(resolve_db_id "$alias")"
    props_json="$(get_props_json "$db_id")"

    payload="$(node -e '
const [q,propsRaw] = process.argv.slice(1);
const props = JSON.parse(propsRaw);
if (!props.title) { process.stderr.write("Database sem coluna title.\n"); process.exit(2); }
const p = { filter: { property: props.title, title: { contains: q } }, page_size: 50 };
process.stdout.write(JSON.stringify(p));
' "$q" "$props_json")"

    request POST "$api/databases/$db_id/query" "$payload"
    ;;

  next)
    alias="${1:-}"
    if [[ -z "$alias" ]]; then
      echo 'Usage: notion_mvp.sh next <alias>' >&2
      exit 1
    fi
    db_id="$(resolve_db_id "$alias")"
    props_json="$(get_props_json "$db_id")"
    raw="$(request POST "$api/databases/$db_id/query" '{"page_size":100}')"

    node -e '
const [raw,propsRaw] = process.argv.slice(1);
const props = JSON.parse(propsRaw);
const j = JSON.parse(raw);
if (j.object === "error") { console.log(JSON.stringify(j)); process.exit(0); }
const today = new Date().toISOString().slice(0,10);
const getText = (arr=[]) => (arr||[]).map(x => x?.plain_text || x?.text?.content || "").join("").trim();
const items = (j.results||[]).map(r => {
  const p=r.properties||{};
  const bloco = getText(p[props.title]?.title);
  const data = p[props.date]?.date?.start || "";
  const hora = props.time ? getText(p[props.time]?.rich_text) : "";
  const local = props.location ? getText(p[props.location]?.rich_text) : "";
  return {bloco,data,hora,local,id:r.id,url:r.url};
}).filter(x => /^\d{4}-\d{2}-\d{2}/.test(x.data));
items.sort((a,b)=> (a.data+a.hora).localeCompare(b.data+b.hora));
const next = items.find(x => x.data.slice(0,10) >= today) || null;
console.log(JSON.stringify({today, next, total: items.length}));
' "$raw" "$props_json"
    ;;

  *)
    cat >&2 <<'TXT'
Usage:
  notion_mvp.sh aliases
  notion_mvp.sh add <alias> "<bloco>" [YYYY-MM-DD] [HH:MM] ["<local>"]
  notion_mvp.sh today <alias>
  notion_mvp.sh query <alias> "<text>"
  notion_mvp.sh next <alias>
TXT
    exit 1
    ;;
esac
