# pages/historico.py
"""
pages/historico.py
------------------------------------------------------
Página de histórico do sistema.
Mostra linha do tempo com todas as operações de auditoria
desde criação da REP até conclusão/entrega do laudo.
------------------------------------------------------
"""

import sys
import os
import json
import streamlit as st
from datetime import datetime, timedelta

# Garante que a raiz do projeto está no sys.path
ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu
from core.auth import obter_usuario_logado, exigir_autenticacao
from core.audit import buscar_historico_geral, formatar_operacao

# ------------------------------------------------------─
# CONFIGURAÇÃO DA PÁGINA
# ------------------------------------------------------─
st.set_page_config(
    page_title="Histórico — LaudoPericial",
    page_icon="📜",
    layout="wide",
)

# Defina a página atual na sessão para o menu funcionar corretamente
st.session_state["_active_page"] = __file__

# Renderiza o menu lateral (já exige autenticação)
renderizar_menu()

# ------------------------------------------------------─
# FUNÇÕES AUXILIARES
# ------------------------------------------------------─

def obter_descricao_tabela(tabela: str) -> str:
    """Retorna nome amigável para cada tabela."""
    mapa = {
        "rep": "REP",
        "laudos": "Laudo",
        "templates": "Template",
        "tipos_exame": "Tipo de Exame",
        "solicitantes": "Solicitante",
        "usuarios": "Usuário",
        "secoes_template": "Seção de Template",
        "secoes_laudo": "Seção de Laudo",
        "versoes_laudo": "Versão de Laudo",
        "modelo_cabecalho": "Modelo de Cabeçalho",
        "ilustracoes": "Ilustração",
    }
    return mapa.get(tabela, tabela)

def formatar_data(data_str: str) -> str:
    """Formata data para exibição amigável."""
    try:
        dt = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return data_str

def formatar_dados_anteriores(dados_json: str) -> str:
    """Formata dados anteriores em JSON para exibição legível."""
    if not dados_json:
        return ""
    try:
        dados = json.loads(dados_json)
        return json.dumps(dados, indent=2, ensure_ascii=False)
    except:
        return dados_json

def criar_link_registro(tabela: str, registro_id: int) -> str:
    """Cria texto de link para registro baseado na tabela."""
    desc_tabela = obter_descricao_tabela(tabela)
    return f"**{desc_tabela} #{registro_id}**"

# ------------------------------------------------------─
# INTERFACE PRINCIPAL
# ------------------------------------------------------─

st.title("📜 Histórico do Sistema")

st.markdown("""
**Linha do tempo completa** de todas as operações no sistema, desde a criação de uma REP
até a conclusão ou entrega do laudo.
""")

# ------------------------------------------------------─
# SEÇÃO DE FILTROS
# ------------------------------------------------------─

st.subheader("🔍 Filtros")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Filtro por tabela
    tabelas = [
        "", "rep", "laudos", "templates", "tipos_exame",
        "solicitantes", "usuarios", "secoes_template",
        "secoes_laudo", "versoes_laudo"
    ]
    tabela_filtro = st.selectbox(
        "Tabela",
        tabelas,
        format_func=lambda x: "Todas as tabelas" if x == "" else obter_descricao_tabela(x)
    )

with col2:
    # Filtro por operação
    operacoes = [
        "", "CRIAR", "EDITAR", "EXCLUIR", "FINALIZAR",
        "LOGIN", "LOGOUT"
    ]
    operacao_filtro = st.selectbox(
        "Operação",
        operacoes,
        format_func=lambda x: "Todas as operações" if x == "" else formatar_operacao(x)
    )

with col3:
    # Filtro por período
    periodo_opcoes = [
        "Últimos 7 dias",
        "Últimos 30 dias",
        "Últimos 90 dias",
        "Personalizado",
        "Todo o período"
    ]
    periodo_selecionado = st.selectbox("Período", periodo_opcoes)

with col4:
    # Limite de registros
    limite_registros = st.number_input(
        "Limite de registros",
        min_value=10,
        max_value=1000,
        value=100,
        step=10
    )

# Campos para período personalizado (apenas se selecionado)
data_ini = None
data_fim = None

if periodo_selecionado == "Personalizado":
    col_a, col_b = st.columns(2)
    with col_a:
        data_ini = st.date_input("Data inicial", value=datetime.now() - timedelta(days=30))
    with col_b:
        data_fim = st.date_input("Data final", value=datetime.now())
elif periodo_selecionado == "Últimos 7 dias":
    data_ini = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
