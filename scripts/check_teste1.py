import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import executar_query

laudo = executar_query("SELECT id, status FROM laudos WHERE rep_id = 12")
if laudo:
    print(f"Laudo vinculado: {dict(laudo[0])}")
else:
    print("Não tem laudo vinculado")

rep = executar_query("SELECT id, numero_rep, status FROM rep WHERE numero_rep = 'TESTE1'")
if rep:
    print(f"REP: {dict(rep[0])}")