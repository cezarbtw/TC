# Persistência em SQL Server — EmotionLens

Este documento descreve a camada de persistência opcional em Microsoft SQL
Server do backend EmotionLens, que complementa (sem substituir) o
`InMemorySessionRepository` usado por padrão em desenvolvimento.

## Visão geral

O domínio define uma porta única, `SessionRepository`
(`app/domain/services/ports.py`), com três operações: `create`, `list_all` e
`get`. Existem duas implementações intercambiáveis:

- `InMemorySessionRepository` (`app/infrastructure/repositories/in_memory_session_repository.py`) — estado em processo, perdido a cada reinício. Padrão.
- `SqlServerSessionRepository` (`app/infrastructure/repositories/sql_server_session_repository.py`) — persiste em SQL Server via `pyodbc` puro (sem ORM/SQLAlchemy), com SQL parametrizado.

A escolha é feita **exclusivamente por configuração** (`EMOTIONLENS_SESSION_REPOSITORY_BACKEND`), em `app/api/deps/dependencies.py::get_session_repository()`. Nenhum caso de uso, rota ou contrato de resposta da API muda entre os dois modos.

**Escopo de dados persistidos**: apenas o resultado da análise emocional (nome da sessão, nome do arquivo de origem, data, duração, distribuição de emoções e timeline agregada). O vídeo/imagem enviado nunca é persistido — é gravado em arquivo temporário só para leitura pelo OpenCV e removido logo em seguida (`app/api/routes/sessions.py`).

## Pré-requisitos

- Microsoft SQL Server 2019 ou superior (testado com uma instância local `MSSQLSERVER`).
- ODBC Driver 17 ou 18 for SQL Server instalado no sistema operacional (não é um pacote Python — é o driver nativo do SO).
- Dependência Python `pyodbc` (já listada em `backend/requirements.txt`).

## Modelo de dados

```
dbo.emotions
  id             TINYINT       PK
  code           VARCHAR(20)   UNIQUE  -- rótulo em PT: 'feliz','triste','raiva','surpresa','medo','nojo','neutro'
  label_en       VARCHAR(20)           -- rótulo canônico em EN
  sort_order     TINYINT               -- ordem esperada pelo frontend

dbo.sessions
  id                     INT IDENTITY  PK
  name                   NVARCHAR(50)          -- "Sessão 01", atribuído após o INSERT
  source_file            NVARCHAR(255)         -- só o NOME do arquivo enviado
  session_date           DATE
  duration               VARCHAR(8)            -- "MM:SS"
  frames                 INT
  predominant_emotion_id TINYINT       FK -> emotions(id)
  confidence             DECIMAL(5,2)
  timeline_json          NVARCHAR(MAX)         -- JSON: dict[emoção, lista de scores por frame]
  created_at             DATETIME2(3)          -- auditoria
  updated_at             DATETIME2(3)          -- auditoria
  deleted_at             DATETIME2(3)  NULL    -- soft delete (estrutura preparada; sem UI/endpoint ainda)

dbo.session_emotion_scores
  session_id   INT       FK -> sessions(id) ON DELETE CASCADE
  emotion_id   TINYINT   FK -> emotions(id)
  score        DECIMAL(5,2)
  PK (session_id, emotion_id)
```

**Relacionamentos**: uma sessão tem exatamente uma emoção predominante (`sessions.predominant_emotion_id → emotions.id`) e 7 scores, um por emoção (`session_emotion_scores`, 1 sessão : N scores, N emoção : N scores).

### Por que `probabilities` é normalizado e `timeline` fica em JSON?

- **`probabilities`** tem cardinalidade fixa e pequena (7 pares emoção→score por sessão). Normalizar em `session_emotion_scores` custa apenas 7 `INSERT`s por sessão (via `executemany`), permite consultas SQL diretas (ex.: score médio de "raiva" entre todas as sessões) e é reconstruído com uma única query, mesmo para várias sessões de uma vez (`list_all` não faz N+1 queries).
- **`timeline`** guarda uma série por frame (até ~600 amostras × 7 emoções por sessão). Normalizar geraria milhares de linhas por upload e mais uma classe de bug (ordenação, gaps). SQL Server não tem tipo `JSON` nativo, mas `NVARCHAR(MAX)` com `CHECK (ISJSON(...) = 1)` garante validade estrutural, e o round-trip via `json.dumps`/`json.loads` no Python é 100% fiel ao formato já consumido pelo frontend. Se no futuro forem necessárias queries SQL ponto-a-ponto na timeline, o SQL Server suporta `JSON_VALUE`/`OPENJSON` sobre essa mesma coluna sem migração de schema.

## Executando os scripts

Os scripts estão em `backend/database/` e devem ser executados **nesta ordem**, contra uma instância SQL Server acessível:

1. `create_database.sql` — cria o banco `EmotionLensDB`.
2. `create_tables.sql` — cria as 3 tabelas.
3. `constraints.sql` — adiciona FKs, `UNIQUE` e `CHECK`s.
4. `indexes.sql` — cria os índices de suporte às consultas.
5. `seed.sql` — popula `dbo.emotions` (**obrigatório**: as FKs dependem dessas 7 linhas).

