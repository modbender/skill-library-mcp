#!/bin/bash
# AI Labs Builder - CLI principale

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Colori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logo
echo -e "${BLUE}"
cat << "EOF"
    _    ___       _      _           _ _     _           
   /_\  |_ _|_ __ | | ___| |__   __ _| | | __| | ___ _ __ 
  / _ \  | || '_ \| |/ _ \ '_ \ / _\` | | |/ _\` |/ _ \ '__|
 /_/ \_\|___| .__/|_|\___/_.__/ \__,_|_|_|\__,_|\___|_|   
            |_|                                           
EOF
echo -e "${NC}"

# Funzioni di utilità
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Help
show_help() {
    cat << EOF
AI Labs Builder - Crea siti web, applicazioni AI, dashboard e workflows

USAGE:
    ailabs <command> [options]

COMMANDS:
    create website <name> --type <type>     Crea un sito web
    create ai-app <name> --type <type>      Crea un'app AI
    create dashboard <name> --type <type>   Crea una dashboard
    create workflow <name> --template <tpl> Crea un workflow
    deploy <project> --platform <platform>  Deploy del progetto
    integrate <project> --service <svc>     Integra servizi
    help                                    Mostra questo help

EXAMPLES:
    ailabs create website my-portfolio --type portfolio
    ailabs create ai-app my-chat --type chat
    ailabs create dashboard my-analytics --type analytics
    ailabs deploy my-portfolio --platform vercel
EOF
}

# Parse command
case "${1:-help}" in
    create)
        shift
        case "${1:-}" in
            website)
                shift
                "$SCRIPT_DIR/create-website.sh" "$@"
                ;;
            ai-app)
                shift
                "$SCRIPT_DIR/create-ai-app.sh" "$@"
                ;;
            dashboard)
                shift
                "$SCRIPT_DIR/create-dashboard.sh" "$@"
                ;;
            workflow)
                shift
                "$SCRIPT_DIR/create-workflow.sh" "$@"
                ;;
            *)
                log_error "Tipo di creazione non valido. Usa: website, ai-app, dashboard, workflow"
                exit 1
                ;;
        esac
        ;;
    deploy)
        shift
        "$SCRIPT_DIR/deploy.sh" "$@"
        ;;
    integrate)
        shift
        "$SCRIPT_DIR/integrate.sh" "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Comando non riconosciuto: $1"
        show_help
        exit 1
        ;;
esac
