---
name: code-executor
description: Ejecuta código Python, JavaScript, Bash dinámicamente. El bot puede crear y ejecutar código al vuelo.
metadata: {"openclaw":{"emoji":"⚡","auto":false,"tier":"god"}}
---

# Code Executor (Ejecutor de Código) 🔥

**PODER INFINITO.** El bot puede escribir y ejecutar código para resolver cualquier problema.

## ¿Qué Hace?

Si el bot necesita hacer algo que no tiene una skill:
1. **Escribe el código** necesario
2. **Lo ejecuta** en un sandbox
3. **Retorna** el resultado

## Comandos

```
# Ejecutar código directamente
run python "print('Hello World')"
run js "console.log(2+2)"
run bash "ls -la"

# Ejecutar archivo
run ~/script.py
execute ~/automation.js

# El bot decide qué código escribir
solve "calcula el factorial de 100"
compute "genera 10 números primos"
```

## Ejemplo Real

```
Usuario: calcula cuántos días faltan para mi cumpleaños (15 de marzo)

Bot: ⚡ Necesito calcular esto...

     📝 Código generado:
     ```python
     from datetime import date
     
     today = date.today()
     birthday = date(today.year, 3, 15)
     
     if birthday < today:
         birthday = date(today.year + 1, 3, 15)
     
     days = (birthday - today).days
     print(f"Faltan {days} días para tu cumpleaños")
     ```
     
     ⚡ Ejecutando...
     
     ✅ Resultado:
     Faltan 40 días para tu cumpleaños (15 de marzo, 2026)
```

## Resolución de Problemas

```
Usuario: necesito renombrar 500 archivos agregando la fecha

Bot: ⚡ Generando script...

     ```python
     import os
     from datetime import datetime
     
     folder = "/ruta/a/archivos"
     date_str = datetime.now().strftime("%Y%m%d")
     
     for filename in os.listdir(folder):
         name, ext = os.path.splitext(filename)
         new_name = f"{date_str}_{name}{ext}"
         os.rename(
             os.path.join(folder, filename),
             os.path.join(folder, new_name)
         )
         print(f"Renamed: {filename} -> {new_name}")
     ```
     
     ⚠️ Este script renombrará 500 archivos.
     ¿Ejecutar? [Sí] [Ver preview] [Cancelar]
```

## Lenguajes Soportados

| Lenguaje | Runtime |
|----------|---------|
| Python | python3 |
| JavaScript | node |
| TypeScript | ts-node |
| Bash | bash/sh |
| SQL | sqlite3 |

## Modo Interactivo

```
Usuario: abre un REPL de Python

Bot: ⚡ Python REPL iniciado:

     >>> 
     
Usuario: import math; math.pi

Bot: >>> import math; math.pi
     3.141592653589793
     
Usuario: exit

Bot: ⚡ REPL cerrado
```

## Instalación de Dependencias

```
Usuario: necesito usar pandas para analizar este CSV

Bot: ⚡ pandas no está instalado
     
     ¿Instalar pandas? [Sí] [No]

Usuario: sí

Bot: ⚡ pip install pandas
     ✅ pandas instalado
     
     Continuando con el análisis...
```

## Seguridad

```bash
CODE_SANDBOX=true           # Ejecutar en sandbox
CODE_TIMEOUT=30             # Timeout en segundos
CODE_ALLOW_NETWORK=false    # Bloquear red por defecto
CODE_ALLOW_FILESYSTEM=read  # Solo lectura por defecto
CODE_REQUIRE_CONFIRM=true   # Confirmar antes de ejecutar
```

## Casos de Uso

1. **Cálculos complejos** que no tiene ninguna skill
2. **Transformación de datos** personalizada
3. **Automatizaciones únicas** que no ameritan una skill
4. **Prototipado rápido** de soluciones
5. **Debugging** y testing
