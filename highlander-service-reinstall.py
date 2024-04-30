# Cria um serviço persistente que mantém outro serviço startado mesmo sendo fechado manualmente por alguém, esse script refaz a instalação caso alguém desinstale
# Você pode usar as condições do outro script highlander para checar o status do serviço
# Utilize o pyexec/pyinstaller para criar um executável para Windows

import time
import os
import subprocess
from win32serviceutil import RestartService, QueryServiceStatus, StartService
import win32service

# Nome do serviço a ser monitorado
highlander_service = "NomeDoServico"

# Caminho para o instalador do software, caso seja necessário reinstalá-lo
caminho_instalador = "C:\\caminho\\para\\instalador.exe"

def verificar_estado_servico(nome_servico):
    try:
        status = QueryServiceStatus(nome_servico)[1]
        return status
    except Exception as e:
        print(f"Erro ao verificar o status do serviço {nome_servico}: {e}")
        return None

def reiniciar_servico(nome_servico):
    try:
        RestartService(nome_servico)
        print(f"Serviço {nome_servico} reiniciado com sucesso.")
    except Exception as e:
        print(f"Erro ao reiniciar o serviço {nome_servico}: {e}")

def iniciar_servico(nome_servico):
    try:
        StartService(nome_servico)
        print(f"Serviço {nome_servico} iniciado com sucesso.")
    except Exception as e:
        print(f"Erro ao iniciar o serviço {nome_servico}: {e}")

def software_instalado():
    # Implemente uma verificação para determinar se o software está instalado
    # Isso pode ser uma verificação de arquivo, registro, etc.
    return os.path.exists("C:\\caminho\\para\\o\\software")

def reinstalar_software():
    print("Reinstalando o software...")
    subprocess.run([caminho_instalador, '/S'], check=True)  # Assume-se que '/S' seja o parâmetro para instalação silenciosa
    print("Software reinstalado.")

while True:
    estado = verificar_estado_servico(highlander_service)
    if estado == win32service.SERVICE_STOPPED:
        print(f"Serviço {highlander_service} parado. Tentando reiniciar...")
        iniciar_servico(highlander_service)

    if not software_instalado():
        print("Software desinstalado. Reinstalando...")
        reinstalar_software()
        time.sleep(60)  # Dá tempo para a instalação ser concluída
        iniciar_servico(highlander_service)

    time.sleep(10)  # Fica verificando a cada 10 secs o estado do serviço...
