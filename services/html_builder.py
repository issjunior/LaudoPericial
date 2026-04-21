"""
services/html_builder.py
─────────────────────────────────────────────────────
Construtor de HTML consolidado do Laudo para PDF.
Monta um documento HTML único com CSS otimizado para impressão.
─────────────────────────────────────────────────────
"""

import logging

logger = logging.getLogger(__name__)


# CSS otimizado para impressão - mantém formatação do Jodit
CSS_IMPRESSAO = """
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html {
        font-size: 16px;
    }
    
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
        background: white;
    }
    
    /* Cabeçalho */
    .laudo-header {
        border-bottom: 3px solid #000;
        padding-bottom: 15px;
        margin-bottom: 20px;
        page-break-after: avoid;
    }
    
    .laudo-header h1 {
        font-size: 16pt;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }
    
    .laudo-header .info-linha {
        text-align: center;
        font-size: 10pt;
        line-height: 1.4;
        margin: 2px 0;
    }
    
    /* Seções */
    .laudo-secao {
        margin-bottom: 15px;
        page-break-inside: avoid;
    }
    
    .laudo-secao h2 {
        font-size: 14pt;
        font-weight: bold;
        background-color: #f5f5f5;
        padding: 8px 10px;
        border-left: 4px solid #2c3e50;
        margin-bottom: 10px;
        page-break-after: avoid;
    }
    
    .laudo-secao-conteudo {
        padding-left: 10px;
        text-align: justify;
    }
    
    /* Parágrafos */
    p {
        margin: 8px 0;
        text-align: justify;
    }
    
    /* Listas */
    ul, ol {
        margin: 10px 0 10px 30px;
    }
    
    li {
        margin: 5px 0;
        text-align: justify;
    }
    
    /* Tabelas */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        page-break-inside: avoid;
    }
    
    table thead {
        background-color: #e8e8e8;
    }
    
    table th {
        border: 1px solid #999;
        padding: 8px;
        text-align: left;
        font-weight: bold;
        font-size: 10pt;
    }
    
    table td {
        border: 1px solid #999;
        padding: 8px;
        font-size: 10pt;
    }
    
    table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    /* Links e formatação */
    a {
        color: #0066cc;
        text-decoration: none;
    }
    
    strong, b {
        font-weight: bold;
    }
    
    em, i {
        font-style: italic;
    }
    
    u {
        text-decoration: underline;
    }
    
    /* Blocos de código/citação */
    blockquote {
        border-left: 4px solid #ccc;
        padding-left: 15px;
        margin-left: 0;
        margin: 10px 0;
        color: #666;
        font-style: italic;
    }
    
    code {
        background-color: #f4f4f4;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
    }
    
    pre {
        background-color: #f4f4f4;
        padding: 10px;
        border-radius: 4px;
        overflow-x: auto;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        font-size: 10pt;
    }
    
    /* Imagens */
    img {
        max-width: 100%;
        height: auto;
        margin: 10px 0;
        page-break-inside: avoid;
    }
    
    /* Quebra de página */
    .page-break {
        page-break-before: always;
        margin-top: 20px;
    }
    
    /* Rodapé */
    .laudo-footer {
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #999;
        text-align: center;
        font-size: 9pt;
        color: #666;
        page-break-before: avoid;
    }
    
    @media print {
        body {
            background: white;
        }
        
        a {
            text-decoration: underline;
        }
        
        .no-print {
            display: none;
        }
    }
"""


def construir_html_laudo(
    cabecalho_html: str,
    secoes: list,
    rodape_html: str = None
) -> str:
    """
    Monta HTML consolidado do laudo com CSS de impressão.
    
    Args:
        cabecalho_html: HTML do cabeçalho (pré-renderizado com placeholders substituídos)
        secoes: Lista de dicts com {'titulo': str, 'conteudo': str (HTML)}
        rodape_html: HTML opcional para rodapé
        
    Returns:
        str: HTML completo do documento
    """
    
    # Validar entrada
    if not isinstance(secoes, list) or len(secoes) == 0:
        logger.warning("Lista de seções vazia ou inválida")
        secoes = []
    
    # Construir HTML
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Laudo Pericial</title>
    <style>
{CSS_IMPRESSAO}
    </style>
</head>
<body>
"""
    
    # Adicionar cabeçalho
    if cabecalho_html:
        html += f"""    <div class="laudo-header">
{cabecalho_html}
    </div>
"""
    
    # Adicionar seções
    for idx, secao in enumerate(secoes):
        titulo = secao.get('titulo', f'Seção {idx + 1}').upper()
        conteudo = secao.get('conteudo', '')
        
        html += f"""    <div class="laudo-secao">
        <h2>{titulo}</h2>
        <div class="laudo-secao-conteudo">
{conteudo}
        </div>
    </div>
"""
    
    # Adicionar rodapé
    if rodape_html:
        html += f"""    <div class="laudo-footer">
{rodape_html}
    </div>
"""
    
    html += """</body>
</html>"""
    
    return html


def processar_placeholders(
    texto: str,
    placeholders: dict
) -> str:
    """
    Substitui placeholders em texto HTML por valores reais.
    
    Args:
        texto: String com placeholders (ex: "{{chave}}")
        placeholders: Dict com valores {chave: valor}
        
    Returns:
        str: Texto com placeholders substituídos
    """
    resultado = texto
    for chave, valor in placeholders.items():
        # Converter valor para string e escapar caracteres especiais HTML se necessário
        valor_str = str(valor or '')
        placeholder = f"{{{{{chave}}}}}"
        resultado = resultado.replace(placeholder, valor_str)
    
    return resultado


def preparar_secoes_para_html(
    secoes_banco: list,
    placeholders: dict
) -> list:
    """
    Prepara seções do banco de dados para renderização em HTML.
    Substitui placeholders e valida conteúdo.
    
    Args:
        secoes_banco: Lista de seções do banco (com 'titulo' e 'conteudo')
        placeholders: Dict com dados para substituir placeholders
        
    Returns:
        list: Seções prontas para HTML
    """
    secoes_processadas = []
    
    for secao in secoes_banco:
        titulo = secao.get('titulo', '')
        conteudo = secao.get('conteudo', '')
        
        # Processar conteúdo (substituir placeholders e remover tags perigosas)
        conteudo_processado = processar_placeholders(conteudo, placeholders)
        
        secoes_processadas.append({
            'titulo': titulo,
            'conteudo': conteudo_processado
        })
    
    return secoes_processadas


def limpar_html_para_pdf(html: str) -> str:
    """
    Remove elementos que podem causar problemas no Playwright.
    Ex: scripts, iframes, mídia externa.
    
    Args:
        html: HTML bruto
        
    Returns:
        str: HTML limpo
    """
    import re
    
    # Remover scripts
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remover iframes
    html = re.sub(r'<iframe[^>]*>.*?</iframe>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remover comentários HTML
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Remover estilos inline que podem quebrar o layout
    html = re.sub(r'(style=")([^"]*)(page-break|display:\s*none)([^"]*)(")', r'\1\2\5', html)
    
    return html
