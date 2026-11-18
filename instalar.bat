@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title RotaLivre AI - instalacao

if not defined ROTALIVRE_LLM set "ROTALIVRE_LLM=qwen2.5:7b"
if not defined ROTALIVRE_EMB set "ROTALIVRE_EMB=bge-m3"

echo ============================================================
echo  RotaLivre AI - instalacao no Windows
echo  Pasta: %CD%
echo ============================================================
echo.

rem ---------------------------------------------------------- 1. Python
echo [1/5] Procurando o Python 3.10 ou mais novo...
set "PY="
py -3.12 -c "import sys" >nul 2>nul && set "PY=py -3.12"
if not defined PY py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul && set "PY=py -3"
if not defined PY python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>nul && set "PY=python"
if not defined PY goto sem_python
for /f "delims=" %%v in ('%PY% --version') do echo       Encontrado: %%v

rem ---------------------------------------------------------- 2. Ambiente virtual
echo.
echo [2/5] Ambiente virtual .venv
if exist ".venv\Scripts\python.exe" goto venv_ok
echo       Criando .venv ...
%PY% -m venv .venv
if errorlevel 1 goto erro_venv
:venv_ok
set "VPY=%CD%\.venv\Scripts\python.exe"
if not exist "%VPY%" goto erro_venv
echo       OK: %VPY%

rem ---------------------------------------------------------- 3. Dependencias
echo.
echo [3/5] Instalando as dependencias Python. Pode levar alguns minutos...
"%VPY%" -m pip install --upgrade pip
if errorlevel 1 goto erro_pip
"%VPY%" -m pip install -r requirements.txt
if errorlevel 1 goto erro_pip
echo       Dependencias instaladas.

rem ---------------------------------------------------------- 4. Testes
echo.
echo [4/5] Rodando os testes automatizados. Eles NAO precisam do Ollama...
"%VPY%" -m pytest
if errorlevel 1 goto erro_testes

rem ---------------------------------------------------------- 5. Ollama e modelos
echo.
echo [5/5] Verificando o Ollama...
where ollama >nul 2>nul
if errorlevel 1 goto sem_ollama
ollama --version
echo.
echo       Baixando o LLM %ROTALIVRE_LLM%. Na primeira vez sao varios GB...
ollama pull %ROTALIVRE_LLM%
if errorlevel 1 goto erro_pull
echo.
echo       Baixando o modelo de embeddings %ROTALIVRE_EMB%...
ollama pull %ROTALIVRE_EMB%
if errorlevel 1 goto erro_pull
echo.
"%VPY%" -m rotalivre_ai.verificar
if errorlevel 1 goto fim_erro

echo.
echo ============================================================
echo  Instalacao concluida com sucesso.
echo  Proximo passo: de dois cliques em rodar.bat e escolha 2 - notebooks.
echo ============================================================
echo.
pause
exit /b 0

rem ---------------------------------------------------------- mensagens de erro
:sem_python
echo.
echo [ERRO] Python 3.10 ou mais novo nao foi encontrado.
echo        1. Baixe o Python 3.12 em https://www.python.org/downloads/windows/
echo        2. Na primeira tela do instalador MARQUE "Add python.exe to PATH" e clique em Install Now.
echo        3. Feche esta janela e rode o instalar.bat de novo.
goto fim_erro

:erro_venv
echo.
echo [ERRO] Nao foi possivel criar o ambiente virtual .venv.
echo        Apague a pasta .venv, se existir, e rode o instalar.bat de novo.
goto fim_erro

:erro_pip
echo.
echo [ERRO] Falha ao instalar as dependencias Python.
echo        Confira sua conexao com a internet e rode o instalar.bat de novo.
goto fim_erro

:erro_testes
echo.
echo [ERRO] Os testes automatizados falharam. Veja a mensagem acima.
goto fim_erro

:sem_ollama
echo.
echo [PENDENTE] O Ollama ainda nao esta instalado. As etapas 1 a 4 ja ficaram prontas.
echo        1. Baixe e instale o Ollama para Windows em https://ollama.com/download
echo        2. FECHE esta janela, abra o instalar.bat de novo. Na segunda vez as etapas 1 a 4 sao rapidas.
goto fim_erro

:erro_pull
echo.
echo [ERRO] Nao foi possivel baixar o modelo.
echo        Confira se o Ollama esta aberto: procure "Ollama" no menu Iniciar e abra.
echo        Confira tambem a internet e o espaco livre em disco, e rode o instalar.bat de novo.
goto fim_erro

:fim_erro
echo.
pause
exit /b 1
