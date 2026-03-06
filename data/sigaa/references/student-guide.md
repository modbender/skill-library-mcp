# SIGAA Student Portal - Complete Guide

## JSF Navigation

SIGAA uses JavaServer Faces (JSF) with the `jsCookMenu` JS library. All menu actions require a POST with:

```
POST /sigaa/portais/discente/discente.jsf
Fields:
  menu:form_menu_discente = menu:form_menu_discente
  id = <user_numeric_id>          # extracted from hidden input on portal page
  jscook_action = <action_string> # menu item action
  javax.faces.ViewState = <vs>    # extracted from hidden input
```

### Key JSF Menu Actions (Discente)

| Action | jscook_action value |
|--------|-------------------|
| Enrollment result | `menu_form_menu_discente_discente_menu:A]#{matriculaGraduacao.verComprovanteSolicitacoes}` |
| Start enrollment (stricto sensu) | `menu_form_menu_discente_discente_menu:A]#{matriculaStrictoBean.iniciar}` |
| Grades report | `menu_form_menu_discente_discente_menu:A]#{relatorioNotasAluno.gerarRelatorio}` |
| Academic history | `menu_form_menu_discente_discente_menu:A]#{portalDiscente.historicoComDadosAdicionais}` |
| Enrollment certificate | `menu_form_menu_discente_discente_menu:A]#{portalDiscente.atestadoMatriculaUnb}` |
| Remove enrollment | `menu_form_menu_discente_discente_menu:A]#{retiradaMatricula.popularSolicitacao}` |
| Lock enrollment | `menu_form_menu_discente_discente_menu:A]#{trancamentoMatricula.popularSolicitacao}` |

### Enrollment Status Values

| Status | Meaning |
|--------|---------|
| SUBMETIDA | Submitted, awaiting processing by coordinator |
| DEFERIDA | Approved by coordinator |
| NEGADA / INDEFERIDA | Rejected |
| CONFIRMADA / APROVADA | Fully confirmed, student is enrolled |
| AGUARDANDO | Waiting (e.g., waiting for prerequisite check) |

### Key Page URLs (direct GET, no menu required)

| Page | URL |
|------|-----|
| Portal discente | `/sigaa/portais/discente/discente.jsf` |
| All virtual classes | `/sigaa/portais/discente/turmas.jsf` |
| Profile | `/sigaa/portais/discente/perfil.jsf` |

## Parsing Tips

### Extract user ID (needed for menu posts)
```bash
grep -oP 'name="id"\s+value="\K[0-9]+' page.html | head -1
```

### Extract ViewState
```bash
grep -oP 'name="javax\.faces\.ViewState"[^>]*value="\K[^"]+' page.html | head -1
```

### Extract table data (Python)
```python
import re, html as h

def extract_tables(html_content):
    # Remove scripts/styles
    content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.DOTALL)
    result = []
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
        clean = [h.unescape(re.sub(r'<[^>]+>|\s+', ' ', c)).strip() for c in cells]
        clean = [c for c in clean if c]
        if clean:
            result.append(clean)
    return result
```

## Graduate (Stricto Sensu) Specifics

For pós-graduação (mestrado/doutorado), the portal is the same (`/portais/discente/discente.jsf`) but some actions differ:

- Enrollment is via `matriculaStrictoBean` not `matriculaGraduacao`
- Room locations are often listed separately on the program's website (not in SIGAA)
- The "Turmas do Semestre" block in the portal home shows enrolled classes; if empty with SUBMETIDA status, the enrollment is pending coordinator approval

## Common Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| "Credenciais inválidas" | Wrong username format | Try matricula number instead of CPF (or vice versa) |
| "Nenhuma turma neste semestre" | Enrollment pending | Check enrollment-result for SUBMETIDA status |
| Session expired / redirect to login | Cookie expired | Re-login with sigaa_login.sh |
| JSF POST returns portal page (no navigation) | Wrong jscook_action or stale ViewState | Re-fetch portal page to get fresh ViewState |
