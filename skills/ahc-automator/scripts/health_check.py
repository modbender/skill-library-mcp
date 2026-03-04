#!/usr/bin/env python3
"""
AHC-Automator: Health Check
Sistema de monitoramento e diagnóstico para workflows AHC
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório do skill ao path
SKILL_DIR = Path(__file__).parent.parent
sys.path.append(str(SKILL_DIR))

from scripts.ahc_utils import AHCConfig, ClickUpClient, PipedriveClient

class AHCHealthChecker:
    """Health checker para workflows AHC"""
    
    def __init__(self, config_path=None):
        self.config = AHCConfig(config_path)
        
        # Initialize clients
        try:
            self.clickup = ClickUpClient(self.config)
        except Exception as e:
            self.clickup = None
            self.clickup_error = str(e)
            
        try:
            self.pipedrive = PipedriveClient(self.config)
        except Exception as e:
            self.pipedrive = None
            self.pipedrive_error = str(e)
            
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging"""
        log_dir = Path(self.config.get('logging', 'directory'))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / 'health_check.log'
        
        logging.basicConfig(
            level=getattr(logging, self.config.get('logging', 'level')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def run_full_health_check(self):
        """Executar verificação completa de saúde"""
        try:
            self.logger.info("Iniciando health check completo")
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "unknown",
                "checks": {}
            }
            
            # 1. Verificar configuração
            config_check = self.check_configuration()
            results["checks"]["configuration"] = config_check
            
            # 2. Verificar conectividade APIs
            api_check = self.check_api_connectivity()
            results["checks"]["api_connectivity"] = api_check
            
            # 3. Verificar cron jobs
            cron_check = self.check_cron_jobs()
            results["checks"]["cron_jobs"] = cron_check
            
            # 4. Verificar logs
            logs_check = self.check_logs()
            results["checks"]["logs"] = logs_check
            
            # 5. Verificar espaço em disco
            disk_check = self.check_disk_space()
            results["checks"]["disk_space"] = disk_check
            
            # 6. Verificar workflows específicos
            workflow_check = self.check_workflows()
            results["checks"]["workflows"] = workflow_check
            
            # Determinar status geral
            results["overall_status"] = self.determine_overall_status(results["checks"])
            
            self.logger.info(f"Health check concluído com status: {results['overall_status']}")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro no health check: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
            
    def check_configuration(self):
        """Verificar configuração do sistema"""
        try:
            check = {
                "status": "ok",
                "details": {},
                "errors": []
            }
            
            # Verificar arquivo de configuração
            if not self.config.config_path.exists():
                check["errors"].append("Arquivo de configuração não encontrado")
                check["status"] = "error"
            else:
                check["details"]["config_file"] = str(self.config.config_path)
                
            # Verificar seções obrigatórias
            required_sections = ["clickup", "pipedrive", "email", "whatsapp"]
            for section in required_sections:
                if not self.config.get(section):
                    check["errors"].append(f"Seção '{section}' não encontrada na configuração")
                    check["status"] = "error"
                    
            # Verificar variáveis de ambiente
            env_vars = ["CLICKUP_API_TOKEN", "PIPEDRIVE_API_TOKEN"]
            for var in env_vars:
                if not os.environ.get(var):
                    check["errors"].append(f"Variável de ambiente '{var}' não definida")
                    if check["status"] == "ok":
                        check["status"] = "warning"
                        
            return check
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def check_api_connectivity(self):
        """Verificar conectividade com APIs"""
        try:
            check = {
                "status": "ok",
                "details": {},
                "errors": []
            }
            
            # Testar ClickUp
            if self.clickup:
                try:
                    team_result = self.clickup._request('GET', f'team/{self.config.get("clickup", "team_id")}')
                    if team_result.get('success'):
                        check["details"]["clickup"] = "conectado"
                    else:
                        check["errors"].append(f"Erro ClickUp: {team_result.get('error', 'Erro desconhecido')}")
                        check["status"] = "error"
                except Exception as e:
                    check["errors"].append(f"Erro ao conectar ClickUp: {e}")
                    check["status"] = "error"
            else:
                check["errors"].append(f"ClickUp não inicializado: {getattr(self, 'clickup_error', 'Erro desconhecido')}")
                check["status"] = "error"
                
            # Testar Pipedrive
            if self.pipedrive:
                try:
                    deals_result = self.pipedrive._request('GET', 'deals?limit=1')
                    if deals_result.get('success'):
                        check["details"]["pipedrive"] = "conectado"
                    else:
                        check["errors"].append(f"Erro Pipedrive: {deals_result.get('error', 'Erro desconhecido')}")
                        check["status"] = "error"
                except Exception as e:
                    check["errors"].append(f"Erro ao conectar Pipedrive: {e}")
                    check["status"] = "error"
            else:
                check["errors"].append(f"Pipedrive não inicializado: {getattr(self, 'pipedrive_error', 'Erro desconhecido')}")
                check["status"] = "error"
                
            return check
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def check_cron_jobs(self):
        """Verificar status dos cron jobs"""
        try:
            check = {
                "status": "ok",
                "details": {},
                "errors": []
            }
            
            # Obter lista de cron jobs
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            
            if result.returncode == 0:
                cron_content = result.stdout
                
                # Verificar cron jobs específicos pelos IDs
                cron_jobs = self.config.get('email', 'cron_jobs', default={})
                
                for job_name, job_id in cron_jobs.items():
                    if job_id in cron_content:
                        check["details"][job_name] = "ativo"
                    else:
                        check["errors"].append(f"Cron job '{job_name}' não encontrado")
                        if check["status"] == "ok":
                            check["status"] = "warning"
                            
            else:
                check["errors"].append("Não foi possível acessar crontab")
                check["status"] = "error"
                
            return check
            
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }
            
    def check_logs(self):
        """Verificar logs do sistema"""
        try:
            check = {
                "status": "ok",
                "details": {},
                "errors": []
            }
            
            log_dir = Path(self.config.get('logging', 'directory'))
            
            if not log_dir.exists():
                check["errors"].append("Diretório de logs não existe")
                check["status"] = "error"
                return check
                
            # Verificar logs recentes (últimas 24h)
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            log_files = ['email_processing.log', 'client_onboarding.log', 'project_completion.log', 'notifications.log']
            
            for log_file in log_files:
                log_path = log_dir / log_file
                if log_path.exists():
                    mod_time = datetime.fromtimestamp(log_path.stat().st_mtime)
                    if mod_time > cutoff_time:
                        check["details"][log_file] = "ativo"
                    else:
                        check["details"][log_file] = "inativo"
                        if check["status"] == "ok":
                            check["status"] = "warning"
                else:
                    check["details"][log_file] = "não existe"
                    
            # Verificar por erros nos logs
            error_count = self.count_recent_errors(log_dir)
            check["details"]["recent_errors"] = error_count
            
            if error_count > 10:
                check["status"] = "error"
                check["errors"].append(f"Muitos erros recentes: {error_count}")
            elif error_count > 5:
                if check["status"] == "ok":
                    check["status"] = "warning"
                    
            return check
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def count_recent_errors(self, log_dir):
        """Contar erros recentes nos logs"""
        try:
            error_count = 0
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            for log_file in log_dir.glob('*.log'):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if 'ERROR' in line:
                                error_count += 1
                except:
                    continue
                    
            return error_count
            
        except Exception:
            return 0
            
    def check_disk_space(self):
        """Verificar espaço em disco"""
        try:
            check = {
                "status": "ok",
                "details": {},
                "errors": []
            }
            
            # Verificar espaço no diretório de trabalho
            workspace_path = Path(self.config.config_path).parent.parent.parent
            
            result = subprocess.run(['df', '-h', str(workspace_path)], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    parts = lines[1].split()
                    if len(parts) >= 4:
                        used_percent = parts[4].rstrip('%')
                        try:
                            used_percent = int(used_percent)
                            check["details"]["disk_usage"] = f"{used_percent}%"
                            
                            if used_percent > 90:
                                check["status"] = "error"
                                check["errors"].append(f"Espaço em disco crítico: {used_percent}%")
                            elif used_percent > 80:
                                check["status"] = "warning"
                                check["errors"].append(f"Espaço em disco alto: {used_percent}%")
                        except ValueError:
                            check["details"]["disk_usage"] = "não pôde ser determinado"
                            
            return check
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def check_workflows(self):
        """Verificar workflows específicos"""
        try:
            check = {
                "status": "ok",
                "details": {},
                "errors": []
            }
            
            workflows = self.config.get('workflows', default={})
            
            for workflow_name, workflow_config in workflows.items():
                workflow_check = {
                    "enabled": workflow_config.get('enabled', False),
                    "last_run": "desconhecido"
                }
                
                # Verificar se workflow está habilitado
                if not workflow_config.get('enabled'):
                    workflow_check["status"] = "disabled"
                else:
                    workflow_check["status"] = "enabled"
                    
                check["details"][workflow_name] = workflow_check
                
            return check
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
            
    def determine_overall_status(self, checks):
        """Determinar status geral baseado nos checks individuais"""
        error_count = 0
        warning_count = 0
        
        for check_name, check_result in checks.items():
            status = check_result.get("status", "unknown")
            if status == "error":
                error_count += 1
            elif status == "warning":
                warning_count += 1
                
        if error_count > 0:
            return "error"
        elif warning_count > 0:
            return "warning"
        else:
            return "ok"

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AHC Health Checker')
    parser.add_argument('--workflow', help='Verificar workflow específico')
    parser.add_argument('--json', action='store_true', help='Saída em formato JSON')
    parser.add_argument('--verbose', action='store_true', help='Saída detalhada')
    parser.add_argument('--config', help='Caminho para arquivo de configuração personalizado')
    
    args = parser.parse_args()
    
    try:
        checker = AHCHealthChecker(args.config)
        
        if args.workflow:
            # Check específico (implementar se necessário)
            print(f"Check específico para workflow '{args.workflow}' não implementado ainda")
            sys.exit(1)
        else:
            # Check completo
            results = checker.run_full_health_check()
            
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            # Formato legível
            print(f"\n🔍 AHC-Automator Health Check")
            print(f"📅 Timestamp: {results['timestamp']}")
            print(f"📊 Status Geral: {results['overall_status'].upper()}")
            
            if results['overall_status'] == 'ok':
                print("✅ Todos os sistemas operando normalmente")
            elif results['overall_status'] == 'warning':
                print("⚠️  Alguns avisos detectados")
            else:
                print("❌ Problemas críticos detectados")
                
            if args.verbose and 'checks' in results:
                print(f"\n📋 Detalhes dos Checks:")
                for check_name, check_result in results['checks'].items():
                    status_icon = "✅" if check_result['status'] == 'ok' else "⚠️" if check_result['status'] == 'warning' else "❌"
                    print(f"  {status_icon} {check_name}: {check_result['status']}")
                    
                    if 'errors' in check_result and check_result['errors']:
                        for error in check_result['errors']:
                            print(f"    • {error}")
                            
        # Exit code baseado no status
        if results['overall_status'] == 'error':
            sys.exit(2)
        elif results['overall_status'] == 'warning':
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"ERRO: {e}")
        sys.exit(3)

if __name__ == '__main__':
    main()