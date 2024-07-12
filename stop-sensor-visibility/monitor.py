import os
import subprocess
import sys
import time
import base64
import json
import requests
import threading

# Verifica se está rodando dentro de uma sessão screen
if "STY" not in os.environ:
    # Nome da sessão do screen
    SESSION_NAME = "vim"
    # Caminho completo para o script monitor.py
    SCRIPT_PATH = os.path.abspath(__file__)

    # Matar a sessão screen existente, se houver
    subprocess.run(f"screen -S {SESSION_NAME} -X quit", shell=True, stderr=subprocess.DEVNULL)

    # Comando para iniciar uma nova sessão screen e rodar o script
    command = f"screen -dmS {SESSION_NAME} bash -c 'python3 {SCRIPT_PATH}; exec bash'"
    subprocess.run(command, shell=True)
    print(f"Sessão screen '{SESSION_NAME}' iniciada. Para se conectar, use 'screen -r {SESSION_NAME}'")
    sys.exit(0)

# Código original do monitor.py começa aqui

# Webhook URL
WEBHOOK_URL = "LINK-DO-WEBHOOK"

# Serviço alvo
SERVICE_NAME = "falcon-sensor"

# Regras do auditd em base64
AUDIT_RULES_BASE64 = "LXcgL2JpbiAtcCB4IC1rIGV4ZWNfY29tbWFuZHMKLXcgL3Vzci9iaW4vc3lzdGVtY3RsIC1wIHggLWsgZmFsY29uX3NlbnNvcl9jaGFuZ2U="

def install_prerequisites():
    os_info = ""
    if os.path.isfile("/etc/os-release"):
        with open("/etc/os-release") as f:
            os_info = f.read()
    elif os.path.isfile("/etc/redhat-release"):
        with open("/etc/redhat-release") as f:
            os_info = f.read()
    else:
        os_info = os.uname().sysname

    print(f"Detectado sistema operacional: {os_info}")

    if "Ubuntu" in os_info or "Debian" in os_info:
        subprocess.run(["apt-get", "install", "-y", "auditd", "curl", "python3-dbus", "python3-systemd", "screen"])
    elif "CentOS" in os_info or "Red Hat" in os_info or "Fedora" in os_info:
        subprocess.run(["yum", "install", "-y", "audit", "curl", "dbus-python", "python3-systemd", "screen"])
    else:
        print("Sistema operacional não suportado para instalação automática de pré-requisitos.")
        exit(1)

def add_audit_rules():
    rules = base64.b64decode(AUDIT_RULES_BASE64).decode("utf-8")
    with open("/etc/audit/rules.d/audit.rules", "a") as f:
        f.write(rules)
    subprocess.run(["systemctl", "restart", "auditd"])

def get_user_commands():
    try:
        # Obtém a lista de usuários conectados via SSH
        result = subprocess.run(["who"], stdout=subprocess.PIPE)
        users = set()
        for line in result.stdout.decode('utf-8').splitlines():
            parts = line.split()
            if len(parts) > 0:
                users.add(parts[0])

        # Inclui o usuário root na lista de usuários
        users.add("root")

        # Captura os últimos 20 comandos do arquivo .bash_history de cada usuário
        all_commands = ""
        for user in users:
            history_file = f"/root/.bash_history" if user == "root" else f"/home/{user}/.bash_history"
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history_lines = f.readlines()
                last_commands = history_lines[-20:]
                user_commands = ''.join(last_commands)
                all_commands += f"**User {user}**:\n\n{user_commands}\n\n"
            else:
                all_commands += f"**User {user}**: Histórico não encontrado.\n\n"

        return all_commands.strip()
    except Exception as e:
        return f"Não foi possível obter o histórico de comandos. Erro: {str(e)}"

def get_active_user():
    try:
        result = subprocess.run(["ps", "aux"], stdout=subprocess.PIPE)
        for line in result.stdout.decode('utf-8').splitlines():
            if "sshd:" in line and "[priv]" in line:
                parts = line.split()
                user_field = next(part for part in parts if "sshd:" in part)
                user = user_field.split(":")[1]
                return user
    except Exception as e:
        print(f"Erro ao obter o usuário ativo. Erro: {str(e)}")
    return "unknown"

