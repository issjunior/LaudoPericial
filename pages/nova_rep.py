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
from services.template_service import listar_templates
from services.laudo_service import criar_laudo

SECTION_CSS = """
<style>
.rep-section-card {
    background: var(--background-color, #ffffff08);
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid var(--section-color, #1971c2);
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin: 1rem 0 0.75rem 0;
}
.rep-section-title {
    font-size: 1rem;
    font-weight: 700;
    margin: 0;
}
.rep-section-desc {
    font-size: 0.82rem;
    opacity: 0.72;
    margin: 0.2rem 0 0 0;
}
</style>
"""

def render_section_card(titulo: str, cor: str, descricao: str = ""):
    descricao_html = f'<p class="rep-section-desc">{descricao}</p>' if descricao else ""
    st.markdown(
        f'<div class="rep-section-card" style="--section-color: {cor};">'
        f'<p class="rep-section-title">{titulo}</p>'
        f"{descricao_html}"
        f"</div>",
        unsafe_allow_html=True,
    )

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
st.markdown(SECTION_CSS, unsafe_allow_html=True)

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
    nomes_tipos_exame = ["— Não definido —"] + sorted(list(opcoes_tipos_exame.keys()))

    opcoes_solicitantes = {s['orgao']: s['id'] for s in solicitantes}
    nomes_solicitantes = ["Selecione um Solicitante"] + sorted(list(opcoes_solicitantes.keys()))


    # Estado para controlar a exibição dos campos de local
    if "exame_de_local_selecionado" not in st.session_state:
        st.session_state["exame_de_local_selecionado"] = False

    # Callback para preencher a autoridade automaticamente
    def on_change_solicitante():
        sel = st.session_state.get("solicitante_selecionado_key")
        if sel and sel != "Selecione um Solicitante":
            sol_data = next((s for s in solicitantes if s['orgao'] == sel), None)
            if sol_data and sol_data.get('nome'):
                st.session_state["nome_autoridade_key"] = sol_data['nome']

    render_section_card(
        "1) 📋 Dados da REP",
        "#1971c2",
        "Informações da requisição e dados essenciais para abertura."
    )
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        numero_rep = st.text_input(
            "Número da REP *",
            placeholder=f"Ex: 12.345-{date.today().year}",
            help="Número único de identificação da Requisição de Exame Pericial no formato XX.XXX-ANO."
        )
    with col2:
        data_solicitacao = st.date_input(
            "Data de recebimento de REP *",
            value=date.today(),
            format="DD/MM/YYYY",
            help="Data em que a REP foi recebida no setor."
        )
    with col3:
        tipo_exame_selecionado = st.selectbox(
            "Tipo de Exame *",
            options=nomes_tipos_exame,
            index=0,
            help="Selecione o tipo de exame pericial.",
            key="tipo_exame_key"
        )
        # Atualiza o estado para mostrar/esconder campos de local
        if tipo_exame_selecionado != "— Não definido —":
            tipo_exame_id_selecionado = opcoes_tipos_exame[tipo_exame_selecionado]
            exame_info = next((te for te in tipos_exame if te['id'] == tipo_exame_id_selecionado), None)
            if exame_info and exame_info['exame_de_local']:
                st.session_state["exame_de_local_selecionado"] = True
            else:
                st.session_state["exame_de_local_selecionado"] = False
        else:
            st.session_state["exame_de_local_selecionado"] = False

    # Template de laudo integrado ao bloco principal
    opcoes_templates_laudo = {}
    templates_filtrados = []
    template_laudo_selecionado = ""
    template_laudo_obj = None
    tipo_exame_definido = tipo_exame_selecionado != "— Não definido —"

    with col4:
        if not tipo_exame_definido:
            st.selectbox(
                "Template de Laudo",
                options=["Selecione um Tipo de Exame"],
                index=0,
                disabled=True,
                help="Com Tipo de Exame não definido, a REP fica Pendente e não cria laudo."
            )
        else:
            tipo_exame_id_para_template = opcoes_tipos_exame[tipo_exame_selecionado]
            templates_filtrados = listar_templates(
                apenas_ativos=True,
                tipo_exame_id=tipo_exame_id_para_template
            )

            if not templates_filtrados:
                st.selectbox(
                    "Template de Laudo",
                    options=["Nenhum template ativo para este tipo"],
                    index=0,
                    disabled=True
                )
            else:
                opcoes_templates_laudo = {
                    f"{t['tipo_exame_codigo']} — {t['nome']}": t['id']
                    for t in templates_filtrados
                }
                nomes_templates_laudo = ["— Não vincular agora —"] + list(opcoes_templates_laudo.keys())
                template_laudo_selecionado = st.selectbox(
                    "Template de Laudo",
                    options=nomes_templates_laudo,
                    index=0,
                    help="Somente templates compatíveis com o Tipo de Exame selecionado."
                )
                template_laudo_obj = next(
                    (t for t in templates_filtrados if f"{t['tipo_exame_codigo']} — {t['nome']}" == template_laudo_selecionado),
                    None
                )

    # NOVO CAMPO: Nome do Envolvido/Vítima
    nome_envolvido = st.text_input(
        "Nome do Envolvido / Vítima (Opcional)",
        placeholder="Ex: João da Silva, Vítima 01",
        help="Nome da pessoa envolvida ou vítima principal da ocorrência."
    )

    render_section_card(
        "2) 🏛️ Dados do Solicitante",
        "#2f9e44",
        "Informações sobre o órgão e a autoridade solicitante."
    )
    col4, col5 = st.columns(2)

    with col4:
        solicitante_selecionado = st.selectbox(
            "Órgão Solicitante *",
            options=nomes_solicitantes,
            index=0,
            help="Selecione o órgão ou pessoa que solicitou a perícia.",
            key="solicitante_selecionado_key",
            on_change=on_change_solicitante
        )
    with col5:
        nome_autoridade = st.text_input(
            "Nome da Autoridade Solicitante (Opcional)",
            placeholder="Ex: Delegado João da Silva",
            help="Nome da autoridade que assina o documento de solicitação.",
            key="nome_autoridade_key"
        )

    render_section_card(
        "3) 📝 Detalhes da Solicitação",
        "#e67700",
        "Dados do documento que originou a requisição."
    )
    col6, col7, col8 = st.columns(3)

    with col6:
        tipo_documento = st.selectbox(
            "Tipo de Documento *",
            options=["Selecione", "BO", "BO PM", "BO PC", "Ofício", "CECOMP", "Outro"],
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
            format="DD/MM/YYYY",
            help="Data de emissão do documento de solicitação."
        )

    render_section_card(
        "4) 📍 Dados da REP (Complementares)",
        "#1971c2",
        "Observações e dados de local, quando o tipo de exame exigir."
    )
    with st.expander("📝 Observações Adicionais", expanded=False):
        observacoes = st.text_area(
            "Observações Gerais (Opcional)",
            height=100,
            help="Qualquer informação extra relevante para a REP."
        )

    aba_geral, aba_local = st.tabs(["Dados Gerais", "Dados do Local"])

    with aba_geral:
        st.caption("Dados gerais complementares preenchidos acima.")

    with aba_local:
        exame_eh_de_local = st.session_state["exame_de_local_selecionado"]
        if not exame_eh_de_local:
            st.warning("📍 Os dados referentes ao local somente estarão disponíveis quando o tipo de exame for de local.")
        if exame_eh_de_local:
            local_fato_descricao_input = st.text_area(
                "Descrição do Local do Fato",
                placeholder="Ex: Residência na Rua X, nº Y, Bairro Z. Próximo ao mercado K.",
                help="Descrição objetiva do local onde ocorreu o fato.",
                height=80
            )
            col_horario1, col_horario2, col_horario3 = st.columns(3)
            with col_horario1:
                horario_acionamento_input = st.time_input(
                    "Horário de Acionamento",
                    value=None
                )
            with col_horario2:
                horario_chegada_input = st.time_input(
                    "Horário de Chegada",
                    value=None
                )
            with col_horario3:
                horario_saida_input = st.time_input(
                    "Horário de Saída",
                    value=None
                )

            col_coords1, col_coords2 = st.columns(2)
            with col_coords1:
                latitude_input = st.text_input(
                    "Latitude",
                    placeholder="Ex: -25.4284"
                )
            with col_coords2:
                longitude_input = st.text_input(
                    "Longitude",
                    placeholder="Ex: -49.2733"
                )

            local_fato_descricao = local_fato_descricao_input
            horario_acionamento = horario_acionamento_input
            horario_chegada = horario_chegada_input
            horario_saida = horario_saida_input
            latitude = latitude_input
            longitude = longitude_input
        else:
            local_fato_descricao = None
            horario_acionamento = None
            horario_chegada = None
            horario_saida = None
            latitude = None
            longitude = None

    st.markdown("### Resumo")
    with st.container(border=True):
        st.markdown(f"**REP:** {numero_rep or '—'}")
        st.markdown(f"**Tipo de Exame:** {tipo_exame_selecionado}")
        if tipo_exame_definido:
            st.markdown(f"**Template de Laudo:** {template_laudo_selecionado or 'Selecione um Template'}")
        else:
            st.markdown("**Template de Laudo:** desabilitado (Tipo de Exame não definido)")
        st.markdown(f"**Solicitante:** {solicitante_selecionado}")
        st.markdown(f"**Documento:** {tipo_documento} - {numero_documento or '—'}")

    st.markdown("---")

    col_submit, _ = st.columns([2, 4])

    with col_submit:
        criar_laudo_no_fluxo = tipo_exame_definido and template_laudo_selecionado in opcoes_templates_laudo
        label_botao = "💾 Registrar REP e Criar Laudo" if criar_laudo_no_fluxo else "💾 Registrar REP"
        submitted = st.button(
            label_botao,
            use_container_width=True,
            type="primary"
        )

    # ── VALIDAÇÃO E EXECUÇÃO (Fora das colunas para usar largura total) ──
    if submitted:
        erros_validacao = []

        if not numero_rep:
            erros_validacao.append("O campo **Número da REP** é obrigatório.")

        if solicitante_selecionado == "Selecione um Solicitante":
            erros_validacao.append("Você precisa selecionar um **Órgão Solicitante**.")

        if tipo_documento == "Selecione":
            erros_validacao.append("O **Tipo de Documento** (ex: BO, Ofício) deve ser informado.")

        if not numero_documento:
            erros_validacao.append("O **Número do Documento** é obrigatório para o registro.")

        # Validação de data
        if data_documento and data_solicitacao < data_documento:
            data_rec_str = data_solicitacao.strftime('%d/%m/%Y')
            data_doc_str = data_documento.strftime('%d/%m/%Y')
            erros_validacao.append(f"A **Data de recebimento** ({data_rec_str}) não pode ser anterior à **Data do Documento** ({data_doc_str}).")

        if erros_validacao:
            st.session_state["erros_temp"] = erros_validacao
            st.rerun()

        # Se passou na validação, prossegue com o cadastro
        tipo_exame_id = opcoes_tipos_exame[tipo_exame_selecionado] if tipo_exame_selecionado != "— Não definido —" else None
        solicitante_id = opcoes_solicitantes[solicitante_selecionado]

        # ... (resto do código de salvamento)
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
                nome_envolvido      = nome_envolvido,
                local_fato_descricao= local_fato_descricao,
                tipo_exame_id       = tipo_exame_id,
                latitude            = latitude,
                longitude           = longitude,
                observacoes         = observacoes,
                usuario_id          = usuario_logado['id']
            )
            if tipo_exame_definido and template_laudo_selecionado in opcoes_templates_laudo:
                try:
                    template_laudo_id = opcoes_templates_laudo[template_laudo_selecionado]
                    laudo_id = criar_laudo(nova_rep_id, template_laudo_id)
                    st.success(f"✅ REP **{numero_rep}** registrada e Laudo **#{laudo_id}** criado com sucesso!")
                    st.toast(f"REP {numero_rep} registrada e laudo #{laudo_id} criado.", icon="✅")
                    st.info("Próximo passo:")
                    st.page_link("pages/editor_laudo.py", label="Ir para Editor de Laudo", use_container_width=True)
                    st.page_link("pages/nova_rep.py", label="Registrar outra REP", use_container_width=True)
                except Exception as e_laudo:
                    st.warning(
                        f"⚠️ REP **{numero_rep}** registrada com sucesso, mas houve erro ao criar o laudo automaticamente: {e_laudo}"
                    )
                    st.toast(f"REP {numero_rep} registrada; houve falha ao criar o laudo automático.", icon="⚠️")
                    st.info("Você pode criar o laudo depois na página **Vincular Laudo a REP**.")
                    st.page_link("pages/novo_laudo.py", label="Ir para Vincular Laudo a REP", use_container_width=True)
            else:
                st.success(f"✅ REP **{numero_rep}** registrada com sucesso!")
                st.toast(f"REP {numero_rep} registrada com status Pendente.", icon="✅")
                st.page_link("pages/nova_rep.py", label="Registrar outra REP", use_container_width=True)
        except Exception as e:
            st.error(f"❌ Erro ao registrar REP: {e}")

    # Exibe erros de validação (se houver) em largura total
    if "erros_temp" in st.session_state:
        st.error("### ⚠️ Verifique o preenchimento:\n\n" + "\n".join([f"- {e}" for e in st.session_state["erros_temp"]]))
        del st.session_state["erros_temp"]

main()
