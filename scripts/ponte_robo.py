"""Ponte ESP32 -> API: lê o Serial do carrinho (firmware do repositório MakerLab, sem alterações)
e envia um evento à API a cada MUDANÇA de classe do modelo TinyML.

Linhas do firmware que são lidas:
    [12345 ms] [TINYML] ACAO -> obstaculo
    [12345 ms] [LDR] valor=900 (farol ON)

Uso:
    python scripts/ponte_robo.py --porta COM5                 # com o carrinho no modo TinyML (SELECT)
    python scripts/ponte_robo.py --simular                    # demonstração sem hardware
Nota: só distância/luminosidade/classe saem do carrinho. Nenhum dado pessoal trafega.
"""
import argparse
import json
import re
import sys
import time
import urllib.request

RE_ACAO = re.compile(r"\[TINYML\]\s+ACAO\s+->\s+(livre|aproximando|obstaculo)")
RE_LDR = re.compile(r"\[LDR\]\s+valor=(\d+)")
RE_FRENTE = re.compile(r"frente=([\d.]+)cm")


def enviar(api, classe, luz, dist):
    corpo = {"classe": classe}
    if luz is not None:
        corpo["luminosidade"] = luz
    if dist is not None:
        corpo["distancia_cm"] = dist
    req = urllib.request.Request(f"{api}/evento", data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        saida = json.load(r)
    print(f"\n>>> evento {corpo}\n    ação recomendada: {saida['acao_recomendada']}")
    for e in saida["explicacoes"]:
        fontes = "; ".join(f["citacao"] for f in e["fontes"]) or "sem fonte"
        print(f"    - {e['resposta']}  [{fontes}]")


def linhas_serial(porta, baud):
    import serial  # pip install pyserial

    with serial.Serial(porta, baud, timeout=1) as s:
        while True:
            l = s.readline().decode("utf-8", errors="ignore").strip()
            if l:
                yield l


def linhas_simuladas():
    roteiro = [
        "[1000 ms] [LDR] valor=2500 (farol OFF)", "[1500 ms] [TINYML] ACAO -> livre",
        "[4000 ms] [LDR] valor=900 (farol ON)", "[4500 ms] [PROX] auto | frente=14.0cm (ATENCAO)",
        "[5000 ms] [TINYML] ACAO -> obstaculo",
    ]
    for l in roteiro:
        time.sleep(1)
        yield l


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://localhost:8000")
    ap.add_argument("--porta")
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()
    if not a.simular and not a.porta:
        sys.exit("Informe --porta (ex.: COM5) ou use --simular")
    luz = dist = ultima = None
    for l in (linhas_simuladas() if a.simular else linhas_serial(a.porta, a.baud)):
        if m := RE_LDR.search(l):
            luz = int(m.group(1))
        if m := RE_FRENTE.search(l):
            dist = float(m.group(1))
        if m := RE_ACAO.search(l):
            if m.group(1) != ultima:
                ultima = m.group(1)
                enviar(a.api, ultima, luz, dist)


if __name__ == "__main__":
    main()
