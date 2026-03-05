#!/usr/bin/env bash
# iDRAC Redfish API Helper Script
# Supports iDRAC 8/9 on Dell PowerEdge servers

set -euo pipefail

CONFIG_FILE="${IDRAC_CONFIG:-$HOME/.config/idrac-skill/config}"
CREDS_FILE="$HOME/.idrac-credentials"

# Load configuration
load_config() {
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config not found at $CONFIG_FILE" >&2
    echo "Create it with:" >&2
    echo "  mkdir -p ~/.config/idrac-skill" >&2
    echo "  cat > ~/.config/idrac-skill/config <<EOF" >&2
    echo '  IDRAC_IP="<your-idrac-ip>"' >&2
    echo '  CREDS_SOURCE="file"  # or "1password" or "env"' >&2
    echo "  EOF" >&2
    exit 1
  fi
  # shellcheck source=/dev/null
  source "$CONFIG_FILE"

  if [ -z "${IDRAC_IP:-}" ]; then
    echo "Error: IDRAC_IP not set in $CONFIG_FILE" >&2
    exit 1
  fi

  IDRAC_BASE="https://${IDRAC_IP}/redfish/v1"
  CREDS_SOURCE="${CREDS_SOURCE:-file}"
}

# Hydrate credentials based on configured source
hydrate_creds() {
  case "${CREDS_SOURCE}" in
    1password)
      if [ ! -f "$CREDS_FILE" ]; then
        local op_item="${OP_ITEM:?OP_ITEM not set in config}"
        echo "Hydrating credentials from 1Password ($op_item)..." >&2
        op item get "$op_item" --fields username,password --format json | \
          jq -r '"\(.[0].value):\(.[1].value)"' > "$CREDS_FILE"
        chmod 600 "$CREDS_FILE"
      fi
      ;;
    env)
      if [ -z "${IDRAC_USER:-}" ] || [ -z "${IDRAC_PASS:-}" ]; then
        echo "Error: IDRAC_USER and IDRAC_PASS must be set for CREDS_SOURCE=env" >&2
        exit 1
      fi
      # Write ephemeral creds file for curl
      echo "${IDRAC_USER}:${IDRAC_PASS}" > "$CREDS_FILE"
      chmod 600 "$CREDS_FILE"
      ;;
    file)
      if [ ! -f "$CREDS_FILE" ]; then
        echo "Error: Credentials file not found at $CREDS_FILE" >&2
        echo "Create it: echo 'username:password' > $CREDS_FILE && chmod 600 $CREDS_FILE" >&2
        exit 1
      fi
      ;;
    *)
      echo "Error: Unknown CREDS_SOURCE '$CREDS_SOURCE' (use: 1password, file, env)" >&2
      exit 1
      ;;
  esac
}

# API call wrapper
api_get() {
  local endpoint="$1"
  hydrate_creds
  curl -k -s -u "$(cat "$CREDS_FILE")" "${IDRAC_BASE}${endpoint}"
}

# Load config before any command
load_config

