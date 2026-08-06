/*
    EmotionLens — dados de referência (obrigatório, não é dado de exemplo).

    Popula dbo.emocoes com as 7 emoções suportadas pelo pipeline HSEmotion.
    As FKs de dbo.sessoes e dbo.pontuacoes_emocao_sessao dependem destas linhas
    existirem — execute este script antes de qualquer sessão ser persistida.

    Idempotente: pode ser reexecutado sem duplicar ou falhar.
*/

USE EmotionLensDB;
GO

MERGE dbo.emocoes AS target
USING (VALUES
    (1, N'feliz',    N'happy',    1),
    (2, N'triste',   N'sad',      2),
    (3, N'raiva',    N'angry',    3),
    (4, N'surpresa', N'surprise', 4),
    (5, N'medo',     N'fear',     5),
    (6, N'nojo',     N'disgust',  6),
    (7, N'neutro',   N'neutral',  7)
) AS source (id, codigo, rotulo_en, ordem)
ON target.id = source.id
WHEN MATCHED THEN
    UPDATE SET codigo = source.codigo, rotulo_en = source.rotulo_en, ordem = source.ordem
WHEN NOT MATCHED THEN
    INSERT (id, codigo, rotulo_en, ordem)
    VALUES (source.id, source.codigo, source.rotulo_en, source.ordem);
GO
