# Template: Resumen de Review

Usa este template para generar el resumen general al finalizar un code review.
Se coloca como comentario principal del PR o al inicio del review.

---

## Formato del Resumen

# Code Review Summary

**PR:** [Título del PR]
**Autor:** [Nombre]
**Reviewer:** AI Code Reviewer
**Fecha:** [Fecha]
**Archivos revisados:** [N]
**Líneas cambiadas:** +[añadidas] / -[eliminadas]

---

## Veredicto

[🔴 CAMBIOS REQUERIDOS / 🟡 APROBADO CON OBSERVACIONES / 🟢 APROBADO]

[Resumen en 2-3 oraciones del estado general del PR]

---

## Estadísticas

| Severidad   | Cantidad | Estado     |
|-------------|----------|------------|
| 🔴 Blocker  | X        | Debe fijarse antes de merge |
| 🟡 Warning  | X        | Debería fijarse             |
| 🔵 Suggest  | X        | Considerar para mejorar     |
| 💡 Nit      | X        | Opcional                    |
| **Total**   | **X**    |            |

---

## Hallazgos Críticos (Blockers)

Si hay blockers, listarlos aquí con resumen breve:

1. 🔴 **[Categoría]: [Título]** - `archivo.ext:línea`
   Breve descripción del problema y su impacto.

2. 🔴 **[Categoría]: [Título]** - `archivo.ext:línea`
   Breve descripción del problema y su impacto.

Si no hay blockers:
  ✅ No se encontraron hallazgos críticos.

---

## Resumen de Warnings

Si hay warnings, listarlos:

1. 🟡 **[Categoría]: [Título]** - `archivo.ext:línea`
2. 🟡 **[Categoría]: [Título]** - `archivo.ext:línea`

Si no hay warnings:
  ✅ No se encontraron warnings.

---

## Suggestions y Nits

Resumen agrupado (no detalle completo, eso va en los comentarios inline):

**Suggestions:**
- [Breve descripción] (`archivo.ext`)
- [Breve descripción] (`archivo.ext`)

**Nits:**
- [Breve descripción] (`archivo.ext`)
- [Breve descripción] (`archivo.ext`)

---

## Lo Positivo 👏

Destacar lo que está bien hecho en el PR:

- [Aspecto positivo 1]
- [Aspecto positivo 2]
- [Aspecto positivo 3]

Ejemplos de cosas positivas a destacar:
- Buen manejo de errores
- Tests completos y bien estructurados
- Naming claro y consistente
- Buena separación de responsabilidades
- Documentación actualizada
- Commit messages claros
- Buen uso de tipos (TypeScript)
- Performance considerada
- Accesibilidad incluida

---

## Archivos Revisados

| Archivo | Cambios | Hallazgos |
|---------|---------|-----------|
| `ruta/archivo1.ext` | +X / -Y | 🔴 1, 🟡 2 |
| `ruta/archivo2.ext` | +X / -Y | 🔵 1 |
| `ruta/archivo3.ext` | +X / -Y | ✅ Sin hallazgos |

---

## Ejemplo Completo

A continuación un ejemplo de cómo se ve un resumen terminado:

# Code Review Summary

**PR:** feat(orders): add bulk discount calculation
**Autor:** María García
**Reviewer:** AI Code Reviewer
**Fecha:** 2026-02-12
**Archivos revisados:** 8
**Líneas cambiadas:** +347 / -42

---

## Veredicto

🔴 CAMBIOS REQUERIDOS

El PR implementa correctamente la lógica de descuentos por volumen, pero se
encontró una vulnerabilidad de SQL injection en el nuevo endpoint de búsqueda
y hay errores silenciados en el servicio de notificaciones que deben resolverse
antes del merge.

---

## Estadísticas

| Severidad   | Cantidad | Estado     |
|-------------|----------|------------|
| 🔴 Blocker  | 2        | Debe fijarse antes de merge |
| 🟡 Warning  | 3        | Debería fijarse             |
| 🔵 Suggest  | 4        | Considerar para mejorar     |
| 💡 Nit      | 2        | Opcional                    |
| **Total**   | **11**   |            |

---

## Hallazgos Críticos (Blockers)

1. 🔴 **Seguridad: SQL Injection** - `src/repositories/order.repository.ts:45`
   El parámetro de búsqueda se concatena directamente en la query SQL.
   Un atacante puede ejecutar queries arbitrarios contra la base de datos.

2. 🔴 **Credenciales: API key hardcodeada** - `src/services/payment.service.ts:12`
   La API key de Stripe en modo live está en el código fuente.
   Debe moverse a variables de entorno y rotar la key comprometida.

---

## Resumen de Warnings

1. 🟡 **Complejidad: Función con 6 niveles de nesting** - `src/services/order.service.ts:78`
2. 🟡 **Error Handling: Errores silenciados** - `src/services/notification.service.ts:23`
3. 🟡 **Naming: Variables genéricas** - `src/services/pricing.service.ts:15`

---

## Suggestions y Nits

**Suggestions:**
- Extraer magic numbers a constantes (`pricing.service.ts`)
- Agregar tests para edge cases de descuentos (`order.service.test.ts`)
- Considerar usar Strategy pattern para tipos de descuento (`discount/`)
- Agregar índice de DB para la nueva query de búsqueda (`migrations/`)

**Nits:**
- Import no utilizado: `Formatter` (`user.controller.ts:3`)
- Variable `data` debería ser `monthlySalesReport` (`report.service.ts:45`)

---

## Lo Positivo 👏

- Excelente estructura de la lógica de descuentos, bien modularizada
- Tests cubren los escenarios principales correctamente
- Tipos de TypeScript bien definidos para las nuevas entidades
- Commit messages claros y siguiendo Conventional Commits
- Documentación del endpoint actualizada en el README

---

## Archivos Revisados

| Archivo | Cambios | Hallazgos |
|---------|---------|-----------|
| `src/repositories/order.repository.ts` | +45 / -3 | 🔴 1 |
| `src/services/payment.service.ts` | +12 / -8 | 🔴 1 |
| `src/services/order.service.ts` | +89 / -12 | 🟡 1, 🔵 1 |
| `src/services/notification.service.ts` | +34 / -5 | 🟡 1 |
| `src/services/pricing.service.ts` | +67 / -0 | 🟡 1, 🔵 1 |
| `src/services/order.service.test.ts` | +78 / -0 | 🔵 1 |
| `src/controllers/user.controller.ts` | +12 / -8 | 💡 1 |
| `src/services/report.service.ts` | +10 / -6 | 💡 1, 🔵 1 |

---

## Criterios de Veredicto

Usar estos criterios para determinar el veredicto:

🔴 CAMBIOS REQUERIDOS:
  - Hay al menos 1 blocker
  - Hay vulnerabilidades de seguridad
  - Hay bugs que afectan funcionalidad core
  - Hay credenciales expuestas
  - El código puede causar pérdida de datos

🟡 APROBADO CON OBSERVACIONES:
  - No hay blockers
  - Hay warnings que deberían atenderse
  - El código funciona pero tiene áreas de mejora importantes
  - Se recomienda atender los warnings antes del merge o en PR de seguimiento

🟢 APROBADO:
  - No hay blockers ni warnings significativos
  - Solo suggestions y nits opcionales
  - El código es sólido, legible y bien testeado
  - Se puede mergear con confianza