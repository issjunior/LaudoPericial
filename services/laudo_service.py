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

import json
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
        SELECT l.id, l.rep_id, l.template_id, l.status, l.versao_atual, l.criado_em, l.atualizado_em, r.usuario_id
        FROM laudos l
        JOIN rep r ON l.rep_id = r.id
        WHERE l.id = ?
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
        "UPDATE secoes_laudo SET conteudo = ?, atualizado_em = datetime('now','localtime') WHERE id = ?",
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


def salvar_versao_snapshot(laudo_id: int) -> int:
    """
    Salva um snapshot do laudo com todas as seções.
    Mantém máximo de 3 versões (remove a mais antiga se houver mais).

    Args:
        laudo_id: ID do laudo.

    Returns:
        Número da versão salva.

    Raises:
        ValueError: Se o laudo não existir.
    """
    laudo = buscar_laudo(laudo_id)
    if not laudo:
        raise ValueError("Laudo não encontrado.")

    secoes = listar_secoes_laudo(laudo_id)
    
    snapshot_data = {
        "laudo_id": laudo_id,
        "rep_id": laudo['rep_id'],
        "template_id": laudo['template_id'],
        "versao_atual": laudo['versao_atual'],
        "secoes": [
            {
                "id": s['id'],
                "titulo": s['titulo'],
                "conteudo": s['conteudo'],
                "ordem": s['ordem'],
                "obrigatoria": s['obrigatoria'],
                "permite_fotos": s['permite_fotos']
            }
            for s in secoes
        ]
    }
    
    snapshot_json = json.dumps(snapshot_data, ensure_ascii=False)
    
    ultima_versao = buscar_ultima_versao(laudo_id)
    nova_versao = (ultima_versao['versao'] + 1) if ultima_versao else 1
    
    executar_comando(
        "INSERT INTO versoes_laudo (laudo_id, versao, snapshot) VALUES (?, ?, ?)",
        (laudo_id, nova_versao, snapshot_json)
    )
    
    limitar_versoes(laudo_id)
    
    return nova_versao


def limitar_versoes(laudo_id: int) -> None:
    """
    Limita o número de versões para no máximo 3 (as mais recentes).
    Remove as versões mais antigas se houver mais de 3.
    """
    sql_count = "SELECT COUNT(*) as total FROM versoes_laudo WHERE laudo_id = ?"
    resultado = executar_query(sql_count, (laudo_id,))
    total = resultado[0]['total'] if resultado else 0
    
    if total > 3:
        versoes_a_manter = """
            SELECT id FROM versoes_laudo 
            WHERE laudo_id = ? 
            ORDER BY versao DESC 
            LIMIT 3
        """
        ids_manter = [row['id'] for row in executar_query(versoes_a_manter, (laudo_id,))]
        
        if ids_manter:
            placeholders = ','.join('?' * len(ids_manter))
            sql_delete = f"""
                DELETE FROM versoes_laudo 
                WHERE laudo_id = ? AND id NOT IN ({placeholders})
            """
            executar_comando(sql_delete, (laudo_id, *ids_manter))


def buscar_ultima_versao(laudo_id: int) -> dict | None:
    """Busca a última versão salva do laudo."""
    sql = """
        SELECT id, laudo_id, versao, snapshot, criado_em
        FROM versoes_laudo
        WHERE laudo_id = ?
        ORDER BY versao DESC
        LIMIT 1
    """
    rows = executar_query(sql, (laudo_id,))
    if rows:
        return dict(rows[0])
    return None


def listar_versoes(laudo_id: int) -> list:
    """
    Lista todas as versões de um laudo (máximo 3).

    Args:
        laudo_id: ID do laudo.

    Returns:
        Lista de versões ordenadas da mais recente para a mais antiga.
    """
    sql = """
        SELECT id, laudo_id, versao, snapshot, criado_em
        FROM versoes_laudo
        WHERE laudo_id = ?
        ORDER BY versao DESC
    """
    rows = executar_query(sql, (laudo_id,))
    return [dict(row) for row in rows]


def excluir_versao(versao_id: int) -> bool:
    """Exclui uma versão específica do laudo."""
    sql = "SELECT id FROM versoes_laudo WHERE id = ?"
    rows = executar_query(sql, (versao_id,))
    
    if not rows:
        return False
    
    executar_comando("DELETE FROM versoes_laudo WHERE id = ?", (versao_id,))
    return True


def restaurar_versao(versao_id: int) -> None:
    """
    Restaura o laudo para uma versão anterior.

    Args:
        versao_id: ID da versão a ser restaurada.
    """
    sql = "SELECT snapshot FROM versoes_laudo WHERE id = ?"
    rows = executar_query(sql, (versao_id,))
    
    if not rows:
        raise ValueError("Versão não encontrada.")
    
    snapshot_data = json.loads(rows[0]['snapshot'])
    
    for secao in snapshot_data['secoes']:
        executar_comando(
            """UPDATE secoes_laudo 
               SET conteudo = ?, atualizado_em = datetime('now','localtime') 
               WHERE id = ?""",
            (secao['conteudo'], secao['id'])
        )