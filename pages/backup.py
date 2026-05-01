# pages/backup.py
"""
pages/backup.py
──────────────────────────────────────────────────────
Página para gerenciamento de Backups e Restauração.
Focada no Banco de Dados (Tipos de Exame, Solicitantes e Templates).
──────────────────────────────────────────────────────
"""

import sys
import os
import streamlit as st
import zipfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu
from core.auth import obter_usuario_logado
from database.db import DATABASE_PATH, importar_banco_de_dados

st.set_page_config(
    page_title="Backup e Restauração — LaudoPericial",
    page_icon="💾",
    layout="wide",
)

renderizar_menu()

usuario_logado = obter_usuario_logado()
if not usuario_logado:
    st.error("Usuário não autenticado.")
    st.stop()

def main():
    st.title("💾 Backup e Restauração")
    st.markdown("Gerencie a segurança dos seus modelos de laudo e cadastros base.")
    st.divider()

    # Cria abas para separar as funcionalidades
    tab1, tab2 = st.tabs(["📤 Exportar Backup", "📥 Restaurar Backup"])

    with tab1:
        st.subheader("Exportar Backup")
        st.info("Gera uma cópia contendo apenas as **configurações base** (Tipos de Exame, Solicitantes e Templates). As REPs e Laudos registrados serão descartados para manter o backup leve e focado em modelos.")

        if st.button("Gerar Backup de Configurações", type="primary"):
            try:
                from scripts.snapshot_db import criar_snapshot_limpo
                criar_snapshot_limpo()

                pasta_script = os.path.join(ROOT, "scripts")
                arquivo_backup = os.path.join(pasta_script, "backup_laudopericial.db")

                with open(arquivo_backup, "rb") as f:
                    st.download_button(
                        label="⬇️ Baixar Arquivo .db",
                        data=f,
                        file_name="backup_config_laudo.db",
                        mime="application/x-sqlite3"
                    )
                st.success("Backup essencial gerado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao gerar backup: {e}")

    with tab2:
        st.subheader("Restaurar Backup")
        st.warning("⚠️ A restauração substituirá todos os dados atuais!")

        arquivo_upload = st.file_uploader("Selecione o arquivo de backup (.db)", type="db")

        if arquivo_upload is not None:
            confirmar = st.checkbox("Confirmo que desejo substituir as configurações atuais.")

            if confirmar and st.button("Restaurar Configurações", type="secondary"):
                try:
                    # Salva o upload em um arquivo temporário
                    temp_db = os.path.join(ROOT, "temp_restore.db")
                    with open(temp_db, "wb") as f:
                        f.write(arquivo_upload.getbuffer())

                    # Usa a função de serviço para realizar a troca segura
                    importar_banco_de_dados(temp_db)

                    st.success("✅ Configurações restauradas com sucesso!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao restaurar: {e}")

if __name__ == "__main__":
    main()
