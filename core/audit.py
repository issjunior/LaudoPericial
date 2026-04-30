"""
core/audit.py
──────────────────────────────────────────────────────
Registra todas as operações no sistema para auditoria.
Quem fez, o quê, quando e em qual registro.
──────────────────────────────────────────────────────
"""

import json
import streamlit as st
from database.db import executar_query, executar_comando


def registrar(
    tabela:           str,
    registro_id:      int,
    operacao:         str,
    descricao:        str  = "",
    dados_anteriores: dict = None
) -> None:
    """
    Registra uma operação no histórico do sistema.

    Args:
        tabela:           nome da tabela afetada
                          (ex: 'rep', 'laudos', 'templates')
        registro_id:      ID do registro afetado
        operacao:         tipo da operação realizada
                          ('CRIAR','EDITAR','EXCLUIR',
                           'FINALIZAR','LOGIN','LOGOUT')
        descricao:        texto descrevendo o que foi feito
        dados_anteriores: dados antes da alteração (para EDITAR)
                          será salvo como JSON
    """
    # Pega o ID do usuário logado na sessão
    usuario_id = st.session_state.get("usuario_id")

    # Converte dados anteriores para JSON se fornecido
    dados_json = None
    if dados_anteriores:
        dados_json = json.dumps(
            dados_anteriores,
            ensure_ascii=False
        )

    executar_comando("""
        INSERT INTO historico
            (usuario_id, tabela, registro_id,
             operacao, descricao, dados_anteriores)
        VALUES
            (?, ?, ?, ?, ?, ?)
    """, (
        usuario_id,
        tabela,
        registro_id,
        operacao,
        descricao,
        dados_json
    ))


def buscar_historico_registro(
    tabela:      str,
    registro_id: int
) -> list:
    """
    Busca todo o histórico de um registro específico.
    Usado para mostrar o histórico dentro de uma REP ou laudo.

    Args:
        tabela:      nome da tabela (ex: 'rep')
        registro_id: ID do registro

    Returns:
        Lista de eventos ordenados do mais recente ao mais antigo
    """
    rows = executar_query("""
        SELECT
            h.criado_em,
            h.operacao,
            h.descricao,
            h.dados_anteriores,
            u.nome      AS usuario_nome,
            u.matricula AS usuario_matricula
        FROM historico h
        LEFT JOIN usuarios u ON h.usuario_id = u.id
        WHERE h.tabela      = ?
          AND h.registro_id = ?
        ORDER BY h.criado_em DESC
    """, (tabela, registro_id))

    return [dict(row) for row in rows]


def buscar_historico_geral(
    limite:    int  = 100,
    operacao:  str  = None,
    tabela:    str  = None,
    data_ini:  str  = None,
    data_fim:  str  = None
) -> list:
    """
    Busca o histórico geral do sistema com filtros opcionais.
    Usado na página de auditoria global.

    Args:
        limite:   máximo de registros a retornar
        operacao: filtrar por tipo de operação (opcional)
        tabela:   filtrar por tabela (opcional)
        data_ini: filtrar a partir desta data 'YYYY-MM-DD'
        data_fim: filtrar até esta data 'YYYY-MM-DD'

    Returns:
        Lista de eventos de auditoria
    """
    # Monta a query dinamicamente conforme os filtros
    sql    = """
        SELECT
            h.id,
            h.criado_em,
            h.tabela,
            h.registro_id,
            h.operacao,
            h.descricao,
            h.dados_anteriores,
            u.nome      AS usuario_nome,
            u.matricula AS usuario_matricula
        FROM historico h
        LEFT JOIN usuarios u ON h.usuario_id = u.id
        WHERE 1=1
    """
    params = []

    if operacao:
        sql += " AND h.operacao = ?"
        params.append(operacao)

    if tabela:
        sql += " AND h.tabela = ?"
        params.append(tabela)

    if data_ini:
        sql += " AND DATE(h.criado_em) >= ?"
        params.append(data_ini)

    if data_fim:
        sql += " AND DATE(h.criado_em) <= ?"
        params.append(data_fim)

    sql += " ORDER BY h.criado_em DESC LIMIT ?"
    params.append(limite)

    rows = executar_query(sql, tuple(params))
    return [dict(row) for row in rows]


def formatar_operacao(operacao: str) -> str:
    """
    Retorna um texto amigável e emoji para cada tipo
    de operação. Usado na exibição do histórico.

    Args:
        operacao: código da operação

    Returns:
        String formatada para exibição
    """
    mapa = {
        "CRIAR":     "🟢 Criado",
        "EDITAR":    "🔵 Editado",
        "EXCLUIR":   "🔴 Excluído",
        "FINALIZAR": "✅ Finalizado",
        "LOGIN":     "🔑 Login",
        "LOGOUT":    "🚪 Logout",
    }
    return mapa.get(operacao, operacao)
