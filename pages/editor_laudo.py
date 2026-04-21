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
    atualizar_secao_laudo,
    listar_versoes,
    restaurar_versao,
    excluir_versao,
    salvar_versao_snapshot
)
from services.rep_service import listar_reps
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

    from services.rep_service import buscar_rep
    rep = buscar_rep(laudo['rep_id'])

    st.markdown("---")
    st.markdown(f"### Editando: REP {rep['numero_rep']} - {rep['tipo_exame_nome']}")

    placeholders_disponiveis = """
    **Placeholders disponíveis (copie e cole no texto):**

    *Dados Gerais da REP:*
    | Placeholder | Descrição |
    |-------------|-----------|
    | `{{numero_rep}}` | Número da REP |
    | `{{data_solicitacao}}` | Data da solicitação |
    | `{{tipo_exame}}` | Nome do tipo de exame |
    | `{{nome_envolvido}}` | Nome do envolvido/vítima |

    *Dados do Solicitante:*
    | Placeholder | Descrição |
    |-------------|-----------|
    | `{{solicitante}}` | Nome do órgão solicitante |
    | `{{solicitante_orgao}}` | Órgão do solicitante |
    | `{{nome_autoridade}}` | Nome da autoridade solicitante |

    *Detalhes da Solicitação:*
    | Placeholder | Descrição |
    |-------------|-----------|
    | `{{tipo_solicitacao}}` | Tipo de documento (BO, Ofício, etc) |
    | `{{numero_documento}}` | Número do documento |
    | `{{data_documento}}` | Data do documento |

    *Dados do Local (se aplicável):*
    | Placeholder | Descrição |
    |-------------|-----------|
    | `{{local_fato}}` | Descrição do local do fato |
    | `{{horario_acionamento}}` | Horário de acionamento |
    | `{{horario_chegada}}` | Horário de chegada ao local |
    | `{{horario_saida}}` | Horário de saída do local |
    | `{{latitude}}` | Latitude do local |
    | `{{longitude}}` | Longitude do local |

    *Dados do Perito:*
    | Placeholder | Descrição |
    |-------------|-----------|
    | `{{perito_nome}}` | Nome do perito responsável |
    | `{{perito_matricula}}` | Matrícula do perito |
    | `{{perito_cargo}}` | Cargo do perito |
    | `{{perito_lotacao}}` | Lotação do perito |
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
                    'enableDragAndDropFileToEditor': False,
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
                    key=f"secao_{secao['id']}",
                    help=f"Seção: {secao['titulo']}. Use os placeholders listados no expander acima."
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
                from services.laudo_service import atualizar_status_laudo
                try:
                    atualizar_status_laudo(laudo_id, 'Finalizado')
                    st.success("Laudo marcado como Finalizado!")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Erro: {e}")

    st.markdown("---")
    col_vis, col_salvar = st.columns([1, 3])
    with col_vis:
        try:
            from services.gerador_pdf_playwright import gerar_pdf_laudo
            from services.rep_service import buscar_rep
            laudo = buscar_laudo(laudo_id)
            rep = buscar_rep(laudo['rep_id'])
            numero_rep = rep['numero_rep'].replace('/', '_')
            pdf_bytes = gerar_pdf_laudo(laudo_id)
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
        with st.expander("Versoes Anteriores"):
            st.caption("Apos restaurar use o botao Visualizar PDF para ver o resultado.")
            for v in versoes:
                col_v1, col_v2, col_v3 = st.columns([3, 1, 1])
                with col_v1:
                    st.markdown(f"**Versao {v['versao']}** - {formatar_data_br(v['criado_em'])}")
                with col_v2:
                    if st.button("Restaurar", key=f"restaurar_{v['id']}"):
                        try:
                            restaurar_versao(v['id'])
                            st.success(f"Versao {v['versao']} restaurada!")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"Erro: {e}")
                with col_v3:
                    if st.button("Excluir", key=f"excluir_{v['id']}"):
                        try:
                            excluir_versao(v['id'])
                            st.success("Versao excluida!")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"Erro: {e}")


def main():
    st.title("Editar Laudo")
    st.markdown("Editar laudos existentes.")
    st.markdown("---")

    reps_em_andamento = listar_reps(
        status='Em Andamento',
        usuario_id=usuario_logado['id']
    )

    if not reps_em_andamento:
        st.info("Nenhuma REP em andamento encontrada.")
        st.markdown("---")
        st.markdown("### Como criar um novo laudo?")
        st.page_link("pages/novo_laudo.py", label="Clique aqui para vincular um laudo a uma REP", use_container_width=True)
        st.stop()

    opcoes_reps = {
        f"{r['numero_rep']} — {r['tipo_exame_nome']} — ({r['status']})": r['id']
        for r in reps_em_andamento
    }
    nomes_reps = ["Selecione uma REP"] + sorted(list(opcoes_reps.keys()))

    rep_selecionada = st.selectbox(
        "Selecione uma REP para Editar o Laudo",
        options=nomes_reps,
        key="rep_selecionada"
    )

    if rep_selecionada != "Selecione uma REP":
        rep_id = opcoes_reps[rep_selecionada]
        laudo = buscar_laudo_por_rep(rep_id)
        if laudo:
            st.session_state["laudo_id_selecionado"] = laudo['id']
            renderizar_secoes(laudo['id'])
        else:
            st.warning("Esta REP não possui laudo vinculado.")


main()
