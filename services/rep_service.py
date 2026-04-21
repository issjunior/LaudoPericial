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

# Garante que a raiz do projeto está no sys.path
# Funciona localmente E no Streamlit Cloud
ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.db import executar_query, executar_comando
from services.cadastro_service import buscar_tipo_exame, buscar_solicitante
# A importação de obter_usuario_logado não é estritamente necessária aqui,
# pois o serviço de REP não precisa saber quem é o usuário logado para suas funções.
# Ela foi incluída anteriormente por engano ou para um cenário futuro que não se concretizou.
# Vamos removê-la para evitar confusão e possíveis erros de importação desnecessários.
# from services.auth_service import obter_usuario_logado


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
    """
    Lista as Requisições de Exame Pericial (REPs) com filtros.

    Args:
        apenas_ativas: Se True, filtra por status 'Pendente' ou 'Em Andamento'.
        usuario_id: ID do usuário (perito) responsável.
        status: Status específico da REP (ex: 'Pendente', 'Concluído').
        numero_rep: Número da REP (busca parcial).
        tipo_exame_id: ID do tipo de exame.
        solicitante_id: ID do solicitante.
        data_inicio: Data de solicitação mínima (YYYY-MM-DD).
        data_fim: Data de solicitação máxima (YYYY-MM-DD).

    Returns:
        Lista de dicionários com os dados das REPs.
    """
    sql = """
        SELECT
            r.id,
            r.numero_rep,
            r.data_solicitacao,
            r.horario_acionamento,
            r.horario_chegada,
            r.horario_saida,
            r.tipo_solicitacao,
            r.numero_documento,
            r.data_documento,
            r.solicitante_id,
            s.nome AS solicitante_nome,
            s.orgao AS solicitante_orgao,
            r.nome_autoridade,
            r.nome_envolvido,
            r.local_fato_descricao,
            r.tipo_exame_id,
            te.nome AS tipo_exame_nome,
            te.codigo AS tipo_exame_codigo,
            te.exame_de_local,
            r.latitude,
            r.longitude,
            r.status,
            r.observacoes,
            r.usuario_id,
            u.nome AS usuario_nome,
            r.criado_em,
            r.atualizado_em
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
    """
    Busca uma REP pelo ID.

    Args:
        rep_id: ID da REP.

    Returns:
        Dicionário com os dados da REP ou None se não encontrada.
    """
    sql = """
        SELECT
            r.id,
            r.numero_rep,
            r.data_solicitacao,
            r.horario_acionamento,
            r.horario_chegada,
            r.horario_saida,
            r.tipo_solicitacao,
            r.numero_documento,
            r.data_documento,
            r.solicitante_id,
            s.nome AS solicitante_nome,
            s.orgao AS solicitante_orgao,
            s.contato AS solicitante_email, -- Adicionado para o placeholder
            r.nome_autoridade,
            r.nome_envolvido,
            r.local_fato_descricao,
            r.tipo_exame_id,
            te.nome AS tipo_exame_nome,
            te.codigo AS tipo_exame_codigo,
            te.exame_de_local,
            r.latitude,
            r.longitude,
            r.status,
            r.observacoes,
            r.usuario_id,
            u.nome AS usuario_nome,
            u.matricula AS usuario_matricula,
            u.cargo AS usuario_cargo,
            u.lotacao AS usuario_lotacao,
            r.criado_em,
            r.atualizado_em
        FROM rep r
        LEFT JOIN solicitantes s ON r.solicitante_id = s.id
        LEFT JOIN tipos_exame te ON r.tipo_exame_id = te.id
        LEFT JOIN usuarios u ON r.usuario_id = u.id
        WHERE r.id = ?
    """
    rows = executar_query(sql, (rep_id,))
    if rows:
        return dict(rows[0])
    return None

def criar_rep(
    numero_rep:          str,
    data_solicitacao:    str, # YYYY-MM-DD
    tipo_solicitacao:    str,
    numero_documento:    str,
    tipo_exame_id:       int,
    usuario_id:          int,
    horario_acionamento: str = None, # HH:MM
    horario_chegada:     str = None, # HH:MM
    horario_saida:       str = None, # HH:MM
    data_documento:      str = None, # YYYY-MM-DD
    solicitante_id:      int = None,
    nome_autoridade:     str = None,
    nome_envolvido:      str = None, # NOVO PARÂMETRO
    local_fato_descricao:str = None, # NOVO PARÂMETRO
    latitude:            str = None,
    longitude:           str = None,
    observacoes:         str = None,
) -> int:
    """
    Cria uma nova Requisição de Exame Pericial (REP).
    ... (docstring permanece o mesmo, adicione os novos args) ...
    """
    numero_rep = numero_rep.strip()
    if not numero_rep:
        raise ValueError("O número da REP é obrigatório.")

    # Verifica se o número da REP já existe
    existe = executar_query(
        "SELECT id FROM rep WHERE LOWER(numero_rep) = LOWER(?)",
        (numero_rep,)
    )
    if existe:
        raise ValueError(f"Já existe outra REP com o número '{numero_rep}'.")

    # Validações de IDs (tipo_exame_id pode ser None)
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
            latitude, longitude, status, observacoes, usuario_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pendente', ?, ?)
    """
    rep_id = executar_comando(
        sql,
        (
            numero_rep, data_solicitacao, horario_acionamento, horario_chegada,
            horario_saida, tipo_solicitacao, numero_documento, data_documento,
            solicitante_id, nome_autoridade, tipo_exame_id,
            nome_envolvido, local_fato_descricao,
            latitude, longitude, observacoes, usuario_id
        )
    )

    # Verificar se existe template para o tipo de exame e criar laudo automaticamente
    try:
        from services.template_service import listar_templates
        templates = listar_templates(apenas_ativos=True, tipo_exame_id=tipo_exame_id)
        if templates:
            template_id = templates[0]['id']
            from services.laudo_service import criar_laudo
            criar_laudo(rep_id, template_id)
    except Exception:
        pass  # Se nao conseguir criar laudo, ignora (nao bloqueia criacao da REP)

    return rep_id

