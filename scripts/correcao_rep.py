import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import executar_comando, executar_query

# Corrigir REPs com tipo_exame_id = 0 ou NULL
reps = executar_query("SELECT id, numero_rep, tipo_exame_id, status FROM rep")
corrigidas = 0

for r in reps:
    r = dict(r)
    tid = r['tipo_exame_id']
    if tid == 0 or tid is None:
        if r['status'] != 'Pendente':
            print(f"Corrigindo {r['numero_rep']}: status {r['status']} -> Pendente")
            executar_comando("UPDATE rep SET status = ? WHERE id = ?", ("Pendente", r['id']))
            corrigidas += 1
        else:
            print(f"{r['numero_rep']}: ja Pendente (ok)")

print(f"\n{corrigidas} REP(s) corrigida(s)")