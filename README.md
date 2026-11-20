# RotaLivre AI

Assistente de acessibilidade de calçadas com **LLM local (Ollama)**, **RAG** e **agente verificador**.
Projeto da disciplina **Generative AI for Engineering** · Global Solution 2026.2 · CitizenTech · FIAP.

A IA responde perguntas sobre acessibilidade de calçadas **somente com base em uma base de conhecimento com fonte**, cita a fonte, **recusa** quando a resposta não está na base e explica os eventos do robô RotaLivre (obstáculo, aproximação, pouca luz).

O relatório da disciplina está em **[RELATORIO.md](RELATORIO.md)**.

## Integrantes

| Nome completo | RM |
| ------------- | -- |
| Bruno Eduardo Caputo Paulino | 558303 |
| Lucas Rodrigues | 98344 |
| Juan Pinheiro de França | 552202 |
| Kaiky Alvaro Miranda | 98118 |

---

## O que vai ser instalado

| Item | Para que serve | Tamanho aproximado |
| ---- | -------------- | ------------------ |
| Python 3.12 | roda o projeto | 100 MB |
| Ollama | roda os modelos de IA no seu computador | 1 a 2 GB |
| Modelo `qwen2.5:7b` | LLM que gera as respostas | 4,7 GB |
| Modelo `bge-m3` | embeddings (busca por significado) | 1,2 GB |
| Bibliotecas Python | numpy, pandas, FastAPI, Jupyter etc. | 500 MB |

**Requisitos:** cerca de 10 GB livres em disco e internet para os downloads. Uma placa NVIDIA com 8 GB de VRAM deixa tudo rápido; sem placa de vídeo também funciona, só que mais devagar. Nada usa Docker.

