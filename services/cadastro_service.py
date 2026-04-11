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
import re # Importar 're' para validação de e-mail

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
            SELECT id, codigo, nome, descricao, exame_de_local, ativo
            FROM tipos_exame
            WHERE ativo = 1
            ORDER BY codigo
        """
    else:
        sql = """
            SELECT id, codigo, nome, descricao, exame_de_local, ativo
            FROM tipos_exame
            ORDER BY codigo
        """

    rows = executar_query(sql)
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
        SELECT id, codigo, nome, descricao, exame_de_local, ativo
        FROM tipos_exame
        WHERE id = ?
    """
    rows = executar_query(sql, (tipo_id,))

    if rows:
        return dict(rows[0])
    return None


def criar_tipo_exame(
    codigo:         str,
    nome:           str,
    descricao:      str  = "",
    exame_de_local: bool = False,
) -> int:
    """
    Cria um novo tipo de exame.

    Args:
        codigo:         Código único do exame (ex: H-001)
        nome:           Nome do tipo de exame (obrigatório)
        descricao:      Descrição opcional
        exame_de_local: Se exige deslocamento ao local

    Returns:
        ID do novo tipo de exame criado

    Raises:
        ValueError: Se o código ou nome estiverem vazios
                    ou já existirem
    """
    codigo = codigo.strip().upper()
    nome   = nome.strip()

    if not codigo:
        raise ValueError("O código do exame é obrigatório.")

    if not nome:
        raise ValueError("O nome do tipo de exame é obrigatório.")

    # Valida formato X-000
    if not re.match(r'^[A-Z]-\d{3}$', codigo):
        raise ValueError(
            "Código inválido. Use o formato X-000 "
            "(1 letra, hífen, 3 números). Ex: H-001"
        )

    # Valida tamanho máximo
    if len(codigo) > 10:
        raise ValueError("O código deve ter no máximo 10 caracteres.")

    # Verifica duplicidade do código
    existe_codigo = executar_query(
        "SELECT id FROM tipos_exame WHERE UPPER(codigo) = UPPER(?)",
        (codigo,)
    )
    if existe_codigo:
        raise ValueError(f"Já existe um tipo de exame com o código '{codigo}'.")

    # Verifica duplicidade do nome
    existe_nome = executar_query(
        "SELECT id FROM tipos_exame WHERE LOWER(nome) = LOWER(?)",
        (nome,)
    )
    if existe_nome:
        raise ValueError(f"Já existe um tipo de exame com o nome '{nome}'.")

    sql = """
        INSERT INTO tipos_exame (codigo, nome, descricao, exame_de_local, ativo)
        VALUES (?, ?, ?, ?, 1)
    """
    return executar_comando(
        sql,
        (codigo, nome, descricao.strip(), int(exame_de_local))
    )


