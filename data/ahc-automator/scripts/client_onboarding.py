#!/usr/bin/env python3
"""
AHC-Automator: Client Onboarding Workflow
Automatiza processo de onboarding de novos clientes com criação de projetos ClickUp estruturados
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

class ClientOnboardingProcessor:
    """Processador de onboarding de clientes AHC"""
    
    def __init__(self, config_path=None):
        self.config = AHCConfig(config_path)
        self.clickup = ClickUpClient(self.config)
        self.pipedrive = PipedriveClient(self.config) 
        self.whatsapp = WhatsAppNotifier(self.config)
        
        # Setup logging
        self.setup_logging()
        
        # Templates de projeto
        self.project_templates = self.load_project_templates()
        
    def setup_logging(self):
        """Configurar logging"""
        log_dir = Path(self.config.get('logging', 'directory'))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / 'client_onboarding.log'
        
        logging.basicConfig(
            level=getattr(logging, self.config.get('logging', 'level')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_project_templates(self):
        """Carregar templates de projeto"""
        return {
            'standard': {
                'name': 'Composite Manufacturing Project',
                'folders': [
                    {
                        'name': '01 - Design & Engineering',
                        'tasks': [
                            'Initial requirements gathering',
                            'Technical specifications review', 
                            'Design approval',
                            'Engineering drawings finalization'
                        ]
                    },
                    {
                        'name': '02 - Material Planning',
                        'tasks': [
                            'Material cost estimation',
                            'Supplier quotes',
                            'Material ordering',
                            'Inventory verification'
                        ]
                    },
                    {
                        'name': '03 - Manufacturing',
                        'tasks': [
                            'Production planning',
                            'Quality control setup',
                            'Manufacturing execution',
                            'Progress monitoring'
                        ]
                    },
                    {
                        'name': '04 - Quality & Testing',
                        'tasks': [
                            'Quality testing protocols',
                            'Final inspection',
                            'Test results documentation',
                            'Quality certification'
                        ]
                    },
                    {
                        'name': '05 - Delivery & Closure',
                        'tasks': [
                            'Delivery coordination',
                            'Client handover',
                            'Project closure documentation',
                            'Post-delivery support setup'
                        ]
                    }
                ]
            },
            'aerospace': {
                'name': 'Aerospace Grade Composite Project',
                'folders': [
                    {
                        'name': '01 - Design & Engineering',
                        'tasks': [
                            'Aerospace requirements analysis',
                            'Regulatory compliance review',
                            'Advanced CAD modeling',
                            'Stress analysis simulation',
                            'Design validation'
                        ]
                    },
                    {
                        'name': '02 - Material Planning',
                        'tasks': [
                            'Aerospace-grade material selection',
                            'Certified supplier verification',
                            'Material traceability setup',
                            'Cost analysis and approval'
                        ]
                    },
                    {
                        'name': '03 - Manufacturing',
                        'tasks': [
                            'Clean room preparation',
                            'Advanced manufacturing setup',
                            'Process control implementation',
                            'Continuous monitoring'
                        ]
                    },
                    {
                        'name': '04 - Quality & Testing',
                        'tasks': [
                            'Aerospace testing protocols',
                            'Non-destructive testing',
                            'Material certification',
                            'Regulatory compliance verification',
                            'Final aerospace certification'
                        ]
                    },
                    {
                        'name': '05 - Delivery & Closure',
                        'tasks': [
                            'Aerospace packaging standards',
                            'Delivery coordination',
                            'Complete documentation handover',
                            'Long-term support agreement'
                        ]
                    }
                ]
            },
            'custom': {
                'name': 'Custom Engineering Project',
                'folders': [
                    {
                        'name': '01 - Custom Design',
                        'tasks': [
                            'Custom requirements analysis',
                            'Feasibility study',
                            'Prototype development',
                            'Design iteration and approval'
                        ]
                    },
                    {
                        'name': '02 - Engineering & Planning',
                        'tasks': [
                            'Custom engineering solutions',
                            'Specialized material selection',
                            'Manufacturing process design',
                            'Cost estimation'
                        ]
                    },
                    {
                        'name': '03 - Implementation',
                        'tasks': [
                            'Custom tooling preparation',
                            'Specialized manufacturing',
                            'Quality control adaptation',
                            'Progress tracking'
                        ]
                    },
                    {
                        'name': '04 - Validation & Testing',
                        'tasks': [
                            'Custom testing protocols',
                            'Performance validation',
                            'Client-specific requirements verification',
                            'Final approval'
                        ]
                    },
                    {
                        'name': '05 - Delivery & Support',
                        'tasks': [
                            'Custom delivery requirements',
                            'Specialized training if needed',
                            'Documentation package',
                            'Ongoing support setup'
                        ]
                    }
                ]
            }
        }
        
    def onboard_client(self, client_name, client_email=None, template='standard', 
                      project_value=None, currency='EUR', notes=None, quick=False):
        """Executar processo completo de onboarding"""
        try:
            self.logger.info(f"Iniciando onboarding do cliente: {client_name}")
            
            results = {}
            
            # 1. Criar pessoa no Pipedrive (se não existir)
            if not quick:
                person_result = self.create_pipedrive_person(client_name, client_email)
                results['pipedrive_person'] = person_result
                
                # 2. Criar deal no Pipedrive
                if person_result.get('success'):
                    person_id = person_result['data']['id']
                    deal_result = self.create_pipedrive_deal(
                        client_name, project_value, currency, person_id
                    )
                    results['pipedrive_deal'] = deal_result
                    
            # 3. Criar projeto ClickUp estruturado
            project_result = self.create_clickup_project(client_name, template, notes)
            results['clickup_project'] = project_result
            
            # 4. Enviar notificações
            if project_result.get('success'):
                self.send_onboarding_notifications(client_name, project_result)
                
            # 5. Gerar email de boas-vindas (placeholder)
            if client_email and not quick:
                welcome_result = self.send_welcome_email(client_name, client_email)
                results['welcome_email'] = welcome_result
                
            self.logger.info(f"Onboarding concluído para {client_name}")
            return {"success": True, "results": results}
            
        except Exception as e:
            self.logger.error(f"Erro no onboarding de {client_name}: {e}")
            return {"success": False, "error": str(e)}
            
    def create_pipedrive_person(self, name, email):
        """Criar pessoa no Pipedrive"""
        try:
            return self.pipedrive.create_or_find_person(name, email)
        except Exception as e:
            self.logger.error(f"Erro ao criar pessoa no Pipedrive: {e}")
            return {"success": False, "error": str(e)}
            
    def create_pipedrive_deal(self, client_name, value, currency, person_id):
        """Criar deal no Pipedrive"""
        try:
            deal_title = f"Projeto Composites - {client_name}"
            return self.pipedrive.create_deal(
                title=deal_title,
                value=value,
                currency=currency,
                person_id=person_id
            )
        except Exception as e:
            self.logger.error(f"Erro ao criar deal no Pipedrive: {e}")
            return {"success": False, "error": str(e)}
            
    def create_clickup_project(self, client_name, template, notes):
        """Criar projeto estruturado no ClickUp"""
        try:
            template_data = self.project_templates.get(template, self.project_templates['standard'])
            project_name = f"[{client_name}] - {template_data['name']}"
            
            self.logger.info(f"Criando projeto ClickUp: {project_name}")
            
            # Por enquanto, usar lista existente como exemplo
            # Em implementação completa, criaria Space/Folder estruturado
            list_id = self.config.get('clickup', 'templates', 'standard')
            
            # Criar task principal do projeto
            main_task_result = self.clickup.create_task(
                list_id=list_id,
                name=project_name,
                description=f"Projeto para cliente {client_name}\nTemplate: {template}\n\nNotas: {notes or 'Nenhuma nota adicional'}"
            )
            
            if not main_task_result.get('success'):
                return main_task_result
                
            # Criar subtasks para cada fase
            subtasks = []
            for folder in template_data['folders']:
                folder_task = self.clickup.create_task(
                    list_id=list_id,
                    name=f"{project_name} - {folder['name']}",
                    description=f"Fase: {folder['name']}\n\nTasks incluídas:\n" + 
                               '\n'.join([f"- {task}" for task in folder['tasks']])
                )
                subtasks.append(folder_task)
                
            return {
                "success": True,
                "data": {
                    "main_task": main_task_result['data'],
                    "subtasks": subtasks,
                    "template_used": template
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao criar projeto ClickUp: {e}")
            return {"success": False, "error": str(e)}
            
    def send_welcome_email(self, client_name, client_email):
        """Enviar email de boas-vindas (placeholder)"""
        try:
            # Placeholder para integração de email
            self.logger.info(f"Enviando email de boas-vindas para {client_name} ({client_email})")
            
            # TODO: Implementar envio real de email
            welcome_message = f"""
            Olá {client_name},

            Bem-vindo à Alan Harper Composites!

            Seu projeto foi criado e nossa equipe está pronta para começar.
            Você receberá atualizações regulares sobre o progresso.

            Em caso de dúvidas, entre em contato conosco.

            Atenciosamente,
            Equipe Alan Harper Composites
            """
            
            return {"success": True, "message": "Email de boas-vindas preparado"}
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar email de boas-vindas: {e}")
            return {"success": False, "error": str(e)}
            
    def send_onboarding_notifications(self, client_name, project_result):
        """Enviar notificações de onboarding"""
        try:
            message = self.config.get('whatsapp', 'message_templates', 'client_onboarded').format(
                client_name=client_name
            )
            
            project_url = project_result['data']['main_task'].get('url', '')
            self.whatsapp.send_notification(message, project_url)
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificações: {e}")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AHC Client Onboarding Processor')
    parser.add_argument('--client', required=True, help='Nome do cliente')
    parser.add_argument('--email', help='Email do cliente')
    parser.add_argument('--template', choices=['standard', 'aerospace', 'custom'], 
                       default='standard', help='Template de projeto')
    parser.add_argument('--value', type=float, help='Valor do projeto')
    parser.add_argument('--currency', default='EUR', help='Moeda do projeto')
    parser.add_argument('--notes', help='Notas adicionais')
    parser.add_argument('--quick', action='store_true', help='Onboarding rápido (apenas ClickUp)')
    parser.add_argument('--debug', action='store_true', help='Ativar modo debug')
    parser.add_argument('--config', help='Caminho para arquivo de configuração personalizado')
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        os.environ['AHC_DEBUG'] = 'true'
        
    try:
        processor = ClientOnboardingProcessor(args.config)
        
        result = processor.onboard_client(
            client_name=args.client,
            client_email=args.email,
            template=args.template,
            project_value=args.value,
            currency=args.currency,
            notes=args.notes,
            quick=args.quick
        )
        
        if result['success']:
            print(f"✅ Onboarding concluído com sucesso para {args.client}")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Erro no onboarding: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"ERRO: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()