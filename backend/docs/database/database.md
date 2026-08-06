# Persistência em SQL Server — EmotionLens

Este documento descreve a camada de persistência em Microsoft SQL Server do
backend EmotionLens — o único backend de persistência suportado (não há mais
um modo "em memória" em produção).

## Visão geral

A camada de serviços (`app/servicos/`) depende de `RepositorioSessao`
(`app/persistencia/repositorio_sessao.py`), com três operações: `criar`,
`listar_todas` e `obter`. Não há interface abstrata nem implementação
alternativa — é a única forma de persistência da aplicação, resolvida em
`app/rotas/dependencias.py::obter_repositorio_sessao()`.

**Escopo de dados persistidos**: apenas o resultado da análise emocional (nome
da sessão, nome do arquivo de origem, data, duração, distribuição de emoções e
timeline agregada). O vídeo/imagem enviado nunca é persistido — é gravado em
arquivo temporário só para leitura pelo OpenCV e removido logo em seguida
(`app/rotas/sessao.py`).

## Pré-requisitos

- Microsoft SQL Server 2019 ou superior (testado com uma instância local `MSSQLSERVER`).
- ODBC Driver 17 ou 18 for SQL Server instalado no sistema operacional (não é um pacote Python — é o driver nativo do SO).
- Dependência Python `pyodbc` (já listada em `backend/requirements.txt`).

## Modelo de dados

```
dbo.emocoes
  id             TINYINT       PK
  codigo         VARCHAR(20)   UNIQUE  -- rótulo em PT: 'feliz','triste','raiva','surpresa','medo','nojo','neutro'
  rotulo_en      VARCHAR(20)           -- rótulo canônico em EN
  ordem          TINYINT               -- ordem esperada pelo frontend

dbo.sessoes
  id                      INT IDENTITY  PK
  nome                    NVARCHAR(50)          -- "Sessão 01", atribuído após o INSERT
  arquivo_origem          NVARCHAR(255)         -- só o NOME do arquivo enviado
  data_sessao             DATE
  duracao                 VARCHAR(8)            -- "MM:SS"
  frames                  INT
  emocao_predominante_id  TINYINT       FK -> emocoes(id)
  confianca               DECIMAL(5,2)
  linha_do_tempo_json     NVARCHAR(MAX)         -- JSON: dict[emoção, lista de scores por frame]
  criado_em               DATETIME2(3)          -- auditoria
  atualizado_em           DATETIME2(3)          -- auditoria
  excluido_em             DATETIME2(3)  NULL    -- soft delete (estrutura preparada; sem UI/endpoint ainda)

dbo.pontuacoes_emocao_sessao
  sessao_id    INT       FK -> sessoes(id) ON DELETE CASCADE
  emocao_id    TINYINT   FK -> emocoes(id)
  pontuacao    DECIMAL(5,2)
  PK (sessao_id, emocao_id)
```

**Relacionamentos**: uma sessão tem exatamente uma emoção predominante (`sessoes.emocao_predominante_id → emocoes.id`) e 7 pontuações, uma por emoção (`pontuacoes_emocao_sessao`, 1 sessão : N pontuações, N emoção : N pontuações).

### Por que `probabilities` é normalizado e `timeline` fica em JSON?

- **`probabilities`** (as pontuações por emoção, expostas no contrato de API) tem cardinalidade fixa e pequena (7 pares emoção→score por sessão). Normalizar em `pontuacoes_emocao_sessao` custa apenas 7 `INSERT`s por sessão (via `executemany`), permite consultas SQL diretas (ex.: score médio de "raiva" entre todas as sessões) e é reconstruído com uma única query, mesmo para várias sessões de uma vez (`listar_todas` não faz N+1 queries).
- **`timeline`** guarda uma série por frame (até ~600 amostras × 7 emoções por sessão). Normalizar geraria milhares de linhas por upload e mais uma classe de bug (ordenação, gaps). SQL Server não tem tipo `JSON` nativo, mas `NVARCHAR(MAX)` com `CHECK (ISJSON(...) = 1)` garante validade estrutural, e o round-trip via `json.dumps`/`json.loads` no Python é 100% fiel ao formato já consumido pelo frontend. Se no futuro forem necessárias queries SQL ponto-a-ponto na timeline, o SQL Server suporta `JSON_VALUE`/`OPENJSON` sobre essa mesma coluna sem migração de schema.

## Executando os scripts

Os scripts estão em `backend/database/` e devem ser executados **nesta ordem**, contra uma instância SQL Server acessível:

