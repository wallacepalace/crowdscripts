> Este script é usado para configurar um ambiente de inicialização segura (Safe Boot) com rede no Windows, executar scripts PowerShell para remover arquivos relacionados ao CrowdStrike, restaurar configurações de inicialização normais e copiar um script de restauração para a área de trabalho de todos os usuários. Vamos analisar cada parte do script:

- 1 - Habilitar Safe Boot com Rede:

```cmd
Copiar código
@echo off
REM Habilitar Safe Boot com Rede
bcdedit /set {current} safeboot network
```
> Este comando habilita a inicialização segura (Safe Boot) com suporte de rede para a configuração atual do sistema.

- 2 - Criar script PowerShell para remover arquivos do CrowdStrike:

```cmd
Copiar código
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
> Esta seção cria um script PowerShell RemoveCrowdStrike.ps1 que verifica a existência do diretório C:\Windows\System32\drivers\CrowdStrike, remove arquivos com o padrão C-00000291*.sys, e escreve mensagens de saída conforme a operação é realizada.

- 3 - Criar script PowerShell para restaurar configurações de boot:

```cmd
Copiar código
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
> Esta seção cria um script PowerShell RestoreBoot.ps1 que remove a configuração de Safe Boot, restaura a chave de registro Userinit para seu valor padrão e reinicia a máquina.

- 4 - Copiar o script de restauração para a área de trabalho de todos os usuários:

```cmd
Copiar código
REM Copiar RestoreBoot.ps1 para a área de trabalho de todos os usuários
for /d %%i in (C:\Users\*) do (
    if exist "%%i\Desktop" (
        copy C:\RestoreBoot.ps1 "%%i\Desktop\INICIA NORMAL.ps1"
    )
)
```
> Este loop copia o script RestoreBoot.ps1 para a área de trabalho de todos os usuários no sistema, nomeando-o como INICIA NORMAL.ps1.

- 5 - Criar script PowerShell para checar Safe Boot e rodar RestoreBoot:

```cmd
Copiar código
REM Criar script PowerShell para checar Safe Boot e rodar RestoreBoot
echo Start-Sleep -Seconds 120 > C:\CheckSafeBoot.ps1
echo $safeMode = Get-ItemPropertyValue "HKLM:\SYSTEM\CurrentControlSet\Control\SafeBoot\Option" -Name OptionValue >> C:\CheckSafeBoot.ps1
echo if ($safeMode -eq 2) { >> C:\CheckSafeBoot.ps1
echo     Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File C:\RestoreBoot.ps1' >> C:\CheckSafeBoot.ps1
echo } >> C:\CheckSafeBoot.ps1
```
> Este script CheckSafeBoot.ps1 aguarda 120 segundos, verifica se o sistema está em modo de inicialização segura (Safe Boot) e, se estiver, executa o script RestoreBoot.ps1.

- 6 - Modificar a chave de registro Userinit para rodar RemoveCrowdStrike.ps1 na tela de login:

```cmd
Copiar código
REM Modificar chave de registro Userinit para rodar RemoveCrowdStrike.ps1 na tela de login
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "cmd.exe /c powershell.exe -ExecutionPolicy Bypass -File C:\RemoveCrowdStrike.ps1 && powershell.exe -ExecutionPolicy Bypass -File C:\CheckSafeBoot.ps1" /f
```
> Este comando modifica a chave de registro Userinit para que, ao iniciar a sessão, os scripts RemoveCrowdStrike.ps1 e CheckSafeBoot.ps1 sejam executados.

- 7 - Reiniciar a máquina:

```cmd
Copiar código
REM Reiniciar a máquina
shutdown /r /t 0
```
> Finalmente, este comando reinicia a máquina imediatamente para aplicar as alterações.

> Este script automatiza o processo de remoção de arquivos específicos do CrowdStrike em um ambiente de inicialização segura e, em seguida, restaura as configurações de inicialização normais e reinicia o sistema.
