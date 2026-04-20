"""
setup_projeto.py
────────────────────────────────────────────────────────
Script de configuração inicial do projeto LaudoPericial.
Execute UMA ÚNICA VEZ para criar toda a estrutura de
pastas e arquivos necessários.

Como usar:
    python setup_projeto.py
────────────────────────────────────────────────────────
"""

import os
from pathlib import Path

# ──────────────────────────────────────────────────────
# PASTA RAIZ DO PROJETO
# (é a pasta onde este script está sendo executado)
# ──────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent

print("=" * 55)
print("  LaudoPericial — Configuração Inicial do Projeto")
print("=" * 55)
print(f"\n📁 Pasta raiz: {BASE_DIR}\n")


# ──────────────────────────────────────────────────────
# LISTA DE TODAS AS PASTAS QUE DEVEM EXISTIR
# ──────────────────────────────────────────────────────
PASTAS = [
    "core",
    "database",
    "pages",
    "pages/02_rep",
    "pages/03_laudos",
    "pages/04_templates",
    "pages/05_cadastros",
    "services",
    "generators",
    "components",
    "assets",
    "exports",        # pasta onde os laudos gerados serão salvos
    "backups",        # pasta para backups do banco de dados
]


# ──────────────────────────────────────────────────────
# LISTA DE TODOS OS ARQUIVOS QUE DEVEM EXISTIR
# Formato: ("caminho/do/arquivo.py", "conteúdo do arquivo")
# Se o conteúdo for string vazia, cria arquivo em branco
# ──────────────────────────────────────────────────────
ARQUIVOS = [

    # ── ARQUIVOS RAIZ ──────────────────────────────────

    (".env", """\
# ──────────────────────────────────────────────
# CONFIGURAÇÕES DO SISTEMA — NÃO COMPARTILHE!
# ──────────────────────────────────────────────

# Chave secreta — troque por texto aleatório longo
SECRET_KEY=laudo_pericial_pcpr_2026_chave_secreta

# Nome do arquivo do banco de dados
DATABASE_NAME=laudopericial.db

# Informações do sistema
APP_VERSION=1.0.0
APP_NAME=LaudoPericial PCPR
"""),

    ("requirements.txt", """\
# Interface
streamlit==1.43.2

# Banco de dados
sqlalchemy==2.0.36

# Criptografia e autenticação
bcrypt==4.2.1
cryptography==44.0.0

# Editor de texto rico
streamlit-lexical-extended==0.2.1

# Geração de documentos
python-docx==1.1.2
odfpy==1.4.1
reportlab==4.2.5
Pillow==11.1.0

# Gráficos
plotly==5.24.1

# Utilitários
python-dateutil==2.9.0
pytz==2024.2
python-dotenv==1.0.1
"""),

    (".gitignore", """\
# Ambiente virtual
venv/

# Banco de dados — NUNCA enviar!
*.db
*.sqlite
*.sqlite3
*.db-shm
*.db-wal

# Configurações locais e senhas
.env
*.env

# Laudos exportados — ficam só no computador
exports/

# Backups — ficam só no computador
backups/

# Windows
Thumbs.db
desktop.ini

# Python
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/

# VS Code
.vscode/settings.json

# Temporários
*.tmp
*.log
"""),

    ("README.md", """\
# 🔍 LaudoPericial — PCPR

Sistema de gestão e confecção de laudos periciais criminais.

## Sobre
Desenvolvido para uso da Polícia Científica do Paraná.
Sistema privado — uso restrito.

## Tecnologias
- Python 3.13
- Streamlit
- SQLite

## Status
🚧 Em desenvolvimento

## Como executar
```bash
# Ativar ambiente virtual
venv\\Scripts\\activate

# Rodar o sistema
streamlit run app.py
```
"""),

    # arquivo de entrada principal (será preenchido depois)
    ("app.py", """\
\"\"\"
app.py
Ponto de entrada do sistema LaudoPericial.
\"\"\"

import streamlit as st

st.set_page_config(
    page_title="LaudoPericial PCPR",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 LaudoPericial PCPR")
st.info("Sistema em configuração... Aguarde os próximos passos.")
"""),

    # ── MÓDULO: core ───────────────────────────────────
    ("core/__init__.py",       ""),
    ("core/auth.py",           "# Autenticação — será preenchido no próximo passo\n"),
    ("core/audit.py",          "# Auditoria — será preenchido no próximo passo\n"),
    ("core/crypto.py",         "# Criptografia — será preenchido no próximo passo\n"),

    # ── MÓDULO: database ───────────────────────────────
    ("database/__init__.py",   ""),
    ("database/db.py",         "# Conexão com banco — será preenchido no próximo passo\n"),
    ("database/models.py",     "# Modelos do banco — será preenchido no próximo passo\n"),

    # ── MÓDULO: pages ──────────────────────────────────
    ("pages/__init__.py",              ""),
    ("pages/00_login.py",              "# Tela de login — será preenchido em breve\n"),
    ("pages/01_dashboard.py",          "# Dashboard — será preenchido em breve\n"),
    ("pages/02_rep/__init__.py",       ""),
    ("pages/02_rep/nova_rep.py",       "# Nova REP — será preenchido em breve\n"),
    ("pages/02_rep/editar_rep.py",     "# Editar REP — será preenchido em breve\n"),
    ("pages/02_rep/listar_rep.py",     "# Listar REPs — será preenchido em breve\n"),
    ("pages/03_laudos/__init__.py",    ""),
    ("pages/03_laudos/novo_laudo.py",  "# Novo laudo — será preenchido em breve\n"),
    ("pages/03_laudos/editor_laudo.py","# Editor de laudo — será preenchido em breve\n"),
    ("pages/03_laudos/visualizar_laudo.py", "# Visualizar laudo — será preenchido em breve\n"),
    ("pages/04_templates/__init__.py", ""),
    ("pages/04_templates/gerenciar_templates.py", "# Gerenciar templates — será preenchido em breve\n"),
    ("pages/04_templates/editor_template.py",     "# Editor de template — será preenchido em breve\n"),
    ("pages/05_cadastros/__init__.py", ""),
    ("pages/05_cadastros/tipos_exame.py",  "# Tipos de exame — será preenchido em breve\n"),
    ("pages/05_cadastros/solicitantes.py", "# Solicitantes — será preenchido em breve\n"),
    ("pages/06_busca.py",              "# Busca — será preenchido em breve\n"),
    ("pages/07_historico.py",          "# Histórico — será preenchido em breve\n"),
    ("pages/08_perfil.py",             "# Perfil do usuário — será preenchido em breve\n"),

    # ── MÓDULO: services ───────────────────────────────
    ("services/__init__.py",       ""),
    ("services/rep_service.py",    "# Regras de negócio da REP\n"),
    ("services/laudo_service.py",  "# Regras de negócio do laudo\n"),
    ("services/template_service.py","# Gestão de templates\n"),
    ("services/prazo_service.py",  "# Cálculo e alertas de prazo\n"),
    ("services/backup_service.py", "# Export/import do banco\n"),

    # ── MÓDULO: generators ─────────────────────────────
    ("generators/__init__.py",         ""),
    ("generators/docx_generator.py",   "# Gerador Word (.docx)\n"),
    ("generators/odt_generator.py",    "# Gerador ODT\n"),
    ("generators/pdf_generator.py",    "# Gerador PDF\n"),
    ("generators/preambulo_builder.py","# Montagem automática do preâmbulo\n"),

    # ── MÓDULO: components ─────────────────────────────
    ("components/__init__.py",     ""),
    ("components/rich_editor.py",  "# Componente editor de texto rico\n"),
    ("components/image_uploader.py","# Upload e gestão de fotos\n"),
    ("components/prazo_badge.py",  "# Badge visual de prazo\n"),
    ("components/confirm_dialog.py","# Diálogo de confirmação com senha\n"),
]


