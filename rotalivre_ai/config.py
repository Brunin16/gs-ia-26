"""Configuração central. Tudo pode ser trocado por variável de ambiente."""
import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE_DIR = RAIZ / "base"
AVAL_DIR = RAIZ / "avaliacao"

# "ollama" (padrão, resultados oficiais) ou "stub" (apenas testes automatizados, sem LLM)
BACKEND = os.getenv("ROTALIVRE_BACKEND", "ollama")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL = os.getenv("ROTALIVRE_LLM", "qwen2.5:7b")
EMB_MODEL = os.getenv("ROTALIVRE_EMB", "bge-m3")
TOP_K = int(os.getenv("ROTALIVRE_TOPK", "3"))
LIMIAR_INICIAL = float(os.getenv("ROTALIVRE_LIMIAR", "0.50"))  # só vale até o notebook 03 calibrar

# Resultados do stub nunca vão para a pasta oficial do repositório.
RESULTS_DIR = (
    AVAL_DIR / "resultados"
    if BACKEND == "ollama"
    else Path(tempfile.gettempdir()) / "rotalivre_stub_resultados"
)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def limiar() -> float:
    """Limiar de recusa calibrado no notebook 03 (avaliacao/resultados/limiar.json)."""
    arq = RESULTS_DIR / "limiar.json"
    if arq.exists():
        return float(json.loads(arq.read_text(encoding="utf-8"))["limiar"])
    return LIMIAR_INICIAL


def normalizar(texto: str) -> str:
    """minúsculas, sem acento, espaços colapsados."""
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"\s+", " ", t).strip()


def numeros(texto: str) -> set:
    """Conjunto de números do texto, normalizados (vírgula decimal -> ponto)."""
    achados = re.findall(r"\d+(?:[.,]\d+)?", texto)
    return {n.replace(",", ".") for n in achados}
