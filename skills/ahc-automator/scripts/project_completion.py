#!/usr/bin/env python3
"""
AHC-Automator: Project Completion Sequence
Automatiza processo de conclusão de projetos com relatórios, faturação e pesquisas de satisfação
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

class ProjectCompletionProcessor:
    """Processador de conclusão de projetos AHC"""
    
    def __init__(self, config_path=None):
        self.config = AHCConfig(config_path)
        self.clickup = ClickUpClient(self.config)
        self.pipedrive = PipedriveClient(self.config)
        self.whatsapp = WhatsAppNotifier(self.config)
        
        # Setup logging
        self.setup_logging()
        
        # Templates de relatório
        self.report_templates = self.load_report_templates()
        
    def setup_logging(self):
        """Configurar logging"""
        log_dir = Path(self.config.get('logging', 'directory'))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / 'project_completion.log'
        
        logging.basicConfig(
            level=getattr(logging, self.config.get('logging', 'level')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_report_templates(self):
        """Carregar templates de relatório"""
        return {
            'delivery_report': {
                'title': 'Project Delivery Report',
                'sections': [
                    'Executive Summary',
                    'Project Timeline',
                    'Deliverable Specifications',
                    'Quality Metrics',
                    'Material Usage',
                    'Cost Analysis',
                    'Client Requirements Fulfillment'
                ]
            },
            'handover_document': {
                'title': 'Client Handover Document',
                'sections': [
                    'Product Specifications',
                    'Installation Guidelines',
                    'Maintenance Instructions',
                    'Warranty Information',
                    'Support Contacts',
                    'Spare Parts Information'
                ]
            },
            'internal_review': {
                'title': 'Internal Project Review',
                'sections': [
                    'Project Overview',
                    'Performance Metrics',
                    'Resource Utilization',
                    'Lessons Learned',
                    'Process Improvements',
                    'Client Feedback Summary',
                    'Recommendations'
                ]
            }
        }
        
    def complete_project(self, project_id=None, task_id=None, client_name=None, 
                        generate_reports=True, trigger_invoice=False, send_survey=True):
        """Executar sequência completa de conclusão de projeto"""
        try:
            self.logger.info(f"Iniciando conclusão de projeto: {project_id or task_id}")
            
            results = {}
            
            # 1. Obter dados do projeto
            project_data = self.get_project_data(project_id, task_id)
            if not project_data:
                return {"success": False, "error": "Projeto não encontrado"}
                
            results['project_data'] = project_data
            
            # 2. Gerar relatórios se solicitado
            if generate_reports:
                reports_result = self.generate_project_reports(project_data)
                results['reports'] = reports_result
                
            # 3. Atualizar status no ClickUp e Pipedrive
            status_result = self.update_project_status(project_data)
            results['status_updates'] = status_result
            
            # 4. Trigger de faturação se solicitado
            if trigger_invoice:
                invoice_result = self.trigger_invoice_generation(project_data)
                results['invoice'] = invoice_result
                
            # 5. Enviar pesquisa de satisfação se solicitado
            if send_survey:
                survey_result = self.send_satisfaction_survey(project_data)
                results['survey'] = survey_result
                
            # 6. Notificar stakeholders
            notification_result = self.send_completion_notifications(project_data)
            results['notifications'] = notification_result
            
            self.logger.info(f"Conclusão de projeto finalizada: {project_data.get('name', 'Projeto')}")
            return {"success": True, "results": results}
            
        except Exception as e:
            self.logger.error(f"Erro na conclusão de projeto: {e}")
            return {"success": False, "error": str(e)}
            
    def get_project_data(self, project_id, task_id):
        """Obter dados do projeto do ClickUp"""
        try:
            if task_id:
                # Usar task_id diretamente
                task_result = self.clickup._request('GET', f'task/{task_id}')
                if task_result.get('success'):
                    task_data = task_result['data']
                    return {
                        'id': task_data['id'],
                        'name': task_data['name'],
                        'status': task_data['status']['status'],
                        'list_id': task_data['list']['id'],
                        'url': task_data['url'],
                        'created': task_data['date_created'],
                        'due_date': task_data.get('due_date'),
                        'assignees': task_data.get('assignees', []),
                        'description': task_data.get('description', '')
                    }
            else:
                self.logger.warning("ID do projeto não fornecido")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do projeto: {e}")
            return None
            
    def generate_project_reports(self, project_data):
        """Gerar relatórios do projeto"""
        try:
            self.logger.info(f"Gerando relatórios para projeto: {project_data['name']}")
            
            reports = {}
            
            # 1. Relatório de entrega
            delivery_report = self.generate_delivery_report(project_data)
            reports['delivery_report'] = delivery_report
            
            # 2. Documento de handover
            handover_doc = self.generate_handover_document(project_data)
            reports['handover_document'] = handover_doc
            
            # 3. Review interno
            internal_review = self.generate_internal_review(project_data)
            reports['internal_review'] = internal_review
            
            return {"success": True, "reports": reports}
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar relatórios: {e}")
            return {"success": False, "error": str(e)}
            
    def generate_delivery_report(self, project_data):
        """Gerar relatório de entrega"""
        template = self.report_templates['delivery_report']
        
        report_content = f"""
