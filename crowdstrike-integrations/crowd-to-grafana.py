# ------------ README -------------------------------------
# Não esquece de instalar os "pip install flask requests"
# Don't forget to install "pip install flask requests"
# Change vars:
# If console us-1, us-2, gov, change in "auth_url"
# client_id, client_secret
# -----------------------------------------
# Add Simple JSON Data Source in Grafana:
# Go to Settings > Data Sources > Add Data Source.
# Select "Simple JSON".
# Configure the URL to point to the Flask server (http://<your-server-ip>:5000).
# ---------------------------------------------------------

import requests
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

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

@app.route('/search', methods=['POST'])
def search():
    # Implementação necessária para o Grafana Simple JSON Datasource
    return jsonify([])

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.json

        CLIENT_ID = 'your-client-id'
        CLIENT_SECRET = 'your-client-secret'

        token = get_auth_token(CLIENT_ID, CLIENT_SECRET)
        crowdstrike_data = get_crowdstrike_data(token)

        # Preparar dados para o Grafana
        results = []
        for target in data['targets']:
            datapoints = []
            # Adicione lógica para transformar `crowdstrike_data` em datapoints do Grafana
            # Por exemplo, se `crowdstrike_data` tiver uma chave 'timestamp' e 'value'
            for entry in crowdstrike_data:
                timestamp = entry['timestamp']  # Substitua pela chave correta
                value = entry['value']  # Substitua pela chave correta
                datapoints.append([value, timestamp])

            results.append({
                'target': target['target'],
                'datapoints': datapoints
            })

        return jsonify(results)

    except Exception as e:
        print("Error:", e)
        return jsonify([])

@app.route('/annotations', methods=['POST'])
def annotations():
    # Implementação necessária para o Grafana Simple JSON Datasource
    return jsonify([])

@app.route('/tag-keys', methods=['POST'])
def tag_keys():
    # Implementação necessária para o Grafana Simple JSON Datasource
    return jsonify([])

@app.route('/tag-values', methods=['POST'])
def tag_values():
    # Implementação necessária para o Grafana Simple JSON Datasource
    return jsonify([])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
