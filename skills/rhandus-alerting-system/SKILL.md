---
name: alerting-system
description: "Centralized alerting and notification system for OpenClaw. Multi-channel alerts, intelligent rules, escalation, and audit."
license: MIT
metadata:
  author: Rhandus Malpica
  company: Tiklick
  website: https://tiklick.com
  version: "1.0.0"
  openclaw:
    emoji: "🚨"
    ui:
      color: "#FF4444"
      icon: "bell"
---

# Alerting & Notification System

Sistema centralizado de alertas y notificaciones para OpenClaw. Alertas multi-canal, reglas inteligentes, escalación y auditoría.

## 🎯 Objetivo

Permitir que OpenClaw sea **proactivo** en lugar de reactivo, detectando problemas y notificando automáticamente antes de que impacten operaciones.

## 📋 Características

### Nivel 1 (Semana 1 - Base):
- ✅ **Multi-canal:** Telegram, Email (Gmail), Log
- ✅ **Reglas básicas:** Umbrales, patrones, horarios
- ✅ **Prioridades:** Info, Warning, Critical, Emergency
- ✅ **Agrupación:** Alertas relacionadas agrupadas
- ✅ **Historial:** Auditoría completa de alertas

### Nivel 2 (Semana 2 - Avanzado):
- 🔄 **Escalación automática:** Si no hay respuesta
- 📊 **Dashboard web:** Visualización en tiempo real
- 🤖 **Auto-resolución:** Alertas que se resuelven solas
- 📈 **Análisis:** Patrones y tendencias de alertas
- 🔗 **Integraciones:** Webhooks, Slack, etc.

### Nivel 3 (Semana 3 - Inteligente):
- 🧠 **Aprendizaje:** Reduce falsos positivos
- ⏰ **Horarios inteligentes:** Respeta horas no laborales
- 👥 **Routing:** Enruta a persona correcta
- 📱 **Mobile:** Notificaciones push
- 🔄 **Feedback loop:** Mejora continua

## 🚀 Uso

### Comandos Principales:

#### `alert monitor`
Monitorea un endpoint o recurso.

```bash
# Monitorear API Tiklick
alert monitor https://api.tiklick.com/health --interval 60 --channel telegram

# Monitorear archivo de log
alert monitor /var/log/tiklick_app.log --pattern "ERROR\|CRITICAL" --channel email

# Monitorear métrica del sistema
alert monitor system.cpu --threshold 80 --duration 300 --channel both
```

#### `alert threshold`
Configura alertas basadas en umbrales.

```bash
# Ventas mínimas diarias
alert threshold /workspace/ventas.csv --column "total" --min 1000000 --channel email

# Uso máximo de disco
alert threshold system.disk --path /workspace --max 90 --channel telegram

# Tiempo respuesta API
alert threshold api.response_time --url https://api.tiklick.com --max 2000 --channel both
```

#### `alert pattern`
Busca patrones en logs o datos.

```bash
# Errores críticos en logs
alert pattern /var/log/app.log --pattern "FATAL\|SEGFAULT\|OutOfMemory" --channel telegram

# Intentos fallidos de login
alert pattern /var/log/auth.log --pattern "Failed password" --count 5 --window 300 --channel email

# Patrones de seguridad
alert pattern security --type "brute_force\|sql_injection\|xss" --channel both
```

#### `alert status`
Muestra estado de alertas.

```bash
# Alertas activas
alert status --active

# Historial de alertas
alert status --history --days 7

# Resumen estadístico
alert status --stats
```

#### `alert resolve`
Marca alertas como resueltas.

```bash
# Resolver alerta específica
alert resolve ALERT-1234

# Resolver todas de un servicio
alert resolve --service api-tiklick

# Auto-resolver después de verificación
alert resolve --auto --check "curl -s https://api.tiklick.com/health"
```

## ⚙️ Configuración

### Canales Disponibles:
1. **telegram** - Notificación inmediata a Telegram
2. **email** - Email a lista configurada
3. **log** - Registro en archivo de log
4. **dashboard** - Visualización en dashboard web
5. **all** - Todos los canales

### Prioridades:
- **emergency** (🔴) - Requiere acción inmediata
- **critical** (🟠) - Acción requerida pronto
- **warning** (🟡) - Atención recomendada
- **info** (🔵) - Informativo solamente

