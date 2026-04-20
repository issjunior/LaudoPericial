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


def substituir_placeholders(texto: str, rep: dict, perito: dict) -> str:
    if not texto:
        return texto
    
    substituicoes = {
        '{{numero_rep}}': rep.get('numero_rep', ''),
        '{{data_solicitacao}}': rep.get('data_solicitacao', ''),
        '{{numero_documento}}': rep.get('numero_documento', ''),
        '{{data_documento}}': rep.get('data_documento', ''),
        '{{tipo_solicitacao}}': rep.get('tipo_solicitacao', ''),
        '{{tipo_exame}}': rep.get('tipo_exame_nome', ''),
        '{{nome_autoridade}}': rep.get('nome_autoridade', ''),
        '{{nome_envolvido}}': rep.get('nome_envolvido', ''),
        '{{local_fato}}': rep.get('local_fato_descricao', ''),
        '{{solicitante}}': rep.get('solicitante_nome', ''),
        '{{solicitante_orgao}}': rep.get('solicitante_orgao', ''),
        '{{horario_acionamento}}': rep.get('horario_acionamento', ''),
        '{{horario_chegada}}': rep.get('horario_chegada', ''),
        '{{horario_saida}}': rep.get('horario_saida', ''),
        '{{latitude}}': rep.get('latitude', ''),
        '{{longitude}}': rep.get('longitude', ''),
        '{{perito_nome}}': perito.get('nome', ''),
        '{{perito_matricula}}': perito.get('matricula', ''),
        '{{perito_cargo}}': perito.get('cargo', ''),
        '{{perito_lotacao}}': perito.get('lotacao', ''),
    }
    
    resultado = texto
    for placeholder, valor in substituicoes.items():
        resultado = resultado.replace(placeholder, valor or '')
    
    return resultado


def gerar_pdf_laudo(laudo_id: int) -> bytes:
    from services.laudo_service import buscar_laudo, listar_secoes_laudo
    from services.rep_service import buscar_rep

    laudo = buscar_laudo(laudo_id)
    if not laudo:
        raise ValueError("Laudo nao encontrado")

    rep = buscar_rep(laudo['rep_id'])
    secoes = listar_secoes_laudo(laudo_id)
    
    sql = "SELECT nome, matricula, cargo, lotacao FROM usuarios WHERE id = ?"
    rows = executar_query(sql, (laudo['usuario_id'],))
    perito = dict(rows[0]) if rows else {}

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

    sql_cab = "SELECT conteudo FROM modelo_cabecalho WHERE ativo = 1 LIMIT 1"
    rows_cab = executar_query(sql_cab)
    if rows_cab:
        cabecalho = rows_cab[0]['conteudo']
        cabecalho = cabecalho.replace('{{tipo_exame}}', rep.get('tipo_exame_nome', ''))
        cabecalho = cabecalho.replace('{{tipo_exame_codigo}}', rep.get('tipo_exame_codigo', ''))
        cabecalho = cabecalho.replace('{{numero_rep}}', rep.get('numero_rep', ''))
        cabecalho = cabecalho.replace('{{data_solicitacao}}', rep.get('data_solicitacao', ''))
        for linha in cabecalho.split('\n'):
            if linha.strip():
                story.append(Paragraph(linha.strip(), estilo_titulo if linha.startswith('LAUDO') else estilo_info))
    else:
        story.append(Paragraph("LAUDO DE PERÍCIA CRIMINAL", estilo_titulo))
        story.append(Paragraph(f"({rep.get('tipo_exame_nome', 'N/A')})", estilo_subtitulo))
        story.append(Paragraph(f"Código: {rep.get('tipo_exame_codigo', 'N/A')}", estilo_info))
        story.append(Paragraph(f"REP: {rep['numero_rep']} | Data: {formatar_data_br(rep['data_solicitacao'])}", estilo_subtitulo))

    for idx, secao in enumerate(secoes, 1):
        story.append(Paragraph(f"{idx}. {secao['titulo'].upper()}", estilo_secao_titulo))
        conteudo = limpar_html(secao.get('conteudo') or '')
        conteudo = substituir_placeholders(conteudo, rep, perito)
        if conteudo:
            story.append(Paragraph(conteudo, estilo_conteudo))
        else:
            story.append(Paragraph("<i>(Secao vazia)</i>", estilo_conteudo))

    story.append(Paragraph(f"<b>Perito Responsavel:</b> {perito.get('nome', 'N/A')}", estilo_info))
    story.append(Paragraph(f"<b>Data de Emissao:</b> {formatar_data_br(laudo.get('atualizado_em', ''))}", estilo_info))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
