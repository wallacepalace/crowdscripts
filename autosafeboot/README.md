> Este script é usado para configurar a inicialização segura (Safe Boot) com rede no Windows, executar scripts PowerShell que removem arquivos relacionados ao CrowdStrike, restaurar as configurações normais de inicialização e copiar um script de restauração para a área de trabalho de todos os usuários. Vamos analisar cada parte do script:

### 1. Habilitar o Safe Boot com rede

```bat
@echo off
REM Habilitar Safe Boot com Rede
bcdedit /set {current} safeboot network
```
> Este comando habilita a inicialização segura (Safe Boot) com suporte a rede na configuração de boot atual do sistema.

### 2. Criar script PowerShell para remover arquivos do CrowdStrike

```bat
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
```
> Esta seção cria o script PowerShell `RemoveCrowdStrike.ps1`, que verifica se o diretório `C:\Windows\System32\drivers\CrowdStrike` existe, remove os arquivos com o padrão `C-00000291*.sys` e escreve mensagens de saída conforme a operação é realizada.

### 3. Criar script PowerShell para restaurar configurações de boot

```bat
REM Criar script PowerShell para restaurar configurações de boot
echo # Set the execution policy to Bypass for the current session > C:\RestoreBoot.ps1
echo Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force >> C:\RestoreBoot.ps1
echo # Remove Safe Boot configuration >> C:\RestoreBoot.ps1
echo Start-Process -FilePath "$env:SystemRoot\System32\bcdedit.exe" -ArgumentList "/deletevalue {current} safeboot" -Wait >> C:\RestoreBoot.ps1
echo # Restore Userinit registry key to its default value >> C:\RestoreBoot.ps1
echo Start-Process -FilePath "reg.exe" -ArgumentList 'add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "C:\Windows\system32\userinit.exe," /f' -Wait >> C:\RestoreBoot.ps1
echo # Restart the machine >> C:\RestoreBoot.ps1
echo Start-Process -FilePath "shutdown.exe" -ArgumentList '/r /t 0' -Wait >> C:\RestoreBoot.ps1
```
> Esta seção cria o script PowerShell `RestoreBoot.ps1`, que remove a configuração de Safe Boot, restaura a chave de registro `Userinit` para o valor padrão e reinicia a máquina.

### 4. Copiar o script de restauração para a área de trabalho de todos os usuários

```bat
REM Copiar RestoreBoot.ps1 para a área de trabalho de todos os usuários
for /d %%i in (C:\Users\*) do (
    if exist "%%i\Desktop" (
        copy C:\RestoreBoot.ps1 "%%i\Desktop\INICIA NORMAL.ps1"
    )
)
```
> Este loop copia o script `RestoreBoot.ps1` para a área de trabalho de todos os usuários do sistema, com o nome `INICIA NORMAL.ps1`.

### 5. Criar script PowerShell para checar Safe Boot e rodar RestoreBoot

```bat
REM Criar script PowerShell para checar Safe Boot e rodar RestoreBoot
echo Start-Sleep -Seconds 120 > C:\CheckSafeBoot.ps1
echo $safeMode = Get-ItemPropertyValue "HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\Option" -Name OptionValue >> C:\CheckSafeBoot.ps1
echo if ($safeMode -eq 2) { >> C:\CheckSafeBoot.ps1
echo     Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File C:\RestoreBoot.ps1' >> C:\CheckSafeBoot.ps1
echo } >> C:\CheckSafeBoot.ps1
```
> O script `CheckSafeBoot.ps1` aguarda 120 segundos, verifica se o sistema está no modo de inicialização segura (Safe Boot) e, se estiver, executa o script `RestoreBoot.ps1`.

### 6. Modificar a chave de registro Userinit para rodar RemoveCrowdStrike.ps1 no logon

```bat
REM Modificar chave de registro Userinit para rodar RemoveCrowdStrike.ps1 na tela de login
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "cmd.exe /c powershell.exe -ExecutionPolicy Bypass -File C:\RemoveCrowdStrike.ps1 && powershell.exe -ExecutionPolicy Bypass -File C:\CheckSafeBoot.ps1" /f
```
> Este comando modifica a chave de registro `Userinit` para que, ao iniciar a sessão, os scripts `RemoveCrowdStrike.ps1` e `CheckSafeBoot.ps1` sejam executados.

### 7. Reiniciar a máquina

```bat
REM Reiniciar a máquina
shutdown /r /t 0
```
> Finalmente, este comando reinicia a máquina imediatamente para aplicar as alterações.

> Em resumo, o script automatiza a remoção de arquivos específicos do CrowdStrike no modo de inicialização segura e, em seguida, restaura as configurações normais de inicialização e reinicia o sistema.