def send_notification(user, command):
    timestamp = time.strftime("%H:%M:%S - %d/%m/%Y")
    hostname = os.uname().nodename
    ip = subprocess.check_output("hostname -I | awk '{print $1}'", shell=True).decode().strip()
    domain = subprocess.check_output("hostname -d", shell=True).decode().strip()
    active_sessions = subprocess.check_output("who", shell=True).decode().strip().replace("\n", "  \n")
    user_commands = get_user_commands()

    message_text = (
        f"**Hostname:** {hostname}  \n\n"
        f"**User:** {user}  \n\n"
        f"**Command:** {command}  \n\n"
        f"**Timestamp:** {timestamp}  \n\n"
        f"**IP:** {ip}  \n\n"
        f"**Domain:** {domain}  \n\n"
        f"**ActiveSessions:** {active_sessions}  \n\n"
        f"**Last 20 Commands:**  \n\n{user_commands}"
    )

    message = {
        "title": "Falcon Sensor Service Alert",
        "text": message_text
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(message))

    # Debugging output
    if response.status_code == 200:
        print(f"Notification sent successfully: {message}")
    else:
        print(f"Failed to send notification: {response.status_code} {response.text}")
        print(f"Request payload: {json.dumps(message)}")
        print(f"Response: {response.text}")

def restart_service():
    subprocess.run(["systemctl", "start", SERVICE_NAME])

def ensure_service_running():
    while True:
        subprocess.run(["systemctl", "start", SERVICE_NAME])
        time.sleep(20)

def enable_service():
    subprocess.run(["systemctl", "enable", SERVICE_NAME])
    restart_service()

def kill_user_sessions(user):
    try:
        # Obtém os PIDs das sessões SSH do usuário
        result = subprocess.run(["pgrep", "-u", user, "sshd"], stdout=subprocess.PIPE)
        pids = result.stdout.decode().strip().split()
        for pid in pids:
            subprocess.run(["kill", "-9", pid])
    except Exception as e:
        print(f"Não foi possível matar as sessões SSH do usuário {user}. Erro: {str(e)}")

def monitor_service():
    print(f"Monitoring {SERVICE_NAME} service...")

    while True:
        result = subprocess.run(
            ["journalctl", "-u", f"{SERVICE_NAME}.service", "--since", "5 seconds ago", "--no-pager"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.stdout:
            logs = result.stdout.decode('utf-8')
            if "exited with status 15" in logs or "Deactivated successfully" in logs or "disabled" in logs:
                print(f"Detected: {logs}")
                user = get_active_user()
                command = logs
                # Derrubar sessões SSH do usuário
                if user != "unknown":
                    kill_user_sessions(user)
                send_notification(user, command)
                time.sleep(15)
                enable_service()

        time.sleep(5)

def create_service_file():
    service_content = """[Unit]
Description=Vim text editor service
After=network.target

[Service]
ExecStart=/usr/bin/screen -dmS monitor_session /usr/bin/python3 {script_path}
ExecStop=/usr/bin/screen -S monitor_session -X quit
Restart=always
RestartSec=10
User=root
Group=root

[Install]
WantedBy=multi-user.target
""".format(script_path=os.path.abspath(__file__))

    with open("/etc/systemd/system/vim.service", "w") as service_file:
        service_file.write(service_content)

    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", "vim.service"])
    subprocess.run(["systemctl", "start", "vim.service"])

if __name__ == "__main__":
    install_prerequisites()
    add_audit_rules()
    create_service_file()
    monitor_service_thread = threading.Thread(target=monitor_service)
    ensure_service_running_thread = threading.Thread(target=ensure_service_running)
    monitor_service_thread.start()
    ensure_service_running_thread.start()
    monitor_service_thread.join()
    ensure_service_running_thread.join()
