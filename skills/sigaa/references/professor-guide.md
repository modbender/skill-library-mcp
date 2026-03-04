# SIGAA Professor Portal - Complete Guide

## Portal Access

Professor portal URL: `/sigaa/verPortalDocente.do`

The docente portal shows:
- Current semester classes (turmas)
- Pending attendance entries
- Research projects (bolsistas, orientandos)
- Extension activities

## JSF Menu Actions (Docente)

All menu POSTs go to `/sigaa/verPortalDocente.do`:

```
POST /sigaa/verPortalDocente.do
Fields:
  menu:form_menu_docente = menu:form_menu_docente
  id = <user_numeric_id>
  jscook_action = <action>
  javax.faces.ViewState = <vs>
```

| Action | jscook_action value |
|--------|-------------------|
| List my classes | `menu_form_menu_docente_docente_menu:A]#{turmaDocente.listar}` |
| Record attendance | `menu_form_menu_docente_docente_menu:A]#{frequenciaAluno.listarTurmasComFrequenciaPendente}` |
| Launch grades | `menu_form_menu_docente_docente_menu:A]#{lancamentoNota.listar}` |
| View schedule | `menu_form_menu_docente_docente_menu:A]#{horarioDocente.visualizarHorario}` |
| Attendance report | `menu_form_menu_docente_docente_menu:A]#{frequenciaAluno.emitirRelatorioFrequencia}` |
| Student list | `menu_form_menu_docente_docente_menu:A]#{turmaDocente.listarAlunos}` |

## Class (Turma) URLs

After listing classes, each turma has an ID that enables direct access:

```
/sigaa/graduacao/turma/discente/lista.jsf?id=<turma_id>
/sigaa/graduacao/frequencia/cadastro/form.jsf?id=<turma_id>
/sigaa/graduacao/nota/lancamento/form.jsf?id=<turma_id>
```

## Grade Entry

Grades are entered per `unidade avaliativa` (evaluation unit), scale 0–10.0.

Grade status in SIGAA:
- `EM ABERTO` — not yet entered
- `CONSOLIDADO` — finalized (cannot change without coordination)
- `HOMOLOGADO` — approved by coordinator

## Attendance (Frequência)

- Minimum attendance: typically 75% (varies by institution/course)
- Record as: present (P), absent (F), absent justified (FJ)
- Submit before deadline — after consolidation, requires coordinator override

## Turma Virtual

Professors can manage content in the virtual classroom:
- Post news/announcements
- Upload materials (PDF, video links)
- Create tasks (tarefas) with deadlines
- Run polls (enquetes)
- Forum management

## Important Deadlines (typical academic calendar)

- Enrollment period: usually weeks 1-2 of semester
- Attendance submission: weekly or at end of semester (varies)
- Grade submission (partial): after each evaluation unit
- Grade consolidation: before official grade deadline (dates vary by institution)