def atualizar_rep(
    rep_id:              int,
    numero_rep:          str,
    data_solicitacao:    str, # YYYY-MM-DD
    tipo_solicitacao:    str,
    numero_documento:    str,
    tipo_exame_id:       int,
    usuario_id:          int,
    horario_acionamento: str = None, # HH:MM
    horario_chegada:     str = None, # HH:MM
    horario_saida:       str = None, # HH:MM
    data_documento:      str = None, # YYYY-MM-DD
    solicitante_id:      int = None,
    nome_autoridade:     str = None,
    latitude:            str = None,
    longitude:           str = None,
    status:              str = None,
    observacoes:         str = None,
) -> None:
    """
    Atualiza os dados de uma Requisição de Exame Pericial (REP) existente.

    Args:
        rep_id:              ID da REP a ser atualizada.
        numero_rep:          Novo número da REP.
        data_solicitacao:    Nova data de solicitação.
        tipo_solicitacao:    Novo tipo de documento.
        numero_documento:    Novo número do documento.
        tipo_exame_id:       Novo ID do tipo de exame.
        usuario_id:          Novo ID do perito responsável.
        horario_acionamento: Novo horário de acionamento.
        horario_chegada:     Novo horário de chegada.
        horario_saida:       Novo horário de saída.
        data_documento:      Nova data do documento.
        solicitante_id:      Novo ID do solicitante.
        nome_autoridade:     Novo nome da autoridade.
        latitude:            Nova latitude.
        longitude:           Nova longitude.
        status:              Novo status da REP.
        observacoes:         Novas observações.

    Raises:
        ValueError: Se a REP não existir ou dados forem inválidos.
    """
    numero_rep = numero_rep.strip()
    if not numero_rep:
        raise ValueError("O número da REP é obrigatório.")

    rep_existente = buscar_rep(rep_id)
    if not rep_existente:
        raise ValueError("REP não encontrada.")

    # Verifica duplicidade do número da REP (ignora o próprio registro)
    existe = executar_query(
        "SELECT id FROM rep WHERE LOWER(numero_rep) = LOWER(?) AND id != ?",
        (numero_rep, rep_id)
    )
    if existe:
        raise ValueError(f"Já existe outra REP com o número '{numero_rep}'.")

    # Validações de IDs
    if not buscar_tipo_exame(tipo_exame_id):
        raise ValueError("Tipo de exame não encontrado.")
    if solicitante_id and not buscar_solicitante(solicitante_id):
        raise ValueError("Solicitante não encontrado.")

    sql = """
        UPDATE rep
        SET
            numero_rep = ?, data_solicitacao = ?, horario_acionamento = ?,
            horario_chegada = ?, horario_saida = ?, tipo_solicitacao = ?,
            numero_documento = ?, data_documento = ?, solicitante_id = ?,
            nome_autoridade = ?, tipo_exame_id = ?, latitude = ?, longitude = ?,
            status = ?, observacoes = ?, usuario_id = ?
        WHERE id = ?
    """
    executar_comando(
        sql,
        (
            numero_rep, data_solicitacao, horario_acionamento, horario_chegada,
            horario_saida, tipo_solicitacao, numero_documento, data_documento,
            solicitante_id, nome_autoridade, tipo_exame_id, latitude, longitude,
            status, observacoes, usuario_id, rep_id
        )
    )

