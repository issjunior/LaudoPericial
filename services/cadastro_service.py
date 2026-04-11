"""
services/cadastro_service.py
──────────────────────────────────────────────────────
Serviço responsável pelos cadastros de apoio:
  - Tipos de Exame
  - Solicitantes

Toda lógica de negócio dos cadastros passa por aqui.
──────────────────────────────────────────────────────
"""

import sys
import os

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.db import executar_query, executar_comando


# ══════════════════════════════════════════════════════
# TIPOS DE EXAME
# ══════════════════════════════════════════════════════

def listar_tipos_exame(apenas_ativos: bool = True) -> list:
    """
    Retorna todos os tipos de exame cadastrados.

    Args:
        apenas_ativos: Se True, retorna só os ativos.
                       Se False, retorna todos.

    Returns:
        Lista de dicionários com os tipos de exame.
    """
    if apenas_ativos:
        sql = """
            SELECT id, nome, descricao, exame_de_local, ativo
            FROM tipos_exame
            WHERE ativo = 1
            ORDER BY nome
        """
    else:
        sql = """
            SELECT id, nome, descricao, exame_de_local, ativo
            FROM tipos_exame
            ORDER BY nome
        """

    rows = executar_query(sql)

    # Converte sqlite3.Row para dicionário
    return [dict(row) for row in rows]


def buscar_tipo_exame(tipo_id: int) -> dict | None:
    """
    Busca um tipo de exame pelo ID.

    Args:
        tipo_id: ID do tipo de exame

    Returns:
        Dicionário com os dados ou None se não encontrado
    """
    sql = """
        SELECT id, nome, descricao, exame_de_local, ativo
        FROM tipos_exame
        WHERE id = ?
    """
    rows = executar_query(sql, (tipo_id,))

    if rows:
        return dict(rows[0])
    return None


def criar_tipo_exame(
    nome:           str,
    descricao:      str  = "",
    exame_de_local: bool = False,
) -> int:
    """
    Cria um novo tipo de exame.

    Args:
        nome:           Nome do tipo de exame (obrigatório)
        descricao:      Descrição opcional
        exame_de_local: Se exige deslocamento ao local

    Returns:
        ID do novo tipo de exame criado

    Raises:
        ValueError: Se o nome estiver vazio ou já existir
    """
    nome = nome.strip()

    if not nome:
        raise ValueError("O nome do tipo de exame é obrigatório.")

    # Verifica duplicidade
    existe = executar_query(
        "SELECT id FROM tipos_exame WHERE LOWER(nome) = LOWER(?)",
        (nome,)
    )
    if existe:
        raise ValueError(f"Já existe um tipo de exame com o nome '{nome}'.")

    sql = """
        INSERT INTO tipos_exame (nome, descricao, exame_de_local, ativo)
        VALUES (?, ?, ?, 1)
    """
    return executar_comando(sql, (nome, descricao.strip(), int(exame_de_local)))


def atualizar_tipo_exame(
    tipo_id:        int,
    nome:           str,
    descricao:      str  = "",
    exame_de_local: bool = False,
) -> None:
    """
    Atualiza os dados de um tipo de exame existente.

    Args:
        tipo_id:        ID do tipo a atualizar
        nome:           Novo nome
        descricao:      Nova descrição
        exame_de_local: Novo valor do campo exame_de_local

    Raises:
        ValueError: Se o tipo não existir ou nome já usado
    """
    nome = nome.strip()

    if not nome:
        raise ValueError("O nome do tipo de exame é obrigatório.")

    # Verifica se o tipo existe
    tipo = buscar_tipo_exame(tipo_id)
    if not tipo:
        raise ValueError("Tipo de exame não encontrado.")

    # Verifica duplicidade (ignora o próprio registro)
    existe = executar_query(
        """
        SELECT id FROM tipos_exame
        WHERE LOWER(nome) = LOWER(?) AND id != ?
        """,
        (nome, tipo_id)
    )
    if existe:
        raise ValueError(f"Já existe um tipo de exame com o nome '{nome}'.")

    sql = """
        UPDATE tipos_exame
        SET nome = ?, descricao = ?, exame_de_local = ?
        WHERE id = ?
    """
    executar_comando(sql, (nome, descricao.strip(), int(exame_de_local), tipo_id))


def alternar_status_tipo_exame(tipo_id: int) -> bool:
    """
    Ativa ou desativa um tipo de exame.

    Args:
        tipo_id: ID do tipo de exame

    Returns:
        True se ficou ativo, False se ficou inativo

    Raises:
        ValueError: Se o tipo não existir
    """
    tipo = buscar_tipo_exame(tipo_id)
    if not tipo:
        raise ValueError("Tipo de exame não encontrado.")

    novo_status = 0 if tipo["ativo"] else 1

    executar_comando(
        "UPDATE tipos_exame SET ativo = ? WHERE id = ?",
        (novo_status, tipo_id)
    )

    return bool(novo_status)


def excluir_tipo_exame(tipo_id: int) -> None:
    """
    Exclui um tipo de exame pelo ID.

    Só permite excluir se não houver REPs vinculadas.

    Args:
        tipo_id: ID do tipo de exame

    Raises:
        ValueError: Se não existir ou tiver REPs vinculadas
    """
    tipo = buscar_tipo_exame(tipo_id)
    if not tipo:
        raise ValueError("Tipo de exame não encontrado.")

    # Verifica se há REPs vinculadas
    em_uso = executar_query(
        "SELECT id FROM requisicoes WHERE tipo_exame_id = ? LIMIT 1",
        (tipo_id,)
    )
    if em_uso:
        raise ValueError(
            f"Não é possível excluir '{tipo['nome']}' pois "
            f"existem REPs vinculadas. Desative-o ao invés de excluir."
        )

    executar_comando(
        "DELETE FROM tipos_exame WHERE id = ?",
        (tipo_id,)
    )