elif periodo_selecionado == "Últimos 30 dias":
    data_ini = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
elif periodo_selecionado == "Últimos 90 dias":
    data_ini = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

# Converter datas para string se necessário
if data_ini and hasattr(data_ini, "strftime"):
    data_ini = data_ini.strftime("%Y-%m-%d")
if data_fim and hasattr(data_fim, "strftime"):
    data_fim = data_fim.strftime("%Y-%m-%d")

# ------------------------------------------------------─
# BOTÃO DE APLICAÇÃO DOS FILTROS
# ------------------------------------------------------─

if st.button("🔍 Aplicar Filtros", type="primary"):
    st.session_state["filtros_aplicados"] = True
    st.session_state["filtro_tabela"] = tabela_filtro if tabela_filtro else None
    st.session_state["filtro_operacao"] = operacao_filtro if operacao_filtro else None
    st.session_state["filtro_data_ini"] = data_ini
    st.session_state["filtro_data_fim"] = data_fim
    st.session_state["filtro_limite"] = limite_registros
    st.rerun()

# Inicializa filtros na sessão se não existirem
if "filtros_aplicados" not in st.session_state:
    st.session_state["filtros_aplicados"] = False
    st.session_state["filtro_tabela"] = None
    st.session_state["filtro_operacao"] = None
    st.session_state["filtro_data_ini"] = None
    st.session_state["filtro_data_fim"] = None
    st.session_state["filtro_limite"] = 100

# ------------------------------------------------------─
# EXIBIÇÃO DO HISTÓRICO
# ------------------------------------------------------─

st.divider()
st.subheader("📋 Histórico de Auditoria")

