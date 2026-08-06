/*
    EmotionLens — índices de suporte às consultas do repositório.

    Execute após constraints.sql.
*/

USE EmotionLensDB;
GO

-- Suporta listar_todas(): sessões ativas (não deletadas), mais recentes primeiro.
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_sessoes_ativas_id')
    CREATE INDEX IX_sessoes_ativas_id
        ON dbo.sessoes (id DESC)
        WHERE excluido_em IS NULL;
GO

-- Suporta futuras consultas/relatórios por período.
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_sessoes_data_sessao')
    CREATE INDEX IX_sessoes_data_sessao ON dbo.sessoes (data_sessao);
GO

-- Suporta agregações por emoção (ex.: score médio de 'raiva' entre sessões).
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_pontuacoes_emocao_id')
    CREATE INDEX IX_pontuacoes_emocao_id
        ON dbo.pontuacoes_emocao_sessao (emocao_id)
        INCLUDE (pontuacao);
GO
