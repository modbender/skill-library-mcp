#!/usr/bin/env python3
import os

def list_tools():
    reference_path = os.path.join(os.path.dirname(__file__), '..', 'references', 'tools.md')
    if not os.path.exists(reference_path):
        print("Reference file not found.")
        return

    with open(reference_path, 'r') as f:
        lines = f.readlines()
        
    print("📋 Menu de Instalação - Setup Automatik:")
    for line in lines:
        line = line.strip()
        if line.startswith('## '):
            print(f"\n📂 {line[3:]}")
        elif line.startswith('- **'):
            # Formato esperado: - **Tool Name**: Description
            try:
                parts = line.split('**: ')
                tool = parts[0].replace('- **', '').strip()
                description = parts[1].strip()
                # O usuário quer: Tool: Desc. -- copie e cole no chat instalar [Tool] Setup automatik
                print(f"{tool}: {description}. -- copie e cole no chat: instalar {tool} Setup automatik")
            except IndexError:
                continue

if __name__ == "__main__":
    list_tools()
