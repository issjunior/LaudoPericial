# pages/editor_laudo.py
"""
pages/editor_laudo.py
────────────────────────────────────────────────────
Página para editar Laudos existentes.
────────────────────────────────────────────────────
"""

import sys
import os
import streamlit as st

from core.path_utils import get_root
ROOT = str(get_root())
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu
from core.auth import obter_usuario_logado
from services.laudo_service import (
    listar_laudos,
    buscar_laudo,
    listar_secoes_laudo,
    atualizar_secao_laudo,
    finalizar_laudo,
    listar_versoes,
    restaurar_versao,
    excluir_versao,
    salvar_versao_snapshot
)
from services.rep_service import listar_reps, buscar_rep
from services.laudo_service import buscar_laudo_por_rep


def formatar_data_br(data_iso: str) -> str:
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(data_iso.replace(' ', 'T'))
        return dt.strftime("%d/%m/%Y - %H:%M:%S")
    except:
        return data_iso


try:
    from streamlit_jodit import st_jodit
except ImportError:
    st_jodit = None

st.set_page_config(
    page_title="Editar Laudo — LaudoPericial",
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


def renderizar_secoes(laudo_id: int):
    secoes = listar_secoes_laudo(laudo_id)
    laudo = buscar_laudo(laudo_id)

    if not secoes:
        st.info("Este laudo não possui seções.")
        return

    rep = buscar_rep(laudo['rep_id'])

    st.markdown("---")
    st.markdown(f"### Editando: REP {rep['numero_rep']} - {rep.get('tipo_exame_nome') or 'Tipo não definido'}")

    placeholders_disponiveis = """
    **Placeholders disponíveis (copie e cole no texto):**

    *Dados Gerais da REP:*
    | Placeholder | Descrição |
    |-------------|-----------|
    | `{{numero_rep}}` | Número da REP |
    | `{{data_solicitacao}}` | Data da solicitação (DD/MM/AAAA) |
    | `{{tipo_exame}}` | Nome do tipo de exame |
    | `{{nome_envolvido}}` | Nome do envolvido/vítima |
    | `{{cidade}}` | Cidade do perito (lotação) |

    *Dados do Solicitante:*
    | Placeholder | Descrição |
    |-------------|-----------|
    | `{{solicitante}}` | Nome do órgão solicitante |
    | `{{solicitante_orgao}}` | Órgão do solicitante |
    | `{{nome_autoridade}}` | Nome da autoridade solicitante |
    """

    with st.expander("Ver Placeholders Disponíveis", expanded=False):
        st.markdown(placeholders_disponiveis)

    secoes_salvas = {}

    for idx, secao in enumerate(secoes, 1):
        with st.expander(f"{idx} - {secao['titulo'].upper()}", expanded=True):
            if secao['obrigatoria']:
                st.markdown("<small style='color: #e74c3c;'>* Obrigatória</small>", unsafe_allow_html=True)

            if st_jodit:
                config = {
                    'minHeight': 350,
                    'height': 400,
                    'theme': 'default',
                    'allowResizeY': True,
                    'allowResizeX': True,
                }
                conteudo = st_jodit(
                    value=secao['conteudo'] or "",
                    key=f"secao_{secao['id']}",
                    config=config
                )
            else:
                st.warning("Editor Jodit não disponível. Usando campo de texto padrão.")
                conteudo = st.text_area(
                    "Conteúdo",
                    value=secao['conteudo'] or "",
                    height=200,
                    key=f"secao_{secao['id']}"
                )

            secoes_salvas[secao['id']] = {
                'titulo': secao['titulo'],
                'conteudo': conteudo,
                'obrigatoria': secao['obrigatoria']
            }

    if st.button("Salvar Laudo", type="primary"):
        erros = []
        for secao_id, dados in secoes_salvas.items():
            if dados['obrigatoria'] and not dados['conteudo'].strip():
                erros.append(dados['titulo'])

        if erros:
            st.error(f"Preencha as seções obrigatórias: {', '.join(erros)}")
        else:
            for secao_id, dados in secoes_salvas.items():
                atualizar_secao_laudo(secao_id, dados['conteudo'])
            
            try:
                versao = salvar_versao_snapshot(laudo_id)
                st.success(f"Laudo salvo! Versao {versao} criada (max. 3 versoes)")
            except ValueError:
                st.success("Laudo salvo com sucesso!")
            st.rerun()

    if laudo['status'] == 'Em Andamento':
        st.markdown("---")
        col_btn_finalizar, _ = st.columns([1, 3])
        with col_btn_finalizar:
            if st.button("✅ Marcar como Finalizado", type="primary", use_container_width=True):
                try:
                    finalizar_laudo(laudo_id)
                    st.success("Laudo marcado como Finalizado e REP vinculada marcada como Concluído!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Erro: {e}")

    st.markdown("---")
    col_vis, _ = st.columns([1, 3])
    with col_vis:
        try:
            from services.gerador_pdf_playwright import gerar_pdf_laudo
            pdf_bytes = gerar_pdf_laudo(laudo_id)
            numero_rep = rep['numero_rep'].replace('/', '_')
            st.download_button(
                label="Visualizar PDF",
                data=pdf_bytes,
                file_name=f"{numero_rep}.pdf",
                mime="application/pdf",
                icon="👁️"
            )
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

    versoes = listar_versoes(laudo_id)
    if versoes:
        with st.expander("Versões Anteriores"):
            for v in versoes:
                col_v1, col_v2, col_v3 = st.columns([3, 1, 1])
                with col_v1:
                    st.markdown(f"**Versão {v['versao']}** - {formatar_data_br(v['criado_em'])}")
                with col_v2:
                    if st.button("Restaurar", key=f"restaurar_{v['id']}"):
                        restaurar_versao(v['id'])
                        st.rerun()
                with col_v3:
                    if st.button("Excluir", key=f"excluir_{v['id']}"):
                        excluir_versao(v['id'])
                        st.rerun()


def main():
    st.title("Editar Laudo")
    st.markdown("Editar laudos existentes.")
    st.markdown("---")

    # Busca laudos vinculados ao usuário logado
    laudos_usuario = listar_laudos(usuario_id=usuario_logado['id'])

    if not laudos_usuario:
        st.info("Nenhum laudo encontrado para edição.")
        st.markdown("---")
        st.page_link("pages/novo_laudo.py", label="Clique aqui para vincular um laudo a uma REP", use_container_width=True)
        st.stop()

    opcoes_reps = {
        f"{l['numero_rep']} — {l.get('tipo_exame_nome') or 'Tipo não definido'} — ({l['status']})": l['rep_id']
        for l in laudos_usuario
    }
    nomes_reps = ["Selecione uma REP"] + sorted(list(opcoes_reps.keys()))

    rep_selecionada = st.selectbox(
        "Selecione uma REP para Editar o Laudo",
        options=nomes_reps,
        key="rep_selecionada_dropdown"
    )

    if rep_selecionada != "Selecione uma REP":
        rep_id = opcoes_reps[rep_selecionada]
        laudo = buscar_laudo_por_rep(rep_id)
        if laudo:
            renderizar_secoes(laudo['id'])
        else:
            st.warning("Esta REP não possui laudo vinculado.")


main()
