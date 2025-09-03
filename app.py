import json
import logging
import os
import io
import csv
import re
import time
import sqlite3
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from zoneinfo import ZoneInfo
from collections import defaultdict
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
import subprocess
import whois
from OpenSSL import crypto

import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    stream_with_context,
    request,
    redirect,
    url_for,
)
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Carrega variáveis de ambiente
load_dotenv()

# --- Configuração de Logging ---
LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler = RotatingFileHandler(os.path.join(LOG_DIR, 'dns_resolver.log'), maxBytes=10485760, backupCount=5)
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)
logger = logging.getLogger(__name__)

# --- Configuração da Sessão de Requests ---
def requests_retry_session(session=None):
    session = session or requests.Session()
    retry = Retry(total=5, backoff_factor=2, status_forcelist=(500, 502, 503, 504, 429))
    adapter = HTTPAdapter(max_retries=retry, pool_maxsize=100, pool_connections=100)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# --- Carregamento de Credenciais da API ---
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')
VAR_DOMINIO = os.getenv('VAR_DOMINIO')

if not API_KEY or not API_SECRET:
    logger.error("Variáveis de ambiente API_KEY ou API_SECRET não configuradas. As rotas de API podem não funcionar.")

def get_formatted_domains(domain_string):
    if not domain_string:
        return []
    domains = [d.strip() for d in domain_string.split(',') if d.strip()]
    return [f'*{d}*' for d in domains]

# --- Variável para Rate Limiting da API ---
last_update_time = None

# --- Funções de Banco de Dados ---
CERT_DATABASE = 'certificates.db'

