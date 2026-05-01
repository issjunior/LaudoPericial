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
from services.placeholders_custom_service import obter_mapeamento_placeholders_custom


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
    import html
    texto = html.unescape(texto)
    texto = re.sub(r'<span[^>]*>|</span>', '', texto)
    texto = re.sub(r'<p[^>]*>', '\n', texto)
    texto = re.sub(r'</p>', '\n', texto)
    texto = re.sub(r'<br\s*/?>', '\n', texto)
    texto = re.sub(r'<strong[^>]*>', '**', texto)
    texto = re.sub(r'</strong>', '**', texto)
    texto = re.sub(r'<b[^>]*>', '**', texto)
    texto = re.sub(r'</b>', '**', texto)
    texto = re.sub(r'<em[^>]*>', '_', texto)
    texto = re.sub(r'</em>', '_', texto)
    texto = re.sub(r'<i[^>]*>', '_', texto)
    texto = re.sub(r'</i>', '_', texto)
    texto = re.sub(r'<u[^>]*>', '', texto)
    texto = re.sub(r'</u>', '', texto)
    texto = re.sub(r'<div[^>]*>', '\n', texto)
    texto = re.sub(r'</div>', '\n', texto)
    texto = re.sub(r'<ul[^>]*>', '\n', texto)
    texto = re.sub(r'</ul>', '\n', texto)
    texto = re.sub(r'<ol[^>]*>', '\n', texto)
    texto = re.sub(r'</ol>', '\n', texto)
    texto = re.sub(r'<li[^>]*>', '- ', texto)
    texto = re.sub(r'</li>', '\n', texto)
    texto = re.sub(r'<a[^>]*>', '', texto)
    texto = re.sub(r'</a>', '', texto)
    texto = re.sub(r'<img[^>]*>', '', texto)
    texto = re.sub(r'<hr[^>]*>', '\n---\n', texto)
    texto = re.sub(r'<[^>]+>', '', texto)
    texto = texto.replace('&nbsp;', ' ')
    texto = texto.replace('&amp;', '&')
    texto = texto.replace('&lt;', '<')
    texto = texto.replace('&gt;', '>')
    texto = texto.replace('&quot;', '"')
    texto = texto.replace('&copy;', '(c)')
    texto = texto.replace('&reg;', '(R)')
    texto = texto.replace('&trade;', '(TM)')
    texto = texto.replace('\n\n\n', '\n\n')
    texto = texto.strip()
    return texto


def converter_html_pdf(texto: str) -> list:
    if not texto:
        return []
    import re
    import html
    texto = html.unescape(texto)
    padrao = re.compile(r'<p[^>]*>(.*?)</p>', re.DOTALL | re.IGNORECASE)
    matches = padrao.findall(texto)
    resultado = []
    from reportlab.lib.enums import TA_RIGHT, TA_LEFT
    for p in matches:
        p = p.strip()
        if not p:
            continue
        alinhamento = TA_JUSTIFY
        if 'text-align:center' in p or 'center' in p.lower():
            alinhamento = TA_CENTER
        elif 'text-align:right' in p or 'right' in p.lower():
            alinhamento = TA_RIGHT
        elif 'text-align:left' in p or 'left' in p.lower():
            alinhamento = TA_LEFT
        p = re.sub(r'<[^>]*>', '', p)
        p = p.replace('&nbsp;', ' ')
        p = p.replace('&amp;', '&')
        p = p.replace('&quot;', '"')
        p = p.strip()
        if p:
            resultado.append((p, alinhamento))
    if not resultado:
        texto_limpo = re.sub(r'<[^>]+>', '', texto)
        texto_limpo = texto_limpo.replace('&nbsp;', ' ').replace('&amp;', '&').strip()
        if texto_limpo:
            resultado.append((texto_limpo, TA_JUSTIFY))
    return resultado


def substituir_placeholders(texto: str, rep: dict, perito: dict) -> str:
    if not texto:
        return texto
    
    substituicoes = {
        '{{numero_rep}}': rep.get('numero_rep', ''),
        '{{data_solicitacao}}': formatar_data_br(rep.get('data_solicitacao', '')),
        '{{numero_documento}}': rep.get('numero_documento', ''),
        '{{data_documento}}': formatar_data_br(rep.get('data_documento', '')),
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
        '{{lacre_entrada}}': rep.get('lacre_entrada', ''),
        '{{lacre_saida}}': rep.get('lacre_saida', ''),
        '{{observacoes}}': rep.get('observacoes', ''),
        '{{perito_nome}}': perito.get('nome', ''),
        '{{perito_matricula}}': perito.get('matricula', ''),
        '{{perito_cargo}}': perito.get('cargo', ''),
        '{{perito_lotacao}}': perito.get('lotacao', ''),
        '{{cidade}}': perito.get('lotacao', ''),
    }

    # Acrescenta placeholders personalizados sem sobrescrever os placeholders nativos.
    for placeholder, valor in obter_mapeamento_placeholders_custom(com_chaves=True).items():
        if placeholder not in substituicoes:
            substituicoes[placeholder] = valor
    
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
        from reportlab.lib.enums import TA_RIGHT
        cabecalho_html = rows_cab[0]['conteudo']
        for texto, alinhamento in converter_html_pdf(cabecalho_html):
            texto = texto.replace('{{tipo_exame}}', rep.get('tipo_exame_nome', ''))
            texto = texto.replace('{{tipo_exame_codigo}}', rep.get('tipo_exame_codigo', ''))
            texto = texto.replace('{{numero_rep}}', rep.get('numero_rep', ''))
            texto = texto.replace('{{data_solicitacao}}', formatar_data_br(rep.get('data_solicitacao', '')))
            if texto.strip():
                estilo_par = ParagraphStyle(
                    'Cabecalho',
                    parent=styles['Normal'],
                    fontSize=11,
                    alignment=alinhamento,
                    spaceAfter=5
                )
                story.append(Paragraph(texto.strip(), estilo_par))
    else:
        story.append(Paragraph("LAUDO DE PERÍCIA CRIMINAL", estilo_titulo))
        story.append(Paragraph(f"({rep.get('tipo_exame_nome', 'N/A')})", estilo_subtitulo))
        story.append(Paragraph(f"Código: {rep.get('tipo_exame_codigo', 'N/A')}", estilo_info))
        story.append(Paragraph(f"REP: {rep['numero_rep']} | Data: {formatar_data_br(rep['data_solicitacao'])}", estilo_subtitulo))

    for idx, secao in enumerate(secoes, 1):
        story.append(Paragraph(f"{idx}. {secao['titulo'].upper()}", estilo_secao_titulo))
        paragrafos = converter_html_pdf(secao.get('conteudo') or '')
        if not paragrafos:
            story.append(Paragraph("(Secao vazia)", estilo_conteudo))
        else:
            for texto, alinhamento in paragrafos:
                texto = substituir_placeholders(texto, rep, perito)
                if texto.strip():
                    est = ParagraphStyle(
                        'Secao',
                        parent=styles['Normal'],
                        fontSize=11,
                        alignment=alinhamento,
                        spaceAfter=5
                    )
                    story.append(Paragraph(texto.strip(), est))

    story.append(Paragraph(f"<b>Perito Responsavel:</b> {perito.get('nome', 'N/A')}", estilo_info))
    story.append(Paragraph(f"<b>Data de Emissao:</b> {formatar_data_br(laudo.get('atualizado_em', ''))}", estilo_info))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
