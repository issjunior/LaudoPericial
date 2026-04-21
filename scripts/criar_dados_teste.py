"""
Script para criar dados de teste.
Executar com ambiente virtual: venv/Scripts/python scripts/criar_dados_teste.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import executar_comando, executar_query, init_database
from datetime import datetime, timedelta


def criar_dados():
    db_file = ROOT / "laudopericial.db"
    if not db_file.exists():
        print("Banco nao existe. Criando tabelas...")
        init_database()
    
    # Usuario
    try:
        import bcrypt
        senha_hash = bcrypt.hashpw("teste".encode(), bcrypt.gensalt()).decode()
        executar_comando("""
            INSERT INTO usuarios (nome, cargo, username, lotacao, email, senha_hash, criado_em, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now','localtime'), datetime('now','localtime'))""",
            ("Perito Teste", "Perito Oficial Criminal", "teste", "PCP - Unidade teste", "teste@pcp.pr.gov.br", senha_hash)
        )
        print("  Usuario 'teste' criado")
    except:
        pass
    
    # Tipos de exame
    tipos = [
        ("B-602", "Eficiência e Prestabilidade", "Exame de eficiência e prestabilidade de vestígios balísticos", 0),
        ("E-381", "Equipamento Eletrônico", "Exame de equipamento Eletrônico", 0),
        ("I-801", "Numerações Identificadoras", "Exame nas numerações identificadoras de veículos", 0),
        ("A-470", "Acidente de Trânsito", "Exame em acidente de trânsito", 1),
        ("M-112", "Local de Morte", "Exame em local de morte (homocídio)", 1),
    ]
    for cod, nome, desc, loc in tipos:
        executar_comando(
            "INSERT INTO tipos_exame (codigo, nome, descricao, exame_de_local, ativo) VALUES (?, ?, ?, ?, 1)",
            (cod, nome, desc, loc)
        )
    print("  5 Tipos de exame")
    
    # Solicitantes
    sols = [
        ("Delegado 1", "delegado1@pcp.pr.gov.br", "18ª SDP - Telêmaco Borba"),
        ("Escrivão 1", "escrivao1@pcp.pr.gov.br", "DP - Curiúva"),
        ("Delegado 2", "delegado2@pcp.pr.gov.br", "DP - Reserva"),
        ("Escrivão 2", "escrivao2@pcp.pr.gov.br", "DP - Tibagi"),
        ("Promotor 1", "promotor1@mpr.mp.br", "MP-PR"),
        ("Juiz 1", "juiz1@tjpr.jus.br", "Fórum de Telêmaco Borba"),
    ]
    for resp, email, orgao in sols:
        executar_comando(
            "INSERT INTO solicitantes (nome, orgao, contato, ativo) VALUES (?, ?, ?, 1)",
            (resp, orgao, email)
        )
    print("  5 Solicitantes")
    
    # Templates
    templates = [
        ("B-602", "Eficiência e Prestabilidade", "Exame de eficiência e prestabilidade"),
        ("I-801", "Numerações Identificadoras", "Exame nas numerações identificadoras"),
        ("E-381", "Equipamento Eletrônico", "Exame de equipamento eletrônico"),
        ("A-470", "Acidente de Trânsito", "Exame em acidente de trânsito"),
        ("M-112", "Local de Morte", "Exame em local de morte (homicídio)"),
    ]
    for cod, nome, desc in templates:
        row = executar_query("SELECT id FROM tipos_exame WHERE codigo = ?", (cod,))
        if row:
            executar_comando(
                "INSERT INTO templates (tipo_exame_id, nome, descricao_exame, ativo) VALUES (?, ?, ?, 1)",
                (row[0]['id'], nome, desc)
            )
    print("  5 Templates")
    
    # Secoes template
    secoes = [
        (1, "PREAMBULO", "<p>Ao {{data_solicitacao}}, compareci no local indicado.</p>", 1, 1),
        (1, "HISTORICO", "<p>Historico do fato...</p>", 2, 0),
        (1, "EXAME", "<p>Exames realizados...</p>", 3, 1),
        (1, "LAUDO", "<p>Diante do exposto, opinamos...</p>", 4, 1),
        (2, "PREAMBULO", "<p>Ao {{data_solicitacao}}, examinei o veiculo.</p>", 1, 1),
        (2, "HISTORICO", "<p>Historico...</p>", 2, 0),
        (2, "EXAME", "<p>Exame realizado...</p>", 3, 1),
        (2, "LAUDO", "<p>Opinio...</p>", 4, 1),
        (3, "PREAMBULO", "<p>Ao {{data_solicitacao}}, examinei o equipamento.</p>", 1, 1),
        (3, "HISTORICO", "<p>Historico...</p>", 2, 0),
        (3, "DESCRICAO", "<p>Descricao do equipamento...</p>", 3, 1),
        (3, "LAUDO", "<p>Opinio...</p>", 4, 1),
        (4, "PREAMBULO", "<p>Ao {{data_solicitacao}}, compareci no local {{local_fato}}.</p>", 1, 1),
        (4, "HISTORICO", "<p>Historico do fato...</p>", 2, 0),
        (4, "OBJETIVO", "<p>Objetivo do exame...</p>", 3, 0),
        (4, "CONSTATA", "<p>Constatacoes...</p>", 4, 1),
        (4, "LAUDO", "<p>Opinio pericial...</p>", 5, 1),
        (5, "PREAMBULO", "<p>Ao {{data_solicitacao}}, compareci no local {{local_fato}}.</p>", 1, 1),
        (5, "HISTORICO", "<p>Historico do fato...</p>", 2, 0),
        (5, "EXAME", "<p>Exames realizados...</p>", 3, 1),
        (5, "LAUDO", "<p>Opinio pericial...</p>", 4, 1),
    ]
    for tid, tit, cont, ord, obr in secoes:
        executar_comando(
            "INSERT INTO secoes_template (template_id, titulo, conteudo_base, ordem, obrigatoria, permite_fotos) VALUES (?, ?, ?, ?, ?, 0)",
            (tid, tit, cont, ord, obr)
        )
    print("  Secoes de template")
    
    # REPs - corrigido para colunas certas
    reps = [
        ("0001-2026", "BO", "12345/2026", "2026-01-14", 1, "Delegado Jose", "Joao Silva", "Rua ABC, 123", "A-470"),
        ("0002-2026", "Ofício", "500/2026", "2026-01-15", 1, "Promotor Carlos", "Pedro Santos", "Av. Central, 100", "E-381"),
        ("0003-2026", "BO PC", "12346/2026", "2026-01-16", 1, "Delegado Maria", "Maria Oliveira", "Rua XYZ, 200", "I-801"),
        ("0004-2026", "BO PM", "111/2026", "2026-01-17", 1, "Capitao PM", "Ana Costa", "Rodovia BR-376, Km 150", "M-112"),
        ("0005-2026", "CECOMP", "CECOMP-001/2026", "2026-01-18", 1, "Comandante", "Carlos Lima", "Pracas publicas", "B-602"),
    ]
    for num, tipo, numdoc, data, solid, aut, env, local, cod in reps:
        row = executar_query("SELECT id FROM tipos_exame WHERE codigo = ?", (cod,))
        if row:
            tid = row[0]['id']
            dsol = (datetime.strptime(data, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            executar_comando("""
                INSERT INTO rep (numero_rep, data_solicitacao, tipo_solicitacao, numero_documento, data_documento, solicitante_id, nome_autoridade, nome_envolvido, local_fato_descricao, tipo_exame_id, status, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pendente', 1)""",
                (num, dsol, tipo, numdoc, data, solid, aut, env, local, tid)
            )
    print("  5 REPs")
    
    # Laudos
    laudos_rep = [("0004-2026", 4), ("0005-2026", 5)]
    for num, template_id in laudos_rep:
        rrow = executar_query("SELECT id FROM rep WHERE numero_rep = ?", (num,))
        if rrow:
            executar_comando(
                "INSERT INTO laudos (rep_id, template_id, status, versao_atual) VALUES (?, ?, 'Rascunho', 1)",
                (rrow[0]['id'], template_id)
            )
            executar_comando("UPDATE rep SET status = 'Em Andamento' WHERE id = ?", (rrow[0]['id'],))
    print("  2 Laudos")
    
    # Secoes laudo
    for lid in executar_query("SELECT id, template_id FROM laudos"):
        lid = dict(lid)
        secs = executar_query(
            "SELECT id, titulo, conteudo_base, ordem, obrigatoria FROM secoes_template WHERE template_id = ? ORDER BY ordem",
            (lid['template_id'],)
        )
        for s in secs:
            ds = dict(s)
            executar_comando(
                "INSERT INTO secoes_laudo (laudo_id, secao_template_id, titulo, conteudo, ordem, obrigatoria, permite_fotos) VALUES (?, ?, ?, ?, ?, ?, 0)",
                (lid['id'], ds['id'], ds['titulo'], ds['conteudo_base'], ds['ordem'], ds['obrigatoria'])
            )
    print("  Secoes de laudo")
    
    print("\nPronto!")


if __name__ == "__main__":
    criar_dados()