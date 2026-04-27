"""
services/placeholders_custom_service.py
──────────────────────────────────────────────────────
Serviço para gerenciamento de placeholders personalizados.
Persistência em arquivo JSON em data/placeholders_custom.json
com migração automática de data/custom_placeholders.json.
──────────────────────────────────────────────────────
"""

import json
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

NOVO_ARQUIVO = Path(ROOT) / "data" / "placeholders_custom.json"
ARQUIVO_LEGADO = Path(ROOT) / "data" / "custom_placeholders.json"


def _normalizar_item(item: dict) -> dict:
    nome = (item.get("nome") or "").strip().lower().replace(" ", "_")
    # Compatibilidade retroativa: "descricao" virou "valor"
    valor = item.get("valor")
    if valor is None:
        valor = item.get("descricao", "")
    valor = str(valor or "").strip()
    exemplo = str(item.get("exemplo", "") or "").strip()
    return {"nome": nome, "valor": valor, "exemplo": exemplo}


def listar_placeholders_custom() -> list:
    origem = NOVO_ARQUIVO if NOVO_ARQUIVO.exists() else ARQUIVO_LEGADO
    if not origem.exists():
        return []
    try:
        with open(origem, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if not isinstance(dados, list):
            return []
        normalizados = [_normalizar_item(item) for item in dados if isinstance(item, dict)]
        # Limpa itens inválidos sem nome
        return [item for item in normalizados if item["nome"]]
    except Exception:
        return []


def salvar_placeholders_custom(lista: list) -> None:
    NOVO_ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    normalizados = [_normalizar_item(item) for item in lista if isinstance(item, dict)]
    normalizados = [item for item in normalizados if item["nome"]]
    with open(NOVO_ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(normalizados, f, ensure_ascii=False, indent=2)


def obter_mapeamento_placeholders_custom(com_chaves: bool = False) -> dict:
    placeholders = listar_placeholders_custom()
    if com_chaves:
        return {f"{{{{{item['nome']}}}}}": item.get("valor", "") for item in placeholders}
    return {item["nome"]: item.get("valor", "") for item in placeholders}

