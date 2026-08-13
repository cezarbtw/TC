# EmotionLens

Aplicação web de apoio a consultas psicológicas que usa visão computacional para
identificar emoções faciais. Projeto de TCC de Ciência da Computação, dividido em
dois módulos independentes:

- **`frontend/`** — dashboard em React + Vite (upload de vídeo, gráficos, sessões).
- **`backend/`** — API em FastAPI que detecta faces e classifica emoções
  (YOLOv8-face + HSEmotion, via OpenCV).

## Stack

| Camada | Tecnologias |
|--------|-------------|
| Frontend | React 18, Vite, React Router DOM, Axios, react-chartjs-2 + Chart.js, CSS modularizado |
| Backend | FastAPI, Uvicorn, Pydantic v2, OpenCV, YOLOv8-face (ultralytics), HSEmotion (PyTorch), SQL Server (pyodbc) |

## Arquitetura do backend (em camadas: Router → Service → Persistência)

```
backend/app/
  rotas/          Routers finos (FastAPI) + injeção de dependência + validação
  servicos/       Regras de negócio e orquestração do fluxo
  dominio/        Entidades puras (sem Pydantic/FastAPI) — representam os dados/tabelas do banco
  esquemas/       Contratos de API (Pydantic) — o JSON que o frontend consome
  persistencia/   Repositório(s) + conexão com o SQL Server
  ia/             Pipeline de visão computacional (YOLOv8, HSEmotion, OpenCV, agregação)
  nucleo/         Config, logging, exceções
```

Fluxo de uma requisição: **Router → Service → Repositório (Persistência) →
Banco de Dados**, com o Service também orquestrando o pipeline de `ia/` na
análise do vídeo.

O Domínio (`dominio/`) usa nomes de campo em português (`nome`,
`arquivo_origem`, `predominante`...) e é independente de Pydantic/FastAPI. O
Schema de API (`esquemas/`) mantém os nomes de campo em inglês (`name`,
`source_file`, `predominant`...) para preservar o contrato já consumido pelo
frontend — a conversão entre os dois acontece explicitamente em
`servicos/servico_sessao.py::sessao_para_schema()`.

Não há interfaces abstratas (ABCs) entre as camadas: cada adapter de IA e o
repositório têm uma única implementação, então cada peça pode ser trocada
diretamente sem precisar de uma hierarquia de classes abstratas para isso.

## Pipeline de análise (HSEmotion)

1. Amostra o vídeo a **~5 FPS** (não processa todos os frames).
2. Detecta faces com **YOLOv8-face**; ignora frames sem face, com baixa
   confiança de detecção ou faces muito pequenas.
3. **Alinha** a face pelos olhos antes de classificar.
4. Classifica emoções com **HSEmotion** (modelo de 7 classes) — emoção
   predominante + probabilidades por frame.
5. Aplica **suavização temporal** (média móvel) para reduzir ruído quadro a
   quadro.
6. Agrega: emoção predominante da sessão, % por emoção, confiança média e
   timeline.

Os modelos são carregados **uma única vez na inicialização** do backend (não
a cada requisição) e usam **GPU automaticamente** quando disponível.

## Requisitos

### Backend
- **Python 3.11** (ou 3.10)
- **pip**
- **virtualenv** (`python -m venv`)
- (Opcional) GPU NVIDIA + CUDA — usa CPU automaticamente quando não há GPU

### Frontend
- **Node.js 18+**
- **npm**

## Como rodar

### 1) Backend (API)
```bash
cd backend
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # Linux/macOS/Git Bash
pip install -r requirements.txt
cp .env.example .env               # ajuste se necessário
uvicorn app.main:app --reload
```
API em `http://localhost:8000` — documentação em `http://localhost:8000/docs`.

> O peso do detector de faces (`yolov8n-face.pt`) já vem versionado no
> repositório. O peso do HSEmotion é baixado automaticamente na primeira
> inicialização (precisa de internet uma vez).

#### Aceleração por GPU (opcional)
Para usar GPU, instale o PyTorch com CUDA a partir do índice oficial antes
das demais dependências, por exemplo:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```
O código detecta a GPU automaticamente (`EMOTIONLENS_DISPOSITIVO=auto`).

### 2) Frontend (dashboard)
```bash
cd frontend
npm install
cp .env.example .env               # ajuste se necessário
npm run dev
```
App em `http://localhost:5173`.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/sessions/upload` | Recebe **vídeo**; retorna objeto de sessão agregado (chaves em PT) |
| `GET`  | `/sessions` | Lista as sessões analisadas |
| `GET`  | `/sessions/{id}` | Detalha uma sessão |
| `GET`  | `/health` | Verificação de saúde |

## Variáveis de ambiente

Nenhuma configuração sensível ou específica de máquina fica no código: cada
módulo tem um `.env.example` versionado, que deve ser copiado para um `.env`
local (este **não** é versionado).

### `backend/.env` (prefixo `EMOTIONLENS_`)
| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `EMOTIONLENS_ORIGENS_CORS` | Origens permitidas (CORS), em JSON | `["http://localhost:5173"]` |
| `EMOTIONLENS_TAMANHO_MAXIMO_UPLOAD_BYTES` | Tamanho máximo de upload | `209715200` (200 MB) |
| `EMOTIONLENS_DISPOSITIVO` | Dispositivo de inferência (`auto`/`cpu`/`cuda`) | `auto` |
| `EMOTIONLENS_FPS_ALVO` | Taxa de amostragem do vídeo (frames por segundo analisados) | `5` |
| `EMOTIONLENS_MAX_FRAMES_ANALISADOS` | Teto de frames analisados por vídeo | `600` |
| `EMOTIONLENS_CHAVE_CRIPTOGRAFIA` | Chave da camada AES-256-GCM usada para proteger a análise no banco | obrigatório em ambiente real |
| `EMOTIONLENS_CHAVE_MCE` | Chave da camada autoral MCE aplicada antes do AES | obrigatório em ambiente real |

> Lista completa das variáveis (incluindo conexão com o SQL Server) em
> [`backend/.env.example`](backend/.env.example).

## Criptografia dos dados de análise

Os dados detalhados da análise emocional são protegidos antes de serem gravados
no SQL Server. O backend aplica duas camadas:

1. **MCE (Mapeamento Criptográfico Emocional)** — camada autoral do projeto. Ela
   transforma a estrutura emocional, renomeando emoções para códigos internos,
   reordenando esses códigos por chave e removendo os nomes semânticos das
   emoções antes da criptografia principal.
2. **AES-256-GCM** — camada criptográfica pronta e padronizada, implementada com
   a biblioteca `cryptography`. Ela cifra o resultado da MCE e também valida a
   integridade dos dados na leitura.

O banco armazena um envelope JSON criptografado em
`dbo.sessoes.analise_criptografada`. A API descriptografa esse envelope na camada
de persistência, então o frontend continua consumindo o mesmo contrato de
`probabilities` e `timeline`.

### `frontend/.env`
| Variável | Descrição |
|----------|-----------|
| `VITE_API_URL` | Endpoint do backend FastAPI (ex.: `http://localhost:8000`) |

## Integração frontend ↔ backend

O frontend consome os endpoints acima diretamente
(`frontend/src/services/sessionsService.js`), usando `VITE_API_URL` para
montar as chamadas.

## Estrutura do repositório
```
TC/
  backend/    API FastAPI (rotas → serviços → persistência)
  frontend/   Dashboard React + Vite
```
