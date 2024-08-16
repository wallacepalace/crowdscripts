# Docker Compose para a Comunidade

Postar esse compose surgiu da necessidade de ajudar a comunidade de alguma forma com respostas a incidentes e integrações com CrowdStrike e outras ferramentas de segurança.

## Serviços

### Elasticsearch

- **Imagem**: `docker.elastic.co/elasticsearch/elasticsearch:8.9.2`
- **Descrição**: O Elasticsearch é um mecanismo de busca e análise distribuído, utilizado para armazenar e buscar grandes volumes de dados.
- **Ambiente**:
  - `discovery.type=single-node`: Configura o Elasticsearch para operar em um modo de nó único.
  - `xpack.security.enabled=false`: Desativa a segurança do X-Pack, útil para ambientes de teste.
- **Portas**: 
  - `9200:9200`: Mapeia a porta 9200 do container para a porta 9200 do host.
- **Volumes**:
  - `esdata:/usr/share/elasticsearch/data`: Volume para persistência de dados do Elasticsearch.

### Cortex

- **Imagem**: `thehiveproject/cortex:latest`
- **Descrição**: Cortex é uma ferramenta para análise e enriquecimento de dados de segurança. Ele trabalha com o TheHive para fornecer análises detalhadas e automatizadas.
- **Ambiente**:
  - `job_directory=/opt/cortex/jobs`: Define o diretório onde os trabalhos do Cortex serão armazenados.
- **Portas**:
  - `9001:9001`: Mapeia a porta 9001 do container para a porta 9001 do host.
- **Volumes**:
  - `cortexdata:/opt/cortex/jobs`: Volume para persistência dos trabalhos do Cortex.
  - `cortexlogs:/var/log/cortex`: Volume para persistência dos logs do Cortex.
- **Dependências**:
  - Depende do serviço `elasticsearch`.

### TheHive

- **Imagem**: `thehiveproject/thehive:latest`
- **Descrição**: TheHive é uma plataforma de resposta a incidentes e gerenciamento de casos. Ele utiliza o Elasticsearch para armazenar e buscar dados relacionados a incidentes.
- **Ambiente**:
  - `THEHIVE_ELASTICSEARCH__URL=http://elasticsearch:9200`: Configura a URL do Elasticsearch que o TheHive deve usar.
- **Portas**:
  - `9000:9000`: Mapeia a porta 9000 do container para a porta 9000 do host.
- **Volumes**:
  - `thehivedata:/opt/thehive`: Volume para persistência dos dados do TheHive.
- **Dependências**:
  - Depende do serviço `elasticsearch`.

## Volumes

- **esdata**: Volume para persistência de dados do Elasticsearch.
- **cortexdata**: Volume para persistência dos trabalhos do Cortex.
- **cortexlogs**: Volume para persistência dos logs do Cortex.
- **thehivedata**: Volume para persistência dos dados do TheHive.

Este `docker-compose.yml` oferece uma solução completa para a coleta, análise e gestão de eventos de segurança, facilitando a configuração e uso das ferramentas mencionadas.
