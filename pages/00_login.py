# pages/00_login.py
"""
pages/00_login.py
─────────────────────────────────────────────────────
Página de login do sistema LaudoPericial.
─────────────────────────────────────────────────────
"""

import sys
import os
import streamlit as st
from datetime import date

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.db import init_database, executar_query
from core.auth import (
    usuario_existe,
    criar_usuario,
    fazer_login,
    fazer_logout,
    esta_autenticado,
    verificar_senha,
    gerar_hash_senha,
)

init_database()

st.set_page_config(
    page_title="Login — LaudoPericial",
    page_icon="🔐",
    layout="centered",
)

if esta_autenticado():
    st.switch_page("app.py")

def main():
    st.title("🔐 LaudoPericial PCPR")
    st.markdown("Sistema de Gestão de Laudos Periciais")
    st.markdown("---")

    tab_login, tab_cadastro = st.tabs(["Login", "Primeiro Acesso"])

    with tab_login:
        with st.form("form_login"):
            username = st.text_input("Usuário", placeholder="izaias.santos")
            senha = st.text_input("Senha", type="password")

            submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)

            if submitted:
                if not username or not senha:
                    st.error("Preencha usuário e senha.")
                else:
                    try:
                        fazer_login(username, senha)
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

    with tab_cadastro:
        if usuario_existe():
            st.info("Já existe usuário cadastrado. Faça login acima.")
        else:
            st.warning("Primeiro acesso. Crie seu usuário.")
            with st.form("form_cadastro"):
                nome = st.text_input("Nome Completo", placeholder="João da Silva")
                cargo = st.text_input("Cargo", value="Perito Oficial Criminal")
                lotacao = st.text_input("Lotação", placeholder="Laboratório de Perícia")
                username = st.text_input("Usuário (prefixo do email)", placeholder="joao.silva")
                email = st.text_input("Email", placeholder="joao.silva@policiacientifica.pr.gov.br")
                senha = st.text_input("Senha", type="password")
                confirmar_senha = st.text_input("Confirmar Senha", type="password")

                submitted = st.form_submit_button("Cadastrar", type="primary", use_container_width=True)

                if submitted:
                    if not all([nome, cargo, lotacao, username, email, senha, confirmar_senha]):
                        st.error("Preencha todos os campos.")
                    elif senha != confirmar_senha:
                        st.error("As senhas não conferem.")
                    else:
                        try:
                            criar_usuario(
                                nome=nome,
                                cargo=cargo,
                                lotacao=lotacao,
                                username=username,
                                email=email,
                                senha=senha
                            )
                            st.success("Usuário criado! Faça login.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro: {e}")

if __name__ == "__main__":
    main()