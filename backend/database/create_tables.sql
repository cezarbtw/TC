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
IF OBJECT_ID(N'dbo.emocoes', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.emocoes
    (
        id          TINYINT         NOT NULL,
        codigo      VARCHAR(20)     NOT NULL,   -- rótulo em PT usado na API ('feliz', 'triste', ...)
        rotulo_en   VARCHAR(20)     NOT NULL,   -- rótulo canônico em EN ('happy', 'sad', ...)
        ordem       TINYINT         NOT NULL,   -- ordem esperada pelo frontend (EMOCOES_PT)
        CONSTRAINT PK_emocoes PRIMARY KEY (id)
    );
END
GO

-- Uma linha por sessão de análise emocional (agregado retornado pela API).
IF OBJECT_ID(N'dbo.sessoes', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.sessoes
    (
        id                      INT             IDENTITY(1,1) NOT NULL,
        nome                    NVARCHAR(50)    NOT NULL,   -- ex.: "Sessão 01"
        arquivo_origem          NVARCHAR(255)   NOT NULL,   -- apenas o NOME do arquivo enviado (nunca path/binário)
        data_sessao             DATE            NOT NULL,
        duracao                 VARCHAR(8)      NOT NULL,   -- formato "MM:SS", fiel ao contrato atual da API
        frames                  INT             NOT NULL,
        emocao_predominante_id  TINYINT         NOT NULL,
        confianca               DECIMAL(5,2)    NOT NULL,
        analise_criptografada   NVARCHAR(MAX)   NOT NULL,   -- envelope JSON com MCE + AES-256-GCM
        criado_em               DATETIME2(3)    NOT NULL CONSTRAINT DF_sessoes_criado_em DEFAULT SYSUTCDATETIME(),
        atualizado_em           DATETIME2(3)    NOT NULL CONSTRAINT DF_sessoes_atualizado_em DEFAULT SYSUTCDATETIME(),
        excluido_em             DATETIME2(3)    NULL,       -- soft delete (nunca DELETE físico)
        CONSTRAINT PK_sessoes PRIMARY KEY (id)
    );
END
GO

IF OBJECT_ID(N'dbo.sessoes', N'U') IS NOT NULL
   AND COL_LENGTH('dbo.sessoes', 'analise_criptografada') IS NULL
BEGIN
    ALTER TABLE dbo.sessoes ADD analise_criptografada NVARCHAR(MAX) NULL;
END
GO

IF EXISTS (SELECT 1 FROM sys.check_constraints WHERE name = 'CK_sessoes_linha_do_tempo_e_json')
    ALTER TABLE dbo.sessoes DROP CONSTRAINT CK_sessoes_linha_do_tempo_e_json;
GO

IF OBJECT_ID(N'dbo.sessoes', N'U') IS NOT NULL
   AND COL_LENGTH('dbo.sessoes', 'linha_do_tempo_json') IS NOT NULL
BEGIN
    ALTER TABLE dbo.sessoes ALTER COLUMN linha_do_tempo_json NVARCHAR(MAX) NULL;
END
GO

IF OBJECT_ID(N'dbo.sessoes', N'U') IS NOT NULL
   AND COL_LENGTH('dbo.sessoes', 'linha_do_tempo_json') IS NOT NULL
   AND COL_LENGTH('dbo.sessoes', 'analise_criptografada') IS NOT NULL
BEGIN
    UPDATE dbo.sessoes
    SET analise_criptografada = linha_do_tempo_json
    WHERE analise_criptografada IS NULL
      AND ISJSON(linha_do_tempo_json) = 1
      AND JSON_VALUE(linha_do_tempo_json, '$.alg') = 'AES-256-GCM';
END
GO

IF OBJECT_ID(N'dbo.sessoes', N'U') IS NOT NULL
   AND COL_LENGTH('dbo.sessoes', 'linha_do_tempo_json') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1
       FROM dbo.sessoes
       WHERE analise_criptografada IS NULL
   )
BEGIN
    ALTER TABLE dbo.sessoes DROP COLUMN linha_do_tempo_json;
END
GO

-- Distribuição aberta por emoção mantida apenas para bases antigas/relatórios.
-- A aplicação atual grava os dados completos em dbo.sessoes.analise_criptografada.
IF OBJECT_ID(N'dbo.pontuacoes_emocao_sessao', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.pontuacoes_emocao_sessao
    (
        sessao_id   INT             NOT NULL,
        emocao_id   TINYINT         NOT NULL,
        pontuacao   DECIMAL(5,2)    NOT NULL,
        CONSTRAINT PK_pontuacoes_emocao_sessao PRIMARY KEY (sessao_id, emocao_id)
    );
END
GO
