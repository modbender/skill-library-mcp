#!/bin/bash
# 🚨 Script de Integración del Sistema de Alertas
# Para uso inmediato con OpenClaw

set -e

ALERT_SYSTEM_DIR="/workspace/skills/alerting-system"
ALERT_DB="/workspace/.openclaw_alerts.json"
LOG_DIR="/var/log/openclaw_alerts"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    log_info "Verificando dependencias..."
    
    # Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js no encontrado. Instalar con: sudo apt install nodejs"
        exit 1
    fi
    
    # curl
    if ! command -v curl &> /dev/null; then
        log_warning "curl no encontrado. Instalar con: sudo apt install curl"
    fi
    
    # Directorio de logs
    if [ ! -d "$LOG_DIR" ]; then
        log_info "Creando directorio de logs: $LOG_DIR"
        sudo mkdir -p "$LOG_DIR"
        sudo chown rhandus:rhandus "$LOG_DIR"
    fi
    
    log_success "Dependencias verificadas"
}

# Inicializar sistema
initialize_system() {
    log_info "Inicializando sistema de alertas..."
    
    if [ ! -f "$ALERT_DB" ]; then
        log_info "Creando base de datos de alertas..."
        echo '{"alerts": [], "rules": [], "history": []}' > "$ALERT_DB"
        log_success "Base de datos creada: $ALERT_DB"
    fi
    
    # Probar sistema básico
    cd "$ALERT_SYSTEM_DIR"
    if node src/index.js stats &> /dev/null; then
        log_success "Sistema de alertas inicializado correctamente"
    else
        log_error "Error inicializando sistema de alertas"
        exit 1
    fi
}

# Crear alerta de ejemplo
create_example_alert() {
    log_info "Creando alerta de ejemplo..."
    
    cd "$ALERT_SYSTEM_DIR"
    node src/index.js create "Sistema de Alertas Iniciado" "El sistema de alertas ha sido inicializado correctamente" "alerting-system" "info"
    
    log_success "Alerta de ejemplo creada"
}

# Monitorear API de ejemplo
monitor_example_api() {
    local url="${1:-https://httpbin.org/status/200}"
    
    log_info "Monitoreando API de ejemplo: $url"
    
    cd "$ALERT_SYSTEM_DIR"
    node src/index.js monitor "$url" 200
    
    log_success "Monitoreo completado"
}

# Mostrar estado actual
show_status() {
    log_info "Estado actual del sistema de alertas:"
    
    cd "$ALERT_SYSTEM_DIR"
    node src/index.js stats
    
    echo ""
    log_info "Alertas activas:"
    node src/index.js list active
}

# Integrar con skill API Testing
integrate_with_api_testing() {
    log_info "Integrando con skill API Testing..."
    
    local api_testing_dir="/workspace/skills/api-testing"
    
    if [ ! -d "$api_testing_dir" ]; then
        log_warning "Skill API Testing no encontrado"
        return 1
    fi
    
    # Crear script de integración
    cat > "$api_testing_dir/alert_integration.js" << 'EOF'
/**
 * Integración entre API Testing y Alerting System
 */

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function alertOnAPIFailure(url, error) {
    const command = `cd /workspace/skills/alerting-system && \
                    node src/index.js create \
                    "API Testing Failure: ${url}" \
                    "Error al probar API: ${error}" \
                    "api-testing" \
                    "critical"`;
    
    try {
        await execAsync(command, { shell: true });
        console.log(`🚨 Alerta creada para fallo de API: ${url}`);
    } catch (err) {
        console.error(`Error creando alerta: ${err.message}`);
    }
}

export async function monitorAPIContinuously(url, interval = 300) {
    console.log(`📡 Monitoreando API continuamente: ${url} (cada ${interval}s)`);
    
    setInterval(async () => {
        try {
            const response = await fetch(url, { timeout: 10000 });
            
            if (!response.ok) {
                await alertOnAPIFailure(url, `HTTP ${response.status}`);
            }
        } catch (error) {
            await alertOnAPIFailure(url, error.message);
        }
    }, interval * 1000);
}
EOF
    
    log_success "Integración con API Testing creada"
    log_info "Archivo: $api_testing_dir/alert_integration.js"
}

