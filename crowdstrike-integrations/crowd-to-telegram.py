# Wallace Alves
# wallace.palves@rededor.com.br ou (21) 97009-3729
import requests
import json
import os
from datetime import datetime, timedelta

# --- INÍCIO DA CONFIGURAÇÃO ---
# Preencha com suas credenciais.
# Abaixo a URL da sua cloud: https://api.us-2.crowdstrike.com, etc. Então cuidado ao configurar aqui pois depende da sua console
CS_BASE_URL = 'https://api.crowdstrike.com'
CS_CLIENT_ID = 'SEU_ID_DE_CLIENTE_CROWDSTRIKE'
CS_CLIENT_SECRET = 'SEU_SEGREDO_DE_CLIENTE_CROWDSTRIKE'

TELEGRAM_BOT_TOKEN = 'SEU_TOKEN_DE_BOT_DO_TELEGRAM'
TELEGRAM_CHAT_ID = 'SEU_CHAT_ID_DO_TELEGRAM' # Pode ser um ID de grupo ou de usuário

# Arquivo para guardar o timestamp da última detecção processada
TIMESTAMP_FILE = 'last_detection_timestamp.txt'
# --- FIM DA CONFIGURAÇÃO ---


def get_auth_token():
    """Autentica na API do CrowdStrike para obter um token de acesso."""
    print("Autenticando na API do CrowdStrike...")
    url = f"{CS_BASE_URL}/oauth2/token"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'client_id': CS_CLIENT_ID,
        'client_secret': CS_CLIENT_SECRET,
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        response_json = response.json()
        token = response_json.get('access_token')
        if not token:
            print("Erro: Token de acesso não encontrado na resposta da API.")
            return None
        print("Autenticação bem-sucedida.")
        return token
    except requests.exceptions.RequestException as e:
        print(f"Erro ao autenticar na API: {e}")
        return None
    except json.JSONDecodeError:
        print("Erro: A resposta da API de autenticação não é um JSON válido.")
        return None


