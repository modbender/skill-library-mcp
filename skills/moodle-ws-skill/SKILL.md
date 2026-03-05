---
name: moodle-ws
description: >
  Integrar con Moodle 4.x usando Web Services REST. Usar esta skill cuando el usuario pida crear cursos,
  inscribir o desinscribir usuarios, crear o actualizar actividades (quiz, assignment, forum),
  enviar calificaciones o listar cursos/estudiantes en un campus Moodle con Web Services habilitados.
---

# Moodle Web Services (REST) – Skill

## 1. Contexto y requisitos

Esta skill sirve para trabajar con **Moodle 4.x** mediante **Web Services (REST)**.

Funcionalidades principales:

- Crear curso
- Inscribir / desinscribir usuarios
- Crear / actualizar actividades:
  - Quiz (cuestionarios)
  - Assignment (tareas / entregas)
  - Forum (foros)
- Enviar calificaciones
- Obtener listas de cursos y estudiantes

Requisitos:

- URL base de Moodle (por ejemplo: `https://moodle.ejemplo.com`)
- Token de Web Service con los permisos adecuados (role con capabilities para:
  - crear cursos,
  - gestionar matriculaciones,
  - gestionar actividades,
  - gestionar notas).

**Importante:** nunca guardar el token en el chat. Pedirle al usuario que lo configure en un archivo local o variable de entorno.

Sugerencia: guardar en un archivo de config no versionado, por ejemplo:

```bash
~/.openclaw/workspace/secrets/moodle-ws.json

## 7. Autoría y uso

Skill **moodle-ws** diseñada por **Exe Andino**.

Pensada para:
- integrar Moodle 4.x con asistentes OpenClaw,
- automatizar tareas docentes y administrativas (creación de cursos, matriculaciones, actividades, notas),
- siempre usando tokens de Web Services con permisos limitados y entornos controlados.

Se recomienda:
- usar tokens específicos para este tipo de integración,
- no versionar ni exponer la configuración de URL + token,
- probar primero en entornos de prueba antes de producción.
