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
                "**Exame de Local**\n\n"
                "Marque quando o perito precisa se "
                "deslocar fisicamente ao local."
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
            if not nome.strip():
                st.error("❌ O nome do tipo de exame é obrigatório.")
            else:
                try:
                    criar_tipo_exame(
                        nome           = nome,
                        descricao      = descricao,
                        exame_de_local = exame_de_local,
                    )
                    st.success(f"✅ Tipo de exame **{nome}** criado com sucesso!")
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
                "**Exame de Local**\n\n"
                "Marque quando o perito precisa se "
                "deslocar fisicamente ao local."
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
            if not nome.strip():
                st.error("❌ O nome do tipo de exame é obrigatório.")
            else:
                try:
                    atualizar_tipo_exame(
                        tipo_id        = tipo_id,
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
    Exibe a tabela de tipos de exame com ações.

    Args:
        tipos: lista de dicionários com os tipos
    """
    if not tipos:
        st.info("📭 Nenhum tipo de exame cadastrado ainda.")
        return

    # Cabeçalho da tabela
    col_nome, col_desc, col_local, col_status, col_acoes = st.columns(
        [3, 4, 1.5, 1.5, 2]
    )
    col_nome.markdown("**Nome**")
    col_desc.markdown("**Descrição**")
    col_local.markdown("**Local**")
    col_status.markdown("**Status**")
    col_acoes.markdown("**Ações**")

    st.markdown("---")

    for tipo in tipos:
        col_nome, col_desc, col_local, col_status, col_acoes = st.columns(
            [3, 4, 1.5, 1.5, 2]
        )

        with col_nome:
            st.markdown(f"**{tipo['nome']}**")

        with col_desc:
            descricao = tipo["descricao"] or "—"
            # Trunca descrições longas
            if len(descricao) > 60:
                descricao = descricao[:60] + "..."
            st.markdown(descricao)

        with col_local:
            if tipo["exame_de_local"]:
                st.markdown("🚗 Sim")
            else:
                st.markdown("— Não")

        with col_status:
            if tipo["ativo"]:
                st.markdown("🟢 Ativo")
            else:
                st.markdown("🔴 Inativo")

        with col_acoes:
            col_btn1, col_btn2, col_btn3 = st.columns(3)

            # Botão Editar
            with col_btn1:
                if st.button(
                    "✏️",
                    key=f"editar_{tipo['id']}",
                    help="Editar"
                ):
                    abrir_editar(tipo["id"])
                    st.rerun()

            # Botão Ativar/Desativar
            with col_btn2:
                icone_status = "🔴" if tipo["ativo"] else "🟢"
                help_status  = "Desativar" if tipo["ativo"] else "Ativar"
                if st.button(
                    icone_status,
                    key=f"status_{tipo['id']}",
                    help=help_status
                ):
                    try:
                        novo = alternar_status_tipo_exame(tipo["id"])
                        msg  = "ativado" if novo else "desativado"
                        st.success(
                            f"✅ **{tipo['nome']}** {msg} com sucesso!"
                        )
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ {e}")

            # Botão Excluir
            with col_btn3:
                if st.button(
                    "🗑️",
                    key=f"excluir_{tipo['id']}",
                    help="Excluir"
                ):
                    try:
                        excluir_tipo_exame(tipo["id"])
                        st.success(
                            f"✅ **{tipo['nome']}** excluído com sucesso!"
                        )
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ {e}")

        st.markdown("---")


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