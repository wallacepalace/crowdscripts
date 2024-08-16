### OpenCTI no docker-compose sem precisar de Portainer

Fiz esse compose para facilitar a vida de quem precisava subir uma estrutura de OpenCTI, inclusive já vem com alguns conectores, como:

> connector-crowdstrike

> connector-alienvault

> connector-abuse-ipdb

> connector-cve

> connector-mitre-atlas

> connector-mitre

- O conector Crowdstrike permite integrar dados de inteligência de ameaças da plataforma Crowdstrike.
- O conector AlienVault permite integrar dados da plataforma AlienVault Open Threat Exchange (OTX).
- O conector Abuse.ipdb permite integrar dados sobre endereços IP maliciosos do serviço AbuseIPDB.
- O conector CVE permite importar vulnerabilidades da base de dados CVE (Common Vulnerabilities and Exposures).
- O conector MITRE ATLAS permite integrar dados da matriz de táticas e técnicas MITRE ATT&CK navegável.
- O conector MITRE permite integrar vários conjuntos de dados públicos da MITRE, incluindo ferramentas, malware, campanhas, padrões de ataque, etc.

Não esqueça de incluir suas keys de API antes de usar, se não vai dar erro nos conectores.

Seja feliz!
