---
name: jwdiario
description: Buscar y obtener el texto diario de la página oficial de los Testigos de Jehová para la Librería Watchtower en español (wol.jw.org/es/). Utiliza web_fetch para acceder al contenido y extraer el texto del día actual. Use cuando se solicite el texto diario de JW o contenido bíblico diario de fuentes JW.
---

# Habilidad JWDiario

Esta habilidad permite obtener el texto diario de la página oficial de los Testigos de Jehová en español ([wol.jw.org/es/](https://wol.jw.org/es/wol/h/r4/lp-s)).

## Funcionalidad principal

La habilidad realiza lo siguiente:
1. Accede a la página de la Biblioteca en Línea de los Testigos de Jehová
2. Extrae el texto diario correspondiente a la fecha actual
3. Presenta el texto con contexto bíblico y explicación pertinente

## Uso típico

Cuando se solicita:
- "Texto diario de JW"
- "Texto de hoy de JW"
- "Buscar texto del día en JW"
- "Mostrar lectura diaria de JW"

## Flujo de trabajo

1. Usa `web_fetch` para acceder a https://wol.jw.org/es/wol/h/r4/lp-s/AÑO/MES/DIA (por ejemplo: https://wol.jw.org/es/wol/h/r4/lp-s/2026/2/8 para el 8 de febrero de 2026)
2. Extrae el contenido del día actual
3. Incluye el encabezado del día con la cita bíblica correspondiente y la explicación sin cambiar su texto de ninguna forma.
4. Incluye el enlace `https://wol.jw.org/es/` al final del mensaje

## Nota importante

- **Siempre usar la versión en español** de la página (wol.jw.org/es/).
- **No traducir el texto**. El contenido debe extraerse directamente de la fuente en español, tal como aparece en la página oficial.

## Ejemplo de uso

```
Usuario: "Texto diario de JW por favor"
Habilidad: Obtiene el texto del día desde `https://wol.jw.org/es/wol/h/r4/lp-s` y lo presenta con el versículo bíblico y explicación correspondiente. No cambia el texto original. Añade el enlace al final.
```

## Recursos necesarios

- `web_fetch` para acceder al sitio web
- Capacidad de procesamiento de texto para formatear correctamente la salida