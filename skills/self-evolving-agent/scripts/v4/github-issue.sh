#!/usr/bin/env bash
# ============================================================
# github-issue.sh — Self-Evolving Agent v4.1 GitHub 이슈 통합
#
# 역할:
#   1. 각 제안에 대해 GitHub Issue 생성 (GH_TOKEN 필요)
#      - 레이블: self-evolving, 심각도 레이블
#      - Assignee: 레포 소유자
#      - 본문: 제안 마크다운 + before/after diff
#   2. `sea approve`로 승인 시 이슈 자동 종료 + 코멘트
#   3. 레이블 자동 생성 (없을 시)
#
# 사용법:
#   bash github-issue.sh create <proposal_file>     # 이슈 생성
#   bash github-issue.sh create --all               # 모든 pending 제안 이슈 생성
#   bash github-issue.sh close  <proposal_id>       # 이슈 종료 (승인 시)
#   bash github-issue.sh sync                       # proposals/ 와 이슈 동기화
#   bash github-issue.sh list                       # self-evolving 레이블 이슈 목록
#
# 환경변수:
#   GH_TOKEN        GitHub Personal Access Token (필수)
#   GH_REPO         owner/repo 형식 (기본: git remote에서 자동 감지)
#   GH_ASSIGNEE     기본 Assignee (기본: 레포 소유자)
#
# 변경 이력:
#   v4.1 (2026-02-18) — 신규 구현
# ============================================================

# SECURITY MANIFEST:
# Environment variables: GH_TOKEN, GH_REPO, GH_ASSIGNEE
# External endpoints: api.github.com (GitHub REST API)
# Local files read: data/proposals/*.json, /tmp/sea-v4/proposal.md
# Local files written: data/proposals/*.json (issue_number 필드 추가)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROPOSALS_DIR="${SKILL_DIR}/data/proposals"
TMP_DIR="${SEA_TMP_DIR:-/tmp/sea-v4}"

# ── 색상 ──────────────────────────────────────────────────
R=$'\033[0;31m'; G=$'\033[0;32m'; Y=$'\033[1;33m'
C=$'\033[0;36m'; B=$'\033[1m';    N=$'\033[0m'

die()  { echo -e "${R}[github-issue] Error: $*${N}" >&2; exit 1; }
info() { echo -e "${C}[github-issue] $*${N}" >&2; }
ok()   { echo -e "${G}[github-issue] $*${N}" >&2; }
warn() { echo -e "${Y}[github-issue] $*${N}" >&2; }

# ── 사전 조건 확인 ────────────────────────────────────────
check_prereqs() {
  command -v curl    &>/dev/null || die "curl 필요"
  command -v python3 &>/dev/null || die "python3 필요"
  [ -n "${GH_TOKEN:-}" ] || die "GH_TOKEN 환경변수 필요 (GitHub PAT)"
}

# ── 레포 자동 감지 ────────────────────────────────────────
detect_repo() {
  if [ -n "${GH_REPO:-}" ]; then
    echo "$GH_REPO"
    return
  fi
  # git remote에서 추출
  local remote
  remote=$(git -C "$SKILL_DIR" remote get-url origin 2>/dev/null \
    || git -C "${HOME}/openclaw" remote get-url origin 2>/dev/null \
    || echo "")
  if [ -n "$remote" ]; then
    # SSH: git@github.com:owner/repo.git
    # HTTPS: https://github.com/owner/repo.git
    echo "$remote" | sed -E 's|.*github\.com[:/]||; s|\.git$||'
  else
    die "GH_REPO 미설정이고 git remote에서 레포를 감지할 수 없음.\n환경변수 설정: export GH_REPO=owner/repo"
  fi
}

