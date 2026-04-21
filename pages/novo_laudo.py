# pages/novo_laudo.py
"""
pages/novo_laudo.py
─────────────────────────────────────────────────────
Página para criar novo Laudo vinculando a uma REP.
─────────────────────────────────────────────────────
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
from services.rep_service import listar_reps
from services.template_service import listar_templates
from services.laudo_service import (
    criar_laudo,
    verificar_laudo_existe
)

st.set_page_config(
    page_title="Vincular Laudo a REP — LaudoPericial",
    page_icon="✏️",
    layout="wide",
)

# Define a página atual na sessão para o menu funcionar corretamente
st.session_state["_active_page"] = __file__

renderizar_menu()

usuario_logado = obter_usuario_logado()
if not usuario_logado:
    st.error("Usuário não autenticado. Por favor, faça login.")
    st.stop()


def main():
    st.title("➕ Vincular Laudo a REP")
    st.markdown("Vincular um modelo de laudo a uma REP existente.")
    st.markdown("---")

    reps_pendentes = listar_reps(
        status='Pendente',
        usuario_id=usuario_logado['id']
    )
    reps_andamento = listar_reps(
        status='Em Andamento',
        usuario_id=usuario_logado['id']
    )

    reps = reps_pendentes + reps_andamento

    reps_disponiveis = []
    for rep in reps:
        if not verificar_laudo_existe(rep['id']):
            reps_disponiveis.append(rep)

    if not reps_disponiveis:
        st.warning("⚠️ Não há REPs disponíveis para criar laudo.")
        st.info("Somente REPs Pendentes ou Em Andamento sem laudo vinculado são listadas.")
        st.markdown("---")
        st.markdown("### Como criar uma REP?")
        st.page_link("pages/nova_rep.py", label="Clique aqui para criar uma nova REP", use_container_width=True)
        st.stop()

    opcoes_reps = {
        f"{rep['numero_rep']} — {rep.get('tipo_exame_nome') or 'Tipo não definido'} — ({rep['status']})": rep['id']
        for rep in reps_disponiveis
    }
    if opcoes_reps:
        nomes_reps = ["Selecione uma REP"] + sorted(list(opcoes_reps.keys()))
    else:
        nomes_reps = []

    templates = listar_templates(apenas_ativos=True)

    if not templates:
        st.warning("⚠️ Não há templates de laudo cadastrados.")
        st.info("Cadastre um template antes de criar laudos.")
        st.markdown("---")
        st.markdown("### Como criar um template?")
        st.page_link("pages/gerenciar_templates.py", label="Clique aqui para gerenciar templates", use_container_width=True)
        st.stop()

    opcoes_templates = {
        f"{t['tipo_exame_codigo']} — {t['nome']}": t['id']
        for t in templates
    }
    nomes_templates = ["Selecione um Template"] + list(opcoes_templates.keys())

    with st.form("form_novo_laudo", clear_on_submit=True):
        st.markdown("### Seleções")

        rep_selecionado = st.selectbox(
            "REP *",
            options=nomes_reps,
            index=0,
            help="Selecione a Requisição de Exame Pericial para a qual deseja criar o laudo."
        )

        template_selecionado = st.selectbox(
            "Template de Laudo *",
            options=nomes_templates,
            index=0,
            help="Selecione o modelo de laudo que será usado."
        )

        st.markdown("---")
        submitted = st.form_submit_button(
            "➕ Criar Laudo",
            type="primary"
        )

        if submitted:
            if rep_selecionado == "Selecione uma REP":
                st.error("❌ Por favor, selecione uma REP.")
                st.stop()
            if template_selecionado == "Selecione um Template":
                st.error("❌ Por favor, selecione um Template de Laudo.")
                st.stop()

            rep_id = opcoes_reps[rep_selecionado]
            template_id = opcoes_templates[template_selecionado]

            try:
                laudo_id = criar_laudo(rep_id, template_id)
                st.success(f"✅ Laudo criado com sucesso! ID: {laudo_id}")
                st.balloons()
                st.markdown("---")
                st.markdown("### Próximos passos")
                st.info("O laudo foi criado. Para editá-lo, vá até a página Editor de Laudo.")

            except ValueError as e:
                st.error(f"❌ Erro ao criar laudo: {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")


main()