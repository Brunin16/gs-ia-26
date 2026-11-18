"""As três configurações comparadas no placar:

A) sem_contexto  : o mesmo LLM, sem nenhum trecho.
B) rag_simples   : busca vetorial top-k + geração fundamentada em JSON. Sempre responde com o que achou.
C) agente        : especialização por agente = reescrita da consulta, portão de relevância (limiar
                   calibrado), busca híbrida, geração, verificador LLM, verificação determinística
                   de números/citações e recusa explícita.
"""
import json
from dataclasses import dataclass, field
from typing import List, Optional

from . import config
from .retriever import Indice

RECUSA = "Não consta na base de conhecimento."

SCHEMA_RESPOSTA = {
    "type": "object",
    "properties": {
        "resposta": {"type": "string"},
        "trecho_ids": {"type": "array", "items": {"type": "string"}},
        "recusou": {"type": "boolean"},
    },
    "required": ["resposta", "trecho_ids", "recusou"],
}
SCHEMA_REESCRITA = {
    "type": "object",
    "properties": {
        "consulta_busca": {"type": "string"},
        "tema": {"type": "string", "enum": ["norma", "lei", "dado", "robo", "outro"]},
    },
    "required": ["consulta_busca", "tema"],
}
SCHEMA_VERIFICACAO = {
    "type": "object",
    "properties": {"suportada": {"type": "boolean"}, "problemas": {"type": "string"}},
    "required": ["suportada", "problemas"],
}

SYS_SEM_CONTEXTO = (
    "Você é um assistente sobre acessibilidade de calçadas no Brasil e sobre um robô de inspeção de calçadas. "
    "Responda em português, de forma curta e objetiva, em JSON: 'resposta' (texto), 'trecho_ids' (sempre lista vazia) "
    "e 'recusou' (true somente se você não souber responder)."
)
SYS_RAG = (
    "Você responde SOMENTE com base nos TRECHOS fornecidos. Regras: "
    "1) use apenas informações presentes nos trechos, nunca conhecimento próprio; "
    "2) em 'trecho_ids' liste os IDs dos trechos que usou; "
    f"3) se os trechos não contêm a resposta, use resposta='{RECUSA}', trecho_ids=[] e recusou=true; "
    "4) não invente números; 5) responda em até 3 frases, em português."
)
SYS_REESCREVER = (
    "Reescreva a pergunta como uma consulta de busca curta, com termos técnicos que provavelmente aparecem no texto-fonte "
    "(ex.: calçada, passeio, faixa livre, faixa de serviço, rebaixamento, NBR 9050, CTB, IBGE, Censo 2022, robô, LDR, TinyML). "
    "Não responda a pergunta. Classifique o tema: norma, lei, dado, robo ou outro."
)
SYS_VERIFICAR = (
    "Você é um verificador rigoroso. Dados TRECHOS, PERGUNTA e RESPOSTA, diga se TODA afirmação da resposta é sustentada "
    "pelos trechos (inclusive números). Se algo não for sustentado ou se a resposta não responder à pergunta, 'suportada'=false "
    "e descreva em 'problemas'."
)


@dataclass
class Resp:
    resposta: str = ""
    trecho_ids: List[str] = field(default_factory=list)
    recusou: bool = False
    json_valido: bool = True
    bruto: str = ""
    config: str = ""
    trace: list = field(default_factory=list)


def _parse(bruto: str, cfg: str) -> Resp:
    try:
        d = json.loads(bruto)
        ok = (
            isinstance(d, dict)
            and isinstance(d.get("resposta"), str)
            and isinstance(d.get("trecho_ids"), list)
            and all(isinstance(i, str) for i in d["trecho_ids"])
            and isinstance(d.get("recusou"), bool)
        )
        if not ok:
            raise ValueError("esquema inválido")
        return Resp(d["resposta"], d["trecho_ids"], d["recusou"], True, bruto, cfg)
    except Exception:
        return Resp("", [], False, False, bruto, cfg)


def _formatar_trechos(hits) -> str:
    return "\n".join(f"[{h.trecho.id}] {h.trecho.texto}" for h in hits)


# ------------------------------------------------------------------ A) sem contexto
def responder_sem_contexto(pergunta: str, be) -> Resp:
    bruto = be.chat("sem_contexto", SYS_SEM_CONTEXTO, f"PERGUNTA: {pergunta}", SCHEMA_RESPOSTA, pergunta=pergunta)
    r = _parse(bruto, "A_sem_contexto")
    r.trecho_ids = []  # o modelo não tem trechos para citar
    return r


