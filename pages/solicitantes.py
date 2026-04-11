"""
pages/solicitantes.py
──────────────────────────────────────────────────────
Página de gerenciamento de Solicitantes.
Permite criar, editar, ativar/desativar e excluir.
──────────────────────────────────────────────────────
"""

import sys
import os
import streamlit as st

# Garante que a raiz do projeto está no sys.path
# Funciona localmente E no Streamlit Cloud
ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu
from services.cadastro_service import (
    listar_solicitantes,
    buscar_solicitante,
    criar_solicitante,
    atualizar_solicitante,
    alternar_status_solicitante,
    excluir_solicitante,
)

# ──────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Solicitantes — LaudoPericial",
    page_icon="🏢",
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
    if "sol_modo" not in st.session_state:
        # Modos possíveis: None | "criar" | "editar"
        st.session_state["sol_modo"]       = None
    if "sol_id_editando" not in st.session_state:
        # ID do solicitante sendo editado
        st.session_state["sol_id_editando"] = None


def abrir_criar():
    """Abre o formulário de criação."""
    st.session_state["sol_modo"]        = "criar"
    st.session_state["sol_id_editando"] = None


def abrir_editar(solicitante_id: int):
    """Abre o formulário de edição para o solicitante informado."""
    st.session_state["sol_modo"]        = "editar"
    st.session_state["sol_id_editando"] = solicitante_id


def fechar_formulario():
    """Fecha qualquer formulário aberto."""
    st.session_state["sol_modo"]        = None
    st.session_state["sol_id_editando"] = None


# ──────────────────────────────────────────────────────
# FORMULÁRIO — CRIAR
# ──────────────────────────────────────────────────────

