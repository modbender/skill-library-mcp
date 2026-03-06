# LobsterGuard v6.1 — Auditor de Seguridad para OpenClaw

> **[Read in English](README.md)**

Plugin de seguridad para OpenClaw controlable desde Telegram. Escanea, detecta y corrige problemas de seguridad en tu servidor.

## Qué hace

- **68 checks de seguridad** en 6 categorías
- **11 auto-fixes** ejecutables desde Telegram
- **Scanner de skills** con 4 capas de análisis
- **Quarantine watcher** que vigila skills sospechosas 24/7
- **Auto-scan cada 6 horas** con alertas por Telegram
- **31 patrones de amenazas** en tiempo real
- **Limpieza automática de procesos fantasma** (post-comando + cron)
- **Bilingüe** (Español / English) — idioma seleccionado durante la instalación
- **Auto-detecta credenciales de Telegram** desde la configuración de OpenClaw

## Categorías de Checks

| Categoría | Checks | Qué revisa |
|-----------|--------|------------|
| OpenClaw | 5 | Gateway, autenticación, versión, credenciales, skills |
| Servidor | 10 | SSH, firewall, fail2ban, puertos, docker, disco |
| Avanzado | 13 | Permisos, SSL, backups, supply chain, CORS, sandbox |
| IA Agental | 22 | Prompt injection, exfiltración, MCP, typosquatting, memoria |
| Forense | 7 | Rootkits, reverse shells, cryptominers, DNS tunneling |
| Endurecimiento | 11 | Kernel, systemd, auditd, core dumps, swap, namespaces |

## Comandos de Telegram

### Escaneo
- `/scan` — Escaneo completo con score 0-100
- `/checkskill [nombre|all]` — Escanea skills con 4 capas de análisis
- `/lgsetup` — Verifica que LobsterGuard esté bien instalado
- `/fixlist` — Lista todos los fixes disponibles
- `/cleanup` — Elimina procesos fantasma de OpenClaw

### Auto-fixes
| Comando | Qué arregla |
|---------|-------------|
| `/fixfw` | Instala y configura firewall UFW |
| `/fixbackup` | Configura backups automáticos diarios |
| `/fixkernel` | Endurece parámetros del kernel |
| `/fixcore` | Deshabilita core dumps |
| `/fixaudit` | Instala y configura auditd |
| `/fixsandbox` | Configura sandbox y permisos |
| `/fixsystemd` | Crea/endurece servicio systemd para OpenClaw |
| `/fixenv` | Protege variables de entorno con secrets |
| `/fixtmp` | Limpia y asegura /tmp |
| `/fixcode` | Restricciones de ejecución de código |
| `/runuser` | Migra OpenClaw de root a usuario dedicado |


## ⚠️ Importante: Aislamiento con Docker (Altamente Recomendado)

LobsterGuard puede detectar y corregir la mayoría de problemas de seguridad automáticamente, pero **la mejora de seguridad más importante** que puedes hacer es ejecutar OpenClaw dentro de un contenedor Docker.

Sin aislamiento de contenedor, OpenClaw corre directamente en tu sistema con acceso a todo — archivos, red, procesos y configuraciones del sistema. Si un skill malicioso o un ataque de prompt injection compromete OpenClaw, el atacante tiene acceso directo a tu servidor.

Ejecutar OpenClaw en Docker proporciona:

- **Aislamiento de archivos** — OpenClaw solo puede acceder a los volúmenes montados, no a todo tu sistema
- **Aislamiento de red** — limita qué puertos y servicios puede alcanzar OpenClaw
- **Aislamiento de procesos** — un contenedor comprometido no puede ver ni afectar procesos del host
- **Límites de recursos** — evita abuso de CPU/memoria por procesos descontrolados
- **Recuperación fácil** — destruye y recrea el contenedor sin afectar tu servidor

Este es el único check en LobsterGuard que no tiene auto-fix porque requiere reestructurar cómo se despliega OpenClaw. Una guía paso a paso detallada está incluida en `docs/docker-setup-guide.md`.

**Sin Docker, tu score de LobsterGuard está limitado a 95/100.** Con Docker, puedes alcanzar un 100/100 perfecto.

## Instalación

```bash
git clone https://github.com/jarb02/lobsterguard.git
cd lobsterguard
sudo bash install.sh
```

El instalador:
1. Detecta tu instalación de OpenClaw y el usuario
2. Te pide seleccionar un idioma (Español o English)
3. Instala dependencias (ufw, auditd)
4. Configura permisos sudo (NOPASSWD para comandos de seguridad)
5. Copia scripts y registra el plugin
6. Configura limpieza automática de procesos fantasma (cron cada 5 minutos)
7. Verifica la instalación

Las credenciales de Telegram se detectan automáticamente desde tu configuración de OpenClaw — no necesitas configurar nada manualmente.

Para desinstalar:
```bash
sudo bash install.sh --uninstall
```

## Requisitos

- OpenClaw instalado y corriendo
- Python 3
- Telegram configurado en OpenClaw
- Acceso root (solo para instalar)

## Estructura del Proyecto

```
lobsterguard/
├── scripts/
│   ├── check.py              # 68 checks de seguridad
│   ├── fix_engine.py          # 13 auto-fixes con rollback
│   ├── skill_scanner.py       # Scanner de skills (4 capas)
│   ├── autoscan.py            # Auto-scan periódico
│   ├── quarantine_watcher.py  # Vigila carpeta quarantine
│   ├── cleanup.py             # Limpieza de procesos fantasma
│   ├── telegram_utils.py      # Utilidades compartidas de Telegram
│   └── lgsetup.py             # Asistente de configuración
├── extension/
│   └── dist/
│       ├── index.js           # Plugin OpenClaw (16 comandos)
│       ├── interceptor.js     # 31 patrones de amenazas
│       ├── watcher.js         # File watcher
│       ├── fix_tool.js        # Tool de remediación
│       └── types.js           # Tipos
├── data/
│   └── config.json            # Preferencia de idioma
└── install.sh                 # Instalador automático
```

## Licencia

MIT
