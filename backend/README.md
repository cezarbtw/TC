# EmotionLens — Backend

API de apoio a consultas psicológicas: recebe imagens/vídeos, detecta faces e
classifica emoções, retornando dados estruturados para o frontend React.

## Requisitos

- Python 3.11 (ou 3.10)
- pip
- virtualenv (`python -m venv`)
- (Opcional) GPU NVIDIA + CUDA para aceleração — o código usa CPU automaticamente
  quando não há GPU.

## Stack
- Python **3.10 ou 3.11**
- FastAPI + Uvicorn
- Pydantic v2 / pydantic-settings
- OpenCV (`opencv-python-headless`)
- **YOLOv8-face** (ultralytics) para detecção/alinhamento de faces
- **HSEmotion** (PyTorch) para classificação emocional

## Pipeline de análise (HSEmotion)

1. Amostra o vídeo a **~5 FPS** (não processa todos os frames).
2. Detecta faces com **YOLOv8-face**; ignora frames sem face, com baixa confiança
   de detecção ou faces muito pequenas.
3. **Alinha** a face pelos olhos antes de classificar.
4. Classifica emoções com **HSEmotion** (modelo de 7 classes) — emoção
   predominante + probabilidades por frame.
5. Aplica **suavização temporal** (média móvel) para reduzir ruído quadro a quadro.
6. Agrega: emoção predominante da sessão, % por emoção, confiança média e timeline.

Os modelos são carregados **uma única vez na inicialização** do backend (não a
cada requisição) e usam **GPU automaticamente** quando disponível.

## Arquitetura (Clean Architecture / Hexagonal)

```
app/
  api/            Routers finos + injeção de dependência + validação
  application/    Casos de uso (orquestração)
  core/           Config, logging, exceções
  domain/         Entidades, schemas (contrato), portas, regras puras
  infrastructure/ Adapters concretos (YOLOv8, HSEmotion, OpenCV, repositório)
```

Regra central: as camadas internas (domain/application) **não** conhecem
FastAPI/PyTorch/OpenCV. A infraestrutura implementa as **portas**
(`domain/services/ports.py`), injetadas em `api/deps/dependencies.py`. Por isso a
suíte de testes roda sem os modelos de IA instalados.

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

# 2) Dependências (torch/torchvision instalam a build de CPU por padrão)
pip install -r requirements.txt

# 3) Subir a API (a partir da pasta backend/)
uvicorn app.main:app --reload
```

- API: <http://localhost:8000>
- Documentação interativa (Swagger): <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

> Na **primeira** inicialização, os pesos do YOLOv8-face e do HSEmotion são
> baixados automaticamente (precisa de internet uma vez).

### Aceleração por GPU (opcional)
Para usar GPU, instale o PyTorch com CUDA a partir do índice oficial antes das
demais dependências, por exemplo:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```
O código detecta a GPU automaticamente (`EMOTIONLENS_DEVICE=auto`).

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

Os testes usam **fakes** das portas — não exigem os modelos de IA (torch,
ultralytics, hsemotion) nem OpenCV:

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
