# Resultados (gerados pelos notebooks com o Ollama)

Esta pasta é preenchida ao rodar os notebooks **com o backend `ollama`** (nunca com o `stub`):

| Arquivo | Gerado por | Conteúdo |
| ------- | ---------- | -------- |
| `recall.csv`, `recall.png` | notebook 03 | recall@1 e recall@3 por tipo de busca |
| `limiar.json`, `limiar.png` | notebook 03 | limiar de recusa calibrado (Youden J) |
| `placar.csv`, `placar.md`, `placar.png` | notebook 06 | placar das 3 configurações |
| `avaliacao_por_caso.csv`, `respostas.json` | notebook 06 | resultado e trace por caso e configuração |
| `erros_candidatos.md` | notebook 06 | erros reais para escolher os 5 do relatório |

Faça o commit destes arquivos junto com os notebooks (com as saídas salvas).
