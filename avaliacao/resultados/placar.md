Modelo: `qwen2.5:7b` | embeddings: `bge-m3` | limiar: 0.694 | casos: 34

| configuração   |   acerto (%) |   alucinação (%) |   JSON válido (%) |   citação correta (%) |   recusa correta em 'não consta' (%) |   recusa indevida em 'consta' (%) |   casos |
|:---------------|-------------:|-----------------:|------------------:|----------------------:|-------------------------------------:|----------------------------------:|--------:|
| A_sem_contexto |         17.6 |             52.9 |               100 |                  23.5 |                                   25 |                              11.5 |      34 |
| B_rag_simples  |         94.1 |              0   |               100 |                  91.2 |                                  100 |                               3.8 |      34 |
| C_agente       |         76.5 |              0   |               100 |                  76.5 |                                  100 |                              30.8 |      34 |
