@echo off
REM Habilitar Safe Boot com Rede
bcdedit /set {current} safeboot network

REM Criar script PowerShell para remover arquivos
echo $path = "C:\Windows\System32\drivers\CrowdStrike" > C:\RemoveCrowdStrike.ps1
echo if (Test-Path $path) { >> C:\RemoveCrowdStrike.ps1
echo     $files = Get-ChildItem -Path $path -Filter "C-00000291*.sys" >> C:\RemoveCrowdStrike.ps1
echo     foreach ($file in $files) { >> C:\RemoveCrowdStrike.ps1
echo         Remove-Item -Path $file.FullName -Force >> C:\RemoveCrowdStrike.ps1
echo         Write-Output "Arquivo excluído: $($file.FullName)" >> C:\RemoveCrowdStrike.ps1
echo     } >> C:\RemoveCrowdStrike.ps1
echo     Write-Output "Ação concluída. Inicialize o host normalmente." >> C:\RemoveCrowdStrike.ps1
echo } else { >> C:\RemoveCrowdStrike.ps1
echo     Write-Output "Nao achei: $path" >> C:\RemoveCrowdStrike.ps1
echo } >> C:\RemoveCrowdStrike.ps1

REM Criar script PowerShell para restaurar configurações de boot
echo # Set the execution policy to Bypass for the current session > C:\RestoreBoot.ps1
echo Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force >> C:\RestoreBoot.ps1
echo # Remove Safe Boot configuration >> C:\RestoreBoot.ps1
echo Start-Process -FilePath "$env:SystemRoot\System32\bcdedit.exe" -ArgumentList "/deletevalue {current} safeboot" -Wait >> C:\RestoreBoot.ps1
echo # Restore Userinit registry key to its default value >> C:\RestoreBoot.ps1
echo Start-Process -FilePath "reg.exe" -ArgumentList 'add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "C:\Windows\system32\userinit.exe," /f' -Wait >> C:\RestoreBoot.ps1
echo # Restart the machine >> C:\RestoreBoot.ps1
echo Start-Process -FilePath "shutdown.exe" -ArgumentList '/r /t 0' -Wait >> C:\RestoreBoot.ps1

REM Copiar RestoreBoot.ps1 para a área de trabalho de todos os usuários
for /d %%i in (C:\Users\*) do (
    if exist "%%i\Desktop" (
        copy C:\RestoreBoot.ps1 "%%i\Desktop\INICIA NORMAL.ps1"
    )
)

REM Criar script PowerShell para checar Safe Boot e rodar RestoreBoot
echo Start-Sleep -Seconds 120 > C:\CheckSafeBoot.ps1
echo $safeMode = Get-ItemPropertyValue "HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\Option" -Name OptionValue >> C:\CheckSafeBoot.ps1
echo if ($safeMode -eq 2) { >> C:\CheckSafeBoot.ps1
echo     Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File C:\RestoreBoot.ps1' >> C:\CheckSafeBoot.ps1
echo } >> C:\CheckSafeBoot.ps1

REM Modificar chave de registro Userinit para rodar RemoveCrowdStrike.ps1 na tela de login
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "cmd.exe /c powershell.exe -ExecutionPolicy Bypass -File C:\RemoveCrowdStrike.ps1 && powershell.exe -ExecutionPolicy Bypass -File C:\CheckSafeBoot.ps1" /f

REM Reiniciar a máquina
shutdown /r /t 0