def atualizar_rep(
    rep_id:              int,
    numero_rep:          str,
    data_solicitacao:    str, # YYYY-MM-DD
    tipo_solicitacao:    str,
    numero_documento:    str,
    tipo_exame_id:       int,
    usuario_id:          int,
    horario_acionamento: str = None, # HH:MM
    horario_chegada:     str = None, # HH:MM
    horario_saida:       str = None, # HH:MM
    data_documento:      str = None, # YYYY-MM-DD
    solicitante_id:      int = None,
    nome_autoridade:     str = None,
    nome_envolvido:      str = None, # NOVO PARÂMETRO
    local_fato_descricao:str = None, # NOVO PARÂMETRO
    latitude:            str = None,
    longitude:           str = None,
    status:              str = None,
    observacoes:         str = None,
) -> None:
    """
    Atualiza os dados de uma Requisição de Exame Pericial (REP) existente.
    ... (docstring permanece o mesmo, adicione os novos args) ...
    """
    numero_rep = numero_rep.strip()
    if not numero_rep:
        raise ValueError("O número da REP é obrigatório.")

    rep_existente = buscar_rep(rep_id)
    if not rep_existente:
        raise ValueError("REP não encontrada.")

    # Verifica duplicidade do número da REP (ignora o próprio registro)
    existe = executar_query(
        "SELECT id FROM rep WHERE LOWER(numero_rep) = LOWER(?) AND id != ?",
        (numero_rep, rep_id)
    )
    if existe:
        raise ValueError(f"Já existe outra REP com o número '{numero_rep}'.")

    # Validações de IDs (tipo_exame_id pode ser None)
    if tipo_exame_id and not buscar_tipo_exame(tipo_exame_id):
        raise ValueError("Tipo de exame não encontrado.")
    if solicitante_id and not buscar_solicitante(solicitante_id):
        raise ValueError("Solicitante não encontrado.")

    # Se tipo_exame_id for None, reverte status para Pendente (não pode ter laudo sem tipo)
    if tipo_exame_id is None and status != "Pendente":
        status = "Pendente"

    sql = """
        UPDATE rep
        SET
            numero_rep = ?, data_solicitacao = ?, horario_acionamento = ?,
            horario_chegada = ?, horario_saida = ?, tipo_solicitacao = ?,
            numero_documento = ?, data_documento = ?, solicitante_id = ?,
            nome_autoridade = ?, tipo_exame_id = ?,
            nome_envolvido = ?, local_fato_descricao = ?, -- NOVOS CAMPOS AQUI
            latitude = ?, longitude = ?, status = ?, observacoes = ?, usuario_id = ?
        WHERE id = ?
    """
    executar_comando(
        sql,
        (
            numero_rep, data_solicitacao, horario_acionamento, horario_chegada,
            horario_saida, tipo_solicitacao, numero_documento, data_documento,
            solicitante_id, nome_autoridade, tipo_exame_id,
            nome_envolvido, local_fato_descricao,
            latitude, longitude, status, observacoes, usuario_id, rep_id
        )
    )

def verificar_laudo_vinculado(rep_id: int) -> dict | None:
    """
    Verifica se existe um laudo vinculado a esta REP.

    Args:
        rep_id: ID da REP.

    Returns:
        Dicionário com os dados do laudo se existir, ou None.
    """
    from database.db import executar_query
    sql = """
        SELECT id, status, versao_atual, criado_em
        FROM laudos
        WHERE rep_id = ?
    """
    rows = executar_query(sql, (rep_id,))
    if rows:
        return dict(rows[0])
    return None


def excluir_rep(rep_id: int, forcar_exclusao: bool = False) -> str:
    """
    Exclui uma REP pelo ID.

    Args:
        rep_id: ID da REP.
        forcar_exclusao: Se True, exclui mesmo com laudo vinculado (exclui o laudo também).

    Returns:
        Mensagem de confirmação.

    Raises:
        ValueError: Se a REP não existir.
    """
    rep_existente = buscar_rep(rep_id)
    if not rep_existente:
        raise ValueError("REP não encontrada.")

    laudo_vinculado = verificar_laudo_vinculado(rep_id)
    if laudo_vinculado and not forcar_exclusao:
        return "AVISO: Esta REP tem um laudo vinculado que será excluído junto."

    from database.db import executar_comando
    from core.audit import registrar

    try:
        if laudo_vinculado:
            from services.laudo_service import buscar_laudo_por_rep
            from database.db import executar_comando
            executar_comando("DELETE FROM laudos WHERE rep_id = ?", (rep_id,))

        executar_comando(
            "DELETE FROM rep WHERE id = ?",
            (rep_id,)
        )
        registrar(
            tabela="rep",
            registro_id=rep_id,
            operacao="EXCLUIR",
            descricao=f"REP '{rep_existente['numero_rep']}' excluída"
        )

        return "REP excluída com sucesso!"

    except Exception as e:
        raise ValueError(f"Erro ao excluir REP: {e}")


def alterar_status_rep_simples(rep_id: int, novo_status: str) -> None:
    """
    Altera apenas o status da REP (função simples para evitar circular import).

    Args:
        rep_id: ID da REP.
        novo_status: Novo status.
    """
    STATUS_VALIDOS = ["Pendente", "Em Andamento", "Concluído"]
    if novo_status not in STATUS_VALIDOS:
        raise ValueError(f"Status inválido: {novo_status}")

    from database.db import executar_comando
    executar_comando(
        "UPDATE rep SET status = ?, atualizado_em = datetime('now','localtime') WHERE id = ?",
        (novo_status, rep_id)
    )