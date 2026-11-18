#!/usr/bin/env bash
# RotaLivre AI - menu.  Uso: ./rodar.sh [verificar|notebooks|api|robo-sim|robo /dev/ttyUSB0|testes]
set -uo pipefail
cd "$(dirname "$0")"
VPY="$(pwd)/.venv/bin/python"
if [ ! -x "$VPY" ]; then echo "[ERRO] Ambiente nao instalado. Rode primeiro ./instalar.sh"; exit 1; fi

OP="${1:-}"
if [ -z "$OP" ]; then
  echo "===================== RotaLivre AI ====================="
  echo " 1 - verificar  : confere Python, Ollama e modelos"
  echo " 2 - notebooks  : abre o Jupyter Lab no navegador"
  echo " 3 - api        : sobe a API em http://localhost:8000/docs"
  echo " 4 - robo-sim   : simula o robo mandando eventos para a API"
  echo " 5 - robo       : conecta no carrinho real pela porta serial"
  echo " 6 - testes     : roda os testes automatizados"
  echo " Obs.: as opcoes 4 e 5 precisam da API rodando em OUTRO terminal."
  echo "========================================================"
  read -r -p "Escolha uma opcao: " n
  case "$n" in 1) OP=verificar;; 2) OP=notebooks;; 3) OP=api;; 4) OP=robo-sim;; 5) OP=robo;; 6) OP=testes;; *) exit 0;; esac
fi

case "$OP" in
  verificar) "$VPY" -m rotalivre_ai.verificar ;;
  notebooks) echo "Abrindo o Jupyter Lab. Para encerrar: Ctrl+C."; "$VPY" -m jupyter lab ;;
  api)       echo "API em http://localhost:8000/docs . Para encerrar: Ctrl+C."; "$VPY" -m uvicorn api.main:app --host 127.0.0.1 --port 8000 ;;
  robo-sim)  "$VPY" scripts/ponte_robo.py --simular ;;
  robo)      PORTA="${2:-}"; [ -z "$PORTA" ] && read -r -p "Porta serial do carrinho (ex.: /dev/ttyUSB0): " PORTA
             "$VPY" scripts/ponte_robo.py --porta "$PORTA" ;;
  testes)    "$VPY" -m pytest ;;
  *)         echo "Opcao invalida: $OP"; exit 1 ;;
esac