# Commands
case "${1:-help}" in
  status)
    echo "=== System Status ==="
    api_get "/Systems/System.Embedded.1" | jq '{
      Model,
      Manufacturer,
      ServiceTag: .SKU,
      PowerState,
      Health: .Status.Health,
      State: .Status.State,
      BiosVersion,
      Processors: .ProcessorSummary.Count,
      LogicalProcessors: .ProcessorSummary.LogicalProcessorCount,
      MemoryGB: .MemorySummary.TotalSystemMemoryGiB
    }'
    ;;

  health)
    echo "=== Health Status ==="
    api_get "/Systems/System.Embedded.1" | jq -r '
      "Overall Health: \(.Status.Health)",
      "State: \(.Status.State)",
      "Power: \(.PowerState)"
    '
    echo ""
    echo "=== Thermal Status ==="
    api_get "/Chassis/System.Embedded.1/Thermal" | jq -r '
      "Temperatures:",
      (.Temperatures[] | "  \(.Name): \(.ReadingCelsius)°C [\(.Status.Health)]"),
      "",
      "Fans:",
      (.Fans[] | "  \(.Name): \(.Reading) \(.Units) [\(.Status.Health)]")
    '
    ;;

  power)
    api_get "/Systems/System.Embedded.1" | jq -r '.PowerState'
    ;;

  inventory)
    echo "=== Hardware Inventory ==="
    api_get "/Systems/System.Embedded.1" | jq '{
      System: {
        Model,
        Manufacturer,
        SerialNumber,
        ServiceTag: .SKU,
        BiosVersion
      },
      Processors: .ProcessorSummary,
      Memory: .MemorySummary
    }'
    ;;

  logs)
    echo "=== System Event Log (last 10) ==="
    api_get "/Managers/iDRAC.Embedded.1/Logs/Sel" | \
      jq -r '.Members[:10][] | "\(.Created) [\(.Severity)]: \(.Message)"'
    ;;

  thermal)
    echo "=== Thermal Details ==="
    api_get "/Chassis/System.Embedded.1/Thermal" | jq '{
      Temperatures: [.Temperatures[] | {
        Name,
        Reading: .ReadingCelsius,
        Upper: .UpperThresholdCritical,
        Status: .Status.Health
      }],
      Fans: [.Fans[] | {
        Name,
        Speed: .Reading,
        Units,
        Status: .Status.Health
      }]
    }'
    ;;

  storage)
    echo "=== Storage Controllers ==="
    api_get "/Systems/System.Embedded.1/Storage" | \
      jq -r '.Members[]."@odata.id"' | while read -r controller; do
        echo ""
        echo "Controller: $controller"
        api_get "$controller" | jq '{
          Name,
          Model: .StorageControllers[0].Model,
          Status: .StorageControllers[0].Status,
          Drives: [.Drives[]."@odata.id"]
        }'
      done
    ;;

  reset-types)
    echo "=== Available Reset Types ==="
    api_get "/Systems/System.Embedded.1" | \
      jq -r '.Actions."#ComputerSystem.Reset"."ResetType@Redfish.AllowableValues"[]'
    ;;

  test)
    echo "Testing iDRAC connectivity and authentication..."
    echo "Target: ${IDRAC_IP}"
    echo "Credential source: ${CREDS_SOURCE}"
    echo ""

    # Test 1: Network connectivity
    echo -n "1. Network connectivity... "
    if curl -k -s --connect-timeout 5 "https://${IDRAC_IP}/redfish/v1/" > /dev/null 2>&1; then
      echo "✅ OK"
    else
      echo "❌ FAILED (cannot reach ${IDRAC_IP})"
      exit 1
    fi

    # Test 2: Authentication
    echo -n "2. Credential hydration (${CREDS_SOURCE})... "
    hydrate_creds
    if [ -f "$CREDS_FILE" ]; then
      echo "✅ OK"
    else
      echo "❌ FAILED"
      exit 1
    fi

    # Test 3: API access
    echo -n "3. API access (Redfish root)... "
    RESPONSE=$(api_get "/" 2>&1)
    if echo "$RESPONSE" | jq -e '.RedfishVersion' > /dev/null 2>&1; then
      VERSION=$(echo "$RESPONSE" | jq -r '.RedfishVersion')
      echo "✅ OK (Redfish ${VERSION})"
    else
      echo "❌ FAILED (invalid response or auth failure)"
      exit 1
    fi

    # Test 4: System query
    echo -n "4. System data... "
    SYSTEM=$(api_get "/Systems/System.Embedded.1" 2>&1)
    if echo "$SYSTEM" | jq -e '.Model' > /dev/null 2>&1; then
      MODEL=$(echo "$SYSTEM" | jq -r '.Model')
      HEALTH=$(echo "$SYSTEM" | jq -r '.Status.Health')
      echo "✅ OK (${MODEL}, Health: ${HEALTH})"
    else
      echo "❌ FAILED"
      exit 1
    fi

    echo ""
    echo "All tests passed! iDRAC API is fully accessible."
    ;;

  help|*)
    cat <<EOF
iDRAC Redfish API Helper

Usage: $0 <command>

Commands:
  test          Test connectivity and authentication
  status        System summary (model, power, CPU, memory)
  health        Health checks (overall, temps, fans, power)
  power         Current power state
  inventory     Full hardware inventory
  logs          Recent system event log entries (last 10)
  thermal       Detailed temperature and fan status
  storage       Storage controllers and drives
  reset-types   Available power reset types
  help          Show this help

Config: ${CONFIG_FILE}
Credentials: ${CREDS_SOURCE} → ${CREDS_FILE}
EOF
    ;;
esac
