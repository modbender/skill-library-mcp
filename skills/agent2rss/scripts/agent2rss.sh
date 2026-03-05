#!/usr/bin/env bash
set -euo pipefail

# Agent2RSS helper (macOS/Linux)
# Subcommands:
#   init [--server-url URL]             初始化配置（默认官方服务）
#   health                              健康检查
#   create-channel <name> [desc]        创建频道并写入配置，设为默认
#   update-channel <channelId> <name> <desc>  更新频道名称/描述（需 token）
#   list                                列出本地配置的频道
#   set-default <channelId>             设置当前默认频道
#   push-file <path> [idempotencyKey] [channelId]
#   push-json <file|-> [idempotencyKey] [channelId]
#
# 环境变量：
#   CONFIG_DIR (默认 ~/.openclaw/workspace/.skill-data/agent2rss-client)
#   CONFIG_FILE (默认 $CONFIG_DIR/config.json)
#   SERVER_URL (默认 config.json 里的 serverUrl)
#   DRY_RUN=1 (打印请求，不实际发送)

CONFIG_DIR="${CONFIG_DIR:-$HOME/.openclaw/workspace/.skill-data/agent2rss-client}"
CONFIG_FILE="${CONFIG_FILE:-$CONFIG_DIR/config.json}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="$SCRIPT_DIR/../assets/config-template.json"
DEFAULT_SERVER="https://agent2rss.yaotutu.top:8765"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "缺少依赖: $1" >&2; exit 1; }
}

load_field() {
  local jq_filter=$1
  jq -er "$jq_filter" "$CONFIG_FILE" 2>/dev/null
}

save_json() {
  local tmp="$CONFIG_FILE.tmp"
  cat >"$tmp"
  mv "$tmp" "$CONFIG_FILE"
}

ensure_secure_perms() {
  chmod 600 "$CONFIG_FILE" 2>/dev/null || true
}

warn_if_remote_or_insecure() {
  local url=$1
  case "$url" in
    http://127.0.0.1*|http://localhost*|https://127.0.0.1*|https://localhost*)
      ;;
    http://*)
      echo "⚠️ 警告：你正在使用非 HTTPS 的远程地址：$url" >&2
      echo "   建议改为 HTTPS，或使用你信任的自部署实例。" >&2
      ;;
    https://*)
      echo "ℹ️ 当前使用远程服务：$url" >&2
      echo "   请确认该服务由你信任的主体维护。" >&2
      ;;
    *)
      echo "serverUrl 必须是 http/https" >&2
      exit 1
      ;;
  esac
}

http_call() {
  if [ "${DRY_RUN:-0}" = "1" ]; then
    echo "[DRY_RUN] curl $*"
    return 0
  fi
  curl "$@"
}

parse_init_args() {
  local url=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --server-url)
        shift
        url="${1:-}"
        [ -n "$url" ] || { echo "--server-url 需要参数" >&2; exit 1; }
        ;;
      -h|--help)
        echo "用法: $0 init [--server-url URL]"; exit 0 ;;
      *)
        # 兼容旧格式：init <url>
        url="$1"
        ;;
    esac
    shift || true
  done
  echo "${url:-$DEFAULT_SERVER}"
}

init() {
  need_cmd curl; need_cmd jq
  mkdir -p "$CONFIG_DIR"
  local url
  url=$(parse_init_args "$@")

  if [ ! -f "$CONFIG_FILE" ]; then
    cp "$TEMPLATE" "$CONFIG_FILE"
  fi

  warn_if_remote_or_insecure "$url"
  jq --arg url "$url" '.serverUrl = $url' "$CONFIG_FILE" | save_json
  ensure_secure_perms

  local sv
  sv=$(load_field '.serverUrl') || { echo "config 缺少 serverUrl"; exit 1; }
  warn_if_remote_or_insecure "$sv"

  echo "配置已写入 $CONFIG_FILE (serverUrl=$sv)"
  echo "提示：init 不会自动创建频道；请显式执行 create-channel。"
}

health() {
  need_cmd curl
  local sv="${SERVER_URL:-$(load_field '.serverUrl')}"
  warn_if_remote_or_insecure "$sv"
  echo "GET $sv/health"
  http_call -fsS "$sv/health"
}

current_channel_id() {
  load_field '.currentChannelId // empty'
}

channel_token() {
  local id=$1
  jq -er --arg id "$id" '.channels[] | select(.id==$id) | .token' "$CONFIG_FILE"
}

channel_posts_url() {
  local id=$1
  local sv="${SERVER_URL:-$(load_field '.serverUrl')}"
  echo "$sv/api/channels/$id/posts"
}

channel_upload_url() {
  local id=$1
  local sv="${SERVER_URL:-$(load_field '.serverUrl')}"
  echo "$sv/api/channels/$id/posts/upload"
}

