"""Métricas automáticas do placar. Definições (também no README):

* acerto        consta: JSON válido, não recusou e contém todos os grupos de `deve_conter`;
                nao_consta: JSON válido e recusou.
* alucinação    consta: citou trecho inexistente OU trouxe número que não está na pergunta nem nos
                trechos do gabarito nem nos trechos reais que a própria resposta citou (nem em
                identificadores de norma da base);
                nao_consta: respondeu em vez de recusar (afirmou algo sem base).
* recusa indevida  consta mas recusou (erro de omissão, não conta como alucinação).
* citação correta  consta: citou ao menos um trecho do gabarito; nao_consta: não citou nada.
"""
import numpy as np
import pandas as pd

from . import config


def _ids_normas(trechos) -> set:
    """Números que aparecem em fonte/referência (ex.: 9050, 16537, 13.146, 181): identificadores, não valores."""
    ids = set()
    for t in trechos:
        ids |= config.numeros(t.fonte + " " + t.referencia)
    return ids


def avaliar(caso: dict, resp, trechos) -> dict:
    por_id = {t.id: t for t in trechos}
    citou = list(resp.trecho_ids)
    fonte_inventada = any(i not in por_id for i in citou)
    consta = caso["tipo"] == "consta"
    out = dict(
        id=caso["id"], tipo=caso["tipo"], json_valido=resp.json_valido, recusou=resp.recusou,
        recusa_indevida=False, fonte_inventada=fonte_inventada, numeros_fora=[],
    )
    if not resp.json_valido:
        out.update(acerto=False, alucinou=False, citou_certo=False)
        return out

    if not consta:
        out.update(acerto=bool(resp.recusou), alucinou=not resp.recusou, citou_certo=len(citou) == 0)
        return out

    texto = config.normalizar(resp.resposta)
    grupos_ok = all(any(config.normalizar(a) in texto for a in g) for g in caso["deve_conter"])
    permitidos = config.numeros(caso["pergunta"]) | _ids_normas(trechos)
    for tid in caso["trechos_gabarito"]:
        permitidos |= config.numeros(por_id[tid].texto)
    for tid in citou:                       # número vindo de um trecho REAL citado também tem base
        if tid in por_id:
            permitidos |= config.numeros(por_id[tid].texto)
    fora = sorted(config.numeros(resp.resposta) - permitidos) if not resp.recusou else []
    out.update(
        acerto=(not resp.recusou) and grupos_ok,
        alucinou=(fonte_inventada or bool(fora)) and not resp.recusou,
        recusa_indevida=bool(resp.recusou),
        numeros_fora=fora,
        citou_certo=bool(set(citou) & set(caso["trechos_gabarito"])),
    )
    return out


def classificar_erro(av: dict) -> str:
    if not av["json_valido"]:
        return "JSON inválido"
    if av["tipo"] == "nao_consta" and not av["recusou"]:
        return "alucinação: respondeu algo que não consta na base"
    if av["fonte_inventada"]:
        return "alucinação: citou fonte inexistente"
    if av["numeros_fora"]:
        return f"alucinação: número fora da base {av['numeros_fora']}"
    if av["recusa_indevida"]:
        return "recusa indevida (a base tinha a resposta)"
    if av["tipo"] == "consta" and not av["acerto"]:
        return "resposta incompleta ou incorreta"
    return ""


def resumir(df: pd.DataFrame) -> pd.DataFrame:
    """df: uma linha por (config, caso) com as colunas de avaliar() + 'config'."""
    linhas = []
    for cfg, g in df.groupby("config", sort=True):
        c, n = g[g.tipo == "consta"], g[g.tipo == "nao_consta"]
        linhas.append({
            "configuração": cfg,
            "acerto (%)": round(100 * g.acerto.mean(), 1),
            "alucinação (%)": round(100 * g.alucinou.mean(), 1),
            "JSON válido (%)": round(100 * g.json_valido.mean(), 1),
            "citação correta (%)": round(100 * g.citou_certo.mean(), 1),
            "recusa correta em 'não consta' (%)": round(100 * n.acerto.mean(), 1) if len(n) else np.nan,
            "recusa indevida em 'consta' (%)": round(100 * c.recusa_indevida.mean(), 1) if len(c) else np.nan,
            "casos": len(g),
        })
    return pd.DataFrame(linhas)


def recall_at_k(indice, casos, k, metodo="emb") -> float:
    """Fração dos casos 'consta' em que algum trecho do gabarito está entre os k primeiros."""
    alvo = [c for c in casos if c["tipo"] == "consta"]
    acertos = 0
    for c in alvo:
        ids = {h.trecho.id for h in indice.buscar(c["pergunta"], k=k, metodo=metodo)}
        acertos += bool(ids & set(c["trechos_gabarito"]))
    return acertos / len(alvo)
