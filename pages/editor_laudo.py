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
from datetime import datetime
import logging

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
from services.placeholders_custom_service import listar_placeholders_custom
from services.ai_service import gerar_texto_com_ia

logger = logging.getLogger(__name__)

# Jodit config cache - criado uma única vez
JODIT_CONFIG = {
    'minHeight': 350,
    'height': 400,
    'theme': 'default',
    'allowResizeY': True,
    'allowResizeX': True,
    'colorPickerDefaultTab': 'text',
    'uploader': {
        'insertImageAsBase64URI': True
    }
}


def formatar_data_br(data_iso: str) -> str:
    """Formata data ISO para padrão brasileiro."""
    try:
        dt = datetime.fromisoformat(data_iso.replace(' ', 'T'))
        return dt.strftime("%d/%m/%Y - %H:%M:%S")
    except ValueError as e:
        logger.warning(f"Erro ao formatar data {data_iso}: {e}")
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


@st.cache_data(ttl=300)
def _cache_placeholders():
    """Cache placeholders personalizados por 5 minutos."""
    return listar_placeholders_custom()


@st.cache_data(ttl=300)
def _cache_rep(rep_id):
    """Cache REP por 5 minutos."""
    return buscar_rep(rep_id)


def renderizar_secoes(laudo_id: int, laudo: dict):
    """
    Renderiza seções de edição do laudo.
    Recebe laudo como parâmetro para evitar nova query.
    """
    secoes = listar_secoes_laudo(laudo_id)

    if not secoes:
        st.info("Este laudo não possui seções.")
        return

    rep = _cache_rep(laudo['rep_id'])

    st.markdown("---")
    st.markdown(f"### Editando: REP {rep['numero_rep']} - {rep.get('tipo_exame_nome') or 'Tipo não definido'}")

    with st.expander("💡 Explorar Placeholders Disponíveis", expanded=False):
        st.markdown("<small>Clique no ícone de copiar 📋 ao lado do placeholder para utilizá-lo facilmente no texto.</small>", unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Dados Gerais", "🏢 Solicitante", "📄 Template", "✨ Personalizados"
        ])
        
        with tab1:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.caption("Número da REP")
                st.code("{{numero_rep}}", language="plaintext")
                st.caption("Tipo de Exame")
                st.code("{{tipo_exame}}", language="plaintext")
            with c2:
                st.caption("Data da Solicitação")
                st.code("{{data_solicitacao}}", language="plaintext")
                st.caption("Nome do Envolvido")
                st.code("{{nome_envolvido}}", language="plaintext")
            with c3:
                st.caption("Cidade do Perito")
                st.code("{{cidade}}", language="plaintext")
                st.caption("Observações")
                st.code("{{observacoes}}", language="plaintext")
                
        with tab2:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.caption("Órgão Solicitante")
                st.code("{{solicitante}}", language="plaintext")
            with c2:
                st.caption("Nome da Autoridade")
                st.code("{{nome_autoridade}}", language="plaintext")
            with c3:
                st.caption("Órgão da Autoridade")
                st.code("{{solicitante_orgao}}", language="plaintext")

        with tab3:
            c1, c2 = st.columns(2)
            with c1:
                st.caption("Nome do Template")
                st.code("{{template_nome}}", language="plaintext")
            with c2:
                st.caption("Descrição do Template")
                st.code("{{template_descricao}}", language="plaintext")

        with tab4:
            placeholders_custom = _cache_placeholders()
            if placeholders_custom:
                cols = st.columns(3)
                for i, ph in enumerate(placeholders_custom):
                    with cols[i % 3]:
                        st.caption(f"Valor atual: {ph.get('valor', '') or '—'}")
                        st.code(f"{{{{{ph.get('nome', '')}}}}}", language="plaintext")
            else:
                st.info("Nenhum placeholder personalizado cadastrado.")

    secoes_salvas = {}

    for idx, secao in enumerate(secoes, 1):
        with st.expander(f"{idx} - {secao['titulo'].upper()}", expanded=True):
            if secao['obrigatoria']:
                st.markdown("<small style='color: #e74c3c;'>* Obrigatória</small>", unsafe_allow_html=True)

            if st_jodit:
                conteudo = st_jodit(
                    value=secao['conteudo'] or "",
                    key=f"secao_{secao['id']}",
                    config=JODIT_CONFIG
                )
            else:
                st.warning("Editor Jodit não disponível. Usando campo de texto padrão.")
                conteudo = st.text_area(
                    "Conteúdo",
                    value=secao['conteudo'] or "",
                    height=200,
                    key=f"secao_{secao['id']}"
                )

            mostrar_ia = st.checkbox("✨ Abrir Assistente de IA (Groq)", key=f"chk_ia_{secao['id']}")
            if mostrar_ia:
                with st.container(border=True):
                    st.markdown(f"<small>A IA analisará o texto atual desta seção (**{secao['titulo']}**) para gerar a sugestão.</small>", unsafe_allow_html=True)
                    
                    c_btn1, c_btn2, c_btn3 = st.columns(3)
                    
                    acao_ia = None
                    if c_btn1.button("Revisar a ortografia", key=f"btn_rev_{secao['id']}", use_container_width=True):
                        acao_ia = 'revisar_ortografia'
                    if c_btn2.button("Adequar texto", key=f"btn_ade_{secao['id']}", use_container_width=True):
                        acao_ia = 'adequar_texto'
                    if c_btn3.button("Descrição de imagem", key=f"btn_desc_{secao['id']}", use_container_width=True):
                        acao_ia = 'descricao_imagem'
                    
                    state_key = f"ia_res_{secao['id']}"
                    if acao_ia:
                        with st.spinner("A IA está gerando a sugestão..."):
                            resultado = gerar_texto_com_ia(acao_ia, secao['titulo'], conteudo)
                            st.session_state[state_key] = resultado
                    
                    if state_key in st.session_state:
                        st.success("Sugestão gerada com sucesso! Copie o texto abaixo e cole no editor.")
                        
                        st.markdown("**Sugestão da IA:**")
                        st.code(st.session_state[state_key], language="markdown", wrap_lines=True)
                        
                        if st.button("Limpar Sugestão", key=f"btn_limp_{secao['id']}"):
                            del st.session_state[state_key]
                            st.rerun()

            secoes_salvas[secao['id']] = {
                'titulo': secao['titulo'],
                'conteudo': conteudo,
                'obrigatoria': secao['obrigatoria']
            }

    usuario = obter_usuario_logado()
    pasta_exp = usuario.get('pasta_exportacao', '') if usuario else ''

    col_salvar, col_vis = st.columns(2)
    with col_salvar:
        if st.button("Salvar Laudo", type="primary", use_container_width=True):
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

                if pasta_exp:
                    try:
                        from services.gerador_pdf_playwright import salvar_pdf_laudo
                        import webbrowser
                        caminho_pdf = salvar_pdf_laudo(laudo_id, pasta_exp)
                        webbrowser.open(f'file:///{caminho_pdf}')
                        st.success(f"PDF gerado e aberto: {caminho_pdf}")
                    except Exception as e:
                        st.error(f"Erro ao gerar PDF: {e}")
                st.rerun()

    with col_vis:
        if pasta_exp and st.button("Visualizar PDF", type="primary", use_container_width=True):
            try:
                from services.gerador_pdf_playwright import salvar_pdf_laudo
                import webbrowser
                caminho_pdf = salvar_pdf_laudo(laudo_id, pasta_exp)
                webbrowser.open(f'file:///{caminho_pdf}')
                st.success(f"PDF aberto: {caminho_pdf}")
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")
        elif not pasta_exp:
            st.info("Configure a pasta de exportação nas configurações do perfil.")

    if laudo['status'] == 'Em Andamento':
        st.markdown("---")
        col_btn_finalizar, _ = st.columns([1, 3])
        with col_btn_finalizar:
            if st.button("Marcar como Finalizado", type="primary", use_container_width=True):
                try:
                    finalizar_laudo(laudo_id)
                    st.success("Laudo marcado como Finalizado e REP vinculada marcada como Concluido!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Erro: {e}")

    versoes = listar_versoes(laudo_id)
    if versoes:
        with st.expander("Versões Anteriores", expanded=False):
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

    # Cria o dicionário de opções apenas uma vez
    opcoes_reps = {
        f"{l['numero_rep']} — {l.get('tipo_exame_nome') or 'Tipo não definido'} — ({l['status']})": l['id']
        for l in laudos_usuario
    }
    nomes_reps = ["Selecione uma REP"] + sorted(list(opcoes_reps.keys()))

    rep_selecionada = st.selectbox(
        "Selecione uma REP para Editar o Laudo",
        options=nomes_reps,
        key="rep_selecionada_dropdown"
    )

    if rep_selecionada != "Selecione uma REP":
        laudo_id = opcoes_reps[rep_selecionada]
        laudo = buscar_laudo(laudo_id)
        if laudo:
            renderizar_secoes(laudo_id, laudo)
        else:
            st.warning("Este laudo não possui conteúdo vinculado.")


main()
