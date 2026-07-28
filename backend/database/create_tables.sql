/*
    EmotionLens — criação das tabelas.

    Execute após create_database.sql. Constraints (FKs/CHECKs) e índices ficam
    em scripts separados (constraints.sql, indexes.sql), propositalmente, para
    facilitar reexecução/alteração isolada de cada camada do schema.
*/

USE EmotionLensDB;
GO

-- Tabela de referência: as 7 emoções suportadas pelo pipeline (HSEmotion).
-- Populada por seed.sql — é pré-requisito, não dado de exemplo opcional.
IF OBJECT_ID(N'dbo.emotions', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.emotions
    (
        id          TINYINT         NOT NULL,
        code        VARCHAR(20)     NOT NULL,   -- rótulo em PT usado na API ('feliz', 'triste', ...)
        label_en    VARCHAR(20)     NOT NULL,   -- rótulo canônico em EN ('happy', 'sad', ...)
        sort_order  TINYINT         NOT NULL,   -- ordem esperada pelo frontend (PT_EMOTIONS)
        CONSTRAINT PK_emotions PRIMARY KEY (id)
    );
END
GO

-- Uma linha por sessão de análise emocional (agregado retornado pela API).
IF OBJECT_ID(N'dbo.sessions', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.sessions
    (
        id                      INT             IDENTITY(1,1) NOT NULL,
        name                    NVARCHAR(50)    NOT NULL,   -- ex.: "Sessão 01"
        source_file             NVARCHAR(255)   NOT NULL,   -- apenas o NOME do arquivo enviado (nunca path/binário)
        session_date            DATE            NOT NULL,
        duration                VARCHAR(8)      NOT NULL,   -- formato "MM:SS", fiel ao contrato atual da API
        frames                  INT             NOT NULL,
        predominant_emotion_id  TINYINT         NOT NULL,
        confidence              DECIMAL(5,2)    NOT NULL,
        timeline_json           NVARCHAR(MAX)   NOT NULL,   -- série por frame/emoção (dict[str, list[float]] serializado)
        created_at              DATETIME2(3)    NOT NULL CONSTRAINT DF_sessions_created_at DEFAULT SYSUTCDATETIME(),
        updated_at              DATETIME2(3)    NOT NULL CONSTRAINT DF_sessions_updated_at DEFAULT SYSUTCDATETIME(),
        deleted_at              DATETIME2(3)    NULL,       -- soft delete (nunca DELETE físico)
        CONSTRAINT PK_sessions PRIMARY KEY (id)
    );
END
GO

-- Distribuição de probabilidade por emoção de cada sessão (7 linhas por sessão).
IF OBJECT_ID(N'dbo.session_emotion_scores', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.session_emotion_scores
    (
        session_id  INT             NOT NULL,
        emotion_id  TINYINT         NOT NULL,
        score       DECIMAL(5,2)    NOT NULL,
        CONSTRAINT PK_session_emotion_scores PRIMARY KEY (session_id, emotion_id)
    );
END
GO
