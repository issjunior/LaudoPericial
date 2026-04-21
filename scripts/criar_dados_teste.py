"""
Script para criar dados de teste.

COMO EXECUTAR:
  1. Ative o ambiente virtual:
       No Windows:  venv\Scripts\activate
       No Linux/Mac: source venv/bin/activate

  2. Execute o script:
       python scripts/criar_dados_teste.py

  3. Inicie o Streamlit:
       streamlit run app.py

NOTA: Delete o banco 'laudopericial.db' antes de executar.
"""

import sys
from pathlib import Path
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import executar_comando, executar_query, init_database


def criar_dados():
    db_file = ROOT / "laudopericial.db"
    if not db_file.exists():
        print("Banco nao existe. Criando tabelas...")
        init_database()

    # Busca dados existentes no banco
    tipos = [dict(r) for r in executar_query("SELECT id, codigo, nome, descricao, exame_de_local FROM tipos_exame WHERE ativo = 1")]
    solicitantes = [dict(r) for r in executar_query("SELECT id, nome, orgao, contato FROM solicitantes WHERE ativo = 1")]
    templates = [dict(r) for r in executar_query("SELECT id, tipo_exame_id, nome FROM templates WHERE ativo = 1")]
    usuarios = [dict(r) for r in executar_query("SELECT id FROM usuarios")]

    print(f"\n📊 Dados no banco:")
    print(f"  - {len(tipos)} tipo(s) de exame")
    print(f"  - {len(solicitantes)} solicitante(s)")
    print(f"  - {len(templates)} template(s)")
    print(f"  - {len(usuarios)} usuário(s)")

    # Cria dados mínimos se não existirem
    if not usuarios:
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
        usuarios = [dict(r) for r in executar_query("SELECT id FROM usuarios")]

    if not tipos:
        tipos_fallback = [
            ("A-470", "Acidente de Trânsito", "Exame em acidente de trânsito", 1),
            ("M-112", "Local de Morte", "Exame em local de morte (homicídio)", 1),
            ("E-381", "Equipamento Eletrônico", "Exame de equipamento eletrônico", 0),
        ]
        for cod, nome, desc, loc in tipos_fallback:
            executar_comando(
                "INSERT INTO tipos_exame (codigo, nome, descricao, exame_de_local, ativo) VALUES (?, ?, ?, ?, 1)",
                (cod, nome, desc, loc)
            )
        tipos = [dict(r) for r in executar_query("SELECT id, codigo, nome, descricao, exame_de_local FROM tipos_exame WHERE ativo = 1")]

    if not solicitantes:
        sols_fallback = [
            ("Delegado Teste", "delegado@pcp.pr.gov.br", "DP - Teste"),
        ]
        for nome, email, orgao in sols_fallback:
            executar_comando(
                "INSERT INTO solicitantes (nome, orgao, contato, ativo) VALUES (?, ?, ?, 1)",
                (nome, orgao, email)
            )
        solicitantes = [dict(r) for r in executar_query("SELECT id, nome, orgao, contato FROM solicitantes WHERE ativo = 1")]

    if not templates and tipos:
        for t in tipos[:4]:
            executar_comando(
                "INSERT INTO templates (tipo_exame_id, nome, descricao_exame, ativo) VALUES (?, ?, ?, 1)",
                (t['id'], t['nome'], t['descricao'] or "")
            )
        templates = [dict(r) for r in executar_query("SELECT id, tipo_exame_id, nome FROM templates WHERE ativo = 1")]

    # Seções template
    secoes_count = executar_query("SELECT COUNT(*) FROM secoes_template")[0][0]
    if secoes_count == 0 and templates:
        for tid in range(1, min(len(templates), 4) + 1):
            secoes = [
                (tid, "PREAMBULO", "<p>Ao {{data_solicitacao}}, compareci no local indicado.</p>", 1, 1),
                (tid, "HISTORICO", "<p>Historico do fato...</p>", 2, 0),
                (tid, "EXAME", "<p>Exames realizados...</p>", 3, 1),
                (tid, "LAUDO", "<p>Diante do exposto, opinamos...</p>", 4, 1),
            ]
            for t_id, tit, cont, ord, obr in secoes:
                executar_comando(
                    "INSERT INTO secoes_template (template_id, titulo, conteudo_base, ordem, obrigatoria) VALUES (?, ?, ?, ?, ?)",
                    (t_id, tit, cont, ord, obr)
                )

    # ID do usuário
    usuario_id = usuarios[0]['id'] if usuarios else 1

    # Data base: mês atual (abril/2026)
    data_base = date(2026, 4, 20)

    # Criar REPs
    print("\n📝 Criando REPs...")
    envolvidos = ["Veículo VW/Gol", "Celular iPhone", "Moto Honda", "Local de morte",
                  "Arma de fogo", "Veículo Fiat", "Notebook Dell", "Local de acidente",
                  "Veículo Renault", "Computador"]
    locais = ["Rua ABC, 123", "Av. Central, 100", "Rua XYZ, 200", "Rodovia BR-376, Km 150",
              "Praças públicas", "Rua DEF, 456", "Av. Norte, 200", "BR-101, Km 80",
              "Rua GHI, 789", "Escritório central"]
    tipos_sol = ["BO", "Ofício", "BO PC", "BO PM", "CECOMP"]

    num_rep = 1
    for i in range(10):
        dias_atras = i * 3
        data_doc = (data_base - timedelta(days=dias_atras)).strftime("%Y-%m-%d")
        data_sol = (data_base - timedelta(days=dias_atras + 1)).strftime("%Y-%m-%d")

        tipo_exame = tipos[i % len(tipos)] if tipos else None
        solicitante = solicitantes[i % len(solicitantes)] if solicitantes else None

        if tipo_exame and solicitante:
            num_str = f"{num_rep:04d}-2026"
            executar_comando("""
                INSERT INTO rep (numero_rep, data_solicitacao, tipo_solicitacao, numero_documento, data_documento,
                                solicitante_id, nome_autoridade, nome_envolvido, local_fato_descricao, tipo_exame_id,
                                status, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pendente', ?)""",
                (num_str, data_sol, tipos_sol[i % len(tipos_sol)], f"{1000+i}/2026",
                 data_doc, solicitante['id'], solicitante['nome'], envolvidos[i], locais[i],
                 tipo_exame['id'], usuario_id)
            )
            num_rep += 1

    reps_criadas = executar_query("SELECT COUNT(*) FROM rep")[0][0]
    print(f"  {reps_criadas} REP(s)")

    # Criar laudos
    print("\n📄 Criando laudos...")
    laudos_status = ["Em Andamento", "Em Andamento", "Finalizado", "Entregue", "Entregue"]
    for i in range(min(5, reps_criadas)):
        rep = executar_query(f"SELECT id FROM rep LIMIT 1 OFFSET {i}")
        if rep and templates:
            template = templates[i % len(templates)]
            executar_comando(
                "INSERT INTO laudos (rep_id, template_id, status, versao_atual) VALUES (?, ?, ?, 1)",
                (rep[0]['id'], template['id'], laudos_status[i])
            )

            rep_status = "Em Andamento" if laudos_status[i] == "Em Andamento" else "Concluído"
            executar_comando("UPDATE rep SET status = ? WHERE id = ?", (rep_status, rep[0]['id']))

            secoes = executar_query("SELECT * FROM secoes_template WHERE template_id = ?", (template['id'],))
            laudo_id = executar_query("SELECT id FROM laudos ORDER BY id DESC LIMIT 1")[0]['id']
            for s in secoes:
                s = dict(s)
                executar_comando("""
                    INSERT INTO secoes_laudo (laudo_id, secao_template_id, titulo, conteudo, ordem, obrigatoria)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (laudo_id, s['id'], s['titulo'], s['conteudo_base'], s['ordem'], s['obrigatoria'])
                )

    laudos_criados = executar_query("SELECT COUNT(*) FROM laudos")[0][0]
    print(f"  {laudos_criados} laudo(s)")

    print("\n✅ Pronto!")

    # Inicia Streamlit
    import subprocess
    print("\n🚀 Iniciando Streamlit...")
    subprocess.Popen(["streamlit", "run", "app.py"])


if __name__ == "__main__":
    criar_dados()