"""
Script para criar dados de teste no banco.

Executar (usar ambiente virtual):
    venv\Scripts\python scripts\criar_dados_teste.py
"""

import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from database.db import executar_comando, executar_query, init_database
from datetime import date, datetime, time, timedelta


def criar_dados_teste():
    print("Criando dados de teste...")

    # Verificar se as tabelas existem
    try:
        tabelas = executar_query("SELECT name FROM sqlite_master WHERE type='table'")
    except:
        tabelas = []

    if not tabelas:
        print("  Banco vazio. Criando tabelas...")
        init_database()

    # Verificar se ja existe usuario
    usuarios = executar_query("SELECT id FROM usuarios LIMIT 1")
    if not usuarios:
        print("  Nenhum usuario encontrado. Criando usuario de teste...")
        try:
            import bcrypt
            senha_hash = bcrypt.hashpw("teste".encode(), bcrypt.gensalt()).decode()
            executar_comando("""
                INSERT INTO usuarios (
                    nome, cargo, username, lotacao, email,
                    senha_hash, criado_em, atualizado_em
                ) VALUES (?, ?, ?, ?, ?, ?, datetime('now','localtime'), datetime('now','localtime'))""",
                ("Perito Teste", "Perito Oficial Criminal", "teste", "PCP - Unidade teste", "teste@pcp.pr.gov.br", senha_hash)
            )
            usuarios = executar_query("SELECT id FROM usuarios WHERE username = 'teste'")
            if usuarios:
                print("  Usuario 'teste' criado com sucesso!")
        except ImportError:
            print("  Erro: bcrypt nao instalado. Execute 'pip install bcrypt'")
            return
        except Exception as e:
            print(f"  Erro ao criar usuario: {e}")
            return

    usuario_id = usuarios[0]["id"]

