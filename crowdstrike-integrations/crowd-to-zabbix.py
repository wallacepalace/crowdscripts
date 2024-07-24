# Don't forget to install "pip install pyzabbix"
# Change vars:
# If console us-1, us-2, gov, change in "auth_url"
# client_id, client_secret
# -----------------------------------------
# change down there
#    CLIENT_ID = 'your-client-id'
#    CLIENT_SECRET = 'your-client-secret'
#    ZABBIX_SERVER = 'your-zabbix-server'
#    ZABBIX_HOST = 'your-zabbix-host'
#    ZABBIX_KEY = 'crowdstrike.data'

import requests
import json
from pyzabbix import ZabbixAPI, ZabbixMetric, ZabbixSender

# Função para obter o token de autenticação
def get_auth_token(client_id, client_secret):
    auth_url = 'https://api.crowdstrike.com/oauth2/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(auth_url, headers=headers, data=payload)
    if response.status_code == 201 or response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to obtain auth token: " + response.text)

# Função para obter dados do CrowdStrike
def get_crowdstrike_data(token):
    url = 'https://api.crowdstrike.com/some/endpoint'  # Substitua com o endpoint correto
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Função para enviar dados para o Zabbix
def send_to_zabbix(zabbix_server, zabbix_host, key, value):
    zbx = ZabbixSender(zabbix_server=zabbix_server)
    metrics = [ZabbixMetric(zabbix_host, key, value)]
    result = zbx.send(metrics)
    return result

if __name__ == "__main__":
    CLIENT_ID = 'your-client-id'
    CLIENT_SECRET = 'your-client-secret'
    ZABBIX_SERVER = 'your-zabbix-server'
    ZABBIX_HOST = 'your-zabbix-host'
    ZABBIX_KEY = 'crowdstrike.data'

    try:
        # Obter token de autenticação
        token = get_auth_token(CLIENT_ID, CLIENT_SECRET)
        
        # Obter dados do CrowdStrike
        data = get_crowdstrike_data(token)
        
        # Enviar dados para o Zabbix
        response = send_to_zabbix(ZABBIX_SERVER, ZABBIX_HOST, ZABBIX_KEY, json.dumps(data))
        print("Data sent to Zabbix:", response)
    except Exception as e:
        print("Error:", e)
