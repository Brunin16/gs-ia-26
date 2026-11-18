"""Testes automatizados (sem LLM): base, casos, métricas, pipelines e API.
Rodar:  rodar.bat testes   |   ./rodar.sh testes
Eles validam a ENGENHARIA (esquemas, métricas, recusa, segurança da API). A qualidade do modelo
é medida nos notebooks com o Ollama."""
import json

import pytest
from fastapi.testclient import TestClient

from rotalivre_ai import config, kb, metrics, montar, pipelines
from rotalivre_ai.pipelines import Resp


@pytest.fixture(scope="module")
def ctx():
    return montar(cache=False)


def test_base_valida():
    trechos = kb.carregar_trechos()
    assert len(trechos) >= 25
    assert all(t.texto and t.fonte and t.url and t.licenca for t in trechos)


def test_casos_validos_e_balanceados():
    trechos, casos = kb.carregar_trechos(), kb.carregar_casos()
    assert kb.validar_casos(casos, trechos) == []
    assert sum(c["tipo"] == "nao_consta" for c in casos) >= 5
    assert len({c["id"] for c in casos}) == len(casos)


def test_gabarito_e_satisfeito_pelos_proprios_trechos():
    """Sanidade do gabarito: o texto do trecho de gabarito responde ao critério `deve_conter`
    (exceto casos em que a resposta é uma negação/síntese, conferidos à mão)."""
    trechos = {t.id: t for t in kb.carregar_trechos()}
    sintese = {"C05", "C11", "C24", "C26", "C22"}  # a resposta reescreve o trecho, não o copia
    for c in kb.carregar_casos():
        if c["tipo"] != "consta" or c["id"] in sintese:
            continue
        texto = config.normalizar(" ".join(trechos[t].texto for t in c["trechos_gabarito"]))
        for g in c["deve_conter"]:
            assert any(config.normalizar(a) in texto for a in g), (c["id"], g)


def test_recall_lexical_razoavel(ctx):
    trechos, be, idx = ctx
    casos = kb.carregar_casos()
    assert metrics.recall_at_k(idx, casos, 3, "bm25") >= 0.7  # BM25 independe do LLM


def test_metricas_alucinacao_numero_inventado(ctx):
    trechos, _, _ = ctx
    caso = {"id": "X", "tipo": "consta", "pergunta": "Qual a largura mínima da faixa livre?",
            "trechos_gabarito": ["T11"], "deve_conter": [["1,20"]]}
    boa = Resp("A largura mínima é 1,20 m.", ["T11"], False, True)
    ruim = Resp("A largura mínima é 0,90 m, ou 1,20 m.", ["T11"], False, True)
    assert metrics.avaliar(caso, boa, trechos)["acerto"] and not metrics.avaliar(caso, boa, trechos)["alucinou"]
    assert metrics.avaliar(caso, ruim, trechos)["alucinou"]


def test_numero_de_outro_trecho_real_citado_nao_e_alucinacao(ctx):
    trechos, _, _ = ctx
    caso = {"id": "X", "tipo": "consta", "pergunta": "Qual a largura mínima da faixa livre?",
            "trechos_gabarito": ["T11"], "deve_conter": [["1,20"]]}
    r = Resp("O mínimo é 1,20 m e o recomendado é 1,50 m.", ["T13"], False, True)   # T13 traz 1,20 e 1,50
    av = metrics.avaliar(caso, r, trechos)
    assert av["acerto"] and not av["alucinou"] and not av["citou_certo"]  # citou trecho válido, mas não o do gabarito


def test_metricas_nao_consta(ctx):
    trechos, _, _ = ctx
    caso = {"id": "N", "tipo": "nao_consta", "pergunta": "Qual a multa?", "trechos_gabarito": [], "deve_conter": []}
    assert metrics.avaliar(caso, Resp(pipelines.RECUSA, [], True, True), trechos)["acerto"]
    av = metrics.avaliar(caso, Resp("R$ 195,23", [], False, True), trechos)
    assert av["alucinou"] and not av["acerto"]


def test_json_invalido_detectado():
    r = pipelines._parse("isto não é json", "X")
    assert not r.json_valido


def test_agente_recusa_quando_abaixo_do_limiar(ctx):
    trechos, be, idx = ctx
    dentro = "Qual a largura mínima da faixa livre da calçada?"
    fora = "receita de bolo de cenoura com cobertura de chocolate"
    c_in, c_out = idx.cos_max(dentro), idx.cos_max(fora)
    assert c_in > c_out                       # o portão consegue separar os dois
    meio = (c_in + c_out) / 2
    r = pipelines.responder_agente(fora, idx, be, limiar=meio)
    assert r.recusou and r.resposta == pipelines.RECUSA and r.trace[-1]["passo"] == "recusa"
    assert not pipelines.responder_agente(dentro, idx, be, limiar=meio).recusou


def test_agente_responde_com_citacao_e_trace(ctx):
    trechos, be, idx = ctx
    r = pipelines.responder_agente("Qual a largura mínima da faixa livre da calçada?", idx, be, limiar=0.10)
    assert not r.recusou and r.trecho_ids and r.trace
    assert {t["passo"] for t in r.trace} >= {"reescrever", "portao", "busca_hibrida"}


def test_verificacao_deterministica_barra_numero_fora(ctx):
    trechos, be, idx = ctx
    hits = idx.buscar("faixa livre largura", k=2, metodo="bm25")
    r = Resp("A faixa livre deve ter 7,77 m.", [hits[0].trecho.id], False, True)
    ok, motivo = pipelines._fundamentada(r, hits, "pergunta")
    assert not ok and "7.77" in motivo


# ----------------------------------------------------------------- API
@pytest.fixture(scope="module")
def client():
    from api.main import app
    with TestClient(app) as c:
        yield c


def test_api_saude(client):
    assert client.get("/saude").json()["status"] == "ok"


def test_api_validacao_de_entrada(client):
    assert client.post("/perguntar", json={"pergunta": "oi"}).status_code == 422
    assert client.post("/perguntar", json={"pergunta": "x" * 301}).status_code == 422
    assert client.post("/evento", json={"classe": "explodiu"}).status_code == 422
    assert client.post("/evento", json={"classe": "livre", "luminosidade": 99999}).status_code == 422


def test_api_perguntar_e_evento(client):
    r = client.post("/perguntar", json={"pergunta": "Qual a largura mínima da faixa livre da calçada?"})
    assert r.status_code == 200 and "aviso" in r.json()
    e = client.post("/evento", json={"classe": "obstaculo", "distancia_cm": 12.5, "luminosidade": 800})
    assert e.status_code == 200
    corpo = e.json()
    assert corpo["iluminacao_insuficiente"] is True and "verificação humana" in corpo["acao_recomendada"]
    assert len(corpo["explicacoes"]) == 3  # 2 da classe + 1 do farol