# exame_de_local = 0 → Exame por ofício, SEM deslocamento (não exige ir ao local)
# exame_de_local = 1 → Exame DE LOCAL (exige deslocamento, habilita campos de horário e coordenadas)

    # Criar tipos de exame
    tipos_exame = [
        ("B-602", "Eficiência e Prestabilidade", "Exame de eficiência e prestabilidade de vestígios balísticos", 0),
        ("E-381", "Equipamento Eletrônico", "Exame de equipamento Eletrônico", 0),
        ("I-801", "Numerações Identificadoras", "Exame nas numerações identificadoras de veículos", 0),
        ("A-470", "Acidente de Trânsito", "Exame em acidente de trânsito", 1),
        ("M-112", "Local de Morte", "Exame em local de morte (homocídio)", 1),
    ]
    for codigo, nome, desc, exame_local in tipos_exame:
        try:
            executar_comando(
                "INSERT OR IGNORE INTO tipos_exame (codigo, nome, descricao, exame_de_local, ativo) VALUES (?, ?, ?, ?, 1)",
                (codigo, nome, desc, exame_local)
            )
        except:
            pass

    print("  Tipos de exame criados")

    # Criar solicitantes
    solicitantes = [
        ("18ª SDP - Telêmaco Borba", "Delegacia de Policia Civil"),
        ("DP - Curiúva", "Delegacia de Polícia de Curiúva"),
        ("DP - Reserva", "Delegacia de Polícia de Reserva"),
        ("DP - Tibagi", "Delegacia de Polícia de Tibagi"),
        ("MP-PR", "Ministerio Publico do Estado do Paraná"),
    ]
    for nome, orgao in solicitantes:
        try:
            executar_comando(
                "INSERT OR IGNORE INTO solicitantes (nome, orgao, ativo) VALUES (?, ?, 1)",
                (nome, orgao)
            )
        except:
            pass

    print("  Solicitantes criados")

    # Criar templates - busca tipo_exame_id pelo codigo
    templates_codigos = [
        ("B-602", "Eficiência e Prestabilidade", "Exame de eficiência e prestabilidade"),
        ("I-801", "Numerações Identificadoras", "Exame nas numerações identificadoras"),
        ("E-381", "Equipamento Eletrônico", "Exame de equipamento eletrônico"),
        ("A-470", "Acidente de Trânsito", "Exame em acidente de trânsito"),
        ("M-112", "Local de Morte", "Exame em local de morte (homicídio)"),
    ]
    for codigo, nome, desc in templates_codigos:
        try:
            # Buscar o ID do tipo de exame pelo código
            rows = executar_query("SELECT id FROM tipos_exame WHERE codigo = ?", (codigo,))
            if rows:
                tipo_exame_id = rows[0]["id"]
                executar_comando(
                    "INSERT OR IGNORE INTO templates (tipo_exame_id, nome, descricao_exame, ativo) VALUES (?, ?, ?, 1)",
                    (tipo_exame_id, nome, desc)
                )
        except:
            pass

    print("  Templates criados")

    # Criar secoes para cada template (TODOS os templates!)
    secoes_template = [
        # Template 1: B-602 Eficiencia
        (1, "PREAMBULO", "<p>Ao {{data_solicitacao}}, compareci no local indicado, a fim de realizar exame pericial de eficiencia e prestabilidade.</p>", 1, 1),
        (1, "HISTORICO", "<p>Historico do fato...</p>", 2, 0),
        (1, "EXAME", "<p>Exames realizados...</p>", 3, 1),
        (1, "LAUDO", "<p>Diante do exposto, opinamos...</p>", 4, 1),
        # Template 2: I-801 Numeracoes
        (2, "PREAMBULO", "<p>Ao {{data_solicitacao}}, examinei o veiculo para verificacao das numeracoes identificadoras.</p>", 1, 1),
        (2, "HISTORICO", "<p>Historico...</p>", 2, 0),
        (2, "EXAME", "<p>Exame realizado...</p>", 3, 1),
        (2, "LAUDO", "<p>Opinio...</p>", 4, 1),
        # Template 3: E-381 Eletronico
        (3, "PREAMBULO", "<p>Ao {{data_solicitacao}}, examinei o equipamento eletronico.</p>", 1, 1),
        (3, "HISTORICO", "<p>Historico...</p>", 2, 0),
        (3, "DESCRICAO", "<p>Descricao do equipamento...</p>", 3, 1),
        (3, "LAUDO", "<p>Opinio...</p>", 4, 1),
        # Template 4: A-470 Acidente
        (4, "PREAMBULO", "<p>Ao {{data_solicitacao}}, compareci no local {{local_fato}}, a fim de realizar exame pericial de transito.</p>", 1, 1),
        (4, "HISTORICO", "<p>Historico do fato...</p>", 2, 0),
        (4, "OBJETIVO", "<p>Objetivo do exame...</p>", 3, 0),
        (4, "CONSTATA", "<p>Constatacoes...</p>", 4, 1),
        (4, "LAUDO", "<p>Opinio pericial...</p>", 5, 1),
        # Template 5: M-112 Local de Morte
        (5, "PREAMBULO", "<p>Ao {{data_solicitacao}}, compareci no local {{local_fato}}, para exame pericial em local de morte.</p>", 1, 1),
        (5, "HISTORICO", "<p>Historico do fato...</p>", 2, 0),
        (5, "EXAME", "<p>Exames realizados...</p>", 3, 1),
        (5, "LAUDO", "<p>Opinio pericial...</p>", 4, 1),
    ]
    for template_id, titulo, conteudo, ordem, obrig in secoes_template:
        try:
            executar_comando(
                "INSERT OR IGNORE INTO secoes_template (template_id, titulo, conteudo_base, ordem, obrigatoria, permite_fotos) VALUES (?, ?, ?, ?, ?, 0)",
                (template_id, titulo, conteudo, ordem, obrig)
            )
        except:
            pass

    print("  Secoes de template criadas")

