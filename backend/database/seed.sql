/*
    EmotionLens — dados de referência (obrigatório, não é dado de exemplo).

    Popula dbo.emotions com as 7 emoções suportadas pelo pipeline HSEmotion.
    As FKs de dbo.sessions e dbo.session_emotion_scores dependem destas linhas
    existirem — execute este script antes de qualquer sessão ser persistida.

    Idempotente: pode ser reexecutado sem duplicar ou falhar.
*/

USE EmotionLensDB;
GO

MERGE dbo.emotions AS target
USING (VALUES
    (1, N'feliz',    N'happy',    1),
    (2, N'triste',   N'sad',      2),
    (3, N'raiva',    N'angry',    3),
    (4, N'surpresa', N'surprise', 4),
    (5, N'medo',     N'fear',     5),
    (6, N'nojo',     N'disgust',  6),
    (7, N'neutro',   N'neutral',  7)
) AS source (id, code, label_en, sort_order)
ON target.id = source.id
WHEN MATCHED THEN
    UPDATE SET code = source.code, label_en = source.label_en, sort_order = source.sort_order
WHEN NOT MATCHED THEN
    INSERT (id, code, label_en, sort_order)
    VALUES (source.id, source.code, source.label_en, source.sort_order);
GO
