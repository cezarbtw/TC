/*
    EmotionLens — constraints (FKs, UNIQUE, CHECK).

    Execute após create_tables.sql e antes de seed.sql (a tabela dbo.emotions
    precisa existir e ter suas constraints antes de ser populada).
*/

USE EmotionLensDB;
GO

-- --- dbo.emotions ---------------------------------------------------------

IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'UQ_emotions_code')
    ALTER TABLE dbo.emotions ADD CONSTRAINT UQ_emotions_code UNIQUE (code);
GO

-- --- dbo.sessions -----------------------------------------------------------

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_sessions_predominant_emotion')
    ALTER TABLE dbo.sessions
        ADD CONSTRAINT FK_sessions_predominant_emotion
        FOREIGN KEY (predominant_emotion_id) REFERENCES dbo.emotions (id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_sessions_frames_nonnegative')
    ALTER TABLE dbo.sessions ADD CONSTRAINT CK_sessions_frames_nonnegative CHECK (frames >= 0);
GO

IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_sessions_confidence_range')
    ALTER TABLE dbo.sessions ADD CONSTRAINT CK_sessions_confidence_range CHECK (confidence BETWEEN 0 AND 100);
GO

IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_sessions_timeline_is_json')
    ALTER TABLE dbo.sessions ADD CONSTRAINT CK_sessions_timeline_is_json CHECK (ISJSON(timeline_json) = 1);
GO

-- LGPD: impede gravar caminho de arquivo (absoluto ou relativo) — apenas o
-- nome do arquivo enviado deve ser armazenado.
IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_sessions_source_file_no_path')
    ALTER TABLE dbo.sessions
        ADD CONSTRAINT CK_sessions_source_file_no_path
        CHECK (source_file NOT LIKE '%[/\]%' AND source_file NOT LIKE '%:%');
GO

-- --- dbo.session_emotion_scores ---------------------------------------------

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_scores_session')
    ALTER TABLE dbo.session_emotion_scores
        ADD CONSTRAINT FK_scores_session
        FOREIGN KEY (session_id) REFERENCES dbo.sessions (id) ON DELETE CASCADE;
GO

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_scores_emotion')
    ALTER TABLE dbo.session_emotion_scores
        ADD CONSTRAINT FK_scores_emotion
        FOREIGN KEY (emotion_id) REFERENCES dbo.emotions (id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_scores_range')
    ALTER TABLE dbo.session_emotion_scores ADD CONSTRAINT CK_scores_range CHECK (score BETWEEN 0 AND 100);
GO
