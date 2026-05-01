# pages/busca.py
"""
pages/busca.py
----------------------------------------
Página de busca unificada do sistema.
Permite buscar por REPs, Laudos, LACRES, Templates e visualizar últimos laudos editados.
----------------------------------------
"""

import sys
import os
import streamlit as st
from datetime import datetime, date
import pandas as pd

# Garante que a raiz do projeto está no sys.path
ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu
from core.auth import obter_usuario_logado
from services.rep_service import listar_reps
from services.laudo_service import listar_laudos
from services.template_service import listar_templates
from services.cadastro_service import listar_tipos_exame
from database.db import executar_query

# ----------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ----------------------------------------
st.set_page_config(
    page_title="Busca — LaudoPericial",
    page_icon="🔍",
    layout="wide",
)

# Defina a página atual na sessão para o menu funcionar corretamente
st.session_state["_active_page"] = __file__

# Renderiza o menu lateral (já exige autenticação)
renderizar_menu()

# ----------------------------------------
# FUNÇÕES AUXILIARES DE BUSCA
# ----------------------------------------

def buscar_por_lacre(lacre: str, tipo_lacre: str = "ambos") -> list:
    """
    Busca REPs por número de lacre (entrada ou saída).

    Args:
        lacre: Número do lacre para busca
        tipo_lacre: "entrada", "saida" ou "ambos"

    Returns:
        Lista de REPs que correspondem ao critério
    """
    sql = """
        SELECT
            r.id,
            r.numero_rep,
            r.data_solicitacao,
            r.nome_envolvido,
            r.local_fato_descricao,
            r.lacre_entrada,
            r.lacre_saida,
            r.status,
            s.orgao AS solicitante_orgao,
            te.nome AS tipo_exame_nome
        FROM rep r
        LEFT JOIN solicitantes s ON r.solicitante_id = s.id
        LEFT JOIN tipos_exame te ON r.tipo_exame_id = te.id
        WHERE
    """
    params = []
    conditions = []

    if tipo_lacre == "entrada" or tipo_lacre == "ambos":
        conditions.append("LOWER(r.lacre_entrada) LIKE LOWER(?)")
        params.append(f"%{lacre}%")

    if tipo_lacre == "saida" or tipo_lacre == "ambos":
        if tipo_lacre == "ambos" and len(conditions) > 0:
            conditions[-1] = conditions[-1] + " OR LOWER(r.lacre_saida) LIKE LOWER(?)"
            params.append(f"%{lacre}%")
        else:
            conditions.append("LOWER(r.lacre_saida) LIKE LOWER(?)")
            params.append(f"%{lacre}%")

    if conditions:
        sql += "(" + " OR ".join(conditions) + ")"
    else:
        return []

    sql += " ORDER BY r.data_solicitacao DESC"
    rows = executar_query(sql, tuple(params))
    return [dict(row) for row in rows]

def buscar_rep_por_numero(numero_rep: str):
    """
    Busca uma REP pelo número (retorna o ID).

    Args:
        numero_rep: Número da REP

    Returns:
        ID da REP ou None se não encontrada
    """
    sql = "SELECT id FROM rep WHERE LOWER(numero_rep) = LOWER(?)"
    rows = executar_query(sql, (numero_rep,))
    if rows:
        return rows[0]['id']
    return None

def buscar_ultimos_laudos_editados(limite: int = 25) -> list:
    """
    Busca os últimos laudos editados ordenados por data de atualização.

    Args:
        limite: Número máximo de laudos a retornar

    Returns:
        Lista de laudos com informações da REP associada
    """
    sql = """
        SELECT
            l.id AS laudo_id,
            l.rep_id,
            l.status AS laudo_status,
            l.atualizado_em,
            l.versao_atual,
            r.numero_rep,
            r.nome_envolvido,
            r.local_fato_descricao,
            r.status AS rep_status,
            te.nome AS tipo_exame_nome
        FROM laudos l
        JOIN rep r ON l.rep_id = r.id
        LEFT JOIN tipos_exame te ON r.tipo_exame_id = te.id
        ORDER BY l.atualizado_em DESC
        LIMIT ?
    """
    rows = executar_query(sql, (limite,))
    return [dict(row) for row in rows]

# ----------------------------------------
# FUNÇÕES DE RENDERIZAÇÃO DAS ABAS
# ----------------------------------------