### Variables de Entorno:
```bash
ALERTING_TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID}"  # Variable de entorno
ALERTING_EMAIL_RECIPIENTS="rhandus@gmail.com,admin@tiklick.com"
ALERTING_SMTP_SERVER="smtp.gmail.com"
ALERTING_DASHBOARD_URL="http://localhost:3000/alerts"
ALERTING_RETENTION_DAYS="30"
```

## 📊 Integración con Skills Existentes

### Con API Testing:
```bash
# Si API falla, generar alerta
api test https://api.tiklick.com/health --on-failure "alert trigger api.down --priority critical"
```

### Con Security Tools:
```bash
# Alertar hallazgos críticos de seguridad
security scan --on-finding-critical "alert trigger security.critical --details {finding}"
```

### Con Docker Management:
```bash
# Alertar si contenedor cae
docker monitor tiklick-app --on-crash "alert trigger docker.crash --container {name}"
```

### Con Calendar Integration:
```bash
# Recordatorios de eventos importantes
calendar monitor --before 30 --action "alert trigger calendar.reminder --event {title}"
```

## 🎯 Ejemplos para Tiklick

### Caso 1: Monitoreo API Producción
```bash
# Configurar monitoreo 24/7
alert monitor https://api.tiklick.com/health \
  --interval 30 \
  --timeout 10 \
  --expected-status 200 \
  --on-failure "alert trigger api.production.down --priority emergency" \
  --on-recovery "alert resolve api.production.down" \
  --channel all
```

### Caso 2: Ventas por Debajo de Umbral
```bash
# Verificar ventas cada hora
alert threshold /workspace/ventas/ultima_hora.csv \
  --column "total_ventas" \
  --min 500000 \
  --check-every 3600 \
  --on-below "alert trigger sales.low --priority warning --details 'Ventas bajas: {value}'" \
  --channel telegram,email
```

### Caso 3: Backup Fallido
```bash
# Verificar backup diario
alert monitor /workspace/backups/latest.tar.gz \
  --max-age 86400 \
  --min-size 1000000 \
  --on-failure "alert trigger backup.failed --priority critical" \
  --channel email
```

### Caso 4: Horario No Laboral (Silenciar)
```bash
# Solo alertas críticas fuera de horario
alert rule working-hours \
  --days mon-fri \
  --time 08:00-18:00 \
  --action "allow-all" \
  --else "allow-only critical,emergency"
```

## 🔧 Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Detección     │───▶│   Procesamiento │───▶│   Notificación  │
│  (Monitores)    │    │    (Reglas)     │    │   (Canales)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  APIs Tiklick   │    │  Agrupación     │    │  Telegram       │
│  Sistema        │    │  Escalación     │    │  Email          │
│  Logs           │    │  Deduplicación  │    │  Dashboard      │
│  Métricas       │    │  Priorización   │    │  Log            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📈 Métricas y Monitoreo

### Métricas a Seguir:
- **Tiempo medio de detección:** < 60 segundos
- **Tiempo medio de resolución:** < 15 minutos
- **Falsos positivos:** < 5%
- **Cobertura:** > 95% de sistemas críticos
- **Satisfacción:** > 4.5/5 en encuestas

### Dashboard de Alertas:
- **Alertas activas** por prioridad
- **Tendencia histórica**
- **Top servicios con problemas**
- **Tiempos de respuesta**
- **Estadísticas de resolución**

## 🛡️ Seguridad

- **Autenticación:** Verificación de origen de alertas
- **Autorización:** Quién puede configurar/ver alertas
- **Auditoría:** Log completo de todas las acciones
- **Rate limiting:** Prevenir spam de alertas
- **Cifrado:** Datos sensibles cifrados

## 🔄 Mantenimiento

### Diario:
- Revisar alertas activas
- Verificar canales de notificación
- Limpiar alertas resueltas antiguas

### Semanal:
- Revisar reglas y ajustar umbrales
- Analizar falsos positivos
- Actualizar contactos de escalación

### Mensual:
- Auditoría completa del sistema
- Revisión de métricas y KPIs
- Plan de mejora continua

## 🚨 Plan de Implementación

### Semana 1: Base (Actual)
- Estructura del skill
- Canal Telegram
- Reglas básicas
- Testing inicial

### Semana 2: Avanzado
- Canal Email
- Dashboard web
- Reglas avanzadas
- Integración skills

### Semana 3: Inteligente
- Escalación automática
- Aprendizaje automático
- Mobile notifications
- Optimización

---

**Estado:** 🟡 EN DESARROLLO (Semana 1)  
**Próximo hito:** Canal Telegram funcional  
**Responsable:** TK Claw  
**Fecha objetivo:** 2026-02-26