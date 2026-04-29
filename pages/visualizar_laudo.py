# pages/visualizar_laudo.py
"""
pages/visualizar_laudo.py
────────────────────────────────────────────────────
Página para visualizar Laudos existentes.
────────────────────────────────────────────────────
"""

import sys
import os
import streamlit as st

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu
from core.auth import obter_usuario_logado
from services.laudo_service import (
    listar_laudos,
    listar_secoes_laudo,
    buscar_laudo,
)
from services.rep_service import buscar_rep


st.set_page_config(
    page_title="Visualizar Laudo — LaudoPericial",
    page_icon="👁️",
    layout="wide",
)

st.session_state["_active_page"] = __file__

renderizar_menu()

usuario_logado = obter_usuario_logado()
if not usuario_logado:
    st.error("Usuário não autenticado. Por favor, faça login.")
    st.stop()


def renderizar_laudo(laudo_id: int):
    secoes = listar_secoes_laudo(laudo_id)
    laudo = None
    for l in listar_laudos():
        if l['id'] == laudo_id:
            laudo = l
            break
    
    if not laudo:
        st.error("Laudo não encontrado.")
        return
    
    from services.laudo_service import buscar_laudo
    laudo = buscar_laudo(laudo_id)
    
    if not secoes:
        st.info("Este laudo não possui seções.")
        return

    rep = buscar_rep(laudo['rep_id'])

    st.markdown("---")
    st.markdown(f"### REP {rep['numero_rep']} — {rep.get('tipo_exame_nome') or 'Tipo não definido'}")

    col_st1, col_st2, col_pdf = st.columns([1, 1, 1])
    with col_st1:
        st.markdown(f"**Status do Laudo:** {laudo['status']}")
    with col_st2:
        st.markdown(f"**Status da REP:** {rep['status']}")
    with col_pdf:
        usuario = obter_usuario_logado()
        pasta_exp = usuario.get('pasta_exportacao', '') if usuario else ''
        try:
            if pasta_exp and st.button("Visualizar PDF", use_container_width=True):
                from services.gerador_pdf_playwright import salvar_pdf_laudo
                import webbrowser
                caminho_pdf = salvar_pdf_laudo(laudo_id, pasta_exp)
                webbrowser.open(f'file:///{caminho_pdf}')
                st.success(f"PDF aberto: {caminho_pdf}")
            elif not pasta_exp:
                st.info("Configure a pasta de exportação nas configurações do perfil.")
            else:
                pass
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

    for idx, secao in enumerate(secoes, 1):
        with st.expander(f"{idx} - {secao['titulo'].upper()}", expanded=True):
            if secao['obrigatoria']:
                st.markdown("<small style='color: #e74c3c;'>* Obrigatória</small>", unsafe_allow_html=True)
            
            conteudo = secao['conteudo'] or "<i>Seção vazia</i>"
            st.markdown(conteudo, unsafe_allow_html=True)


def main():
    st.title("👁️ Visualizar Laudo")
    st.markdown("Visualize laudos existentes.")
    st.markdown("---")

    laudos_existentes = listar_laudos(
        usuario_id=usuario_logado['id']
    )

    laudos_disponiveis = [
        l for l in laudos_existentes 
        if l['status'] in ('Em Andamento', 'Finalizado', 'Entregue')
    ]

    if not laudos_disponiveis:
        st.info("Nenhum laudo para visualizar encontrado.")
        st.markdown("---")
        st.markdown("### Como criar um novo laudo?")
        st.page_link("pages/novo_laudo.py", label="Clique aqui para vincular um laudo a uma REP", use_container_width=True)
        st.stop()

    opcoes_laudos = {
        f"{l['numero_rep']} — {l['tipo_exame_nome']} — ({l['status']})": l['id']
        for l in laudos_disponiveis
    }
    nomes_laudos = ["Selecione um Laudo"] + sorted(list(opcoes_laudos.keys()))

    col_sel, _ = st.columns([2, 1])
    with col_sel:
        laudo_selecionado = st.selectbox(
            "Selecione um Laudo para Visualizar",
            options=nomes_laudos,
            key="laudo_selecionado"
        )

    if laudo_selecionado != "Selecione um Laudo":
        laudo_id = opcoes_laudos[laudo_selecionado]
        st.session_state["laudo_id_selecionado"] = laudo_id
        renderizar_laudo(laudo_id)


main()