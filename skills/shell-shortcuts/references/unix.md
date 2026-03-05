# macOS / Ubuntu (bash/zsh) Templates

Install location:

- zsh: `~/.zshrc`
- bash: `~/.bashrc` (or `~/.bash_profile`)

## proxy_on / proxy_off

```sh
proxy_on() {
  http_proxy_url="http://127.0.0.1:7890"
  socks_proxy_url="socks5://127.0.0.1:7890"
  no_proxy_list="localhost,127.0.0.1,.qualcomm.com,*.amazonaws.com"

  proxy_off >/dev/null 2>&1

  export http_proxy="$http_proxy_url"
  export https_proxy="$http_proxy_url"
  export HTTP_PROXY="$http_proxy_url"
  export HTTPS_PROXY="$http_proxy_url"

  export all_proxy="$socks_proxy_url"
  export ALL_PROXY="$socks_proxy_url"

  export no_proxy="$no_proxy_list"
  export NO_PROXY="$no_proxy_list"

  command -v git >/dev/null 2>&1 && git config --global http.proxy "$http_proxy_url"
  command -v git >/dev/null 2>&1 && git config --global https.proxy "$http_proxy_url"

  echo "Proxy is ON"
  echo "  HTTP/HTTPS: $http_proxy_url"
  echo "  SOCKS5:     $socks_proxy_url"
  echo "  NO_PROXY:   $no_proxy_list"
}

proxy_off() {
  unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY no_proxy NO_PROXY
  command -v git >/dev/null 2>&1 && git config --global --unset http.proxy >/dev/null 2>&1
  command -v git >/dev/null 2>&1 && git config --global --unset https.proxy >/dev/null 2>&1
  echo "Proxy is OFF"
}
```

## goto (portable: zsh/bash without associative arrays)

Persistent DB: `~/.goto_paths` (format: `key<TAB>/abs/path`).

```sh
GOTO_DB="$HOME/.goto_paths"

_goto_absdir() {
  p="$1"
  [ -z "$p" ] && return 1
  p="${p/#\~/$HOME}"
  (cd "$p" 2>/dev/null && pwd -P)
}

_goto_list() {
  echo "Available shortcuts:"
  [ -f "$GOTO_DB" ] || return 0
  awk -F'\t' 'NF>=2 {printf "  %-12s -> %s\n", $1, $2}' "$GOTO_DB" | sort
}

_goto_set() {
  key="$1"; path="$2"
  tmp="${GOTO_DB}.tmp"
  mkdir -p "$(dirname "$GOTO_DB")" 2>/dev/null
  [ -f "$GOTO_DB" ] || : >"$GOTO_DB"
  awk -F'\t' -v k="$key" '$1!=k {print $0}' "$GOTO_DB" >"$tmp" && mv "$tmp" "$GOTO_DB"
  printf "%s\t%s\n" "$key" "$path" >>"$GOTO_DB"
}

_goto_del() {
  key="$1"
  [ -f "$GOTO_DB" ] || return 0
  tmp="${GOTO_DB}.tmp"
  awk -F'\t' -v k="$key" '$1!=k {print $0}' "$GOTO_DB" >"$tmp" && mv "$tmp" "$GOTO_DB"
}

goto() {
  cmd="$1"
  case "$cmd" in
    ""|ls|list)
      _goto_list
      ;;
    add)
      key="$2"; shift 2
      path="$*"
      [ -z "$key" ] || [ -z "$path" ] && { echo "Usage: goto add <shortcut> <path>"; return 1; }
      abs="$(_goto_absdir "$path")" || { echo "Invalid path: $path"; return 1; }
      _goto_set "$key" "$abs"
      echo "Added: $key -> $abs"
      ;;
    rm|remove|del)
      key="$2"
      [ -z "$key" ] && { echo "Usage: goto remove <shortcut>"; return 1; }
      _goto_del "$key"
      echo "Removed: $key"
      ;;
    clear|removeAll|rmAll)
      : >"$GOTO_DB"
      echo "All shortcuts cleared."
      ;;
    *)
      target=""
      [ -f "$GOTO_DB" ] && target="$(awk -F'\t' -v k="$cmd" '$1==k {print $2; exit}' "$GOTO_DB")"
      if [ -n "$target" ]; then
        cd "$target" || return 1
      else
        echo "Unknown shortcut: $cmd"
        echo "Tip: goto list"
        return 1
      fi
      ;;
  esac
}
```

## gpu (Ubuntu only, NVIDIA)

```sh
gpu() {
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "nvidia-smi not found (need NVIDIA driver + tools)"
    return 1
  fi

  echo "======== GPU Overview ========"
  printf "%-3s %-25s %-6s %-6s %-8s %-20s %-6s\n" "ID" "Name" "Temp" "Fan" "Power" "VRAM" "Util"

  nvidia-smi --query-gpu=index,name,temperature.gpu,fan.speed,power.draw,memory.used,memory.total,utilization.gpu \
    --format=csv,noheader,nounits 2>/dev/null | \
  awk -F', ' '{
    name = substr($2, 1, 24);
    printf "%-3s %-25s %-6s %-6s %-8s %-6s / %-5s MB %-6s\n",
      $1, name, $3"C", $4"%", $5"W", $6, $7, $8"%"
  }'
}
```