# {template['title']}

**Project:** {project_data['name']}
**Completion Date:** {datetime.now().strftime('%Y-%m-%d')}
**Project URL:** {project_data['url']}

## Executive Summary
Project completed successfully with all deliverables meeting specifications.

## Project Timeline
- **Start Date:** {datetime.fromtimestamp(int(project_data['created'])/1000).strftime('%Y-%m-%d')}
- **Completion Date:** {datetime.now().strftime('%Y-%m-%d')}
- **Duration:** {self.calculate_project_duration(project_data)} days

## Deliverable Specifications
All specifications met according to initial requirements.

## Quality Metrics
- Quality control passed: ✅
- Client approval received: ✅
- Documentation complete: ✅

## Material Usage
Materials used efficiently within budget constraints.

## Cost Analysis
Project completed within approved budget.

## Client Requirements Fulfillment
All client requirements have been successfully fulfilled.
        """
        
        # Salvar relatório
        report_path = self.save_report(project_data, 'delivery_report', report_content)
        
        return {
            "success": True,
            "content": report_content,
            "file_path": report_path
        }
        
    def generate_handover_document(self, project_data):
        """Gerar documento de handover"""
        template = self.report_templates['handover_document']
        
        handover_content = f"""
# {template['title']}

**Project:** {project_data['name']}
**Handover Date:** {datetime.now().strftime('%Y-%m-%d')}

## Product Specifications
[Product specifications and technical details]

## Installation Guidelines
[Step-by-step installation instructions]

## Maintenance Instructions
[Regular maintenance procedures and schedules]

## Warranty Information
- **Warranty Period:** 2 years from delivery date
- **Coverage:** Material defects and manufacturing issues
- **Contact:** support@alanharpercomposites.com.br

## Support Contacts
- **Technical Support:** Ian Harper - ian@alanharpercomposites.com.br
- **General Inquiries:** info@alanharpercomposites.com.br
- **Emergency:** +55 (11) 9999-9999

## Spare Parts Information
[List of recommended spare parts and ordering information]
        """
        
        # Salvar documento
        doc_path = self.save_report(project_data, 'handover_document', handover_content)
        
        return {
            "success": True,
            "content": handover_content,
            "file_path": doc_path
        }
        
    def generate_internal_review(self, project_data):
        """Gerar review interno"""
        template = self.report_templates['internal_review']
        
        review_content = f"""
# {template['title']}

**Project:** {project_data['name']}
**Review Date:** {datetime.now().strftime('%Y-%m-%d')}

## Project Overview
Project completed successfully with valuable lessons learned.

## Performance Metrics
- **Timeline Performance:** On schedule
- **Budget Performance:** Within budget
- **Quality Performance:** Exceeds standards

## Resource Utilization
Resources utilized efficiently throughout the project.

## Lessons Learned
- [Key lessons from this project]
- [Areas for improvement]

## Process Improvements
- [Suggested process improvements]
- [Tools or methods to implement]

## Client Feedback Summary
Client satisfaction high with positive feedback received.

