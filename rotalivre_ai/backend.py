"""Acesso ao LLM e ao modelo de embeddings.

* OllamaBackend: LLM e embeddings 100% locais (Ollama). É o único usado para gerar resultados.
* StubBackend: determinístico e SEM LLM. Existe só para os testes automatizados rodarem
  sem GPU. Seus resultados nunca são gravados em avaliacao/resultados (ver config.RESULTS_DIR).
"""
import hashlib
import json
import re
import time
from typing import List, Optional

import numpy as np

from . import config


class OllamaBackend:
    nome = "ollama"

    def __init__(self, host=None, llm=None, emb=None, timeout=300):
        import requests  # import tardio: o stub não precisa

        self._rq = requests
        self.host = (host or config.OLLAMA_HOST).rstrip("/")
        self.llm = llm or config.LLM_MODEL
        self.emb = emb or config.EMB_MODEL
        self.timeout = timeout

    def _post(self, rota, payload):
        ultimo = None
        for tentativa in range(2):
            try:
                r = self._rq.post(f"{self.host}{rota}", json=payload, timeout=self.timeout)
                r.raise_for_status()
                return r.json()
            except Exception as e:  # rede/timeout: tenta de novo uma vez
                ultimo = e
                time.sleep(1.5)
        raise RuntimeError(f"Falha ao falar com o Ollama em {self.host}: {ultimo}")

    def embed(self, textos: List[str]) -> np.ndarray:
        dados = self._post("/api/embed", {"model": self.emb, "input": textos})
        return np.array(dados["embeddings"], dtype=np.float32)

    def chat(self, kind: str, system: str, user: str, schema: dict, **_) -> str:
        """Retorna o texto bruto do modelo, forçado ao JSON Schema pelo Ollama (structured outputs)."""
        dados = self._post(
            "/api/chat",
            {
                "model": self.llm,
                "stream": False,
                "format": schema,
                "options": {"temperature": 0, "seed": 7},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        return dados["message"]["content"]


class StubBackend:
    nome = "stub"
    DIM = 256

    def embed(self, textos: List[str]) -> np.ndarray:
        out = np.zeros((len(textos), self.DIM), dtype=np.float32)
        for i, t in enumerate(textos):
            for tok in re.findall(r"[a-z0-9,]+", config.normalizar(t)):
                if len(tok) <= 3:   # descarta stopwords curtas ("de", "com", "da"...)
                    continue
                h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
                out[i, h % self.DIM] += 1.0
        return out

    def chat(self, kind, system, user, schema, contexto: Optional[list] = None, pergunta: str = "", **_) -> str:
        if kind == "reescrever":
            return json.dumps({"consulta_busca": pergunta, "tema": "outro"})
        if kind == "verificar":
            return json.dumps({"suportada": True, "problemas": ""})
        if kind == "gerar" and contexto:
            tid, texto = contexto[0]
            return json.dumps({"resposta": texto, "trecho_ids": [tid], "recusou": False})
        if kind == "gerar":
            return json.dumps({"resposta": "Não consta na base de conhecimento.", "trecho_ids": [], "recusou": True})
        # sem_contexto: simula um modelo que inventa
        return json.dumps({"resposta": "O valor é 42.", "trecho_ids": [], "recusou": False})


def criar_backend():
    return OllamaBackend() if config.BACKEND == "ollama" else StubBackend()
