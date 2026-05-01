# services/rep_service.py
"""
services/rep_service.py
──────────────────────────────────────────────────────
Serviço responsável pelo gerenciamento de Requisições de Exame Pericial (REP).
──────────────────────────────────────────────────────
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
from services.cadastro_service import buscar_tipo_exame, buscar_solicitante

# ══════════════════════════════════════════════════════
# REQUISIÇÕES DE EXAME PERICIAL (REP)
# ══════════════════════════════════════════════════════

def listar_reps(
    apenas_ativas: bool = False,
    usuario_id: int = None,
    status: str = None,
    numero_rep: str = None,
    tipo_exame_id: int = None,
    solicitante_id: int = None,
    data_inicio: str = None, # Formato YYYY-MM-DD
    data_fim: str = None     # Formato YYYY-MM-DD
) -> list:
    sql = """
        SELECT
            r.id, r.numero_rep, r.data_solicitacao, r.horario_acionamento,
            r.horario_chegada, r.horario_saida, r.tipo_solicitacao,
            r.numero_documento, r.data_documento, r.solicitante_id,
            s.nome AS solicitante_nome, s.orgao AS solicitante_orgao,
            r.nome_autoridade, r.nome_envolvido, r.local_fato_descricao,
            r.tipo_exame_id, te.nome AS tipo_exame_nome,
            te.codigo AS tipo_exame_codigo, te.exame_de_local,
            r.latitude, r.longitude, r.lacre_entrada, r.lacre_saida,
            r.status, r.observacoes,
            r.usuario_id, u.nome AS usuario_nome, r.criado_em, r.atualizado_em
        FROM rep r
        LEFT JOIN solicitantes s ON r.solicitante_id = s.id
        LEFT JOIN tipos_exame te ON r.tipo_exame_id = te.id
        LEFT JOIN usuarios u ON r.usuario_id = u.id
    """
    params = []
    conditions = []

    if apenas_ativas:
        conditions.append("r.status IN ('Pendente', 'Em Andamento')")
    if usuario_id:
        conditions.append("r.usuario_id = ?")
        params.append(usuario_id)
    if status:
        conditions.append("r.status = ?")
        params.append(status)
    if numero_rep:
        conditions.append("LOWER(r.numero_rep) LIKE LOWER(?)")
        params.append(f"%{numero_rep}%")
    if tipo_exame_id:
        conditions.append("r.tipo_exame_id = ?")
        params.append(tipo_exame_id)
    if solicitante_id:
        conditions.append("r.solicitante_id = ?")
        params.append(solicitante_id)
    if data_inicio:
        conditions.append("r.data_solicitacao >= ?")
        params.append(data_inicio)
    if data_fim:
        conditions.append("r.data_solicitacao <= ?")
        params.append(data_fim)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY r.data_solicitacao DESC, r.numero_rep DESC"
    rows = executar_query(sql, tuple(params))
    return [dict(row) for row in rows]


def buscar_rep(rep_id: int) -> dict | None:
    sql = """
        SELECT
            r.id, r.numero_rep, r.data_solicitacao, r.horario_acionamento,
            r.horario_chegada, r.horario_saida, r.tipo_solicitacao,
            r.numero_documento, r.data_documento, r.solicitante_id,
            s.nome AS solicitante_nome, s.orgao AS solicitante_orgao,
            s.contato AS solicitante_email, r.nome_autoridade,
            r.nome_envolvido, r.local_fato_descricao, r.tipo_exame_id,
            te.nome AS tipo_exame_nome, te.codigo AS tipo_exame_codigo,
            te.exame_de_local, r.latitude, r.longitude,
            r.lacre_entrada, r.lacre_saida,
            r.status, r.observacoes, r.usuario_id, u.nome AS usuario_nome,
            u.matricula AS usuario_matricula, u.cargo AS usuario_cargo,
            u.lotacao AS usuario_lotacao, r.criado_em, r.atualizado_em
        FROM rep r
        LEFT JOIN solicitantes s ON r.solicitante_id = s.id
        LEFT JOIN tipos_exame te ON r.tipo_exame_id = te.id
        LEFT JOIN usuarios u ON r.usuario_id = u.id
        WHERE r.id = ?
    """
    rows = executar_query(sql, (rep_id,))
    return dict(rows[0]) if rows else None


def criar_rep(
    numero_rep, data_solicitacao, tipo_solicitacao, numero_documento, usuario_id,
    tipo_exame_id=None, horario_acionamento=None, horario_chegada=None,
    horario_saida=None, data_documento=None, solicitante_id=None,
    nome_autoridade=None, nome_envolvido=None, local_fato_descricao=None,
    latitude=None, longitude=None, lacre_entrada=None, lacre_saida=None,
    observacoes=None
) -> int:
    numero_rep = numero_rep.strip()
    if not numero_rep:
        raise ValueError("O número da REP é obrigatório.")

    existe = executar_query("SELECT id FROM rep WHERE LOWER(numero_rep) = LOWER(?)", (numero_rep,))
    if existe:
        raise ValueError(f"Já existe outra REP com o número '{numero_rep}'.")

    if tipo_exame_id and not buscar_tipo_exame(tipo_exame_id):
        raise ValueError("Tipo de exame não encontrado.")
    if solicitante_id and not buscar_solicitante(solicitante_id):
        raise ValueError("Solicitante não encontrado.")

    sql = """
        INSERT INTO rep (
            numero_rep, data_solicitacao, horario_acionamento, horario_chegada,
            horario_saida, tipo_solicitacao, numero_documento, data_documento,
            solicitante_id, nome_autoridade, tipo_exame_id,
            nome_envolvido, local_fato_descricao,
            latitude, longitude, lacre_entrada, lacre_saida,
            status, observacoes, usuario_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pendente', ?, ?)
    """
    return executar_comando(sql, (
        numero_rep, data_solicitacao, horario_acionamento, horario_chegada,
        horario_saida, tipo_solicitacao, numero_documento, data_documento,
        solicitante_id, nome_autoridade, tipo_exame_id,
        nome_envolvido, local_fato_descricao,
        latitude, longitude, lacre_entrada, lacre_saida, observacoes, usuario_id
    ))


def atualizar_rep(
    rep_id, numero_rep, data_solicitacao, tipo_solicitacao, numero_documento,
    tipo_exame_id, usuario_id, horario_acionamento=None, horario_chegada=None,
    horario_saida=None, data_documento=None, solicitante_id=None,
    nome_autoridade=None, nome_envolvido=None, local_fato_descricao=None,
    latitude=None, longitude=None, lacre_entrada=None, lacre_saida=None,
    status=None, observacoes=None
) -> None:
    numero_rep = numero_rep.strip()
    if not numero_rep:
        raise ValueError("O número da REP é obrigatório.")

    rep_existente = buscar_rep(rep_id)
    if not rep_existente:
        raise ValueError("REP não encontrada.")

    existe = executar_query("SELECT id FROM rep WHERE LOWER(numero_rep) = LOWER(?) AND id != ?", (numero_rep, rep_id))
    if existe:
        raise ValueError(f"Já existe outra REP com o número '{numero_rep}'.")

    if tipo_exame_id and not buscar_tipo_exame(tipo_exame_id):
        raise ValueError("Tipo de exame não encontrado.")
    if solicitante_id and not buscar_solicitante(solicitante_id):
        raise ValueError("Solicitante não encontrado.")

    # Ajuste de status automático
    if tipo_exame_id is None and status != "Pendente":
        status = "Pendente"
    elif rep_existente['tipo_exame_id'] is None and tipo_exame_id and status == "Pendente":
        status = "Em Andamento"

    sql = """
        UPDATE rep
        SET
            numero_rep = ?, data_solicitacao = ?, horario_acionamento = ?,
            horario_chegada = ?, horario_saida = ?, tipo_solicitacao = ?,
            numero_documento = ?, data_documento = ?, solicitante_id = ?,
            nome_autoridade = ?, tipo_exame_id = ?,
            nome_envolvido = ?, local_fato_descricao = ?,
            latitude = ?, longitude = ?, lacre_entrada = ?, lacre_saida = ?,
            status = ?, observacoes = ?, usuario_id = ?
        WHERE id = ?
    """
    executar_comando(sql, (
        numero_rep, data_solicitacao, horario_acionamento, horario_chegada,
        horario_saida, tipo_solicitacao, numero_documento, data_documento,
        solicitante_id, nome_autoridade, tipo_exame_id,
        nome_envolvido, local_fato_descricao,
        latitude, longitude, lacre_entrada, lacre_saida, status, observacoes, usuario_id, rep_id
    ))


def verificar_laudo_vinculado(rep_id: int) -> dict | None:
    sql = "SELECT id, status, versao_atual, criado_em FROM laudos WHERE rep_id = ?"
    rows = executar_query(sql, (rep_id,))
    return dict(rows[0]) if rows else None


def excluir_rep(rep_id: int, forcar_exclusao: bool = False) -> str:
    rep_existente = buscar_rep(rep_id)
    if not rep_existente:
        raise ValueError("REP não encontrada.")

    laudo_vinculado = verificar_laudo_vinculado(rep_id)
    if laudo_vinculado and not forcar_exclusao:
        return "AVISO: Esta REP tem um laudo vinculado que será excluído junto."

    try:
        if laudo_vinculado:
            executar_comando("DELETE FROM laudos WHERE rep_id = ?", (rep_id,))
        executar_comando("DELETE FROM rep WHERE id = ?", (rep_id,))
        
        from core.audit import registrar
        registrar(tabela="rep", registro_id=rep_id, operacao="EXCLUIR", 
                  descricao=f"REP '{rep_existente['numero_rep']}' excluída")
        return "REP excluída com sucesso!"
    except Exception as e:
        raise ValueError(f"Erro ao excluir REP: {e}")


def alterar_status_rep_simples(rep_id: int, novo_status: str) -> None:
    STATUS_VALIDOS = ["Pendente", "Em Andamento", "Concluido"]
    if novo_status not in STATUS_VALIDOS:
        raise ValueError(f"Status inválido: {novo_status}")

    executar_comando(
        "UPDATE rep SET status = ?, atualizado_em = datetime('now','localtime') WHERE id = ?",
        (novo_status, rep_id)
    )