---
- [Link para o video](https://www.youtube.com/watch?v=PzD18DrZ8WA)
---
## Instalação no Windows, passo a passo

### Passo 1: instalar o Python 3.12

1. Acesse https://www.python.org/downloads/windows/ e baixe o **Windows installer (64-bit)** do Python 3.12.
2. Abra o instalador. **Na primeira tela, marque a caixa "Add python.exe to PATH"** e clique em **Install Now**.
3. Para conferir, abra um **novo** PowerShell (menu Iniciar, digite `PowerShell`) e rode:
   ```powershell
   py --version
   ```
   Deve aparecer `Python 3.12.x`.

### Passo 2: instalar o Ollama

1. Acesse https://ollama.com/download, escolha **Windows** e baixe o instalador.
2. Instale normalmente. Ao final, o Ollama fica aberto em segundo plano (ícone perto do relógio).
3. Para conferir, abra um **novo** PowerShell e rode:
   ```powershell
   ollama --version
   ```

### Passo 3: baixar o projeto

**Opção A, com Git** (instale em https://git-scm.com/download/win se ainda não tiver):
```powershell
cd C:\
mkdir projetos
cd projetos
git clone https://github.com/Brunin16/gs-ia-26.git RotaLivre-genai
```

**Opção B, sem Git:** no GitHub, clique em **Code → Download ZIP** e extraia em `C:\projetos\RotaLivre-genai`.

> Prefira uma pasta como `C:\projetos`. Pastas dentro do OneDrive podem travar a instalação durante a sincronização.

### Passo 4: rodar o instalador

Abra a pasta `C:\projetos\RotaLivre-genai` no Explorador de Arquivos e dê **dois cliques em `instalar.bat`**. Ele faz, em ordem:

1. encontra o Python 3.10 ou mais novo;
2. cria o ambiente virtual `.venv` dentro da pasta do projeto (nada é instalado no Python do sistema);
3. instala as bibliotecas do `requirements.txt`;
4. roda os testes automatizados (não precisam do Ollama);
5. baixa os modelos `qwen2.5:7b` e `bge-m3` no Ollama e faz uma chamada de teste em cada um.

Na primeira vez leva de 10 a 30 minutos, dependendo da internet. No fim deve aparecer **"Instalação concluída com sucesso"**. Se aparecer algum `[ERRO]` ou `[PENDENTE]`, a própria mensagem diz o que fazer; depois de corrigir, rode o `instalar.bat` de novo (as etapas já feitas passam rápido).

### Passo 5: conferir a instalação

Dê dois cliques em **`rodar.bat`** e escolha **1 - verificar**. As quatro linhas devem terminar com OK.

### Passo 6: rodar os notebooks (gera os resultados da disciplina)

1. Dê dois cliques em `rodar.bat` e escolha **2 - notebooks**. O Jupyter Lab abre no navegador.
2. Na barra lateral, entre em `notebooks/` e abra os notebooks **em ordem, de 01 a 06**.
3. Em cada um, use o menu **Run → Run All Cells**, espere terminar e salve com **Ctrl+S**.
   - O 03 calcula a busca e o limiar de recusa.
   - O 06 roda as três configurações nos 34 casos de teste e é o mais demorado (de 10 a 40 minutos).
4. Os resultados ficam em `avaliacao/resultados/`. Use-os para preencher o [RELATORIO.md](RELATORIO.md).
5. Para fechar o Jupyter, volte na janela preta e aperte **Ctrl+C**.

### Passo 7: subir a API

Dê dois cliques em `rodar.bat` e escolha **3 - api**. Abra http://localhost:8000/docs no navegador, clique em **POST /perguntar → Try it out**, troque o texto da pergunta e clique em **Execute**. Deixe essa janela aberta enquanto usar a API.

### Passo 8: ligar o robô (opcional)

Com a API rodando (passo 7), abra **outra** janela do `rodar.bat`:

- **4 - robo-sim:** simula o robô mandando eventos, não precisa do carrinho.
- **5 - robo:** conecta no carrinho real. Informe a porta (ex.: `COM5`). Antes, **feche o Monitor Serial da Arduino IDE** e ligue o modo TinyML no carrinho (botão **SELECT** no Dabble). O firmware do carrinho não precisa de nenhuma alteração.

### Passo 9: publicar no GitHub

Depois de rodar os notebooks e preencher o relatório:
```powershell
cd C:\projetos\RotaLivre-genai
git add .
git commit -m "Resultados dos notebooks e relatorio"
git push
```
Confira no GitHub que os notebooks aparecem **com as saídas** e que `avaliacao/resultados/` tem os arquivos gerados.

---

## Instalação no Linux e no macOS

1. **Python 3.10+**: no Ubuntu/Debian, `sudo apt install python3 python3-venv python3-pip`; no macOS, instale por https://www.python.org/downloads/macos/.
2. **Ollama**: no Linux, `curl -fsSL https://ollama.com/install.sh | sh`; no macOS, baixe o app em https://ollama.com/download e abra.
3. Baixe o projeto (passo 3) e, no terminal, dentro da pasta:
   ```bash
   chmod +x instalar.sh rodar.sh
   ./instalar.sh
   ./rodar.sh            # mesmo menu do Windows
   ```

---

## Instalação manual (os mesmos passos dos scripts, comando por comando)

Para quem prefere não usar os scripts. No **PowerShell**, dentro da pasta do projeto:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pytest
ollama pull qwen2.5:7b
ollama pull bge-m3
.venv\Scripts\python -m rotalivre_ai.verificar
.venv\Scripts\python -m jupyter lab
.venv\Scripts\python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
.venv\Scripts\python scripts\ponte_robo.py --simular
```

No Linux/macOS, troque `py -3.12` por `python3` e `.venv\Scripts\python` por `.venv/bin/python`.

---

## Usar um modelo menor (se a máquina for mais fraca)

No PowerShell:
```powershell
setx ROTALIVRE_LLM llama3.2:3b
```
Feche e abra o terminal, rode o `instalar.bat` de novo (ele baixa o modelo novo) e refaça os notebooks. Informe no relatório qual modelo foi usado.

## Problemas comuns

| Sintoma | Solução |
| ------- | ------- |
| `Python 3.10 ou mais novo nao foi encontrado` | Reinstale o Python marcando **Add python.exe to PATH** e abra um terminal novo. |
| Digitar `python` abre a Microsoft Store | Use o `instalar.bat` (ele usa o comando `py`), ou desative os "Aliases de execução de aplicativo" do Python nas configurações do Windows. |
| `O Ollama ainda nao esta instalado` logo depois de instalar | Feche a janela e abra o `instalar.bat` de novo, para o Windows recarregar o PATH. |
| `Ollama não respondeu em http://localhost:11434` | Abra o aplicativo **Ollama** pelo menu Iniciar e tente de novo. |
| Download do modelo falhou | Confira a internet e o espaço em disco; rode o `instalar.bat` de novo (o download continua). |
| Notebooks muito lentos | É normal sem placa de vídeo. Use o modelo menor (seção acima). |
| `Address already in use` ao subir a API | Já existe uma API aberta em outra janela; feche-a ou use essa. |
| A porta COM do carrinho dá erro de acesso | Feche o Monitor Serial da Arduino IDE e confira a porta no Gerenciador de Dispositivos. |

## Estrutura do projeto

```
RotaLivre-genai/
├── README.md              este guia
├── RELATORIO.md           relatório da disciplina
├── requirements.txt       bibliotecas Python
├── instalar.bat           instalador do Windows
├── rodar.bat              menu do Windows
├── instalar.sh, rodar.sh  equivalentes para Linux/macOS
├── pytest.ini             configuração dos testes
├── base/                  base de conhecimento (trechos.jsonl) e tabela de fontes (FONTES.md)
├── avaliacao/             casos de teste com gabarito e resultados/ gerados pelos notebooks
├── notebooks/             01 a 06, rodar em ordem
├── rotalivre_ai/          código: busca, RAG, agente, métricas e verificação da instalação
├── api/                   API FastAPI (/perguntar e /evento)
├── scripts/               ponte_robo.py (carrinho ou simulação → API)
└── tests/                 testes automatizados
```
