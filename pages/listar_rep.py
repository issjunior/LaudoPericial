# pages/listar_rep.py
"""
pages/listar_rep.py
──────────────────────────────────────────────────────
Página para listar todas as Requisições de Exame Pericial (REPs).
Permite visualizar, buscar e filtrar as REPs.
──────────────────────────────────────────────────────
"""
import streamlit as st
from database.db import executar_query
from core.auth import obter_usuario_logado
from components.menu import renderizar_menu
from datetime import date

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
            te.nome AS tipo_exame_nome,
            r.status,
            u.nome AS usuario_responsavel
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

def obter_tipos_exame():
    """
    Retorna uma lista de dicionários com id, nome e codigo dos tipos de exame.
    """
    return executar_query("SELECT id, codigo, nome FROM tipos_exame ORDER BY nome") # <--- ADICIONADO 'codigo'

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
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_numero_rep = st.text_input("Número da REP", placeholder="Ex: REP-2024-001")

            tipos_exame = obter_tipos_exame()
            # Prepara as opções para o selectbox no formato "CÓDIGO - Nome do Exame"
            tipo_exame_opcoes_display = ["Todos"] + [f"{te['codigo']} - {te['nome']}" for te in tipos_exame]
            tipo_exame_selecionado_display = st.selectbox("Tipo de Exame", tipo_exame_opcoes_display)

            filtro_tipo_exame_id = None
            if tipo_exame_selecionado_display != "Todos":
                # Encontra o ID do tipo de exame selecionado
                for te in tipos_exame:
                    if f"{te['codigo']} - {te['nome']}" == tipo_exame_selecionado_display:
                        filtro_tipo_exame_id = te["id"]
                        break

        with col2:
            orgaos_solicitantes = obter_orgaos_solicitantes()
            orgaos_solicitantes_opcoes = ["Todos"] + orgaos_solicitantes
            filtro_orgao_solicitante = st.selectbox("Órgão Solicitante", orgaos_solicitantes_opcoes)
            if filtro_orgao_solicitante == "Todos":
                filtro_orgao_solicitante = None

            status_opcoes = ["Todos", "Pendente", "Em Andamento", "Concluído", "Arquivado", "Cancelado"]
            filtro_status = st.selectbox("Status", status_opcoes)
            if filtro_status == "Todos":
                filtro_status = None

        with col3:
            st.markdown("Data da Solicitação")
            col_data_inicio, col_data_fim = st.columns(2)
            with col_data_inicio:
                filtro_data_inicio = st.date_input("De", value=None, format="DD/MM/YYYY")
            with col_data_fim:
                filtro_data_fim = st.date_input("Até", value=None, format="DD/MM/YYYY")

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
        st.dataframe(
            reps,
            use_container_width=True,
            hide_index=True,
            column_order=[
                "numero_rep",
                "data_solicitacao",
                "tipo_solicitacao",
                "orgao_solicitante",
                "tipo_exame_nome",
                "numero_documento",
                "usuario_responsavel",
                "status"
            ],
            column_config={
                "numero_rep": st.column_config.TextColumn("Número da REP"),
                "data_solicitacao": st.column_config.DateColumn("Data da Solicitação", format="DD/MM/YYYY"),
                "tipo_solicitacao": st.column_config.TextColumn("Tipo de Solicitação"),
                "orgao_solicitante": st.column_config.TextColumn("Órgão Solicitante"),
                "tipo_exame_nome": st.column_config.TextColumn("Tipo de Exame"),
                "numero_documento": st.column_config.TextColumn("Número do Documento"),
                "status": st.column_config.TextColumn("Status"),
                "usuario_responsavel": st.column_config.TextColumn("Responsável"),
            }
        )
    else:
        st.info("Nenhuma Requisição de Exame Pericial (REP) encontrada com os filtros aplicados.")
        st.markdown("---")
        st.button("➕ Criar Nova REP", on_click=lambda: st.switch_page("pages/nova_rep.py"))


if __name__ == "__main__":
    main()