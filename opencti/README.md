### OpenCTI no docker-compose sem precisar de Portainer

Fiz este compose para facilitar a vida de quem precisa subir uma estrutura de OpenCTI. Ele já vem com alguns conectores, como:

- `connector-crowdstrike`
- `connector-alienvault`
- `connector-abuse-ipdb`
- `connector-cve`
- `connector-mitre-atlas`
- `connector-mitre`

O que cada um faz:

- O conector CrowdStrike permite integrar dados de inteligência de ameaças da plataforma CrowdStrike.
- O conector AlienVault permite integrar dados da plataforma AlienVault Open Threat Exchange (OTX).
- O conector AbuseIPDB permite integrar dados sobre endereços IP maliciosos do serviço AbuseIPDB.
- O conector CVE permite importar vulnerabilidades da base de dados CVE (Common Vulnerabilities and Exposures).
- O conector MITRE ATLAS permite integrar dados da matriz de táticas e técnicas MITRE ATT&CK navegável.
- O conector MITRE permite integrar vários conjuntos de dados públicos da MITRE, incluindo ferramentas, malware, campanhas, padrões de ataque etc.

Não se esqueça de incluir suas chaves de API antes de usar; caso contrário, os conectores vão dar erro.

Seja feliz!
