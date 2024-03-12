# Se o script rodar em um determinado momento que um usuario nao tenha seu perfil criado ainda
# o script só ira remover as permissoes de usuarios anteriormente criados, portanto criei o bloco de comandos abaixo
# para schedullar o script para todo usuario que logar no sistema

# Cria a tarefa agendada para executar o script sempre que um usuario novo crie perfil na maquina

$taskName = "ExecuteScriptAtLogin"
$scriptPath = "C:\recext.ps1"
$action = New-ScheduledTaskAction -Execute "Powershell.exe" -Argument "-WindowStyle Hidden -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -AtLogon
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal
Write-Host "Tarefa agendada schedullada no sistema"

# Script que remove as permissoes

function Remover-Permissoes {
    param(
        [string]$caminho
    )
    try {
        $null = icacls $caminho /inheritance:r /grant:r *S-1-1-0:R
        Write-Host "Permissoes removidas com sucesso para a pasta: $caminho"
    } catch {
        Write-Host "Nao consegui remover as permissoes: $caminho"
        Write-Host $_.Exception.Message
    }
}

$pastaUsuarios = "C:\Users"
foreach ($usuario in (Get-ChildItem -Directory $pastaUsuarios)) {
    $pastaUsuarioChrome = Join-Path -Path $usuario.FullName -ChildPath "AppData\Local\Google\Chrome\User Data\Default\Extensions"
    $pastaUsuarioEdge = Join-Path -Path $usuario.FullName -ChildPath "AppData\Local\Microsoft\Edge\User Data\Default\Extensions"

    if (Test-Path $pastaUsuarioChrome) {
        Remover-Permissoes -caminho $pastaUsuarioChrome
    }
    
    if (Test-Path $pastaUsuarioEdge) {
        Remover-Permissoes -caminho $pastaUsuarioEdge
    }
}
Write-Host "Permissoes removidas de todas as pastas de usuarios"
