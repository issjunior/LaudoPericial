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

    # Oculta o menu padrão do Streamlit (Double Menu fix)
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

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

    # ── DEFINIÇÃO DAS SEÇÕES ──
    secao_rep = ["pages/nova_rep.py", "pages/listar_rep.py", "pages/editar_rep.py"]
    secao_laudos = ["pages/novo_laudo.py", "pages/editor_laudo.py", "pages/visualizar_laudo.py"]
    secao_cadastros = ["pages/tipos_exame.py", "pages/solicitantes.py", "pages/gerenciar_templates.py", "pages/cabecalho.py", "pages/placeholders.py"]
    secao_sistema = ["pages/busca.py", "pages/historico.py", "pages/backup.py", "pages/perfil.py"]

    # ── PERFIL E NAVEGAÇÃO ──
    with st.sidebar:
        # ── Perfil do Usuário (Design Moderno) ──
        st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #1a3a5c 0%, #2a5298 100%);
            padding: 1.25rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid rgba(255,255,255,0.1);
        '>
            <div style='display: flex; align-items: center; margin-bottom: 10px;'>
                <div style='
                    background: rgba(255,255,255,0.2);
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 12px;
                    font-size: 20px;
                '>👤</div>
                <div>
                    <p style='color: rgba(255,255,255,0.7); font-size: 0.75rem; margin: 0; text-transform: uppercase; letter-spacing: 1px;'>
                        Perito Logado
                    </p>
                    <p style='color: white; font-weight: 700; font-size: 1.1rem; margin: 0; line-height: 1.2;'>
                        {usuario['nome'].split()[0]}
                    </p>
                </div>
            </div>
            <div style='border-top: 1px solid rgba(255,255,255,0.1); pt: 10px; margin-top: 10px;'>
                <p style='color: #aac4e0; font-size: 0.8rem; margin: 0; display: flex; align-items: center;'>
                    <span style='margin-right: 8px;'>🎖️</span> {usuario['cargo']}
                </p>
                <p style='color: #aac4e0; font-size: 0.8rem; margin: 4px 0 0 0; display: flex; align-items: center;'>
                    <span style='margin-right: 8px;'>📍</span> {usuario['lotacao']}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.page_link("app.py", label="Dashboard Inicial", icon="🏠")
        st.markdown("---")

        # ── EXPANSORES (Estilo Padrão) ──

        # 1. REPs
        with st.expander("📋 Requisições (REPs)", expanded=pagina_ativa(secao_rep)):
            st.page_link("pages/nova_rep.py", label="Nova REP", icon="➕")
            st.page_link("pages/listar_rep.py", label="Listar REPs", icon="📄")
            st.page_link("pages/editar_rep.py", label="Editar REP", icon="✏️")
        
        # 2. Laudos
        with st.expander("✍️ Laudos Periciais", expanded=pagina_ativa(secao_laudos)):
            st.page_link("pages/novo_laudo.py", label="Vincular Laudo", icon="🔗")
            st.page_link("pages/editor_laudo.py", label="Escrever Laudo", icon="✒️")
            st.page_link("pages/visualizar_laudo.py", label="Visualizar / Exportar", icon="👁️")

        # 3. Cadastros
        with st.expander("🗂️ Cadastros Base", expanded=pagina_ativa(secao_cadastros)):
            st.page_link("pages/tipos_exame.py", label="Tipos de Exame", icon="🏷️")
            st.page_link("pages/solicitantes.py", label="Solicitantes", icon="🏛️")
            st.page_link("pages/gerenciar_templates.py", label="Templates de Laudo", icon="📋")
            st.page_link("pages/cabecalho.py", label="Cabeçalho do Laudo", icon="📄")
            st.page_link("pages/placeholders.py", label="Placeholders", icon="🧩")

        # 4. Sistema
        with st.expander("🛠️ Sistema / Ferramentas", expanded=pagina_ativa(secao_sistema)):
            st.page_link("pages/busca.py", label="Busca Avançada", icon="🔍")
            st.page_link("pages/historico.py", label="Histórico de Ações", icon="📜")
            st.page_link("pages/backup.py", label="Backup (Import/Export)", icon="💾")
            st.page_link("pages/perfil.py", label="Meu Perfil", icon="👤")

        # ── RODAPÉ ──
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.page_link(
                "pages/99_logout.py",
                label="Sair",
                icon="🚪"
            )