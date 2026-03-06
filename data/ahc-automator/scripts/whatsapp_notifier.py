#!/usr/bin/env python3
"""
AHC-Automator: WhatsApp Notifier
Sistema de notificações WhatsApp para workflows AHC
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Adicionar o diretório do skill ao path
SKILL_DIR = Path(__file__).parent.parent
sys.path.append(str(SKILL_DIR))

from scripts.ahc_utils import AHCConfig

class AHCWhatsAppNotifier:
    """Notificador WhatsApp específico para AHC workflows"""
    
    def __init__(self, config_path=None):
        self.config = AHCConfig(config_path)
        self.setup_logging()
        
        # Configurações WhatsApp
        self.notification_groups = self.config.get('whatsapp', 'notification_groups', default=[])
        self.individual_contacts = self.config.get('whatsapp', 'individual_contacts', default=[])
        self.message_templates = self.config.get('whatsapp', 'message_templates', default={})
        
    def setup_logging(self):
        """Configurar logging"""
        log_dir = Path(self.config.get('logging', 'directory'))
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / 'notifications.log'
        
        logging.basicConfig(
            level=getattr(logging, self.config.get('logging', 'level')),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def send_notification(self, message_type, **kwargs):
        """Enviar notificação usando template específico"""
        try:
            template = self.message_templates.get(message_type)
            if not template:
                self.logger.error(f"Template não encontrado: {message_type}")
                return {"success": False, "error": "Template não encontrado"}
                
            # Formatar mensagem com dados fornecidos
            try:
                formatted_message = template.format(**kwargs)
            except KeyError as e:
                self.logger.error(f"Parâmetro faltando para template {message_type}: {e}")
                return {"success": False, "error": f"Parâmetro faltando: {e}"}
                
            # Adicionar timestamp
            timestamp = datetime.now().strftime('%H:%M')
            full_message = f"[{timestamp}] {formatted_message}"
            
            # Adicionar link se fornecido
            if kwargs.get('link'):
                full_message += f"\n🔗 {kwargs['link']}"
                
            return self.send_to_all_channels(full_message)
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificação: {e}")
            return {"success": False, "error": str(e)}
            
    def send_to_all_channels(self, message):
        """Enviar mensagem para todos os canais configurados"""
        results = {}
        
        # Enviar para grupos
        for group in self.notification_groups:
            result = self.send_to_group(group, message)
            results[f"group_{group}"] = result
            
        # Enviar para contatos individuais
        for contact in self.individual_contacts:
            result = self.send_to_contact(contact, message)
            results[f"contact_{contact}"] = result
            
        # Log da notificação
        self.logger.info(f"Notification sent: {message}")
        
        return {"success": True, "results": results}
        
    def send_to_group(self, group_name, message):
        """Enviar mensagem para grupo específico"""
        try:
            # Por enquanto, apenas log
            # Em implementação real, usaria OpenClaw message tool ou API WhatsApp
            self.logger.info(f"[GROUP {group_name}] {message}")
            
            # TODO: Implementar envio real
            # Exemplo usando OpenClaw message tool:
            # message_tool_result = self.send_via_openclaw_message(group_name, message)
            
            return {"success": True, "target": group_name, "type": "group"}
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar para grupo {group_name}: {e}")
            return {"success": False, "error": str(e)}
            
    def send_to_contact(self, contact_name, message):
        """Enviar mensagem para contato individual"""
        try:
            # Por enquanto, apenas log
            self.logger.info(f"[CONTACT {contact_name}] {message}")
            
            # TODO: Implementar envio real
            return {"success": True, "target": contact_name, "type": "contact"}
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar para contato {contact_name}: {e}")
            return {"success": False, "error": str(e)}
            
    def send_task_created_notification(self, task_title, task_url=None, assignee=None):
        """Notificação específica para task criada"""
        return self.send_notification(
            'task_created',
            task_title=task_title,
            link=task_url,
            assignee=assignee or 'Não atribuído'
        )
        
    def send_deal_created_notification(self, deal_title, deal_value=None, client_name=None):
        """Notificação específica para deal criado"""
        return self.send_notification(
            'deal_created', 
            deal_title=deal_title,
            deal_value=deal_value or 'Não especificado',
            client_name=client_name or 'Cliente não especificado'
        )
        
    def send_project_completed_notification(self, project_name, project_url=None, completion_date=None):
        """Notificação específica para projeto concluído"""
        return self.send_notification(
            'project_completed',
            project_name=project_name,
            link=project_url,
            completion_date=completion_date or datetime.now().strftime('%Y-%m-%d')
        )
        
    def send_client_onboarded_notification(self, client_name, project_url=None, template_used=None):
        """Notificação específica para cliente onboardado"""
        return self.send_notification(
            'client_onboarded',
            client_name=client_name,
            link=project_url,
            template_used=template_used or 'standard'
        )
        
    def send_custom_notification(self, message, urgent=False):
        """Enviar notificação customizada"""
        try:
            if urgent:
                message = f"🚨 URGENTE: {message}"
            else:
                message = f"ℹ️ {message}"
                
            timestamp = datetime.now().strftime('%H:%M')
            full_message = f"[{timestamp}] {message}"
            
            return self.send_to_all_channels(full_message)
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificação customizada: {e}")
            return {"success": False, "error": str(e)}
            
    def send_error_notification(self, error_message, context=None):
        """Enviar notificação de erro"""
        try:
            error_msg = f"❌ ERRO AHC-Automator: {error_message}"
            if context:
                error_msg += f"\nContexto: {context}"
                
            return self.send_custom_notification(error_msg, urgent=True)
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificação de erro: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Função principal para teste e uso direto"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AHC WhatsApp Notifier')
    parser.add_argument('--type', required=True, 
                       choices=['task_created', 'deal_created', 'project_completed', 'client_onboarded', 'custom', 'error'],
                       help='Tipo de notificação')
    parser.add_argument('--message', help='Mensagem personalizada (para tipo custom/error)')
    parser.add_argument('--task-title', help='Título da task')
    parser.add_argument('--task-url', help='URL da task')
    parser.add_argument('--deal-title', help='Título do deal')
    parser.add_argument('--deal-value', help='Valor do deal')
    parser.add_argument('--client-name', help='Nome do cliente')
    parser.add_argument('--project-name', help='Nome do projeto')
    parser.add_argument('--project-url', help='URL do projeto')
    parser.add_argument('--urgent', action='store_true', help='Marcar como urgente')
    parser.add_argument('--debug', action='store_true', help='Ativar modo debug')
    parser.add_argument('--config', help='Caminho para arquivo de configuração personalizado')
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        os.environ['AHC_DEBUG'] = 'true'
        
    try:
        notifier = AHCWhatsAppNotifier(args.config)
        
        if args.type == 'task_created':
            if not args.task_title:
                print("❌ --task-title é obrigatório para task_created")
                sys.exit(1)
            result = notifier.send_task_created_notification(args.task_title, args.task_url)
            
        elif args.type == 'deal_created':
            if not args.deal_title:
                print("❌ --deal-title é obrigatório para deal_created")
                sys.exit(1)
            result = notifier.send_deal_created_notification(args.deal_title, args.deal_value, args.client_name)
            
        elif args.type == 'project_completed':
            if not args.project_name:
                print("❌ --project-name é obrigatório para project_completed")
                sys.exit(1)
            result = notifier.send_project_completed_notification(args.project_name, args.project_url)
            
        elif args.type == 'client_onboarded':
            if not args.client_name:
                print("❌ --client-name é obrigatório para client_onboarded")
                sys.exit(1)
            result = notifier.send_client_onboarded_notification(args.client_name, args.project_url)
            
        elif args.type == 'custom':
            if not args.message:
                print("❌ --message é obrigatório para tipo custom")
                sys.exit(1)
            result = notifier.send_custom_notification(args.message, args.urgent)
            
        elif args.type == 'error':
            if not args.message:
                print("❌ --message é obrigatório para tipo error")
                sys.exit(1)
            result = notifier.send_error_notification(args.message)
            
        if result['success']:
            print("✅ Notificação enviada com sucesso")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Erro ao enviar notificação: {result['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"ERRO: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()