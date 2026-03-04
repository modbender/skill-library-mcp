#!/usr/bin/env python3
"""Omie ERP API Client."""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta

APP_KEY = os.environ.get("OMIE_APP_KEY", "")
APP_SECRET = os.environ.get("OMIE_APP_SECRET", "")
BASE_URL = "https://app.omie.com.br/api/v1"


def api_call(endpoint: str, call: str, params: list) -> dict:
    """Make an Omie API call."""
    payload = json.dumps({
        "call": call,
        "app_key": APP_KEY,
        "app_secret": APP_SECRET,
        "param": params
    }).encode("utf-8")

    req = urllib.request.Request(
        f"{BASE_URL}/{endpoint}/",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}", "detail": body}
    except Exception as e:
        return {"error": str(e)}


# ── Clientes ──────────────────────────────────────────────

def clientes_listar(pagina=1, por_pagina=20):
    data = api_call("geral/clientes", "ListarClientesResumido", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def clientes_buscar(filtro: dict):
    params = {"pagina": 1, "registros_por_pagina": 50}
    if "cnpj_cpf" in filtro:
        params["clientesFiltro"] = {"cnpj_cpf": filtro["cnpj_cpf"]}
    if "codigo" in filtro:
        params["clientesFiltro"] = {"codigo_cliente_omie": int(filtro["codigo"])}
    if "nome" in filtro:
        params["clientesFiltro"] = {"nome_fantasia": filtro["nome"]}
    data = api_call("geral/clientes", "ListarClientesResumido", [params])
    return data


def clientes_detalhar(codigo: int):
    data = api_call("geral/clientes", "ConsultarCliente", [
        {"codigo_cliente_omie": codigo}
    ])
    return data


# ── Produtos ──────────────────────────────────────────────

def produtos_listar(pagina=1, por_pagina=20):
    data = api_call("geral/produtos", "ListarProdutosResumido", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def produtos_detalhar(codigo: int):
    data = api_call("geral/produtos", "ConsultarProduto", [
        {"codigo_produto": codigo}
    ])
    return data


# ── Pedidos de Venda ──────────────────────────────────────

def pedidos_listar(pagina=1, por_pagina=20):
    data = api_call("produtos/pedido", "ListarPedidos", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def pedidos_detalhar(numero: int):
    data = api_call("produtos/pedido", "ConsultarPedido", [
        {"numero_pedido": numero}
    ])
    return data


def pedidos_status(numero: int):
    data = api_call("produtos/pedido", "ConsultarStatusPedido", [
        {"numero_pedido": numero}
    ])
    return data


# ── Financeiro ────────────────────────────────────────────

def contas_receber(pagina=1, por_pagina=20):
    data = api_call("financas/contasreceber", "ListarContasReceber", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def contas_pagar(pagina=1, por_pagina=20):
    data = api_call("financas/contaspagar", "ListarContasPagar", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def resumo_financeiro():
    hoje = datetime.now().strftime("%d/%m/%Y")
    data = api_call("financas/contasreceber", "ListarContasReceber", [
        {"pagina": 1, "registros_por_pagina": 1}
    ])
    return {"data": hoje, "resumo": data}


# ── Notas Fiscais ─────────────────────────────────────────

def nfe_listar(pagina=1, por_pagina=20):
    data = api_call("produtos/nfe", "ListarNFe", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def nfe_detalhar(numero: int):
    data = api_call("produtos/nfe", "ConsultarNFe", [
        {"numero_nfe": numero}
    ])
    return data


# ── Estoque ───────────────────────────────────────────────

def estoque_posicao(pagina=1, por_pagina=20):
    data = api_call("estoque/saldo", "ConsultarSaldoEstoque", [
        {"pagina": pagina, "registros_por_pagina": por_pagina}
    ])
    return data


def estoque_produto(codigo: int):
    data = api_call("estoque/saldo", "ConsultarSaldoEstoque", [
        {"codigo_produto": codigo}
    ])
    return data


# ── CLI ────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: omie_client.py <command> [args]")
        print("\nCommands:")
        print("  clientes_listar [pagina] [por_pagina]")
        print("  clientes_buscar [filtro]")
        print("  clientes_detalhar codigo")
        print("  produtos_listar [pagina] [por_pagina]")
        print("  produtos_detalhar codigo")
        print("  pedidos_listar [pagina] [por_pagina]")
        print("  pedidos_detalhar numero")
        print("  pedidos_status numero")
        print("  contas_receber [pagina] [por_pagina]")
        print("  contas_pagar [pagina] [por_pagina]")
        print("  resumo_financeiro")
        print("  nfe_listar [pagina] [por_pagina]")
        print("  nfe_detalhar numero")
        print("  estoque_posicao [pagina] [por_pagina]")
        print("  estoque_produto codigo")
        sys.exit(1)

    command = sys.argv[1]
    
    try:
        if command == "clientes_listar":
            page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            per_page = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = clientes_listar(page, per_page)
        elif command == "clientes_buscar":
            filtro = {}
            for arg in sys.argv[2:]:
                if "=" in arg:
                    k, v = arg.split("=", 1)
                    filtro[k] = v
            result = clientes_buscar(filtro)
        elif command == "clientes_detalhar":
            result = clientes_detalhar(int(sys.argv[2]))
        elif command == "produtos_listar":
            page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            per_page = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = produtos_listar(page, per_page)
        elif command == "produtos_detalhar":
            result = produtos_detalhar(int(sys.argv[2]))
        elif command == "pedidos_listar":
            page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            per_page = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = pedidos_listar(page, per_page)
        elif command == "pedidos_detalhar":
            result = pedidos_detalhar(int(sys.argv[2]))
        elif command == "pedidos_status":
            result = pedidos_status(int(sys.argv[2]))
        elif command == "contas_receber":
            page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            per_page = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = contas_receber(page, per_page)
        elif command == "contas_pagar":
            page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            per_page = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = contas_pagar(page, per_page)
        elif command == "resumo_financeiro":
            result = resumo_financeiro()
        elif command == "nfe_listar":
            page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            per_page = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = nfe_listar(page, per_page)
        elif command == "nfe_detalhar":
            result = nfe_detalhar(int(sys.argv[2]))
        elif command == "estoque_posicao":
            page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            per_page = int(sys.argv[3]) if len(sys.argv) > 3 else 20
            result = estoque_posicao(page, per_page)
        elif command == "estoque_produto":
            result = estoque_produto(int(sys.argv[2]))
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
        
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)
