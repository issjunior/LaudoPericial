# services/gerador_pdf.py
"""
Servico para gerar PDF do Laudo.
"""

import os
import sys
import io
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
from database.db import executar_query


def formatar_data_br(data_iso: str) -> str:
    try:
        if not data_iso:
            return ""
        dt = datetime.fromisoformat(data_iso.replace(' ', 'T'))
        return dt.strftime("%d/%m/%Y")
    except:
        return data_iso or ""


def limpar_html(texto: str) -> str:
    if not texto:
        return ""
    import re
    texto = re.sub(r'<[^>]+>', '', texto)
    texto = texto.replace('&nbsp;', ' ')
    texto = texto.replace('&amp;', '&')
    texto = texto.replace('&lt;', '<')
    texto = texto.replace('&gt;', '>')
    texto = texto.replace('&quot;', '"')
    return texto


def gerar_pdf_laudo(laudo_id: int) -> bytes:
    from services.laudo_service import buscar_laudo, listar_secoes_laudo
    from services.rep_service import buscar_rep

    laudo = buscar_laudo(laudo_id)
    if not laudo:
        raise ValueError("Laudo nao encontrado")

    rep = buscar_rep(laudo['rep_id'])
    secoes = listar_secoes_laudo(laudo_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=20,
        bold=True
    )

    estilo_subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=15,
        textColor=colors.gray
    )

    estilo_info = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=5
    )

    estilo_secao_titulo = ParagraphStyle(
        'SecaoTitulo',
        parent=styles['Heading2'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=15,
        bold=True
    )

    estilo_conteudo = ParagraphStyle(
        'Conteudo',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=15,
        leading=16
    )

    story.append(Paragraph("LAUDO PERICIAL", estilo_titulo))
    story.append(Paragraph(f"REP: {rep['numero_rep']} | Tipo: {rep['tipo_exame_nome']} | Data: {formatar_data_br(rep['data_solicitacao'])}", estilo_subtitulo))

    story.append(Paragraph("<b>DADOS DO LAUDO</b>", styles['Heading3']))
    story.append(Paragraph(f"<b>Periciado:</b> {rep.get('nome_envolvido', 'N/A')}", estilo_info))
    story.append(Paragraph(f"<b>Solicitante:</b> {rep.get('solicitante_nome', 'N/A')}", estilo_info))
    story.append(Paragraph(f"<b>Autoridade Requerente:</b> {rep.get('nome_autoridade', 'N/A')}", estilo_info))
    story.append(Paragraph(f"<b>Local do Fato:</b> {rep.get('local_fato', 'N/A')}", estilo_info))
    story.append(Paragraph(f"<b>Objeto do Exame:</b> {rep.get('objeto_exame', 'N/A')}", estilo_info))

    from database.db import executar_query
    sql = "SELECT nome FROM usuarios WHERE id = ?"
    rows = executar_query(sql, (laudo['usuario_id'],))
    perito_nome = rows[0]['nome'] if rows else "N/A"

    story.append(Paragraph("<b>LAUDO</b>", styles['Heading3']))

    preambulo = f"No dia {formatar_data_br(rep['data_solicitacao'])}, a requisicao de exame pericial foi devidamente recebida por este Nucleo de Pericia Oficial, tendo sido autuada sob o numero {rep['numero_rep']}. O presente laudo tem por objetivo apresentar os resultados do exame realizado."
    story.append(Paragraph(preambulo, estilo_conteudo))

    for idx, secao in enumerate(secoes, 1):
        story.append(Paragraph(f"{idx}. {secao['titulo'].upper()}", estilo_secao_titulo))
        conteudo = limpar_html(secao.get('conteudo') or '')
        if conteudo:
            story.append(Paragraph(conteudo, estilo_conteudo))
        else:
            story.append(Paragraph("<i>(Secao vazia)</i>", estilo_conteudo))

    story.append(Paragraph(f"<b>Perito Responsavel:</b> {perito_nome}", estilo_info))
    story.append(Paragraph(f"<b>Data de Emissao:</b> {formatar_data_br(laudo.get('atualizado_em', ''))}", estilo_info))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
