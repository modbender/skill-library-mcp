# Automatización Jira Cloud — avanzado

## Buenas prácticas
- Definir **scope** (global vs proyecto) y propietario de la regla.
- Añadir **guardrails** (labels/issueType) para evitar loops.
- Usar `re-fetch issue data` en transiciones complejas.
- Monitorizar **audit log** y límites de ejecución.

## Patrones comunes
- SLA/tiempos: cambios de prioridad → reajustar fechas objetivo.
- Handoff: al pasar a “En QA” asignar reviewer automático.
- Notificaciones: solo cuando cambia estado crítico.

## Límites
- Revisar cuota de automatización por plan.
- Evitar reglas en cadena (posibles loops).
