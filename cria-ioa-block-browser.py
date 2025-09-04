import requests

# Infos pra autenticacao
url = 'https://api.crowdstrike.com'
id = 'id-crowd'
secret = 'secret-crowd'
rulegroup_id = 'rulegroup-do-seu-ioagroup'

def TokenAuth():
    """Autentica na API do CrowdStrike para obter um token de acesso."""
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    data = {
        'client_id': id,
        'client_secret': secret,
    }

    try:
        response = requests.post(url + '/oauth2/token', headers=headers, data=data)
        response.raise_for_status()  # Lança um erro para respostas HTTP ruins (4xx ou 5xx)
        response_json = response.json()
        token_auth = response_json.get('access_token')
        if not token_auth:
            print("Erro: Token de acesso não encontrado na resposta.")
            return None
        return token_auth
    except requests.exceptions.RequestException as e:
        print(f"Erro ao autenticar na API: {e}")
        return None
    except ValueError:
        print("Erro: A resposta da API de autenticação não é um JSON válido.")
        return None


def CreateBrowserBlockRule(token_auth):
    """Cria uma única regra de IOA para bloquear a execução de navegadores específicos."""
    if not token_auth:
        print("Criação da regra cancelada devido à falha na autenticação.")
        return None

    headers = {
        'accept': 'application/json',
        'authorization': f'Bearer {token_auth}',
        'Content-Type': 'application/json',
    }

    # Estrutura de dados para a nova regra de bloqueio de navegadores
    data = {
        "comment": "Regra para bloquear navegadores de internet indesejados.",
        "description": "Bloqueia a execução dos navegadores Chrome, Edge, Brave, Firefox e Opera.",
        "disposition_id": 30,  # 30 = Kill Process (Ação de bloqueio)
        "field_values": [
            {
                "final_value": "",
                "label": "Image Filename",
                "name": "ImageFilename",
                "type": "excludable",
                "value": r"(?i)(.*chrome.*|.*msedge.*|.*brave.*|.*firefox.*|.*opera.*)\.exe",
                "values": [
                    {
                        "label": "include",
                        "value": r"(?i)(.*chrome.*|.*msedge.*|.*brave.*|.*firefox.*|.*opera.*)\.exe"
                    }
                ]
            }
        ],
        "name": "Browsers-Malditos",
        "pattern_severity": "high",
        "rulegroup_id": rulegroup_id,
        "ruletype_id": "1"  # 1 = Process Creation
    }

    try:
        response = requests.post(url + '/ioarules/entities/rules/v1', headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao criar a regra na API: {e}")
        # Imprime o corpo da resposta se houver mais detalhes do erro
        try:
            print(f"Detalhes do erro da API: {response.json()}")
        except ValueError:
            print(f"Resposta não-JSON da API: {response.text}")
        return None
    except ValueError:
        print("Erro: A resposta da API de criação de regras não é um JSON válido.")
        return None

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    print("Iniciando processo de criação de regra de IOA...")
    
    # 1. Obter o token de autenticação
    access_token = TokenAuth()
    
    # 2. Se o token for obtido com sucesso, criar a regra
    if access_token:
        print("Autenticação bem-sucedida. Criando a regra de bloqueio de navegadores...")
        rule_response = CreateBrowserBlockRule(access_token)
        
        # 3. Imprimir o resultado
        if rule_response:
            print("\n--- Resposta da API ---")
            print(rule_response)
            if 'resources' in rule_response and rule_response['resources']:
                 print("\nSucesso! A regra 'Browsers-Malditos' foi criada com êxito.")
            else:
                 print("\nFalha ao criar a regra. Verifique a resposta da API acima para mais detalhes.")

    else:
        print("Processo finalizado com erro na autenticação.")
