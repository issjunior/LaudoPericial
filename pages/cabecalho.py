"""
pages/cabecalho.py
─────────────────────────────────────────────────────
Página para configurar o cabeçalho do Laudo PDF.
Permite personalização do texto que aparece em todos os laudos.

Nota: O cabeçalho editado aqui é automaticamente utilizado pelo novo
gerador de PDF (Playwright) em services/gerador_pdf_playwright.py
para manter a formatação completa no documento final.
─────────────────────────────────────────────────────
"""

import sys
import os

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st
from components.menu import renderizar_menu
from core.auth import obter_usuario_logado
from database.db import executar_query, executar_comando


st.set_page_config(
    page_title="Cabeçalho do Laudo — LaudoPericial",
    page_icon="📄",
    layout="wide",
)

st.session_state["_active_page"] = __file__
renderizar_menu()

usuario_logado = obter_usuario_logado()
if not usuario_logado:
    st.error("Usuário não autenticado. Por favor, faça login.")
    st.stop()


def buscar_cabecalho() -> dict:
    sql = "SELECT id, modelo, conteudo, ativo FROM modelo_cabecalho WHERE ativo = 1 LIMIT 1"
    rows = executar_query(sql)
    return dict(rows[0]) if rows else None


def salvar_cabecalho(modelo: str, conteudo: str) -> None:
    existente = buscar_cabecalho()
    if existente:
        sql = "UPDATE modelo_cabecalho SET modelo = ?, conteudo = ? WHERE id = ?"
        executar_comando(sql, (modelo, conteudo, existente['id']))
    else:
        sql = "INSERT INTO modelo_cabecalho (modelo, conteudo, ativo) VALUES (?, ?, 1)"
        executar_comando(sql, (modelo, conteudo))


try:
    from streamlit_jodit import st_jodit
except ImportError:
    st_jodit = None


def main():
    st.title("📄 Configurar Cabeçalho do Laudo")
    
    with st.expander("ℹ️ O que é o Cabeçalho?", expanded=False):
        st.markdown("""
        O **cabeçalho** é o texto personalizado que aparece no topo de todos os laudos 
        Periciais, independente do template utilizado.
        """)

    with st.expander("Ver Placeholders Disponíveis", expanded=False):
        st.markdown("""
        | Placeholder | Descrição |
        |-------------|-----------|
        | `{{tipo_exame}}` | Nome do tipo de exame |
        | `{{tipo_exame_codigo}}` | Código do tipo de exame |
        | `{{numero_rep}}` | Número da REP |
        | `{{data_solicitacao}}` | Data da solicitação |
        """)

    st.markdown("### Editar Cabeçalho")

    cabecalho_atual = buscar_cabecalho()

    valor_padrao = """LAUDO DE PERÍCIA CRIMINAL
({{tipo_exame}})

Código: {{tipo_exame_codigo}}
REP: {{numero_rep}} | Data: {{data_solicitacao}}"""

    conteudo_cabecalho = None
    if st_jodit:
        config = {
            'minHeight': 250,
            'height': 300,
            'theme': 'default',
            'defaultLineHeight': 1,
            'allowResizeY': True,
            'allowResizeX': True,
            'enableDragAndDropFileToEditor': False,
        }
        st_jodit(
            value=cabecalho_atual.get('conteudo', valor_padrao) if cabecalho_atual else valor_padrao,
            key="cabecalho_editor",
            config=config
        )
        conteudo_cabecalho = st.session_state.get("cabecalho_editor") or cabecalho_atual.get('conteudo', valor_padrao) if cabecalho_atual else valor_padrao
    else:
        conteudo_cabecalho = st.text_area(
            "Conteúdo do Cabeçalho",
            value=cabecalho_atual.get('conteudo', valor_padrao) if cabecalho_atual else valor_padrao,
            height=200,
            help="Use quebras de linha para formatar."
        )

    st.markdown("---")

    if conteudo_cabecalho:
        st.markdown("#### Preview")
        preview = conteudo_cabecalho.replace('{{tipo_exame}}', 'Exame de equipamento Eletrônico')
        preview = preview.replace('{{tipo_exame_codigo}}', 'E-381')
        preview = preview.replace('{{numero_rep}}', '00.000-2024')
        preview = preview.replace('{{data_solicitacao}}', '2024-01-01')
        st.markdown(f'<div style="background-color:white;padding:15px;border-radius:5px;">{preview}</div>', unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        salvar = st.button("💾 Salvar Cabeçalho", type="primary", use_container_width=True)
    if salvar:
        try:
            salvar_cabecalho("Padrão", conteudo_cabecalho)
            st.success("✅ Cabeçalho salvo com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao salvar: {e}")


main()