def renderizar_busca_rep(usuario):
    """Interface de busca por REPs."""
    st.subheader("🔍 Busca por REP")

    with st.expander("Filtros de Busca", expanded=True):
        col1, col2 = st.columns([2, 1])

        busca_rapida = col1.text_input("Busca rápida (Número REP, Envolvido, Local)")

        status_opcoes = ["Todos", "Pendente", "Em Andamento", "Concluido"]
        filtro_status = col2.selectbox("Status", status_opcoes)

        col_d1, col_d2 = st.columns(2)
        data_inicio = col_d1.date_input("Data Início", value=None, format="DD/MM/YYYY")
        data_fim = col_d2.date_input("Data Fim", value=None, format="DD/MM/YYYY")

        # Opção para incluir apenas REPs ativas
        apenas_ativas = st.checkbox("Apenas REPs ativas (Pendente/Em Andamento)", value=False)

    if st.button("Buscar REPs", type="primary", key="buscar_reps"):
        # Usar função existente de listar_reps do serviço
        reps = listar_reps(
            apenas_ativas=apenas_ativas,
            usuario_id=usuario['id'],
            status=filtro_status if filtro_status != "Todos" else None,
            numero_rep=busca_rapida if busca_rapida else None,
            data_inicio=data_inicio.isoformat() if data_inicio else None,
            data_fim=data_fim.isoformat() if data_fim else None
        )

        if reps:
            # Exibir como cards visuais
            st.info(f"📊 Total de {len(reps)} REP(s) encontrada(s).")

            # Agrupar por status para organização
            status_groups = {}
            for rep in reps:
                status = rep.get('status', 'Sem Status')
                if status not in status_groups:
                    status_groups[status] = []
                status_groups[status].append(rep)

            for status, rep_list in status_groups.items():
                st.markdown(f"### {status} ({len(rep_list)})")

                # Criar colunas para cards (3 por linha)
                cols = st.columns(3)
                for idx, rep in enumerate(rep_list):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        with st.container(border=True):
                            st.markdown(f"**Nº REP:** {rep.get('numero_rep', 'N/A')}")
                            st.markdown(f"**Envolvido:** {rep.get('nome_envolvido', 'N/A')}")
                            st.markdown(f"**Local:** {rep.get('local_fato_descricao', 'N/A')[:50]}...")
                            st.markdown(f"**Data:** {rep.get('data_solicitacao', 'N/A')}")
                            st.markdown(f"**Solicitante:** {rep.get('solicitante_orgao', 'N/A')}")

                            # Botão para ver detalhes (navegação para REP)
                            if st.button(f"Ver Detalhes", key=f"rep_{rep['id']}", type="secondary"):
                                st.session_state['rep_id'] = rep['id']
                                st.switch_page("pages/editar_rep.py")
        else:
            st.info("Nenhuma REP encontrada com os filtros aplicados.")

def renderizar_busca_laudo(usuario):
    """Interface de busca por Laudos."""
    st.subheader("📄 Busca por Laudo")

    with st.expander("Filtros de Busca", expanded=True):
        col1, col2 = st.columns([2, 1])

        busca_numero_rep = col1.text_input("Número da REP")

        status_opcoes = ["Todos", "Pendente", "Em Andamento", "Concluido", "Entregue"]
        filtro_status = col2.selectbox("Status do Laudo", status_opcoes)

    if st.button("Buscar Laudos", type="primary", key="buscar_laudos"):
        # Buscar ID da REP se número foi fornecido
        rep_id_filtro = None
        if busca_numero_rep:
            rep_id_filtro = buscar_rep_por_numero(busca_numero_rep)
            if not rep_id_filtro:
                st.warning(f"Nenhuma REP encontrada com o número '{busca_numero_rep}'.")
                return

        # Usar função existente de listar_laudos
        laudos = listar_laudos(
            status=filtro_status if filtro_status != "Todos" else None,
            usuario_id=usuario['id'],
            rep_id=rep_id_filtro
        )

        if laudos:
            st.info(f"📄 Total de {len(laudos)} laudo(s) encontrado(s).")

            # Exibir como cards
            cols = st.columns(3)
            for idx, laudo in enumerate(laudos):
                col_idx = idx % 3
                with cols[col_idx]:
                    with st.container(border=True):
                        st.markdown(f"**REP Nº:** {laudo.get('numero_rep', 'N/A')}")
                        st.markdown(f"**Status Laudo:** {laudo.get('status', 'N/A')}")
                        st.markdown(f"**Tipo de Exame:** {laudo.get('tipo_exame_nome', 'N/A')}")
                        st.markdown(f"**Versão:** {laudo.get('versao_atual', 'N/A')}")

                        if 'atualizado_em' in laudo and laudo['atualizado_em']:
                            data_formatada = datetime.fromisoformat(laudo['atualizado_em']).strftime('%d/%m/%Y %H:%M')
                            st.markdown(f"**Última atualização:** {data_formatada}")

                        # Botão para editar laudo (navegação para editor)
                        if st.button(f"Abrir Laudo", key=f"laudo_{laudo['id']}", type="secondary"):
                            st.session_state['laudo_id'] = laudo['id']
                            st.switch_page("pages/editor_laudo.py")
        else:
            st.info("Nenhum laudo encontrado com os filtros aplicados.")

