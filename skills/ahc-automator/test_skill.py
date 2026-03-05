#!/usr/bin/env python3
"""
AHC-Automator: Test Script
Script de teste para verificar funcionamento básico do skill
"""

import os
import sys
import json
from pathlib import Path

SKILL_DIR = Path(__file__).parent
sys.path.append(str(SKILL_DIR))

def test_imports():
    """Testar se todas as importações funcionam"""
    print("🧪 Testando importações...")
    
    try:
        from scripts.ahc_utils import AHCConfig, ClickUpClient, PipedriveClient, WhatsAppNotifier
        print("  ✅ ahc_utils")
    except Exception as e:
        print(f"  ❌ ahc_utils: {e}")
        return False
        
    try:
        from scripts.email_to_clickup_pipedrive import EmailToClickUpPipedriveProcessor
        print("  ✅ email_to_clickup_pipedrive")
    except Exception as e:
        print(f"  ❌ email_to_clickup_pipedrive: {e}")
        return False
        
    try:
        from scripts.client_onboarding import ClientOnboardingProcessor
        print("  ✅ client_onboarding")
    except Exception as e:
        print(f"  ❌ client_onboarding: {e}")
        return False
        
    try:
        from scripts.project_completion import ProjectCompletionProcessor
        print("  ✅ project_completion")
    except Exception as e:
        print(f"  ❌ project_completion: {e}")
        return False
        
    try:
        from scripts.whatsapp_notifier import AHCWhatsAppNotifier
        print("  ✅ whatsapp_notifier")
    except Exception as e:
        print(f"  ❌ whatsapp_notifier: {e}")
        return False
        
    try:
        from scripts.health_check import AHCHealthChecker
        print("  ✅ health_check")
    except Exception as e:
        print(f"  ❌ health_check: {e}")
        return False
        
    return True

def test_configuration():
    """Testar carregamento de configuração"""
    print("\n📋 Testando configuração...")
    
    try:
        from scripts.ahc_utils import AHCConfig
        config = AHCConfig()
        
        # Verificar seções principais
        sections = ['clickup', 'pipedrive', 'email', 'whatsapp', 'logging']
        for section in sections:
            if config.get(section):
                print(f"  ✅ {section}")
            else:
                print(f"  ❌ {section}: não encontrado")
                return False
                
        # Verificar configurações específicas
        team_id = config.get('clickup', 'team_id')
        if team_id == '90132745943':
            print(f"  ✅ ClickUp Team ID: {team_id}")
        else:
            print(f"  ⚠️  ClickUp Team ID: {team_id} (esperado: 90132745943)")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na configuração: {e}")
        return False

def test_api_clients():
    """Testar inicialização dos clientes API"""
    print("\n🔌 Testando clientes API...")
    
    try:
        from scripts.ahc_utils import AHCConfig, ClickUpClient, PipedriveClient
        config = AHCConfig()
        
        # Testar ClickUp Client
        try:
            clickup = ClickUpClient(config)
            print("  ✅ ClickUp Client: inicializado")
        except Exception as e:
            print(f"  ❌ ClickUp Client: {e}")
            
        # Testar Pipedrive Client  
        try:
            pipedrive = PipedriveClient(config)
            print("  ✅ Pipedrive Client: inicializado")
        except Exception as e:
            print(f"  ❌ Pipedrive Client: {e}")
            
        # Testar WhatsApp Notifier
        try:
            from scripts.ahc_utils import WhatsAppNotifier
            whatsapp = WhatsAppNotifier(config)
            print("  ✅ WhatsApp Notifier: inicializado")
        except Exception as e:
            print(f"  ❌ WhatsApp Notifier: {e}")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nos clientes API: {e}")
        return False

def test_file_structure():
    """Testar estrutura de arquivos"""
    print("\n📁 Testando estrutura de arquivos...")
    
    required_files = [
        'SKILL.md',
        '_meta.json',
        'configs/ahc_config.json',
        'scripts/ahc_utils.py',
        'scripts/email_to_clickup_pipedrive.py',
        'scripts/client_onboarding.py',
        'scripts/project_completion.py',
        'scripts/whatsapp_notifier.py',
        'scripts/health_check.py',
        'scripts/setup.py',
        'docs/README.md',
        'templates/email_templates.json',
        'workflows/custom_workflow_example.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = SKILL_DIR / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}: não encontrado")
            missing_files.append(file_path)
            
    if missing_files:
        print(f"\n  ⚠️  Arquivos faltando: {len(missing_files)}")
        return False
    else:
        print(f"\n  ✅ Todos os arquivos presentes ({len(required_files)} arquivos)")
        return True

def test_example_execution():
    """Testar execução de exemplo (sem APIs reais)"""
    print("\n🚀 Testando execução de exemplo...")
    
    try:
        # Testar notificação WhatsApp (modo exemplo)
        from scripts.whatsapp_notifier import AHCWhatsAppNotifier
        from scripts.ahc_utils import AHCConfig
        
        config = AHCConfig()
        notifier = AHCWhatsAppNotifier()
        
        result = notifier.send_custom_notification("🧪 Teste do AHC-Automator skill", urgent=False)
        
        if result.get('success'):
            print("  ✅ Notificação de teste: enviada")
        else:
            print(f"  ❌ Notificação de teste: {result.get('error')}")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na execução de exemplo: {e}")
        return False

def run_full_test():
    """Executar todos os testes"""
    print("🔧 AHC-Automator Skill Test Suite")
    print("=" * 50)
    
    tests = [
        ("Importações", test_imports),
        ("Configuração", test_configuration),
        ("Clientes API", test_api_clients),
        ("Estrutura de Arquivos", test_file_structure),
        ("Execução de Exemplo", test_example_execution)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
        
    # Relatório final
    print("\n" + "=" * 50)
    print("📊 RELATÓRIO DE TESTES")
    print("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, success in results.items():
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
            
    print(f"\n📈 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! AHC-Automator skill está funcionando.")
        print("\n📚 Próximos passos:")
        print("  1. Configure as APIs: python scripts/setup.py")
        print("  2. Execute health check: python scripts/health_check.py")
        print("  3. Leia a documentação: docs/README.md")
        return True
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam. Corrija os problemas antes de usar.")
        return False

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AHC-Automator Test Suite')
    parser.add_argument('--quick', action='store_true', help='Apenas testes rápidos')
    
    args = parser.parse_args()
    
    try:
        if args.quick:
            # Apenas teste de importações
            success = test_imports()
        else:
            # Teste completo
            success = run_full_test()
            
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Testes cancelados pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO nos testes: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()