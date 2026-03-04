---
name: sigaa
description: "Interact with SIGAA (Sistema Integrado de Gestão de Atividades Acadêmicas), the academic management system used by 50+ Brazilian federal universities (UNB, UFRN, UFC, UFPE, UFCG, UFPI, etc.). Use when: (1) checking enrollment status or classes for students, (2) verifying grades or academic history, (3) accessing professor portal (classes, attendance, grade launch), (4) logging in to any SIGAA instance via CAS SSO or direct authentication, (5) automating any SIGAA task via web scraping. Handles both undergrad and graduate (stricto/lato sensu) portals. **REQUIRED ENVIRONMENT VARIABLES:** SIGAA_URL (institution base URL), SIGAA_USER (login/matricula), SIGAA_PASSWORD (password)."
metadata:
  openclaw:
    requires:
      bins:
        - curl
        - python3
        - grep
      env:
        - SIGAA_URL
        - SIGAA_USER
        - SIGAA_PASSWORD
    credentials:
      - name: sigaa-account
        description: "SIGAA institutional account (matricula/CPF + password)"
        env: SIGAA_USER,SIGAA_PASSWORD
    homepage: "https://github.com/olegantonov/sigaa-openclaw-skill"
---

# SIGAA Skill

SIGAA is a JSF-based web system with no public REST API. All automation uses authenticated web scraping (curl + Python).

## Prerequisites

**Required Environment Variables:**

```bash
export SIGAA_URL='https://sigaa.unb.br'   # Institution base URL (no trailing slash)
export SIGAA_USER='241104251'             # Login: matricula number or CPF (institution-specific)
export SIGAA_PASSWORD='yourpassword'      # Your SIGAA password
```

- For username format per institution → see `references/institutions.md`
- **Never pass credentials as command-line arguments** — use env vars only

## Quick Start

### 1. Login

```bash
source scripts/sigaa_login.sh
# Sets $SIGAA_COOKIE_FILE and $SIGAA_USER_ID
# Cookie file is chmod 600 and auto-removed on shell exit
```

### 2. Student Operations

```bash
bash scripts/sigaa_student.sh status             # Basic info + active program
bash scripts/sigaa_student.sh enrollments        # Current semester classes
bash scripts/sigaa_student.sh enrollment-result  # Status of enrollment requests (SUBMETIDA / DEFERIDA / NEGADA)
bash scripts/sigaa_student.sh grades             # Grades
bash scripts/sigaa_student.sh history            # Full academic history
bash scripts/sigaa_student.sh schedule           # Class schedule
```

### 3. Professor Operations

```bash
bash scripts/sigaa_professor.sh classes              # Current semester classes
bash scripts/sigaa_professor.sh students <turma_id>  # Students in a class
bash scripts/sigaa_professor.sh attendance           # Pending attendance
bash scripts/sigaa_professor.sh schedule             # Teaching schedule
```

## JSF Navigation Pattern

SIGAA uses JavaServer Faces (JSF) with `jsCookMenu`. All menu actions require a POST with a fresh `ViewState` and `jscook_action`:

```bash
VS=$(curl -s -b "$SIGAA_COOKIE_FILE" -c "$SIGAA_COOKIE_FILE" \
  "${SIGAA_URL}/sigaa/portais/discente/discente.jsf" | \
  grep -oP 'name="javax\.faces\.ViewState"[^>]*value="\K[^"]+' | head -1)

curl -s -L -b "$SIGAA_COOKIE_FILE" -c "$SIGAA_COOKIE_FILE" \
  -X POST "${SIGAA_URL}/sigaa/portais/discente/discente.jsf" \
  -d "menu%3Aform_menu_discente=menu%3Aform_menu_discente" \
  -d "id=${SIGAA_USER_ID}" \
  --data-urlencode "jscook_action=menu_form_menu_discente_discente_menu:A]#{BEAN.method}" \
  --data-urlencode "javax.faces.ViewState=${VS}"
```

Full action reference → `references/student-guide.md` and `references/professor-guide.md`

## Parsing Responses

```python
import re, html as h

def clean_html(content):
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', content)
    return h.unescape(re.sub(r'[ \t]+', ' ', text))

def extract_table_rows(html_content):
    content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.DOTALL)
    result = []
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
        clean = [h.unescape(re.sub(r'<[^>]+>|\s+', ' ', c)).strip() for c in cells if c.strip()]
        if clean:
            result.append(clean)
    return result
```

## Security Notes

- **Credentials via env vars only** — never pass as CLI arguments (prevents shell history leakage)
- **Cookie files**: auto-created with `chmod 600`, auto-deleted on shell exit via `trap`
- **Rate limiting**: 0.5s delay between requests (built into scripts)
- **Session scope**: SIGAA sessions expire after ~20 min inactivity — re-source login if you get redirected to login page
- **Network targets**: scripts only contact `$SIGAA_URL` and the CAS SSO host derived from the login redirect — confirm these match your institution before running

## Common Issues

| Symptom | Fix |
|---------|-----|
| "Credenciais inválidas" | Check username format for institution (see `references/institutions.md`) |
| "Nenhuma turma neste semestre" | Run `enrollment-result` — status may be SUBMETIDA (pending) |
| JSF POST returns portal page | ViewState stale — re-fetch portal before POST |
| Session redirect to login | Cookie expired — re-source `sigaa_login.sh` |
| "Você não pode tentar re-enviar" | Reused LT token — always fetch a fresh login page |

## References

- `references/institutions.md` — Supported institutions, login URLs, username formats
- `references/student-guide.md` — Full student portal guide, all JSF actions, parsing tips
- `references/professor-guide.md` — Professor portal, grade/attendance workflows
