# Webhook interface request e sender para whatsapp
# Precisa ter o WhatsApp enterprise (developer)
# Precisa apenas instalar o flask (pip3 install flask) o resto já é nativo
# Qualquer dúvida: 2197009-3729 (Wallace)

import requests
import json
from flask import Flask, request, jsonify

# --- Configuração do WhatsApp (Preencha com seus dados) --- se ligue nessa parte, pois sem isso CERTO, não vai funcionar (precisa configurar no META - facebook developers)
WA_API_URL = "https"
WA_ACCESS_TOKEN = "SEU_TOKEN_DE_ACESSO_PERMANENTE"  # Token do seu App Meta
WA_PHONE_NUMBER_ID = "ID_DO_SEU_NUMERO_DE_TELEFONE"  # ID do número de telefone registrado
RECIPIENT_WA_ID = "55119XXXXXXXX"  # Número de quem vai receber (com código do país/área)
WA_TEMPLATE_NAME = "seu_template_de_alerta"  # Nome do modelo pré-aprovado
# -----------------------------------------------------------

app = Flask(__name__)

def send_to_whatsapp(alert_data):
    """
    Envia uma mensagem formatada para o WhatsApp usando um modelo.
    """
    
    # --- Processamento do Alerta (Exemplo) ---
    # Você precisa adaptar isso à estrutura REAL do JSON do CrowdStrike (depende do que você vai enviar no workflow, então se liga aqui também nos campos que você vai enviar)
    # Isto é apenas uma suposição de campos que podem existir.
    try:
        # Tenta extrair dados relevantes do JSON do CrowdStrike
        alert_name = alert_data.get('event_simpleName', 'N/A')
        hostname = alert_data.get('device', {}).get('hostname', 'Host Desconhecido')
        severity = alert_data.get('severity_name', 'Indefinida')

    except Exception as e:
        print(f"Erro ao processar JSON do CrowdStrike: {e}")
        alert_name = "Erro de Processamento"
        hostname = str(alert_data) # Envia o JSON bruto se falhar
        severity = "Alta"

    # URL da API de Mensagens do WhatsApp
    url = f"https{WA_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WA_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    # Estrutura da mensagem baseada em TEMPLATE
    # Assumindo que seu template 'seu_template_de_alerta' tenha 3 variáveis
    payload = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_WA_ID,
        "type": "template",
        "template": {
            "name": WA_TEMPLATE_NAME,
            "language": {
                "code": "pt_BR"  # Ou o código do seu template
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": alert_name
                        },
                        {
                            "type": "text",
                            "text": hostname
                        },
                        {
                            "type": "text",
                            "text": severity
                        }
                    ]
                }
            ]
        }
    }

    print(f"Enviando alerta para o WhatsApp: {alert_name} em {hostname}")
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Lança um erro se a requisição falhar (código 4xx ou 5xx)
        print(f"Resposta da API do WhatsApp: {response.status_code}")
        print(response.json())
        
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar para a API do WhatsApp: {e}")
        if e.response is not None:
            print(f"Detalhes do erro: {e.response.text}")

@app.route('/webhook', methods=['POST'])
def crowdstrike_webhook():
    """
    Recebe o webhook do CrowdStrike.
    """
    if request.is_json:
        data = request.get_json()
        
        # Imprime o alerta recebido no console (para debug)
        print("Alerta recebido do CrowdStrike:")
        print(json.dumps(data, indent=2))
        
        # Envia os dados para a função do WhatsApp
        send_to_whatsapp(data)
        
        return jsonify({"status": "sucesso", "message": "Alerta recebido"}), 200
    else:
        return jsonify({"status": "erro", "message": "Payload não é JSON"}), 400

if __name__ == '__main__':
    print("Iniciando servidor webhook na porta 48000...")
    # '0.0.0.0' torna o servidor acessível na rede (não apenas localhost) ou seja, fica rodando em bind 0.0.0.0 na 48000, mesmo que voce rode num container
    app.run(host='0.0.0.0', port=48000, debug=True)
