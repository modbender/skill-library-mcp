#!/bin/bash
# ntopng Admin Helper for Angie - Network Monitor
# Monitoreo general de red: dispositivos, tráfico y conexiones

set -e

OPNSENSE_HOST="${OPNSENSE_HOST:-192.168.1.1}"
OPNSENSE_SSH_PORT="${OPNSENSE_SSH_PORT:-50222}"

# ============================================
# UTILIDADES
# ============================================

ssh_opnsense() {
    ssh -p "$OPNSENSE_SSH_PORT" "root@$OPNSENSE_HOST" "$@"
}

# ============================================
# LISTADO DE DISPOSITIVOS
# ============================================

list_devices() {
    local limit="${1:-20}"
    
    echo "=== DISPOSITIVOS EN LA RED ==="
    
    local keys=$(ssh_opnsense "redis-cli keys 'ntopng.serialized_macs.ifid_0_*'" 2>/dev/null | head -$limit)
    
    for key in $keys; do
        local data=$(ssh_opnsense "redis-cli get '$key'" 2>/dev/null)
        if [[ -n "$data" && "$data" != "nil" ]]; then
            local mac=$(echo "$data" | jq -r '.mac')
            local sent=$(echo "$data" | jq -r '.sent.bytes')
            local rcvd=$(echo "$data" | jq -r '.rcvd.bytes')
            local total=$((sent + rcvd))
            local last_seen=$(echo "$data" | jq -r '.seen.last')
            
            # Buscar IP
            local ip=$(ssh_opnsense "arp -an" 2>/dev/null | grep -i "$mac" | head -1 | grep -oE '192\.168\.[0-9]+\.[0-9]+')
            ip=${ip:-"desconocida"}
            
            printf "%-18s | %-15s | Total: %6s MB | Ultimo: %s\n" "$mac" "$ip" "$((total/1024/1024))" "$last_seen"
        fi
    done
}

# ============================================
# INFORMACIÓN DE DISPOSITIVO
# ============================================

device_info() {
    local target="$1"
    
    if [[ -z "$target" ]]; then
        echo "Uso: device-info <ip|mac>"
        return 1
    fi
    
    local mac=""
    local ip=""
    
    # Determinar si es IP o MAC
    if echo "$target" | grep -qE "^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$"; then
        mac="$target"
        ip=$(ssh_opnsense "arp -an" 2>/dev/null | grep -i "$mac" | head -1 | grep -oE '192\.168\.[0-9]+\.[0-9]+')
    else
        ip="$target"
        mac=$(ssh_opnsense "arp -an" 2>/dev/null | grep "$ip" | head -1 | awk '{print $4}')
    fi
    
    echo "=== INFORMACION DEL DISPOSITIVO ==="
    echo "IP: ${ip:-No encontrada}"
    echo "MAC: ${mac:-No encontrada}"
    
    if [[ -n "$mac" && "$mac" != "<incomplete>" ]]; then
        local data=$(ssh_opnsense "redis-cli get 'ntopng.serialized_macs.ifid_0_${mac}'" 2>/dev/null)
        if [[ -n "$data" && "$data" != "nil" ]]; then
            echo ""
            echo "Trafico:"
            local sent=$(echo "$data" | jq -r '.sent.bytes')
            local rcvd=$(echo "$data" | jq -r '.rcvd.bytes')
            local pkts_out=$(echo "$data" | jq -r '.sent.packets')
            local pkts_in=$(echo "$data" | jq -r '.rcvd.packets')
            local devtype=$(echo "$data" | jq -r '.devtype')
            
            echo "  Enviado: $((sent/1024/1024)) MB"
            echo "  Recibido: $((rcvd/1024/1024)) MB"
            echo "  Packets Out: $pkts_out"
            echo "  Packets In: $pkts_in"
            
            echo ""
            echo "Tipo: $(case $devtype in
                0) echo "Desconocido" ;;
                1) echo "PC/Workstation" ;;
                2) echo "Servidor" ;;
                3) echo "Smartphone" ;;
                4) echo "Tablet" ;;
                5) echo "Laptop" ;;
                6) echo "Telefono/Dispositivo movil" ;;
                8) echo "Virtual/Container" ;;
                *) echo "Codigo $devtype" ;;
            esac)"
        fi
    fi
}

# ============================================
# CONEXIONES Y DOMINIOS
# ============================================

device_connections() {
    local ip="$1"
    local lines="${2:-100}"
    
    if [[ -z "$ip" ]]; then
        echo "Uso: connections <ip> [líneas]"
        return 1
    fi
    
    echo "=== CONEXIONES DE $ip (últimas $lines) ==="
    
    # Buscar en logs de ntopng
    ssh_opnsense "grep '$ip' /var/db/ntopng/ntopng.log | tail -$lines" 2>/dev/null | grep -oE "'[^']+\.(com|net|org|io|co|app|dev|cloud)'" | tr -d "'" | sort | uniq -c | sort -nr | head -20 | while read count domain; do
        printf "%4s conexiones | %s\n" "$count" "$domain"
    done
}