def renderizar_busca_lacre():
    """Interface de busca por número de LACRE."""
    st.subheader("🏷️ Busca por LACRE")

    with st.expander("Busca por LACRE", expanded=True):
        lacre = st.text_input("Número do LACRE")

        tipo_opcoes = ["Ambos (Entrada ou Saída)", "Entrada", "Saída"]
        tipo_lacre = st.radio("Tipo de LACRE", tipo_opcoes, horizontal=True)

        tipo_map = {
            "Ambos (Entrada ou Saída)": "ambos",
            "Entrada": "entrada",
            "Saída": "saida"
        }

    if st.button("Buscar por LACRE", type="primary", key="buscar_lacre"):
        if lacre:
            reps = buscar_por_lacre(lacre, tipo_map[tipo_lacre])

            if reps:
                st.info(f"🏷️ Total de {len(reps)} REP(s) encontrada(s) com LACRE contendo '{lacre}'.")

                # Exibir como cards com informação mínima
                cols = st.columns(3)
                for idx, rep in enumerate(reps):
                    col_idx = idx % 3
                    with cols[col_idx]:
                        with st.container(border=True):
                            st.markdown(f"**Nº REP:** {rep.get('numero_rep', 'N/A')}")
                            st.markdown(f"**Envolvido:** {rep.get('nome_envolvido', 'N/A')}")
                            st.markdown(f"**Data:** {rep.get('data_solicitacao', 'N/A')}")

                            # Mostrar qual lacre foi encontrado
                            lacre_encontrado = "Desconhecido"
                            if rep.get('lacre_entrada') and lacre.lower() in rep['lacre_entrada'].lower():
                                lacre_encontrado = "Entrada"
                            elif rep.get('lacre_saida') and lacre.lower() in rep['lacre_saida'].lower():
                                lacre_encontrado = "Saída"

                            st.markdown(f"**LACRE {lacre_encontrado}:** {lacre}")

                            # Botão para ver detalhes da REP
                            if st.button(f"Ver REP", key=f"lacre_rep_{rep['id']}", type="secondary"):
                                st.session_state['rep_id'] = rep['id']
                                st.switch_page("pages/editar_rep.py")
            else:
                st.info(f"Nenhuma REP encontrada com LACRE contendo '{lacre}'.")
        else:
            st.warning("Por favor, informe um número de LACRE para buscar.")

def renderizar_ultimos_laudos():
    """Exibe os últimos laudos editados."""
    st.subheader("📝 Últimos Laudos Editados")
    st.markdown("Lista dos laudos mais recentemente atualizados.")

    limite = st.slider("Quantidade de laudos a exibir", 10, 100, 25)

    laudos = buscar_ultimos_laudos_editados(limite)

    if laudos:
        st.info(f"📝 Exibindo os {len(laudos)} últimos laudos editados.")

        # Exibir como cards organizados por data
        for laudo in laudos:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    st.markdown(f"**REP Nº:** {laudo.get('numero_rep', 'N/A')}")
                    st.markdown(f"**Envolvido:** {laudo.get('nome_envolvido', 'N/A')}")

                with col2:
                    st.markdown(f"**Local:** {laudo.get('local_fato_descricao', 'N/A')[:80]}...")
                    st.markdown(f"**Tipo de Exame:** {laudo.get('tipo_exame_nome', 'N/A')}")

                with col3:
                    if 'atualizado_em' in laudo and laudo['atualizado_em']:
                        try:
                            data_formatada = datetime.fromisoformat(laudo['atualizado_em']).strftime('%d/%m/%Y %H:%M')
                            st.markdown(f"**Atualizado:** {data_formatada}")
                        except:
                            st.markdown(f"**Atualizado:** {laudo['atualizado_em']}")

                    st.markdown(f"**Status:** {laudo.get('laudo_status', 'N/A')}")

                # Botões de ação
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(f"Abrir Laudo", key=f"ultimo_laudo_{laudo['laudo_id']}"):
                        st.session_state['laudo_id'] = laudo['laudo_id']
                        st.switch_page("pages/editor_laudo.py")
                with col_btn2:
                    if st.button(f"Ver REP", key=f"ultimo_rep_{laudo['rep_id']}"):
                        st.session_state['rep_id'] = laudo['rep_id']
                        st.switch_page("pages/editar_rep.py")
    else:
        st.info("Nenhum laudo encontrado.")

