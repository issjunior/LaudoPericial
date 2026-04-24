"""
pages/tipos_exame.py
──────────────────────────────────────────────────────
Página de gerenciamento de Tipos de Exame.
Permite criar, editar, ativar/desativar e excluir.
──────────────────────────────────────────────────────
"""

import sys
import os

# Garante que a raiz do projeto está no sys.path
# Funciona localmente E no Streamlit Cloud
ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st
from components.menu import renderizar_menu
from services.cadastro_service import (
    listar_tipos_exame,
    buscar_tipo_exame,
    criar_tipo_exame,
    atualizar_tipo_exame,
    alternar_status_tipo_exame,
    excluir_tipo_exame,
)

# ──────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tipos de Exame — LaudoPericial",
    page_icon="🏷️",
    layout="wide",
)

# Renderiza o menu lateral (já exige autenticação)
renderizar_menu()


# ──────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ──────────────────────────────────────────────────────

def inicializar_estado():
    """
    Inicializa as variáveis de controle de estado da página.
    Controla qual formulário está aberto no momento.
    """
    if "te_modo" not in st.session_state:
        # Modos possíveis: None | "criar" | "editar"
        st.session_state["te_modo"]       = None
    if "te_id_editando" not in st.session_state:
        # ID do tipo sendo editado
        st.session_state["te_id_editando"] = None


def abrir_criar():
    """Abre o formulário de criação."""
    st.session_state["te_modo"]        = "criar"
    st.session_state["te_id_editando"] = None


def abrir_editar(tipo_id: int):
    """Abre o formulário de edição para o tipo informado."""
    st.session_state["te_modo"]        = "editar"
    st.session_state["te_id_editando"] = tipo_id


def fechar_formulario():
    """Fecha qualquer formulário aberto."""
    st.session_state["te_modo"]        = None
    st.session_state["te_id_editando"] = None


# ──────────────────────────────────────────────────────
# FORMULÁRIO — CRIAR
# ──────────────────────────────────────────────────────

def formulario_criar():
    """
    Formulário para criação de novo tipo de exame.
    """
    st.markdown("### ➕ Novo Tipo de Exame")

    with st.form("form_criar_tipo"):
        col1, col2 = st.columns([2, 1])

        with col1:
            col_cod, col_nome = st.columns([1, 2])

            with col_cod:
                codigo = st.text_input(
                    "Código do exame no GDL *",
                    placeholder="Ex: H-001",
                    max_chars=10,
                    help="Código único do exame no GDL. Formato: X-000"
                )
            with col_nome:
                nome = st.text_input(
                    "Nome do Tipo de Exame *",
                    placeholder="Ex: Homicídio, Roubo, Incêndio..."
                )

            descricao = st.text_area(
                "Descrição",
                placeholder="Descreva brevemente este tipo de exame (opcional)",
                height=100,
            )

        with col2:
            exame_de_local = st.checkbox(
                "🚗 Exame de Local",
                help=(
                    "Marque se este tipo de exame exige "
                    "deslocamento até o local do crime."
                )
            )
            st.markdown(" ")
            st.info(
                "**Código GDL**\n\n"
                "Use o mesmo código cadastrado "
                "no GDL para este tipo de exame.\n\n"
            )

        st.markdown("---")
        col_salvar, col_cancelar, _ = st.columns([1, 1, 3])

        with col_salvar:
            submitted = st.form_submit_button(
                "💾 Salvar",
                use_container_width=True,
                type="primary"
            )
        with col_cancelar:
            cancelar = st.form_submit_button(
                "Cancelar",
                use_container_width=True,
            )

        if cancelar:
            fechar_formulario()
            st.rerun()

        if submitted:
            try:
                criar_tipo_exame(
                    codigo         = codigo,
                    nome           = nome,
                    descricao      = descricao,
                    exame_de_local = exame_de_local,
                )
                st.success(
                    f"✅ Tipo de exame **{nome}** "
                    f"criado com sucesso!"
                )
                fechar_formulario()
                st.rerun()

            except ValueError as e:
                st.error(f"❌ {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")

# ──────────────────────────────────────────────────────
# FORMULÁRIO — EDITAR
# ──────────────────────────────────────────────────────