def formulario_criar():
    """
    Formulário para criação de novo solicitante.
    """
    st.markdown("### ➕ Novo Solicitante")

    with st.form("form_criar_solicitante"):
        col1, col2 = st.columns([2, 1])

        with col1:
            orgao = st.text_input(
                "Nome do Órgão Solicitante *", # Agora obrigatório
                placeholder="Ex: 1ª Delegacia de Polícia de Curitiba"
            )
            nome = st.text_input(
                "Nome do Contato (Opcional)", # Não obrigatório
                placeholder="Ex: Delegado João da Silva"
            )
            email = st.text_input(
                "Email do Órgão (Opcional)", # Novo campo, não obrigatório
                placeholder="Ex: delegacia1@pc.pr.gov.br"
            )

        with col2:
            st.markdown(" ")
            st.info(
                "**Informações do Solicitante**\n\n"
                "Preencha os dados da instituição ou pessoa "
                "que solicita as perícias."
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
                criar_solicitante(
                    nome    = nome,
                    orgao   = orgao,
                    email   = email, # Passando o novo campo
                )
                st.success(f"✅ Solicitante **{orgao}** criado com sucesso!")
                fechar_formulario()
                st.rerun()

            except ValueError as e:
                st.error(f"❌ {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")

# ──────────────────────────────────────────────────────
# FORMULÁRIO — EDITAR
# ──────────────────────────────────────────────────────

def formulario_editar(solicitante_id: int):
    """
    Formulário para edição de um solicitante existente.

    Args:
        solicitante_id: ID do solicitante a editar
    """
    solicitante = buscar_solicitante(solicitante_id)

    if not solicitante:
        st.error("❌ Solicitante não encontrado.")
        fechar_formulario()
        return

    st.markdown(f"### ✏️ Editando: {solicitante['orgao']}") # Exibe o órgão no título

    with st.form("form_editar_solicitante"):
        col1, col2 = st.columns([2, 1])

        with col1:
            orgao = st.text_input(
                "Nome do Órgão Solicitante *", # Agora obrigatório
                value=solicitante["orgao"] or ""
            )
            nome = st.text_input(
                "Nome do Contato (Opcional)", # Não obrigatório
                value=solicitante["nome"] or ""
            )
            email = st.text_input(
                "Email do Órgão (Opcional)", # Novo campo, não obrigatório
                value=solicitante["contato"] or "" # 'contato' no banco é 'email' aqui
            )

        with col2:
            st.markdown(" ")
            st.info(
                "**Informações do Solicitante**\n\n"
                "Preencha os dados da instituição ou pessoa "
                "que solicita as perícias."
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
                atualizar_solicitante(
                    solicitante_id = solicitante_id,
                    nome           = nome,
                    orgao          = orgao,
                    email          = email, # Passando o novo campo
                )
                st.success(
                    f"✅ Solicitante **{orgao}** " # Exibe o órgão na mensagem
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

def tabela_solicitantes(solicitantes: list):
    """
    Exibe a tabela de solicitantes com ações.

    Args:
        solicitantes: lista de dicionários com os solicitantes
    """
    if not solicitantes:
        st.info("📭 Nenhum solicitante cadastrado ainda.")
        return

    # Cabeçalho da tabela
    col_orgao, col_nome, col_email, col_status, col_acoes = st.columns(
        [3, 2, 2, 1.5, 2]
    )
    col_orgao.markdown("**Órgão**")
    col_nome.markdown("**Contato**") # Agora é o nome do contato
    col_email.markdown("**Email**")  # Agora é o email do órgão
    col_status.markdown("**Status**")
    col_acoes.markdown("**Ações**")

    st.markdown("---")

    for solicitante in solicitantes:
        col_orgao, col_nome, col_email, col_status, col_acoes = st.columns(
            [3, 2, 2, 1.5, 2]
        )

        with col_orgao:
            st.markdown(f"**{solicitante['orgao']}**")

        with col_nome:
            nome_contato = solicitante["nome"] or "—" # 'nome' no banco é 'nome do contato' aqui
            st.markdown(nome_contato)

        with col_email:
            email_orgao = solicitante["contato"] or "—" # 'contato' no banco é 'email do órgão' aqui
            st.markdown(email_orgao)

        with col_status:
            if solicitante["ativo"]:
                st.markdown("🟢 Ativo")
            else:
                st.markdown("🔴 Inativo")

        with col_acoes:
            col_btn1, col_btn2, col_btn3 = st.columns(3)

            # Botão Editar
            with col_btn1:
                if st.button(
                    "✏️",
                    key=f"editar_{solicitante['id']}",
                    help="Editar"
                ):
                    abrir_editar(solicitante["id"])
                    st.rerun()

            # Botão Ativar/Desativar
            with col_btn2:
                icone_status = "🔴" if solicitante["ativo"] else "🟢"
                help_status  = "Desativar" if solicitante["ativo"] else "Ativar"
                if st.button(
                    icone_status,
                    key=f"status_{solicitante['id']}",
                    help=help_status
                ):
                    try:
                        novo = alternar_status_solicitante(solicitante["id"])
                        msg  = "ativado" if novo else "desativado"
                        st.success(
                            f"✅ **{solicitante['orgao']}** {msg} com sucesso!"
                        )
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ {e}")

            # Botão Excluir
            with col_btn3:
                if st.button(
                    "🗑️",
                    key=f"excluir_{solicitante['id']}",
                    help="Excluir"
                ):
                    try:
                        excluir_solicitante(solicitante["id"])
                        st.success(
                            f"✅ **{solicitante['orgao']}** excluído com sucesso!"
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
    Ponto de entrada da página Solicitantes.
    """
    inicializar_estado()

    # Cabeçalho
    st.title("🏢 Solicitantes")
    st.markdown(
        "Gerencie as instituições ou pessoas que solicitam exames periciais."
    )
    st.markdown("---")

    modo = st.session_state["sol_modo"]

    # ── Exibe formulário se estiver em modo criar/editar ─
    if modo == "criar":
        formulario_criar()
        st.markdown("---")

    elif modo == "editar":
        formulario_editar(st.session_state["sol_id_editando"])
        st.markdown("---")

    # ── Barra de ações ──────────────────────────────────
    col_btn, col_filtro, _ = st.columns([2, 2, 4])

    with col_btn:
        if modo is None:
            if st.button(
                "➕ Novo Solicitante",
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
    solicitantes = listar_solicitantes(
        apenas_ativos=not mostrar_inativos
    )

    # Contador
    total = len(solicitantes)
    st.caption(
        f"{total} solicitante(s) encontrado(s)"
    )

    tabela_solicitantes(solicitantes)


main()