def get_cert_db_connection():
    conn = sqlite3.connect(CERT_DATABASE, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_cert_db():
    with get_cert_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dominio TEXT UNIQUE,
                autoridade_certificadora TEXT,
                emitido_em TEXT,
                vence_em TEXT,
                email TEXT,
                last_scan_date TEXT,
                porta TEXT
            )
        """)
        conn.commit()
init_cert_db()

# --- Configuração de E-mail ---
SMTP_SERVER = os.getenv('SMTP_SERVER', '')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_LOGIN = os.getenv('SMTP_LOGIN', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', '')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', '')

def send_certificate_alert_email(recipient_email, subject, certificate_data):
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"CyberCERT Alerta <{SENDER_EMAIL}>"
        msg["To"] = recipient_email
        msg["Subject"] = subject

        html_template = f'''
        <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }}
                    .header {{ background-color: #007bff; color: #ffffff; padding: 15px 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 24px; }}
                    .content {{ padding: 20px; }}
                    .content p {{ line-height: 1.6; color: #333333; }}
                    .certificate-details {{ background-color: #f9f9f9; border-left: 5px solid #007bff; padding: 15px; margin-top: 20px; border-radius: 4px; }}
                    .certificate-details strong {{ color: #007bff; }}
                    .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #888888; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>ALERTA DE VENCIMENTO DO CERTIFICADO</h1>
                    </div>
                    <div class="content">
                        <p>Olá,</p>
                        <p>Este é um alerta automático informando que o seguinte certificado está próximo do vencimento ou já venceu:</p>
                        <div class="certificate-details">
                            <p><strong>Domínio:</strong> {certificate_data.get('dominio', 'N/A')}</p>
                            <p><strong>Certificado emitido em:</strong> {certificate_data.get('emitido_em', 'N/A')}</p>
                            <p><strong>Certificado vence em:</strong> {certificate_data.get('vence_em', 'N/A')}</p>
                            <p><strong>E-mail responsável:</strong> {certificate_data.get('email', 'N/A')}</p>
                            <p><strong>Porta do certificado:</strong> {certificate_data.get('porta', 'N/A')}</p>
                            <p><strong>Autoridade Certificadora:</strong> {certificate_data.get('autoridade_certificadora', 'N/A')}</p>
                        </div>
                        <p>Por favor, tome as medidas necessárias para renovar o certificado.</p>
                        <p>Qualquer dúvida: wallace.palves@rededor.com.br</p>
                    </div>
                    <div class="footer">
                        <p>Este e-mail foi enviado automaticamente. Por favor, não responda.</p>
                    </div>
                </div>
            </body>
        </html>
        '''
        part1 = MIMEText(html_template, "html")
        msg.attach(part1)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_LOGIN, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        logger.info(f"E-mail de alerta enviado para {recipient_email} para o domínio {certificate_data.get('dominio')}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail de alerta para {recipient_email} para o domínio {certificate_data.get('dominio')}: {e}")
        return False

# --- Lógica da API CrowdStrike ---

# --- Lógica da API CrowdStrike ---
cloud = 'https://api.crowdstrike.com'
id_cred = os.getenv('CROWDSTRIKE_CLIENT_ID')
secret = os.getenv('CROWDSTRIKE_CLIENT_SECRET')

def TokenAuth():
    if not id_cred or not secret:
        logger.error("CROWDSTRIKE_CLIENT_ID ou CROWDSTRIKE_CLIENT_SECRET não configurados no .env")
        return None
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'client_id': id_cred, 'client_secret': secret}
    try:
        response = requests_retry_session().post(f'{cloud}/oauth2/token', headers=headers, data=data, timeout=15)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        logger.error(f"Erro ao obter token: {e}")
        return None

def run_crowdstrike_query(token, session, start_time, end_time):
    formatted_domains = get_formatted_domains(VAR_DOMINIO)
    domain_values_str = ", ".join(formatted_domains)
    query = f'''#event_simpleName="DnsRequest"
| in(DomainName, values=[{domain_values_str}])
| groupBy(DomainName, limit=200000)
| table(DomainName, limit=200000)'''

    payload = {"queryString": query, "isLive": False, "start": start_time, "end": end_time, "timeZone": "America/Sao_Paulo"}
    headers = {'accept': 'application/json', 'authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    api_url_jobs = f"{cloud}/humio/api/v1/repositories/search-all/queryjobs"
    
    try:
        response = session.post(api_url_jobs, headers=headers, json=payload, timeout=45)
        
        if response.status_code == 401:
            logger.warning("Token expirado para consulta. Tentando obter um novo token.")
            new_token = TokenAuth()
            if new_token:
                headers['authorization'] = f'Bearer {new_token}'
                response = session.post(api_url_jobs, headers=headers, json=payload, timeout=45)
            else:
                logger.error("Não foi possível obter um novo token. Abortando consulta.")
                response.raise_for_status()

        response.raise_for_status()
        
        job_id = response.json().get('id')
        if not job_id: 
            logger.error("Falha ao criar o job de consulta.")
            return []
        
        api_url_job_status = f"{api_url_jobs}/{job_id}"
        for _ in range(180):
            time.sleep(10)
            status_response = session.get(api_url_job_status, headers=headers, timeout=30)
            if status_response.status_code == 200 and status_response.json().get('done'):
                logger.info("Job de consulta concluído. Coletando eventos.")
                events = status_response.json().get('events', [])
                
                # Salvar resultados brutos
                with open('brutoconsole.txt', 'w') as f:
                    for event in events:
                        f.write(f"{event.get('DomainName', '')}\n")
                
                return events
        
        logger.warning("Job demorou mais de 30 minutos. Cancelando.")
        session.delete(api_url_job_status, headers=headers)
        return []
        
    except Exception as e:
        logger.error(f"Erro na consulta CrowdStrike: {e}")
        return []

# --- Lógica de Scan de Certificados e Whois ---
def get_certificate_info(domain, port):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    try:
        with socket.create_connection((domain, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert_der = ssock.getpeercert(True)
                cert = crypto.load_certificate(crypto.FILETYPE_ASN1, cert_der)
                
                issuer = cert.get_issuer()
                issuer_str = ", ".join([f"{name.decode()}={value.decode()}" for name, value in issuer.get_components()])
                
                not_before = datetime.strptime(cert.get_notBefore().decode('ascii'), '%Y%m%d%H%M%SZ')
                not_after = datetime.strptime(cert.get_notAfter().decode('ascii'), '%Y%m%d%H%M%SZ')

                return {
                    "autoridade_certificadora": issuer_str,
                    "emitido_em": not_before.strftime('%d/%m/%Y'),
                    "vence_em": not_after.strftime('%d/%m/%Y')
                }, port
    except Exception:
        return None

def get_whois_info(domain):
    retries = 3
    for i in range(retries):
        try:
            w = whois.whois(domain) # Usa timeout padrão do python-whois
            email = w.email[0] if isinstance(w.email, list) and w.email else (w.email if isinstance(w.email, str) else "")
            return {"email": email if email else "N/A"}
        except Exception as e:
            logger.warning(f"Tentativa {i+1}/{retries} de WHOIS (python-whois) para {domain} falhou: {e}")
            time.sleep(2 ** i) # Backoff exponencial
    logger.error(f"WHOIS (python-whois) para {domain} falhou após {retries} tentativas.")
    return {"email": "N/A"}

def get_system_whois_email(domain):
    try:
        command = f"/usr/bin/whois {domain}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60) # 60s timeout
        
        if result.returncode == 0:
            output = result.stdout
            # Tenta encontrar o e-mail específico do campo 'e-mail:'
            specific_email_match = re.search(r'e-mail:\s*([\w\.-]+@[\w\.-]+)', output, re.IGNORECASE)
            if specific_email_match:
                return specific_email_match.group(1)
            
            # Se não encontrar o específico, tenta o padrão genérico (fallback)
            email_matches = re.findall(r'[\w\.-]+@[\w\.-]+', output)
            if email_matches:
                unique_emails = list(set(email_matches))
                # Prioriza e-mails que contenham 'rededor.com.br' ou 'rededorsaoluiz.com.br'
                rededor_emails = [e for e in unique_emails if 'rededor.com.br' in e or 'rededorsaoluiz.com.br' in e]
                if redor_emails:
                    return ", ".join(rededor_emails)
                return ", ".join(unique_emails)
        
        logger.warning(f"Nenhum e-mail encontrado via whois do sistema para {domain} ou comando falhou.")
        return "N/A"
    except subprocess.TimeoutExpired:
        logger.warning(f"Comando whois do sistema para {domain} excedeu o tempo limite de 60s.")
        return "N/A"
    except Exception as e:
        logger.error(f"Erro ao executar whois do sistema para {domain}: {e}")
        return "N/A"

def check_port_responsiveness(domain, port, timeout=1):
    try:
        with socket.create_connection((domain, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

def run_subfinder_and_save_output(domains_to_scan):
    if not domains_to_scan:
        logger.warning("Nenhum domínio fornecido para o subfinder.")
        return

    all_subdomains = set()
    for domain in domains_to_scan.split(','):
        domain = domain.strip()
        if not domain:
            continue
        
        logger.info(f"Executando subfinder para o domínio: {domain}")
        try:
            command = f"./subfinder -d {domain}"
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300,
                cwd="./subfinder"
            )

            if result.returncode == 0:
                subdomains = result.stdout.strip().split('\n')
                for sub in subdomains:
                    if sub.strip():
                        all_subdomains.add(sub.strip())
                logger.info(f"Subfinder para {domain} concluído. Encontrados {len(subdomains)} subdomínios.")
            else:
                logger.error(f"Subfinder para {domain} falhou com erro: {result.stderr}")
        except subprocess.TimeoutExpired:
            logger.error(f"Subfinder para {domain} excedeu o tempo limite de 5 minutos.")
        except Exception as e:
            logger.error(f"Erro ao executar subfinder para {domain}: {e}")

    if all_subdomains:
        try:
            with open('dns-manual.txt', 'w') as f:
                for sub in sorted(list(all_subdomains)):
                    f.write(f"{sub}\n")
            logger.info(f"Subdomínios do subfinder salvos em dns-manual.txt. Total: {len(all_subdomains)}")
        except Exception as e:
            logger.error(f"Erro ao salvar subdomínios em dns-manual.txt: {e}")
    else:
        logger.info("Nenhum subdomínio encontrado pelo subfinder para salvar.")

def scan_domain(domain):
    ports = [443, 636, 465, 995, 993, 8443, 3389, 1813, 1194, 990, 5986]

    
    # Verifica a conectividade das portas em paralelo
    responsive_ports = []
    with ThreadPoolExecutor(max_workers=len(ports)) as executor:
        port_futures = {executor.submit(check_port_responsiveness, domain, port): port for port in ports}
        for future in port_futures:
            if future.result():
                responsive_ports.append(port_futures[future])
    
    if not responsive_ports:
        # Se nenhuma porta respondeu, descarta o domínio imediatamente
        return None

    cert_info = None
    found_port = "N/A"
    for port in responsive_ports:
        cert_result = get_certificate_info(domain, port)
        if cert_result:
            cert_data, p = cert_result
            cert_info = cert_data
            found_port = str(p)
            break
    
    if not cert_info:
        # Se nenhum certificado foi encontrado em nenhuma porta responsiva, descarta o domínio
        return None

    whois_info = get_whois_info(domain)
    
    result = {
        "dominio": domain,
        **cert_info,
        **whois_info,
        "last_scan_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "porta": found_port
    }

    # Verifica se todos os campos relevantes são "N/A" ou vazios
    if all(result.get(field, "N/A") in ["N/A", ""] for field in [
        "autoridade_certificadora", "emitido_em", "vence_em", "email"
    ]):
        return None # Descarta se não houver informações relevantes

    return result

def update_cert_database(scan_results):
    with get_cert_db_connection() as conn:
        cursor = conn.cursor()
        for result in scan_results:
            cursor.execute("""
                INSERT INTO certificates (dominio, autoridade_certificadora, emitido_em, vence_em, owner, email, last_scan_date)
                VALUES (:dominio, :autoridade_certificadora, :emitido_em, :vence_em, :owner, :email, :last_scan_date)
                ON CONFLICT(dominio) DO UPDATE SET
                autoridade_certificadora = excluded.autoridade_certificadora,
                emitido_em = excluded.emitido_em,
                vence_em = excluded.vence_em,
                owner = excluded.owner,
                email = excluded.email,
                last_scan_date = excluded.last_scan_date;
            """, result)
        conn.commit()

def buscar_dados_certificados_do_db():
    with get_cert_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, dominio, autoridade_certificadora, emitido_em, vence_em, email, last_scan_date, porta FROM certificates ORDER BY dominio ASC")
        rows = cursor.fetchall()
        cert_data_with_color = []
        for row in rows:
            item = dict(row)
            vence_em_str = item.get('vence_em')
            if vence_em_str and vence_em_str != "N/A":
                try:
                    vence_em_date = datetime.strptime(vence_em_str, '%d/%m/%Y').date() # Apenas a data
                    hoje = datetime.now().date()
                    
                    # Calcula a diferença em meses de forma mais precisa
                    diferenca_dias = (vence_em_date - hoje).days
                    diferenca_meses = diferenca_dias / 30.44 # Média de dias por mês

                    if diferenca_meses >= 3:
                        item['status_color'] = 'green'
                    elif diferenca_meses >= 2:
                        item['status_color'] = 'orange'
                    elif diferenca_meses >= 1:
                        item['status_color'] = 'red'
                    else:
                        item['status_color'] = 'red' # Vencido ou faltando menos de 1 mês
                except ValueError:
                    item['status_color'] = 'black' # Erro na data, cor padrão
            else:
                item['status_color'] = 'black' # Sem data, cor padrão
            cert_data_with_color.append(item)
        return cert_data_with_color

# --- Rotas Flask Protegidas (Interface Web) ---
@app.route('/')
def index():
    
    cert_data = buscar_dados_certificados_do_db()
    return render_template('index.html', cert_data=cert_data)

@app.route('/stream-refresh')
def stream_refresh():
    
    def generate():
        logger.info("Iniciando stream-refresh.")
        token = TokenAuth()
        if not token:
            logger.error("Falha na autenticação com a API CrowdStrike. Token não obtido.")
            yield f"event: error\ndata: Falha na autenticação com a API CrowdStrike\n\n"
            return
        logger.info("Token da API CrowdStrike obtido com sucesso.")
        
        yield "event: message\ndata: Executando subfinder para encontrar subdomínios...\n\n"
        run_subfinder_and_save_output(VAR_DOMINIO)
        
        end_time = datetime.now(ZoneInfo("America/Sao_Paulo"))
        start_time = end_time - timedelta(days=7)
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)

        yield "event: message\ndata: Buscando domínios na API CrowdStrike...\n\n"
        logger.info(f"Iniciando consulta CrowdStrike para o período: {start_time} a {end_time}")
        with requests_retry_session() as session:
            events = run_crowdstrike_query(token, session, start_ms, end_ms)
        logger.info(f"Consulta CrowdStrike concluída. Eventos encontrados: {len(events) if events else 0}")

        if events:
            all_domains_crowdstrike = list(set(event.get('DomainName') for event in events if event.get('DomainName')))
            
            manual_domains = []
            try:
                with open('dns-manual.txt', 'r') as f:
                    manual_domains = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                logger.warning("Arquivo dns-manual.txt não encontrado. Nenhum domínio manual será processado.")
            except Exception as e:
                logger.error(f"Erro ao ler dns-manual.txt: {e}")

            combined_domains = list(set(all_domains_crowdstrike + manual_domains))
            # Filtrar domínios inválidos (vazios ou começando com '.')
            domains = sorted([d for d in combined_domains if d and not d.startswith('.')])
            
            if not domains:
                yield "event: message\ndata: Nenhum domínio válido encontrado para escaneamento.\n\n"
                yield "event: finished\ndata: Atualização concluída. A página será recarregada.\n\n"
                return

            yield f"event: message\ndata: {len(domains)} domínios válidos encontrados. Iniciando escaneamento...\n\n"
            
            with get_cert_db_connection() as conn:
                cursor = conn.cursor()
                with ThreadPoolExecutor(max_workers=100) as executor:
                    futures = {executor.submit(scan_domain, domain): domain for domain in domains}
                    for i, future in enumerate(futures):
                        domain = futures[future]
                        try:
                            scan_result = future.result()
                            if scan_result: # Só processa se o resultado não for None (domínio não descartado)
                                # Adiciona o status_color ao scan_result para o frontend
                                vence_em_str = scan_result.get('vence_em')
                                if vence_em_str and vence_em_str != "N/A":
                                    try:
                                        vence_em_date = datetime.strptime(vence_em_str, '%d/%m/%Y').date()
                                        hoje = datetime.now().date()
                                        diferenca_dias = (vence_em_date - hoje).days
                                        diferenca_meses = diferenca_dias / 30.44

                                        if diferenca_meses >= 3:
                                            scan_result['status_color'] = 'green'
                                        elif diferenca_meses >= 2:
                                            scan_result['status_color'] = 'orange'
                                        elif diferenca_meses >= 1:
                                            scan_result['status_color'] = 'red'
                                        else:
                                            scan_result['status_color'] = 'red'
                                    except ValueError:
                                        scan_result['status_color'] = 'black'
                                else:
                                    scan_result['status_color'] = 'black'

                                cursor.execute("""
                                    INSERT INTO certificates (dominio, emitido_em, vence_em, email, last_scan_date, porta, autoridade_certificadora)
                                    VALUES (:dominio, :emitido_em, :vence_em, :email, :last_scan_date, :porta, :autoridade_certificadora)
                                    ON CONFLICT(dominio) DO UPDATE SET
                                    emitido_em = excluded.emitido_em,
                                    vence_em = excluded.vence_em,
                                    email = excluded.email,
                                    last_scan_date = excluded.last_scan_date,
                                    porta = excluded.porta,
                                    autoridade_certificadora = excluded.autoridade_certificadora;
                                """, scan_result)
                                conn.commit()
                                progress = (i + 1) / len(domains) * 100
                                yield f"event: progress\ndata: {json.dumps({'progress': progress, 'domain': domain, 'data': scan_result})}\n\n"

                            else:
                                # Se o domínio foi descartado, ainda atualiza o progresso, mas sem dados
                                progress = (i + 1) / len(domains) * 100
                                yield f"event: progress\ndata: {json.dumps({'progress': progress, 'domain': domain, 'discarded': True})}\n\n"
                        except Exception as e:
                            logger.error(f"Erro ao escanear ou salvar domínio {domain}: {e}")
                            progress = (i + 1) / len(domains) * 100
                            yield f"event: progress\ndata: {json.dumps({'progress': progress, 'domain': domain, 'error': str(e)})}""\n\n"

            yield "event: message\ndata: Escaneamento concluído. Buscando e-mails WHOIS do sistema...\n\n"
            
            # Busca e-mails WHOIS do sistema em paralelo
            with ThreadPoolExecutor(max_workers=100) as executor:
                email_futures = {executor.submit(get_system_whois_email, domain): domain for domain in domains}
                for future in email_futures:
                    domain = email_futures[future]
                    system_email = future.result()
                    if system_email and system_email != "N/A":
                        # Atualiza o banco de dados com o e-mail do WHOIS do sistema
                        cursor.execute("""
                            UPDATE certificates SET email = ? WHERE dominio = ?;
                        """, (system_email, domain))
                        conn.commit()
                        yield f"event: email_update\ndata: {json.dumps({'domain': domain, 'email': system_email})}\n\n"

            yield "event: message\ndata: Atualização de e-mails WHOIS concluída. A página será recarregada.\n\n"
        else:
            yield "event: message\ndata: Nenhum domínio encontrado no período.\n\n"

        yield "event: finished\ndata: Atualização concluída. A página será recarregada.\n\n"
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/export-csv')
def export_csv():
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Dominio', 'Emitido Em', 'Vence Em', 'Email', 'Porta', 'Autoridade Certificadora', 'Último Scan'])
    
    cert_data = buscar_dados_certificados_do_db()
    for item in cert_data:
        writer.writerow([
            item.get('dominio'), item.get('emitido_em'),
            item.get('vence_em'), item.get('email'), item.get('porta'), item.get('autoridade_certificadora'), item.get('last_scan_date')
        ])
        
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=relatorio_certificados.csv"})

@app.route('/alertar-vencimentos', methods=['POST'])
def alertar_vencimentos():
    logger.info("Iniciando processo de alerta de vencimentos.")
    
    certificados_a_vencer = []
    with get_cert_db_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, dominio, autoridade_certificadora, emitido_em, vence_em, email, last_scan_date, porta FROM certificates")
        rows = cursor.fetchall()
        
        hoje = datetime.now().date()
        
        for row in rows:
            item = dict(row)
            vence_em_str = item.get('vence_em')
            if vence_em_str and vence_em_str != "N/A":
                try:
                    vence_em_date = datetime.strptime(vence_em_str, '%d/%m/%Y').date()
                    diferenca_dias = (vence_em_date - hoje).days
                    diferenca_meses = diferenca_dias / 30.44

                    if diferenca_meses <= 3: # 3 meses ou menos
                        certificados_a_vencer.append(item)
                except ValueError:
                    logger.warning(f"Data de vencimento inválida para o domínio {item.get('dominio')}: {vence_em_str}")

    if not certificados_a_vencer:
        logger.info("Nenhum certificado encontrado para alertar (vencimento em 3 meses ou menos).")
        return jsonify({"status": "success", "message": "Nenhum certificado encontrado para alertar."})

    logger.info(f"Encontrados {len(certificados_a_vencer)} certificados a vencer em 3 meses ou menos. Iniciando envio de e-mails.")
    
    # Envia e-mails com delay
    for i, cert_data in enumerate(certificados_a_vencer):
        if i > 0: # Não atrasa o primeiro e-mail
            time.sleep(10) # Atraso de 10 segundos entre os e-mails
        
        success = send_certificate_alert_email(RECIPIENT_EMAIL, "Certificado a vencer", cert_data)
        if not success:
            logger.error(f"Falha ao enviar e-mail para o domínio {cert_data.get('dominio')}")

    logger.info("Processo de alerta de vencimentos concluído.")
    return jsonify({"status": "success", "message": f"Alertas enviados para {len(certificados_a_vencer)} certificados."})


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
