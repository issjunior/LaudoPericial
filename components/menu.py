# components/menu.py
"""
components/menu.py
──────────────────────────────────────────────────────
Menu lateral reutilizável.
Importado por todas as páginas do sistema.
──────────────────────────────────────────────────────
"""
import sys
import os
import streamlit as st
from core.auth import (
    obter_usuario_logado,
    fazer_logout,
    exigir_autenticacao,
)

# Garante que a raiz do projeto está no sys.path
ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

def renderizar_menu():
    """
    Renderiza o menu lateral com o expander da
    seção atual aberto automaticamente.

    Deve ser chamado no início de cada página.
    """
    # Bloqueia acesso se não estiver logado
    exigir_autenticacao()

    usuario = obter_usuario_logado()

    # Obtém o nome do arquivo da página atual a partir do Streamlit session state
    # st.session_state["_active_page"] contém o caminho completo da página ativa
    active_page_path = st.session_state.get("_active_page", "")
    # Extrai apenas o nome do arquivo (ex: "backup.py")
    active_page_filename = os.path.basename(active_page_path)
    
    # Se ainda não tiver a página ativa, tenta detectar de outras formas
    if not active_page_filename:
        # Tenta pegar do sys.argv (usado pelo Streamlit)
        if len(sys.argv) > 1:
            script_path = sys.argv[1]
            page_name = os.path.basename(script_path)
            if page_name.endswith(".py"):
                active_page_filename = page_name


    def pagina_ativa(paginas_na_secao: list) -> bool:
        """
        Verifica se a página atual pertence à seção para expandir o menu.
        Compara o nome do arquivo da página ativa com os nomes dos arquivos na seção.
        Se não conseguir detectar a página ativa, retorna True para sempre mostrar expandido.
        """
        if not active_page_filename:
            return True
            
        for p in paginas_na_secao:
            secao_filename = os.path.basename(p)
            if active_page_filename == secao_filename:
                return True
        return False

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

        st.page_link(
            "app.py",
            label="Dashboard",
            icon="🏠"
        )

        st.markdown("---")

        with st.expander("📋 Requisições (REPs)", expanded=True):
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

        with st.expander(
            "📝 Laudos",
            expanded=pagina_ativa(secao_laudos)
        ):
            st.page_link(
                "pages/novo_laudo.py",
                label="Novo Laudo",
                icon="✏️"
            )

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

        with st.expander(
            "⚙️ Sistema",
            expanded=pagina_ativa(secao_sistema) # AQUI VAI USAR A LÓGICA ATUALIZADA
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

        st.markdown("---")
        st.page_link(
            "pages/99_logout.py",
            label="Sair",
            icon="🚪"
        )