import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import executar_comando, executar_query

# Excluir laudo vinculado
executar_comando("DELETE FROM laudos WHERE rep_id = 12")
print("Laudo ID 8 excluído")

# Atualizar REP para Pendente
executar_comando("UPDATE rep SET status = 'Pendente' WHERE id = 12")
print("REP TESTE1 atualizada para Pendente")