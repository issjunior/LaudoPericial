"""
app.py
──────────────────────────────────────────────────────
Ponto de entrada do sistema LaudoPericial PCPR.
Controla o fluxo inicial: primeiro acesso ou login.
──────────────────────────────────────────────────────
"""

import streamlit as st
from database.db import init_database
from core.auth import (
    usuario_existe,
    criar_usuario,
    fazer_login,
    fazer_logout,
    esta_autenticado,
    obter_usuario_logado,
)

# ──────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# Deve ser o primeiro comando Streamlit do arquivo
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="LaudoPericial PCPR",
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
    O usuário cadastra seus dados de perito e define a senha.
    """
    st.markdown(
        "<h1 class='header-title'>🔍 LaudoPericial PCPR</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p class='header-subtitle'>Polícia Científica do Paraná</p>",
        unsafe_allow_html=True
    )

    st.info(
        "👋 **Bem-vindo!** Esta é a primeira execução do sistema. "
        "Cadastre seus dados para começar."
    )

    st.markdown("---")
    st.subheader("⚙️ Configuração Inicial — Dados do Perito")

    with st.form("form_primeiro_acesso"):

        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input(
                "Nome Completo *",
                placeholder="Ex: Izaias Santos de Souza Junior"
            )
            email = st.text_input(
                "E-mail Institucional *",
                placeholder="Ex: izaias.santos@policiacientifica.pr.gov.br"
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
            username_preview = email.strip().lower().split("@")[0]
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
        "<h1 class='header-title'>🔍 LaudoPericial PCPR</h1>",
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
                placeholder="Ex: izaias.santos"
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


def tela_dashboard():
    """
    Tela principal após o login.
    """
    usuario = obter_usuario_logado()

    with st.sidebar:
        st.markdown(f"### 👤 {usuario['nome']}")
        st.caption(f"{usuario['cargo']}")
        st.caption(f"📍 {usuario['lotacao']}")
        st.markdown("---")

        st.markdown("### 📋 Menu")
        st.page_link("app.py",
                     label="🏠 Dashboard", icon="🏠")

        st.markdown("**REPs**")
        st.page_link("pages/nova_rep.py",
                     label="➕ Nova REP", icon="➕")
        st.page_link("pages/listar_rep.py",
                     label="📋 Listar REPs", icon="📋")

        st.markdown("**Laudos**")
        st.page_link("pages/novo_laudo.py",
                     label="📝 Novo Laudo", icon="📝")

        st.markdown("**Cadastros**")
        st.page_link("pages/tipos_exame.py",
                     label="🏷️ Tipos de Exame", icon="🏷️")
        st.page_link("pages/solicitantes.py",
                     label="🏛️ Solicitantes", icon="🏛️")
        st.page_link("pages/gerenciar_templates.py",
                     label="📄 Templates", icon="📄")

        st.markdown("**Sistema**")
        st.page_link("pages/busca.py",
                     label="🔍 Busca", icon="🔍")
        st.page_link("pages/historico.py",
                     label="📜 Histórico", icon="📜")
        st.page_link("pages/perfil.py",
                     label="⚙️ Perfil", icon="⚙️")

        st.markdown("---")
        if st.button("🚪 Sair", use_container_width=True):
            fazer_logout()
            st.rerun()

    # ── Conteúdo principal ──────────────────────────────
    st.title("🏠 Dashboard")
    st.markdown(f"Bem-vindo, **{usuario['nome']}**!")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📋 REPs Pendentes",
            value="—",
            help="REPs aguardando início do laudo"
        )
    with col2:
        st.metric(
            label="📝 Em Andamento",
            value="—",
            help="Laudos em elaboração"
        )
    with col3:
        st.metric(
            label="✅ Concluídos",
            value="—",
            help="Laudos finalizados"
        )
    with col4:
        st.metric(
            label="⚠️ Prazo Vencendo",
            value="—",
            help="REPs com prazo nos próximos dias"
        )

    st.markdown("---")
    st.info(
        "💡 **Sistema em construção.** "
        "Os módulos serão ativados conforme o desenvolvimento avança."
    )


# ──────────────────────────────────────────────────────
# ROTEAMENTO PRINCIPAL
# ──────────────────────────────────────────────────────
def main():
    """
    Controla qual tela é exibida:
    1. Primeiro acesso → cadastro inicial
    2. Não autenticado → login
    3. Autenticado     → dashboard
    """
    if not usuario_existe():
        tela_primeiro_acesso()
    elif not esta_autenticado():
        tela_login()
    else:
        tela_dashboard()


main()