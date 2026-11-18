# Base de conhecimento: fontes, formato, licença e número de trechos

Total: **31 trechos** de **14 fontes**. Cada trecho em `trechos.jsonl` tem `id`, `texto`, `fonte`, `referencia`, `url`, `licenca` e `tema`.

| Fonte | Formato | Licença / condição de uso | Nº de trechos | IDs |
| ----- | ------- | ------------------------- | ------------: | --- |
| [Lei 13.146/2015 (Lei Brasileira de Inclusão)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2015/lei/l13146.htm) | HTML/PDF | Domínio público (texto de lei, Lei 9.610/1998, art. 8º, IV) | 3 | T01, T02, T03 |
| [Lei 9.503/1997 (Código de Trânsito Brasileiro)](https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm) | HTML/PDF | Domínio público (texto de lei, Lei 9.610/1998, art. 8º, IV) | 1 | T04 |
| [IBGE, Censo 2022: Brasil tem 14,4 milhões de pessoas com deficiência (Agência de Notícias, 23/05/2025)](https://agenciadenoticias.ibge.gov.br) | Notícia web | Resumo parafraseado de divulgação do IBGE (dados abertos); citar a fonte | 4 | T05, T06, T07, T08 |
| [Agência Brasil/Band, Brasil tem 14,4 milhões de pessoas com deficiência (23/05/2025)](https://www.band.com.br/noticias/brasil-tem-144-milhoes-de-pessoas-com-deficiencia-202505231006) | Notícia web | Resumo parafraseado de divulgação do IBGE (dados abertos); citar a fonte | 1 | T09 |
| [Prefeitura de Belo Horizonte, Cartilha de Acessibilidade (resume a ABNT NBR 9050)](https://prefeitura.pbh.gov.br/sites/default/files/estrutura-de-governo/politica-urbana/Cartilha-Acessibilidade%20(2).pdf) | PDF | Resumo parafraseado de publicação oficial/institucional; citar a fonte. A norma ABNT original é protegida e não é reproduzida | 3 | T10, T11, T12 |
| [Instituto de Engenharia, palestra ABNT NBR 16537 / NBR 9050:2020 calçada](https://institutodeengenharia.org.br/site/wp-content/uploads/2024/09/PALESTRA-INSTITUTO-ENGENHARIA-ABNT-NBR-16537.pdf) | PDF | Resumo parafraseado de publicação oficial/institucional; citar a fonte. A norma ABNT original é protegida e não é reproduzida | 1 | T13 |
| [AGU, Laudo de acessibilidade PR/Curitiba (cita itens da NBR 9050/2020)](https://www.gov.br/agu/pt-br/acesso-a-informacao/acoeseprogramas/acessbilidade-nas-edificacoes-da-agu/pr-laudo-curitiba-pf-pdf.pdf) | PDF | Resumo parafraseado de publicação oficial/institucional; citar a fonte. A norma ABNT original é protegida e não é reproduzida | 3 | T14, T15, T16 |
| [Sudeco, Declaração de Conformidade em Acessibilidade (lista de verificação NBR 9050)](https://www.gov.br/sudeco/pt-br/acesso-a-informacao/convenios-e-transferencias/sou-convenente-quero-executar-um-convenio-ou-outro-instrumento/modelos-de-declaracoes/DeclaraodeAcessibilidaderevJunho23.docx) | DOCX | Resumo parafraseado de publicação oficial/institucional; citar a fonte. A norma ABNT original é protegida e não é reproduzida | 1 | T17 |
| [CREA-RN, Manual do Síndico, parte 2 (calçadas e travessias)](https://crea-rn.org.br/storage/documents/manual-do-sindico-parte2.pdf) | PDF | Resumo parafraseado de publicação oficial/institucional; citar a fonte. A norma ABNT original é protegida e não é reproduzida | 3 | T18, T19, T20 |
| [Prefeitura de Arapiraca, Cartilha de calçadas (cita ABNT NBR 9050/20)](https://web.arapiraca.al.gov.br/wp-content/uploads/2023/07/Cartilha.pdf) | PDF | Resumo parafraseado de publicação oficial/institucional; citar a fonte. A norma ABNT original é protegida e não é reproduzida | 1 | T21 |
| [Prefeitura de São Paulo, Cartilha de calçadas](https://www.prefeitura.sp.gov.br/cidade/secretarias/upload/CARTILHA.pdf) | PDF | Resumo parafraseado de publicação oficial/institucional; citar a fonte. A norma ABNT original é protegida e não é reproduzida | 2 | T22, T23 |
| [Prefeitura de Balneário Camboriú, norma sobre calçadas (cita NBR 16537:2024)](https://www.bc.sc.gov.br/arquivos/conteudo_downloads/ZN2AC4MG.pdf) | PDF | Resumo parafraseado de publicação oficial/institucional; citar a fonte. A norma ABNT original é protegida e não é reproduzida | 1 | T24 |
| [HU-UNIVASF/gov.br, Laudo padrão de acessibilidade (NBR 9050)](https://www.gov.br/hubrasil/pt-br/hospitais-universitarios/regiao-nordeste/hu-univasf/governanca/LaudoPadro_Acessibilidade_HUUNIVASF_PE.pdf) | PDF | Resumo parafraseado de publicação oficial/institucional; citar a fonte. A norma ABNT original é protegida e não é reproduzida | 1 | T25 |
| Projeto RotaLivre, documentação (README e dataset/LEIAME_dataset.txt do repositório MakerLab) | Markdown/TXT | Autoria da equipe (documentação do projeto RotaLivre) | 6 | T26, T27, T28, T29, T30, T31 |

## Observações

- **Texto de lei** (LBI e CTB) é de domínio público no Brasil (Lei 9.610/1998, art. 8º, IV).
- A **ABNT NBR 9050** é protegida por direitos autorais e **não é reproduzida**. Os trechos de norma são resumos parafraseados de cartilhas e laudos públicos de órgãos oficiais que citam os requisitos; confira sempre a edição vigente da norma.
- Os trechos de dados do IBGE são resumos parafraseados com citação da fonte.
- Os trechos `robo` descrevem o próprio dispositivo (autoria da equipe) e permitem ao assistente explicar os eventos do robô.
- **Lacunas propositais:** a base **não** contém valor de multa em reais, iluminância (lux), distância entre postes, inclinação longitudinal máxima, ciclovias, vagas de estacionamento nem dados por estado. Perguntas sobre isso devem ser **recusadas** (casos `nao_consta` em `avaliacao/casos_teste.jsonl`).
