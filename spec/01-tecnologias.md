# Especificação de Tecnologias

## Tech Stack Principal

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| Linguagem | Python | 3.13 |
| Frontend/UI | Streamlit | Latest |
| Database | SQLite | 3.x |
| Hash de senhas | bcrypt | Latest |
| Configuração | python-dotenv | Latest |
| Editor de texto | streamlit-jodit | Latest |
| Geração PDF | Playwright (Chromium) | Latest |

## Dependências Python

```
streamlit
bcrypt
python-dotenv
streamlit-jodit
playwright
```

## Estrura de Diretórios

```
LaudoPericial/
├── app.py                 # Entry point (Streamlit)
├── requirements.txt        # Dependências
├── .env                 # Variáveis de ambiente
├── laudopericial.db     # Banco SQLite
│
├── database/            # Camada de dados
│   ├── db.py           # Conexão e queries
│   └── models.py       # Schema do banco
│
├── core/               # Funcionalidades core
│   ├── auth.py        # Autenticação
│   ├── audit.py      # Auditoria
│   └── crypto.py      # Criptografia
│
├── pages/              # Páginas Streamlit
│   ├── 00_login.py    # Login
│   ├── 01_dashboard.py # Dashboard
│   ├── nova_rep.py   # Nova REP
│   ├── listar_rep.py # Listar REPs
│   ├── editar_rep.py # Editar REP
│   ├── novo_laudo.py  # Vincular Laudo
│   ├── editor_laudo.py # Editar Laudo
│   ├── visualizar_laudo.py # Visualizar Laudo
│   ├── tipos_exame.py # Tipos de Exame
│   ├── solicitantes.py # Solicitantes
│   ├── gerenciar_templates.py # Templates
│   ├── cabecalho.py  # Cabeçalho Laudo
│   ├── busca.py      # Busca Global
│   ├── historico.py # Histórico Auditoria
│   ├── backup.py    # Backup/Restore
│   ├── perfil.py    # Perfil Usuário
│   └── ...outras páginas
│
├── services/           # Regras de negócio
│   ├── rep_service.py       # REP
│   ├── laudo_service.py    # Laudos
│   ├── template_service.py # Templates
│   ├── prazo_service.py    # Prazos
│   ├── backup_service.py  # Backup
│   ├── cadastro_service.py # Cadastros
│   ├── gerador_pdf_playwright.py # PDF (Playwright)
│   ├── playwright_client.py    # Cliente Playwright
│   ├── html_builder.py # Builder HTML
│   └── ...
│
├── components/        # Componentes UI reutilizáveis
│   ├── menu.py
│   └── ...outros componentes
│
├── generators/       # Geradores de documentos
│   ├── pdf_generator.py  # (reservado)
│   ├── docx_generator.py # (reservado)
│   └── odt_generator.py # (reservado)
│
└── chromium/          # Chromium (Playwright)
    └── ...
```

## Padrões de Código

- **Backend**: Funções em `services/` para regras de negócio
- **Database**: Queries centralizadas em `database/db.py`
- **UI**: Páginas em `pages/` seguindo convenção Streamlit
- **Autenticação**: Session state do Streamlit
- **PDF**: Geração via Playwright/Chromium para preservação de formatação