# ══════════════════════════════════════════════════════
# SOLICITANTES
# ══════════════════════════════════════════════════════

def listar_solicitantes(apenas_ativos: bool = True) -> list:
    """
    Retorna todos os solicitantes cadastrados.

    Args:
        apenas_ativos: Se True, retorna só os ativos.

    Returns:
        Lista de dicionários com os solicitantes.
    """
    if apenas_ativos:
        sql = """
            SELECT id, nome, orgao, contato, ativo
            FROM solicitantes
            WHERE ativo = 1
            ORDER BY nome
        """
    else:
        sql = """
            SELECT id, nome, orgao, contato, ativo
            FROM solicitantes
            ORDER BY nome
        """

    rows = executar_query(sql)
    return [dict(row) for row in rows]


def buscar_solicitante(solicitante_id: int) -> dict | None:
    """
    Busca um solicitante pelo ID.

    Args:
        solicitante_id: ID do solicitante

    Returns:
        Dicionário com os dados ou None se não encontrado
    """
    sql = """
        SELECT id, nome, orgao, contato, ativo
        FROM solicitantes
        WHERE id = ?
    """
    rows = executar_query(sql, (solicitante_id,))

    if rows:
        return dict(rows[0])
    return None


def criar_solicitante(
    nome:    str,
    orgao:   str = "",
    contato: str = "",
) -> int:
    """
    Cria um novo solicitante.

    Args:
        nome:    Nome do solicitante (obrigatório)
        orgao:   Órgão ao qual pertence
        contato: Telefone ou e-mail de contato

    Returns:
        ID do novo solicitante criado

    Raises:
        ValueError: Se o nome estiver vazio ou já existir
    """
    nome = nome.strip()

    if not nome:
        raise ValueError("O nome do solicitante é obrigatório.")

    existe = executar_query(
        "SELECT id FROM solicitantes WHERE LOWER(nome) = LOWER(?)",
        (nome,)
    )
    if existe:
        raise ValueError(f"Já existe um solicitante com o nome '{nome}'.")

    sql = """
        INSERT INTO solicitantes (nome, orgao, contato, ativo)
        VALUES (?, ?, ?, 1)
    """
    return executar_comando(sql, (nome, orgao.strip(), contato.strip()))


def atualizar_solicitante(
    solicitante_id: int,
    nome:           str,
    orgao:          str = "",
    contato:        str = "",
) -> None:
    """
    Atualiza os dados de um solicitante existente.

    Args:
        solicitante_id: ID do solicitante
        nome:           Novo nome
        orgao:          Novo órgão
        contato:        Novo contato

    Raises:
        ValueError: Se não existir ou nome já usado
    """
    nome = nome.strip()

    if not nome:
        raise ValueError("O nome do solicitante é obrigatório.")

    solicitante = buscar_solicitante(solicitante_id)
    if not solicitante:
        raise ValueError("Solicitante não encontrado.")

    existe = executar_query(
        """
        SELECT id FROM solicitantes
        WHERE LOWER(nome) = LOWER(?) AND id != ?
        """,
        (nome, solicitante_id)
    )
    if existe:
        raise ValueError(f"Já existe um solicitante com o nome '{nome}'.")

    sql = """
        UPDATE solicitantes
        SET nome = ?, orgao = ?, contato = ?
        WHERE id = ?
    """
    executar_comando(sql, (nome, orgao.strip(), contato.strip(), solicitante_id))


def alternar_status_solicitante(solicitante_id: int) -> bool:
    """
    Ativa ou desativa um solicitante.

    Args:
        solicitante_id: ID do solicitante

    Returns:
        True se ficou ativo, False se ficou inativo

    Raises:
        ValueError: Se o solicitante não existir
    """
    solicitante = buscar_solicitante(solicitante_id)
    if not solicitante:
        raise ValueError("Solicitante não encontrado.")

    novo_status = 0 if solicitante["ativo"] else 1

    executar_comando(
        "UPDATE solicitantes SET ativo = ? WHERE id = ?",
        (novo_status, solicitante_id)
    )

    return bool(novo_status)


def excluir_solicitante(solicitante_id: int) -> None:
    """
    Exclui um solicitante pelo ID.

    Só permite excluir se não houver REPs vinculadas.

    Args:
        solicitante_id: ID do solicitante

    Raises:
        ValueError: Se não existir ou tiver REPs vinculadas
    """
    solicitante = buscar_solicitante(solicitante_id)
    if not solicitante:
        raise ValueError("Solicitante não encontrado.")

    em_uso = executar_query(
        "SELECT id FROM requisicoes WHERE solicitante_id = ? LIMIT 1",
        (solicitante_id,)
    )
    if em_uso:
        raise ValueError(
            f"Não é possível excluir '{solicitante['nome']}' pois "
            f"existem REPs vinculadas. Desative-o ao invés de excluir."
        )

    executar_comando(
        "DELETE FROM solicitantes WHERE id = ?",
        (solicitante_id,)
    )