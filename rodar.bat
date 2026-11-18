@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title RotaLivre AI
set "VPY=%CD%\.venv\Scripts\python.exe"
if not exist "%VPY%" goto sem_venv

rem Uso direto: rodar.bat verificar | notebooks | api | robo-sim | robo COM5 | testes
set "OP=%~1"
if not "%OP%"=="" goto despachar

:menu
echo.
echo ===================== RotaLivre AI =====================
echo  1 - verificar  : confere Python, Ollama e modelos
echo  2 - notebooks  : abre o Jupyter Lab no navegador
echo  3 - api        : sobe a API em http://localhost:8000/docs
echo  4 - robo-sim   : simula o robo mandando eventos para a API
echo  5 - robo       : conecta no carrinho real pela porta COM
echo  6 - testes     : roda os testes automatizados
echo  0 - sair
echo  Obs.: as opcoes 4 e 5 precisam da API rodando em OUTRA janela.
echo ========================================================
set "OP="
set /p "OP=Escolha uma opcao: "
if "%OP%"=="1" set "OP=verificar"
if "%OP%"=="2" set "OP=notebooks"
if "%OP%"=="3" set "OP=api"
if "%OP%"=="4" set "OP=robo-sim"
if "%OP%"=="5" set "OP=robo"
if "%OP%"=="6" set "OP=testes"
if "%OP%"=="0" exit /b 0

:despachar
if /i "%OP%"=="verificar" goto verificar
if /i "%OP%"=="notebooks" goto notebooks
if /i "%OP%"=="api" goto api
if /i "%OP%"=="robo-sim" goto robosim
if /i "%OP%"=="robo" goto robo
if /i "%OP%"=="testes" goto testes
echo Opcao invalida: %OP%
goto menu

:verificar
"%VPY%" -m rotalivre_ai.verificar
goto fim

:notebooks
echo Abrindo o Jupyter Lab no navegador. Para encerrar, volte nesta janela e aperte Ctrl+C.
"%VPY%" -m jupyter lab
goto fim

:api
echo API em http://localhost:8000/docs . Para encerrar, aperte Ctrl+C nesta janela.
"%VPY%" -m uvicorn api.main:app --host 127.0.0.1 --port 8000
goto fim

:robosim
"%VPY%" scripts\ponte_robo.py --simular
goto fim

:robo
set "PORTA=%~2"
if "%PORTA%"=="" set /p "PORTA=Porta COM do carrinho, exemplo COM5: "
echo Feche o Monitor Serial da Arduino IDE antes, senao a porta fica ocupada.
"%VPY%" scripts\ponte_robo.py --porta %PORTA%
goto fim

:testes
"%VPY%" -m pytest
goto fim

:sem_venv
echo [ERRO] Ambiente nao instalado. Rode primeiro o instalar.bat.
goto fim

:fim
echo.
pause
exit /b
