import sqlite3
import os

db_path = 'laudopericial.db'
if not os.path.exists(db_path):
    print(f"Banco de dados não encontrado em {db_path}")
else:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("--- REP TESTE2 ---")
    cursor.execute("SELECT id, numero_rep, status, tipo_exame_id, usuario_id FROM rep WHERE numero_rep = 'TESTE2'")
    row = cursor.fetchone()
    if row:
        rep = dict(row)
        print(rep)
        
        print("\n--- LAUDOS VINCULADOS ---")
        cursor.execute("SELECT id, status, template_id FROM laudos WHERE rep_id = ?", (rep['id'],))
        laudos = cursor.fetchall()
        for l in laudos:
            print(dict(l))
    else:
        print("REP TESTE2 não encontrada.")
    
    conn.close()
