# app.py
"""
app.py
──────────────────────────────────────────────────────
Ponto de entrada do sistema LaudoPericial PCP.
Controla o fluxo inicial: primeiro acesso ou login.
──────────────────────────────────────────────────────
"""
import sys
import os
import shutil

# Garante que a raiz do projeto está no sys.path
# Funciona localmente E no Streamlit Cloud
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st
from database.db import init_database, importar_banco_de_dados, executar_query
from core.auth import (
    usuario_existe,
    criar_usuario,
    fazer_login,
    fazer_logout,
    esta_autenticado,
    obter_usuario_logado,
    extrair_username
)
from datetime import date, timedelta

# ──────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# Deve ser o primeiro comando Streamlit do arquivo
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="PCP - Laudo",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────
# INICIALIZAÇÃO DO BANCO DE DADOS
# ──────────────────────────────────────────────────────
init_database()

# ──────────────────────────────────────────────────────
# ESTILOS CSS
# ──────────────────────────────────────────────────────
st.markdown("""
<style>
    #MainMenu  {visibility: hidden;}
    footer     {visibility: hidden;}

    .header-title {
        text-align: center;
        color: #1a3a5c;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.2rem;
    }
    .header-subtitle {
        text-align: center;
        color: #666;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
# FUNÇÕES DE TELA
# ──────────────────────────────────────────────────────

def tela_primeiro_acesso():
    """
    Exibida apenas na primeira vez que o sistema é executado.
    O usuário cadastra seus dados de perito e define a senha,
    ou importa um banco de dados existente.
    """
    st.markdown(
        "<h1 class='header-title'>🔍 Laudo Pericial</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p class='header-subtitle'>Polícia Científica do Paraná</p>",
        unsafe_allow_html=True
    )

    st.info(
        "👋 **Bem-vindo!** Esta é a primeira execução do sistema. "
        "Cadastre seus dados para começar ou importe um banco de dados existente."
    )

    st.markdown("---")

    # ----------------------------------------------------
    # Opção de Importar Banco de Dados
    # ----------------------------------------------------
    st.subheader("⬆️ Importar Banco de Dados Existente")
    uploaded_file = st.file_uploader(
        "Selecione um arquivo de banco de dados (.db)",
        type=["db"],
        help="Faça upload de um arquivo 'laudopericial.db' de um backup anterior para restaurar seus dados."
    )

    if uploaded_file is not None:
        if st.button("Restaurar Banco de Dados", type="secondary"):
            try:
                # Salva o arquivo temporariamente
                temp_db_path = os.path.join(ROOT, "temp_uploaded.db")
                with open(temp_db_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Importa o banco de dados
                importar_banco_de_dados(temp_db_path)

                st.success("✅ Banco de dados restaurado com sucesso! Redirecionando...")

                # Após importar, o banco pode ter usuários. Tenta logar o primeiro usuário ou ir para o login.
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erro ao restaurar o banco de dados: {e}")
            finally:
                if os.path.exists(temp_db_path):
                    os.remove(temp_db_path)
        st.markdown("---")

    # ----------------------------------------------------
    # Opção de Cadastro de Novo Usuário
    # ----------------------------------------------------
    st.subheader("⚙️ Configuração Inicial — Dados do Perito")

    with st.form("form_primeiro_acesso"):

        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input(
                "Nome Completo *",
                placeholder="Ex: Nome completo"
            )
            email = st.text_input(
                "E-mail Institucional *",
                placeholder="Ex: perito@policiacientifica.pr.gov.br"
            )
            matricula = st.text_input(
                "Matrícula",
                placeholder="Ex: 123456 (opcional)"
            )

        with col2:
            cargo = st.text_input(
                "Cargo *",
                value="Perito Oficial Criminal",
            )
            lotacao = st.text_input(
                "Lotação / Unidade *",
                placeholder="Ex: UETC - Telêmaco Borba"
            )

        # Prévia do username gerado automaticamente
        if email and "@" in email:
            username_preview = extrair_username(email.strip())
            st.info(
                f"👤 Seu nome de usuário para login será: "
                f"**`{username_preview}`**"
            )

        st.markdown("---")
        st.subheader("🔐 Defina sua Senha de Acesso")

        col3, col4 = st.columns(2)
        with col3:
            senha = st.text_input(
                "Senha *",
                type="password",
                placeholder="Mínimo 6 caracteres"
            )
        with col4:
            senha_confirm = st.text_input(
                "Confirmar Senha *",
                type="password",
                placeholder="Repita a senha"
            )

        st.markdown(" ")
        submitted = st.form_submit_button(
            "✅ Salvar e Entrar no Sistema",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            erros = []

            if not nome.strip():
                erros.append("Nome completo é obrigatório.")
            if not email.strip():
                erros.append("E-mail é obrigatório.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                erros.append("E-mail inválido.")
            if not cargo.strip():
                erros.append("Cargo é obrigatório.")
            if not lotacao.strip():
                erros.append("Lotação é obrigatória.")
            if not senha:
                erros.append("Senha é obrigatória.")
            elif len(senha) < 6:
                erros.append("A senha deve ter no mínimo 6 caracteres.")
            elif senha != senha_confirm:
                erros.append("As senhas não coincidem.")

            if erros:
                for erro in erros:
                    st.error(f"❌ {erro}")
            else:
                try:
                    criar_usuario(
                        nome      = nome.strip(),
                        cargo     = cargo.strip(),
                        matricula = matricula.strip(),
                        lotacao   = lotacao.strip(),
                        email     = email.strip().lower(),
                        senha     = senha,
                    )
                    st.success(
                        "✅ Cadastro realizado! "
                        "Redirecionando para o login..."
                    )
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Erro ao criar usuário: {e}")


def tela_login():
    """
    Tela de login — identificação por nome de usuário.
    """
    st.markdown(
        "<h1 class='header-title'>🔍 Laudo Pericial PCP</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p class='header-subtitle'>Polícia Científica do Paraná</p>",
        unsafe_allow_html=True
    )

    col_esq, col_centro, col_dir = st.columns([1, 1.2, 1])

    with col_centro:
        st.markdown("---")

        with st.form("form_login"):
            st.subheader("🔐 Acesso ao Sistema")

            username = st.text_input(
                "Usuário",
                placeholder="Ex: nome.sobrenome"
            )
            senha = st.text_input(
                "Senha",
                type="password",
                placeholder="Digite sua senha"
            )

            st.markdown(" ")
            submitted = st.form_submit_button(
                "Entrar →",
                use_container_width=True,
                type="primary"
            )

            if submitted:
                if not username or not senha:
                    st.error("❌ Preencha usuário e senha.")
                else:
                    if fazer_login(username.strip().lower(), senha):
                        st.success("✅ Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error(
                            "❌ Usuário ou senha incorretos. "
                            "Tente novamente."
                        )

        st.markdown("---")
        st.caption(
            "🔒 Sistema de uso restrito — "
            "Polícia Científica do Paraná"
        )

# Define as constantes de prazo fora da função para fácil acesso
PRAZO_PADRAO_DIAS = 10 # Prazo total para uma REP
DIAS_PARA_ALERTA_VENCENDO = 3 # Quantos dias antes do PRAZO_PADRAO_DIAS para alertar "Vencendo"

def obter_metricas_reps(usuario_id: int):
    """
    Busca as contagens de REPs por status e prazo para o usuário logado.
    Calcula "Prazo Vencendo" e "Em Atraso" com base na data de solicitação.
    """
    # REPs Pendentes (aguardando início do laudo)
    query_pendentes = """
        SELECT COUNT(id) FROM rep
        WHERE usuario_id = ? AND status = 'Pendente'
    """
    pendentes = executar_query(query_pendentes, (usuario_id,))[0][0]

    # REPs Em Andamento (laudos em elaboração)
    query_em_andamento = """
        SELECT COUNT(id) FROM rep
        WHERE usuario_id = ? AND status = 'Em Andamento'
    """
    em_andamento = executar_query(query_em_andamento, (usuario_id,))[0][0]

    # REPs Concluídas (laudos finalizados)
    query_concluidos = """
        SELECT COUNT(id) FROM rep
        WHERE usuario_id = ? AND status = 'Concluído'
    """
    concluidos = executar_query(query_concluidos, (usuario_id,))[0][0]

    # REPs com Prazo Vencendo (nova lógica)
    # São REPs com status 'Pendente' ou 'Em Andamento'
    # cuja data de solicitação é mais antiga que (hoje - PRAZO_PADRAO_DIAS + DIAS_PARA_ALERTA_VENCENDO)
    # e que ainda não estão em atraso (ou seja, data_solicitacao + PRAZO_PADRAO_DIAS ainda não passou de hoje)

    hoje = date.today()

    # Data a partir da qual uma REP entra no estado "Vencendo"
    # Ex: se PRAZO_PADRAO_DIAS = 10 e DIAS_PARA_ALERTA_VENCENDO = 3,
    # uma REP está vencendo se foi solicitada há mais de 7 dias (10 - 3)
    data_limite_para_vencendo = hoje - timedelta(days=PRAZO_PADRAO_DIAS - DIAS_PARA_ALERTA_VENCENDO)

    # Data a partir da qual uma REP entra no estado "Em Atraso"
    data_limite_para_atraso = hoje - timedelta(days=PRAZO_PADRAO_DIAS)

    query_prazo_vencendo = f"""
        SELECT COUNT(id) FROM rep
        WHERE usuario_id = ?
          AND status IN ('Pendente', 'Em Andamento')
          AND data_solicitacao <= ? -- Solicitada há mais tempo que a data limite para vencendo
          AND data_solicitacao > ?  -- Mas ainda não está em atraso
    """
    prazo_vencendo = executar_query(
        query_prazo_vencendo,
        (usuario_id, data_limite_para_vencendo.isoformat(), data_limite_para_atraso.isoformat())
    )[0][0]

    # REPs Em Atraso (lógica mantida)
    query_em_atraso = f"""
        SELECT COUNT(id) FROM rep
        WHERE usuario_id = ?
          AND status IN ('Pendente', 'Em Andamento')
          AND DATE(data_solicitacao, '+{PRAZO_PADRAO_DIAS} days') < ?
    """
    em_atraso = executar_query(
        query_em_atraso,
        (usuario_id, hoje.isoformat())
    )[0][0]


    return {
        "pendentes": pendentes,
        "em_andamento": em_andamento,
        "concluidos": concluidos,
        "prazo_vencendo": prazo_vencendo,
        "em_atraso": em_atraso
    }


def tela_dashboard():
    """
    Tela principal após o login.
    Menu lateral abre automaticamente a seção
    correspondente à página atual.
    """
    usuario = obter_usuario_logado()

    # ── Detecta a página atual pela URL ─────────────────
    path = st.session_state.get("_active_page", "")
    script_atual = os.path.basename(sys.argv[0]) if sys.argv else ""

    def pagina_ativa(paginas: list) -> bool:
        """
        Verifica se alguma das páginas da lista
        é a página atualmente ativa.

        Args:
            paginas: lista de caminhos de arquivo (ex: "pages/nova_rep.py")

        Returns:
            True se a página atual está na lista
        """
        for p in paginas:
            nome_pagina = os.path.basename(p).replace(".py", "")
            if nome_pagina in path or nome_pagina in script_atual.replace(".py", ""):
                return True
        return False

    # Define quais páginas pertencem a cada seção
    secao_rep = [
        "pages/nova_rep.py",
        "pages/listar_rep.py",
        "pages/editar_rep.py",
    ]
    secao_laudos = [
        "pages/novo_laudo.py",
        "pages/editor_laudo.py",
        "pages/visualizar_laudo.py",
    ]
    secao_cadastros = [
        "pages/tipos_exame.py",
        "pages/solicitantes.py",
        "pages/gerenciar_templates.py",
        "pages/editor_template.py",
    ]
    secao_sistema = [
        "pages/busca.py",
        "pages/historico.py",
        "pages/backup.py",
        "pages/perfil.py",
    ]

    # ── Barra lateral ───────────────────────────────────
    with st.sidebar:

        # Cabeçalho do usuário
        st.markdown(f"""
        <div style='
            background-color: #1a3a5c;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        '>
            <p style='color: white; font-size: 0.8rem; margin: 0;'>
                Bem-vindo,
            </p>
            <p style='color: white; font-weight: bold;
                      font-size: 1rem; margin: 0;'>
                {usuario['nome'].split()[0]}
            </p>
            <p style='color: #aac4e0; font-size: 0.75rem; margin: 0;'>
                {usuario['cargo']}
            </p>
            <p style='color: #aac4e0; font-size: 0.75rem; margin: 0;'>
                📍 {usuario['lotacao']}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # ── Início ──────────────────────────────────────
        st.page_link(
            "app.py",
            label="Dashboard",
            icon="🏠"
        )

        st.markdown("---")

        # ── REPs ────────────────────────────────────────
        with st.expander(
            "📋 Requisições (REPs)",
            expanded=pagina_ativa(secao_rep)
        ):
            st.page_link(
                "pages/nova_rep.py",
                label="Nova REP",
                icon="➕"
            )
            st.page_link(
                "pages/listar_rep.py",
                label="Listar REPs",
                icon="📄"
            )
            st.page_link(
                "pages/editar_rep.py",
                label="Editar REP",
                icon="✏️"
            )

        # ── Laudos ──────────────────────────────────────
        with st.expander(
            "📝 Laudos",
            expanded=pagina_ativa(secao_laudos)
        ):
            st.page_link(
                "pages/novo_laudo.py",
                label="Vincular Laudo a REP",
                icon="➕"
            )
            st.page_link(
                "pages/editor_laudo.py",
                label="Editar Laudo",
                icon="✏️"
            )
            st.page_link(
                "pages/visualizar_laudo.py",
                label="Visualizar Laudo",
                icon="👁️"
            )

        # ── Cadastros ───────────────────────────────────
        with st.expander(
            "🗂️ Cadastros",
            expanded=pagina_ativa(secao_cadastros)
        ):
            st.page_link(
                "pages/tipos_exame.py",
                label="Tipos de Exame",
                icon="🏷️"
            )
            st.page_link(
                "pages/solicitantes.py",
                label="Solicitantes",
                icon="🏛️"
            )
            st.page_link(
                "pages/gerenciar_templates.py",
                label="Templates de Laudo",
                icon="📋"
            )

        # ── Sistema ─────────────────────────────────────
        with st.expander(
            "⚙️ Sistema",
            expanded=pagina_ativa(secao_sistema)
        ):
            st.page_link(
                "pages/busca.py",
                label="Busca",
                icon="🔍"
            )
            st.page_link(
                "pages/historico.py",
                label="Histórico",
                icon="📜"
            )
            st.page_link(
                "pages/backup.py",
                label="Importar e Exportar BD",
                icon="💾"
            )
            st.page_link(
                "pages/perfil.py",
                label="Perfil e Configurações",
                icon="👤"
            )

        # ── Sair ────────────────────────────────────────
        st.markdown("---")
        if st.button(
            "Sair",
            icon="🚪",
            use_container_width=True
        ):
            fazer_logout()
            st.rerun()

    # ── Conteúdo principal ──────────────────────────────
    st.title("🏠 Dashboard")
    st.markdown(f"Bem-vindo, **{usuario['nome']}**!")
    st.markdown("---")

    # Obtém as métricas atualizadas
    metricas = obter_metricas_reps(usuario["id"])

    def card_metrica(label, valor, cor, icon):
        return f"""
        <div style="
            background: linear-gradient(135deg, {cor}15, {cor}08);
            border: 1px solid {cor}30;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        ">
            <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
            <div style="font-size: 36px; font-weight: bold; color: {cor};">{valor}</div>
            <div style="font-size: 14px; color: #666; margin-top: 4px;">{label}</div>
        </div>
        """

    st.markdown("### 📊 Visão Geral")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.markdown(card_metrica("📋 Pendentes", metricas["pendentes"], "#FFA500", "📋"), unsafe_allow_html=True)
    col2.markdown(card_metrica("📝 Em Andamento", metricas["em_andamento"], "#1E90FF", "📝"), unsafe_allow_html=True)
    col3.markdown(card_metrica("✅ Concluídos", metricas["concluidos"], "#2ECC71", "✅"), unsafe_allow_html=True)
    col4.markdown(card_metrica(f"⚠️ Vencendo ({PRAZO_PADRAO_DIAS - DIAS_PARA_ALERTA_VENCENDO}-{PRAZO_PADRAO_DIAS}d)", metricas["prazo_vencendo"], "#FF6B6B", "⚠️"), unsafe_allow_html=True)
    col5.markdown(card_metrica(f"🚨 Atrasado (> {PRAZO_PADRAO_DIAS}d)", metricas["em_atraso"], "#DC143C", "🚨"), unsafe_allow_html=True)

    st.markdown("---")
    st.info(
        "💡 **Sistema em construção.** "
        "Os módulos serão ativados conforme o desenvolvimento avança."
    )
# ──────────────────────────────────────────────────────
# ROTEAMENTO PRINCIPAL
# ──────────────────────────────────────────────────────

 #   Controla qual tela é exibida:
 #   1. Primeiro acesso → cadastro inicial
 #   2. Não autenticado → login
 #   3. Autenticado     → dashboard
 
def main():
    # Defina a página atual na sessão para o menu funcionar corretamente
    st.session_state["_active_page"] = __file__
    if not usuario_existe():
        tela_primeiro_acesso()
    elif not esta_autenticado():
        tela_login()
    else:
        tela_dashboard()

main()