# ── GitHub API 공통 호출 ──────────────────────────────────
gh_api() {
  local method="$1" path="$2" data="${3:-}"
  local url="https://api.github.com${path}"
  local args=(-sf -X "$method" \
    -H "Authorization: Bearer ${GH_TOKEN}" \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -H "Content-Type: application/json" \
    --max-time 20)
  [ -n "$data" ] && args+=(-d "$data") || true
  curl "${args[@]}" "$url" 2>&1
}

# ── 레이블 존재 확인 + 없으면 생성 ──────────────────────
ensure_label() {
  local repo="$1" name="$2" color="${3:-0075ca}" desc="${4:-}"
  # 존재 확인
  local exists
  exists=$(gh_api GET "/repos/${repo}/labels/${name}" 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('name',''))" 2>/dev/null || echo "")
  if [ -z "$exists" ]; then
    local payload
    payload=$(python3 -c "import json; print(json.dumps({'name':'$name','color':'$color','description':'$desc'}))" 2>/dev/null || echo "{}")
    gh_api POST "/repos/${repo}/labels" "$payload" > /dev/null 2>&1 \
      && info "레이블 생성: $name" \
      || warn "레이블 생성 실패: $name (이미 있거나 권한 부족)"
  fi
}

# ── 레이블 초기화 ────────────────────────────────────────
init_labels() {
  local repo="$1"
  ensure_label "$repo" "self-evolving"           "1d76db" "Self-Evolving Agent 자동 생성"
  ensure_label "$repo" "severity:critical"       "b60205" "심각도: Critical"
  ensure_label "$repo" "severity:high"           "e4e669" "심각도: High"
  ensure_label "$repo" "severity:medium"         "fbca04" "심각도: Medium"
  ensure_label "$repo" "severity:low"            "0e8a16" "심각도: Low"
  ensure_label "$repo" "status:pending-review"   "d93f0b" "승인 대기 중"
  ensure_label "$repo" "status:approved"         "0e8a16" "승인됨"
  ensure_label "$repo" "status:rejected"         "e4e669" "거부됨"
  ensure_label "$repo" "agent-proposal"          "5319e7" "Agent 제안"
}

# ── 제안 파일 필드 추출 ───────────────────────────────────
pfield() {
  local file="$1" key="$2" default="${3:-}"
  python3 -c "
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    val = d.get(sys.argv[2], sys.argv[3])
    print(val if val is not None else sys.argv[3])
except:
    print(sys.argv[3])
" "$file" "$key" "$default" 2>/dev/null || echo "$default"
}

