# Baixe o PSFalcon no Github do bk-cs "https://github.com/CrowdStrike/psfalcon/archive/refs/heads/master.zip"
# Após isso, descompacte a pasta, entre nela e rode o script abaixo de lá:

Import-Module -Name ./PSFalcon.psd1 -Force

Request-FalconToken -ClientId SUAAPI -ClientSecret SUASECRET -Cloud us-1 # Sua console é US-1, US-2 ou GOV? (Altere também)

# GRUPO DE MÁQUINAS QUE RECEBERÃO O COMANDO
# Para saber o ID do grupo, vá até os "Host Groups" do CrowdStrike, escolha o grupo, edite ele e veja a URL lá em cima.
$GroupId = "cf5b2566f5f0456097ef65f6c07db494" # Segue esse padrão
$HostIds = Get-FalconHost -All -Filter "groups:'$GroupId'"

# Roda um script PERSONALIZADO que está no seu "Response Script and Files"
#Invoke-FalconRTR -Command runscript -Arguments "-CloudFile='wallace-da-massa'" -Verbose -HostIds $HostIds -Timeout 90 | Export-Csv 'wallace.csv'

# Roda o cswindiag (comando de RTR)
Invoke-FalconCommand -SessionID $session.session_id -Command 'runscript' -Arguments @{script_name='cswindiag'} -Verbose -HostIds $HostIds -Timeout 90 | Export-Csv 'cswindiag-result.csv'
