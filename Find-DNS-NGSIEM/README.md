# Find-DNS-NGSIEM: Monitoramento de Certificados e Domínios
> wallace.palves@rededor.com.br ou WhatsApp (21) 97009-3729
#
# Prints do Projeto:
<img src="https://i.imgur.com/8EG2khq.jpeg" style="width: 100%; height: 100%;">
<img src="https://i.imgur.com/Hhbb5d3.jpeg" style="width: 100%; height: 100%;">
<img src="https://i.imgur.com/rmRuptH.jpeg" style="width: 100%; height: 100%;">

## Resumo da Aplicação

O **Find-DNS-NGSIEM** é uma aplicação web desenvolvida em Flask que centraliza o monitoramento de certificados SSL/TLS e informações de domínio. Ele integra dados de diversas fontes para fornecer uma visão abrangente e alertas proativos sobre a saúde e o vencimento de certificados.

**Principais Funcionalidades:**

*   **Descoberta de Domínios:**
    *   Integração com a API CrowdStrike (Humio) para extrair domínios de logs de requisições DNS, focando em domínios configurados via `VAR_DOMINIO`.
    *   Execução automática da ferramenta `subfinder` para enumerar subdomínios com base em `VAR_DOMINIO`, salvando os resultados em `dns-manual.txt`.
    *   Processamento de domínios adicionais listados manualmente em `dns-manual.txt`.
*   **Escaneamento de Certificados:** Conecta-se a domínios em portas comuns (443, 636, etc.) para coletar detalhes de certificados SSL/TLS, como autoridade certificadora, datas de emissão e expiração.
*   **Informações WHOIS:** Realiza consultas WHOIS para obter e-mails de contato associados aos domínios.
*   **Armazenamento de Dados:** Todos os dados coletados são armazenados em um banco de dados SQLite (`certificates.db`).
*   **Interface Web Interativa:** Uma interface de usuário intuitiva em Flask exibe os dados dos certificados em uma tabela, com um sistema de cores para indicar o status de vencimento (verde, laranja, vermelho). Utiliza Server-Sent Events (SSE) para atualizações de progresso em tempo real.
*   **Alertas por E-mail:** Envia automaticamente alertas por e-mail para certificados que estão próximos do vencimento (até 3 meses), garantindo que as renovações sejam feitas a tempo.
*   **Exportação de Dados:** Permite exportar os dados da tabela para um arquivo CSV.

## Como Configurar e Fazer o Sistema Funcionar

Para configurar e executar o Find-DNS-NGSIEM, siga os passos abaixo:

### Pré-requisitos

Você precisará ter instalado em seu sistema:

*   **Python 3.8+**
*   **pip** (gerenciador de pacotes Python)
*   **Go (Golang)** (para compilar e executar o `subfinder`)
*   **git** (para clonar o repositório)

### 1. Clonar o Repositório

Primeiro, clone o repositório para sua máquina local:

```bash
git clone https://github.com/wallacepalace/crowdscripts/Find-DNS-NGSIEM.git
cd Find-DNS-NGSIEM
```

### 2. Configurar o Ambiente Python

Crie e ative um ambiente virtual Python para isolar as dependências do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instale as dependências Python necessárias:

```bash
pip install -r requirements.txt
```

### 3. Compilar o Subfinder

O `subfinder` é uma ferramenta Go que precisa ser compilada. Navegue até a pasta `subfinder` e compile-o:

```bash
cd subfinder
go build -o subfinder ./cmd/subfinder
cd .. # Volte para o diretório raiz do projeto
```

Certifique-se de que o executável `subfinder` esteja presente na pasta `subfinder/`.

### 4. Configurar Variáveis de Ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto (`Find-DNS-NGSIEM/`) e preencha-o com as seguintes variáveis. **Substitua os valores de exemplo pelos seus próprios dados.**

```
CROWDSTRIKE_CLIENT_ID=SEU_CROWDSTRIKE_CLIENT_ID
CROWDSTRIKE_CLIENT_SECRET=SEU_CROWDSTRIKE_CLIENT_SECRET
API_KEY=SUA_API_KEY_OPCIONAL
API_SECRET=SUA_API_SECRET_OPCIONAL
SMTP_SERVER=seu-servidor-smtp
SMTP_PORT=587
SMTP_LOGIN=seu_email@exemplo.com
SMTP_PASSWORD=SUA_SENHA_SMTP
SENDER_EMAIL=seu_email@exemplo.com
RECIPIENT_EMAIL=email_para_receber_alertas@exemplo.com
VAR_DOMINIO=dominio1.com,dominio2.com,dominio3.com # Domínios para CrowdStrike e Subfinder, separados por vírgula
```

*   **`CROWDSTRIKE_CLIENT_ID`** e **`CROWDSTRIKE_CLIENT_SECRET`**: Credenciais da sua API CrowdStrike para acesso ao Humio.
*   **`API_KEY`** e **`API_SECRET`**: Variáveis de API genéricas, podem ser opcionais dependendo de futuras integrações.
*   **Variáveis SMTP**: Configurações para o envio de e-mails de alerta.
*   **`VAR_DOMINIO`**: **CRÍTICO.** Uma lista de domínios (separados por vírgula) que serão usados para:
    *   Filtrar logs DNS na consulta CrowdStrike.
    *   Servir como entrada para a ferramenta `subfinder` para enumeração de subdomínios.

### 5. Executar a Aplicação Flask

Com o ambiente virtual ativado e o arquivo `.env` configurado, você pode iniciar a aplicação Flask:

```bash
python app.py
```

A aplicação será executada em `http://0.0.0.0:5000`.

### 6. Acessar a Interface Web

Abra seu navegador e navegue para `http://localhost:5000` (ou o IP do servidor onde a aplicação está rodando na porta 5000).

### 7. Utilização

*   **"Atualizar Dados (Últimos 7 Dias)"**: Clique neste botão para iniciar o processo de coleta de dados. Ele fará o seguinte:
    1.  Executará o `subfinder` para os domínios em `VAR_DOMINIO` e salvará os resultados em `dns-manual.txt`.
    2.  Consultará a API CrowdStrike para logs DNS dos últimos 7 dias, usando os domínios de `VAR_DOMINIO`.
    3.  Combinará os domínios da CrowdStrike e de `dns-manual.txt`.
    4.  Escaneia cada domínio para obter informações de certificado e WHOIS.
    5.  Atualizará a tabela na interface em tempo real com o progresso.
    6.  Após a conclusão, enviará alertas de e-mail para certificados próximos do vencimento.
*   **"Exportar para CSV"**: Baixa um arquivo CSV com todos os dados de certificados atualmente no banco de dados.
*   **"Alertar Vencimentos"**: Envia manualmente e-mails de alerta para certificados que vencem em até 3 meses.

---
