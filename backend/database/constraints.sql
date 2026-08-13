/*
    EmotionLens — constraints (FKs, UNIQUE, CHECK).

    Execute após create_tables.sql e antes de seed.sql (a tabela dbo.emocoes
    precisa existir e ter suas constraints antes de ser populada).
*/

USE EmotionLensDB;
GO

-- --- dbo.emocoes -----------------------------------------------------------

IF NOT EXISTS (SELECT 1 FROM sys.key_constraints WHERE name = 'UQ_emocoes_codigo')
    ALTER TABLE dbo.emocoes ADD CONSTRAINT UQ_emocoes_codigo UNIQUE (codigo);
GO

-- --- dbo.sessoes -------------------------------------------------------------

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_sessoes_emocao_predominante')
    ALTER TABLE dbo.sessoes
        ADD CONSTRAINT FK_sessoes_emocao_predominante
        FOREIGN KEY (emocao_predominante_id) REFERENCES dbo.emocoes (id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_sessoes_frames_nao_negativo')
    ALTER TABLE dbo.sessoes ADD CONSTRAINT CK_sessoes_frames_nao_negativo CHECK (frames >= 0);
GO

IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_sessoes_confianca_intervalo')
    ALTER TABLE dbo.sessoes ADD CONSTRAINT CK_sessoes_confianca_intervalo CHECK (confianca BETWEEN 0 AND 100);
GO

IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_sessoes_analise_criptografada_e_json')
    ALTER TABLE dbo.sessoes ADD CONSTRAINT CK_sessoes_analise_criptografada_e_json CHECK (ISJSON(analise_criptografada) = 1);
GO

IF EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_sessoes_linha_do_tempo_e_json')
    ALTER TABLE dbo.sessoes DROP CONSTRAINT CK_sessoes_linha_do_tempo_e_json;
GO

-- LGPD: impede gravar caminho de arquivo (absoluto ou relativo) — apenas o
-- nome do arquivo enviado deve ser armazenado.
IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_sessoes_arquivo_origem_sem_caminho')
    ALTER TABLE dbo.sessoes
        ADD CONSTRAINT CK_sessoes_arquivo_origem_sem_caminho
        CHECK (arquivo_origem NOT LIKE '%[/\]%' AND arquivo_origem NOT LIKE '%:%');
GO

-- --- dbo.pontuacoes_emocao_sessao --------------------------------------------

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_pontuacoes_sessao')
    ALTER TABLE dbo.pontuacoes_emocao_sessao
        ADD CONSTRAINT FK_pontuacoes_sessao
        FOREIGN KEY (sessao_id) REFERENCES dbo.sessoes (id) ON DELETE CASCADE;
GO

IF NOT EXISTS (SELECT 1 FROM sys.foreign_keys WHERE name = 'FK_pontuacoes_emocao')
    ALTER TABLE dbo.pontuacoes_emocao_sessao
        ADD CONSTRAINT FK_pontuacoes_emocao
        FOREIGN KEY (emocao_id) REFERENCES dbo.emocoes (id);
GO

IF NOT EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_pontuacoes_intervalo')
    ALTER TABLE dbo.pontuacoes_emocao_sessao ADD CONSTRAINT CK_pontuacoes_intervalo CHECK (pontuacao BETWEEN 0 AND 100);
GO
