#!/usr/bin/env bash
# ============================================================
# export-report.sh — Self-Evolving Agent v4.1 리포트 내보내기
#
# 역할: 주간 제안 리포트를 다양한 형식으로 내보냄
#   - Markdown (기본, 이미 존재)
#   - HTML    (이메일/웹용 — 스타일 포함)
#   - JSON    (API 소비용 — 구조화된 데이터)
#   - PDF     (pandoc 필요)
#
# 사용법:
#   bash export-report.sh                         # Markdown 출력 (stdout)
#   bash export-report.sh --format html           # HTML stdout
#   bash export-report.sh --format html --output report.html
#   bash export-report.sh --format json --output report.json
#   bash export-report.sh --format pdf  --output report.pdf
#   bash export-report.sh --format all  --output-dir ./reports/
#
# 환경변수:
#   SEA_TMP_DIR   임시 디렉토리 (기본: /tmp/sea-v4)
#   SEA_REPORT_TITLE  리포트 제목 (기본: Self-Evolving Agent 주간 리포트)
#
# 변경 이력:
#   v4.1 (2026-02-18) — 신규 구현
# ============================================================

# SECURITY MANIFEST:
# External endpoints: None
# Local files read: /tmp/sea-v4/proposal.md, data/proposals/*.json
# Local files written: --output 경로 (사용자 지정)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
TMP_DIR="${SEA_TMP_DIR:-/tmp/sea-v4}"
PROPOSALS_DIR="${SKILL_DIR}/data/proposals"
PROPOSAL_MD="${TMP_DIR}/proposal.md"
REPORT_TITLE="${SEA_REPORT_TITLE:-Self-Evolving Agent 주간 리포트}"

# 기본값
FORMAT="markdown"
OUTPUT_FILE=""
OUTPUT_DIR=""
VERBOSE=false

# ── 색상 ──────────────────────────────────────────────────
R=$'\033[0;31m'; G=$'\033[0;32m'; Y=$'\033[1;33m'
C=$'\033[0;36m'; B=$'\033[1m';    N=$'\033[0m'

die()  { echo -e "${R}[export-report] Error: $*${N}" >&2; exit 1; }
info() { echo -e "${C}[export-report] $*${N}" >&2; }
ok()   { echo -e "${G}[export-report] $*${N}" >&2; }

# ── 인수 파싱 ────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --format|-f)    FORMAT="${2:-markdown}"; shift 2 ;;
    --output|-o)    OUTPUT_FILE="${2:-}"; shift 2 ;;
    --output-dir)   OUTPUT_DIR="${2:-}"; shift 2 ;;
    --input|-i)     PROPOSAL_MD="${2:-}"; shift 2 ;;
    --verbose|-v)   VERBOSE=true; shift ;;
    --help|-h)
      cat <<EOF
Usage: bash export-report.sh [OPTIONS]

  --format <fmt>         출력 형식: markdown | html | json | pdf | all
  --output <file>        출력 파일 경로 (생략 시 stdout)
  --output-dir <dir>     --format all 시 디렉토리
  --verbose              상세 로그
  --help                 이 도움말

형식별 요구사항:
  markdown  — 추가 의존성 없음
  html      — python3 (마크다운 변환) 또는 pandoc
  json      — python3
  pdf       — pandoc + wkhtmltopdf 또는 pdflatex

예시:
  bash export-report.sh --format html --output ~/report.html
  bash export-report.sh --format json --output ~/report.json
  bash export-report.sh --format all  --output-dir ~/sea-reports/
EOF
      exit 0 ;;
    *) die "알 수 없는 옵션: $1" ;;
  esac
done

