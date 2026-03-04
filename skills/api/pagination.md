# Pagination Traps

## Offset-Based

- Item insertado durante paginación = item duplicado en siguiente página
- Item borrado durante paginación = item skipped, nunca lo ves
- `offset=1000000` + SQL = full table scan, extremadamente lento
- `total_count` cambia entre requests = progress bar miente

## Cursor-Based

- Cursor opaco + cambio de sort order = cursor inválido
- Cursor basado en ID + ID borrado = error o resultados inesperados
- Cursor sin expiración = válido para siempre, inconsistencias si schema cambia
- Primer request sin cursor puede ser diferente a cursor-based — comportamiento inconsistente

## Page-Based

- `page=0` vs `page=1` — APIs inconsistentes, off-by-one errores
- Última página parcial + mismo `per_page` = no sabes si hay más
- Cambio de `per_page` entre requests = items duplicados o skipped
- `total_pages` calculado con división entera = página extra si hay remainder

## Link Headers

- `Link` header sin parsear = regex naive falla con URLs complejas
- `rel="next"` ausente puede significar última página O API no soporta
- URL en Link es absoluta pero puede tener host incorrecto detrás de proxy
- Headers en response HEAD diferentes a GET en algunos APIs

## Parallel Pagination

- Paralelizar páginas sin conocer total = algunas requests a páginas inexistentes
- Rate limit hit = algunas páginas fallan, resultado incompleto
- Orden de procesamiento != orden de páginas = resultados desordenados
- Error en una página = ¿abortar todo o continuar con gaps?

## Infinite Scroll

- Nuevo item insertado mientras usuario scrollea = item aparece dos veces
- Cache de páginas + item actualizado = versión vieja mostrada
- Usuario scrollea rápido = muchos requests pendientes, respuestas out of order