if st.session_state["filtros_aplicados"]:
    # Busca histórico com filtros aplicados
    historico = buscar_historico_geral(
        limite=st.session_state["filtro_limite"],
        operacao=st.session_state["filtro_operacao"],
        tabela=st.session_state["filtro_tabela"],
        data_ini=st.session_state["filtro_data_ini"],
        data_fim=st.session_state["filtro_data_fim"]
    )

    if not historico:
        st.info("Nenhum registro encontrado com os filtros aplicados.")
    else:
        # Exibe contagem de resultados
        st.success(f"📊 **{len(historico)} registros encontrados**")

        # ------------------------------------------------------─
        # VISUALIZAÇÃO EM TIMELINE
        # ------------------------------------------------------─

        st.markdown("### 📅 Linha do Tempo")

        # Agrupa por data
        eventos_por_data = {}
        for evento in historico:
            data_evento = evento["criado_em"][:10]  # YYYY-MM-DD
            if data_evento not in eventos_por_data:
                eventos_por_data[data_evento] = []
            eventos_por_data[data_evento].append(evento)

        # Ordena datas (mais recente primeiro)
        datas_ordenadas = sorted(eventos_por_data.keys(), reverse=True)

        # Exibe timeline
        for data_str in datas_ordenadas:
            eventos_dia = eventos_por_data[data_str]

            # Formata data para exibição
            data_dt = datetime.strptime(data_str, "%Y-%m-%d")
            data_formatada = data_dt.strftime("%d/%m/%Y")
            dia_semana = data_dt.strftime("%A")

            with st.expander(f"**📅 {data_formatada} ({dia_semana})** - {len(eventos_dia)} eventos"):
                for evento in eventos_dia:
                    # Cria colunas para cada evento
                    col_icon, col_content = st.columns([1, 20])

                    with col_icon:
                        # Ícone baseado na operação
                        operacao = evento["operacao"]
                        if operacao == "CRIAR":
                            st.markdown("🟢")
                        elif operacao == "EDITAR":
                            st.markdown("🔵")
                        elif operacao == "EXCLUIR":
                            st.markdown("🔴")
                        elif operacao == "FINALIZAR":
                            st.markdown("✅")
                        elif operacao == "LOGIN":
                            st.markdown("🔑")
                        elif operacao == "LOGOUT":
                            st.markdown("🚪")
                        else:
                            st.markdown("⚪")

                    with col_content:
                        # Formata hora
                        hora = evento["criado_em"][11:16]

                        # Informações principais
                        operacao_formatada = formatar_operacao(evento["operacao"])
                        tabela_formatada = obter_descricao_tabela(evento["tabela"])
                        registro_link = criar_link_registro(evento["tabela"], evento["registro_id"])

                        # Usuário
                        usuario_info = ""
                        if evento.get("usuario_nome"):
                            matricula = evento.get("usuario_matricula", "")
                            usuario_info = f"por **{evento['usuario_nome']}**"
                            if matricula:
                                usuario_info += f" ({matricula})"

                        # Monta linha do tempo
                        linha = f"**{hora}** · {operacao_formatada} {registro_link} "
                        linha += f"({tabela_formatada}) {usuario_info}"

                        st.markdown(linha)

                        # Descrição adicional
                        if evento.get("descricao"):
                            st.caption(f"_{evento['descricao']}_")

                        # Dados anteriores (se houver)
                        if evento.get("dados_anteriores"):
                            with st.expander("📋 Dados anteriores"):
                                st.code(formatar_dados_anteriores(evento["dados_anteriores"]), language="json")

        # ------------------------------------------------------─
        # VISUALIZAÇÃO EM TABELA DETALHADA
        # ------------------------------------------------------─

        st.markdown("### 📋 Visão Detalhada")

        # Prepara dados para tabela
        dados_tabela = []
        for evento in historico:
            dados_tabela.append({
                "Data/Hora": formatar_data(evento["criado_em"]),
                "Operação": formatar_operacao(evento["operacao"]),
                "Tabela": obter_descricao_tabela(evento["tabela"]),
                "Registro": f"{evento['tabela']}#{evento['registro_id']}",
                "Usuário": evento.get("usuario_nome", "N/A"),
                "Descrição": evento.get("descricao", "")[:50] + ("..." if len(evento.get("descricao", "")) > 50 else "")
            })

        # Exibe tabela
        st.dataframe(
            dados_tabela,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Data/Hora": st.column_config.TextColumn(width="medium"),
                "Operação": st.column_config.TextColumn(width="small"),
                "Tabela": st.column_config.TextColumn(width="medium"),
                "Registro": st.column_config.TextColumn(width="small"),
                "Usuário": st.column_config.TextColumn(width="medium"),
                "Descrição": st.column_config.TextColumn(width="large"),
            }
        )

        # ------------------------------------------------------─
        # ESTATÍSTICAS
        # ------------------------------------------------------─

        st.markdown("### 📊 Estatísticas")

        col_stat1, col_stat2, col_stat3 = st.columns(3)

        # Conta operações por tipo
        contagem_operacoes = {}
        contagem_tabelas = {}
        usuarios_unicos = set()

        for evento in historico:
            # Contagem por operação
            op = evento["operacao"]
            contagem_operacoes[op] = contagem_operacoes.get(op, 0) + 1

            # Contagem por tabela
            tab = evento["tabela"]
            contagem_tabelas[tab] = contagem_tabelas.get(tab, 0) + 1

            # Usuários únicos
            if evento.get("usuario_nome"):
                usuarios_unicos.add(evento["usuario_nome"])

        with col_stat1:
            st.metric("Total de Eventos", len(historico))

        with col_stat2:
            # Operação mais comum
            if contagem_operacoes:
                op_mais_comum = max(contagem_operacoes, key=contagem_operacoes.get)
                st.metric(
                    "Operação Mais Frequente",
                    formatar_operacao(op_mais_comum),
                    delta=f"{contagem_operacoes[op_mais_comum]} ocorrências"
                )

        with col_stat3:
            st.metric("Usuários Envolvidos", len(usuarios_unicos))

        # Tabela mais afetada
        if contagem_tabelas:
            tab_mais_comum = max(contagem_tabelas, key=contagem_tabelas.get)
            st.info(
                f"📌 **Tabela mais ativa:** {obter_descricao_tabela(tab_mais_comum)} "
                f"({contagem_tabelas[tab_mais_comum]} eventos)"
            )

else:
    st.info("👆 Configure os filtros acima e clique em **'Aplicar Filtros'** para visualizar o histórico.")

# ------------------------------------------------------─
# BOTÃO PARA LIMPAR FILTROS
# ------------------------------------------------------─

if st.session_state["filtros_aplicados"]:
    if st.button("🧹 Limpar Filtros"):
        for key in ["filtros_aplicados", "filtro_tabela", "filtro_operacao",
                   "filtro_data_ini", "filtro_data_fim", "filtro_limite"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ------------------------------------------------------─
# RODAPÉ INFORMATIVO
# ------------------------------------------------------─

st.divider()
st.caption("""
**Sobre o histórico:** Esta página mostra o rastreamento completo de todas as operações no sistema.
Cada ação é registrada automaticamente com data/hora, usuário responsável e detalhes da operação.
""")
