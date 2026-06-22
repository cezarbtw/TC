"""
Schemas Pydantic — define o formato dos dados que a API recebe e retorna.
O front end consome exatamente esses campos.
"""

from pydantic import BaseModel
from typing import Dict, List


# ─── Resposta de uma sessão completa ──────────────────────────────────────────

class EmotionProbabilities(BaseModel):
    feliz:    float
    triste:   float
    raiva:    float
    surpresa: float
    medo:     float
    nojo:     float
    neutro:   float


class SessionDetail(BaseModel):
    id:           int
    name:         str
    filename:     str
    date:         str           # YYYY-MM-DD
    duration:     str           # MM:SS
    frames:       int
    predominant:  str
    confidence:   float
    probabilities: EmotionProbabilities
    timeline:     Dict[str, List[float]]   # {"feliz": [12, 8, ...], ...}


# ─── Resposta resumida (para listagem) ────────────────────────────────────────

class SessionSummary(BaseModel):
    id:          int
    name:        str
    date:        str
    duration:    str
    frames:      int
    predominant: str
    confidence:  float


# ─── Resposta do upload ───────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    message:    str
    session_id: int
    session:    SessionDetail
