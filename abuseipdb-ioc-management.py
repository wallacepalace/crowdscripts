# Puxa os IPs maliciosos do AbuseIPDB, salva num arquivo e abastece o IOC Management do CrowdStrike
# Obs: coleta sempre de 2 em 2 horas no AbuseIPDB, é o tempo de corte... além disso, se tiverem IPs duplicados, tem a função de remover duplicados
# Não esqueça de mudar de US-1 para US-2 ou GOV para a chamada da API do CrowdStrike, dependendo da sua console
# Wallace Alves

import requests
import os
from datetime import datetime, timedelta

# Configurações da API do AbuseIPDB
ABUSEIPDB_API_KEY = 'sua_chave_api_abuseipdb_aqui'
ABUSEIPDB_URL = 'https://api.abuseipdb.com/api/v2/check-block'
headers_abuseipdb = {
    'Accept': 'application/json',
    'Key': ABUSEIPDB_API_KEY
}

# Configurações da API do Falcon CrowdStrike
CROWDSTRIKE_API_KEY = 'sua_chave_api_crowdstrike_aqui'
CROWDSTRIKE_URL = 'https://api.crowdstrike.com/indicators/entities/iocs/v1'
headers_crowdstrike = {
    'Authorization': f'Bearer {CROWDSTRIKE_API_KEY}',
    'Content-Type': 'application/json'
}

# Coletar IPs do AbuseIPDB
def coletar_ips_abuseipdb():
    dois_horas_atras = datetime.now() - timedelta(hours=2)
    params = {
        'confidenceMinimum': 100,
        'since': dois_horas_atras.strftime('%Y-%m-%dT%H:%M:%S')
    }
    response = requests.get(ABUSEIPDB_URL, headers=headers_abuseipdb, params=params)
    if response.status_code == 200:
        return set(ip['ipAddress'] for ip in response.json()['data'])
    else:
        print('Erro ao buscar IPs no AbuseIPDB')
        return set()

# Salvar IPs em arquivo
def salvar_ips_arquivo(ips):
    with open('ips-maliciosos.txt', 'w') as arquivo:
        for ip in ips:
            arquivo.write(f"{ip}\n")

# Enviar IPs para Falcon CrowdStrike
def enviar_ips_crowdstrike(ips):
    iocs = [{'type': 'ip', 'value': ip, 'policy': 'detect'} for ip in ips]
    response = requests.post(CROWDSTRIKE_URL, headers=headers_crowdstrike, json=iocs)
    if response.status_code != 200:
        print('Erro ao enviar IPs para CrowdStrike')

# Executar script
ips_maliciosos = coletar_ips_abuseipdb()
if ips_maliciosos:
    salvar_ips_arquivo(ips_maliciosos)
    enviar_ips_crowdstrike(ips_maliciosos)
    os.remove('ips-maliciosos.txt')
else:
    print('Nenhum IP malicioso encontrado nas últimas 2 horas.')
