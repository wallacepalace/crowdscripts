## Resumo do Script

Este script tem como objetivo monitorar o serviço `falcon-sensor` em um servidor Linux. Ele realiza as seguintes funções principais:

> Em resumo: só altere o webHook URL e tudo vai funcionar perfeitamente.
> Não sei criar um webHook no Teams, como fazer? (Esse tutorial explica, é simples: https://www.youtube.com/watch?v=amvh4rzTCS0)

1. **Sessão Screen**: Verifica se está sendo executado dentro de uma sessão `screen`. Se não estiver, cria uma nova sessão `screen` e reinicia o script dentro dessa sessão.
2. **Instalação de Pré-requisitos**: Instala pacotes necessários como `auditd`, `curl`, `python3-dbus`, `python3-systemd` e `screen`.
3. **Adição de Regras do auditd**: Adiciona regras de auditoria específicas ao `auditd`.
4. **Notificações**: Monitora logs do serviço `falcon-sensor` e, caso detecte que o serviço foi desativado ou parou, envia uma notificação via Webhook, contendo informações detalhadas sobre o evento.
5. **Reinício do Serviço**: Garante que o serviço `falcon-sensor` esteja sempre em execução, reiniciando-o se necessário.
6. **Desconexão de Usuários**: Mata sessões SSH de usuários ativos, se necessário, e reinicia o serviço.
7. **Criação de Serviço Systemd**: Cria um arquivo de serviço Systemd para garantir que o script seja executado como um serviço no sistema.
8. **Para observação**: a regra de auditd encodada em base64 só faz basicamente isso: "-w /bin -p x -k exec_commands; -w /usr/bin/systemctl -p x -k falcon_sensor_change" então não precisa alterar nada.

## Comandos para Instalação

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y auditd curl python3-dbus python3-systemd screen
```
### CentOS/Red Hat/Oracle Linux

```bash
sudo yum install -y audit curl dbus-python python3-systemd screen
```

### Fedora

```bash
sudo dnf install -y audit curl dbus-python python3-systemd screen
```

## Variáveis que Precisam Ser Alteradas

- Atualize a URL do webhook para a sua URL específica no Microsoft Teams:
- Não sei criar um webHook no Teams, como fazer? (Esse tutorial explica, é simples: https://www.youtube.com/watch?v=amvh4rzTCS0)

```python
WEBHOOK_URL = "LINK-DO-WEBHOOK"
```

- Nome do Serviço:
- Obs: se o serviço a ser monitorado não for falcon-sensor, altere o nome do serviço:
```python
SERVICE_NAME = "nome_do_seu_serviço"
```

- Regras do auditd:
- Se precisar adicionar regras diferentes ao auditd, altere a variável AUDIT_RULES_BASE64 com as novas regras codificadas em base64:
python

```python
AUDIT_RULES_BASE64 = "SUAS_NOVAS_REGRAS_BASE64"
```

- Exemplos de Uso:
Após modificar as variáveis conforme necessário, execute o script. Ele se encarregará de criar a sessão screen, adicionar as regras de auditoria, instalar os pré-requisitos e garantir que o serviço esteja em execução contínua, enviando notificações para o webhook configurado quando eventos específicos forem detectados.
Este script deve ser executado como root ou com permissões sudo para que todas as funções (como instalação de pacotes e manipulação de serviços) funcionem corretamente.
