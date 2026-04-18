# Especificação de Tecnologias

## Tech Stack Principal

| Componente | Tecnologia | Versão |
|------------|------------|--------|
| Linguagem | Python | 3.13 |
| Frontend/UI | Streamlit | Latest |
| Database | SQLite | 3.x |
| Hash de senhas | bcrypt | Latest |
| Configuração | python-dotenv | Latest |

## Dependências Python

```
streamlit
bcrypt
python-dotenv
```

## Estrura de Diretórios

```
LaudoPericial/
├── app.py                 # Entry point (Streamlit)
├── requirements.txt      # Dependências
├── .env                # Variáveis de ambiente
├── laudopericial.db     # Banco SQLite
│
├── core/               # Funcionalidades core
│   ├── auth.py        # Autenticação
│   ├── audit.py      # Auditoria
│   └── crypto.py     # Criptografia
│
├── database/           # Camada de dados
│   ├── db.py         # Conexão e queries
│   └── models.py     # Schema do banco
│
├── pages/             # Páginas Streamlit
│   ├── 00_login.py
│   ├── nova_rep.py
│   ├── listar_rep.py
│   └── ...outras páginas
│
├── services/          # Regras de negócio
│   ├── rep_service.py
│   ├── laudo_service.py
│   └── ...outros serviços
│
├── components/        # Componentes UI reutilizáveis
│   ├── menu.py
│   └── ...outros componentes
│
└── generators/       # Geradores de documentos
    ├── pdf_generator.py
    └── ...outros geradores
```

## Padrões de Código

- **Backend**: Funções em `services/` para regras de negócio
- **Database**: Queries centralizadas em `database/db.py`
- **UI**: Páginas em `pages/` seguindo convenção Streamlit
- **Autenticação**: Session state do Streamlit