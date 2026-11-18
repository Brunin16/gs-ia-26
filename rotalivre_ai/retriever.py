import hashlib
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import List

import numpy as np

from . import config
from .kb import Trecho


def _tokens(texto: str) -> List[str]:
    return re.findall(r"[a-z0-9,]+", config.normalizar(texto))


@dataclass
class Hit:
    trecho: Trecho
    cos: float        # similaridade de cosseno (embeddings)
    bm25: float       # pontuação BM25 (lexical)
    score: float      # pontuação final do método usado (cos, bm25 ou RRF)


class Indice:
    def __init__(self, trechos: List[Trecho], backend, cache=True):
        self.trechos = trechos
        self.be = backend
        textos = [t.texto for t in trechos]
        self._emb = self._embeddings(textos, cache)
        self._docs = [Counter(_tokens(t)) for t in textos]
        self._len = np.array([sum(d.values()) for d in self._docs], dtype=float)
        n = len(self._docs)
        df = Counter(tok for d in self._docs for tok in d)
        self._idf = {tok: math.log(1 + (n - c + 0.5) / (c + 0.5)) for tok, c in df.items()}

    # ---------- embeddings ----------
    def _embeddings(self, textos, cache):
        chave = hashlib.md5(("|".join(textos) + getattr(self.be, "emb", self.be.nome)).encode()).hexdigest()[:12]
        arq = config.RESULTS_DIR / f".emb_{self.be.nome}_{chave}.npy"
        if cache and arq.exists():
            m = np.load(arq)
        else:
            m = self.be.embed(textos)
            if cache:
                np.save(arq, m)
        return m / (np.linalg.norm(m, axis=1, keepdims=True) + 1e-9)

    def _cos(self, consulta: str) -> np.ndarray:
        q = self.be.embed([consulta])[0]
        q = q / (np.linalg.norm(q) + 1e-9)
        return self._emb @ q

    # ---------- BM25 ----------
    def _bm25(self, consulta: str, k1=1.5, b=0.75) -> np.ndarray:
        q = _tokens(consulta)
        media = self._len.mean()
        out = np.zeros(len(self._docs))
        for i, d in enumerate(self._docs):
            for tok in q:
                f = d.get(tok, 0)
                if f:
                    out[i] += self._idf.get(tok, 0) * f * (k1 + 1) / (f + k1 * (1 - b + b * self._len[i] / media))
        return out

    # ---------- API pública ----------
    def buscar(self, consulta: str, k=3, metodo="emb", consulta_extra: str = "") -> List[Hit]:
        """metodo: 'emb' (cosseno), 'bm25' ou 'hibrido' (RRF dos dois). consulta_extra reforça o lexical."""
        cos = self._cos(consulta)
        bm = self._bm25(consulta + " " + consulta_extra)
        if metodo == "emb":
            score = cos
        elif metodo == "bm25":
            score = bm
        elif metodo == "hibrido":
            r_c = {i: r for r, i in enumerate(np.argsort(-cos))}
            r_b = {i: r for r, i in enumerate(np.argsort(-bm))}
            score = np.array([1 / (60 + r_c[i]) + 1 / (60 + r_b[i]) for i in range(len(cos))])
        else:
            raise ValueError(metodo)
        ordem = np.argsort(-score)[:k]
        return [Hit(self.trechos[i], float(cos[i]), float(bm[i]), float(score[i])) for i in ordem]

    def cos_max(self, consulta: str) -> float:
        return float(self._cos(consulta).max())