def renderizar_busca_template():
    """Interface de busca por Templates."""
    st.subheader("📋 Busca por Template")

    with st.expander("Filtros de Busca", expanded=True):
        busca_nome = st.text_input("Nome do Template")

        # Obter tipos de exame para filtro
        tipos_exame = listar_tipos_exame()
        tipos_opcoes = [("Todos", None)] + [(te['nome'], te['id']) for te in tipos_exame]

        tipo_selecionado_nome = st.selectbox(
            "Tipo de Exame",
            [opt[0] for opt in tipos_opcoes]
        )

        # Mapear nome para ID
        tipo_exame_id = None
        for nome, id_val in tipos_opcoes:
            if nome == tipo_selecionado_nome:
                tipo_exame_id = id_val
                break

        apenas_ativos = st.checkbox("Apenas templates ativos", value=True)

    if st.button("Buscar Templates", type="primary", key="buscar_templates"):
        templates = listar_templates(
            apenas_ativos=apenas_ativos,
            tipo_exame_id=tipo_exame_id
        )

        # Filtrar por nome se especificado
        if busca_nome:
            templates = [t for t in templates if busca_nome.lower() in t['nome'].lower()]

        if templates:
            st.info(f"📋 Total de {len(templates)} template(s) encontrado(s).")

            # Exibir como cards
            cols = st.columns(3)
            for idx, template in enumerate(templates):
                col_idx = idx % 3
                with cols[col_idx]:
                    with st.container(border=True):
                        st.markdown(f"**Nome:** {template.get('nome', 'N/A')}")
                        st.markdown(f"**Tipo de Exame:** {template.get('tipo_exame_nome', 'N/A')}")
                        st.markdown(f"**Status:** {'✅ Ativo' if template.get('ativo') else '❌ Inativo'}")

                        if 'descricao_exame' in template and template['descricao_exame']:
                            descricao = template['descricao_exame'][:100] + "..." if len(template['descricao_exame']) > 100 else template['descricao_exame']
                            st.markdown(f"**Descrição:** {descricao}")

                        # Para templates, apenas visualização (sem navegação para edição por padrão)
                        # Mas pode adicionar botão se necessário
                        # if st.button("Ver Template", key=f"template_{template['id']}", type="secondary"):
                        #     st.session_state['template_id'] = template['id']
                        #     st.switch_page("pages/gerenciar_templates.py")
        else:
            st.info("Nenhum template encontrado com os filtros aplicados.")

# ----------------------------------------
# FUNÇÃO PRINCIPAL
# ----------------------------------------

def main():
    usuario = obter_usuario_logado()
    if not usuario:
        st.error("Usuário não logado.")
        st.stop()

    st.title("🔍 Busca Unificada")
    st.markdown("Busque por diferentes tipos de registros no sistema.")
    st.divider()

    # Abas principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Busca por REP",
        "📄 Busca por Laudo",
        "🏷️ Busca por LACRE",
        "📝 Últimos Laudos Editados",
        "📋 Busca por Template"
    ])

    with tab1:
        renderizar_busca_rep(usuario)

    with tab2:
        renderizar_busca_laudo(usuario)

    with tab3:
        renderizar_busca_lacre()

    with tab4:
        renderizar_ultimos_laudos()

    with tab5:
        renderizar_busca_template()

if __name__ == "__main__":
    main()