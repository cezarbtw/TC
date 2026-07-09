"""Schema de resposta de Sessão.

Espelha EXATAMENTE o objeto que o frontend consome
(frontend/src/utils/mockData.js e sessionsService.js): campos ``id``, ``name``,
``sourceFile`` (camelCase), ``date``, ``duration``, ``frames``, ``predominant``,
``confidence``, ``probabilities`` e ``timeline``, com chaves de emoção em
português.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class SessionSchema(BaseModel):
    id: int
    name: str
    source_file: str = Field(serialization_alias="sourceFile")
    date: str
    duration: str
    frames: int
    predominant: str
    confidence: float
    probabilities: dict[str, float]
    timeline: dict[str, list[float]]

    # populate_by_name permite construir por nome do atributo (source_file);
    # o FastAPI serializa por alias (by_alias=True por padrão), gerando
    # "sourceFile" no JSON — compatível com o frontend.
    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Sessão 01",
                "sourceFile": "consulta_2026-07-09.mp4",
                "date": "2026-07-09",
                "duration": "02:34",
                "frames": 154,
                "predominant": "feliz",
                "confidence": 72.0,
                "probabilities": {
                    "feliz": 72.0,
                    "triste": 8.0,
                    "raiva": 3.0,
                    "surpresa": 5.0,
                    "medo": 2.0,
                    "nojo": 1.0,
                    "neutro": 9.0,
                },
                "timeline": {
                    "feliz": [70.0, 72.0, 74.0],
                    "triste": [9.0, 8.0, 7.0],
                    "raiva": [3.0, 3.0, 3.0],
                    "surpresa": [5.0, 5.0, 5.0],
                    "medo": [2.0, 2.0, 2.0],
                    "nojo": [1.0, 1.0, 1.0],
                    "neutro": [10.0, 9.0, 8.0],
                },
            }
        },
    }
