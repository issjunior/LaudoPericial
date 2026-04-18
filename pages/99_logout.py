# pages/99_logout.py
"""
pages/99_logout.py
─────────────────────────────────────────────────────
Página de logout.
─────────────────────────────────────────────────────
"""

import sys
import os

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st

st.set_page_config(
    page_title="Saindo — LaudoPericial",
    page_icon="🚪",
    layout="centered",
)

from core.auth import fazer_logout

fazer_logout()

st.title("👋 Sessão Encerrada")
st.success("Logout realizado com sucesso!")

st.markdown("---")
st.markdown("Clique no botão abaixo para fazer login:")
st.page_link(
    "app.py",
    label="Ir para Login",
    icon="🔐",
    use_container_width=True
)