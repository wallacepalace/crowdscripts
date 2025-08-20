# Wallace Alves - qualquer duvida (21) 97009-3729

$softwareList = @(
    "WinRAR",
    "AnyDesk",
    "TeamViewer",
    "Brave Browser",
    "NordVPN",
    "Tor Browser",
    "Opera GX",
    "Opera",
    "Firefox",
    "uTorrent",
    "BitTorrent",
    "qBittorrent",
    "Epic Games",
    "Epic Online Services",
    "League of Legends",
    "Roblox",
    "Avast Online Security & Privacy",
    "Counter-Strike",
    "Steam",
    "Adobe Flash Player",
    "Riot Client"
)

function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "$timestamp - $Message"
}

Write-Log "Iniciando o processo de remoção stealth com métodos nativos (WMIC e registro)..."

try {
    Write-Log "Matando todos os processos e serviços relacionados aos softwares da lista..."
    foreach ($software in $softwareList) {
        try {
            Get-Process | Where-Object { $_.ProcessName -imatch $software -or $_.ProcessName -imatch "WinRAR|rar|RiotClient|EpicGames" } | Stop-Process -Force -ErrorAction SilentlyContinue
            Write-Log "Processos relacionados a '$software' terminados (se existirem)."
        } catch {
            Write-Log "Erro ao matar processos para '$software': $_. Continuando..."
        }
        try {
            Get-Service | Where-Object { $_.Name -imatch $software -or $_.DisplayName -imatch $software -or $_.Name -imatch "RiotClient|Epic|WinRAR" } | Stop-Service -Force -ErrorAction SilentlyContinue
            Write-Log "Serviços relacionados a '$software' parados (se existirem)."
        } catch {
            Write-Log "Erro ao parar serviços para '$software': $_. Continuando..."
        }
    }
} catch {
    Write-Log "Erro geral ao matar processos/serviços: $_. Continuando com a remoção..."
}

$uninstallRoots = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
)

foreach ($software in $softwareList) {
    try {
        Write-Log "Verificando e removendo '$software' via WMIC (método nativo)..."
        
        $wmicCommand = "wmic product where `"name like '%$software%'`" call uninstall /nointeractive"
        Invoke-Expression $wmicCommand | Out-Null
        Write-Log "Tentativa de remoção via WMIC para '$software' concluída (pode ter sido silenciosa)."
    } catch {
        Write-Log "Erro na remoção via WMIC para '$software': $_. Continuando com método de registro..."
    }
    
    try {
        Write-Log "Verificando '$software' no registro..."
        
        $found = $false
        foreach ($root in $uninstallRoots) {
            $subkeys = Get-ChildItem -Path $root -ErrorAction SilentlyContinue
            foreach ($subkey in $subkeys) {
                $app = Get-ItemProperty -Path $subkey.PSPath -ErrorAction SilentlyContinue
                if ($app.DisplayName -imatch $software -or $app.DisplayName -imatch "WinRAR|rar|RiotClient|EpicGames") {
                    $found = $true
                    Write-Log "Software '$software' encontrado no registro. Removendo sem uninstaller..."
                    
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
                            "$env:USERPROFILE\$software",
                            "$env:ProgramData\$software"
                        )
                        if ($software -imatch "League of Legends|Riot Client") {
                            $commonPaths += @("C:\Riot Games", "$env:ProgramData\Riot Games")
                        }
                        if ($software -imatch "WinRAR") {
                            $commonPaths += @("$env:APPDATA\WinRAR", "$env:ProgramFiles\WinRAR", "$env:ProgramFiles (x86)\WinRAR")
                        }
                        if ($software -imatch "Epic Games|Epic Online Services") {
                            $commonPaths += @("$env:ProgramFiles\Epic Games", "$env:ProgramFiles (x86)\Epic Games", "$env:LOCALAPPDATA\EpicGamesLauncher")
                        }
                        foreach ($path in $commonPaths) {
                            if (Test-Path $path) {
                                $pathsToDelete += $path
                                Write-Log "Pasta comum encontrada: '$path'. Deletando..."
                            }
                        }
                    }
                    
                    foreach ($path in $pathsToDelete) {
                        try {
                            Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
                            Write-Log "Pasta '$path' deletada com sucesso."
                        } catch {
                            Write-Log "Erro ao deletar pasta '$path': $_. Continuando..."
                        }
                    }
                    
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
            $commonPaths = @(
                "$env:ProgramFiles\$software",
                "$env:ProgramFiles (x86)\$software",
                "$env:APPDATA\$software",
                "$env:LOCALAPPDATA\$software",
                "$env:USERPROFILE\$software",
                "$env:USERPROFILE\Desktop\$software",
                "$env:USERPROFILE\Downloads\$software",
                "$env:ProgramData\$software"
            )
            if ($software -imatch "League of Legends|Riot Client") {
                $commonPaths += @("C:\Riot Games", "$env:ProgramData\Riot Games")
            }
            if ($software -imatch "WinRAR") {
                $commonPaths += @("$env:APPDATA\WinRAR", "$env:ProgramFiles\WinRAR", "$env:ProgramFiles (x86)\WinRAR")
            }
            if ($software -imatch "Epic Games|Epic Online Services") {
                $commonPaths += @("$env:ProgramFiles\Epic Games", "$env:ProgramFiles (x86)\Epic Games", "$env:LOCALAPPDATA\EpicGamesLauncher")
            }
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
