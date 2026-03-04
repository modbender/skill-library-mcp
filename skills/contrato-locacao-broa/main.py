import json
import sys
import requests

def fill_rental_form(dados):
    """
    Skill para cadastrar um novo contrato de locação no Google Forms.
    Recebe um dicionário 'dados' contendo as informações do contrato.
    """
    form_id = "1FAIpQLSf9KuCi47rcNOPnlC41PFJol0c97FmbOZ2vPC0M-XVh1wNT4w"
    url = f"https://docs.google.com/forms/d/e/{form_id}/formResponse"

    # Mapeamento dos campos do dicionário para os IDs do Google Forms
    payload = {
        "entry.211432349": dados.get("email"),
        "entry.537318229": dados.get("telefone"),
        "entry.1005338251": dados.get("nome"),
        "entry.77622006": dados.get("cpf"),
        "entry.992935698": dados.get("endereco"),
        "entry.34087811": dados.get("numero"),
        "entry.4796803": dados.get("complemento", ""), # Fallback para vazio se não existir
        "entry.571644012": dados.get("bairro"),
        "entry.973875267": dados.get("cidade"),
        "entry.2126585082": dados.get("estado"),
        "entry.74193818": dados.get("data_entrada"),
        "entry.877461528": dados.get("data_saida"),
        "entry.1983673985": dados.get("valor"),
        "entry.431306295": dados.get("caucao", "")
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            return "Sucesso: O contrato foi registrado e o PDF será enviado."
        else:
            return f"Erro no Forms: Código {response.status_code}"
    except Exception as e:
        return f"Erro de rede: {str(e)}"


if __name__ == "__main__":
    # Se houver argumentos na linha de comando, usamos eles (vêm da IA)
    if len(sys.argv) > 1:
        try:
            # A IA envia os dados como uma string JSON no primeiro argumento
            dados_input = json.loads(sys.argv[1])
            # Se a IA enviar {"dados": {...}}, extraímos o conteúdo
            payload = dados_input.get("dados", dados_input)
            print(fill_rental_form(payload))
        except Exception as e:
            print(f"Erro ao processar entrada: {e}")
    else:
        # APENAS para seu teste manual no PC, se não houver argumentos
        data_teste = { "nome": "Teste Local", "email": "teste@email.com" }
        print(fill_rental_form(data_teste))
