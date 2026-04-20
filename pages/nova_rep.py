# pages/nova_rep.py
"""
pages/nova_rep.py
──────────────────────────────────────────────────────
Página para criação de uma nova Requisição de Exame Pericial (REP).
──────────────────────────────────────────────────────
"""

import sys
import os
import streamlit as st
from datetime import date, datetime

# Garante que a raiz do projeto está no sys.path
# Funciona localmente E no Streamlit Cloud
ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu
from core.auth import obter_usuario_logado
from services.cadastro_service import listar_tipos_exame, listar_solicitantes
from services.rep_service import criar_rep

# ──────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nova REP — LaudoPericial",
    page_icon="➕",
    layout="wide",
)

# Define a página atual na sessão para o menu funcionar corretamente
st.session_state["_active_page"] = __file__

# Renderiza o menu lateral (já exige autenticação)
renderizar_menu()

# Obtém o usuário logado para vincular a REP
usuario_logado = obter_usuario_logado()
if not usuario_logado:
    st.error("Usuário não autenticado. Por favor, faça login.")
    st.stop()

# ──────────────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ──────────────────────────────────────────────────────

def main():
    st.title("➕ Nova Requisição de Exame Pericial (REP)")
    st.markdown("Preencha os dados para registrar uma nova REP.")
    st.markdown("---")

    # Carrega dados para os selectboxes
    tipos_exame = listar_tipos_exame(apenas_ativos=True)
    solicitantes = listar_solicitantes(apenas_ativos=True)

    # Mapeia para {nome: id} para os selectboxes e ORDENA ALFABETICAMENTE
    opcoes_tipos_exame = {f"{te['codigo']} - {te['nome']}": te['id'] for te in tipos_exame}
    nomes_tipos_exame = ["Selecione um Tipo de Exame"] + sorted(list(opcoes_tipos_exame.keys()))

    opcoes_solicitantes = {f"{s['orgao']} ({s['nome'] or 'N/A'})": s['id'] for s in solicitantes}
    nomes_solicitantes = ["Selecione um Solicitante"] + sorted(list(opcoes_solicitantes.keys()))


    # Estado para controlar a exibição dos campos de local
    if "exame_de_local_selecionado" not in st.session_state:
        st.session_state["exame_de_local_selecionado"] = False

    with st.form("form_nova_rep", clear_on_submit=True):
        st.markdown("### Dados Gerais da REP")
        col1, col2, col3 = st.columns(3)

        with col1:
            numero_rep = st.text_input(
                "Número da REP *",
                placeholder=f"Ex: 12.345-{date.today().year}", # NOVO PLACEHOLDER
                help="Número único de identificação da Requisição de Exame Pericial no formato XX.XXX-ANO." # NOVA AJUDA
            )
        with col2:
            data_solicitacao = st.date_input(
                "Data da Solicitação *",
                value=date.today(),
                format="DD/MM/YYYY", # NOVO FORMATO DE EXIBIÇÃO
                help="Data em que a REP foi solicitada."
            )
        with col3:
            tipo_exame_selecionado = st.selectbox(
                "Tipo de Exame *",
                options=nomes_tipos_exame,
                index=0,
                help="Selecione o tipo de exame pericial."
            )
            # Atualiza o estado para mostrar/esconder campos de local
            if tipo_exame_selecionado != "Selecione um Tipo de Exame":
                tipo_exame_id_selecionado = opcoes_tipos_exame[tipo_exame_selecionado]
                exame_info = next((te for te in tipos_exame if te['id'] == tipo_exame_id_selecionado), None)
                if exame_info and exame_info['exame_de_local']:
                    st.session_state["exame_de_local_selecionado"] = True
                else:
                    st.session_state["exame_de_local_selecionado"] = False
            else:
                st.session_state["exame_de_local_selecionado"] = False

        # NOVO CAMPO: Nome do Envolvido/Vítima
        nome_envolvido = st.text_input(
            "Nome do Envolvido / Vítima (Opcional)",
            placeholder="Ex: João da Silva, Vítima 01",
            help="Nome da pessoa envolvida ou vítima principal da ocorrência."
        )

        st.markdown("### Dados do Solicitante")
        col4, col5 = st.columns(2)

        with col4:
            solicitante_selecionado = st.selectbox(
                "Órgão Solicitante *",
                options=nomes_solicitantes,
                index=0,
                help="Selecione o órgão ou pessoa que solicitou a perícia."
            )
        with col5:
            nome_autoridade = st.text_input(
                "Nome da Autoridade Solicitante (Opcional)",
                placeholder="Ex: Delegado João da Silva",
                help="Nome da autoridade que assina o documento de solicitação."
            )

        st.markdown("### Detalhes da Solicitação")
        col6, col7, col8 = st.columns(3)

        with col6:
            tipo_documento = st.selectbox(
                "Tipo de Documento *",
                options=["Selecione", "BO", "BO PM", "BO PC", "Ofício", "CECOMP", "Outro"], # NOVAS OPÇÕES
                index=0,
                help="Tipo de documento que formaliza a solicitação (Boletim de Ocorrência, Ofício, etc.)."
            )
        with col7:
            numero_documento = st.text_input(
                "Número do Documento *",
                placeholder="Ex: 12345/2024",
                help="Número do documento de solicitação."
            )
        with col8:
            data_documento = st.date_input(
                "Data do Documento (Opcional)",
                value=None,
                format="DD/MM/YYYY", # NOVO FORMATO DE EXIBIÇÃO
                help="Data de emissão do documento de solicitação."
            )

        # Abas: Dados Gerais e Dados do Local
        st.markdown("### 📝 Dados da REP")
        st.markdown("**Selecione uma aba abaixo:**")
        if st.session_state.get("exame_de_local_selecionado"):
            st.warning("⚠️ IMPORTANTE: Este tipo de exame requer dados do local. Clique na aba **'Dados do Local'** para preencher!")

        tab1, tab2 = st.tabs(["📋 Dados Gerais", "🌍 Dados do Local"])

        with tab1:
            if st.session_state.get("exame_de_local_selecionado"):
                st.info("Dados básicos para este tipo de exame.")
            else:
                st.info("Dados básicos para todos os tipos de exame.")

        with tab2:
            if st.session_state["exame_de_local_selecionado"]:
                local_fato_descricao = st.text_area(
                    "Descrição do Local do Fato",
                    placeholder="Ex: Residência na Rua X, nº Y, Bairro Z. Próximo ao mercado K.",
                    help="Descrição detalhada do local onde ocorreu o fato.",
                    height=80
                )
                col_horario1, col_horario2, col_horario3 = st.columns(3)
                with col_horario1:
                    horario_acionamento = st.time_input(
                        "Horário de Acionamento",
                        value=None,
                        help="Horário em que a equipe pericial foi acionada."
                    )
                with col_horario2:
                    horario_chegada = st.time_input(
                        "Horário de Chegada",
                        value=None,
                        help="Horário de chegada da equipe pericial ao local."
                    )
                with col_horario3:
                    horario_saida = st.time_input(
                        "Horário de Saída",
                        value=None,
                        help="Horário de saída da equipe pericial do local."
                    )

                col_coords1, col_coords2 = st.columns(2)
                with col_coords1:
                    latitude = st.text_input(
                        "Latitude",
                        placeholder="Ex: -25.4284",
                        help="Coordenada de latitude do local do exame."
                    )
                with col_coords2:
                    longitude = st.text_input(
                        "Longitude",
                        placeholder="Ex: -49.2733",
                        help="Coordenada de longitude do local do exame."
                    )
            else:
                local_fato_descricao = None
                horario_acionamento = None
                horario_chegada = None
                horario_saida = None
                latitude = None
                longitude = None
                st.info("Este tipo de exame não requer deslocamento ao local do fato.")

        with st.expander("📝 Observações Adicionais", expanded=False):
            observacoes = st.text_area(
                "Observações Gerais (Opcional)",
                height=100,
                help="Qualquer informação extra relevante para a REP."
            )

        st.markdown("---")

        col_submit, col_cancel = st.columns([1, 5])

        with col_submit:
            if st.session_state.get("exame_de_local_selecionado"):
                submitted = st.form_submit_button(
                    "💾 Atualizar REP",
                    use_container_width=True,
                    type="primary"
                )
            else:
                submitted = st.form_submit_button(
                    "💾 Registrar REP",
                    use_container_width=True,
                    type="primary"
                )

        if submitted:
            # Validações
            if not numero_rep:
                st.error("❌ O número da REP é obrigatório.")
                st.stop()
            if tipo_exame_selecionado == "Selecione um Tipo de Exame":
                st.error("❌ Por favor, selecione um Tipo de Exame.")
                st.stop()
            if solicitante_selecionado == "Selecione um Solicitante":
                st.error("❌ Por favor, selecione um Solicitante.")
                st.stop()
            if tipo_documento == "Selecione":
                st.error("❌ Por favor, selecione o Tipo de Documento.")
                st.stop()
            if not numero_documento:
                st.error("❌ O número do documento é obrigatório.")
                st.stop()

            # Converte IDs
            tipo_exame_id = opcoes_tipos_exame[tipo_exame_selecionado]
            solicitante_id = opcoes_solicitantes[solicitante_selecionado]

            # Formata datas e horários para o banco (YYYY-MM-DD para SQLite)
            data_solicitacao_str = data_solicitacao.strftime("%Y-%m-%d")
            data_documento_str = data_documento.strftime("%Y-%m-%d") if data_documento else None
            horario_acionamento_str = horario_acionamento.strftime("%H:%M") if horario_acionamento else None
            horario_chegada_str = horario_chegada.strftime("%H:%M") if horario_chegada else None
            horario_saida_str = horario_saida.strftime("%H:%M") if horario_saida else None

            try:
                nova_rep_id = criar_rep(
                    numero_rep          = numero_rep,
                    data_solicitacao    = data_solicitacao_str,
                    horario_acionamento = horario_acionamento_str,
                    horario_chegada     = horario_chegada_str,
                    horario_saida       = horario_saida_str,
                    tipo_solicitacao    = tipo_documento,
                    numero_documento    = numero_documento,
                    data_documento      = data_documento_str,
                    solicitante_id      = solicitante_id,
                    nome_autoridade     = nome_autoridade,
                    nome_envolvido      = nome_envolvido, # NOVO CAMPO
                    local_fato_descricao= local_fato_descricao, # NOVO CAMPO
                    tipo_exame_id       = tipo_exame_id,
                    latitude            = latitude,
                    longitude           = longitude,
                    observacoes         = observacoes,
                    usuario_id          = usuario_logado['id']
                )
                st.success(f"✅ REP **{numero_rep}** registrada com sucesso! ID: {nova_rep_id}")
                st.balloons()
                # Opcional: Redirecionar para a página de listagem ou edição da REP
                # st.session_state["page"] = "listar_rep"
                # st.rerun()

            except ValueError as e:
                st.error(f"❌ Erro ao registrar REP: {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")

main()