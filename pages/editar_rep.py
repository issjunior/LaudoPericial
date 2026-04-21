# pages/editar_rep.py
"""
pages/editar_rep.py
─────────────────────────────────────────────────────
Página para edição de uma Requisição de Exame Pericial (REP) existente.
─────────────────────────────────────────────────────
"""

import sys
import os
import streamlit as st
from datetime import date, datetime

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu
from core.auth import obter_usuario_logado
from services.cadastro_service import listar_tipos_exame, listar_solicitantes
from services.rep_service import buscar_rep, atualizar_rep, listar_reps, excluir_rep, verificar_laudo_vinculado

st.set_page_config(
    page_title="Editar REP — LaudoPericial",
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
    st.title("✏️ Editar Requisição de Exame Pericial (REP)")
    st.markdown("---")

    if "rep_selecionado_id" not in st.session_state:
        st.session_state["rep_selecionado_id"] = None

    col_busca1, col_busca2 = st.columns([3, 1])
    with col_busca1:
        Todas_REPs = listar_reps()
        
        opcoes_rep = {f"{r['numero_rep']} - {r.get('tipo_exame_nome') or 'Tipo não definido'} ({r['status']})": r['id'] for r in Todas_REPs}
        nomes_rep = ["Selecione uma REP"] + sorted(list(opcoes_rep.keys()))
        
        rep_selecionado = st.selectbox(
            "Digite ou selecione a REP:",
            options=nomes_rep,
            index=0,
            key="rep_select",
            help="Digite o número da REP para filtrar automaticamente"
        )
    
    with col_busca2:
        st.write("")
        st.write("")
        if st.button("🔄 Atualizar", use_container_width=True):
            st.rerun()

    if rep_selecionado == "Selecione uma REP":
        st.info("Selecione uma REP acima para editar seus dados.")
        st.session_state["rep_selecionado_id"] = None
        st.stop()

    rep_id = opcoes_rep[rep_selecionado]
    st.session_state["rep_selecionado_id"] = rep_id

    rep = buscar_rep(rep_id)
    if not rep:
        st.error("REP não encontrada.")
        st.stop()

    st.markdown(f"**REP:** {rep['numero_rep']} | **Status:** {rep['status']}")
    st.markdown("---")

    tipos_exame = listar_tipos_exame(apenas_ativos=True)
    solicitantes = listar_solicitantes(apenas_ativos=True)

    opcoes_tipos_exame = {f"{te['codigo']} - {te['nome']}": te['id'] for te in tipos_exame}
    nomes_tipos_exame = ["— Não definido —"] + sorted(list(opcoes_tipos_exame.keys()))

    opcoes_solicitantes = {f"{s['orgao']} ({s['nome'] or 'N/A'})": s['id'] for s in solicitantes}
    nomes_solicitantes = ["Selecione um Solicitante"] + sorted(list(opcoes_solicitantes.keys()))

    TIPO_SOLICITACAO = ["BO", "BO PM", "BO PC", "Ofício", "CECOMP", "Outro"]
    STATUS_REP = ["Pendente", "Em Andamento", "Concluído"]

    tipo_exame_atual = next((k for k, v in opcoes_tipos_exame.items() if v == rep.get('tipo_exame_id')), "— Não definido —")
    solicitante_atual = next((k for k, v in opcoes_solicitantes.items() if v == rep.get('solicitante_id')), "Selecione um Solicitante")

    if "exame_de_local_selecionado" not in st.session_state:
        st.session_state["exame_de_local_selecionado"] = bool(rep.get('exame_de_local'))

    with st.form("form_editar_rep"):
        st.markdown("### Dados Gerais da REP")
        col1, col2, col3 = st.columns(3)

        with col1:
            numero_rep = st.text_input(
                "Número da REP *",
                value=rep.get('numero_rep', '')
            )
        with col2:
            data_solicitacao = st.date_input(
                "Data da Solicitação *",
                value=datetime.strptime(rep['data_solicitacao'], '%Y-%m-%d').date() if rep.get('data_solicitacao') else date.today()
            )
        with col3:
            tipo_exame_selecionado = st.selectbox(
                "Tipo de Exame *",
                options=nomes_tipos_exame,
                index=nomes_tipos_exame.index(tipo_exame_atual) if tipo_exame_atual in nomes_tipos_exame else 0
            )

        nome_envolvido = st.text_input(
            "Nome do Envolvido / Vítima (Opcional)",
            value=rep.get('nome_envolvido') or ''
        )

        st.markdown("### Dados do Solicitante")
        col4, col5 = st.columns(2)

        with col4:
            solicitante_selecionado = st.selectbox(
                "Órgão Solicitante",
                options=nomes_solicitantes,
                index=nomes_solicitantes.index(solicitante_atual) if solicitante_atual in nomes_solicitantes else 0
            )
        with col5:
            nome_autoridade = st.text_input(
                "Nome da Autoridade Solicitante (Opcional)",
                value=rep.get('nome_autoridade') or ''
            )

        st.markdown("### Detalhes da Solicitação")
        col6, col7, col8 = st.columns(3)

        tipo_solicitacao_atual = rep.get('tipo_solicitacao', 'BO')
        with col6:
            tipo_documento = st.selectbox(
                "Tipo de Documento *",
                options=TIPO_SOLICITACAO,
                index=TIPO_SOLICITACAO.index(tipo_solicitacao_atual) if tipo_solicitacao_atual in TIPO_SOLICITACAO else 0
            )
        with col7:
            numero_documento = st.text_input(
                "Número do Documento *",
                value=rep.get('numero_documento') or ''
            )
        with col8:
            data_documento_val = None
            if rep.get('data_documento'):
                try:
                    data_documento_val = datetime.strptime(rep['data_documento'], '%Y-%m-%d').date()
                except:
                    pass
            data_documento = st.date_input(
                "Data do Documento (Opcional)",
                value=data_documento_val
            )

        if st.session_state["exame_de_local_selecionado"]:
            with st.expander("🌍 Dados do Local de Exame", expanded=True):
                local_fato_descricao = st.text_area(
                    "Descrição do Local do Fato (Opcional)",
                    value=rep.get('local_fato_descricao') or ''
                )
                col_horario1, col_horario2, col_horario3 = st.columns(3)

                h_acionamento = None
                if rep.get('horario_acionamento'):
                    try:
                        h_acionamento = datetime.strptime(rep['horario_acionamento'], '%H:%M').time()
                    except:
                        pass

                h_chegada = None
                if rep.get('horario_chegada'):
                    try:
                        h_chegada = datetime.strptime(rep['horario_chegada'], '%H:%M').time()
                    except:
                        pass

                h_saida = None
                if rep.get('horario_saida'):
                    try:
                        h_saida = datetime.strptime(rep['horario_saida'], '%H:%M').time()
                    except:
                        pass

                with col_horario1:
                    horario_acionamento = st.time_input(
                        "Horário de Acionamento (Opcional)",
                        value=h_acionamento
                    )
                with col_horario2:
                    horario_chegada = st.time_input(
                        "Horário de Chegada ao Local (Opcional)",
                        value=h_chegada
                    )
                with col_horario3:
                    horario_saida = st.time_input(
                        "Horário de Saída do Local (Opcional)",
                        value=h_saida
                    )

                col_coords1, col_coords2 = st.columns(2)
                with col_coords1:
                    latitude = st.text_input(
                        "Latitude (Opcional)",
                        value=rep.get('latitude') or ''
                    )
                with col_coords2:
                    longitude = st.text_input(
                        "Longitude (Opcional)",
                        value=rep.get('longitude') or ''
                    )
        else:
            local_fato_descricao = rep.get('local_fato_descricao')
            horario_acionamento = None
            horario_chegada = None
            horario_saida = None
            latitude = rep.get('latitude')
            longitude = rep.get('longitude')

        st.markdown("### Observações")
        observacoes = st.text_area(
            "Observações Gerais (Opcional)",
            value=rep.get('observacoes') or ''
        )

        st.markdown(f"**Status:** {rep['status']} *(atualizado automaticamente via laudo)*")

        st.markdown("---")
        col_submit = st.columns([1])

        with col_submit[0]:
            submitted = st.form_submit_button(
                "💾 Salvar Alterações",
                use_container_width=True,
                type="primary"
            )

        if submitted:
            if not numero_rep:
                st.error("❌ O número da REP é obrigatório.")
                st.stop()
            if tipo_exame_selecionado == "Selecione um Tipo de Exame":
                st.error("❌ Por favor, selecione um Tipo de Exame.")
                st.stop()
            if tipo_documento not in TIPO_SOLICITACAO:
                st.error("❌ Por favor, selecione o Tipo de Documento.")
                st.stop()
            if not numero_documento:
                st.error("❌ O número do documento é obrigatório.")
                st.stop()

            tipo_exame_id = opcoes_tipos_exame[tipo_exame_selecionado] if tipo_exame_selecionado != "— Não definido —" else None
            solicitante_id = opcoes_solicitantes[solicitante_selecionado] if solicitante_selecionado != "Selecione um Solicitante" else None

            data_solicitacao_str = data_solicitacao.strftime("%Y-%m-%d")
            data_documento_str = data_documento.strftime("%Y-%m-%d") if data_documento else None
            horario_acionamento_str = horario_acionamento.strftime("%H:%M") if horario_acionamento else None
            horario_chegada_str = horario_chegada.strftime("%H:%M") if horario_chegada else None
            horario_saida_str = horario_saida.strftime("%H:%M") if horario_saida else None

            try:
                atualizar_rep(
                    rep_id              = rep_id,
                    numero_rep          = numero_rep,
                    data_solicitacao    = data_solicitacao_str,
                    tipo_solicitacao    = tipo_documento,
                    numero_documento    = numero_documento,
                    tipo_exame_id       = tipo_exame_id,
                    usuario_id          = usuario_logado['id'],
                    horario_acionamento = horario_acionamento_str,
                    horario_chegada     = horario_chegada_str,
                    horario_saida       = horario_saida_str,
                    data_documento      = data_documento_str,
                    solicitante_id      = solicitante_id,
                    nome_autoridade     = nome_autoridade,
                    nome_envolvido      = nome_envolvido,
                    local_fato_descricao= local_fato_descricao,
                    latitude            = latitude,
                    longitude           = longitude,
                    status              = rep['status'],
                    observacoes         = observacoes,
                )
                st.success(f"✅ REP **{numero_rep}** atualizada com sucesso!")
                st.rerun()

            except ValueError as e:
                st.error(f"❌ Erro ao atualizar REP: {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")

    with st.expander("🗑️ Excluir REP", expanded=False):
        st.warning(f"Tem certeza que deseja excluir a REP **{rep.get('numero_rep')}**?")

        laudo = verificar_laudo_vinculado(rep_id)
        if laudo:
            st.error("⚠️ AVISO: Esta REP tem um laudo vinculado que será excluído junto!")
            st.caption(f"Laudo ID: {laudo['id']} | Status: {laudo['status']}")

            col_confirma, _ = st.columns([1, 2])
            with col_confirma:
                confirmar = st.checkbox("Entendo o risco, quero excluir mesmo assim")

            if confirmar and st.button("🗑️ Confirmar Exclusão", type="primary"):
                try:
                    excluir_rep(rep_id, forcar_exclusao=True)
                    st.success("✅ REP excluída com sucesso!")
                    st.session_state["rep_selecionado_id"] = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao excluir: {e}")
        else:
            if st.button("🗑️ Confirmar Exclusão", type="primary"):
                try:
                    excluir_rep(rep_id)
                    st.success("✅ REP excluída com sucesso!")
                    st.session_state["rep_selecionado_id"] = None
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao excluir: {e}")

main()