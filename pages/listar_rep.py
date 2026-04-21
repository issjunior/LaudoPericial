# pages/listar_rep.py
"""
pages/listar_rep.py
──────────────────────────────────────────────────────
Página para listar todas as Requisições de Exame Pericial (REPs).
Permite visualizar, buscar e filtrar as REPs.
──────────────────────────────────────────────────────
"""
import streamlit as st
from database.db import executar_query, executar_comando
from core.auth import obter_usuario_logado
from components.menu import renderizar_menu
from datetime import date
from pandas import DataFrame

# ──────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Listar REPs — LaudoPericial",
    page_icon="📄",
    layout="wide",
)

# ──────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ──────────────────────────────────────────────────────

def buscar_reps(
    filtro_numero_rep: str = None,
    filtro_orgao_solicitante: str = None,
    filtro_tipo_exame_id: int = None,
    filtro_status: str = None,
    filtro_data_inicio: date = None,
    filtro_data_fim: date = None
):
    """
    Busca Requisições de Exame Pericial (REPs) no banco de dados com filtros.
    Converte os resultados de sqlite3.Row para dicionários.
    """
    query = """
        SELECT
            r.id,
            r.numero_rep,
            r.data_solicitacao,
            r.tipo_solicitacao,
            r.numero_documento,
            s.orgao AS orgao_solicitante,
            COALESCE(te.codigo || ' - ' || te.nome, 'Não definido') AS tipo_exame_nome,
            r.status,
            SUBSTR(u.nome, 1, INSTR(u.nome || ' ', ' ') - 1) AS perito_primeiro_nome
        FROM
            rep r
        LEFT JOIN
            solicitantes s ON r.solicitante_id = s.id
        LEFT JOIN
            tipos_exame te ON r.tipo_exame_id = te.id
        LEFT JOIN
            usuarios u ON r.usuario_id = u.id
        WHERE 1=1
    """
    params = []

    if filtro_numero_rep:
        query += " AND r.numero_rep LIKE ?"
        params.append(f"%{filtro_numero_rep}%")

    if filtro_orgao_solicitante:
        query += " AND s.orgao = ?"
        params.append(filtro_orgao_solicitante)

    if filtro_tipo_exame_id:
        query += " AND r.tipo_exame_id = ?"
        params.append(filtro_tipo_exame_id)

    if filtro_status:
        query += " AND r.status = ?"
        params.append(filtro_status)

    if filtro_data_inicio:
        query += " AND r.data_solicitacao >= ?"
        params.append(filtro_data_inicio.isoformat())

    if filtro_data_fim:
        query += " AND r.data_solicitacao <= ?"
        params.append(filtro_data_fim.isoformat())

    query += " ORDER BY r.data_solicitacao DESC, r.numero_rep DESC"

    reps_raw = executar_query(query, tuple(params))
    reps = [dict(row) for row in reps_raw]
    return reps


def alterar_status_rep(rep_id: int, novo_status: str) -> None:
    """
    Altera o status de uma REP.

    Args:
        rep_id: ID da REP.
        novo_status: Novo status (Pendente, Em Andamento, Concluído).

    Raises:
        ValueError: Se o status for inválido.
    """
    STATUS_VALIDOS = ["Pendente", "Em Andamento", "Concluído"]
    if novo_status not in STATUS_VALIDOS:
        raise ValueError(f"Status inválido: {novo_status}")

    executar_comando(
        "UPDATE rep SET status = ?, atualizado_em = datetime('now','localtime') WHERE id = ?",
        (novo_status, rep_id)
    )

def obter_tipos_exame():
    """
    Retorna uma lista de dicionários com id, nome e codigo dos tipos de exame.
    """
    return executar_query("SELECT id, codigo, nome FROM tipos_exame ORDER BY nome")

def obter_orgaos_solicitantes():
    """Retorna uma lista de nomes de órgãos solicitantes únicos do banco de dados."""
    orgaos_raw = executar_query("SELECT DISTINCT orgao FROM solicitantes WHERE orgao IS NOT NULL AND orgao != '' ORDER BY orgao")
    return [row["orgao"] for row in orgaos_raw]

# ──────────────────────────────────────────────────────
# RENDERIZAÇÃO DA PÁGINA
# ──────────────────────────────────────────────────────

