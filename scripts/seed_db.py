"""
Script de seed para popular o banco de dados com dados fictícios realistas.
Cria 15 REPs em diferentes estágios, vinculados ou não a laudos.

COMO EXECUTAR:
  1. Ative o ambiente virtual:
       No Windows:  venv\Scripts\activate
       No Linux/Mac: source venv/bin/activate

  2. Execute o script:
       python scripts/seed_db.py

  3. Inicie o Streamlit:
       streamlit run app.py

NOTA: Este script deleta o banco 'laudopericial.db' antes de executar para garantir um estado limpo.
"""

import sys
import os
import bcrypt
from pathlib import Path
from datetime import date, datetime, timedelta
import random

# Adiciona o diretório raiz ao path para importar os módulos do projeto
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import executar_comando, executar_query, init_database, DATABASE_PATH

def seed():
    print("Iniciando seed do banco de dados...")
    
    # Se o banco existe, vamos deletar para garantir um estado limpo se desejar, 
    # mas o init_database já usa CREATE TABLE IF NOT EXISTS.
    # Para um seed completo, é melhor começar do zero.
    if DATABASE_PATH.exists():
        print(f"  - Removendo banco existente em {DATABASE_PATH}")
        os.remove(DATABASE_PATH)
    
    init_database()
    
    # 1. Criar Usuário
    print("  - Criando usuario de teste...")
    senha_hash = bcrypt.hashpw("teste".encode(), bcrypt.gensalt()).decode()
    usuario_id = executar_comando("""
        INSERT INTO usuarios (nome, cargo, username, lotacao, email, senha_hash, criado_em, atualizado_em)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now','localtime'), datetime('now','localtime'))""",
        ("Teste Silva", "Perito Oficial Criminal", "teste.silva", "Telemaco Borba - 22a SDP", "teste.silva@policiacientifica.pr.gov.br", senha_hash)
    )

    # 2. Criar Tipos de Exame
    print("  - Criando tipos de exame...")
    tipos_exame = [
        ("B-602", "Eficiência e Prestabilidade", "Exame de eficiência e prestabilidade de vestígios balísticos.", 1),
        ("B-601", "Constatação", "Exame de constatação de vestígios balísticos.", 1),
        ("I-801", "Numerações identificadoras", "Exame numerações identificadoras de veículos.", 1),
        ("E-381", "Caça Níquel", "Exame em equipamentos eletrônicos caça níquel.", 0),
        ("M-112", "Local de local de morte", "Exame local de morte - Homicídio.", 0),
        ("A-470", "Local acidente de trânsito", "Exame local de acidente de trânsito e morte.", 0),
    ]
    
    tipo_ids = []
    for cod, nome, desc, loc in tipos_exame:
        tid = executar_comando(
            "INSERT INTO tipos_exame (codigo, nome, descricao, exame_de_local, ativo) VALUES (?, ?, ?, ?, 1)",
            (cod, nome, desc, loc)
        )
        tipo_ids.append(tid)

    # 3. Criar Solicitantes
    print("  - Criando solicitantes...")
    solicitantes_dados = [
        ("18ª SDP - Tibagi", "Subdivivisão Policial de Tibagi", "contato18sdp@pliciacivil.pr.gov.br"),
        ("18ª SDP - Telêmaco Borba", "Subdivivisão Policial de Telêmaco Borba", "homicidios.telemaco@pc.pr.gov.br"),
        ("43ª DRP - Castro", "Delegacia Regional de Policia de Castro", "transito.castro@pc.pr.gov.br"),
        ("Vara Criminal de Telêmaco Borba", "Tribunal de Justica", "secretaria@1varacrim.telemacoborba.jus.br"),
    ]
    
    solicitante_ids = []
    for nome, orgao, contato in solicitantes_dados:
        sid = executar_comando(
            "INSERT INTO solicitantes (nome, orgao, contato, ativo) VALUES (?, ?, ?, 1)",
            (nome, orgao, contato)
        )
        solicitante_ids.append(sid)

    # 4. Criar Templates
    print("  - Criando templates e secoes...")
    templates_dados = [
        (tipo_ids[0], "Laudo de Eficiência e Prestabilidade"),
        (tipo_ids[2], "Laudo de Local de Morte (Homicidio)"),
        (tipo_ids[4], "Laudo de Constatação de vestígios balísticos"),
    ]
    
    template_ids = []
    for t_exame_id, nome in templates_dados:
        tpl_id = executar_comando(
            "INSERT INTO templates (tipo_exame_id, nome, descricao_exame, ativo) VALUES (?, ?, ?, 1)",
            (t_exame_id, nome, f"Template padrao para {nome}")
        )
        template_ids.append(tpl_id)
        
        # Secoes para o template
        secoes = [
            ("PREÂMBULO", f"<p>Aos {date.today().strftime('%d/%m/%Y')}, no Instituto de Criminalistica, designado pelo Diretor da Unidade...</p>", 1, 1),
            ("HISTÓRICO", "<p>Trata-se de requisicao para exame em local de...</p>", 2, 0),
            ("DO LOCAL", "<p>O local do exame situa-se em via publica, apresentando as seguintes caracteristicas...</p>", 3, 1),
            ("DOS EXAMES", "<p>Durante a pericia foram observados os seguintes vestigios...</p>", 4, 1),
            ("CONCLUSÃO", "<p>Diante do exposto, os peritos concluem que...</p>", 5, 1),
        ]
        for tit, cont, ord, obr in secoes:
            executar_comando(
                "INSERT INTO secoes_template (template_id, titulo, conteudo_base, ordem, obrigatoria) VALUES (?, ?, ?, ?, ?)",
                (tpl_id, tit, cont, ord, obr)
            )

    # 5. Criar 15 REPs
    print("  - Criando 15 REPs com diferentes estagios...")
    
    envolvidos = ["Carlos Eduardo Magalhaes", "Mariana Santos Ferreira", "Desconhecido", "Empresa Alimentos S.A.", "Joao Pedro da Silva", "Beatriz Oliveira"]
    locais = ["Rua Sergipe, 450, Centro", "Av. Higienopolis, 1200", "Rua Paranagua, 89", "Rodovia Celso Garcia Cid, Km 390", "Rua Minas Gerais, 12"]
    tipos_sol = ["BO", "Oficio", "BO PM", "BO PC", "CECOMP"]
    
    data_hoje = date.today()
    
    for i in range(15):
        # Gera dados ficticios mas coerentes
        num_rep = f"2026-{i+1:04d}" # Formato fake
        if i < 5:
            # Primeiras 5: Pendentes, sem laudo
            status_rep = "Pendente"
        elif i < 10:
            # Proximas 5: Em Andamento, com laudo em andamento
            status_rep = "Em Andamento"
        else:
            # Ultimas 5: Concluidas, com laudo Finalizado ou Entregue
            status_rep = "Concluido"
            
        data_sol = data_hoje - timedelta(days=random.randint(1, 30))
        data_doc = data_sol - timedelta(days=random.randint(0, 5))
        
        tipo_idx = i % len(tipo_ids)
        sol_idx = i % len(solicitante_ids)
        
        rep_id = executar_comando("""
            INSERT INTO rep (
                numero_rep, data_solicitacao, tipo_solicitacao, numero_documento, data_documento,
                solicitante_id, nome_autoridade, nome_envolvido, local_fato_descricao, 
                tipo_exame_id, status, usuario_id, criado_em, atualizado_em
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now','localtime'), datetime('now','localtime'))""",
            (
                num_rep, 
                data_sol.isoformat(), 
                random.choice(tipos_sol), 
                f"{100+i}/2026", 
                data_doc.isoformat(),
                solicitante_ids[sol_idx], 
                "Delegado de Plantao", 
                random.choice(envolvidos),
                random.choice(locais),
                tipo_ids[tipo_idx],
                status_rep,
                usuario_id
            )
        )
        
        # 6. Criar Laudos para REPs que nao estao pendentes
        if status_rep != "Pendente":
            # Escolher um template compativel ou o primeiro disponivel
            # Tentamos achar um template que combine com o tipo_exame_id
            template_id = None
            for tpl_id in template_ids:
                # Busca o tipo_exame_id do template
                res = executar_query("SELECT tipo_exame_id FROM templates WHERE id = ?", (tpl_id,))
                if res and res[0]['tipo_exame_id'] == tipo_ids[tipo_idx]:
                    template_id = tpl_id
                    break
            
            if not template_id:
                template_id = template_ids[0] # Fallback
            
            # Status do laudo
            if status_rep == "Em Andamento":
                status_laudo = "Em Andamento"
            else:
                status_laudo = random.choice(["Finalizado", "Entregue"])
                
            laudo_id = executar_comando(
                "INSERT INTO laudos (rep_id, template_id, status, versao_atual, criado_em, atualizado_em) VALUES (?, ?, ?, 1, datetime('now','localtime'), datetime('now','localtime'))",
                (rep_id, template_id, status_laudo)
            )
            
            # Criar secoes do laudo baseadas no template
            secoes_tpl = executar_query("SELECT * FROM secoes_template WHERE template_id = ?", (template_id,))
            for s in secoes_tpl:
                executar_comando("""
                    INSERT INTO secoes_laudo (laudo_id, secao_template_id, titulo, conteudo, ordem, obrigatoria, criado_em, atualizado_em)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now','localtime'), datetime('now','localtime'))""",
                    (laudo_id, s['id'], s['titulo'], s['conteudo_base'], s['ordem'], s['obrigatoria'])
                )
    
    print(f"\nSeed concluido com sucesso!")
    print(f"  - 1 Usuario: teste.silva / teste")
    print(f"  - {len(tipos_exame)} Tipos de Exame")
    print(f"  - {len(solicitantes_dados)} Solicitantes")
    print(f"  - {len(templates_dados)} Templates")
    print(f"  - 15 REPs (5 Pendentes, 5 Em Andamento, 5 Concluidas)")
    print(f"  - 10 Laudos criados e vinculados")


if __name__ == "__main__":
    seed()
