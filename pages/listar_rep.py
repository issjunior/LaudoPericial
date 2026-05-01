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
    filtro_busca: str = None,
    filtro_status: str = None,
    filtro_data_inicio: date = None,
    filtro_data_fim: date = None,
    usuario_id: int = None
):
    """
    Busca Requisições de Exame Pericial (REPs) no banco de dados com filtros.
    """
    query = """
        SELECT
            r.id,
            r.numero_rep,
            r.data_solicitacao,
            r.tipo_solicitacao,
            r.numero_documento,
            s.orgao AS orgao_solicitante,
            r.nome_envolvido,
            r.local_fato_descricao,
            COALESCE(te.codigo || ' - ' || te.nome, 'Não definido') AS tipo_exame_nome,
            r.status
        FROM
            rep r
        LEFT JOIN
            solicitantes s ON r.solicitante_id = s.id
        LEFT JOIN
            tipos_exame te ON r.tipo_exame_id = te.id
        WHERE
            r.usuario_id = ?
    """
    params = [usuario_id]

    if filtro_busca:
        query += " AND (r.numero_rep LIKE ? OR r.nome_envolvido LIKE ? OR r.local_fato_descricao LIKE ?)"
        term = f"%{filtro_busca}%"
        params.extend([term, term, term])

    if filtro_status and filtro_status != "Todos":
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
    return [dict(row) for row in reps_raw]


def main():
    renderizar_menu()
    
    usuario = obter_usuario_logado()
    if not usuario:
        st.error("Usuário não logado.")
        st.stop()

    st.header("📋 Requisições de Exame (REP)")

    # 1. Filtros
    with st.expander("🔍 Filtros", expanded=True):
        col1, col2 = st.columns([2, 1])
        busca = col1.text_input("Busca rápida (Número, Envolvido, Local)")
        status_opcoes = ["Todos", "Pendente", "Em Andamento", "Concluído"]
        filtro_status = col2.selectbox("Status", status_opcoes)
        # Internamente usa sem acento se o filtro for ativado
        filtro_status_interno = filtro_status.replace('Concluído', 'Concluido')

        col_d1, col_d2, col_d3 = st.columns(3)
        data_inicio = col_d1.date_input("Data Início", value=None, format="DD/MM/YYYY")
        data_fim = col_d2.date_input("Data Fim", value=None, format="DD/MM/YYYY")
        
        if st.button("Limpar Filtros"):
            st.rerun()

    # 2. Busca de dados
    reps = buscar_reps(
        filtro_busca=busca,
        filtro_status=filtro_status_interno,
        filtro_data_inicio=data_inicio,
        filtro_data_fim=data_fim,
        usuario_id=usuario['id']
    )

    # 3. Exibição
    if reps:
        # Legendas
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        col_leg1.info("🟡 **Pendente**: REP aguardando início.")
        col_leg2.warning("🔵 **Em Andamento**: Laudo em elaboração.")
        col_leg3.success("🟢 **Concluído**: Laudo finalizado.")

        # Converte status para exibição com acento no DataFrame
        for r in reps:
            if r['status'] == 'Concluido':
                r['status'] = 'Concluído'

        df = DataFrame(reps)
        
        # Ajusta a exibição do status para o usuário (com acento se preferir, mas o valor interno é sem)
        # Para simplificar mantemos como vem do banco
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_order=[
                "numero_rep",
                "data_solicitacao",
                "tipo_solicitacao",
                "numero_documento",
                "orgao_solicitante",
                "nome_envolvido",
                "tipo_exame_nome",
                "status"
            ],
            column_config={
                "numero_rep": st.column_config.TextColumn("REP"),
                "data_solicitacao": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "tipo_solicitacao": st.column_config.TextColumn("Doc."),
                "numero_documento": st.column_config.TextColumn("Nº Doc."),
                "orgao_solicitante": st.column_config.TextColumn("Solicitante"),
                "nome_envolvido": st.column_config.TextColumn("Envolvido"),
                "tipo_exame_nome": st.column_config.TextColumn("Tipo de Exame"),
                "status": st.column_config.TextColumn("Status"),
            }
        )
        
        st.info(f"Total de {len(reps)} requisições encontradas.")
    else:
        st.info("Nenhuma REP encontrada com os filtros aplicados.")
        if st.button("➕ Criar Nova REP"):
            st.switch_page("pages/nova_rep.py")

if __name__ == "__main__":
    main()
