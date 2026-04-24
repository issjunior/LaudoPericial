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

    col1, col2 = st.columns([2, 1])

    with col1:
        orgao = st.text_input(
            "Nome do Órgão Solicitante *",
            placeholder="Ex: 1ª Delegacia de Polícia de Curitiba",
            key="sol_orgao_novo"
        )
        nome = st.text_input(
            "Nome do Contato (Opcional)",
            placeholder="Ex: Delegado João da Silva",
            key="sol_nome_novo"
        )
        email = st.text_input(
            "Email do Órgão (Opcional)",
            placeholder="Ex: delegacia1@pc.pr.gov.br",
            key="sol_email_novo"
        )

    with col2:
        st.markdown(" ")
        st.info("**Informações do Solicitante**\n\nPreencha os dados da instituição ou pessoa que solicita as perícias.")

    st.markdown("---")
    col_salvar, col_cancelar, _ = st.columns([1, 1, 3])

    submitted = col_salvar.button("💾 Salvar", use_container_width=True, type="primary")
    if col_cancelar.button("Cancelar", use_container_width=True):
        fechar_formulario()
        st.rerun()

    if submitted:
        erros = []
        if not orgao: erros.append("O **Nome do Órgão Solicitante** é obrigatório.")
        
        if erros:
            st.session_state["erros_sol"] = erros
            st.rerun()
        else:
            try:
                criar_solicitante(nome=nome, orgao=orgao, email=email)
                st.success(f"✅ Solicitante **{orgao}** criado!")
                fechar_formulario()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro: {e}")

    # Exibe erros em largura total
    if "erros_sol" in st.session_state:
        st.error("### ⚠️ Verifique o preenchimento:\n\n" + "\n".join([f"- {e}" for e in st.session_state["erros_sol"]]))
        del st.session_state["erros_sol"]

# ──────────────────────────────────────────────────────
# FORMULÁRIO — EDITAR
# ──────────────────────────────────────────────────────

def formulario_editar(solicitante_id: int):
    """
    Formulário para edição de um solicitante existente.
    """
    solicitante = buscar_solicitante(solicitante_id)

    if not solicitante:
        st.error("❌ Solicitante não encontrado.")
        fechar_formulario()
        return

    st.markdown(f"### ✏️ Editando: {solicitante['orgao']}")

    col1, col2 = st.columns([2, 1])

    with col1:
        orgao = st.text_input(
            "Nome do Órgão Solicitante *",
            value=solicitante["orgao"] or "",
            key="sol_orgao_edit"
        )
        nome = st.text_input(
            "Nome do Contato (Opcional)",
            value=solicitante["nome"] or "",
            key="sol_nome_edit"
        )
        email = st.text_input(
            "Email do Órgão (Opcional)",
            value=solicitante["contato"] or "",
            key="sol_email_edit"
        )

    with col2:
        st.markdown(" ")
        st.info("**Informações do Solicitante**\n\nPreencha os dados da instituição ou pessoa que solicita as perícias.")

    st.markdown("---")
    col_salvar, col_cancelar, _ = st.columns([1, 1, 3])

    submitted = col_salvar.button("💾 Salvar Alterações", use_container_width=True, type="primary")
    if col_cancelar.button("Cancelar", use_container_width=True):
        fechar_formulario()
        st.rerun()

    if submitted:
        erros = []
        if not orgao: erros.append("O **Nome do Órgão Solicitante** é obrigatório.")
        
        if erros:
            st.session_state["erros_sol"] = erros
            st.rerun()
        else:
            try:
                atualizar_solicitante(solicitante_id=solicitante_id, nome=nome, orgao=orgao, email=email)
                st.success(f"✅ Solicitante **{orgao}** atualizado!")
                fechar_formulario()
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro: {e}")

    # Exibe erros em largura total
    if "erros_sol" in st.session_state:
        st.error("### ⚠️ Verifique o preenchimento:\n\n" + "\n".join([f"- {e}" for e in st.session_state["erros_sol"]]))
        del st.session_state["erros_sol"]

# ──────────────────────────────────────────────────────
# TABELA — LISTAGEM
# ──────────────────────────────────────────────────────

def tabela_solicitantes(solicitantes: list):
    """
    Exibe a listagem de solicitantes usando expanders (layout moderno).
    """
    if not solicitantes:
        st.info("📭 Nenhum solicitante cadastrado ainda.")
        return

    for sol in solicitantes:
        status_icon = "🟢" if sol['ativo'] else "🔴"
        # Título do expander priorizando o Órgão
        expander_title = f"{status_icon} {sol['orgao']}"
        
        with st.expander(expander_title):
            col_info, col_actions = st.columns([3, 1])
            
            with col_info:
                st.markdown(f"**Responsável/Contato:** {sol['nome'] or '—'}")
                st.markdown(f"**Email:** {sol['contato'] or '—'}")
                status_text = "Ativo" if sol['ativo'] else "Inativo"
                st.markdown(f"**Status:** {status_icon} {status_text}")
            
            with col_actions:
                st.markdown("### Ações")
                
                # Botão Editar
                if st.button("✏️ Editar", key=f"edit_sol_{sol['id']}", use_container_width=True):
                    abrir_editar(sol['id'])
                    st.rerun()
                
                # Botão Ativar/Desativar
                btn_status_label = "🔴 Desativar" if sol['ativo'] else "🟢 Ativar"
                if st.button(btn_status_label, key=f"stat_sol_{sol['id']}", use_container_width=True):
                    try:
                        alternar_status_solicitante(sol['id'])
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ {e}")
                
                # Botão Excluir
                if st.button("🗑️ Excluir", key=f"del_sol_{sol['id']}", use_container_width=True, type="secondary"):
                    try:
                        excluir_solicitante(sol['id'])
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ {e}")

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