"""
services/gerador_pdf_playwright.py
─────────────────────────────────────────────────────
Gerador de PDF com Playwright (Chromium).
Mantém toda formatação CSS, tabelas, imagens e layout complexo.
Substitui o antigo gerador_pdf.py (ReportLab) com preservação visual.
─────────────────────────────────────────────────────
"""

import sys
import os
import logging
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from services.playwright_client import gerar_pdf_do_html, validar_html
from services.html_builder import (
    construir_html_laudo,
    processar_placeholders,
    preparar_secoes_para_html,
    limpar_html_para_pdf
)
from services.laudo_service import buscar_laudo, listar_secoes_laudo
from services.rep_service import buscar_rep
from database.db import executar_query

logger = logging.getLogger(__name__)


def formatar_data_br(data_valor) -> str:
    """
    Converte datas ISO (YYYY-MM-DD ou YYYY-MM-DD HH:MM:SS) para DD/MM/AAAA.
    Se não conseguir converter, devolve o valor original como string.
    """
    if not data_valor:
        return ""

    texto = str(data_valor).strip()
    if not texto:
        return ""

    try:
        dt = datetime.fromisoformat(texto.replace(" ", "T"))
        return dt.strftime("%d/%m/%Y")
    except Exception:
        pass

    try:
        dt = datetime.strptime(texto.split(" ")[0], "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return texto


def colher_dados_contexto(laudo_id: int) -> dict:
    """
    Colhe todos os dados de contexto necessários para preencher placeholders.
    
    Args:
        laudo_id: ID do laudo
        
    Returns:
        dict: Dicionário com placeholders e seus valores
    """
    try:
        laudo = buscar_laudo(laudo_id)
        if not laudo:
            raise ValueError(f"Laudo {laudo_id} não encontrado")
        
        rep = buscar_rep(laudo['rep_id'])
        if not rep:
            raise ValueError(f"REP {laudo['rep_id']} não encontrada")
        
        # Buscar dados do solicitante
        solicitante = {}
        if rep.get('solicitante_id'):
            sql = "SELECT * FROM solicitantes WHERE id = ?"
            rows = executar_query(sql, (rep['solicitante_id'],))
            if rows:
                solicitante = dict(rows[0])
        
        # Buscar dados do perito (usuário que criou o laudo)
        perito = {}
        if laudo.get('criado_por'):
            sql = "SELECT id, nome, matricula, cargo, lotacao FROM usuarios WHERE id = ?"
            rows = executar_query(sql, (laudo['criado_por'],))
            if rows:
                perito = dict(rows[0])
        
        # Buscar tipo de exame
        tipo_exame = {}
        if rep.get('tipo_exame_id'):
            sql = "SELECT id, nome, codigo FROM tipos_exame WHERE id = ?"
            rows = executar_query(sql, (rep['tipo_exame_id'],))
            if rows:
                tipo_exame = dict(rows[0])
        
        # Montar dicionário de placeholders
        placeholders = {
            # Dados da REP
            'numero_rep': rep.get('numero_rep', ''),
            'data_solicitacao': formatar_data_br(rep.get('data_solicitacao', '')),
            'tipo_exame': tipo_exame.get('nome', ''),
            'tipo_exame_codigo': tipo_exame.get('codigo', ''),
            'nome_envolvido': rep.get('nome_envolvido', ''),
            
            # Dados do solicitante
            'solicitante': solicitante.get('nome_orgao', ''),
            'solicitante_orgao': solicitante.get('nome_orgao', ''),
            'nome_autoridade': solicitante.get('nome_autoridade', ''),
            
            # Detalhes da solicitação
            'tipo_solicitacao': rep.get('tipo_solicitacao', ''),
            'numero_documento': rep.get('numero_documento', ''),
            'data_documento': formatar_data_br(rep.get('data_documento', '')),
            
            # Dados do local
            'local_fato': rep.get('local_fato', ''),
            'horario_acionamento': rep.get('horario_acionamento', ''),
            'horario_chegada': rep.get('horario_chegada', ''),
            'horario_saida': rep.get('horario_saida', ''),
            'latitude': rep.get('latitude', ''),
            'longitude': rep.get('longitude', ''),
            
            # Dados do perito
            'perito_nome': perito.get('nome', ''),
            'perito_matricula': perito.get('matricula', ''),
            'perito_cargo': perito.get('cargo', ''),
            'perito_lotacao': perito.get('lotacao', ''),
            'cidade': perito.get('lotacao', ''),
        }
        
        return placeholders
        
    except Exception as e:
        logger.error(f"Erro ao colher dados de contexto: {e}")
        raise


def buscar_cabecalho_processado(placeholders: dict) -> str:
    """
    Busca template de cabeçalho do banco e processa placeholders.
    
    Args:
        placeholders: Dicionário com valores para substituir
        
    Returns:
        str: HTML do cabeçalho processado
    """
    try:
        sql = "SELECT conteudo FROM modelo_cabecalho WHERE ativo = 1 LIMIT 1"
        rows = executar_query(sql)
        
        if rows:
            template = dict(rows[0])['conteudo']
            # Processar placeholders no template
            cabecalho = processar_placeholders(template, placeholders)
            
            # Encapsular em HTML semântico
            return f"""<div class="info-linha">
{cabecalho.replace(chr(10), '<br>')}
</div>"""
        
        # Se não houver template, criar cabeçalho padrão
        return f"""<h1>LAUDO DE PERÍCIA CRIMINAL</h1>
<div class="info-linha">
    <strong>{placeholders.get('tipo_exame', '')}</strong><br>
    REP: {placeholders.get('numero_rep', '')} | Data: {placeholders.get('data_solicitacao', '')}
</div>"""
        
    except Exception as e:
        logger.warning(f"Erro ao buscar cabeçalho: {e}")
        return f"""<h1>LAUDO DE PERÍCIA CRIMINAL</h1>
<div class="info-linha">
    REP: {placeholders.get('numero_rep', '')}
</div>"""


def gerar_pdf_laudo_playwright(laudo_id: int) -> bytes:
    """
    Gera PDF do laudo usando Playwright com alta fidelidade de formatação.
    
    FLUXO (Sprint 2-4 do Playwright.md):
    1. Colher dados de contexto (placeholders)
    2. Buscar seções do laudo no banco
    3. Processar placeholders nas seções
    4. Buscar e processar cabeçalho
    5. Construir HTML consolidado com CSS
    6. Limpar HTML (remover elementos perigosos)
    7. Gerar PDF com Playwright
    
    Args:
        laudo_id: ID do laudo a gerar
        
    Returns:
        bytes: Conteúdo PDF em binário
        
    Raises:
        ValueError: Se laudo não encontrado
        Exception: Se houver erro na geração do PDF
    """
    
    try:
        logger.info(f"Iniciando geração de PDF para laudo {laudo_id} com Playwright")
        
        # 1. Colher placeholders e contexto
        placeholders = colher_dados_contexto(laudo_id)
        logger.debug(f"Placeholders coletados: {list(placeholders.keys())}")
        
        # 2. Buscar seções do laudo
        secoes_banco = listar_secoes_laudo(laudo_id)
        if not secoes_banco:
            logger.warning(f"Laudo {laudo_id} não possui seções")
            secoes_banco = []
        
        # 3. Preparar seções (substituir placeholders)
        secoes_processadas = preparar_secoes_para_html(secoes_banco, placeholders)
        logger.info(f"Processadas {len(secoes_processadas)} seções")
        
        # 4. Buscar cabeçalho processado
        cabecalho_html = buscar_cabecalho_processado(placeholders)
        
        # 5. Construir HTML consolidado
        html_documento = construir_html_laudo(
            cabecalho_html=cabecalho_html,
            secoes=secoes_processadas,
            rodape_html=None  # Rodapé pode ser adicionado depois
        )
        
        # 6. Limpar HTML (remover scripts, iframes, etc)
        html_limpo = limpar_html_para_pdf(html_documento)
        
        # 7. Validar HTML básico
        if not validar_html(html_limpo):
            logger.warning("HTML gerado não passa em validação básica, mas tentando gerar PDF mesmo assim")
        
        # 8. Gerar PDF com Playwright
        logger.info("Gerando PDF com Playwright/Chromium...")
        pdf_bytes = gerar_pdf_do_html(html_limpo)
        
        logger.info(f"PDF gerado com sucesso ({len(pdf_bytes)} bytes)")
        return pdf_bytes
        
    except Exception as e:
        logger.error(f"Erro ao gerar PDF com Playwright: {e}", exc_info=True)
        raise


# Função compatível com código antigo (alias)
def gerar_pdf_laudo(laudo_id: int) -> bytes:
    """
    Alias para manter compatibilidade com código antigo.
    Usa o novo gerador com Playwright.
    """
    return gerar_pdf_laudo_playwright(laudo_id)
