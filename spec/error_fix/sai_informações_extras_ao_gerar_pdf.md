# Remeta Informacoes Extras do PDF

## Problema

O PDF gerado pelo Chrome/Chromium continha informacoes extras automaticas:
- **Cabecalho**: `21/04/2026, 21:45 Laudo Pericial` (data/hora + titulo)
- **Rodape**: `file:///C:/Users/Jr/AppData/Local/Temp/tmpmdxfvhel.html 1/1` (caminho do arquivo temporario + numero da pagina)

## Solucao

Modificar o comando do Chrome em `services/playwright_client.py` para desabilitar o cabecalho e rodape automaticos.

### Arquivo Modificado

`services/playwright_client.py` - Linha 50

### Alteracao

Adicionar a flag `--no-pdf-header-footer` ao comando do Chrome:

```python
cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    f"--print-to-pdf={output_path}",
    "--no-pdf-header-footer",  # <-- Nova flag adicionada
    "--virtual-time-budget=15000",
    html_path
]
```

## Data

21/04/2026