# ------------------------------------------------------------------ B) RAG simples
def responder_rag(pergunta: str, idx: Indice, be, k: Optional[int] = None) -> Resp:
    k = k or config.TOP_K
    hits = idx.buscar(pergunta, k=k, metodo="emb")
    user = f"TRECHOS:\n{_formatar_trechos(hits)}\n\nPERGUNTA: {pergunta}"
    contexto = [(h.trecho.id, h.trecho.texto) for h in hits]
    bruto = be.chat("gerar", SYS_RAG, user, SCHEMA_RESPOSTA, contexto=contexto, pergunta=pergunta)
    r = _parse(bruto, "B_rag_simples")
    r.trace = [{"passo": "busca", "ids": [h.trecho.id for h in hits], "cos": [round(h.cos, 3) for h in hits]}]
    return r


# ------------------------------------------------------------------ C) agente
def _fundamentada(r: Resp, hits, pergunta: str):
    """Verificação determinística: citações existem entre os trechos recuperados e todo número
    da resposta aparece nos trechos citados (ou na pergunta). Retorna (ok, motivo)."""
    por_id = {h.trecho.id: h.trecho for h in hits}
    citados = [i for i in r.trecho_ids if i in por_id]
    if not citados:
        return False, "resposta sem citação de trecho válido"
    base = config.numeros(pergunta)
    for i in citados:
        base |= config.numeros(por_id[i].texto)
    fora = config.numeros(r.resposta) - base
    if fora:
        return False, f"números fora dos trechos citados: {sorted(fora)}"
    return True, ""


def responder_agente(pergunta: str, idx: Indice, be, limiar: Optional[float] = None, k: Optional[int] = None) -> Resp:
    k = k or config.TOP_K
    limiar = config.limiar() if limiar is None else limiar
    trace = []

    def recusar(motivo):
        trace.append({"passo": "recusa", "motivo": motivo})
        return Resp(RECUSA, [], True, True, "", "C_agente", trace)

    # 1) reescrita da consulta
    consulta, tema = pergunta, "outro"
    try:
        d = json.loads(be.chat("reescrever", SYS_REESCREVER, f"PERGUNTA: {pergunta}", SCHEMA_REESCRITA, pergunta=pergunta))
        consulta, tema = d.get("consulta_busca") or pergunta, d.get("tema", "outro")
    except Exception:
        pass
    trace.append({"passo": "reescrever", "consulta": consulta, "tema": tema})

    # 2) portão de relevância
    cmax = idx.cos_max(pergunta)
    trace.append({"passo": "portao", "cos_max": round(cmax, 3), "limiar": round(limiar, 3)})
    if cmax < limiar:
        return recusar(f"similaridade máxima {cmax:.2f} abaixo do limiar {limiar:.2f}")

    # 3) busca híbrida
    hits = idx.buscar(pergunta, k=k, metodo="hibrido", consulta_extra=consulta)
    trace.append({"passo": "busca_hibrida", "ids": [h.trecho.id for h in hits]})
    contexto = [(h.trecho.id, h.trecho.texto) for h in hits]

    feedback = ""
    for tentativa in (1, 2):
        user = f"TRECHOS:\n{_formatar_trechos(hits)}\n\nPERGUNTA: {pergunta}{feedback}"
        r = _parse(be.chat("gerar", SYS_RAG, user, SCHEMA_RESPOSTA, contexto=contexto, pergunta=pergunta), "C_agente")
        trace.append({"passo": f"gerar_{tentativa}", "json_valido": r.json_valido, "ids": r.trecho_ids})
        if not r.json_valido:
            feedback = "\n\nCORREÇÃO: devolva JSON válido conforme o esquema."
            continue
        if r.recusou:
            return recusar("o gerador recusou: trechos não contêm a resposta")

        # 4a) verificação determinística
        ok, motivo = _fundamentada(r, hits, pergunta)
        # 4b) verificador LLM
        citados = [h for h in hits if h.trecho.id in r.trecho_ids]
        uv = f"TRECHOS:\n{_formatar_trechos(citados or hits)}\n\nPERGUNTA: {pergunta}\n\nRESPOSTA: {r.resposta}"
        try:
            v = json.loads(be.chat("verificar", SYS_VERIFICAR, uv, SCHEMA_VERIFICACAO))
        except Exception:
            v = {"suportada": False, "problemas": "verificador devolveu JSON inválido"}
        trace.append({"passo": f"verificar_{tentativa}", "deterministico": ok, "motivo": motivo, "llm": v})
        if ok and v.get("suportada"):
            r.trace = trace
            return r
        feedback = f"\n\nCORREÇÃO NECESSÁRIA: {motivo or v.get('problemas', '')}. Use somente os trechos."

    return recusar("não foi possível produzir resposta verificada pelos trechos")