# Criar 5 REPs - uma para cada tipo de exame, com diferentes tipos de documento
    reps = [
        # (numero, tipo_documento, tipo_solicitacao, num_doc, data_doc, solicitante_id, autoridade, nome_envolvido, local_fato, status, codigo_tipo)
        ("0001-2026", "BO", "BO", "12345/2026", "2026-01-14", 1, "Delegado Jose", "Joao Silva", "Rua ABC, 123", "Pendente", "A-470"),
        ("0002-2026", "Oficio", "Ofício", "500/2026", "2026-01-15", 2, "Promotor Carlos", "Pedro Santos", "Av. Central, 100", "Pendente", "E-381"),
        ("0003-2026", "BO PC", "BO", "12346/2026", "2026-01-16", 1, "Delegado Maria", "Maria Oliveira", "Rua XYZ, 200", "Pendente", "I-801"),
        ("0004-2026", "BO PM", "BO PM", "111/2026", "2026-01-17", 3, "Capitao PM", "Ana Costa", "Rodovia BR-376, Km 150", "Pendente", "M-112"),
        ("0005-2026", "CECOMP", "CECOMP", "CECOMP-001/2026", "2026-01-18", 4, "Comandante", "Carlos Lima", "Pracas publicas", "Pendente", "B-602"),
    ]

    for item in reps:
        numero = item[0]
        tipo_documento = item[1]
        tipo_sol = item[2]
        num_doc = item[3]
        data_doc = item[4]
        solicitante_id = item[5]
        autoridade = item[6]
        envolvido = item[7]
        local_fato = item[8]
        status = item[9]
        codigo_tipo = item[10]

        # Buscar tipo_exame_id pelo codigo
        rows_tipo = executar_query("SELECT id FROM tipos_exame WHERE codigo = ?", (codigo_tipo,))
        if not rows_tipo:
            print(f"  Tipo de exame {codigo_tipo} nao encontrado, pulando REP {numero}")
            continue
        tipo_exame_id = rows_tipo[0]["id"]

        # Data solicitacao = dia anterior a data do documento
        data_doc_dt = datetime.strptime(data_doc, "%Y-%m-%d")
        data_sol_str = (data_doc_dt - timedelta(days=1)).strftime("%Y-%m-%d")
        data_doc_str = data_doc_dt.strftime("%Y-%m-%d")

        try:
            executar_comando("""
                INSERT OR IGNORE INTO rep (
                    numero_rep, data_solicitacao, tipo_solicitacao, numero_documento,
                    data_documento, solicitante_id, nome_autoridade, nome_envolvido,
                    local_fato_descricao, tipo_exame_id, status, usuario_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (numero, data_sol_str, tipo_sol, num_doc, data_doc_str, solicitante_id,
                 autoridade, envolvido, local_fato, tipo_exame_id, status, usuario_id)
            )
        except Exception as e:
            print(f"  Erro ao criar REP {numero}: {e}")

    print("  REPs criadas")

    # Criar laudos para algumas REPs - buscar template_id pelo nome parcial
    # Template 4 = Acidente (ID 4), Template 5 = Morte (ID 5)
    laudos_data = [
        ("0004-2026", 4),  # REP 4 + Template 4 (Acidente)
        ("0005-2026", 5),  # REP 5 + Template 5 (Local de Morte)
    ]

    for numero_rep, template_id in laudos_data:
        # Buscar rep_id
        rows_rep = executar_query("SELECT id FROM rep WHERE numero_rep = ?", (numero_rep,))
        if not rows_rep:
            continue
        rep_id = rows_rep[0]["id"]

        # Verificar se template_id existe
        rows_template = executar_query("SELECT id FROM templates WHERE id = ?", (template_id,))
        if not rows_template:
            print(f"  Template ID {template_id} nao encontrado, pulando laudo {numero_rep}")
            continue

        try:
            executar_comando("""
                INSERT OR IGNORE INTO laudos (rep_id, template_id, status, versao_atual)
                VALUES (?, ?, 'Rascunho', 1)""",
                (rep_id, template_id)
            )
            # Atualizar status da REP para Em Andamento
            executar_comando(
                "UPDATE rep SET status = 'Em Andamento' WHERE id = ?",
                (rep_id,)
            )
        except Exception as e:
            print(f"  Erro ao criar laudo: {e}")

    print("  Laudos criados")

    # Criar secoes para laudos criados
    laudos = executar_query("SELECT id, template_id FROM laudos")
    for laudo in laudos:
        laudo_id = laudo["id"]
        template_id = laudo["template_id"]

        secoes = executar_query(
            "SELECT id, titulo, conteudo_base, ordem, obrigatoria FROM secoes_template WHERE template_id = ? ORDER BY ordem",
            (template_id,)
        )

        for secao in secoes:
            try:
                executar_comando("""
                    INSERT INTO secoes_laudo (
                        laudo_id, secao_template_id, titulo, conteudo, ordem, obrigatoria, permite_fotos
                    ) VALUES (?, ?, ?, ?, ?, ?, 0)""",
                    (laudo_id, secao["id"], secao["titulo"], secao["conteudo_base"],
                     secao["ordem"], secao["obrigatoria"])
                )
            except:
                pass

    print("  Secoes de laudo criadas")

    print("\nDados de teste criados com sucesso!")
    print("\nResumo:")
    print("  - 5 Tipos de Exame")
    print("  - 5 Solicitantes")
    print("  - 5 Templates")
    print("  - 5 REPs (3 Pendentes, 2 Em Andamento)")
    print("  - 2 Laudos (em rascunho)")
    print("  - Secoes preenchidas nos laudos")


if __name__ == "__main__":
    criar_dados_teste()