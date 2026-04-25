import os
import sys
from pathlib import Path

def get_root():
    """
    Retorna o caminho raiz do projeto de forma robusta,
    suportando tanto execução via script quanto via executável (PyInstaller).
    """
    if getattr(sys, 'frozen', False):
        # Se estiver rodando como executável (.exe)
        # sys._MEIPASS é a pasta temporária onde o PyInstaller extrai os arquivos
        return Path(sys._MEIPASS).resolve()
    else:
        # Se estiver rodando como script (.py)
        # Assume que o arquivo está em core/path_utils.py, então a raiz é o pai do pai
        return Path(__file__).resolve().parent.parent

def get_permanent_root():
    """
    Retorna a pasta onde o executável .exe está fisicamente localizado (não a pasta temporária).
    Útil para salvar o banco de dados e arquivos exportados.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent.resolve()
    else:
        return Path(__file__).resolve().parent.parent
