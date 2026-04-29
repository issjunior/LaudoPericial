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

    opcoes_solicitantes = {s['orgao']: s['id'] for s in solicitantes}
    nomes_solicitantes = ["Selecione um Solicitante"] + sorted(list(opcoes_solicitantes.keys()))

    TIPO_SOLICITACAO = ["BO", "BO PM", "BO PC", "Oficio", "CECOMP", "Outro"]
    STATUS_REP = ["Pendente", "Em Andamento", "Concluido"]

    tipo_exame_atual = next((k for k, v in opcoes_tipos_exame.items() if v == rep.get('tipo_exame_id')), "— Não definido —")
    solicitante_atual = next((k for k, v in opcoes_solicitantes.items() if v == rep.get('solicitante_id')), "Selecione um Solicitante")

    # Estado para controlar a exibição dos campos de local
    if "exame_de_local_selecionado" not in st.session_state:
        st.session_state["exame_de_local_selecionado"] = bool(rep.get('exame_de_local'))

    # Callback para preencher a autoridade automaticamente
    def on_change_solicitante():
        sel = st.session_state.get("solicitante_selecionado_key")
        if sel and sel != "Selecione um Solicitante":
            sol_data = next((s for s in solicitantes if s['orgao'] == sel), None)
            if sol_data and sol_data.get('nome'):
                st.session_state["nome_autoridade_key"] = sol_data['nome']

    st.markdown("### Dados Gerais da REP")
    col1, col2, col3 = st.columns(3)

    with col1:
        numero_rep = st.text_input(
            "Número da REP *",
            value=rep.get('numero_rep', ''),
            key="numero_rep_key"
        )
    with col2:
        data_solicitacao = st.date_input(
            "Data de recebimento de REP *",
            value=datetime.strptime(rep['data_solicitacao'], '%Y-%m-%d').date() if rep.get('data_solicitacao') else date.today(),
            format="DD/MM/YYYY",
            key="data_solicitacao_key"
        )
    with col3:
        tipo_exame_selecionado = st.selectbox(
            "Tipo de Exame *",
            options=nomes_tipos_exame,
            index=nomes_tipos_exame.index(tipo_exame_atual) if tipo_exame_atual in nomes_tipos_exame else 0,
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

    nome_envolvido = st.text_input(
        "Nome do Envolvido / Vítima (Opcional)",
        value=rep.get('nome_envolvido') or '',
        key="nome_envolvido_key"
    )

    st.markdown("### Dados do Solicitante")
    col4, col5 = st.columns(2)

    with col4:
        solicitante_selecionado = st.selectbox(
            "Órgão Solicitante",
            options=nomes_solicitantes,
            index=nomes_solicitantes.index(solicitante_atual) if solicitante_atual in nomes_solicitantes else 0,
            key="solicitante_selecionado_key",
            on_change=on_change_solicitante
        )
    with col5:
        # Inicializa o valor da autoridade na primeira carga se ainda não houver na sessão
        if "nome_autoridade_key" not in st.session_state:
            st.session_state["nome_autoridade_key"] = rep.get('nome_autoridade') or ''
        
        nome_autoridade = st.text_input(
            "Nome da Autoridade Solicitante (Opcional)",
            key="nome_autoridade_key"
        )

    st.markdown("### Detalhes da Solicitação")
    col6, col7, col8 = st.columns(3)

    tipo_solicitacao_atual = rep.get('tipo_solicitacao', 'BO')
    with col6:
        tipo_documento = st.selectbox(
            "Tipo de Documento *",
            options=TIPO_SOLICITACAO,
            index=TIPO_SOLICITACAO.index(tipo_solicitacao_atual) if tipo_solicitacao_atual in TIPO_SOLICITACAO else 0,
            key="tipo_documento_key"
        )
    with col7:
        numero_documento = st.text_input(
            "Número do Documento *",
            value=rep.get('numero_documento') or '',
            key="numero_documento_key"
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
            value=data_documento_val,
            format="DD/MM/YYYY",
            key="data_documento_key"
        )

    if st.session_state["exame_de_local_selecionado"]:
        with st.expander("🌍 Dados do Local de Exame", expanded=True):
            local_fato_descricao = st.text_area(
                "Descrição do Local do Fato (Opcional)",
                value=rep.get('local_fato_descricao') or '',
                key="local_fato_key"
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
                    value=h_acionamento,
                    key="h_acionamento_key"
                )
            with col_horario2:
                horario_chegada = st.time_input(
                    "Horário de Chegada ao Local (Opcional)",
                    value=h_chegada,
                    key="h_chegada_key"
                )
            with col_horario3:
                horario_saida = st.time_input(
                    "Horário de Saída do Local (Opcional)",
                    value=h_saida,
                    key="h_saida_key"
                )

            col_coords1, col_coords2 = st.columns(2)
            with col_coords1:
                latitude = st.text_input(
                    "Latitude (Opcional)",
                    value=rep.get('latitude') or '',
                    key="latitude_key"
                )
            with col_coords2:
                longitude = st.text_input(
                    "Longitude (Opcional)",
                    value=rep.get('longitude') or '',
                    key="longitude_key"
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
        value=rep.get('observacoes') or '',
        key="observacoes_key"
    )

    st.markdown(f"**Status:** {rep['status']} *(atualizado automaticamente via laudo)*")

    st.markdown("---")
    col_submit = st.columns([1])

    with col_submit[0]:
        submitted = st.button(
            "💾 Salvar Alterações",
            use_container_width=True,
            type="primary"
        )

    # ── VALIDAÇÃO E EXECUÇÃO (Fora das colunas para usar largura total) ──
    if submitted:
        erros_validacao = []

        if not numero_rep:
            erros_validacao.append("O campo **Número da REP** é obrigatório.")

        if tipo_exame_selecionado == "Selecione um Tipo de Exame":
            erros_validacao.append("Por favor, selecione um **Tipo de Exame** válido.")

        if tipo_documento not in TIPO_SOLICITACAO:
            erros_validacao.append("O **Tipo de Documento** deve ser selecionado.")

        if not numero_documento:
            erros_validacao.append("O **Número do Documento** é obrigatório.")

        # Validação de data
        if data_documento and data_solicitacao < data_documento:
            data_rec_str = data_solicitacao.strftime('%d/%m/%Y')
            data_doc_str = data_documento.strftime('%d/%m/%Y')
            erros_validacao.append(f"A **Data de recebimento** ({data_rec_str}) não pode ser anterior à **Data do Documento** ({data_doc_str}).")

        if erros_validacao:
            st.session_state["erros_temp_edit"] = erros_validacao
            st.rerun()

        # Se passou na validação, prossegue
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

    # Exibe erros de validação (se houver) em largura total
    if "erros_temp_edit" in st.session_state:
        st.error("### ⚠️ Erro ao salvar alterações:\n\n" + "\n".join([f"- {e}" for e in st.session_state["erros_temp_edit"]]))
        del st.session_state["erros_temp_edit"]

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