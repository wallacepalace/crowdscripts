# Script para remover softwares usando métodos nativos (WMIC e registro): deletar pastas e chaves de registro
# Executar como administrador. ATENÇÃO: Isso é arriscado e pode corromper o sistema se pastas/chaves erradas forem deletadas!

# Lista de softwares a serem removidos (nomes parciais para busca no registro e WMIC)
$softwareList = @(
    "Google Chrome",
    "Microsoft Edge",
    "Brave Browser",
    "Tor Browser",
    "Opera GX",
    "Opera",
    "Firefox"
)

# Função para exibir mensagens no terminal
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "$timestamp - $Message"
}

# Iniciar o processo
Write-Log "Iniciando o processo de remoção stealth com métodos nativos (WMIC e registro)..."

# Chaves de registro para programas instalados
$uninstallRoots = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
)

# Iterar sobre a lista de softwares
foreach ($software in $softwareList) {
    try {
        Write-Log "Verificando e removendo '$software' via WMIC (método nativo)..."
        
        # Tentar desinstalação via WMIC (nativo e silencioso)
        $wmicCommand = "wmic product where `"name like '%$software%'`" call uninstall /nointeractive"
        Invoke-Expression $wmicCommand | Out-Null
        Write-Log "Tentativa de remoção via WMIC para '$software' concluída (pode ter sido silenciosa)."
    } catch {
        Write-Log "Erro na remoção via WMIC para '$software': $_. Continuando com método de registro..."
    }
    
    # Fallback para método de registro e pastas, independentemente do WMIC (para garantir remoção completa)
    try {
        Write-Log "Verificando '$software' no registro..."
        
        $found = $false
        foreach ($root in $uninstallRoots) {
            $subkeys = Get-ChildItem -Path $root -ErrorAction SilentlyContinue
            foreach ($subkey in $subkeys) {
                $app = Get-ItemProperty -Path $subkey.PSPath -ErrorAction SilentlyContinue
                if ($app.DisplayName -imatch $software) {
                    $found = $true
                    Write-Log "Software '$software' encontrado no registro. Removendo sem uninstaller..."
                    
                    # Descobrir e deletar pastas (usando InstallLocation se disponível, ou paths comuns)
                    $installLocation = $app.InstallLocation
                    $pathsToDelete = @()
                    if ($installLocation -and (Test-Path $installLocation)) {
                        $pathsToDelete += $installLocation
                        Write-Log "Pasta encontrada via registro: '$installLocation'. Deletando..."
                    } else {
                        Write-Log "InstallLocation não encontrado ou inválido. Usando paths comuns..."
                        $commonPaths = @(
                            "$env:ProgramFiles\$software",
                            "$env:ProgramFiles (x86)\$software",
                            "$env:APPDATA\$software",
                            "$env:LOCALAPPDATA\$software",
                            "$env:USERPROFILE\$software"
                        )
                        foreach ($path in $commonPaths) {
                            if (Test-Path $path) {
                                $pathsToDelete += $path
                                Write-Log "Pasta comum encontrada: '$path'. Deletando..."
                            }
                        }
                    }
                    
                    # Deletar pastas
                    foreach ($path in $pathsToDelete) {
                        try {
                            Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
                            Write-Log "Pasta '$path' deletada com sucesso."
                        } catch {
                            Write-Log "Erro ao deletar pasta '$path': $_. Continuando..."
                        }
                    }
                    
                    # Deletar a chave de registro para remover de 'Programas e Recursos'
                    try {
                        Remove-Item -Path $subkey.PSPath -Force -ErrorAction Stop
                        Write-Log "Chave de registro deletada. Software removido de 'Programas e Recursos'."
                    } catch {
                        Write-Log "Erro ao deletar chave de registro: $_. Continuando..."
                    }
                }
            }
        }
        
        if (-not $found) {
            Write-Log "Software '$software' não encontrado no registro. Tentando deletar pastas comuns..."
            # Deletar pastas comuns mesmo sem registro (ex.: apps portáteis)
            $commonPaths = @(
                "$env:ProgramFiles\$software",
                "$env:ProgramFiles (x86)\$software",
                "$env:APPDATA\$software",
                "$env:LOCALAPPDATA\$software",
                "$env:USERPROFILE\$software",
                "$env:USERPROFILE\Desktop\$software",
                "$env:USERPROFILE\Downloads\$software"
            )
            foreach ($path in $commonPaths) {
                if (Test-Path $path) {
                    try {
                        Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
                        Write-Log "Pasta comum '$path' deletada."
                    } catch {
                        Write-Log "Erro ao deletar pasta comum '$path': $_. Continuando..."
                    }
                }
            }
        }
    } catch {
        Write-Log "Erro geral no processamento de '$software': $_. Continuando com o próximo software..."
    }
}

Write-Log "Processo de remoção concluído."
