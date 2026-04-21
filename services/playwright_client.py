"""
services/playwright_client.py
────────────────────────────────────────────────────
Cliente para geração de PDF com alta fidelidade usando Chromium.
────────────────────────────────────────────────────
"""

import os
import sys
import tempfile
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def gerar_pdf_do_html(html: str, pdf_path: str = None) -> bytes:
    """
    Gera PDF a partir de HTML usando Chromium via subprocess.
    """
    with tempfile.NamedTemporaryFile(
        mode='w',
        delete=False,
        suffix='.html',
        encoding='utf-8'
    ) as f:
        f.write(html)
        html_path = f.name

    output_path = pdf_path
    if not output_path:
        output_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix='.pdf'
        )
        output_path = output_file.name
        output_file.close()

    try:
        chrome_path = _encontrar_chromium()

        cmd = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--print-to-pdf={output_path}",
            "--print-to-pdf-no-header",
            "--virtual-time-budget=10000",
            html_path
        ]

        subprocess.run(cmd, capture_output=True, timeout=30)

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            raise Exception(f"PDF não foi gerado em {output_path}")

        pdf_bytes = Path(output_path).read_bytes()

        if not pdf_path:
            os.remove(output_path)

        return pdf_bytes

    except FileNotFoundError:
        raise FileNotFoundError(
            "Chromium não encontrado. Instale o Chromium ou Chrome."
        )
    except subprocess.TimeoutExpired:
        raise TimeoutError("Timeout ao gerar PDF")
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {e}")
        raise
    finally:
        try:
            os.remove(html_path)
        except:
            pass
        if pdf_path and os.path.exists(output_path) and not pdf_path:
            try:
                os.remove(output_path)
            except:
                pass


def _encontrar_chromium() -> str:
    """Encontra o caminho do Chromium ou Chrome."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Chromium local do projeto (preferido para deploy)
    chromium_local = os.path.join(base_dir, "chromium", "chrome.exe")
    if os.path.exists(chromium_local):
        return chromium_local
    
    # 2. Chromium do Playwright (instalação automática)
    chromium_playwright = os.path.expandvars(
        r"%LOCALAPPDATA%\ms-playwright\chromium-1208\chrome-win64\chrome.exe"
    )
    if os.path.exists(chromium_playwright):
        return chromium_playwright
    
    # 3. Chrome do sistema (fallback)
    caminhos = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    ]
    for caminho in caminhos:
        if os.path.exists(caminho):
            return caminho

    raise FileNotFoundError("Chromium/Chrome não encontrado")


def validar_html(html: str) -> bool:
    """Valida se HTML possui tags básicas obrigatórias."""
    required_tags = ['<html', '<head', '<body', '</html>']
    return all(tag in html.lower() for tag in required_tags)