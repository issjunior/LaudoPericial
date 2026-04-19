# pages/editor_laudo.py
"""
pages/editor_laudo.py
─────────────────────────────────────────────────────
Página para editar Laudos existentes.
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
from services.laudo_service import (
    listar_laudos,
    buscar_laudo,
    listar_secoes_laudo,
    atualizar_secao_laudo
)

try:
    from streamlit_quill import st_quill
except ImportError:
    st_quill = None

st.set_page_config(
    page_title="Editar Laudo — LaudoPericial",
    page_icon="✏️",
    layout="wide",
)

renderizar_menu()

usuario_logado = obter_usuario_logado()
if not usuario_logado:
    st.error("Usuário não autenticado. Por favor, faça login.")
    st.stop()


def renderizar_secoes(laudo_id: int):
    secoes = listar_secoes_laudo(laudo_id)
    laudo = buscar_laudo(laudo_id)

    if not secoes:
        st.info("Este laudo não possui seções.")
        return

    from services.rep_service import buscar_rep
    rep = buscar_rep(laudo['rep_id'])

    st.markdown("---")
    st.markdown(f"### 📝 Editando: REP {rep['numero_rep']} - {rep['tipo_exame_nome']}")

    placeholders_disponiveis = """
    **Placeholders disponíveis (copie e cole no texto):**

    | Placeholder | Descrição |
    |-------------|-----------|
    | `{{numero_rep}}` | Número da REP |
    | `{{data_solicitacao}}` | Data da solicitação |
    | `{{nome_autoridade}}` | Nome da autoridade solicitante |
    | `{{nome_envolvido}}` | Nome do envolvido/vítima |
    | `{{local_fato}}` | Descrição do local do fato |
    | `{{tipo_exame}}` | Tipo de exame |
    | `{{solicitante}}` | Órgão solicitante |
    | `{{numero_documento}}` | Número do documento |
    | `{{data_documento}}` | Data do documento |
    """

    with st.expander("Ver Placeholders Disponíveis", expanded=False):
        st.markdown(placeholders_disponiveis)

    secoes_salvas = {}

    for idx, secao in enumerate(secoes, 1):
        with st.expander(f"{idx} - {secao['titulo'].upper()}", expanded=True):
            if secao['obrigatoria']:
                st.markdown("<small style='color: #e74c3c;'>* Obrigatória</small>", unsafe_allow_html=True)

            if st_quill:
                conteudo = st_quill(
                    html=True,
                    value=secao['conteudo'] or "",
                    key=f"secao_{secao['id']}"
                )
            else:
                st.warning("Quill Editor não disponível. Usando campo de texto padrão.")
                conteudo = st.text_area(
                    "Conteúdo",
                    value=secao['conteudo'] or "",
                    height=200,
                    key=f"secao_{secao['id']}",
                    help=f"Seção: {secao['titulo']}. Use os placeholders listados no expander acima."
                )

            secoes_salvas[secao['id']] = {
                'titulo': secao['titulo'],
                'conteudo': conteudo,
                'obrigatoria': secao['obrigatoria']
            }

    if st.button("💾 Salvar Seções", type="primary"):
        erros = []
        for secao_id, dados in secoes_salvas.items():
            if dados['obrigatoria'] and not dados['conteudo'].strip():
                erros.append(dados['titulo'])

        if erros:
            st.error(f"❌ Preencha as seções obrigatórias: {', '.join(erros)}")
        else:
            for secao_id, dados in secoes_salvas.items():
                atualizar_secao_laudo(secao_id, dados['conteudo'])
            st.success("✅ Seções salvas com sucesso!")
            st.rerun()


def main():
    st.title("✏️ Editar Laudo")
    st.markdown("Editar laudos existentes.")
    st.markdown("---")

    laudos_existentes = listar_laudos(
        usuario_id=usuario_logado['id'],
        status='Rascunho'
    )

    if not laudos_existentes:
        st.info("Nenhum laudo em rascunho encontrado.")
        st.markdown("---")
        st.markdown("### Como criar um novo laudo?")
        st.page_link("pages/novo_laudo.py", label="Clique aqui para vincular um laudo a uma REP", use_container_width=True)
        st.stop()

    opcoes_laudos = {
        f"{l['numero_rep']} - {l['tipo_exame_nome']} ({l['status']})": l['id']
        for l in laudos_existentes
    }
    nomes_laudos = ["Selecione um Laudo"] + list(opcoes_laudos.keys())

    laudo_selecionado = st.selectbox(
        "Selecione um Laudo para Editar",
        options=nomes_laudos,
        key="laudo_selecionado"
    )

    if laudo_selecionado != "Selecione um Laudo":
        laudo_id = opcoes_laudos[laudo_selecionado]
        st.session_state["laudo_id_selecionado"] = laudo_id
        renderizar_secoes(laudo_id)


main()