def get_last_timestamp():
    """Lê o timestamp do arquivo ou retorna um de 1 hora atrás se o arquivo não existir."""
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, 'r') as f:
            return f.read().strip()
    else:
        # Na primeira execução, busca detecções da última hora para não sobrecarregar.
        return (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"


def save_last_timestamp(timestamp):
    """Salva o timestamp da última detecção no arquivo."""
    with open(TIMESTAMP_FILE, 'w') as f:
        f.write(timestamp)


def get_new_detections(token, last_timestamp):
    """Busca por novas detecções desde o último timestamp registrado."""
    print(f"Buscando novas detecções desde {last_timestamp}...")
    url = f"{CS_BASE_URL}/detects/queries/detects/v1"
    headers = {'authorization': f'Bearer {token}'}
    
    # Usando FQL (Falcon Query Language) para filtrar por data e ordenar
    params = {
        'filter': f"created_timestamp:>'{last_timestamp}'",
        'sort': 'created_timestamp.asc',
        'limit': 100 # Limite para não sobrecarregar a API, pode ser ajustado
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        detection_ids = response.json().get('resources', [])
        
        if not detection_ids:
            print("Nenhuma nova detecção encontrada.")
            return []
            
        print(f"Encontradas {len(detection_ids)} novas detecções. Buscando detalhes...")
        
        # Busca os detalhes completos das detecções encontradas
        details_url = f"{CS_BASE_URL}/detects/entities/summaries/v1"
        body = {'ids': detection_ids}
        response_details = requests.post(details_url, headers=headers, json=body)
        response_details.raise_for_status()
        
        return response_details.json().get('resources', [])
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar detecções: {e}")
        return []


def format_telegram_message(detection):
    """Formata os detalhes de uma detecção em uma mensagem legível para o Telegram."""
    
    # Função auxiliar para escapar caracteres especiais do MarkdownV2 do Telegram
    def escape_markdown(text):
        if not isinstance(text, str):
            text = str(text)
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

    device = detection.get('device', {})
    behavior = detection.get('behaviors', [{}])[0]
    
    # Informações principais
    detection_id = escape_markdown(detection.get('detection_id'))
    hostname = escape_markdown(device.get('hostname', 'N/A'))
    severity = escape_markdown(detection.get('max_severity_displayname', 'N/A'))
    os_version = escape_markdown(device.get('os_version', 'N/A'))
    user_name = escape_markdown(behavior.get('user_name', 'N/A'))
    
    # Informações do processo
    filename = escape_markdown(behavior.get('filename', 'N/A'))
    cmd_line = escape_markdown(behavior.get('cmdline', 'N/A'))
    
    # Táticas e técnicas do MITRE ATT&CK
    tactic = escape_markdown(behavior.get('tactic', 'N/A'))
    technique = escape_markdown(behavior.get('technique', 'N/A'))
    
    # Timestamp e Link
    timestamp_utc = detection.get('created_timestamp', '').replace('Z', '+00:00')
    timestamp_obj = datetime.fromisoformat(timestamp_utc)
    timestamp_brt = (timestamp_obj - timedelta(hours=3)).strftime('%d/%m/%Y %H:%M:%S') + " (BRT)"
    
    # O link de detecção pode variar um pouco dependendo da sua cloud (ex: falcon.us-2.crowdstrike.com)
    falcon_link = f"https://falcon.crowdstrike.com/activity/detections/detail/{detection.get('detection_id')}"

    # Montando a mensagem com formatação MarkdownV2
    message = (
        f"🚨 *Nova Detecção de Ameaça no CrowdStrike* 🚨\n\n"
        f"*Dispositivo:* `{hostname}`\n"
        f"*Usuário:* `{user_name}`\n"
        f"*Severidade:* *{severity}*\n"
        f"*Sistema Operacional:* {os_version}\n"
        f"*Horário:* {escape_markdown(timestamp_brt)}\n\n"
        f"*{'='*25}*\n\n"
        f"*Detalhes do Processo*\n"
        f"*Nome do Arquivo:* `{filename}`\n"
        f"*Linha de Comando:*\n```\n{cmd_line}\n```\n\n"
        f"*Tática MITRE ATT&CK:* {tactic}\n"
        f"*Técnica MITRE ATT&CK:* {technique}\n\n"
        f"[➡️ Abrir Detecção no Console Falcon]({falcon_link})"
    )
    
    return message

def send_to_telegram(message):
    """Envia a mensagem formatada para o chat do Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'MarkdownV2' # Habilita formatação
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        if response.json().get('ok'):
            print("Alerta enviado com sucesso para o Telegram.")
        else:
            print(f"Falha ao enviar para o Telegram: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para a API do Telegram: {e}")


# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    print("Iniciando o script de monitoramento de alertas CrowdStrike...")
    
    # Validação inicial das credenciais
    if 'SEU_' in CS_CLIENT_ID or 'SEU_' in TELEGRAM_BOT_TOKEN:
        print("\n!!! ERRO: Parece que as credenciais não foram preenchidas. Edite o script e adicione suas chaves de API.")
        exit()

    token = get_auth_token()
    
    if token:
        last_ts = get_last_timestamp()
        new_detections = get_new_detections(token, last_ts)
        
        if new_detections:
            # Ordena as detecções por data para garantir que a última seja realmente a mais recente
            new_detections.sort(key=lambda d: d.get('created_timestamp', ''))
            
            for detection in new_detections:
                print(f"\nProcessando detecção ID: {detection.get('detection_id')}")
                # Formata e envia para o Telegram
                telegram_message = format_telegram_message(detection)
                send_to_telegram(telegram_message)
            
            # Atualiza o timestamp com o da última detecção processada
            latest_timestamp = new_detections[-1].get('created_timestamp')
            print(f"\nAtualizando o timestamp para: {latest_timestamp}")
            save_last_timestamp(latest_timestamp)
        
    print("\nProcesso finalizado.")