create_channel() {
  need_cmd curl; need_cmd jq
  local sv="${SERVER_URL:-$(load_field '.serverUrl')}"
  local name=${1:?"缺少 name"}
  local desc=${2:-""}
  warn_if_remote_or_insecure "$sv"

  local resp
  resp=$(http_call -fsS -X POST "$sv/api/channels" -H 'Content-Type: application/json' -d "{\"name\":\"$name\",\"description\":\"$desc\"}")
  local id token
  id=$(echo "$resp" | jq -r '.channel.id // .id')
  token=$(echo "$resp" | jq -r '.channel.token // .token')
  [ -n "$id" ] && [ -n "$token" ] || { echo "创建频道失败，返回缺少 id/token"; exit 1; }

  jq --arg id "$id" --arg name "$name" --arg desc "$desc" --arg token "$token" --arg sv "$sv" \
    '.channels += [{id:$id,name:$name,description:$desc,token:$token,postsUrl:($sv+"/api/channels/"+$id+"/posts"),rssUrl:($sv+"/channels/"+$id+"/rss.xml")}] | .currentChannelId = $id' \
    "$CONFIG_FILE" | save_json
  ensure_secure_perms

  echo "创建成功: $name ($id)"
  echo "RSS: $sv/channels/$id/rss.xml"
}

list_channels() {
  need_cmd jq
  jq -r '. as $root | .channels[] | "• \(.name) (ID: \(.id)) | RSS: \(.rssUrl) | 默认: \(.id == $root.currentChannelId)"' "$CONFIG_FILE"
}

set_default() {
  need_cmd jq
  local id=${1:?"缺少 channelId"}
  jq --arg id "$id" '.currentChannelId = $id' "$CONFIG_FILE" | save_json
  ensure_secure_perms
  echo "已设置默认频道: $id"
}

update_channel() {
  need_cmd curl; need_cmd jq
  local cid=${1:?'缺少 channelId'}
  local name=${2:?'缺少 name'}
  local desc=${3:?'缺少 description'}
  local sv="${SERVER_URL:-$(load_field '.serverUrl')}"
  local token
  token=$(channel_token "$cid")
  warn_if_remote_or_insecure "$sv"

  http_call -fsS -X PUT "$sv/api/channels/$cid" \
    -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $token" \
    -d "{\"name\":\"$name\",\"description\":\"$desc\"}"
  echo
}

push_file() {
  need_cmd curl; need_cmd jq
  local file=${1:?"缺少文件路径"}
  [ -f "$file" ] || { echo "文件不存在: $file"; exit 1; }
  local key=${2:-"$(basename "$file")-$(date +%s)"}
  local cid=${3:-$(current_channel_id)}
  [ -n "$cid" ] || { echo "未找到默认频道，请传入 channelId 或先 set-default"; exit 1; }
  local token
  token=$(channel_token "$cid")
  local sv="${SERVER_URL:-$(load_field '.serverUrl')}"
  warn_if_remote_or_insecure "$sv"

  http_call -fsS -X POST "$(channel_upload_url "$cid")" \
    -H "Authorization: Bearer $token" \
    -F "file=@$file" \
    -F "idempotencyKey=$key"
}

push_json() {
  need_cmd curl; need_cmd jq
  local json_src=${1:?"缺少 JSON 文件或 -"}
  local key=${2:-"json-$(date +%s)"}
  local cid=${3:-$(current_channel_id)}
  [ -n "$cid" ] || { echo "未找到默认频道，请传入 channelId 或先 set-default"; exit 1; }
  local token
  token=$(channel_token "$cid")
  local sv="${SERVER_URL:-$(load_field '.serverUrl')}"
  warn_if_remote_or_insecure "$sv"

  local data
  if [ "$json_src" = "-" ]; then
    data=$(cat)
  else
    data=$(cat "$json_src")
  fi

  data=$(echo "$data" | jq -c --arg k "$key" '.idempotencyKey //= $k')
  http_call -fsS -X POST "$(channel_posts_url "$cid")" \
    -H "Authorization: Bearer $token" \
    -H 'Content-Type: application/json' \
    -d "$data"
}

usage() {
  sed -n '1,60p' "$0"
}

cmd=${1:-help}
shift || true
case "$cmd" in
  init) init "$@" ;;
  health) health "$@" ;;
  create-channel) create_channel "$@" ;;
  list) list_channels "$@" ;;
  set-default) set_default "$@" ;;
  update-channel) update_channel "$@" ;;
  push-file) push_file "$@" ;;
  push-json) push_json "$@" ;;
  help|--help|-h) usage ;;
  *) echo "未知子命令: $cmd"; usage; exit 1 ;;
esac