def formulario_editar(tipo_id: int):
    """
    Formulário para edição de um tipo de exame existente.

    Args:
        tipo_id: ID do tipo de exame a editar
    """
    tipo = buscar_tipo_exame(tipo_id)

    if not tipo:
        st.error("❌ Tipo de exame não encontrado.")
        fechar_formulario()
        return

    st.markdown(f"### ✏️ Editando: {tipo['nome']}")

    with st.form("form_editar_tipo"):
        col1, col2 = st.columns([2, 1])

        with col1:
            col_cod, col_nome = st.columns([1, 2])

            with col_cod:
                codigo = st.text_input(
                    "Código do exame no GDL *",
                    value=tipo["codigo"],
                    max_chars=10,
                    help="Código único do exame no GDL. Formato: X-000"
                )
            with col_nome:
                nome = st.text_input(
                    "Nome do Tipo de Exame *",
                    value=tipo["nome"]
                )

            descricao = st.text_area(
                "Descrição",
                value=tipo["descricao"] or "",
                height=100,
            )

        with col2:
            exame_de_local = st.checkbox(
                "🚗 Exame de Local",
                value=bool(tipo["exame_de_local"]),
                help=(
                    "Marque se este tipo de exame exige "
                    "deslocamento até o local do crime."
                )
            )
            st.markdown(" ")
            st.info(
                "**Código GDL**\n\n"
                "Use o mesmo código cadastrado "
                "no GDL para este tipo de exame.\n\n"
                "Formato: `X-000`\n\n"
                "Ex: `H-001`, `R-002`"
            )

        st.markdown("---")
        col_salvar, col_cancelar, _ = st.columns([1, 1, 3])

        with col_salvar:
            submitted = st.form_submit_button(
                "💾 Salvar Alterações",
                use_container_width=True,
                type="primary"
            )
        with col_cancelar:
            cancelar = st.form_submit_button(
                "Cancelar",
                use_container_width=True,
            )

        if cancelar:
            fechar_formulario()
            st.rerun()

        if submitted:
            try:
                atualizar_tipo_exame(
                    tipo_id        = tipo_id,
                    codigo         = codigo,
                    nome           = nome,
                    descricao      = descricao,
                    exame_de_local = exame_de_local,
                )
                st.success(
                    f"✅ Tipo de exame **{nome}** "
                    f"atualizado com sucesso!"
                )
                fechar_formulario()
                st.rerun()

            except ValueError as e:
                st.error(f"❌ {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")

# ──────────────────────────────────────────────────────
# TABELA — LISTAGEM
# ──────────────────────────────────────────────────────

def tabela_tipos(tipos: list):
    """
    Exibe a listagem de tipos de exame usando expanders (layout moderno).
    """
    if not tipos:
        st.info("📭 Nenhum tipo de exame cadastrado ainda.")
        return

    for tipo in tipos:
        # Define o título do expander com ícones de status
        status_icon = "🟢" if tipo['ativo'] else "🔴"
        local_icon = "🚗" if tipo['exame_de_local'] else "📝"
        expander_title = f"{status_icon} {local_icon} {tipo['codigo']} — {tipo['nome']}"
        
        with st.expander(expander_title):
            col_info, col_actions = st.columns([3, 1])
            
            with col_info:
                st.markdown(f"**Descrição:** {tipo['descricao'] or '—'}")
                st.markdown(f"**Exame de Local:** {'Sim 🚗' if tipo['exame_de_local'] else 'Não 📝'}")
                status_text = "Ativo" if tipo['ativo'] else "Inativo"
                st.markdown(f"**Status:** {status_icon} {status_text}")
            
            with col_actions:
                st.markdown("### Ações")
                
                # Botão Editar
                if st.button("✏️ Editar", key=f"edit_{tipo['id']}", use_container_width=True):
                    abrir_editar(tipo['id'])
                    st.rerun()
                
                # Botão Ativar/Desativar
                btn_status_label = "🔴 Desativar" if tipo['ativo'] else "🟢 Ativar"
                if st.button(btn_status_label, key=f"stat_{tipo['id']}", use_container_width=True):
                    try:
                        alternar_status_tipo_exame(tipo['id'])
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ {e}")
                
                # Botão Excluir (com confirmação simples via botão de cor diferente)
                if st.button("🗑️ Excluir", key=f"del_{tipo['id']}", use_container_width=True, type="secondary"):
                    try:
                        excluir_tipo_exame(tipo['id'])
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ {e}")
        
# ──────────────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ──────────────────────────────────────────────────────

def main():
    """
    Ponto de entrada da página Tipos de Exame.
    """
    inicializar_estado()

    # Cabeçalho
    st.title("🏷️ Tipos de Exame")
    st.markdown(
        "Gerencie os tipos de exame pericial disponíveis no sistema."
    )
    st.markdown("---")

    modo = st.session_state["te_modo"]

    # ── Exibe formulário se estiver em modo criar/editar ─
    if modo == "criar":
        formulario_criar()
        st.markdown("---")

    elif modo == "editar":
        formulario_editar(st.session_state["te_id_editando"])
        st.markdown("---")

    # ── Barra de ações ──────────────────────────────────
    col_btn, col_filtro, _ = st.columns([2, 2, 4])

    with col_btn:
        if modo is None:
            if st.button(
                "➕ Novo Tipo de Exame",
                use_container_width=True,
                type="primary"
            ):
                abrir_criar()
                st.rerun()

    with col_filtro:
        mostrar_inativos = st.toggle(
            "Mostrar inativos",
            value=False
        )

    st.markdown("---")

    # ── Listagem ────────────────────────────────────────
    tipos = listar_tipos_exame(
        apenas_ativos=not mostrar_inativos
    )

    # Contador
    total = len(tipos)
    st.caption(
        f"{total} tipo(s) de exame encontrado(s)"
    )

    tabela_tipos(tipos)


main()