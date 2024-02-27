# Integração OTX + CrowdStrike IOC Management + JIRA
# Wallace Alves

import requests

otx_api_key = 'api do OTX'
otx_headers = {'X-OTX-API-KEY': otx_api_key}
otx_url = 'https://otx.alienvault.com/api/v1/indicators/file/'

falcon_client_id = 'ID da API do claudinho'
falcon_client_secret = 'Secret da API do claudinho'
falcon_auth_url = 'https://api.crowdstrike.com/oauth2/token'

### Webhook do JIRA
jira_webhook_url = 'coloca a URL do webhook aqui'

### Busca no OTX as hashes e salva num arquivo

def fetch_and_save_malicious_hashes():
    malicious_hashes = ['HASH_SHA256_1', 'HASH_SHA256_2']
    with open('otx-maliciosos.txt', 'w') as f:
        for hash in malicious_hashes:
            f.write(f"{hash}\n")

### Sobe as hashes pro claudinho
            
def upload_hashes_to_crowdstrike():
    auth_response = requests.post(falcon_auth_url, data={'client_id': falcon_client_id, 'client_secret': falcon_client_secret})
    auth_token = auth_response.json().get('access_token')
    headers = {'Authorization': f'Bearer {auth_token}'}

    with open('otx-maliciosos.txt', 'r') as f:
        hashes = [line.strip() for line in f.readlines()]

    for file_hash in hashes:
        upload_url = 'https://api.crowdstrike.com/indicators/entities/iocs/v1'
        payload = {
            'action': 'detect_only',
            'platforms': ['windows', 'mac', 'linux'],
            'severity': 'high',
            'type': 'sha256',
            'value': file_hash,
        }
        response = requests.post(upload_url, headers=headers, json=payload)
        print(f"Upload response for {file_hash}: {response.status_code}")

### Cria a issue no JIRA, subindo as hashes que estão no arquivo
        
def create_jira_issue():
    with open('otx-maliciosos.txt', 'r') as f:
        hashes = f.read()

    payload = {
        "title": "Hashes maliciosas OTX adicionadas com sucesso",
        "description": f"As seguintes hashes foram adicionadas:\n{hashes}"
    }

    response = requests.post(jira_webhook_url, json=payload)
    print(f"Jira webhook response: {response.status_code}")

fetch_and_save_malicious_hashes()
upload_hashes_to_crowdstrike()
create_jira_issue()