Todos os scripts são idempotentes (usam `IF NOT EXISTS`/`MERGE`), podendo ser reexecutados com segurança.

### Via SSMS

Abra cada arquivo em SQL Server Management Studio, conectado à instância desejada, e execute com `F5` na ordem acima.

### Via sqlcmd

```bash
sqlcmd -S localhost -E -i backend/database/create_database.sql
sqlcmd -S localhost -E -i backend/database/create_tables.sql
sqlcmd -S localhost -E -i backend/database/constraints.sql
sqlcmd -S localhost -E -i backend/database/indexes.sql
sqlcmd -S localhost -E -i backend/database/seed.sql
```

(`-E` usa Windows Authentication; troque por `-U usuario -P senha` para SQL Authentication.)

## Configuração do `.env`

Copie `backend/.env.example` para `backend/.env` e ajuste o bloco de persistência:

| Variável | Papel | Padrão |
|---|---|---|
| `EMOTIONLENS_SESSION_REPOSITORY_BACKEND` | `memory` ou `sqlserver` | `memory` |
| `EMOTIONLENS_DB_SERVER` | equivalente a `DB_SERVER` | `localhost` |
| `EMOTIONLENS_DB_DATABASE` | equivalente a `DB_DATABASE` | `EmotionLensDB` |
| `EMOTIONLENS_DB_TRUSTED_CONNECTION` | usa Windows Authentication quando `true` | `true` |
| `EMOTIONLENS_DB_USERNAME` | equivalente a `DB_USERNAME` (só se `TRUSTED_CONNECTION=false`) | vazio |
| `EMOTIONLENS_DB_PASSWORD` | equivalente a `DB_PASSWORD` (só se `TRUSTED_CONNECTION=false`) | vazio |
| `EMOTIONLENS_DB_DRIVER` | equivalente a `DB_DRIVER` | `ODBC Driver 17 for SQL Server` |
| `EMOTIONLENS_DB_CONNECT_TIMEOUT` | timeout de conexão (segundos) | `5` |

O prefixo `EMOTIONLENS_` é mantido em todas as variáveis por consistência com o restante do `Settings` (`app/core/config.py`, pydantic-settings) — os nomes à direita da tabela são os nomes conceituais equivalentes.

**Nunca versione o `.env` real** (já está no `.gitignore`); ele pode conter credenciais se `TRUSTED_CONNECTION=false` for usado.

## LGPD e dados sensíveis

- **Sem caminhos absolutos**: `source_file` guarda apenas o nome do arquivo enviado, nunca um caminho de disco — reforçado por `CK_sessions_source_file_no_path`.
- **Auditoria**: `created_at`/`updated_at` (`DATETIME2(3)`, preenchidos automaticamente) em `dbo.sessions`.
- **Soft delete**: `deleted_at` (`DATETIME2(3) NULL`) está presente no schema e já é respeitado pelas consultas de leitura (`WHERE deleted_at IS NULL`); registros **nunca** são removidos fisicamente. Não há endpoint/método de exclusão hoje — a coluna prepara a estrutura para quando essa funcionalidade for adicionada, sem exigir migração de schema.
- **Criptografia (recomendação futura, não implementada)**: para dados de sessão mais sensíveis, considere `Always Encrypted` (nativo do SQL Server, transparente à aplicação) sobre as colunas `timeline_json`/`source_file`, ou, como alternativa mais simples de operacionalizar num TCC, cifrar `timeline_json` em nível de aplicação (ex.: Fernet) antes do `INSERT`, guardando a chave fora do banco (variável de ambiente/cofre de segredos) — nesse caso a `CHECK CK_sessions_timeline_is_json` precisaria ser removida, já que o conteúdo cifrado deixa de ser JSON válido.

## Troubleshooting

- **`Data source name not found` / driver ausente**: confirme que o ODBC Driver 17 ou 18 for SQL Server está instalado no SO (não é `pip install`) e que `EMOTIONLENS_DB_DRIVER` bate com o nome exato do driver instalado.
- **Falha de login com Windows Authentication**: confirme que o processo do backend roda com o mesmo usuário do Windows que tem acesso à instância, e que `EMOTIONLENS_DB_TRUSTED_CONNECTION=true`.
- **Erro de certificado/TLS**: em ambientes de desenvolvimento com certificado autoassinado, pode ser necessário `TrustServerCertificate=yes` (já incluso implicitamente pelo driver em conexões locais na maioria das instalações padrão; se persistir, verifique a configuração de `Force Encryption` da instância).
- **`503 Falha ao acessar a base de dados`**: resposta padrão da API quando o SQL Server está inacessível (`PersistenceError`, `app/core/errors.py`) — os detalhes reais do erro (SQLSTATE, mensagem do driver) ficam apenas no log do servidor, nunca na resposta ao cliente.

## Voltando para `memory`

Basta definir `EMOTIONLENS_SESSION_REPOSITORY_BACKEND=memory` (ou remover a variável) e reiniciar o processo — nenhuma outra alteração é necessária.
