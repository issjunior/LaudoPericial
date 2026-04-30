"""
scripts/snapshot_db.py
──────────────────────────────────────────────────────
Script para criar um Backup LIMPO (Apenas Configurações).
Preserva: Usuários, Tipos de Exame, Solicitantes e Templates.
Descarta: REPs, Laudos e Histórico.
──────────────────────────────────────────────────────
"""

import os
import sqlite3
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import DATABASE_PATH
from database.models import CREATE_ALL_TABLES

def criar_snapshot_limpo():
    pasta_script = Path(__file__).resolve().parent
    arquivo_backup = pasta_script / "backup_laudopericial.db"
    
    if arquivo_backup.exists():
        os.remove(arquivo_backup)

    print(f"📦 Iniciando extração do Backup Essencial...")

    try:
        # 1. Cria o banco de backup e suas tabelas
        conn_backup = sqlite3.connect(str(arquivo_backup))
        for sql in CREATE_ALL_TABLES:
            conn_backup.execute(sql)
        conn_backup.commit()

        # 2. Conecta ao banco atual e anexa o backup para transferência
        conn_origem = sqlite3.connect(str(DATABASE_PATH))
        conn_origem.execute(f"ATTACH DATABASE '{str(arquivo_backup)}' AS backup")

        # 3. Lista de tabelas essenciais para copiar
        tabelas_essenciais = [
            "usuarios",
            "tipos_exame",
            "solicitantes",
            "templates",
            "secoes_template",
            "modelo_cabecalho"
        ]

        for tabela in tabelas_essenciais:
            print(f"  - Copiando tabela: {tabela}")
            conn_origem.execute(f"INSERT INTO backup.{tabela} SELECT * FROM main.{tabela}")
        
        conn_origem.commit()
        conn_origem.close()
        conn_backup.close()

        print(f"\n✅ Backup ESSENCIAL criado com sucesso em: {arquivo_backup}")
        print(f"💡 REPs e Laudos foram descartados deste arquivo.")

    except Exception as e:
        print(f"❌ Erro ao criar backup limpo: {e}")

if __name__ == "__main__":
    criar_snapshot_limpo()
