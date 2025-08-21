# Wallace Alves - (21) 97009-3729
# Script para forçar atualização do Google Chrome, Microsoft Edge e Adobe Acrobat Reader em segundo plano
# Cria taskschedulles do Chrome: 9h, Edge: 10h, Adobe Reader: 10:30h (semanalmente, a cada 7 dias, às segundas-feiras)

# 1. Configura execução em segundo plano criando um script temp VBS
$vbsScript = @"
Set WShell = CreateObject("WScript.Shell")
WShell.Run "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""$($MyInvocation.MyCommand.Path)"" -Hidden", 0
"@
$vbsPath = "$env:TEMP\RunHidden.vbs"
$vbsScript | Out-File -FilePath $vbsPath -Encoding ASCII

# Verifica se o script já está rodando em modo oculto
if (-not $args.Contains("-Hidden")) {
    # Inicia o script em modo oculto SEM ESPERAR e sai imediatamente
    Start-Process -FilePath "wscript.exe" -ArgumentList "`"$vbsPath`"" -WindowStyle Hidden
    Start-Sleep -Milliseconds 500  # Pequeno delay para garantir que inicie
    Remove-Item $vbsPath -ErrorAction SilentlyContinue
    exit
}

# Função para obter a versão de um software instalado
function Get-SoftwareVersion {
    param ($exePathRegKey, $exeName)
    try {
        $exePath = (Get-ItemProperty $exePathRegKey -ErrorAction SilentlyContinue).'(Default)'
        if ($exePath) {
            return (Get-Item $exePath -ErrorAction SilentlyContinue).VersionInfo.ProductVersion
        } else {
            return $null
        }
    } catch {
        return $null
    }
}

# Função para obter a versão mais recente do Adobe Reader da página de release notes
function Get-LatestAdobeVersion {
    try {
        $response = Invoke-WebRequest -Uri "https://helpx.adobe.com/acrobat/release-note/release-notes-acrobat-reader.html" -UseBasicParsing -TimeoutSec 30
        $content = $response.Content
        # Regex para encontrar a versão mais recente no formato 25.001.20630
        if ($content -match '(\d{2}\.\d{3}\.\d{5})') {
            Write-Output "$(Get-Date): Versão mais recente do Adobe Reader encontrada: $($Matches[1])" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
            return $Matches[1]
        } else {
            throw "Não foi possível extrair a versão mais recente."
        }
    } catch {
        Write-Output "$(Get-Date): Erro ao obter versão mais recente do Adobe Reader: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
        return $null
    }
}

# Função para atualizar um software
function Update-Software {
    param ($name, $url, $installerPath, $exeName, $versionRegKey, $taskName, $taskTime, $taskDescription)
    
    # Para Adobe, obter versão dinâmica e construir URL e installerPath
    if ($name -eq "Adobe Acrobat Reader") {
        $latestVersion = Get-LatestAdobeVersion
        if ($latestVersion) {
            $versionNoDots = $latestVersion.Replace(".", "")
            $url = "https://ardownload2.adobe.com/pub/adobe/acrobat/win/AcrobatDC/$versionNoDots/AcroRdrDCx64${versionNoDots}_MUI.exe"
            $installerPath = "$env:TEMP\AcroRdrDCx64${versionNoDots}_MUI.exe"
            Write-Output "$(Get-Date): Versão mais recente do Adobe Reader detectada: $latestVersion. URL: $url" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
        } else {
            Write-Output "$(Get-Date): Falha ao obter versão mais recente do Adobe Reader. Usando URL de fallback." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
            # URL de fallback para o instalador mais recente (redireciona para a última versão)
            $url = "https://get.adobe.com/reader/download/?installer=Reader_DC_Latest_English_MUI"
            $installerPath = "$env:TEMP\AcroRdrDCx64_Latest_MUI.exe"
        }
    }

    # Obtém a versão atual
    Write-Output "$(Get-Date): Obtendo versão atual do ${name}..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    $initialVersion = Get-SoftwareVersion -exePathRegKey $versionRegKey -exeName $exeName
    if ($initialVersion) {
        Write-Output "$(Get-Date): Versão atual do ${name}: $initialVersion" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    } else {
        Write-Output "$(Get-Date): Não foi possível obter a versão atual do ${name}. Continuando..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    }

    # Para serviços relacionados (apenas para Chrome)
    if ($name -eq "Google Chrome") {
        Write-Output "$(Get-Date): Parando serviços do Google Update..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
        try { Stop-Service -Name "gupdate" -Force -ErrorAction Stop } catch { Write-Output "$(Get-Date): Erro ao parar gupdate: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append }
        try { Stop-Service -Name "gupdatem" -Force -ErrorAction Stop } catch { Write-Output "$(Get-Date): Erro ao parar gupdatem: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append }
    }

    # Limpa cache (apenas para Chrome)
    if ($name -eq "Google Chrome") {
        Write-Output "$(Get-Date): Limpando cache do Chrome..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
        try { Remove-Item -Path "$env:LocalAppData\Google\Chrome\User Data\Default\Cache\*" -Recurse -Force -ErrorAction Stop } catch { Write-Output "$(Get-Date): Erro ao limpar cache: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append }
        try { Remove-Item -Path "$env:LocalAppData\Google\Chrome\User Data\Default\Code Cache\*" -Recurse -Force -ErrorAction Stop } catch { Write-Output "$(Get-Date): Erro ao limpar code cache: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append }
    }

    # Corrige políticas de grupo (apenas para Chrome)
    if ($name -eq "Google Chrome") {
        Write-Output "$(Get-Date): Corrigindo políticas de grupo para Chrome..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
        try { Remove-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Google\Update" -Name "UpdateDefault" -ErrorAction Stop } catch { Write-Output "$(Get-Date): Erro ao remover UpdateDefault: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append }
        try { Remove-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Google\Update" -Name "AutoUpdateCheckPeriodMinutes" -ErrorAction Stop } catch { Write-Output "$(Get-Date): Erro ao remover AutoUpdateCheckPeriodMinutes: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append }
        try { Remove-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Google\Update" -Name "DisableAutoUpdateChecksCheckboxValue" -ErrorAction Stop } catch { Write-Output "$(Get-Date): Erro ao remover DisableAutoUpdateChecksCheckboxValue: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append }
    }

    # Configura regras de firewall
    Write-Output "$(Get-Date): Configurando regras de firewall para ${name}..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    try { New-NetFirewallRule -DisplayName "Permitir ${name} Update" -Direction Outbound -Program "%ProgramFiles(x86)%\${name}\Application\${exeName}" -Action Allow -ErrorAction Stop } catch { Write-Output "$(Get-Date): Erro ao criar regra para ${name}: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append }
    if ($name -eq "Google Chrome") {
        try { New-NetFirewallRule -DisplayName "Permitir Google Update" -Direction Outbound -Program "%ProgramFiles(x86)%\Google\Update\GoogleUpdate.exe" -Action Allow -ErrorAction Stop } catch { Write-Output "$(Get-Date): Erro ao criar regra para Google Update: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append }
    }

    # Baixa e instala o software mais recente
    Write-Output "$(Get-Date): Baixando o instalador offline do ${name}..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    try {
        Invoke-WebRequest -Uri $url -OutFile $installerPath -ErrorAction Stop
    } catch {
        Write-Output "$(Get-Date): Erro ao baixar o instalador do ${name}: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    }

    if (Test-Path $installerPath) {
        Write-Output "$(Get-Date): Instalando o ${name} em segundo plano..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
        try {
            Start-Process -FilePath $installerPath -ArgumentList "/silent /install" -Wait -ErrorAction Stop
        } catch {
            Write-Output "$(Get-Date): Erro ao instalar o ${name}: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
        }

        # Remove o instalador após a instalação
        Write-Output "$(Get-Date): Limpando arquivos temporários do ${name}..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
        try { Remove-Item $installerPath -ErrorAction Stop } catch { Write-Output "$(Get-Date): Erro ao remover instalador do ${name}: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append }
    }

    # Obtém a versão após a atualização
    Write-Output "$(Get-Date): Obtendo versão após atualização do ${name}..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    $newVersion = Get-SoftwareVersion -exePathRegKey $versionRegKey -exeName $exeName
    if ($newVersion) {
        Write-Output "$(Get-Date): Nova versão do ${name}: $newVersion" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    } else {
        Write-Output "$(Get-Date): Não foi possível obter a nova versão do ${name}." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    }

    # Verifica se a versão foi atualizada e fecha/reabre o software apenas se atualizado
    if ($initialVersion -and $newVersion -and [version]$newVersion -gt [version]$initialVersion) {
        Write-Output "$(Get-Date): Versão do ${name} atualizada com sucesso. Fechando e reiniciando..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
        try { Stop-Process -Name $exeName -Force -ErrorAction Stop } catch { Write-Output "$(Get-Date): Erro ao parar o ${name} para reinício: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append }
        if ($name -eq "Google Chrome" -or $name -eq "Microsoft Edge") {
            Start-Process $exeName "about://settings/help"
        } else {
            Start-Process $exeName  # Adobe Reader não tem página de ajuda específica
        }
    } elseif ($initialVersion -and $newVersion -and [version]$newVersion -eq [version]$initialVersion) {
        Write-Output "$(Get-Date): Versão do ${name} não foi atualizada. Nenhuma ação adicional necessária." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    } else {
        Write-Output "$(Get-Date): Não foi possível comparar versões do ${name}. Abrindo para verificação..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
        if ($name -eq "Google Chrome" -or $name -eq "Microsoft Edge") {
            Start-Process $exeName "about://settings/help"
        } else {
            Start-Process $exeName
        }
    }

    # Cria tarefa agendada semanal
    Write-Output "$(Get-Date): Criando tarefa agendada para ${name} às $taskTime (semanalmente)..." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    try {
        # Remove tarefa existente, se houver
        if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
            Write-Output "$(Get-Date): Tarefa existente '${taskName}' removida." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
        }

        # Cria a ação para executar o script com argumento específico
        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$($MyInvocation.MyCommand.Path)`" -Hidden -${name}"

        # Define o gatilho para execução semanal (segunda-feira, a cada 7 dias)
        $trigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Monday -At $taskTime

        # Configurações da tarefa
        $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

        # Define execução com privilégios elevados
        $principal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest

        # Registra a tarefa
        Register-ScheduledTask -TaskName $taskName -Description $taskDescription -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force -ErrorAction Stop
        Write-Output "$(Get-Date): Tarefa agendada '${taskName}' criada com sucesso para rodar às $taskTime semanalmente." | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    } catch {
        Write-Output "$(Get-Date): Erro ao criar tarefa agendada para ${name}: $_" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append
    }
}

