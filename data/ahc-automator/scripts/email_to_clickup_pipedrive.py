#!/usr/bin/env python3
"""
AHC-Automator: Email → ClickUp → Pipedrive Chain
Monitora emails específicos (Ian/Ronaldo) e automaticamente cria tasks no ClickUp e deals no Pipedrive
"""

import os
import sys
import json
import logging
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path

# Adicionar o diretório do skill ao path
SKILL_DIR = Path(__file__).parent.parent
sys.path.append(str(SKILL_DIR))

from scripts.ahc_utils import AHCConfig, ClickUpClient, PipedriveClient, WhatsAppNotifier, EmailParser

class EmailToClickUpPipedriveProcessor:
    def __init__(self, config_path=None):
        """Inicializar processador de email para ClickUp/Pipedrive"""
        self.config = AHCConfig(config_path)
        self.clickup = ClickUpClient(self.config)
        self.pipedrive = PipedriveClient(self.config)
        self.whatsapp = WhatsAppNotifier(self.config)
        self.email_parser = EmailParser(self.config)
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configurar logging"""
        log_dir = Path(self.config.get('logging', 'directory'))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / 'email_processing.log'
        
        logging.basicConfig(
            level=getattr(logging, self.config.get('logging', 'level')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def process_emails(self, account_filter=None):
        """Processar emails para ações ClickUp/Pipedrive"""
        try:
            # Obter emails dos últimos 5 minutos
            since_time = datetime.now() - timedelta(minutes=5)
            
            monitor_accounts = self.config.get('email', 'monitor_accounts')
            if account_filter:
                monitor_accounts = [acc for acc in monitor_accounts if account_filter in acc]
                
            self.logger.info(f"Processando emails de: {monitor_accounts}")
            
            emails = self.email_parser.get_recent_emails(monitor_accounts, since_time)
            
            for email in emails:
                self.process_single_email(email)
                
        except Exception as e:
            self.logger.error(f"Erro ao processar emails: {e}")
            
    def process_single_email(self, email):
        """Processar um email individual"""
        try:
            sender = email.get('sender', '')
            subject = email.get('subject', '')
            body = email.get('body', '')
            
            self.logger.info(f"Processando email de {sender}: {subject}")
            
            # Verificar se contém keywords ClickUp
            if self.email_parser.contains_keywords(email, 'clickup'):
                self.handle_clickup_request(email)
                
            # Verificar se contém keywords Pipedrive
            if self.email_parser.contains_keywords(email, 'pipedrive'):
                self.handle_pipedrive_request(email)
                
        except Exception as e:
            self.logger.error(f"Erro ao processar email individual: {e}")
            
    def handle_clickup_request(self, email):
        """Lidar com solicitações ClickUp"""
        try:
            self.logger.info(f"Processando solicitação ClickUp do email: {email['subject']}")
            
            # Extrair dados do email para task
            task_data = self.email_parser.extract_clickup_data(email)
            
            # Criar task no ClickUp
            task_result = self.clickup.create_task(
                list_id=task_data.get('list_id', self.config.get('clickup', 'templates', 'standard')),
                name=task_data.get('name', f"Solicitação de {email['sender']}"),
                description=task_data.get('description', email['body']),
                assignees=task_data.get('assignees', []),
                priority=task_data.get('priority', 3),
                due_date=task_data.get('due_date')
            )
            
            if task_result.get('success'):
                task_id = task_result['data']['id']
                task_url = task_result['data']['url']
                
                self.logger.info(f"Task criada com sucesso: {task_id}")
                
                # Enviar notificação WhatsApp
                message = self.config.get('whatsapp', 'message_templates', 'task_created').format(
                    task_title=task_data.get('name', 'Nova Task')
                )
                self.whatsapp.send_notification(message, task_url)
                
                return task_result
                
            else:
                self.logger.error(f"Erro ao criar task ClickUp: {task_result}")
                
        except Exception as e:
            self.logger.error(f"Erro ao processar solicitação ClickUp: {e}")
            
    def handle_pipedrive_request(self, email):
        """Lidar com solicitações Pipedrive"""
        try:
            self.logger.info(f"Processando solicitação Pipedrive do email: {email['subject']}")
            
            # Extrair dados do email para deal/person
            pipedrive_data = self.email_parser.extract_pipedrive_data(email)
            
            # Primeiro criar/encontrar pessoa se necessário
            person_id = None
            if pipedrive_data.get('person_name'):
                person_result = self.pipedrive.create_or_find_person(
                    name=pipedrive_data['person_name'],
                    email=pipedrive_data.get('person_email'),
                    phone=pipedrive_data.get('person_phone')
                )
                if person_result.get('success'):
                    person_id = person_result['data']['id']
                    
            # Criar deal se solicitado
            if pipedrive_data.get('deal_title'):
                deal_result = self.pipedrive.create_deal(
                    title=pipedrive_data['deal_title'],
                    value=pipedrive_data.get('value'),
                    currency=pipedrive_data.get('currency', 'EUR'),
                    person_id=person_id,
                    org_id=pipedrive_data.get('org_id')
                )
                
                if deal_result.get('success'):
                    deal_id = deal_result['data']['id']
                    self.logger.info(f"Deal criado com sucesso: {deal_id}")
                    
                    # Enviar notificação WhatsApp
                    message = self.config.get('whatsapp', 'message_templates', 'deal_created').format(
                        deal_title=pipedrive_data['deal_title']
                    )
                    self.whatsapp.send_notification(message)
                    
                    return deal_result
                else:
                    self.logger.error(f"Erro ao criar deal Pipedrive: {deal_result}")
                    
        except Exception as e:
            self.logger.error(f"Erro ao processar solicitação Pipedrive: {e}")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AHC Email to ClickUp/Pipedrive Processor')
    parser.add_argument('--account', help='Filtrar por conta de email específica')
    parser.add_argument('--debug', action='store_true', help='Ativar modo debug')
    parser.add_argument('--config', help='Caminho para arquivo de configuração personalizado')
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        os.environ['AHC_DEBUG'] = 'true'
        
    try:
        processor = EmailToClickUpPipedriveProcessor(args.config)
        processor.process_emails(args.account)
        
        processor.logger.info("Processamento de emails concluído com sucesso")
        
    except Exception as e:
        print(f"ERRO: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()