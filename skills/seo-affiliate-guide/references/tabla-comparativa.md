# Plantillas de Tablas Comparativas para Guías de Afiliado

---

## Tabla 1 — Comparativa Rápida (para el inicio del artículo)

Esta tabla va justo después de la introducción. Debe ser escaneable en segundos.

```markdown
| Producto | Precio aprox. | Lo mejor | Puntuación | Enlace |
|---|---|---|---|---|
| [Nombre Producto 1] | ~XXX€ | Mejor completo | ⭐ 9.5/10 | [Ver precio →](url) |
| [Nombre Producto 2] | ~XXX€ | Mejor calidad-precio | ⭐ 9.2/10 | [Ver precio →](url) |
| [Nombre Producto 3] | ~XXX€ | Mejor económico | ⭐ 8.8/10 | [Ver precio →](url) |
| [Nombre Producto 4] | ~XXX€ | Mejor para [uso específico] | ⭐ 8.5/10 | [Ver precio →](url) |
| [Nombre Producto 5] | ~XXX€ | Mejor compacto / ligero | ⭐ 8.3/10 | [Ver precio →](url) |
```

**Etiquetas comunes para la columna "Lo mejor":**
- Mejor completo / Mejor del mercado
- Mejor calidad-precio
- Más económico que vale la pena
- Mejor para profesionales
- Mejor para principiantes
- Más ligero / más compacto
- Mejor para [necesidad específica: alérgicos, mascotas, pisos grandes…]
- Mejor opción premium

---

## Tabla 2 — Comparativa Técnica Detallada (mitad o final del artículo)

Para guías de productos técnicos donde las especificaciones importan.

### Ejemplo: Aspiradoras Sin Cable

```markdown
| Modelo | Potencia | Autonomía | Peso | Filtro | Nivel ruido | Precio | Valoración |
|---|---|---|---|---|---|---|---|
| Dyson V15 Detect | 240 AW | 60 min | 3,09 kg | HEPA H13 | 79 dB | ~750€ | 9.5/10 |
| Rowenta X-Force 14.60 | 185 W | 65 min | 2,7 kg | Multi-ciclón | 82 dB | ~390€ | 9.2/10 |
| Bosch Unlimited 7 | 150 W | 60 min | 2,8 kg | HEPA | 80 dB | ~300€ | 8.9/10 |
| Cecotec Conga 900 | 18.000 Pa | 40 min | 1,5 kg | Estándar | 85 dB | ~90€ | 8.3/10 |
```

### Ejemplo: Robots de Cocina

```markdown
| Modelo | Potencia | Capacidad | Funciones | Conectividad | Garantía | Precio | Valoración |
|---|---|---|---|---|---|---|---|
| Thermomix TM6 | 1.300 W | 2,2 L | +20 | WiFi + App | 2 años | ~1.400€ | 9.8/10 |
| Monsieur Cuisine Smart | 1.200 W | 3 L | 12 | WiFi | 2 años | ~400€ | 9.3/10 |
| Olla GM G | 900 W | 6 L | 8 | No | 2 años | ~120€ | 8.5/10 |
```

---

## Tabla 3 — Matriz de Decisión por Perfil de Comprador

Ideal para guías donde hay perfiles muy distintos de compradores.

```markdown
| Si eres… | Te recomendamos | Por qué |
|---|---|---|
| Tienes mascotas | [Producto X] | Filtro HEPA y cepillo anti-pelo |
| Piso pequeño (<50m²) | [Producto Y] | Ligero y económico, suficiente |
| Alérgico/a | [Producto Z] | Única opción con filtración HEPA H13 |
| Presupuesto ajustado | [Producto W] | Mejor rendimiento por menos de 150€ |
| Quieres lo mejor sin mirar precio | [Producto V] | El más completo del mercado |
```

---

## Tabla 4 — Pros y Contras por Producto (formato alternativo)

Útil cuando quieres que el lector compare de un vistazo.

```markdown
| | [Producto A] | [Producto B] | [Producto C] |
|---|---|---|---|
| **Precio** | ~~€~~ | ~~€€~~ | ~~€€€~~ |
| **Potencia** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Facilidad de uso** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Durabilidad** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Relación calidad-precio** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
```

---

## Notas importantes sobre las tablas

### SEO
- Las tablas bien estructuradas tienen más probabilidades de aparecer como **featured snippet**
- Usa encabezados de columna descriptivos (no solo "Precio" → "Precio en Amazon")
- Incluye siempre una columna de link/CTA en la tabla rápida del inicio

### UX / Conversión
- Las tablas deben ser responsivas (no demasiado anchas para móvil)
- Si la tabla tiene más de 6 columnas, considera dividirla en dos tablas más pequeñas
- Colores o iconos (✅ ❌ ⭐) mejoran la escaneabilidad

### Actualización
- Los precios cambian constantemente: indica siempre "(precio aproximado, actualizado [mes/año])"
- Considera usar rangos en vez de precios exactos: "~300–400€" en lugar de "389€"

---

## Fragmento de código Schema para tabla comparativa (para el desarrollador)

Si quieres implementar schema markup en las tablas de comparación, usa este formato JSON-LD:

```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Las 8 Mejores Aspiradoras Sin Cable 2025",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Dyson V15 Detect",
      "url": "https://tu-blog.com/guia-aspiradoras/#dyson-v15"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Rowenta X-Force Flex 14.60",
      "url": "https://tu-blog.com/guia-aspiradoras/#rowenta-x-force"
    }
  ]
}
```