# Obtém a versão mais recente do Adobe Reader para uso no bloco principal
$adobeVersion = Get-LatestAdobeVersion
$adobeUrl = "https://get.adobe.com/reader/download/?installer=Reader_DC_Latest_English_MUI"  # URL de fallback
$adobeInstallerPath = "$env:TEMP\AcroRdrDCx64_Latest_MUI.exe"
if ($adobeVersion) {
    $versionNoDots = $adobeVersion.Replace(".", "")
    $adobeUrl = "https://ardownload2.adobe.com/pub/adobe/acrobat/win/AcrobatDC/$versionNoDots/AcroRdrDCx64${versionNoDots}_MUI.exe"
    $adobeInstallerPath = "$env:TEMP\AcroRdrDCx64${versionNoDots}_MUI.exe"
}

# Verifica se um software específico foi passado como argumento, senão atualiza todos
$softwareToUpdate = $args[1]
if ($softwareToUpdate) {
    switch ($softwareToUpdate) {
        "Google Chrome" {
            Update-Software -name "Google Chrome" -url "https://dl.google.com/chrome/install/ChromeStandaloneSetup64.exe" -installerPath "$env:TEMP\ChromeInstaller.exe" -exeName "chrome.exe" -versionRegKey "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" -taskName "ChromeWeeklyUpdate" -taskTime "9:00 AM" -taskDescription "Força atualização do Google Chrome semanalmente às 9h"
        }
        "Microsoft Edge" {
            Update-Software -name "Microsoft Edge" -url "https://go.microsoft.com/fwlink/?linkid=2109047&Channel=Stable&language=en" -installerPath "$env:TEMP\EdgeInstaller.exe" -exeName "msedge.exe" -versionRegKey "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe" -taskName "EdgeWeeklyUpdate" -taskTime "10:00 AM" -taskDescription "Força atualização do Microsoft Edge semanalmente às 10h"
        }
        "Adobe Acrobat Reader" {
            Update-Software -name "Adobe Acrobat Reader" -url $adobeUrl -installerPath $adobeInstallerPath -exeName "AcroRd32.exe" -versionRegKey "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\AcroRd32.exe" -taskName "AcrobatWeeklyUpdate" -taskTime "10:30 AM" -taskDescription "Força atualização do Adobe Acrobat Reader semanalmente às 10:30h"
        }
    }
} else {
    # Atualiza todos os softwares
    Update-Software -name "Google Chrome" -url "https://dl.google.com/chrome/install/ChromeStandaloneSetup64.exe" -installerPath "$env:TEMP\ChromeInstaller.exe" -exeName "chrome.exe" -versionRegKey "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe" -taskName "ChromeWeeklyUpdate" -taskTime "9:00 AM" -taskDescription "Força atualização do Google Chrome semanalmente às 9h"
    Update-Software -name "Microsoft Edge" -url "https://go.microsoft.com/fwlink/?linkid=2109047&Channel=Stable&language=en" -installerPath "$env:TEMP\EdgeInstaller.exe" -exeName "msedge.exe" -versionRegKey "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe" -taskName "EdgeWeeklyUpdate" -taskTime "10:00 AM" -taskDescription "Força atualização do Microsoft Edge semanalmente às 10h"
    Update-Software -name "Adobe Acrobat Reader" -url $adobeUrl -installerPath $adobeInstallerPath -exeName "AcroRd32.exe" -versionRegKey "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\AcroRd32.exe" -taskName "AcrobatWeeklyUpdate" -taskTime "10:30 AM" -taskDescription "Força atualização do Adobe Acrobat Reader semanalmente às 10:30h"
}

Write-Output "$(Get-Date): Concluído!" | Out-File "$env:TEMP\SoftwareUpdateLog.txt" -Append

# Limpa o script temporário
Remove-Item $vbsPath -ErrorAction SilentlyContinue
