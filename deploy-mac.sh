#!/bin/bash

# Parar a execução em caso de erros
set -e

# Defina o caminho para o instalador do sensor e o seu Customer ID (CID)
INSTALLER_PATH="/tmp/FalconSensorMacOS.pkg"
CID="SEU_CUSTOMER_ID_AQUI"

# URL do instalador (substitua pela URL fornecida pela CrowdStrike)
INSTALLER_URL="https://falcon.crowdstrike.com/installer"

# Baixar o instalador do sensor
curl -o "$INSTALLER_PATH" "$INSTALLER_URL"

# Instalar o sensor
sudo installer -pkg "$INSTALLER_PATH" -target /

# Registrar o sensor com o CID
sudo /Applications/Falcon.app/Contents/Resources/falconctl license "$CID"

# Limpar o instalador
rm "$INSTALLER_PATH"

# Conceder permissões necessárias (acesso completo ao disco)
sudo /usr/bin/tccutil reset All com.crowdstrike.falcon.Agent
sudo /usr/bin/tccutil grant FullDiskAccess com.crowdstrike.falcon.Agent

# Notificar o usuário sobre a extensão do sistema (se necessário)
if [ -e "/Library/Extensions/falcon.kext" ]; then
    echo "A extensão do sistema do Falcon foi instalada. Pode ser necessário permitir o carregamento nas Preferências de Segurança e Privacidade."
fi

echo "Instalação do sensor CrowdStrike Falcon concluída com sucesso."