# Integrar con skill Security Tools
integrate_with_security_tools() {
    log_info "Integrando con skill Security Tools..."
    
    local security_dir="/workspace/skills/security-tools"
    
    if [ ! -d "$security_dir" ]; then
        log_warning "Skill Security Tools no encontrado"
        return 1
    fi
    
    # Crear script de integración
    cat > "$security_dir/alert_integration.js" << 'EOF'
/**
 * Integración entre Security Tools y Alerting System
 */

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export async function alertOnSecurityFinding(finding) {
    const { severity, title, description, file } = finding;
    
    let priority = 'info';
    if (severity === 'high') priority = 'critical';
    if (severity === 'medium') priority = 'warning';
    
    const command = `cd /workspace/skills/alerting-system && \
                    node src/index.js create \
                    "Security Finding: ${title}" \
                    "${description}\\n\\nArchivo: ${file}" \
                    "security-tools" \
                    "${priority}"`;
    
    try {
        await execAsync(command, { shell: true });
        console.log(`🔐 Alerta de seguridad creada: ${title}`);
    } catch (err) {
        console.error(`Error creando alerta de seguridad: ${err.message}`);
    }
}

export async function alertOnCriticalPermission(file, permission) {
    const command = `cd /workspace/skills/alerting-system && \
                    node src/index.js create \
                    "Permiso Peligroso Detectado" \
                    "Archivo: ${file}\\nPermiso: ${permission}\\n\\nEste permiso podría ser un riesgo de seguridad." \
                    "security-tools" \
                    "critical"`;
    
    try {
        await execAsync(command, { shell: true });
        console.log(`🔐 Alerta de permiso peligroso creada: ${file}`);
    } catch (err) {
        console.error(`Error creando alerta: ${err.message}`);
    }
}
EOF
    
    log_success "Integración con Security Tools creada"
    log_info "Archivo: $security_dir/alert_integration.js"
}

# Crear cron job para monitoreo automático
setup_cron_job() {
    log_info "Configurando cron job para monitoreo automático..."
    
    local cron_file="/etc/cron.d/openclaw-alerting"
    local script_path="/workspace/skills/alerting-system/cron_monitor.sh"
    
    # Crear script de monitoreo
    cat > "$script_path" << 'EOF'
#!/bin/bash
# Cron job para monitoreo automático de APIs críticas

ALERT_DIR="/workspace/skills/alerting-system"
LOG_FILE="/var/log/openclaw_alerts/cron.log"

echo "[$(date)] Iniciando monitoreo automático..." >> "$LOG_FILE"

# Monitorear APIs Tiklick (ejemplos - ajustar URLs reales)
APIS=(
    "https://api.tiklick.com/health"
    "https://admin.tiklick.com"
    "https://app.tiklick.com"
)

for api in "${APIS[@]}"; do
    echo "Monitoreando: $api" >> "$LOG_FILE"
    cd "$ALERT_DIR" && node src/index.js monitor "$api" 200 >> "$LOG_FILE" 2>&1
    sleep 2
done

# Verificar sistema de alertas
cd "$ALERT_DIR" && node src/index.js stats >> "$LOG_FILE" 2>&1

echo "[$(date)] Monitoreo completado" >> "$LOG_FILE"
EOF
    
    chmod +x "$script_path"
    
    # Configurar cron job (cada 15 minutos)
    echo "*/15 * * * * rhandus $script_path" | sudo tee "$cron_file" > /dev/null
    
    log_success "Cron job configurado: cada 15 minutos"
    log_info "Script: $script_path"
    log_info "Log: /var/log/openclaw_alerts/cron.log"
}

# Mostrar ayuda
show_help() {
    echo -e "${BLUE}🚨 Sistema de Alertas OpenClaw - Script de Integración${NC}"
    echo ""
    echo "Uso: $0 [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo "  init           - Inicializar sistema completo"
    echo "  status         - Mostrar estado actual"
    echo "  example        - Crear alerta de ejemplo"
    echo "  monitor <url>  - Monitorear API específica"
    echo "  integrate      - Integrar con skills existentes"
    echo "  cron           - Configurar cron job automático"
    echo "  help           - Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  $0 init"
    echo "  $0 monitor https://api.tiklick.com/health"
    echo "  $0 integrate"
    echo ""
}

# Main
case "$1" in
    "init")
        check_dependencies
        initialize_system
        create_example_alert
        show_status
        ;;
        
    "status")
        show_status
        ;;
        
    "example")
        create_example_alert
        ;;
        
    "monitor")
        if [ -z "$2" ]; then
            log_error "Se requiere URL para monitorear"
            echo "Uso: $0 monitor <url>"
            exit 1
        fi
        monitor_example_api "$2"
        ;;
        
    "integrate")
        integrate_with_api_testing
        integrate_with_security_tools
        log_success "Integración completada"
        ;;
        
    "cron")
        setup_cron_job
        ;;
        
    "help"|"")
        show_help
        ;;
        
    *)
        log_error "Comando no reconocido: $1"
        show_help
        exit 1
        ;;
esac