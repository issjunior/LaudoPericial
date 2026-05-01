# Modelos do banco — será preenchido no próximo passo
"""
database/models.py
──────────────────────────────────────────────────────
Define a estrutura de todas as tabelas do banco de dados.
Cada bloco SQL cria uma tabela se ela ainda não existir.
──────────────────────────────────────────────────────
"""

# ──────────────────────────────────────────────────────
# TABELA: usuarios
# Dados do perito. Apenas 1 usuário na versão atual.
# ──────────────────────────────────────────────────────
SQL_CRIAR_USUARIOS = """
CREATE TABLE IF NOT EXISTS usuarios (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nome                TEXT    NOT NULL,
    cargo               TEXT    NOT NULL DEFAULT 'Perito Oficial Criminal',
    matricula           TEXT,
    username            TEXT    NOT NULL UNIQUE,
    lotacao             TEXT    NOT NULL,
    email               TEXT    NOT NULL UNIQUE,
    senha_hash          TEXT    NOT NULL,
    pasta_exportacao    TEXT,
    alerta_prazo        INTEGER NOT NULL DEFAULT 1,
    dias_alerta         INTEGER NOT NULL DEFAULT 3,
    criado_em           TEXT    NOT NULL
                            DEFAULT (datetime('now','localtime')),
    atualizado_em       TEXT    NOT NULL
                            DEFAULT (datetime('now','localtime'))
);
"""
# username → prefixo do e-mail (antes do @)
# Ex: nome.sobrenome@policiacientifica.pr.gov.br → nome.sobrenome

# ──────────────────────────────────────────────────────
# TABELA: tipos_exame
# Ex: "Homicídio", "Acidente de Trânsito", "Incêndio"
# Cadastro livre pelo usuário (CRUD completo)
# ──────────────────────────────────────────────────────
SQL_CRIAR_TIPOS_EXAME = """
    CREATE TABLE IF NOT EXISTS tipos_exame (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo         TEXT    NOT NULL UNIQUE,
        nome           TEXT    NOT NULL,
        descricao      TEXT    DEFAULT '',
        exame_de_local INTEGER DEFAULT 0,
        ativo          INTEGER DEFAULT 1
    )
"""

# exame_de_local = 1 → habilita campos de horário e
#                      coordenadas na REP
# exame_de_local = 0 → exame por ofício, sem deslocamento

# ──────────────────────────────────────────────────────
# TABELA: solicitantes
# Delegacias, Varas, Promotorias que pedem perícias
# ──────────────────────────────────────────────────────
SQL_CRIAR_SOLICITANTES = """
CREATE TABLE IF NOT EXISTS solicitantes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nome            TEXT    NOT NULL,
    orgao           TEXT,  -- Adicionado novamente
    contato         TEXT,  -- Adicionado novamente
    ativo           INTEGER NOT NULL DEFAULT 1,
    criado_em       TEXT    NOT NULL
                        DEFAULT (datetime('now','localtime')),
    atualizado_em   TEXT    NOT NULL
                        DEFAULT (datetime('now','localtime'))
);
"""

# ──────────────────────────────────────────────────────
# TABELA: templates
# Modelos de laudo vinculados a um tipo de exame
# Ex: Tipo "Acidente" → "Colisão", "Atropelamento"
# ──────────────────────────────────────────────────────
SQL_CRIAR_TEMPLATES = """
CREATE TABLE IF NOT EXISTS templates (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_exame_id       INTEGER
                            REFERENCES tipos_exame(id),
    nome                TEXT    NOT NULL,
    descricao_exame     TEXT,
    ativo               INTEGER NOT NULL DEFAULT 1,
    criado_em           TEXT    NOT NULL
                            DEFAULT (datetime('now','localtime')),
    atualizado_em       TEXT    NOT NULL
                            DEFAULT (datetime('now','localtime'))
);
"""

# ──────────────────────────────────────────────────────
# TABELA: secoes_template
# Seções configuráveis de cada template
# Ex: Preâmbulo, Histórico, Objetivo Pericial...
# ──────────────────────────────────────────────────────
SQL_CRIAR_SECOES_TEMPLATE = """
CREATE TABLE IF NOT EXISTS secoes_template (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id     INTEGER NOT NULL
                        REFERENCES templates(id)
                        ON DELETE CASCADE,
    titulo          TEXT    NOT NULL,
    conteudo_base   TEXT    DEFAULT '',
    ordem           INTEGER NOT NULL DEFAULT 0,
    obrigatoria     INTEGER NOT NULL DEFAULT 0,
    criado_em       TEXT    NOT NULL
                        DEFAULT (datetime('now','localtime')),
    atualizado_em  TEXT    NOT NULL
                        DEFAULT (datetime('now','localtime'))
);
"""
# ON DELETE CASCADE → se o template for excluído,
# suas seções são excluídas automaticamente

