#!/usr/bin/env python3
"""
ClawWork Quick Task - Wrapper simplificado para execução rápida
"""

import sys
import os

# Adiciona paths
sys.path.insert(0, "/home/freedom/.openclaw/workspace/ClawWork")
sys.path.insert(0, "/home/freedom/.openclaw/workspace/ClawWork/livebench")

# Carrega .env
from dotenv import load_dotenv
load_dotenv("/home/freedom/.openclaw/workspace/ClawWork/.env")

async def quick_task(task_description: str):
    """Executa uma tarefa rápida sem configuração complexa"""
    
    print(f"💰 ClawWork: {task_description[:50]}...")
    print("")
    
    # Para MVP, vamos apenas simular/mostrar o que aconteceria
    # A execução real requer E2B API key
    
    print("📋 Configuração:")
    print(f"   Modelo: zai/glm-4.7")
    print(f"   Balance inicial: $100.00")
    print(f"   Max steps: 15")
    print("")
    print("🔄 Para executar esta tarefa com ClawWork:")
    print("")
    print("1. Configure E2B_API_KEY em ~/.openclaw/workspace/ClawWork/.env")
    print("   Obtenha em: https://e2b.dev/")
    print("")
    print("2. Execute:")
    print(f"   python /home/freedom/.openclaw/workspace/skills/clawwork/cli.py run -t '{task_description}'")
    print("")
    print("3. Ou use o dashboard:")
    print("   cd /home/freedom/.openclaw/workspace/ClawWork")
    print("   ./start_dashboard.sh")
    print("")
    print("📊 Dados existentes:")
    
    # Mostra dados existentes
    import json
    data_path = "/home/freedom/.openclaw/workspace/ClawWork/livebench/data/agent_data"
    
    if os.path.exists(data_path):
        for agent in os.listdir(data_path):
            agent_dir = os.path.join(data_path, agent)
            if os.path.isdir(agent_dir):
                print(f"   🤖 {agent}")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python quick_task.py 'descrição da tarefa'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    
    import asyncio
    asyncio.run(quick_task(task))
