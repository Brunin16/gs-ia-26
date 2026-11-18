#!/usr/bin/env bash
# RotaLivre AI - instalacao no Linux e no macOS.  Uso:  ./instalar.sh
set -euo pipefail
cd "$(dirname "$0")"
LLM="${ROTALIVRE_LLM:-qwen2.5:7b}"
EMB="${ROTALIVRE_EMB:-bge-m3}"

echo "============================================================"
echo " RotaLivre AI - instalacao (Linux/macOS)"
echo " Pasta: $(pwd)"
echo "============================================================"

echo "[1/5] Procurando o Python 3.10 ou mais novo..."
PY=""
for c in python3.12 python3.13 python3.11 python3.10 python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "[ERRO] Python 3.10+ nao encontrado."
  echo "       Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
  echo "       macOS: instale pelo https://www.python.org/downloads/macos/"
  exit 1
fi
echo "      Encontrado: $("$PY" --version)"

echo "[2/5] Ambiente virtual .venv"
if [ ! -x .venv/bin/python ]; then
  "$PY" -m venv .venv || { echo "[ERRO] Falha ao criar o .venv. No Ubuntu/Debian: sudo apt install python3-venv"; exit 1; }
fi
VPY="$(pwd)/.venv/bin/python"
echo "      OK: $VPY"

echo "[3/5] Instalando as dependencias Python (pode levar alguns minutos)..."
"$VPY" -m pip install --upgrade pip
"$VPY" -m pip install -r requirements.txt

echo "[4/5] Rodando os testes automatizados (nao precisam do Ollama)..."
"$VPY" -m pytest

echo "[5/5] Verificando o Ollama..."
if ! command -v ollama >/dev/null 2>&1; then
  echo "[PENDENTE] O Ollama ainda nao esta instalado. As etapas 1 a 4 ja ficaram prontas."
  echo "       Linux: curl -fsSL https://ollama.com/install.sh | sh"
  echo "       macOS: baixe em https://ollama.com/download e abra o aplicativo"
  echo "       Depois rode ./instalar.sh de novo."
  exit 1
fi
ollama --version || true
echo "      Baixando o LLM $LLM (varios GB na primeira vez)..."
ollama pull "$LLM" || { echo "[ERRO] Falha no download. O Ollama esta rodando? Linux: sudo systemctl start ollama | macOS: abra o app Ollama"; exit 1; }
echo "      Baixando os embeddings $EMB..."
ollama pull "$EMB"
"$VPY" -m rotalivre_ai.verificar

echo "============================================================"
echo " Instalacao concluida. Proximo passo:  ./rodar.sh notebooks"
echo "============================================================"
