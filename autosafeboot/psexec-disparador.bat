@echo off
setlocal enabledelayedexpansion

REM Usuario e senha privilegiada
set USER=seuUsuario
set PASS=suaSenha

REM Caminho para o arquivo com os IPs das maquinas que voce quer atingir
set IP_LIST=ip_list.txt

REM Caminho para o script a ser executado remotamente
set REMOTE_SCRIPT=auto_safeboot-crowdstrike291.bat

REM Loop através da lista de IPs
for /f "tokens=*" %%i in (%IP_LIST%) do (
    echo Executando script em %%i
    psexec \\%%i -u %USER% -p %PASS% -c %REMOTE_SCRIPT%
)

endlocal
pause
