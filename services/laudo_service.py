# services/laudo_service.py
"""
services/laudo_service.py
─────────────────────────────────────────────────────
Serviço de gerenciamento de Laudos.
─────────────────────────────────────────────────────
"""

import sys
import os
from datetime import datetime

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.db import executar_query, executar_comando


def listar_laudos(
    status: str = None,
    usuario_id: int = None,
    rep_id: int = None
) -> list:
    """
    Lista laudos com filtros.

    Args:
        status: Status específico (Rascunho, Em Revisão, Finalizado).
        usuario_id: ID do usuário (através da REP).
        rep_id: ID da REP específica.

    Returns:
        Lista de dicionários com os dados dos laudos.
    """
    sql = """
        SELECT
            l.id,
            l.rep_id,
            l.template_id,
            l.status,
            l.versao_atual,
            l.criado_em,
            l.atualizado_em,
            r.numero_rep,
            r.status AS rep_status,
            te.nome AS tipo_exame_nome
        FROM laudos l
        JOIN rep r ON l.rep_id = r.id
        JOIN tipos_exame te ON r.tipo_exame_id = te.id
    """
    params = []
    conditions = []

    if status:
        conditions.append("l.status = ?")
        params.append(status)

    if usuario_id:
        conditions.append("r.usuario_id = ?")
        params.append(usuario_id)

    if rep_id:
        conditions.append("l.rep_id = ?")
        params.append(rep_id)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY l.atualizado_em DESC"

    rows = executar_query(sql, tuple(params))
    return [dict(row) for row in rows]


def buscar_laudo_por_rep(rep_id: int) -> dict | None:
    """
    Busca um laudo vinculado a uma REP.

    Args:
        rep_id: ID da REP.

    Returns:
        Dicionário com os dados do laudo ou None.
    """
    sql = """
        SELECT id, rep_id, template_id, status, versao_atual, criado_em, atualizado_em
        FROM laudos
        WHERE rep_id = ?
    """
    rows = executar_query(sql, (rep_id,))
    if rows:
        return dict(rows[0])
    return None


def verificar_laudo_existe(rep_id: int) -> bool:
    """Verifica se existe laudo para a REP."""
    return buscar_laudo_por_rep(rep_id) is not None


def criar_laudo(rep_id: int, template_id: int) -> int:
    """
    Cria um novo laudo a partir de uma REP e template.

    Args:
        rep_id: ID da REP.
        template_id: ID do template.

    Returns:
        ID do laudo criado.

    Raises:
        ValueError: Se a REP ou template não existir, ou se já existir laudo.
    """
    from services.rep_service import buscar_rep
    from services.template_service import buscar_template

    rep = buscar_rep(rep_id)
    if not rep:
        raise ValueError("REP não encontrada.")

    template = buscar_template(template_id)
    if not template:
        raise ValueError("Template não encontrado.")

    if verificar_laudo_existe(rep_id):
        raise ValueError(f"Já existe laudo para esta REP.")

    from database.db import executar_comando
    executar_comando(
        """
        INSERT INTO laudos (rep_id, template_id, status, versao_atual)
        VALUES (?, ?, 'Rascunho', 1)
        """,
        (rep_id, template_id)
    )

    novo_laudo = buscar_laudo_por_rep(rep_id)
    if not novo_laudo:
        raise ValueError("Erro ao criar laudo.")

    from services.template_service import listar_secoes_template
    secoes = listar_secoes_template(template_id)
    for secao in secoes:
        executar_comando(
            """
            INSERT INTO secoes_laudo (
                laudo_id, secao_template_id, titulo, conteudo, ordem, obrigatoria, permite_fotos
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                novo_laudo['id'],
                secao['id'],
                secao['titulo'],
                secao['conteudo_base'],
                secao['ordem'],
                secao['obrigatoria'],
                secao['permite_fotos']
            )
        )

    from services.rep_service import buscar_rep
    from services.rep_service import alterar_status_rep_simples
    alterar_status_rep_simples(rep_id, "Em Andamento")

    return novo_laudo['id']


def buscar_laudo(laudo_id: int) -> dict | None:
    """
    Busca um laudo pelo ID.

    Args:
        laudo_id: ID do laudo.

    Returns:
        Dicionário com os dados do laudo ou None.
    """
    sql = """
        SELECT id, rep_id, template_id, status, versao_atual, criado_em, atualizado_em
        FROM laudos
        WHERE id = ?
    """
    rows = executar_query(sql, (laudo_id,))
    if rows:
        return dict(rows[0])
    return None


def listar_secoes_laudo(laudo_id: int) -> list:
    """
    Lista as seções de um laudo.

    Args:
        laudo_id: ID do laudo.

    Returns:
        Lista de dicionários com as seções.
    """
    sql = """
        SELECT id, laudo_id, secao_template_id, titulo, conteudo, ordem, obrigatoria, permite_fotos
        FROM secoes_laudo
        WHERE laudo_id = ?
        ORDER BY ordem
    """
    rows = executar_query(sql, (laudo_id,))
    return [dict(row) for row in rows]


def atualizar_secao_laudo(secao_laudo_id: int, conteudo: str) -> None:
    """
    Atualiza o conteúdo de uma seção do laudo.

    Args:
        secao_laudo_id: ID da seção.
        conteudo: Novo conteúdo.
    """
    from database.db import executar_comando
    executar_comando(
        "UPDATE secoes_laudo SET conteudo = ?, updated_at = datetime('now','localtime') WHERE id = ?",
        (conteudo, secao_laudo_id)
    )


def finalizar_laudo(laudo_id: int) -> None:
    """
    Finaliza um laudo (muda status para Finalizado).

    Args:
        laudo_id: ID do laudo.

    Raises:
        ValueError: Se o laudo não existir.
    """
    laudo = buscar_laudo(laudo_id)
    if not laudo:
        raise ValueError("Laudo não encontrado.")

    from database.db import executar_comando
    executar_comando(
        "UPDATE laudos SET status = 'Finalizado', atualizado_em = datetime('now','localtime') WHERE id = ?",
        (laudo_id,)
    )

    from services.rep_service import buscar_rep
    from services.rep_service import alterar_status_rep_simples
    rep = buscar_rep(laudo['rep_id'])
    if rep:
        alterar_status_rep_simples(rep['id'], "Concluído")