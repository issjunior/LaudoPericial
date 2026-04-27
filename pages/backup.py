# pages/backup.py
"""
pages/backup.py
──────────────────────────────────────────────────────
Página para gerenciamento de backup (exportação e importação)
do banco de dados.
──────────────────────────────────────────────────────
"""

import sys
import os
import streamlit as st
import shutil
from datetime import datetime
from pathlib import Path

# Garante que a raiz do projeto está no sys.path
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_script_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from components.menu import renderizar_menu
from core.auth import obter_usuario_logado, exigir_autenticacao
from core.path_utils import get_permanent_root

# ──────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Backup do Banco de Dados — LaudoPericial",
    page_icon="💾",
    layout="wide",
)

# Defina a página atual na sessão para o menu funcionar corretamente
st.session_state["_active_page"] = __file__

# Renderiza o menu lateral (já exige autenticação)
renderizar_menu()

# Obtém o usuário logado
usuario_logado = obter_usuario_logado()
if not usuario_logado:
    st.error("Usuário não autenticado. Por favor, faça login.")
    st.stop()

# Caminho para o arquivo do banco de dados
# get_permanent_root() retorna a pasta do .exe (em modo empacotado)
# ou a raiz do projeto (em modo dev) — igual ao que database/db.py usa.
PERMANENT_ROOT = get_permanent_root()
DB_NAME = os.getenv("DATABASE_NAME", "laudopericial.db")
DB_PATH = str(PERMANENT_ROOT / DB_NAME)

# ──────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ──────────────────────────────────────────────────────

def _obter_data_modificacao_arquivo(caminho_arquivo: str) -> str:
    """
    Retorna a data e hora da última modificação de um arquivo.
    """
    if os.path.exists(caminho_arquivo):
        timestamp = os.path.getmtime(caminho_arquivo)
        return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")
    return "N/A (arquivo não encontrado)"

# ──────────────────────────────────────────────────────
# FUNÇÕES DE EXPORTAÇÃO/IMPORTAÇÃO
# ──────────────────────────────────────────────────────

def exportar_banco_dados():
    """
    Cria um backup do arquivo do banco de dados e permite download.
    """
    st.subheader("📥 Exportar Banco de Dados")
    st.write("Crie um backup do seu banco de dados atual.")

    data_modificacao_atual = _obter_data_modificacao_arquivo(DB_PATH)
    st.info(f"**Última modificação do banco de dados atual:** `{data_modificacao_atual}`")

    if st.button("Gerar Backup do Banco de Dados", type="primary", use_container_width=True):
        if os.path.exists(DB_PATH):
            try:
                # Cria um nome de arquivo de backup com timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_filename = f"laudopericial_backup_{timestamp}.db"

                # Lê o conteúdo do arquivo do banco de dados
                with open(DB_PATH, "rb") as f:
                    db_bytes = f.read()

                st.download_button(
                    label="Clique para Baixar o Backup",
                    data=db_bytes,
                    file_name=backup_filename,
                    mime="application/octet-stream",
                    use_container_width=True
                )
                st.success("Backup gerado com sucesso! Clique no botão acima para baixar.")
            except Exception as e:
                st.error(f"❌ Erro ao gerar backup: {e}")
        else:
            st.warning("⚠️ O arquivo do banco de dados não foi encontrado.")

def importar_banco_dados():
    """
    Permite ao usuário fazer upload de um arquivo de banco de dados
    para substituir o atual.
    """
    st.subheader("📤 Importar Banco de Dados")

    data_modificacao_atual = _obter_data_modificacao_arquivo(DB_PATH)
    st.warning(
        f"⚠️ **ATENÇÃO:** A importação de um novo banco de dados "
        f"**SOBRESCREVERÁ** o banco de dados atual (última modificação: `{data_modificacao_atual}`). "
        "Certifique-se de ter um backup antes de prosseguir."
    )
    st.write("Faça upload de um arquivo `.db` para restaurar o sistema.")

    uploaded_file = st.file_uploader(
        "Escolha um arquivo .db para importar",
        type=["db"],
        help="Selecione o arquivo de backup do banco de dados (.db) que deseja restaurar."
    )

    if uploaded_file is not None:
        data_modificacao_novo = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        st.info(f"**Arquivo a ser importado:** `{uploaded_file.name}` (será o banco de dados com data: `{data_modificacao_novo}`)")


        if st.button("Confirmar Importação", type="secondary", use_container_width=True):
            try:
                # Salva o arquivo temporariamente na pasta permanente (não em _MEIPASS)
                temp_db_path = str(PERMANENT_ROOT / "temp_laudopericial.db")
                with open(temp_db_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Usa a função do db.py para fechar a conexão, trocar o arquivo e reabrir
                from database.db import importar_banco_de_dados
                importar_banco_de_dados(temp_db_path)

                st.success(
                    "✅ Banco de dados importado com sucesso! "
                    "**Por favor, reinicie o Streamlit para que as alterações sejam aplicadas.**"
                )
                st.info("Para reiniciar, feche a janela do terminal onde o Streamlit está rodando e execute `streamlit run app.py` novamente.")
            except Exception as e:
                st.error(f"❌ Erro ao importar banco de dados: {e}")

# ──────────────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ──────────────────────────────────────────────────────

def main():
    st.title("💾 Gerenciamento de Backup do Banco de Dados") # ATUALIZADO
    st.markdown("Exporte ou importe o arquivo do banco de dados para backup e restauração.")
    st.markdown("---")

    tab_exportar, tab_importar = st.tabs(["📥 Exportar", "📤 Importar"])

    with tab_exportar:
        exportar_banco_dados()

    with tab_importar:
        importar_banco_dados()

main()