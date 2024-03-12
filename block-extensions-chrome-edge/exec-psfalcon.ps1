# Script do PSFalcon
# Para baixar o psfalcon basta ir no Github do bk-cs: https://github.com/CrowdStrike/psfalcon

# Script para execução em massa do script de bloqueio de instalação de extensões Chrome e Edge

Install-Module -Name PSFalcon -Scope CurrentUser -Force
Import-Module -Name PSFalcon -Force

Request-FalconToken -ClientId $id -ClientSecret $secret -Cloud us-1

# O groupID você pode obter entrando na console do CrowdStrike e editando um "Host Group" qualquer, lá em cima na URL tem o ID do GroupId
$GroupId = "bc819ec7dd244f94b5e47028f2dd18c1"
$HostIds = Get-FalconHost -All -Filter "groups:'$GroupId'"

Invoke-FalconRTR -Timeout 60 -Command "put" -Arguments "recext.ps1" -HostIds $HostIds
Invoke-FalconRTR -Command runscript -Arguments "-CloudFile='Executa-recext'" -HostIds $HostIds -Timeout 90
