# EmotionLens — Back End

API REST para análise de expressões faciais em vídeos.  
**TCC — Ciência da Computação | 2026**

---

## Stack

| Camada         | Tecnologia                        |
|----------------|-----------------------------------|
| API            | FastAPI + Uvicorn                 |
| IA / Visão     | DeepFace + OpenCV                 |
| Banco de dados | SQLite (via sqlite3 nativo)        |
| Validação      | Pydantic v2                       |

---

## Estrutura do Projeto

```
emotionlens-backend/
├── main.py                  # Entrada da aplicação FastAPI
├── database.py              # Inicialização e conexão com SQLite
├── schemas.py               # Modelos Pydantic (request / response)
├── requirements.txt         # Dependências Python
├── app.js                   # Front end atualizado (copie para a pasta do HTML)
├── routers/
│   ├── upload.py            # POST /api/upload
│   └── sessions.py          # GET/DELETE /api/sessions
├── utils/
│   └── video_processor.py   # Motor DeepFace — extração de frames e análise
└── uploads/                 # Vídeos recebidos (criado automaticamente)
```

---

## Instalação

### 1. Pré-requisitos

- Python 3.10 ou superior
- pip atualizado: `pip install --upgrade pip`

### 2. Instalar dependências

```bash
cd emotionlens-backend
pip install -r requirements.txt
```

> **Atenção:** O DeepFace baixa os modelos de IA na primeira execução (~500 MB).  
> Mantenha conexão com a internet na primeira análise.

### 3. Subir o servidor

```bash
uvicorn main:app --reload --port 8000
```

O servidor estará disponível em: **http://localhost:8000**

---

## Endpoints da API

| Método   | Rota                      | Descrição                              |
|----------|---------------------------|----------------------------------------|
| `GET`    | `/`                       | Health check                           |
| `POST`   | `/api/upload`             | Envia vídeo e dispara análise          |
| `GET`    | `/api/sessions`           | Lista todas as sessões (resumo)        |
| `GET`    | `/api/sessions/{id}`      | Detalha uma sessão (com timeline)      |
| `DELETE` | `/api/sessions/{id}`      | Remove uma sessão                      |

Documentação interativa (Swagger): **http://localhost:8000/docs**

---

## Exemplo de resposta — `GET /api/sessions/1`

```json
{
  "id": 1,
  "name": "Sessão 01",
  "filename": "entrevista.mp4",
  "date": "2026-04-10",
  "duration": "02:34",
  "frames": 154,
  "predominant": "feliz",
  "confidence": 72.5,
  "probabilities": {
    "feliz": 72.5,
    "triste": 8.0,
    "raiva": 3.0,
    "surpresa": 5.0,
    "medo": 2.0,
    "nojo": 1.0,
    "neutro": 8.5
  },
  "timeline": {
    "feliz":    [65.2, 70.1, 80.3, ...],
    "triste":   [10.0,  8.5,  5.2, ...],
    ...
  }
}
```

---

## Conectar o Front End

1. Copie o arquivo `app.js` (gerado aqui) para a pasta do seu `index.html`, **substituindo** o original.
2. Certifique-se de que o servidor está rodando em `http://localhost:8000`.
3. Abra o `index.html` via servidor local (ex: extensão Live Server do VS Code) — não abra como arquivo direto por conta das restrições de CORS.

---

## Ajuste Fino

### Taxa de amostragem de frames

Em `utils/video_processor.py`, a variável `SAMPLE_RATE` controla quantos frames por segundo são analisados:

```python
SAMPLE_RATE = 1   # 1 frame/s → rápido, menos preciso
SAMPLE_RATE = 2   # 2 frames/s → mais preciso, mais lento
```

### Origem permitida (CORS)

Em `main.py`, troque `allow_origins=["*"]` pela URL real do front end em produção:

```python
allow_origins=["http://localhost:5500"]
```

---

## Observações Acadêmicas

- O banco de dados `emotionlens.db` é criado automaticamente na primeira execução.
- Os vídeos ficam em `/uploads/` com nomes UUID para evitar conflitos.
- O DeepFace usa o modelo **Facenet** por padrão, com boa acurácia para 7 emoções básicas.
- `enforce_detection=False` evita que frames sem rosto visível interrompam o processamento.
