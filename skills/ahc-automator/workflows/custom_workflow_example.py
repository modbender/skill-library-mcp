#!/usr/bin/env python3
"""
AHC-Automator: Exemplo de Workflow Customizado
Demonstra como criar novos workflows usando a infraestrutura AHC-Automator
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório do skill ao path
SKILL_DIR = Path(__file__).parent.parent
sys.path.append(str(SKILL_DIR))

from scripts.ahc_utils import AHCConfig, ClickUpClient, PipedriveClient, WhatsAppNotifier

class CustomWorkflowExample:
    """
    Exemplo de workflow customizado para AHC
    
    Este exemplo demonstra:
    1. Como usar as classes utilitárias
    2. Como estruturar um novo workflow
    3. Como integrar com ClickUp, Pipedrive e notificações
    4. Como implementar logging apropriado
    """
    
    def __init__(self, config_path=None):
        """Inicializar workflow customizado"""
        self.config = AHCConfig(config_path)
        self.clickup = ClickUpClient(self.config)
        self.pipedrive = PipedriveClient(self.config)
        self.whatsapp = WhatsAppNotifier(self.config)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging para este workflow"""
        log_dir = Path(self.config.get('logging', 'directory'))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / 'custom_workflow.log'
        
        logging.basicConfig(
            level=getattr(logging, self.config.get('logging', 'level')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def run_workflow(self, parameters):
        """
        Executar workflow customizado
        
        Args:
            parameters (dict): Parâmetros específicos do workflow
            
        Returns:
            dict: Resultado do workflow
        """
        try:
            self.logger.info(f"Iniciando workflow customizado com parâmetros: {parameters}")
            
            results = {
                "workflow": "custom_example",
                "started_at": datetime.now().isoformat(),
                "success": False,
                "steps": {}
            }
            
            # Passo 1: Validar parâmetros de entrada
            validation_result = self.validate_parameters(parameters)
            results["steps"]["validation"] = validation_result
            
            if not validation_result["success"]:
                return results
                
            # Passo 2: Executar lógica principal
            processing_result = self.process_main_logic(parameters)
            results["steps"]["processing"] = processing_result
            
            # Passo 3: Integrar com ClickUp (exemplo)
            clickup_result = self.integrate_with_clickup(parameters, processing_result)
            results["steps"]["clickup_integration"] = clickup_result
            
            # Passo 4: Integrar com Pipedrive (exemplo)
            pipedrive_result = self.integrate_with_pipedrive(parameters, processing_result)
            results["steps"]["pipedrive_integration"] = pipedrive_result
            
            # Passo 5: Enviar notificações
            notification_result = self.send_notifications(parameters, processing_result)
            results["steps"]["notifications"] = notification_result
            
            # Determinar sucesso geral
            results["success"] = all(
                step.get("success", False) for step in results["steps"].values()
            )
            
            results["completed_at"] = datetime.now().isoformat()
            
            self.logger.info(f"Workflow concluído com sucesso: {results['success']}")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro no workflow customizado: {e}")
            return {
                "workflow": "custom_example",
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
    def validate_parameters(self, parameters):
        """Validar parâmetros de entrada"""
        try:
            required_params = ['client_name', 'project_type']
            
            for param in required_params:
                if param not in parameters:
                    return {
                        "success": False,
                        "error": f"Parâmetro obrigatório faltando: {param}"
                    }
                    
            # Validações específicas
            if not parameters['client_name'].strip():
                return {
                    "success": False,
                    "error": "Nome do cliente não pode estar vazio"
                }
                
            allowed_project_types = ['manufacturing', 'aerospace', 'custom', 'maintenance']
            if parameters['project_type'] not in allowed_project_types:
                return {
                    "success": False,
                    "error": f"Tipo de projeto inválido. Permitidos: {allowed_project_types}"
                }
                
            return {
                "success": True,
                "validated_params": parameters
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na validação: {str(e)}"
            }
            
    def process_main_logic(self, parameters):
        """Executar lógica principal do workflow"""
        try:
            # Exemplo de lógica de processamento
            client_name = parameters['client_name']
            project_type = parameters['project_type']
            
            # Simular processamento baseado no tipo de projeto
            processing_data = {
                "client_name": client_name,
                "project_type": project_type,
                "estimated_duration": self.estimate_project_duration(project_type),
                "required_materials": self.get_required_materials(project_type),
                "team_assignment": self.assign_team(project_type),
                "priority_level": self.determine_priority(parameters)
            }
            
            self.logger.info(f"Dados processados para {client_name}: {processing_data}")
            
            return {
                "success": True,
                "processing_data": processing_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro no processamento: {str(e)}"
            }
            
    def estimate_project_duration(self, project_type):
        """Estimar duração do projeto baseado no tipo"""
        durations = {
            'manufacturing': '2-3 semanas',
            'aerospace': '4-6 semanas',
            'custom': '3-5 semanas',
            'maintenance': '1-2 semanas'
        }
        return durations.get(project_type, '2-4 semanas')
        
    def get_required_materials(self, project_type):
        """Obter materiais necessários baseado no tipo"""
        materials = {
            'manufacturing': ['Carbon Fiber', 'Epoxy Resin', 'Core Material'],
            'aerospace': ['Aerospace Grade Carbon', 'Certified Resin', 'Honeycomb Core'],
            'custom': ['Various Composites', 'Specialty Resins', 'Custom Core'],
            'maintenance': ['Repair Kit', 'Matching Materials', 'Adhesives']
        }
        return materials.get(project_type, ['Standard Materials'])
        
    def assign_team(self, project_type):
        """Atribuir equipe baseado no tipo de projeto"""
        teams = {
            'manufacturing': ['Production Team', 'Quality Control'],
            'aerospace': ['Aerospace Engineers', 'Certified Technicians', 'Quality Aerospace'],
            'custom': ['R&D Team', 'Custom Engineering', 'Prototyping'],
            'maintenance': ['Maintenance Team', 'Field Engineers']
        }
        return teams.get(project_type, ['Standard Team'])
        
    def determine_priority(self, parameters):
        """Determinar prioridade do projeto"""
        # Exemplo de lógica de prioridade
        if parameters.get('urgent', False):
            return 'High'
        elif parameters['project_type'] == 'aerospace':
            return 'High'
        elif parameters.get('value', 0) > 100000:
            return 'High'
        else:
            return 'Medium'
            
    def integrate_with_clickup(self, parameters, processing_result):
        """Integrar com ClickUp"""
        try:
            processing_data = processing_result['processing_data']
            
            # Criar task principal no ClickUp
            task_name = f"[{processing_data['project_type'].upper()}] {processing_data['client_name']}"
            task_description = f"""
Projeto customizado iniciado via workflow automático

**Cliente:** {processing_data['client_name']}
**Tipo:** {processing_data['project_type']}
**Duração Estimada:** {processing_data['estimated_duration']}
**Prioridade:** {processing_data['priority_level']}

**Equipe Atribuída:**
{chr(10).join([f"- {member}" for member in processing_data['team_assignment']])}

**Materiais Necessários:**
{chr(10).join([f"- {material}" for material in processing_data['required_materials']])}

**Criado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            # Determinar prioridade numérica para ClickUp
            priority_map = {'Low': 1, 'Medium': 2, 'High': 3, 'Urgent': 4}
            clickup_priority = priority_map.get(processing_data['priority_level'], 2)
            
            task_result = self.clickup.create_task(
                list_id=self.config.get('clickup', 'templates', 'standard'),
                name=task_name,
                description=task_description,
                priority=clickup_priority
            )
            
            if task_result.get('success'):
                self.logger.info(f"Task ClickUp criada: {task_result['data']['id']}")
                return {
                    "success": True,
                    "task_id": task_result['data']['id'],
                    "task_url": task_result['data'].get('url')
                }
            else:
                self.logger.error(f"Erro ao criar task ClickUp: {task_result}")
                return {
                    "success": False,
                    "error": task_result.get('error', 'Erro desconhecido')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na integração ClickUp: {str(e)}"
            }
            
    def integrate_with_pipedrive(self, parameters, processing_result):
        """Integrar com Pipedrive"""
        try:
            processing_data = processing_result['processing_data']
            
            # Criar pessoa (cliente) se não existir
            person_result = self.pipedrive.create_or_find_person(
                name=processing_data['client_name'],
                email=parameters.get('client_email')
            )
            
            person_id = None
            if person_result.get('success'):
                person_id = person_result['data']['id']
                
            # Criar deal no Pipedrive
            deal_title = f"{processing_data['project_type'].title()} Project - {processing_data['client_name']}"
            deal_value = parameters.get('project_value')
            
            deal_result = self.pipedrive.create_deal(
                title=deal_title,
                value=deal_value,
                currency=parameters.get('currency', 'EUR'),
                person_id=person_id
            )
            
            if deal_result.get('success'):
                self.logger.info(f"Deal Pipedrive criado: {deal_result['data']['id']}")
                return {
                    "success": True,
                    "deal_id": deal_result['data']['id'],
                    "person_id": person_id
                }
            else:
                return {
                    "success": False,
                    "error": deal_result.get('error', 'Erro ao criar deal')
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na integração Pipedrive: {str(e)}"
            }
            
    def send_notifications(self, parameters, processing_result):
        """Enviar notificações"""
        try:
            processing_data = processing_result['processing_data']
            
            # Preparar mensagem de notificação
            notification_message = f"""
🚀 Novo projeto iniciado automaticamente!

**Cliente:** {processing_data['client_name']}
**Tipo:** {processing_data['project_type'].title()}
**Prioridade:** {processing_data['priority_level']}
**Duração:** {processing_data['estimated_duration']}
**Equipe:** {', '.join(processing_data['team_assignment'][:2])}

Via workflow customizado em {datetime.now().strftime('%H:%M')}
"""
            
            # Enviar notificação
            notification_result = self.whatsapp.send_custom_notification(
                notification_message,
                urgent=(processing_data['priority_level'] in ['High', 'Urgent'])
            )
            
            return notification_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao enviar notificações: {str(e)}"
            }

def main():
    """Função principal para demonstração"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Exemplo de Workflow Customizado AHC')
    parser.add_argument('--client', required=True, help='Nome do cliente')
    parser.add_argument('--type', required=True, 
                       choices=['manufacturing', 'aerospace', 'custom', 'maintenance'],
                       help='Tipo de projeto')
    parser.add_argument('--email', help='Email do cliente')
    parser.add_argument('--value', type=float, help='Valor do projeto')
    parser.add_argument('--currency', default='EUR', help='Moeda')
    parser.add_argument('--urgent', action='store_true', help='Marcar como urgente')
    parser.add_argument('--debug', action='store_true', help='Ativar modo debug')
    parser.add_argument('--config', help='Caminho para arquivo de configuração personalizado')
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        os.environ['AHC_DEBUG'] = 'true'
        
    try:
        # Preparar parâmetros
        parameters = {
            'client_name': args.client,
            'project_type': args.type,
            'client_email': args.email,
            'project_value': args.value,
            'currency': args.currency,
            'urgent': args.urgent
        }
        
        # Executar workflow
        workflow = CustomWorkflowExample(args.config)
        result = workflow.run_workflow(parameters)
        
        # Exibir resultado
        if result['success']:
            print("✅ Workflow customizado executado com sucesso!")
            print(json.dumps(result, indent=2, default=str))
        else:
            print("❌ Erro na execução do workflow:")
            print(json.dumps(result, indent=2, default=str))
            sys.exit(1)
            
    except Exception as e:
        print(f"ERRO: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()