# ──────────────────────────────────────────────────────
# TABELA: rep
# Requisição de Exame Pericial — registro central
# ──────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────
# TABELA: rep
# Requisição de Exame Pericial — registro central
# ──────────────────────────────────────────────────────
SQL_CRIAR_REP = """
CREATE TABLE IF NOT EXISTS rep (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_rep          TEXT    NOT NULL UNIQUE,
    data_solicitacao    TEXT    NOT NULL,
    horario_acionamento TEXT,
    horario_chegada     TEXT,
    horario_saida       TEXT,
    tipo_solicitacao    TEXT    NOT NULL
                            CHECK(tipo_solicitacao IN ('BO','Ofício', 'BO PM', 'BO PC', 'CECOMP', 'Outro')), -- ATUALIZADO: Adicionado 'BO PM', 'BO PC', 'CECOMP', 'Outro'
    numero_documento    TEXT    NOT NULL,
    numero_bo           TEXT,           -- NOVO: Número do Boletim de Ocorrência
    numero_ip           TEXT,           -- NOVO: Número do Inquérito Policial
    data_documento      TEXT,
    solicitante_id      INTEGER REFERENCES solicitantes(id),
    nome_autoridade     TEXT,
    tipo_exame_id       INTEGER REFERENCES tipos_exame(id),
    nome_envolvido      TEXT,           -- NOVO CAMPO ADICIONADO
    local_fato_descricao TEXT,     -- NOVO CAMPO ADICIONADO
    lacre_entrada       TEXT,           -- NOVO: Lacre de Entrada
    lacre_saida         TEXT,           -- NOVO: Lacre de Saída
    latitude            TEXT,
    longitude           TEXT,
    status              TEXT    NOT NULL DEFAULT 'Pendente'
                            CHECK(status IN (
                                'Pendente',
                                'Em Andamento',
                                'Concluido'
                            )),
    observacoes         TEXT,
    usuario_id          INTEGER NOT NULL REFERENCES usuarios(id),
    criado_em           TEXT    NOT NULL
                            DEFAULT (datetime('now','localtime')),
    atualizado_em       TEXT    NOT NULL
                            DEFAULT (datetime('now','localtime'))
);
"""

# ──────────────────────────────────────────────────────
# TABELA: laudos
# Um laudo por REP. Controla status e versão.
# ──────────────────────────────────────────────────────
SQL_CRIAR_LAUDOS = """
CREATE TABLE IF NOT EXISTS laudos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    rep_id          INTEGER NOT NULL UNIQUE
                        REFERENCES rep(id),
    template_id     INTEGER REFERENCES templates(id),
    status          TEXT    NOT NULL DEFAULT 'Pendente'
                        CHECK(status IN (
                            'Pendente',
                            'Em Andamento',
                            'Concluido',
                            'Entregue'
                        )),
    versao_atual    INTEGER NOT NULL DEFAULT 1,
    criado_em       TEXT    NOT NULL
                        DEFAULT (datetime('now','localtime')),
    atualizado_em   TEXT    NOT NULL
                        DEFAULT (datetime('now','localtime'))
);
"""

# ──────────────────────────────────────────────────────
# TABELA: secoes_laudo
# Cópia editável das seções do template para cada laudo.
# Alterações aqui NÃO afetam o template original.
# ──────────────────────────────────────────────────────
SQL_CRIAR_SECOES_LAUDO = """
CREATE TABLE IF NOT EXISTS secoes_laudo (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    laudo_id            INTEGER NOT NULL
                            REFERENCES laudos(id)
                            ON DELETE CASCADE,
    secao_template_id   INTEGER
                            REFERENCES secoes_template(id),
titulo              TEXT    NOT NULL,
    conteudo            TEXT    DEFAULT '',
    ordem               INTEGER NOT NULL DEFAULT 0,
    obrigatoria         INTEGER NOT NULL DEFAULT 0,
    criado_em           TEXT    NOT NULL
                        DEFAULT (datetime('now','localtime')),
    atualizado_em      TEXT    NOT NULL
                        DEFAULT (datetime('now','localtime'))
);
"""

