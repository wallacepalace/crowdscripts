# Cria um serviço persistente que mantém outro serviço startado mesmo sendo fechado manualmente por alguém
# Esse apenas mantém o serviço highlander
# Para checar o status a cada 3 segundos, é utilizado um ping para o DNS do cloudflare (1.1.1.1) - OBS: esse check pode ser alterado para o que você quiser
# Utilize o pyexec/pyinstaller para criar um executável para Windows

from win32serviceutil import QueryServiceStatus, StartService
import win32service
import subprocess
import time

# O nome do serviço é referente ao nome que aparece no "services.msc" do Windows, ou seja, o nome real do serviço
highlander_service = "NOMEDOSERVICO"

def verificar_existencia_servico(nome_servico):
    try:
        QueryServiceStatus(nome_servico)
        return True
    except Exception as e:
        return False

def verificar_estado_servico(nome_servico):
    try:
        status = QueryServiceStatus(nome_servico)[1]
        return status
    except Exception as e:
        print(f"Erro ao verificar o status do serviço {nome_servico}: {e}")
        return None


def iniciar_servico(nome_servico):
    try:
        StartService(nome_servico)
        print(f"Serviço {nome_servico} iniciado com sucesso.")
    except Exception as e:
        print(f"Erro ao iniciar o serviço {nome_servico}: {e}")


while True:
    if not verificar_existencia_servico(highlander_service):
        print(f"O serviço {highlander_service} não existe. Saindo do loop.")
        break

    estado = verificar_estado_servico(highlander_service)
    if estado == win32service.SERVICE_STOPPED:
        print(f"Serviço {highlander_service} parado. Tentando reiniciar...")
        print(subprocess.run(["ping", "1.1.1.1"]))
        iniciar_servico(highlander_service)
        
    time.sleep(3)
