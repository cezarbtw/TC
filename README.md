# EmotionLens

Aplicação web de apoio a consultas psicológicas que usa visão computacional para
identificar emoções faciais. Projeto de TCC de Ciência da Computação, dividido em
dois módulos independentes:

- **`frontend/`** — dashboard em React + Vite (upload de vídeo, gráficos, sessões).
- **`backend/`** — API em FastAPI que detecta faces e classifica emoções
  (DeepFace + OpenCV).

## Requisitos

### Backend
- **Python 3.11** (ou 3.10) — o DeepFace/TensorFlow **não** funcionam no Python 3.8/3.9
- **pip**
- **virtualenv** (`python -m venv`)

### Frontend
- **Node.js 18+**
- **npm**

## Stack

| Camada | Tecnologias |
|--------|-------------|
| Frontend | React 18, Vite, React Router DOM, Axios, react-chartjs-2 + Chart.js, CSS modularizado |
| Backend | FastAPI, Uvicorn, Pydantic v2, OpenCV, DeepFace (TensorFlow-CPU) |

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

> Detalhes completos (arquitetura, endpoints, testes) em [`backend/README.md`](backend/README.md).

### 2) Frontend (dashboard)
```bash
cd frontend
npm install
cp .env.example .env               # ajuste se necessário
npm run dev
```
App em `http://localhost:5173`.

## Variáveis de ambiente

Nenhuma configuração sensível ou específica de máquina fica no código: cada módulo
tem um `.env.example` versionado, que deve ser copiado para um `.env` local (este
**não** é versionado).

### `backend/.env` (prefixo `EMOTIONLENS_`)
| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `EMOTIONLENS_CORS_ORIGINS` | Origens permitidas (CORS), em JSON | `["http://localhost:5173"]` |
| `EMOTIONLENS_MAX_UPLOAD_BYTES` | Tamanho máximo de upload | `209715200` (200 MB) |
| `EMOTIONLENS_DETECTOR_BACKEND` | Detector de faces do DeepFace | `opencv` |
| `EMOTIONLENS_FRAME_SAMPLE_COUNT` | Frames amostrados por vídeo | `30` |
| `EMOTIONLENS_MAX_FRAMES_ANALYZED` | Teto de frames por vídeo | `300` |

### `frontend/.env`
| Variável | Descrição |
|----------|-----------|
| `VITE_API_URL` | Endpoint do backend FastAPI (ex.: `http://localhost:8000`) |
| `VITE_USE_MOCK` | `true` = dados mock · `false` = consumir a API real |

## Integração frontend ↔ backend

O frontend consome os endpoints expostos pelo backend. Para deixar de usar os
dados mock e passar a consumir a API, defina no `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK=false
```
Endpoints consumidos:
- `GET  /sessions` — lista de sessões
- `GET  /sessions/:id` — detalhe de uma sessão
- `POST /sessions/upload` — envio de vídeo (multipart/form-data)

Endpoint adicional (análise de imagem única, demonstrável via Swagger):
- `POST /emotion/predict`

## Estrutura do repositório
```
TC/
  backend/    API FastAPI (Clean Architecture) — ver backend/README.md
  frontend/   Dashboard React + Vite
  docs/       Documentação (api, arquitetura, lgpd)
```
