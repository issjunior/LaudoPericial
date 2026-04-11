# Conexão com banco — será preenchido no próximo passo
"""
database/db.py
──────────────────────────────────────────────────────
Responsável pela conexão com o banco de dados SQLite.
Toda comunicação com o banco passa por aqui.
──────────────────────────────────────────────────────
"""

import sqlite3
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# ──────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ──────────────────────────────────────────────────────

# Pasta raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Nome do banco (vem do .env)
DATABASE_NAME = os.getenv("DATABASE_NAME", "laudopericial.db")

# Caminho completo do arquivo do banco
DATABASE_PATH = BASE_DIR / DATABASE_NAME


# ──────────────────────────────────────────────────────
# FUNÇÕES PRINCIPAIS
# ──────────────────────────────────────────────────────

def get_db_connection() -> sqlite3.Connection:
    """
    Abre e retorna uma conexão com o banco de dados.

    O row_factory permite acessar os resultados tanto
    por índice (row[0]) quanto por nome (row["nome"]).

    Returns:
        Conexão ativa com o banco de dados SQLite
    """
    conn = sqlite3.connect(str(DATABASE_PATH))

    # Permite acessar colunas pelo nome (ex: row["nome"])
    conn.row_factory = sqlite3.Row

    # Ativa suporte a relacionamentos entre tabelas
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def init_database() -> None:
    """
    Inicializa o banco de dados criando todas as tabelas
    caso ainda não existam.

    Deve ser chamado uma vez na inicialização do sistema.
    É seguro chamar várias vezes — não apaga dados existentes.
    """
    # Importa aqui para evitar importação circular
    from database.models import CREATE_ALL_TABLES

    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        # Executa cada comando SQL de criação de tabela
        for sql in CREATE_ALL_TABLES:
            cursor.execute(sql)

        conn.commit()
        print("✅ Banco de dados inicializado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        conn.rollback()
        raise

    finally:
        # Sempre fecha a conexão ao terminar
        conn.close()


def database_exists() -> bool:
    """
    Verifica se o arquivo do banco de dados já existe.

    Usado na tela inicial para saber se é o primeiro
    acesso (precisa criar usuário) ou acesso normal (login).

    Returns:
        True se o banco já existe
        False se é a primeira vez rodando o sistema
    """
    return DATABASE_PATH.exists()


def executar_query(sql: str, params: tuple = ()) -> list:
    """
    Executa uma consulta SELECT e retorna os resultados.

    Args:
        sql:    Comando SQL de consulta
        params: Parâmetros para substituir os '?' no SQL

    Returns:
        Lista de linhas encontradas (pode ser vazia)

    Exemplo:
        rows = executar_query(
            'SELECT * FROM rep WHERE status = ?',
            ('Pendente',)
        )
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        conn.close()


def executar_comando(sql: str, params: tuple = ()) -> int:
    """
    Executa um comando INSERT, UPDATE ou DELETE.

    Args:
        sql:    Comando SQL de modificação
        params: Parâmetros para substituir os '?' no SQL

    Returns:
        ID do registro criado (para INSERT)
        ou número de linhas afetadas (para UPDATE/DELETE)

    Exemplo:
        novo_id = executar_comando(
            'INSERT INTO tipos_exame (nome) VALUES (?)',
            ('Homicídio',)
        )
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()

        # Retorna o ID do último registro inserido
        return cursor.lastrowid

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()


def executar_transacao(operacoes: list) -> None:
    """
    Executa múltiplos comandos SQL em uma única transação.
    Se qualquer comando falhar, TODOS são desfeitos.

    Usado quando precisamos garantir que várias operações
    aconteçam juntas ou não aconteçam de forma alguma.

    Args:
        operacoes: Lista de tuplas (sql, params)

    Exemplo:
        executar_transacao([
            ('INSERT INTO laudos ...', (rep_id,)),
            ('INSERT INTO secoes_laudo ...', (laudo_id,)),
        ])
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        for sql, params in operacoes:
            cursor.execute(sql, params)

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()