# ============================================
# TRÁFICO POR PROTOCOLO/APP
# ============================================

app_detection() {
    local app="$1"
    local lines="${2:-200}"
    
    if [[ -z "$app" ]]; then
        echo "Uso: app <nombre-app> [líneas]"
        echo "Ejemplos: app tls, app dns, app http, app ssh"
        return 1
    fi
    
    echo "=== DISPOSITIVOS USANDO: $app ==="
    
    ssh_opnsense "grep -i '$app' /var/db/ntopng/ntopng.log | tail -$lines" 2>/dev/null | grep -oE "'192\.168\.[0-9]+\.[0-9]+'" | tr -d "'" | sort | uniq -c | sort -nr | head -10 | while read count ip; do
        local mac=$(ssh_opnsense "arp -an 2>/dev/null | grep '$ip' | head -1 | awk '{print \$4}'")
        printf "%4s flujos | IP: %-15s | MAC: %s\n" "$count" "$ip" "${mac:-unknown}"
    done
}

# ============================================
# ESTADÍSTICAS GENERALES
# ============================================

network_stats() {
    echo "=== ESTADÍSTICAS DE RED ==="
    
    local device_count=$(ssh_opnsense "redis-cli keys 'ntopng.serialized_macs.ifid_0_*' | wc -l" 2>/dev/null)
    local active_now=$(ssh_opnsense "arp -an 2>/dev/null | grep -c 'ether'")
    
    echo "Dispositivos detectados (histórico): $device_count"
    echo "Dispositivos activos ahora: $active_now"
    echo ""
    
    # Top 5 por tráfico
    echo "Top 5 por tráfico total:"
    ssh_opnsense "redis-cli keys 'ntopng.serialized_macs.ifid_0_*'" 2>/dev/null | while read key; do
        local data=$(ssh_opnsense "redis-cli get '$key'" 2>/dev/null)
        if [[ -n "$data" && "$data" != "nil" ]]; then
            local mac=$(echo "$data" | jq -r '.mac')
            local sent=$(echo "$data" | jq -r '.sent.bytes')
            local rcvd=$(echo "$data" | jq -r '.rcvd.bytes')
            echo "$((sent + rcvd)) $mac"
        fi
    done | sort -rn | head -5 | while read total mac; do
        local ip=$(ssh_opnsense "arp -an 2>/dev/null | grep -i '$mac' | head -1 | grep -oE '192\.168\.[0-9]+\.[0-9]+'")
        printf "  %-18s | %s | %s MB\n" "$mac" "${ip:-N/A}" "$((total/1024/1024))"
    done
}

# ============================================
# ESTADO DEL SERVICIO
# ============================================

service_status() {
    local pid=$(ssh_opnsense "pgrep -f ntopng" 2>/dev/null)
    if [[ -n "$pid" ]]; then
        local uptime=$(ssh_opnsense "ps -o etime= -p $pid" 2>/dev/null | tr -d ' ')
        echo "Status: Running (PID: $pid, Uptime: $uptime)"
    else
        echo "Status: Stopped"
    fi
}

# ============================================
# USO
# ============================================

show_usage() {
    cat << EOF
ntopng Network Monitor

DISPOSITIVOS:
  list [n]              Listar dispositivos (default: 20)
  device-info <ip|mac>  Información detallada de dispositivo
  connections <ip> [n]  Ver dominios conectados por dispositivo

ANÁLISIS:
  app <nombre> [n]      Detectar dispositivos por protocolo/app
  stats                 Estadísticas generales de red
  status                Estado del servicio ntopng

EJEMPLOS:
  $0 list                    # Ver dispositivos en red
  $0 device-info 192.168.1.150  # Info de dispositivo específico
  $0 connections 192.168.1.150  # Qué dominios contacta
  $0 app tls                 # Dispositivos usando TLS/HTTPS
  $0 stats                   # Stats generales

NOTAS:
  - Requiere ntopng ejecutándose en OPNsense
  - Datos almacenados en Redis
  - Logs en /var/db/ntopng/ntopng.log

EOF
}

case "${1:-}" in
    list)
        list_devices "${2:-20}"
        ;;
    device-info)
        device_info "$2"
        ;;
    connections)
        device_connections "$2" "${3:-100}"
        ;;
    app)
        app_detection "$2" "${3:-200}"
        ;;
    stats)
        network_stats
        ;;
    status)
        service_status
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