# ──────────────────────────────────────────────────────
# FUNÇÕES DE CRIAÇÃO
# ──────────────────────────────────────────────────────

def criar_pastas():
    """Cria todas as pastas do projeto."""
    print("📂 Criando pastas...")
    for pasta in PASTAS:
        caminho = BASE_DIR / pasta
        if not caminho.exists():
            caminho.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Criada: {pasta}/")
        else:
            print(f"   ⏭️  Já existe: {pasta}/")


def criar_arquivos():
    """Cria todos os arquivos do projeto."""
    print("\n📄 Criando arquivos...")
    for arquivo, conteudo in ARQUIVOS:
        caminho = BASE_DIR / arquivo
        if not caminho.exists():
            # Garante que a pasta pai existe
            caminho.parent.mkdir(parents=True, exist_ok=True)
            # Cria o arquivo com o conteúdo definido
            caminho.write_text(conteudo, encoding="utf-8")
            print(f"   ✅ Criado: {arquivo}")
        else:
            print(f"   ⏭️  Já existe: {arquivo}")


def verificar_estrutura():
    """Exibe um resumo final da estrutura criada."""
    print("\n" + "=" * 55)
    print("  ✅ Estrutura do projeto criada com sucesso!")
    print("=" * 55)

    total_pastas  = sum(1 for p in PASTAS
                        if (BASE_DIR / p).exists())
    total_arquivos = sum(1 for a, _ in ARQUIVOS
                         if (BASE_DIR / a).exists())

    print(f"\n  📂 Pastas criadas:   {total_pastas}")
    print(f"  📄 Arquivos criados: {total_arquivos}")
    print(f"\n  📁 Localização: {BASE_DIR}")
    print("\n" + "=" * 55)
    print("\n⚡ Próximo passo: preencher database/db.py")
    print("   Continue seguindo o passo a passo!\n")


# ──────────────────────────────────────────────────────
# EXECUÇÃO PRINCIPAL
# ──────────────────────────────────────────────────────
if __name__ == "__main__":
    criar_pastas()
    criar_arquivos()
    verificar_estrutura()