def atualizar_tipo_exame(
    tipo_id:        int,
    codigo:         str,
    nome:           str,
    descricao:      str  = "",
    exame_de_local: bool = False,
) -> None:
    """
    Atualiza os dados de um tipo de exame existente.

    Args:
        tipo_id:        ID do tipo a atualizar
        codigo:         Novo código
        nome:           Novo nome
        descricao:      Nova descrição
        exame_de_local: Novo valor do campo exame_de_local

    Raises:
        ValueError: Se o tipo não existir, código ou
                    nome inválidos ou já em uso
    """
    codigo = codigo.strip().upper()
    nome   = nome.strip()

    if not codigo:
        raise ValueError("O código do exame é obrigatório.")

    if not nome:
        raise ValueError("O nome do tipo de exame é obrigatório.")

    # Valida formato X-000
    if not re.match(r'^[A-Z]-\d{3}$', codigo):
        raise ValueError(
            "Código inválido. Use o formato X-000 "
            "(1 letra, hífen, 3 números). Ex: H-001"
        )

    # Verifica se o tipo existe
    tipo = buscar_tipo_exame(tipo_id)
    if not tipo:
        raise ValueError("Tipo de exame não encontrado.")

    # Verifica duplicidade do código (ignora o próprio)
    existe_codigo = executar_query(
        """
        SELECT id FROM tipos_exame
        WHERE UPPER(codigo) = UPPER(?) AND id != ?
        """,
        (codigo, tipo_id)
    )
    if existe_codigo:
        raise ValueError(f"Já existe um tipo de exame com o código '{codigo}'.")

    # Verifica duplicidade do nome (ignora o próprio)
    existe_nome = executar_query(
        """
        SELECT id FROM tipos_exame
        WHERE LOWER(nome) = LOWER(?) AND id != ?
        """,
        (nome, tipo_id)
    )
    if existe_nome:
        raise ValueError(f"Já existe um tipo de exame com o nome '{nome}'.")

    sql = """
        UPDATE tipos_exame
        SET codigo = ?, nome = ?, descricao = ?, exame_de_local = ?
        WHERE id = ?
    """
    executar_comando(
        sql,
        (codigo, nome, descricao.strip(), int(exame_de_local), tipo_id)
    )


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
            ORDER BY orgao
        """
    else:
        sql = """
            SELECT id, nome, orgao, contato, ativo
            FROM solicitantes
            ORDER BY orgao
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
    nome:    str = "", # Não obrigatório
    orgao:   str = "", # Agora obrigatório
    email:   str = "", # Novo nome, não obrigatório
) -> int:
    """
    Cria um novo solicitante.

    Args:
        nome:    Nome do solicitante (opcional)
        orgao:   Órgão ao qual pertence (obrigatório)
        email:   Email de contato (opcional)

    Returns:
        ID do novo solicitante criado

    Raises:
        ValueError: Se o órgão estiver vazio ou já existir
    """
    nome  = nome.strip()
    orgao = orgao.strip()
    email = email.strip()

    if not orgao:
        raise ValueError("O nome do Órgão é obrigatório.")

    # Verifica duplicidade do órgão (case-insensitive)
    existe = executar_query(
        "SELECT id FROM solicitantes WHERE LOWER(orgao) = LOWER(?)",
        (orgao,)
    )
    if existe:
        raise ValueError(f"Já existe um solicitante com o Órgão '{orgao}'.")

    # Validação de email (se fornecido)
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Formato de e-mail inválido.")

    sql = """
        INSERT INTO solicitantes (nome, orgao, contato, ativo)
        VALUES (?, ?, ?, 1)
    """
    # 'contato' no banco será o 'email' aqui
    return executar_comando(sql, (nome, orgao, email))


def atualizar_solicitante(
    solicitante_id: int,
    nome:           str = "", # Não obrigatório
    orgao:          str = "", # Agora obrigatório
    email:          str = "", # Novo nome, não obrigatório
) -> None:
    """
    Atualiza os dados de um solicitante existente.

    Args:
        solicitante_id: ID do solicitante
        nome:           Novo nome (opcional)
        orgao:          Novo órgão (obrigatório)
        email:          Novo email (opcional)

    Raises:
        ValueError: Se não existir, órgão inválido ou já usado
    """
    nome  = nome.strip()
    orgao = orgao.strip()
    email = email.strip()

    if not orgao:
        raise ValueError("O nome do Órgão é obrigatório.")

    solicitante = buscar_solicitante(solicitante_id)
    if not solicitante:
        raise ValueError("Solicitante não encontrado.")

    # Verifica duplicidade do órgão (ignora o próprio registro)
    existe = executar_query(
        """
        SELECT id FROM solicitantes
        WHERE LOWER(orgao) = LOWER(?) AND id != ?
        """,
        (orgao, solicitante_id)
    )
    if existe:
        raise ValueError(f"Já existe um solicitante com o Órgão '{orgao}'.")

    # Validação de email (se fornecido)
    if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Formato de e-mail inválido.")

    sql = """
        UPDATE solicitantes
        SET nome = ?, orgao = ?, contato = ?
        WHERE id = ?
    """
    # 'contato' no banco será o 'email' aqui
    executar_comando(sql, (nome, orgao, email, solicitante_id))


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