# ── 소스 마크다운 가져오기 ───────────────────────────────
get_markdown_content() {
  if [ -f "$PROPOSAL_MD" ]; then
    cat "$PROPOSAL_MD"
  elif [ -f "${TMP_DIR}/proposal.md" ]; then
    cat "${TMP_DIR}/proposal.md"
  else
    # 최신 proposal JSON에서 직접 생성
    warn() { echo -e "${Y}[export-report] $*${N}" >&2; }
    warn "proposal.md 없음 — 제안 JSON에서 기본 마크다운 생성"
    {
      echo "# ${REPORT_TITLE}"
      echo ""
      echo "> 생성: $(TZ='Asia/Seoul' date '+%Y-%m-%d %H:%M KST' 2>/dev/null || date '+%Y-%m-%d %H:%M')"
      echo ""
      for f in "${PROPOSALS_DIR}"/*.json; do
        [ -f "$f" ] || continue
        python3 - "$f" <<'PYEOF' 2>/dev/null || true
import json, sys
d = json.load(open(sys.argv[1]))
if d.get("status","pending") == "pending":
    sev = d.get("severity", "medium")
    icon = {"high":"🔴","critical":"🔴","medium":"🟡","low":"🟢"}.get(sev,"🟡")
    print(f"## {icon} {d.get('title','제목 없음')}")
    print(f"\n**ID:** `{d.get('id','?')}` | **심각도:** {sev}\n")
    if d.get("evidence"):
        print(f"**근거:** {d['evidence']}\n")
    if d.get("before"):
        print(f"```\n{d['before']}\n```\n")
    if d.get("after"):
        print(f"→ 변경 후:\n```\n{d['after']}\n```\n")
    print("---\n")
PYEOF
      done
    }
  fi
}

# ── HTML CSS 스타일 ───────────────────────────────────────
HTML_CSS='
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    max-width: 900px; margin: 0 auto; padding: 20px 40px;
    background: #0d1117; color: #e6edf3; line-height: 1.6;
  }
  h1 { color: #58a6ff; border-bottom: 2px solid #30363d; padding-bottom: 10px; }
  h2 { color: #79c0ff; border-bottom: 1px solid #30363d; padding-bottom: 6px; margin-top: 32px; }
  h3 { color: #d2a8ff; margin-top: 24px; }
  code { background: #161b22; padding: 2px 6px; border-radius: 4px;
         font-family: "SF Mono", Consolas, monospace; font-size: 0.9em; color: #ff7b72; }
  pre  { background: #161b22; border: 1px solid #30363d; border-radius: 8px;
         padding: 16px; overflow-x: auto; }
  pre code { background: none; padding: 0; color: #e6edf3; }
  table { border-collapse: collapse; width: 100%; margin: 16px 0; }
  th { background: #161b22; color: #79c0ff; padding: 8px 12px; text-align: left;
       border: 1px solid #30363d; }
  td { padding: 8px 12px; border: 1px solid #30363d; }
  tr:nth-child(even) { background: #161b22; }
  blockquote { border-left: 4px solid #3fb950; padding: 8px 16px;
               margin: 0; background: #0d1117; color: #8b949e; }
  hr { border: none; border-top: 1px solid #30363d; margin: 24px 0; }
  .badge-high     { color: #ff7b72; font-weight: bold; }
  .badge-medium   { color: #e3b341; font-weight: bold; }
  .badge-low      { color: #3fb950; font-weight: bold; }
  .meta           { color: #8b949e; font-size: 0.9em; margin-bottom: 20px; }
  .footer         { color: #6e7681; font-size: 0.85em; margin-top: 40px;
                    border-top: 1px solid #30363d; padding-top: 16px; }
'

# ── Markdown → HTML 변환 ─────────────────────────────────
convert_to_html() {
  local md_content="$1"
  local title="${2:-${REPORT_TITLE}}"
  local now
  now=$(TZ="Asia/Seoul" date '+%Y-%m-%d %H:%M KST' 2>/dev/null || date '+%Y-%m-%d %H:%M')

  # pandoc 우선, 없으면 python3 내장 변환
  if command -v pandoc &>/dev/null; then
    local css_file; css_file=$(mktemp /tmp/sea-export-css.XXXXXX.css)
    echo "$HTML_CSS" > "$css_file"
    echo "$md_content" | pandoc \
      --from markdown --to html5 \
      --standalone \
      --metadata title="$title" \
      --css "$css_file" \
      2>/dev/null
    rm -f "$css_file"
  else
    # Python3 자체 변환 (기본 마크다운 요소 지원)
    # 마크다운 내용을 임시 파일로 전달 (stdin은 <<PYEOF 헤레독에 의해 소비됨)
    local _tmp_md; _tmp_md=$(mktemp /tmp/sea-html-XXXXXX.md)
    printf '%s\n' "$md_content" > "$_tmp_md"
    python3 - "$title" "$now" "$HTML_CSS" "$_tmp_md" <<PYEOF
import sys, re, html

title   = sys.argv[1]
now     = sys.argv[2]
css     = sys.argv[3]
md_file = sys.argv[4] if len(sys.argv) > 4 else None
content = open(md_file, 'r', encoding='utf-8').read() if md_file else sys.stdin.read()

def md_to_html(t):
    # 코드 블록 (먼저 처리)
    t = re.sub(r'\`\`\`(\w*)\n(.*?)\n\`\`\`', lambda m: f'<pre><code class="language-{m.group(1)}">{html.escape(m.group(2))}</code></pre>', t, flags=re.DOTALL)
    # 인라인 코드
    t = re.sub(r'\`([^\`]+)\`', lambda m: f'<code>{html.escape(m.group(1))}</code>', t)
    # 헤더
    for i in range(6, 0, -1):
        t = re.sub(rf'^{"#"*i} (.+)$', rf'<h{i}>\1</h{i}>', t, flags=re.MULTILINE)
    # 테이블
    lines = t.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if '|' in line and i+1 < len(lines) and re.match(r'^\|[-|: ]+\|$', lines[i+1]):
            # 테이블 감지
            headers = [c.strip() for c in line.split('|') if c.strip()]
            i += 2  # separator 건너뜀
            table_html = '<table>\n<thead><tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr></thead>\n<tbody>\n'
            while i < len(lines) and '|' in lines[i]:
                cells = [c.strip() for c in lines[i].split('|') if c.strip()]
                table_html += '<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>\n'
                i += 1
            table_html += '</tbody></table>'
            result.append(table_html)
        else:
            result.append(line)
            i += 1
    t = '\n'.join(result)
    # 굵게 / 이탤릭
    t = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', t)
    t = re.sub(r'\*\*(.+?)\*\*',     r'<strong>\1</strong>', t)
    t = re.sub(r'\*(.+?)\*',         r'<em>\1</em>', t)
    # 링크
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    # blockquote
    t = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', t, flags=re.MULTILINE)
    # HR
    t = re.sub(r'^---+$', '<hr>', t, flags=re.MULTILINE)
    # 문단
    paragraphs = re.split(r'\n\n+', t)
    result = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if re.match(r'^<(h[1-6]|hr|table|pre|blockquote|ul|ol)', p):
            result.append(p)
        else:
            lines_p = p.split('\n')
            if len(lines_p) > 1 and all(re.match(r'^[-*] ', l) or re.match(r'^\d+\. ', l) for l in lines_p if l.strip()):
                # 목록
                is_ordered = re.match(r'^\d+\. ', lines_p[0])
                tag = 'ol' if is_ordered else 'ul'
                _list_pat = re.compile(r'^[-*] |^\d+\. ')
                items = ''.join('<li>' + _list_pat.sub('', l.strip()) + '</li>' for l in lines_p if l.strip())
                result.append('<' + tag + '>' + items + '</' + tag + '>')
            else:
                result.append(f'<p>{p.replace(chr(10), "<br>")}</p>')
    return '\n'.join(result)

body = md_to_html(content)

print(f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <style>{css}</style>
</head>
<body>
  <div class="meta">📅 생성: {now} | 🤖 Self-Evolving Agent v4.1</div>
  {body}
  <div class="footer">
    generated by self-evolving-agent v4.1 export-report.sh — {now}
  </div>
</body>
</html>""")
PYEOF
    rm -f "$_tmp_md" 2>/dev/null || true
  fi
}

# ── Markdown → JSON 변환 ─────────────────────────────────
convert_to_json() {
  local now
  now=$(TZ="Asia/Seoul" date '+%Y-%m-%dT%H:%M:%S+09:00' 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")

  # 제안 JSON 파일들에서 직접 구조화 데이터 수집
  python3 - "$PROPOSALS_DIR" "$now" "$REPORT_TITLE" <<'PYEOF'
import json, sys, os, glob, datetime

prop_dir, now, title = sys.argv[1], sys.argv[2], sys.argv[3]

proposals_by_status = {"pending": [], "applied": [], "rejected": []}
all_proposals = []

for pf in sorted(glob.glob(os.path.join(prop_dir, "*.json"))):
    try:
        d = json.load(open(pf, encoding="utf-8"))
        status = d.get("status", "pending")
        all_proposals.append(d)
        proposals_by_status.get(status, proposals_by_status["pending"]).append(d)
    except Exception as e:
        pass  # 파싱 실패 시 건너뜀

summary = {
    "total": len(all_proposals),
    "pending": len(proposals_by_status["pending"]),
    "applied": len(proposals_by_status["applied"]),
    "rejected": len(proposals_by_status["rejected"]),
    "by_severity": {
        "critical": sum(1 for p in all_proposals if p.get("severity") == "critical"),
        "high":     sum(1 for p in all_proposals if p.get("severity") == "high"),
        "medium":   sum(1 for p in all_proposals if p.get("severity") == "medium"),
        "low":      sum(1 for p in all_proposals if p.get("severity") == "low"),
    }
}

output = {
    "meta": {
        "title": title,
        "generated_at": now,
        "version": "4.1",
        "source": "self-evolving-agent"
    },
    "summary": summary,
    "proposals": all_proposals,
}

print(json.dumps(output, ensure_ascii=False, indent=2))
PYEOF
}

# ── Markdown → PDF 변환 ──────────────────────────────────
convert_to_pdf() {
  local md_content="$1" output="$2"

  if ! command -v pandoc &>/dev/null; then
    die "PDF 생성에 pandoc이 필요합니다. 설치: brew install pandoc"
  fi

  local tmp_md; tmp_md=$(mktemp /tmp/sea-export.XXXXXX.md)
  echo "$md_content" > "$tmp_md"

  # wkhtmltopdf 우선 (더 나은 CSS 지원), 없으면 기본 PDF 엔진
  if command -v wkhtmltopdf &>/dev/null 2>/dev/null; then
    local tmp_html; tmp_html=$(mktemp /tmp/sea-export.XXXXXX.html)
    convert_to_html "$md_content" > "$tmp_html"
    wkhtmltopdf --quiet \
      --page-size A4 \
      --margin-top 20mm --margin-bottom 20mm \
      --margin-left 15mm --margin-right 15mm \
      "$tmp_html" "$output" 2>/dev/null \
      && ok "PDF 생성 완료 (wkhtmltopdf): $output" \
      || { info "wkhtmltopdf 실패 — pandoc으로 재시도"; rm -f "$tmp_html"; }
    rm -f "$tmp_html"
  else
    pandoc "$tmp_md" \
      --from markdown --to pdf \
      --output "$output" \
      --pdf-engine=xelatex \
      -V geometry:margin=1in \
      -V mainfont="AppleGothic" \
      2>/dev/null \
      && ok "PDF 생성 완료 (pandoc): $output" \
      || {
        # CJK 폰트 없으면 기본 엔진
        pandoc "$tmp_md" \
          --from markdown --to pdf \
          --output "$output" \
          2>/dev/null \
          && ok "PDF 생성 완료 (pandoc 기본): $output" \
          || die "PDF 생성 실패. pandoc + pdflatex 또는 wkhtmltopdf 필요"
      }
  fi
  rm -f "$tmp_md"
}

# ── 출력 함수 ────────────────────────────────────────────
write_output() {
  local content="$1" dest="$2"
  if [ -z "$dest" ]; then
    echo "$content"
  else
    mkdir -p "$(dirname "$dest")" 2>/dev/null || true
    echo "$content" > "$dest"
    ok "저장됨: $dest"
  fi
}

# ── 메인 ─────────────────────────────────────────────────
MD_CONTENT=$(get_markdown_content)

case "$FORMAT" in
  markdown|md)
    write_output "$MD_CONTENT" "$OUTPUT_FILE"
    ;;

  html)
    [ -z "$OUTPUT_FILE" ] && OUTPUT_FILE=""
    HTML=$(convert_to_html "$MD_CONTENT" "$REPORT_TITLE")
    write_output "$HTML" "$OUTPUT_FILE"
    ;;

  json)
    JSON=$(convert_to_json)
    write_output "$JSON" "$OUTPUT_FILE"
    ;;

  pdf)
    [ -z "$OUTPUT_FILE" ] && {
      OUTPUT_FILE="$(pwd)/sea-report-$(date +%Y%m%d).pdf"
      info "출력 파일 미지정 — 기본: $OUTPUT_FILE"
    }
    convert_to_pdf "$MD_CONTENT" "$OUTPUT_FILE"
    ;;

  all)
    [ -z "$OUTPUT_DIR" ] && OUTPUT_DIR="$(pwd)/sea-reports-$(date +%Y%m%d)"
    mkdir -p "$OUTPUT_DIR" 2>/dev/null || die "디렉토리 생성 실패: $OUTPUT_DIR"
    info "출력 디렉토리: $OUTPUT_DIR"

    # Markdown
    echo "$MD_CONTENT" > "${OUTPUT_DIR}/report.md"
    ok "Markdown: ${OUTPUT_DIR}/report.md"

    # HTML
    convert_to_html "$MD_CONTENT" "$REPORT_TITLE" > "${OUTPUT_DIR}/report.html" 2>/dev/null \
      && ok "HTML: ${OUTPUT_DIR}/report.html" \
      || info "HTML 생성 건너뜀"

    # JSON
    convert_to_json > "${OUTPUT_DIR}/report.json" 2>/dev/null \
      && ok "JSON: ${OUTPUT_DIR}/report.json" \
      || info "JSON 생성 건너뜀"

    # PDF (pandoc 있을 때만)
    if command -v pandoc &>/dev/null; then
      convert_to_pdf "$MD_CONTENT" "${OUTPUT_DIR}/report.pdf" \
        && ok "PDF: ${OUTPUT_DIR}/report.pdf" \
        || info "PDF 생성 건너뜀 (pandoc 오류)"
    else
      info "PDF 건너뜀 (pandoc 미설치)"
    fi

    ok "완료: $OUTPUT_DIR"
    ls -la "$OUTPUT_DIR" 2>/dev/null | grep -v "^total" | awk '{print "  " $0}' || true
    ;;

  *)
    die "알 수 없는 형식: $FORMAT (markdown | html | json | pdf | all)"
    ;;
esac