# ── 이슈 본문 생성 ───────────────────────────────────────
build_issue_body() {
  local file="$1"
  python3 - "$file" "$SKILL_DIR" <<'PYEOF'
import json, sys, datetime, os

fpath = sys.argv[1]
skill_dir = sys.argv[2]

try:
    d = json.load(open(fpath, encoding="utf-8"))
except Exception as e:
    print(f"제안 파일 로드 실패: {e}")
    sys.exit(1)

prop_id   = d.get("id", "unknown")
title     = d.get("title", "제목 없음")
severity  = d.get("severity", "medium")
section   = d.get("section", "AGENTS.md 일반")
evidence  = d.get("evidence", "근거 없음")
before    = d.get("before", "")
after     = d.get("after", "")
created   = d.get("created_at", datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"))
diff_type = d.get("diff_type", "agents_md_addition")

sev_icon = {"critical": "🔴", "high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "🟡")

body = f"""## 🤖 Self-Evolving Agent — 자동 생성 제안

> 이 이슈는 [Self-Evolving Agent v4.1](https://github.com/search?q=self-evolving-agent)이 자동 생성했습니다.
> 승인: `sea approve {prop_id}` | 거부: `sea reject {prop_id} "이유"`

---

### 메타데이터

| 항목 | 값 |
|------|----|
| **ID** | `{prop_id}` |
| **심각도** | {sev_icon} {severity} |
| **대상 섹션** | {section} |
| **변경 유형** | {diff_type} |
| **생성 시각** | {created} |

---

### 📋 근거 (Evidence)

```
{evidence}
```

---

### 🔴 Before (현재 상태)

```
{before if before else "(변경 전 내용 없음 — 신규 추가)"}
```

### 🟢 After (적용 시 변경)

```
{after if after else "(변경 후 내용 없음)"}
```

---

### 적용 방법

```bash
# 터미널에서 직접 적용
sea approve {prop_id}

# 거부
sea reject {prop_id} "거부 이유"

# watch 모드 (대화형)
sea watch
```

---

*generated by self-evolving-agent v4.1 — {datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}*
"""

print(body)
PYEOF
}

# ── 이슈 생성 ─────────────────────────────────────────────
create_issue() {
  local file="$1" repo="$2"

  [ -f "$file" ] || die "파일 없음: $file"

  local prop_id title severity
  prop_id=$(pfield "$file" id "unknown")
  title=$(pfield "$file" title "제목 없음")
  severity=$(pfield "$file" severity "medium")

  # 이미 이슈 있으면 건너뜀
  local existing_issue
  existing_issue=$(pfield "$file" github_issue_number "")
  if [ -n "$existing_issue" ]; then
    warn "이슈 이미 존재: #${existing_issue} — 건너뜀 ($prop_id)"
    return 0
  fi

  # pending 상태만 처리
  local status
  status=$(pfield "$file" status "pending")
  [ "$status" = "pending" ] || { warn "$prop_id 는 pending 아님 ($status) — 건너뜀"; return 0; }

  info "이슈 생성 중: $prop_id ($title)"

  # 레이블 배열
  local labels=("self-evolving" "agent-proposal" "severity:${severity}" "status:pending-review")

  # Assignee (레포 소유자 = repo의 첫 번째 부분)
  local assignee="${GH_ASSIGNEE:-$(echo "$repo" | cut -d/ -f1)}"

  # 이슈 본문
  local body
  body=$(build_issue_body "$file")

  # JSON 페이로드
  local payload
  payload=$(python3 - "$title" "$body" "$assignee" <<PYEOF
import json, sys
title, body, assignee = sys.argv[1], sys.argv[2], sys.argv[3]
labels = ["self-evolving", "agent-proposal", "severity:${severity}", "status:pending-review"]
data = {
    "title": f"[SEA] {title}",
    "body": body,
    "labels": labels,
}
if assignee:
    data["assignees"] = [assignee]
print(json.dumps(data))
PYEOF
)

  # API 호출
  local response
  response=$(gh_api POST "/repos/${repo}/issues" "$payload")

  local issue_num issue_url
  issue_num=$(echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('number',''))" 2>/dev/null || echo "")
  issue_url=$(echo "$response" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('html_url',''))" 2>/dev/null || echo "")

  if [ -z "$issue_num" ]; then
    warn "이슈 생성 실패 — API 응답:"
    echo "$response" | head -5 >&2
    return 1
  fi

  ok "✅ 이슈 생성됨: #${issue_num} — ${issue_url}"

  # 제안 JSON에 이슈 번호 저장
  python3 - "$file" "$issue_num" "$issue_url" <<'PYEOF'
import json, sys, datetime
fpath, issue_num, issue_url = sys.argv[1], int(sys.argv[2]), sys.argv[3]
d = json.load(open(fpath, encoding="utf-8"))
d["github_issue_number"] = issue_num
d["github_issue_url"]    = issue_url
d["github_issue_created_at"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
json.dump(d, open(fpath, 'w', encoding="utf-8"), ensure_ascii=False, indent=2)
PYEOF

  echo "$issue_num"
}

# ── 이슈 종료 (승인 시) ────────────────────────────────────
close_issue() {
  local prop_id="$1" repo="$2"
  local comment="${3:-}"

  # 제안 파일 찾기
  local file=""
  for f in "${PROPOSALS_DIR}"/*.json; do
    [ -f "$f" ] || continue
    local fid; fid=$(pfield "$f" id "")
    [ "$fid" = "$prop_id" ] && { file="$f"; break; }
  done

  [ -z "$file" ] && die "제안 파일 없음: $prop_id"

  local issue_num
  issue_num=$(pfield "$file" github_issue_number "")
  [ -z "$issue_num" ] && { warn "이슈 번호 없음: $prop_id (GitHub 이슈 없이 승인됨)"; return 0; }

  info "이슈 #${issue_num} 종료 중..."

  # 종료 코멘트
  local default_comment="✅ **제안 승인 및 적용됨**

제안 \`${prop_id}\`가 \`sea approve\`를 통해 승인 및 AGENTS.md에 적용되었습니다.

_closed by self-evolving-agent v4.1_"

  local final_comment="${comment:-$default_comment}"

  # 코멘트 추가
  local comment_payload
  comment_payload=$(python3 -c "import json; print(json.dumps({'body': '$final_comment'}))" 2>/dev/null \
    || echo "{\"body\":\"제안 승인됨\"}")
  gh_api POST "/repos/${repo}/issues/${issue_num}/comments" "$comment_payload" > /dev/null 2>&1 \
    && info "코멘트 추가됨" \
    || warn "코멘트 추가 실패"

  # 이슈 상태를 closed로 변경 + 레이블 업데이트
  local close_payload='{"state":"closed","state_reason":"completed"}'
  gh_api PATCH "/repos/${repo}/issues/${issue_num}" "$close_payload" > /dev/null 2>&1 \
    && ok "✅ 이슈 #${issue_num} 종료됨" \
    || warn "이슈 종료 실패 (수동 종료 필요)"

  # 레이블 업데이트: pending-review → approved
  local label_payload='{"labels":["self-evolving","agent-proposal","status:approved"]}'
  gh_api PATCH "/repos/${repo}/issues/${issue_num}" "$label_payload" > /dev/null 2>&1 || true

  # 제안 JSON에 종료 기록
  python3 - "$file" "$issue_num" <<'PYEOF'
import json, sys, datetime
fpath, issue_num = sys.argv[1], sys.argv[2]
d = json.load(open(fpath, encoding="utf-8"))
d["github_issue_closed_at"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
json.dump(d, open(fpath, 'w', encoding="utf-8"), ensure_ascii=False, indent=2)
PYEOF
}

# ── 동기화 (proposals/ ↔ GitHub Issues) ──────────────────
sync_issues() {
  local repo="$1"
  info "제안 ↔ GitHub 이슈 동기화 중..."

  local created=0 skipped=0 closed=0

  for f in "${PROPOSALS_DIR}"/*.json; do
    [ -f "$f" ] || continue
    local status prop_id
    status=$(pfield "$f" status "pending")
    prop_id=$(pfield "$f" id "unknown")

    case "$status" in
      pending)
        local issue_num
        issue_num=$(pfield "$f" github_issue_number "")
        if [ -z "$issue_num" ]; then
          create_issue "$f" "$repo" > /dev/null 2>&1 && created=$((created+1)) || true
        else
          skipped=$((skipped+1))
        fi
        ;;
      applied)
        local issue_num
        issue_num=$(pfield "$f" github_issue_number "")
        local closed_at
        closed_at=$(pfield "$f" github_issue_closed_at "")
        if [ -n "$issue_num" ] && [ -z "$closed_at" ]; then
          close_issue "$prop_id" "$repo" > /dev/null 2>&1 && closed=$((closed+1)) || true
        fi
        ;;
    esac
  done

  ok "동기화 완료: 생성=${created}, 건너뜀=${skipped}, 종료=${closed}"
}

# ── 이슈 목록 ────────────────────────────────────────────
list_issues() {
  local repo="$1"
  info "GitHub 이슈 목록 (self-evolving)..."
  local response
  response=$(gh_api GET "/repos/${repo}/issues?labels=self-evolving&state=all&per_page=20")
  echo "$response" | python3 - <<'PYEOF'
import json, sys
try:
    issues = json.load(sys.stdin)
    if not isinstance(issues, list):
        print("이슈 없음 또는 API 오류")
        sys.exit(0)
    state_icons = {"open": "🟡", "closed": "✅"}
    for iss in issues:
        num   = iss.get("number", "?")
        title = iss.get("title", "?")
        state = iss.get("state", "?")
        icon  = state_icons.get(state, "❓")
        url   = iss.get("html_url", "")
        labels = [l["name"] for l in iss.get("labels", [])]
        sev = next((l.split(":")[1] for l in labels if l.startswith("severity:")), "?")
        print(f"{icon} #{num} [{sev}] {title}")
        print(f"   {url}")
    if not issues:
        print("self-evolving 레이블 이슈 없음")
except json.JSONDecodeError:
    print("API 응답 파싱 실패 (토큰 또는 레포 확인 필요)")
PYEOF
}

# ── 메인 ─────────────────────────────────────────────────
main() {
  local cmd="${1:-}" ; shift 2>/dev/null || true

  # --help는 prereq 체크 없이 먼저 처리
  case "$cmd" in
    --help|-h|help)
      cat <<EOF
Usage: bash github-issue.sh <command> [options]

  create <file|id>   제안 파일/ID로 GitHub 이슈 생성
  create --all       모든 pending 제안 이슈 생성
  close  <id>        제안 승인 후 이슈 종료
  sync               proposals/ ↔ GitHub 이슈 동기화
  list               self-evolving 이슈 목록
  labels             레이블 초기화

환경변수:
  GH_TOKEN        GitHub PAT (필수 — repo 권한 필요)
  GH_REPO         owner/repo (기본: git remote에서 감지)
  GH_ASSIGNEE     Assignee 사용자명 (기본: 레포 소유자)

예시:
  export GH_TOKEN=ghp_xxxx
  bash github-issue.sh create --all
  bash github-issue.sh close prop-20260218-001
  bash github-issue.sh sync
EOF
      return 0 ;;
  esac

  check_prereqs
  local repo
  repo=$(detect_repo)
  info "레포: $repo"

  case "$cmd" in
    create)
      # 레이블 초기화
      init_labels "$repo"
      if [ "${1:-}" = "--all" ]; then
        local n=0
        for f in "${PROPOSALS_DIR}"/*.json; do
          [ -f "$f" ] || continue
          [ "$(pfield "$f" status "pending")" = "pending" ] || continue
          create_issue "$f" "$repo" > /dev/null && n=$((n+1)) || true
        done
        ok "총 ${n}개 이슈 생성됨"
      else
        local file="${1:-}"
        [ -z "$file" ] && die "사용법: github-issue.sh create <proposal_file>"
        # ID로 찾기
        if [ ! -f "$file" ]; then
          for f in "${PROPOSALS_DIR}"/*.json; do
            [ -f "$f" ] || continue
            [ "$(pfield "$f" id "")" = "$file" ] && { file="$f"; break; }
          done
        fi
        [ -f "$file" ] || die "파일/ID 없음: $1"
        init_labels "$repo"
        create_issue "$file" "$repo"
      fi
      ;;

    close)
      local prop_id="${1:-}"
      [ -z "$prop_id" ] && die "사용법: github-issue.sh close <proposal_id>"
      local comment="${2:-}"
      close_issue "$prop_id" "$repo" "$comment"
      ;;

    sync)
      init_labels "$repo"
      sync_issues "$repo"
      ;;

    list)
      list_issues "$repo"
      ;;

    labels)
      info "레이블 초기화..."
      init_labels "$repo"
      ok "레이블 초기화 완료"
      ;;

    *)
      warn "알 수 없는 명령: ${cmd:-없음}"
      echo ""
      exec bash "$0" --help
      ;;
  esac
}

main "$@"