1. `create_database.sql` — cria o banco `EmotionLensDB`.
2. `create_tables.sql` — cria as 3 tabelas.
3. `constraints.sql` — adiciona FKs, `UNIQUE` e `CHECK`s.
4. `indexes.sql` — cria os índices de suporte às consultas.
5. `seed.sql` — popula `dbo.emocoes` (**obrigatório**: as FKs dependem dessas 7 linhas).

Todos os scripts são idempotentes (usam `IF NOT EXISTS`/`MERGE`), podendo ser reexecutados com segurança — **exceto** quando o banco já existir com os nomes de tabela antigos (em inglês): nesse caso os scripts criam as tabelas novas em português ao lado das antigas, sem migrar dados. Se o banco já foi criado antes da padronização em português, derrube-o (`DROP DATABASE EmotionLensDB;`) e rode os scripts do zero.

Ou, de forma equivalente, execute tudo de uma vez com:

```bash
python database/run_setup.py
```

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
| `EMOTIONLENS_DB_SERVIDOR` | endereço do servidor SQL Server | `localhost` |
| `EMOTIONLENS_DB_BANCO` | nome do banco | `EmotionLensDB` |
| `EMOTIONLENS_DB_CONEXAO_CONFIAVEL` | usa Windows Authentication quando `true` | `true` |
| `EMOTIONLENS_DB_USUARIO` | usuário SQL (só se `CONEXAO_CONFIAVEL=false`) | vazio |
| `EMOTIONLENS_DB_SENHA` | senha SQL (só se `CONEXAO_CONFIAVEL=false`) | vazio |
| `EMOTIONLENS_DB_DRIVER` | nome exato do driver ODBC instalado | `ODBC Driver 17 for SQL Server` |
| `EMOTIONLENS_DB_TEMPO_LIMITE_CONEXAO` | timeout de conexão (segundos) | `5` |

O prefixo `EMOTIONLENS_` é mantido em todas as variáveis por consistência com o restante de `Configuracoes` (`app/nucleo/configuracoes.py`, pydantic-settings).

**Nunca versione o `.env` real** (já está no `.gitignore`); ele pode conter credenciais se `CONEXAO_CONFIAVEL=false` for usado.

## LGPD e dados sensíveis

- **Sem caminhos absolutos**: `arquivo_origem` guarda apenas o nome do arquivo enviado, nunca um caminho de disco — reforçado por `CK_sessoes_arquivo_origem_sem_caminho`.
- **Auditoria**: `criado_em`/`atualizado_em` (`DATETIME2(3)`, preenchidos automaticamente) em `dbo.sessoes`.
- **Soft delete**: `excluido_em` (`DATETIME2(3) NULL`) está presente no schema e já é respeitado pelas consultas de leitura (`WHERE excluido_em IS NULL`); registros **nunca** são removidos fisicamente. Não há endpoint/método de exclusão hoje — a coluna prepara a estrutura para quando essa funcionalidade for adicionada, sem exigir migração de schema.
- **Criptografia (recomendação futura, não implementada)**: para dados de sessão mais sensíveis, considere `Always Encrypted` (nativo do SQL Server, transparente à aplicação) sobre as colunas `linha_do_tempo_json`/`arquivo_origem`, ou, como alternativa mais simples de operacionalizar num TCC, cifrar `linha_do_tempo_json` em nível de aplicação (ex.: Fernet) antes do `INSERT`, guardando a chave fora do banco (variável de ambiente/cofre de segredos) — nesse caso a `CHECK CK_sessoes_linha_do_tempo_e_json` precisaria ser removida, já que o conteúdo cifrado deixa de ser JSON válido.

## Troubleshooting

- **`Data source name not found` / driver ausente**: confirme que o ODBC Driver 17 ou 18 for SQL Server está instalado no SO (não é `pip install`) e que `EMOTIONLENS_DB_DRIVER` bate com o nome exato do driver instalado.
- **Falha de login com Windows Authentication**: confirme que o processo do backend roda com o mesmo usuário do Windows que tem acesso à instância, e que `EMOTIONLENS_DB_CONEXAO_CONFIAVEL=true`.
- **Erro de certificado/TLS**: em ambientes de desenvolvimento com certificado autoassinado, pode ser necessário `TrustServerCertificate=yes` (já incluso implicitamente pelo driver em conexões locais na maioria das instalações padrão; se persistir, verifique a configuração de `Force Encryption` da instância).
- **`503 Falha ao acessar a base de dados`**: resposta padrão da API quando o SQL Server está inacessível (`ErroPersistencia`, `app/nucleo/erros.py`) — os detalhes reais do erro (SQLSTATE, mensagem do driver) ficam apenas no log do servidor, nunca na resposta ao cliente.
