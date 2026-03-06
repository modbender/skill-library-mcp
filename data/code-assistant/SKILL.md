---
name: code-assistant
description: Asistente de programación especializado. Analiza código, encuentra bugs, sugiere optimizaciones, refactoriza y genera documentación automáticamente.
metadata: {"openclaw":{"emoji":"💻","auto":false}}
---

# Code Assistant (Asistente de Programación Pro)

Una super-habilidad para desarrolladores. Va más allá de escribir código: analiza, depura, optimiza, refactoriza y documenta.

## Capacidades

```
┌─────────────────────────────────────────────────────┐
│                  CODE ASSISTANT                      │
├─────────────────────────────────────────────────────┤
│  🔍 Análisis    │  Encuentra bugs y code smells     │
│  ⚡ Optimización │  Mejora rendimiento y eficiencia  │
│  🔄 Refactor    │  Limpia y estructura código       │
│  📝 Documenta   │  Genera docstrings y README       │
│  🧪 Tests       │  Crea tests unitarios             │
│  🔐 Seguridad   │  Detecta vulnerabilidades         │
└─────────────────────────────────────────────────────┘
```

## Comandos

### Análisis de Código

```
# Analizar un archivo
code analyze src/utils.ts

# Analizar un directorio
code analyze src/ --depth:2

# Buscar bugs específicos
code bugs src/api/
code find-bugs src/

# Revisar complejidad
code complexity src/heavy-function.ts
```

### Optimización

```
# Sugerir optimizaciones
code optimize src/slow-algorithm.py

# Optimizar queries SQL
code optimize-sql queries/

# Reducir bundle size
code optimize-bundle src/
```

### Refactorización

```
# Refactorizar archivo
code refactor src/legacy-code.js

# Aplicar convenciones (PEP8, ESLint rules)
code format src/ --style:pep8

# Extraer función
code extract-function src/long-file.ts --lines:45-80
```

### Documentación

```
# Generar docstrings
code document src/api/

# Crear README
code readme src/my-project/

# Generar changelog
code changelog --since:v1.0.0
```

### Tests

```
# Generar tests unitarios
code test-gen src/calculator.ts

# Sugerir edge cases
code edge-cases src/validator.py
```

## Ejemplo de Uso

```
Usuario: code analyze src/users/auth.ts

Bot: 🔍 Análisis de: src/users/auth.ts

     📊 Métricas:
     ├── Líneas: 245
     ├── Funciones: 12
     ├── Complejidad ciclomática: 18 ⚠️ (alta)
     └── Cobertura de docs: 30% ⚠️

     🐛 Bugs Potenciales (2):
     
     1. Línea 67: Race condition
        ```typescript
        // ❌ Problema
        if (user) {
          await saveUser(user);  // user puede cambiar entre check y save
        }
        ```
        💡 Solución: Usar transacción o lock
     
     2. Línea 142: SQL Injection
        ```typescript
        // ❌ Problema
        query(`SELECT * FROM users WHERE id = ${userId}`)
        ```
        💡 Solución: Usar parámetros preparados

     ⚡ Optimizaciones Sugeridas (3):
     
     1. Línea 89: Usar Map en lugar de Object para lookups frecuentes
     2. Línea 156: Memoizar resultado de getPermissions()
     3. Línea 201: Lazy loading para módulo crypto

     🔄 Refactorizaciones Sugeridas:
     
     1. Extraer validateToken() a módulo separado
     2. Aplicar patrón Repository para queries
     
     ¿Ejecutar alguna acción? [Documentar] [Refactorizar] [Generar Tests]
```

## Lenguajes Soportados

| Lenguaje | Análisis | Docs | Tests |
|----------|----------|------|-------|
| TypeScript/JavaScript | ✅ | ✅ | ✅ |
| Python | ✅ | ✅ | ✅ |
| Go | ✅ | ✅ | ✅ |
| Rust | ✅ | ✅ | ⚠️ |
| Java | ✅ | ✅ | ✅ |
| C/C++ | ⚠️ | ⚠️ | ⚠️ |

## Integración con Coding Agents

Puede delegar tareas complejas a Codex, Claude Code o Pi:

```
# Usar Codex para refactorizar
code refactor src/legacy.ts --agent:codex

# Usar Claude para documentar
code document src/ --agent:claude
```

## Configuración

| Variable | Descripción | Default |
|----------|-------------|---------|
| `CODE_DEFAULT_STYLE` | Estilo de código | `auto` |
| `CODE_MAX_COMPLEXITY` | Umbral de complejidad | `15` |
| `CODE_AUTO_FIX` | Aplicar fixes automáticamente | `false` |
| `CODE_IGNORE_PATTERNS` | Patrones a ignorar | `node_modules,dist` |

## Reglas de Análisis

El asistente detecta:

- **Security**: SQL injection, XSS, path traversal, hardcoded secrets
- **Performance**: N+1 queries, loops ineficientes, memory leaks
- **Style**: Nombres inconsistentes, funciones largas, código muerto
- **Logic**: Null checks faltantes, race conditions, off-by-one errors

## Integración

- **self-repair**: Los bugs encontrados pueden auto-corregirse
- **knowledge-base**: Busca en documentación indexada
- **expert-researcher**: Investiga mejores prácticas
