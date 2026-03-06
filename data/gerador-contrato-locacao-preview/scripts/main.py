import json
import os
import sys
import re
import logging
from typing import Dict, List

import requests

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

FORM_ID = os.environ.get("FORM_ID", "1FAIpQLSf9KuCi47rcNOPnlC41PFJol0c97FmbOZ2vPC0M-XVh1wNT4w")
DRY_RUN = os.environ.get("DRY_RUN")

REQUIRED_FIELDS: List[str] = [
    "email", "telefone", "nome", "cpf",
    "endereco", "numero", "bairro",
    "cidade", "estado", "data_entrada",
    "data_saida", "valor"
]

if not FORM_ID:
    logging.error("FORM_ID não definido como variável de ambiente.")
    sys.exit(1)


def clean_digits(value: str) -> str:
    return re.sub(r"\D", "", str(value))


def parse_date(date_str: str):
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        raise ValueError(f"Data inválida: {date_str}. Use YYYY-MM-DD")
    return date_str.split("-")


def validate_required(dados: Dict):
    missing = [f for f in REQUIRED_FIELDS if not dados.get(f)]
    if missing:
        raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing)}")


def build_confirmation_summary(dados: Dict) -> str:
    lines = ["📄 Resumo do contrato de locação:", ""]
    mapping = {
        "nome": "Nome",
        "email": "E-mail",
        "telefone": "Telefone",
        "cpf": "CPF",
        "endereco": "Endereço",
        "numero": "Número",
        "bairro": "Bairro",
        "cidade": "Cidade",
        "estado": "Estado",
        "data_entrada": "Data de entrada",
        "data_saida": "Data de saída",
        "valor": "Valor",
        "caucao": "Caução",
        "complemento": "Complemento",
    }
    for key, label in mapping.items():
        if dados.get(key):
            lines.append(f"- {label}: {dados[key]}")
    lines.append("\nDeseja confirmar o envio desses dados?")
    return "\n".join(lines)


def execute_skill(dados: Dict) -> str:
    cpf = clean_digits(dados.get("cpf"))
    telefone = clean_digits(dados.get("telefone"))

    dt_entrada = parse_date(dados.get("data_entrada"))
    dt_saida = parse_date(dados.get("data_saida"))

    url = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"

    payload = {
        "entry.211432349": dados.get("email"),
        "entry.537318229": telefone,
        "entry.1005338251": dados.get("nome"),
        "entry.77622006": cpf,
        "entry.992935698": dados.get("endereco"),
        "entry.34087811": dados.get("numero"),
        "entry.4796803": dados.get("complemento", ""),
        "entry.571644012": dados.get("bairro"),
        "entry.973875267": dados.get("cidade"),
        "entry.2126585082": dados.get("estado"),
        "entry.1983673985": dados.get("valor"),
        "entry.431306295": dados.get("caucao", ""),
        "entry.74193818_year": dt_entrada[0],
        "entry.74193818_month": dt_entrada[1],
        "entry.74193818_day": dt_entrada[2],
        "entry.877461528_year": dt_saida[0],
        "entry.877461528_month": dt_saida[1],
        "entry.877461528_day": dt_saida[2],
    }

    if DRY_RUN:
        return f"[DRY-RUN] Payload gerado: {json.dumps(payload, ensure_ascii=False)}"

    response = requests.post(
        url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10
    )

    if response.status_code == 200:
        return "Sucesso: contrato registrado e PDF será enviado."
    elif response.status_code == 400:
        return "Erro: Google Forms rejeitou os dados enviados."
    else:
        return f"Erro inesperado no Forms: HTTP {response.status_code}."


if __name__ == "__main__":
    try:
        if not sys.stdin.isatty():
            _input_data = json.load(sys.stdin)
        elif len(sys.argv) > 1:
            _input_data = json.loads(sys.argv[1])
        else:
            raise ValueError("Nenhum JSON fornecido")

        _dados = _input_data.get("dados", _input_data)
        validate_required(_dados)
        print(build_confirmation_summary(_dados))
        print(execute_skill(_dados))

    except Exception as e:
        logging.error(str(e))
        print(f"Erro: {e}")