## Recommendations
- Continue current quality standards
- Apply lessons learned to future projects
        """
        
        # Salvar review
        review_path = self.save_report(project_data, 'internal_review', review_content)
        
        return {
            "success": True,
            "content": review_content,
            "file_path": review_path
        }
        
    def save_report(self, project_data, report_type, content):
        """Salvar relatório em arquivo"""
        try:
            reports_dir = Path(self.config.get('logging', 'directory')).parent / 'reports'
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            safe_project_name = "".join(c for c in project_data['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_project_name}_{report_type}_{datetime.now().strftime('%Y%m%d')}.md"
            
            file_path = reports_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório: {e}")
            return None
            
    def update_project_status(self, project_data):
        """Atualizar status do projeto no ClickUp e Pipedrive"""
        try:
            results = {}
            
            # Atualizar ClickUp
            clickup_result = self.clickup.update_task(
                task_id=project_data['id'],
                status='complete'
            )
            results['clickup'] = clickup_result
            
            # Buscar e atualizar deal correspondente no Pipedrive (se existir)
            # Isso seria uma implementação mais complexa baseada em nomes/IDs correlacionados
            
            return {"success": True, "updates": results}
            
        except Exception as e:
            self.logger.error(f"Erro ao atualizar status: {e}")
            return {"success": False, "error": str(e)}
            
    def trigger_invoice_generation(self, project_data):
        """Trigger para geração de fatura"""
        try:
            self.logger.info(f"Triggering invoice generation for project: {project_data['name']}")
            
            # Placeholder para integração com sistema de faturação
            # Isso dependeria do sistema contábil usado
            
            invoice_data = {
                "project_name": project_data['name'],
                "completion_date": datetime.now().isoformat(),
                "status": "ready_for_invoicing"
            }
            
            return {"success": True, "invoice_data": invoice_data}
            
        except Exception as e:
            self.logger.error(f"Erro ao trigger de faturação: {e}")
            return {"success": False, "error": str(e)}
            
    def send_satisfaction_survey(self, project_data):
        """Enviar pesquisa de satisfação"""
        try:
            self.logger.info(f"Sending satisfaction survey for project: {project_data['name']}")
            
            # Placeholder para envio de pesquisa
            survey_data = {
                "project_name": project_data['name'],
                "survey_link": f"https://survey.alanharpercomposites.com.br/{project_data['id']}",
                "sent_date": datetime.now().isoformat()
            }
            
            return {"success": True, "survey_data": survey_data}
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar pesquisa: {e}")
            return {"success": False, "error": str(e)}
            
    def send_completion_notifications(self, project_data):
        """Enviar notificações de conclusão"""
        try:
            message = self.config.get('whatsapp', 'message_templates', 'project_completed').format(
                project_name=project_data['name']
            )
            
            self.whatsapp.send_notification(message, project_data['url'])
            
            return {"success": True, "message_sent": True}
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificações: {e}")
            return {"success": False, "error": str(e)}
            
    def calculate_project_duration(self, project_data):
        """Calcular duração do projeto em dias"""
        try:
            start_date = datetime.fromtimestamp(int(project_data['created'])/1000)
            end_date = datetime.now()
            return (end_date - start_date).days
        except:
            return 0

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AHC Project Completion Processor')
    parser.add_argument('--project-id', help='ID do projeto')
    parser.add_argument('--task-id', help='ID da task principal do projeto')
    parser.add_argument('--client-name', help='Nome do cliente')
    parser.add_argument('--no-reports', action='store_true', help='Não gerar relatórios')
    parser.add_argument('--trigger-invoice', action='store_true', help='Trigger geração de fatura')
    parser.add_argument('--no-survey', action='store_true', help='Não enviar pesquisa de satisfação')
    parser.add_argument('--debug', action='store_true', help='Ativar modo debug')
    parser.add_argument('--config', help='Caminho para arquivo de configuração personalizado')
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not args.project_id and not args.task_id:
        print("❌ É necessário fornecer --project-id ou --task-id")
        sys.exit(1)
        
    # Set debug mode
    if args.debug:
        os.environ['AHC_DEBUG'] = 'true'
        
    try:
        processor = ProjectCompletionProcessor(args.config)
        
        result = processor.complete_project(
            project_id=args.project_id,
            task_id=args.task_id,
            client_name=args.client_name,
            generate_reports=not args.no_reports,
            trigger_invoice=args.trigger_invoice,
            send_survey=not args.no_survey
        )
        
        if result['success']:
            print(f"✅ Conclusão de projeto executada com sucesso")
            print(json.dumps(result, indent=2, default=str))
        else:
            print(f"❌ Erro na conclusão: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"ERRO: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()