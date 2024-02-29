# Remove extensões do Chrome e Edge
# Wallace Alves

# - - nome da extensão (confere no path do navegador que está na var logo abaixo - -

$nomeExtensao = "NomeDaExtensao"

# chrome
$chromePath = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Extensions"
Get-ChildItem -Path $chromePath | ForEach-Object {
    $extPath = Join-Path -Path $chromePath -ChildPath $_
    
    ### troca o 'manifest.json' com o arquivo de configuração ou um identificador exclusivo da sua extensão (no edge vai ser a mesma coisa) 
    $manifest = Get-Content -Path (Join-Path -Path $extPath -ChildPath "manifest.json") -ErrorAction SilentlyContinue | ConvertFrom-Json
    if ($manifest.name -eq $nomeExtensao) {
        Remove-Item -Path $extPath -Recurse -Force
        Write-Output "Extensão removida do Chrome: $nomeExtensao"
    }
}

# edge
$edgePath = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Extensions"
Get-ChildItem -Path $edgePath | ForEach-Object {
    $extPath = Join-Path -Path $edgePath -ChildPath $_
    $manifest = Get-Content -Path (Join-Path -Path $extPath -ChildPath "manifest.json") -ErrorAction SilentlyContinue | ConvertFrom-Json
    if ($manifest.name -eq $nomeExtensao) {
        Remove-Item -Path $extPath -Recurse -Force
        Write-Output "Extensão removida do Edge: $nomeExtensao"
    }
}
