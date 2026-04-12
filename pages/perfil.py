# pages/perfil.py
"""
pages/perfil.py
──────────────────────────────────────────────────────
Página de perfil e configurações do usuário.
──────────────────────────────────────────────────────
"""

import sys
import os
import streamlit as st

# Garante que a raiz do projeto está no sys.path
ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu
from core.auth import obter_usuario_logado, exigir_autenticacao

# ──────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Perfil e Configurações — LaudoPericial",
    page_icon="👤",
    layout="wide",
)

# Defina a página atual na sessão para o menu funcionar corretamente
st.session_state["_active_page"] = __file__

# Renderiza o menu lateral (já exige autenticação)
renderizar_menu()

st.title("👤 Perfil e Configurações")
st.write("Página de perfil — será preenchida em breve.")
