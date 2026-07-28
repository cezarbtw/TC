/*
    EmotionLens — criação do banco de dados.

    Execute como o primeiro script, com um login que tenha permissão
    CREATE DATABASE (ex.: sysadmin em ambiente de desenvolvimento local).

    Este script NÃO cria logins/usuários nem grava credenciais — isso deve
    ser feito manualmente pelo DBA, fora do controle de versão, para evitar
    segredos versionados no repositório.
*/

USE master;
GO

IF DB_ID(N'EmotionLensDB') IS NULL
BEGIN
    CREATE DATABASE EmotionLensDB
        COLLATE Latin1_General_CI_AI; -- comparação/ordenação acento-insensível (PT-BR)
END
GO

-- Ambiente de desenvolvimento/TCC: recovery simples (sem exigência de backup de log).
ALTER DATABASE EmotionLensDB SET RECOVERY SIMPLE;
GO
