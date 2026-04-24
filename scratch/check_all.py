import sqlite3
import os

db_path = 'laudopericial.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("--- TODOS OS LAUDOS ---")
cursor.execute("""
    SELECT l.id, l.rep_id, r.numero_rep, r.usuario_id, l.status as laudo_status, r.status as rep_status
    FROM laudos l
    JOIN rep r ON l.rep_id = r.id
""")
laudos = cursor.fetchall()
for l in laudos:
    print(dict(l))

print("\n--- TODOS OS USUARIOS ---")
cursor.execute("SELECT id, nome, login FROM usuarios")
users = cursor.fetchall()
for u in users:
    print(dict(u))

conn.close()
