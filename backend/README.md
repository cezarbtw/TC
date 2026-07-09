# EmotionLens — Backend

API de apoio a consultas psicológicas: recebe imagens/vídeos, detecta faces e
classifica emoções (DeepFace + OpenCV), retornando dados estruturados para o
frontend React.

## Requisitos

- Python 3.11 (ou 3.10) — o DeepFace/TensorFlow **não** funcionam no 3.8/3.9
- pip
- virtualenv (`python -m venv`)

## Stack
- Python **3.10 ou 3.11** (o DeepFace/TensorFlow **não** funcionam no 3.8)
- FastAPI + Uvicorn
- Pydantic v2 / pydantic-settings
- OpenCV (`opencv-python-headless`)
- DeepFace (backend TensorFlow-CPU)

## Arquitetura (Clean Architecture / Hexagonal)

```
app/
  api/            Routers finos + injeção de dependência + validação
  application/    Casos de uso (orquestração)
  core/           Config, logging, exceções
  domain/         Entidades, schemas (contrato), portas, regras puras
  infrastructure/ Adapters concretos (DeepFace, OpenCV, repositório)
```

Regra central: as camadas internas (domain/application) **não** conhecem
FastAPI/DeepFace/OpenCV. A infraestrutura implementa as **portas**
(`domain/services/ports.py`), injetadas em `api/deps/dependencies.py`. Por isso a
suíte de testes roda sem TensorFlow.

## Como executar

> Pré-requisito: ter o Python 3.10 ou 3.11 instalado. **Não** use o 3.8.

```bash
cd backend

# 1) Ambiente virtual (ajuste o executável conforme sua instalação)
py -3.11 -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Git Bash / Linux / macOS:
# source .venv/bin/activate

# 2) Dependências
pip install -r requirements.txt

# 3) Subir a API (a partir da pasta backend/)
uvicorn app.main:app --reload
```

- API: <http://localhost:8000>
- Documentação interativa (Swagger): <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

> Na **primeira** análise, o DeepFace baixa os pesos do modelo de emoção para
> `~/.deepface/weights` (precisa de internet uma vez).

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/emotion/predict` | Recebe **imagem**; retorna faces + emoções (chaves em inglês) |
| `POST` | `/sessions/upload` | Recebe **vídeo**; retorna objeto `Session` agregado (chaves em PT) |
| `GET`  | `/sessions` | Lista as sessões analisadas |
| `GET`  | `/sessions/{id}` | Detalha uma sessão |
| `GET`  | `/health` | Verificação de saúde |

### Exemplo — `POST /emotion/predict`
```json
{
  "success": true,
  "faces_detected": 1,
  "dominant_emotion": "happy",
  "confidence": 94.5,
  "emotions": { "happy": 94.5, "neutral": 3.2, "sad": 1.1, "angry": 0.5,
                "fear": 0.4, "surprise": 0.3, "disgust": 0.0 },
  "faces": [ /* detalhe por face */ ]
}
```

## Testes

Os testes usam **fakes** das portas — não exigem DeepFace/OpenCV/TensorFlow:

```bash
pip install -r requirements-dev.txt
pytest
```

## Integração com o frontend

O frontend já chama exatamente estes endpoints (`frontend/src/services/sessionsService.js`).
Basta desligar o modo mock:

```
# frontend/.env
VITE_API_URL=http://localhost:8000
VITE_USE_MOCK=false
```
