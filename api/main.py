"""API do assistente RotaLivre.

Segurança e LGPD by design:
* só recebe pergunta (texto curto) ou evento do robô (classe + distância + luminosidade); nenhum dado pessoal;
* nada é gravado em disco nem em banco; o log registra apenas rota, tamanho e tempo (nunca o conteúdo);
* entradas validadas e limitadas (pydantic); sem CORS aberto; LLM e embeddings rodam localmente (Ollama);
* decisões que afetam o cidadão ficam com pessoas: a API só explica e recomenda verificação humana.

Rodar (na raiz do repositório):  rodar.bat api   |   ./rodar.sh api
"""
import logging
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Literal, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # raiz do repositório

from fastapi import FastAPI, HTTPException  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from rotalivre_ai import config, montar, pipelines  # noqa: E402

log = logging.getLogger("rotalivre.api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

ESTADO = {}


@asynccontextmanager
async def lifespan(app):
    trechos, be, idx = montar()
    ESTADO.update(trechos=trechos, be=be, idx=idx, por_id={t.id: t for t in trechos})
    log.info("base carregada: %d trechos | backend=%s | limiar=%.3f", len(trechos), be.nome, config.limiar())
    yield
    ESTADO.clear()


app = FastAPI(title="RotaLivre AI", version="1.0", lifespan=lifespan)


class Pergunta(BaseModel):
    pergunta: str = Field(min_length=5, max_length=300)
    modo: Literal["agente", "rag"] = "agente"


class Fonte(BaseModel):
    id: str
    citacao: str
    url: str
    licenca: str


class Resposta(BaseModel):
    resposta: str
    recusou: bool
    fontes: List[Fonte]
    explicacao: list = Field(description="passos do agente (explicabilidade)")
    aviso: str = "Resposta gerada por IA a partir da base de conhecimento; confirme na norma vigente antes de decidir."


def _responder(pergunta: str, modo: str) -> Resposta:
    idx, be, por_id = ESTADO["idx"], ESTADO["be"], ESTADO["por_id"]
    r = pipelines.responder_agente(pergunta, idx, be) if modo == "agente" else pipelines.responder_rag(pergunta, idx, be)
    fontes = [
        Fonte(id=i, citacao=por_id[i].citacao(), url=por_id[i].url, licenca=por_id[i].licenca)
        for i in r.trecho_ids if i in por_id
    ]
    return Resposta(resposta=r.resposta, recusou=r.recusou, fontes=fontes, explicacao=r.trace)


@app.get("/saude")
def saude():
    return {"status": "ok", "trechos": len(ESTADO.get("trechos", [])), "backend": config.BACKEND, "llm": config.LLM_MODEL}


@app.post("/perguntar", response_model=Resposta)
def perguntar(p: Pergunta):
    t0 = time.time()
    try:
        out = _responder(p.pergunta, p.modo)
    except RuntimeError as e:  # Ollama fora do ar
        raise HTTPException(status_code=503, detail=str(e))
    log.info("POST /perguntar modo=%s len=%d recusou=%s %.2fs", p.modo, len(p.pergunta), out.recusou, time.time() - t0)
    return out


# ---------------------------------------------------------------- integração com o robô
class Evento(BaseModel):
    classe: Literal["livre", "aproximando", "obstaculo"]
    distancia_cm: Optional[float] = Field(default=None, ge=0, le=400)
    luminosidade: Optional[int] = Field(default=None, ge=0, le=4095, description="LDR 0 (escuro) a 4095 (claro)")


PERGUNTAS_CLASSE = {
    "obstaculo": [
        "O que significa a classe 'obstaculo' do modelo do robô e qual ação o robô toma?",
        "Quais obstáculos não podem existir na faixa livre da calçada e qual a largura mínima dela?",
    ],
    "aproximando": ["O que significa a classe 'aproximando' do modelo do robô?"],
    "livre": ["O que significa a classe 'livre' do modelo do robô?"],
}
PERGUNTA_LUZ = "Em quais valores do LDR o farol do robô liga e desliga?"
ACAO = {
    "obstaculo": "Registrar o ponto e encaminhar para verificação humana (zeladoria).",
    "aproximando": "Manter atenção; nenhuma ação automática além da redução de velocidade do robô.",
    "livre": "Nenhuma ação necessária.",
}


class RespostaEvento(BaseModel):
    classe: str
    iluminacao_insuficiente: Optional[bool]
    acao_recomendada: str
    explicacoes: List[Resposta]


@app.post("/evento", response_model=RespostaEvento)
def evento(e: Evento):
    perguntas = list(PERGUNTAS_CLASSE[e.classe])
    escuro = None
    if e.luminosidade is not None:
        escuro = e.luminosidade < 1200  # mesmo limiar de LIGAR o farol no firmware
        if escuro:
            perguntas.append(PERGUNTA_LUZ)
    try:
        exp = [_responder(q, "agente") for q in perguntas]
    except RuntimeError as err:
        raise HTTPException(status_code=503, detail=str(err))
    log.info("POST /evento classe=%s luz_baixa=%s", e.classe, escuro)
    return RespostaEvento(classe=e.classe, iluminacao_insuficiente=escuro, acao_recomendada=ACAO[e.classe], explicacoes=exp)
