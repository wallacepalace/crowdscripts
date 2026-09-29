## Resumo do script

Este script tem como objetivo monitorar o serviço `falcon-sensor` em um servidor Linux.

> Em resumo: só altere a URL do webhook e tudo vai funcionar perfeitamente.
> Não sabe criar um webhook no Teams? Este tutorial explica, é simples: https://www.youtube.com/watch?v=amvh4rzTCS0

Ele realiza as seguintes funções principais:

1. **Sessão screen**: verifica se está sendo executado dentro de uma sessão `screen`. Se não estiver, cria uma nova sessão `screen` e reinicia o script dentro dela.
2. **Instalação de pré-requisitos**: instala os pacotes necessários, como `auditd`, `curl`, `python3-dbus`, `python3-systemd` e `screen`.
3. **Adição de regras do auditd**: adiciona regras de auditoria específicas ao `auditd`.
4. **Notificações**: monitora os logs do serviço `falcon-sensor` e, caso detecte que o serviço foi desativado ou parou, envia uma notificação via webhook com informações detalhadas sobre o evento.
5. **Reinício do serviço**: garante que o serviço `falcon-sensor` esteja sempre em execução, reiniciando-o se necessário.
6. **Desconexão de usuários**: encerra as sessões SSH de usuários ativos, se necessário, e reinicia o serviço.
7. **Criação de serviço systemd**: cria um arquivo de serviço systemd para garantir que o script seja executado como um serviço no sistema.

> Observação: a regra do auditd codificada em base64 faz basicamente isto: `-w /bin -p x -k exec_commands; -w /usr/bin/systemctl -p x -k falcon_sensor_change`. Então, não precisa alterar nada.

## Comandos para instalação

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

### Arch/Manjaro

```bash
sudo pamac install audit curl python-dbus python-systemd screen
```

Ou:

```bash
sudo pacman -Syu audit curl python-dbus python-systemd screen
```

## Variáveis que precisam ser alteradas

- **URL do webhook**: atualize para a URL específica do seu webhook no Microsoft Teams (o tutorial citado acima mostra como criar um).

```python
WEBHOOK_URL = "LINK-DO-WEBHOOK"
```

- **Nome do serviço**: se o serviço a ser monitorado não for o `falcon-sensor`, altere o nome do serviço:

```python
SERVICE_NAME = "nome_do_seu_serviço"
```

- **Regras do auditd**: se precisar adicionar regras diferentes ao auditd, altere a variável `AUDIT_RULES_BASE64` com as novas regras codificadas em base64:

```python
AUDIT_RULES_BASE64 = "SUAS_NOVAS_REGRAS_BASE64"
```

## Uso

Após modificar as variáveis conforme necessário, execute o script. Ele se encarregará de criar a sessão screen, adicionar as regras de auditoria, instalar os pré-requisitos e garantir que o serviço esteja em execução contínua, enviando notificações para o webhook configurado quando eventos específicos forem detectados.

Este script deve ser executado como root ou com permissões de sudo, para que todas as funções (como a instalação de pacotes e a manipulação de serviços) funcionem corretamente.
