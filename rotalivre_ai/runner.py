"""Atalhos usados pelos notebooks, pela API e pelos testes."""
import json
from dataclasses import asdict

import pandas as pd

from . import config, kb, metrics, pipelines
from .backend import criar_backend
from .retriever import Indice

CONFIGS = ("A_sem_contexto", "B_rag_simples", "C_agente")


def montar(cache=True):
    """Retorna (trechos, backend, indice)."""
    trechos = kb.carregar_trechos()
    be = criar_backend()
    return trechos, be, Indice(trechos, be, cache=cache)


def responder(cfg, pergunta, idx, be, **kw):
    if cfg == "A_sem_contexto":
        return pipelines.responder_sem_contexto(pergunta, be)
    if cfg == "B_rag_simples":
        return pipelines.responder_rag(pergunta, idx, be)
    if cfg == "C_agente":
        return pipelines.responder_agente(pergunta, idx, be, **kw)
    raise ValueError(cfg)


def rodar_todas(casos, idx, be, trechos, configs=CONFIGS, verbose=True):
    """Roda cada configuração em cada caso. Retorna (DataFrame de avaliações, lista de respostas brutas)."""
    linhas, respostas = [], []
    for cfg in configs:
        for i, c in enumerate(casos, 1):
            r = responder(cfg, c["pergunta"], idx, be)
            av = metrics.avaliar(c, r, trechos)
            av.update(config=cfg, pergunta=c["pergunta"], resposta=r.resposta, trecho_ids=r.trecho_ids,
                      erro=metrics.classificar_erro(av))
            linhas.append(av)
            respostas.append({"config": cfg, "caso": c["id"], **{k: v for k, v in asdict(r).items() if k != "bruto"}})
            if verbose:
                print(f"\r{cfg} {i}/{len(casos)}", end="")
        if verbose:
            print()
    return pd.DataFrame(linhas), respostas


def checar_ollama() -> str:
    """Confere se o Ollama responde e se os dois modelos existem. Falha com instrução clara."""
    if config.BACKEND != "ollama":
        return "backend=stub (somente testes; NÃO use para gerar resultados)"
    import requests

    try:
        tags = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=10).json()["models"]
    except Exception as e:
        raise RuntimeError(
            f"Ollama não respondeu em {config.OLLAMA_HOST} ({e}). Abra o aplicativo Ollama (Windows/macOS: menu Iniciar/Aplicativos; Linux: rode ollama serve) e tente de novo."
        )
    nomes = [m["name"] for m in tags]
    faltando = [m for m in (config.LLM_MODEL, config.EMB_MODEL) if not any(n == m or n.startswith(m + ":") for n in nomes)]
    if faltando:
        raise RuntimeError(f"Modelos ausentes no Ollama: {faltando}. Rode scripts/preparar_ollama.sh. Disponíveis: {nomes}")
    return f"Ollama OK em {config.OLLAMA_HOST} | LLM={config.LLM_MODEL} | embeddings={config.EMB_MODEL}"
