import json
from dataclasses import dataclass
from typing import List

from . import config

CAMPOS = ("id", "texto", "fonte", "referencia", "url", "formato", "licenca", "tema")


@dataclass(frozen=True)
class Trecho:
    id: str
    texto: str
    fonte: str
    referencia: str
    url: str
    formato: str
    licenca: str
    tema: str

    def citacao(self) -> str:
        return f"{self.fonte}, {self.referencia}"


def _jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def carregar_trechos(path=None) -> List[Trecho]:
    path = path or config.BASE_DIR / "trechos.jsonl"
    trechos = [Trecho(**{k: d[k] for k in CAMPOS}) for d in _jsonl(path)]
    ids = [t.id for t in trechos]
    if len(ids) != len(set(ids)):
        raise ValueError("IDs de trecho duplicados na base")
    return trechos


def carregar_casos(path=None) -> list:
    path = path or config.AVAL_DIR / "casos_teste.jsonl"
    casos = _jsonl(path)
    for c in casos:
        if c["tipo"] not in ("consta", "nao_consta"):
            raise ValueError(f"tipo inválido em {c['id']}")
    return casos


def validar_casos(casos, trechos) -> list:
    """Retorna lista de problemas (vazia = ok): IDs de gabarito inexistentes e 'consta' sem critério."""
    ids = {t.id for t in trechos}
    problemas = []
    for c in casos:
        if c["tipo"] == "consta":
            if not c["trechos_gabarito"] or not c["deve_conter"]:
                problemas.append(f"{c['id']}: 'consta' sem gabarito")
            for tid in c["trechos_gabarito"]:
                if tid not in ids:
                    problemas.append(f"{c['id']}: trecho {tid} não existe")
        elif c["trechos_gabarito"]:
            problemas.append(f"{c['id']}: 'nao_consta' não deve ter trecho de gabarito")
    return problemas