# ──────────────────────────────────────────────────────
# TABELA: ilustracoes
# Fotos vinculadas às seções do laudo.
# Armazenadas como BLOB (binário) dentro do banco.
# ──────────────────────────────────────────────────────
SQL_CRIAR_ILUSTRACOES = """
CREATE TABLE IF NOT EXISTS ilustracoes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    secao_laudo_id  INTEGER NOT NULL
                        REFERENCES secoes_laudo(id)
                        ON DELETE CASCADE,
    laudo_id        INTEGER NOT NULL
                        REFERENCES laudos(id)
                        ON DELETE CASCADE,
    numero_figura   INTEGER NOT NULL,
    legenda         TEXT    NOT NULL DEFAULT '',
    dados_imagem    BLOB    NOT NULL,
    nome_arquivo    TEXT,
    ordem           INTEGER NOT NULL DEFAULT 0,
    criado_em       TEXT    NOT NULL
                        DEFAULT (datetime('now','localtime'))
);
"""

# ──────────────────────────────────────────────────────
# TABELA: versoes_laudo
# Guarda snapshots do laudo a cada salvamento.
# Mantém apenas as 3 últimas versões por laudo.
# ──────────────────────────────────────────────────────
SQL_CRIAR_VERSOES_LAUDO = """
CREATE TABLE IF NOT EXISTS versoes_laudo (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    laudo_id    INTEGER NOT NULL
                    REFERENCES laudos(id)
                    ON DELETE CASCADE,
    versao      INTEGER NOT NULL,
    snapshot    TEXT    NOT NULL,
    criado_em   TEXT    NOT NULL
                    DEFAULT (datetime('now','localtime'))
);
"""

SQL_CRIAR_MODELO_CABECALHO = """
CREATE TABLE IF NOT EXISTS modelo_cabecalho (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    modelo      TEXT    NOT NULL,
    conteudo    TEXT    NOT NULL DEFAULT '',
    ativo       INTEGER NOT NULL DEFAULT 1,
    criado_em   TEXT    NOT NULL
                    DEFAULT (datetime('now','localtime')),
    atualizado_em TEXT  NOT NULL
                    DEFAULT (datetime('now','localtime'))
);
"""

# ──────────────────────────────────────────────────────
# TABELA: historico
# Log completo de todas as operações no sistema.
# Registro de auditoria: quem fez o quê e quando.
# ──────────────────────────────────────────────────────
SQL_CRIAR_HISTORICO = """
CREATE TABLE IF NOT EXISTS historico (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id          INTEGER REFERENCES usuarios(id),
    tabela              TEXT    NOT NULL,
    registro_id         INTEGER NOT NULL,
    operacao            TEXT    NOT NULL
                            CHECK(operacao IN (
                                'CRIAR',
                                'EDITAR',
                                'EXCLUIR',
                                'FINALIZAR',
                                'LOGIN',
                                'LOGOUT'
                            )),
    descricao           TEXT,
    dados_anteriores    TEXT,
    criado_em           TEXT    NOT NULL
                            DEFAULT (datetime('now','localtime'))
);
"""

# ──────────────────────────────────────────────────────
# LISTA ORDENADA DE CRIAÇÃO
# A ordem importa por causa dos relacionamentos!
# Tabelas referenciadas devem existir antes das que
# as referenciam (ex: usuarios deve existir antes de rep)
# ──────────────────────────────────────────────────────
CREATE_ALL_TABLES = [
    SQL_CRIAR_USUARIOS,         # 1º — sem dependências
    SQL_CRIAR_TIPOS_EXAME,      # 2º — sem dependências
    SQL_CRIAR_SOLICITANTES,     # 3º — sem dependências
    SQL_CRIAR_MODELO_CABECALHO, # 4º — sem dependências
    SQL_CRIAR_TEMPLATES,        # 5º — depende de tipos_exame
    SQL_CRIAR_SECOES_TEMPLATE,  # 6º — depende de templates
    SQL_CRIAR_REP,              # 7º — depende de usuarios,
                                #        tipos_exame, solicitantes
    SQL_CRIAR_LAUDOS,           # 8º — depende de rep, templates
    SQL_CRIAR_SECOES_LAUDO,     # 9º — depende de laudos,
                                #        secoes_template
    SQL_CRIAR_ILUSTRACOES,      # 10º — depende de secoes_laudo,
                                #        laudos
    SQL_CRIAR_VERSOES_LAUDO,    # 11º — depende de laudos
    SQL_CRIAR_HISTORICO,        # 12º — depende de usuarios
]