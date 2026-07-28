/*
    EmotionLens — índices de suporte às consultas do repositório.

    Execute após constraints.sql.
*/

USE EmotionLensDB;
GO

-- Suporta list_all(): sessões ativas (não deletadas), mais recentes primeiro.
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_sessions_active_id')
    CREATE INDEX IX_sessions_active_id
        ON dbo.sessions (id DESC)
        WHERE deleted_at IS NULL;
GO

-- Suporta futuras consultas/relatórios por período.
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_sessions_session_date')
    CREATE INDEX IX_sessions_session_date ON dbo.sessions (session_date);
GO

-- Suporta agregações por emoção (ex.: score médio de 'raiva' entre sessões).
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_scores_emotion_id')
    CREATE INDEX IX_scores_emotion_id
        ON dbo.session_emotion_scores (emotion_id)
        INCLUDE (score);
GO