def main():
    renderizar_menu()

    usuario = obter_usuario_logado()
    if not usuario:
        st.stop()

    st.title("📄 Listar Requisições de Exame Pericial (REPs)")
    st.markdown("---")

    # ----------------------------------------------------
    # FILTROS
    # ----------------------------------------------------
    st.subheader("Filtros de Busca")
    with st.expander("Expandir/Recolher Filtros", expanded=False):
        # Primeira linha de filtros
        col1_a, col1_b, col1_c = st.columns(3)
        with col1_a:
            filtro_numero_rep = st.text_input("Número da REP", placeholder="Ex: REP-2024-001")
        with col1_b:
            orgaos_solicitantes = obter_orgaos_solicitantes()
            orgaos_solicitantes_opcoes = ["Todos"] + orgaos_solicitantes
            filtro_orgao_solicitante = st.selectbox("Órgão Solicitante", orgaos_solicitantes_opcoes)
            if filtro_orgao_solicitante == "Todos":
                filtro_orgao_solicitante = None
        with col1_c:
            tipos_exame = obter_tipos_exame()
            tipo_exame_opcoes_display = ["Todos"] + [f"{te['codigo']} - {te['nome']}" for te in tipos_exame]
            tipo_exame_selecionado_display = st.selectbox("Tipo de Exame", tipo_exame_opcoes_display)

            filtro_tipo_exame_id = None
            if tipo_exame_selecionado_display != "Todos":
                for te in tipos_exame:
                    if f"{te['codigo']} - {te['nome']}" == tipo_exame_selecionado_display:
                        filtro_tipo_exame_id = te["id"]
                        break

        # Segunda linha de filtros (Status e Data da Solicitação)
        col2_a, col2_b = st.columns([1, 2]) # Proporção para a data ocupar mais espaço
        with col2_a:
            status_opcoes = ["Todos", "Pendente", "Em Andamento", "Concluído"]
            filtro_status = st.selectbox("Status", status_opcoes)
            if filtro_status == "Todos":
                filtro_status = None
        with col2_b:
            with st.container(border=True):
                st.markdown("Data da Solicitação")
                col_data_inicio, col_data_fim = st.columns(2)
                with col_data_inicio:
                    filtro_data_inicio = st.date_input("De", value=None, format="DD/MM/YYYY", key="data_inicio_filtro", label_visibility="collapsed")
                with col_data_fim:
                    filtro_data_fim = st.date_input("Até", value=None, format="DD/MM/YYYY", key="data_fim_filtro", label_visibility="collapsed")

        st.markdown("---")
        if st.button("Limpar Filtros", key="limpar_filtros_btn", on_click=lambda: st.rerun()):
            pass

    st.markdown("---")

    reps = buscar_reps(
        filtro_numero_rep=filtro_numero_rep,
        filtro_orgao_solicitante=filtro_orgao_solicitante,
        filtro_tipo_exame_id=filtro_tipo_exame_id,
        filtro_status=filtro_status,
        filtro_data_inicio=filtro_data_inicio,
        filtro_data_fim=filtro_data_fim
    )

    if reps:
        col_leg1, col_leg2, col_leg3, col_leg4 = st.columns(4)
        with col_leg1:
            with st.container(border=True):
                st.markdown("**🟡 Pendente**")
                st.caption("REP criada, mas não vinculada.")
        with col_leg2:
            with st.container(border=True):
                st.markdown("**🔵 Em Andamento**")
                st.caption("Laudo está sendo elaborado.")
        with col_leg3:
            with st.container(border=True):
                st.markdown("**🟢 Concluído**")
                st.caption("Laudo finalizedo, pronto para entrega.")
        with col_leg4:
            with st.container(border=True):
                st.markdown("**✅ Entregue**")
                st.caption("Laudo enviado (GDL).")

        st.dataframe(
            reps,
            use_container_width=True,
            hide_index=True,
            column_order=[
                "numero_rep",
                "data_solicitacao",
                "tipo_solicitacao",
                "numero_documento",
                "orgao_solicitante",
                "tipo_exame_nome",
                "status"
            ],
            column_config={
                "numero_rep": st.column_config.TextColumn("Número da REP"),
                "data_solicitacao": st.column_config.DateColumn("Data da Solicitação", format="DD/MM/YYYY"),
                "tipo_solicitacao": st.column_config.TextColumn("Tipo de Documento"),
                "numero_documento": st.column_config.TextColumn("Número do Documento"),
                "orgao_solicitante": st.column_config.TextColumn("Órgão Solicitante"),
                "tipo_exame_nome": st.column_config.TextColumn("Tipo de Exame"),
                "status": st.column_config.TextColumn("Status"),
            }
        )
    else:
        st.info("Nenhuma Requisição de Exame Pericial (REP) encontrada com os filtros aplicados.")
        st.markdown("---")
        st.button("➕ Criar Nova REP", on_click=lambda: st.switch_page("pages/nova_rep.py"))


if __name__ == "__main__":
    main()