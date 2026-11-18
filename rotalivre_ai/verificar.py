"""Checagem da instalação: Python, dependências, Ollama, modelos e uma chamada real a cada modelo.

Uso (na raiz do repositório):  rodar.bat verificar   |   ./rodar.sh verificar
"""
import json
import sys

from . import config
from .runner import checar_ollama


def main() -> int:
    print(f"[1/4] Python {sys.version.split()[0]} em {sys.executable}")
    try:
        import fastapi, matplotlib, numpy, pandas, requests, tabulate  # noqa: F401
    except ImportError as e:
        print(f"[ERRO] dependência ausente: {e}. Rode o instalador de novo.")
        return 1
    print("[2/4] Dependências Python OK")

    try:
        print("[3/4]", checar_ollama())
    except RuntimeError as e:
        print(f"[ERRO] {e}")
        return 1
    if config.BACKEND != "ollama":
        return 0

    from .backend import OllamaBackend

    be = OllamaBackend()
    try:
        v = be.embed(["faixa livre da calçada"])
        print(f"      embeddings OK ({config.EMB_MODEL}, dimensão {v.shape[1]})")
        schema = {"type": "object", "properties": {"ok": {"type": "boolean"}}, "required": ["ok"]}
        bruto = be.chat("teste", "Responda somente em JSON.", "Responda ok=true.", schema)
        json.loads(bruto)
        print(f"      LLM com saída JSON OK ({config.LLM_MODEL})")
    except Exception as e:
        print(f"[ERRO] chamada ao modelo falhou: {e}")
        print("       Atualize o Ollama para a versão mais recente (saída em JSON Schema exige versão recente).")
        return 1
    print("[4/4] Tudo pronto. Próximo passo: abrir os notebooks (rodar.bat notebooks | ./rodar.sh notebooks).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
